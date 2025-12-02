"""
Upload de arquivos CSV para Google Drive.

Este script faz upload dos CSVs de results/ para uma pasta específica no Google Drive
e gera um arquivo de mapeamento (drive_files.json) com os IDs dos arquivos.

Uso:
    python upload_to_drive.py

Primeira execução:
    - Abrirá navegador para autenticação OAuth
    - Salvará token.json para uso futuro
    
Execuções seguintes:
    - Usará token.json salvo (sem necessidade de login)
"""

import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Escopos necessários
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Configurações
PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / 'results'
CREDENTIALS_FILE = PROJECT_ROOT / 'credentials.json'  # Baixe do Google Cloud Console
TOKEN_FILE = PROJECT_ROOT / 'token.json'
DRIVE_FOLDER_NAME = 'TCC_Olympic_Networks_Data'  # Nome da pasta no Drive


def authenticate():
    """Autentica e retorna serviço do Google Drive."""
    creds = None
    
    # Tenta carregar token salvo
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    
    # Se não há credenciais válidas, faz login
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
        
        # Salva token para próxima execução
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)


def find_or_create_folder(service, folder_name):
    """Encontra ou cria pasta no Google Drive."""
    # Busca pasta existente
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    
    if items:
        print(f" Pasta '{folder_name}' já existe (ID: {items[0]['id']})")
        return items[0]['id']
    
    # Cria nova pasta
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    print(f" Pasta '{folder_name}' criada (ID: {folder['id']})")
    return folder['id']


def upload_file(service, file_path, folder_id):
    """Faz upload de um arquivo para o Google Drive."""
    file_name = file_path.name
    
    # Verifica se arquivo já existe na pasta
    query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaFileUpload(str(file_path), resumable=True)
    
    if items:
        # Atualiza arquivo existente
        file_id = items[0]['id']
        file = service.files().update(
            fileId=file_id,
            media_body=media
        ).execute()
        print(f"  [UPDATE] {file_name} (ID: {file_id})")
    else:
        # Upload novo arquivo
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        file_id = file['id']
        print(f"  [NEW] {file_name} (ID: {file_id})")
    
    # Tornar arquivo público (qualquer pessoa com link pode ver)
    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()
    
    return file_id


def get_all_csv_files(results_dir):
    """Retorna lista de todos os CSVs e JSONs em results/ e subdiretórios."""
    data_files = []
    for root, dirs, files in os.walk(results_dir):
        for file in files:
            if file.endswith(('.csv', '.json')):  # Incluir CSVs e JSONs
                full_path = Path(root) / file
                relative_path = full_path.relative_to(results_dir)
                data_files.append({
                    'full_path': full_path,
                    'relative_path': str(relative_path).replace('\\', '/')  # Normalizar
                })
    return data_files


def main():
    """Execução principal."""
    print("=" * 60)
    print("UPLOAD DE DADOS PARA GOOGLE DRIVE")
    print("=" * 60)
    
    # Autentica
    print("\n[1/4] Autenticando...")
    service = authenticate()
    print(" Autenticado com sucesso!")
    
    # Cria/encontra pasta
    print(f"\n[2/4] Configurando pasta '{DRIVE_FOLDER_NAME}'...")
    folder_id = find_or_create_folder(service, DRIVE_FOLDER_NAME)
    
    # Lista arquivos CSV e JSON
    print("\n[3/4] Listando arquivos CSV e JSON...")
    csv_files = get_all_csv_files(RESULTS_DIR)
    print(f" Encontrados {len(csv_files)} arquivos (CSV + JSON)")
    
    # Upload de cada arquivo
    print("\n[4/4] Fazendo upload...")
    drive_mapping = {}
    
    for item in csv_files:
        file_path = item['full_path']
        relative_path = item['relative_path']
        
        file_id = upload_file(service, file_path, folder_id)
        
        # Gera URL de download direto
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        drive_mapping[relative_path] = {
            'file_id': file_id,
            'download_url': download_url,
            'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2)
        }
    
    # Salva mapeamento
    mapping_file = PROJECT_ROOT / 'drive_files.json'
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(drive_mapping, f, indent=2, ensure_ascii=False)
    
    print(f"\n Mapeamento salvo em: {mapping_file}")
    print(f" Total de arquivos enviados: {len(drive_mapping)}")
    
    # Estatísticas
    total_size = sum(item['size_mb'] for item in drive_mapping.values())
    print(f" Tamanho total: {total_size:.2f} MB")
    
    print("\n" + "=" * 60)
    print(" UPLOAD CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print(f"\nPasta no Drive: {DRIVE_FOLDER_NAME}")
    print(f"Link: https://drive.google.com/drive/folders/{folder_id}")


if __name__ == '__main__':
    main()
