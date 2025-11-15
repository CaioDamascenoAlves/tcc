# Instruções: Upload de Dados para Google Drive

Este documento explica como configurar o upload automático de CSVs para o Google Drive.

## 🎯 Objetivo

Os arquivos CSV em `results/` são muito grandes para o GitHub (>100MB). Solução:
- **Desenvolvimento Local**: Usa arquivos em `results/` diretamente
- **Streamlit Cloud**: Baixa arquivos do Google Drive automaticamente

## 📋 Passo a Passo

### 1. Criar Credenciais OAuth (APENAS UMA VEZ)

1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto ou selecione existente
3. **Habilitar API**:
   - Menu: APIs & Services > Library
   - Busque: "Google Drive API"
   - Clique: Enable

4. **Criar Credenciais**:
   - Menu: APIs & Services > Credentials
   - Clique: "+ CREATE CREDENTIALS" > OAuth client ID
   - Se aparecer aviso sobre consent screen:
     - Clique: "CONFIGURE CONSENT SCREEN"
     - Escolha: External
     - Preencha apenas campos obrigatórios:
       - App name: "TCC Olympic Networks"
       - User support email: seu email
       - Developer contact: seu email
     - Clique: SAVE AND CONTINUE
     - Em Scopes, clique: ADD OR REMOVE SCOPES
     - Busque e marque: `.../auth/drive.file`
     - Clique: UPDATE > SAVE AND CONTINUE
     - Em Test users, clique: ADD USERS
     - Adicione seu email do Google
     - Clique: SAVE AND CONTINUE

   - Volte para Credentials > CREATE CREDENTIALS > OAuth client ID
   - Application type: Desktop app
   - Name: "TCC Upload Script"
   - Clique: CREATE

5. **Baixar Credenciais**:
   - Clique no ícone de download (⬇) ao lado da credencial criada
   - Salve como: `c:\Users\Caio\Desktop\tcc\main\credentials.json`

### 2. Instalar Dependências

```cmd
cd c:\Users\Caio\Desktop\tcc\main
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
```

### 3. Fazer Upload dos CSVs

```cmd
cd c:\Users\Caio\Desktop\tcc\main
python scripts\upload_to_drive.py
```

**Primeira execução**:
- Abrirá navegador para autenticação
- Faça login com sua conta Google
- Aceite permissões solicitadas
- Salvará `token.json` para uso futuro

**Execuções seguintes**:
- Usará `token.json` automaticamente (sem login)

### 4. Commitar Mapeamento

O script gera `drive_files.json` com IDs e URLs dos arquivos:

```cmd
git add drive_files.json
git commit -m "Add Google Drive file mapping"
git push
```

**⚠️ IMPORTANTE**: 
- ✅ **COMITAR**: `drive_files.json` 
- ❌ **NÃO COMITAR**: `credentials.json`, `token.json`

### 5. Deploy no Streamlit Cloud

O dashboard detecta automaticamente se está no Streamlit Cloud e baixa os dados do Drive.

**Nenhuma configuração adicional necessária!**

## 🔄 Atualizar Dados

Quando modificar CSVs localmente:

```cmd
python scripts\upload_to_drive.py
git add drive_files.json
git commit -m "Update Drive data"
git push
```

O Streamlit Cloud irá buscar os dados atualizados automaticamente no próximo deploy.

## 🗑️ Limpar Cache Local

Se quiser forçar re-download dos arquivos:

```python
from core.data_loader_auto import get_data_loader
loader = get_data_loader()
if loader.use_drive:
    loader.loader.clear_cache()
```

## 📁 Estrutura de Arquivos

```
main/
├── credentials.json        # Credenciais OAuth (NÃO COMITAR)
├── token.json             # Token de acesso (NÃO COMITAR)
├── drive_files.json       # Mapeamento (COMITAR)
├── .cache/                # Cache de downloads (NÃO COMITAR)
├── scripts/
│   └── upload_to_drive.py
└── src/
    └── core/
        ├── drive_loader.py      # Carregador do Drive
        └── data_loader_auto.py  # Carregador automático
```

## 🐛 Troubleshooting

**Erro: "credentials.json not found"**
- Baixe as credenciais OAuth do Google Cloud Console

**Erro: "Access blocked"**
- Adicione seu email como "Test user" no OAuth consent screen

**Erro: "Permission denied"**
- Verifique se habilitou Google Drive API

**Dados antigos no Streamlit Cloud**
- Os dados são cacheados. Faça novo deploy ou limpe cache manualmente.

## 🔒 Segurança

- `credentials.json` e `token.json` estão no `.gitignore`
- Arquivos no Drive são públicos (qualquer pessoa com link pode ler)
- Se quiser privacidade, remova a permissão `'anyone'` em `upload_to_drive.py`

## 📊 Estatísticas

Após upload, o script mostra:
- Total de arquivos enviados
- Tamanho total em MB
- Link da pasta no Drive
