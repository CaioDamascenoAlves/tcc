"""
Upload de arquivos CSV para Google Drive (versão otimizada).

Melhorias:
- Salva drive_files.json incrementalmente (após cada arquivo)
- Skip de arquivos já enviados com sucesso
- Retry automático com backoff exponencial
- Melhor tratamento de erros e timeouts
- Progresso detalhado
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Escopos necessários
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Configurações
PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / 'results'
CREDENTIALS_FILE = PROJECT_ROOT / 'credentials.json'
TOKEN_FILE = PROJECT_ROOT / 'token.json'
MAPPING_FILE = PROJECT_ROOT / 'drive_files.json'
DRIVE_FOLDER_NAME = 'TCC_Olympic_Networks_Data'

# Configurações de retry
MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # segundos
CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB chunks


def authenticate():
    """Autentica e retorna serviço do Google Drive."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"Arquivo {CREDENTIALS_FILE} não encontrado!\n"
                    "Baixe as credenciais OAuth do Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


def find_or_create_folder(service, folder_name: str) -> str:
    """Encontra ou cria pasta no Google Drive."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])

    if items:
        print(f"✓ Pasta '{folder_name}' encontrada (ID: {items[0]['id']})")
        return items[0]['id']

    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    print(f"✓ Pasta '{folder_name}' criada (ID: {folder['id']})")
    return folder['id']


def load_existing_mapping() -> Dict:
    """Carrega mapeamento existente de drive_files.json."""
    if MAPPING_FILE.exists():
        try:
            with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠ drive_files.json corrompido, iniciando do zero")
            return {}
    return {}


def save_mapping(mapping: Dict):
    """Salva mapeamento incrementalmente."""
    with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)


def get_file_id_from_drive(service, file_name: str, folder_id: str) -> Optional[str]:
    """Busca ID do arquivo no Drive."""
    query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    return items[0]['id'] if items else None


def upload_file_with_retry(service, file_path: Path, folder_id: str, existing_file_id: Optional[str] = None) -> str:
    """Faz upload com retry automático."""
    file_name = file_path.name
    file_metadata = {'name': file_name, 'parents': [folder_id]}

    for attempt in range(MAX_RETRIES):
        try:
            # Configurar upload com chunks para arquivos grandes
            media = MediaFileUpload(
                str(file_path),
                resumable=True,
                chunksize=CHUNK_SIZE
            )

            if existing_file_id:
                # Atualiza arquivo existente
                request = service.files().update(
                    fileId=existing_file_id,
                    media_body=media
                )
            else:
                # Upload novo arquivo
                request = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                )

            # Upload com progresso
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    if progress % 25 == 0:  # Mostra a cada 25%
                        print(f"    {progress}%...", end='', flush=True)

            file_id = response.get('id', existing_file_id)
            return file_id

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                backoff = INITIAL_BACKOFF * (2 ** attempt)
                print(f"\n    ⚠ Erro: {str(e)[:60]}... Tentando novamente em {backoff}s...")
                time.sleep(backoff)
            else:
                raise


def get_all_data_files(results_dir: Path):
    """Retorna lista de todos os CSVs e JSONs."""
    data_files = []
    for root, dirs, files in os.walk(results_dir):
        for file in files:
            if file.endswith(('.csv', '.json')):
                full_path = Path(root) / file
                relative_path = full_path.relative_to(results_dir)
                data_files.append({
                    'full_path': full_path,
                    'relative_path': str(relative_path).replace('\\', '/'),
                    'size_mb': round(full_path.stat().st_size / (1024 * 1024), 2)
                })

    # Ordenar por tamanho (menores primeiro para testar conexão)
    return sorted(data_files, key=lambda x: x['size_mb'])


def main():
    """Execução principal."""
    print("=" * 70)
    print("UPLOAD OTIMIZADO DE DADOS PARA GOOGLE DRIVE")
    print("=" * 70)

    # [1] Autenticar
    print("\n[1/5] Autenticando...")
    service = authenticate()
    print("✓ Autenticado com sucesso!")

    # [2] Configurar pasta
    print(f"\n[2/5] Configurando pasta '{DRIVE_FOLDER_NAME}'...")
    folder_id = find_or_create_folder(service, DRIVE_FOLDER_NAME)

    # [3] Carregar mapeamento existente
    print("\n[3/5] Carregando mapeamento existente...")
    drive_mapping = load_existing_mapping()
    print(f"✓ {len(drive_mapping)} arquivos já mapeados")

    # [4] Listar arquivos
    print("\n[4/5] Listando arquivos locais...")
    data_files = get_all_data_files(RESULTS_DIR)
    total_size = sum(f['size_mb'] for f in data_files)
    print(f"✓ {len(data_files)} arquivos encontrados ({total_size:.2f} MB total)")

    # [5] Upload com progresso
    print("\n[5/5] Fazendo upload...\n")
    uploaded = 0
    skipped = 0
    failed = []

    for i, item in enumerate(data_files, 1):
        file_path = item['full_path']
        relative_path = item['relative_path']
        size_mb = item['size_mb']

        print(f"[{i}/{len(data_files)}] {relative_path} ({size_mb} MB)", end=' ')

        try:
            # Verificar se já existe e está ok
            if relative_path in drive_mapping:
                existing_id = drive_mapping[relative_path].get('file_id')
                print(f"✓ SKIP (já enviado: {existing_id})")
                skipped += 1
                continue

            # Buscar ID no Drive se existir
            existing_id = get_file_id_from_drive(service, file_path.name, folder_id)

            # Upload
            if existing_id:
                print("→ UPDATE", end=' ')
            else:
                print("→ NEW", end=' ')

            file_id = upload_file_with_retry(service, file_path, folder_id, existing_id)

            # Tornar arquivo público (CRÍTICO para download funcionar)
            try:
                service.permissions().create(
                    fileId=file_id,
                    body={'type': 'anyone', 'role': 'reader'}
                ).execute()
            except:
                pass  # Ignora se já for público

            # Salvar no mapeamento
            drive_mapping[relative_path] = {
                'file_id': file_id,
                'download_url': f"https://drive.google.com/uc?export=download&id={file_id}",
                'size_mb': size_mb
            }

            # Salvar incrementalmente
            save_mapping(drive_mapping)

            print(f" ✓ OK (ID: {file_id})")
            uploaded += 1

        except Exception as e:
            print(f" ✗ ERRO: {str(e)[:60]}...")
            failed.append({'file': relative_path, 'error': str(e)})

    # Resumo final
    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)
    print(f"✓ Enviados:     {uploaded} arquivos")
    print(f"→ Já existiam:  {skipped} arquivos")
    print(f"✗ Falharam:     {len(failed)} arquivos")
    print(f"📁 Total:       {len(drive_mapping)} arquivos no mapeamento")
    print(f"💾 Tamanho:     {sum(item['size_mb'] for item in drive_mapping.values()):.2f} MB")

    if failed:
        print("\n⚠ Arquivos que falharam:")
        for item in failed:
            print(f"  - {item['file']}: {item['error'][:60]}...")

    print(f"\n✓ Mapeamento salvo em: {MAPPING_FILE}")
    print(f"✓ Pasta no Drive: https://drive.google.com/drive/folders/{folder_id}")
    print("=" * 70)


if __name__ == '__main__':
    main()
