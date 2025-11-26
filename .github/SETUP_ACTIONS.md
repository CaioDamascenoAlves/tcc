# Configuração GitHub Actions

Este projeto usa GitHub Actions para:
1. **Manter o app Streamlit sempre ativo** (keep-alive.yml)
2. **Atualizar dados no Google Drive automaticamente** (update-drive-data.yml)

## 1. Configurar Secrets do GitHub

Você precisa adicionar 2 secrets no repositório:

### Passo 1: Acessar Settings → Secrets

1. Vá para o repositório no GitHub
2. Clique em **Settings** (aba superior)
3. No menu lateral esquerdo: **Secrets and variables** → **Actions**
4. Clique em **New repository secret**

### Passo 2: Adicionar GOOGLE_CREDENTIALS

**Nome do Secret:** `GOOGLE_CREDENTIALS`

**Valor:** Conteúdo completo do arquivo `main/credentials.json`

```bash
# No terminal, copie o conteúdo:
cat main/credentials.json
```

Cole o JSON completo no campo Value do secret.

**Formato esperado:**
```json
{
  "installed": {
    "client_id": "seu-client-id.apps.googleusercontent.com",
    "project_id": "seu-projeto",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    ...
  }
}
```

### Passo 3: Adicionar GOOGLE_TOKEN

**Nome do Secret:** `GOOGLE_TOKEN`

**Valor:** Conteúdo completo do arquivo `main/token.json`

```bash
# Execute o upload manual primeiro para gerar o token:
cd main/scripts
python upload_to_drive.py

# Depois copie o token gerado:
cat ../token.json
```

Cole o JSON completo no campo Value do secret.

**Formato esperado:**
```json
{
  "token": "ya29.a0...",
  "refresh_token": "1//0g...",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

---

## 2. Configurar URL do App Streamlit

Edite `.github/workflows/keep-alive.yml` e substitua a URL:

```yaml
APP_URL="https://dashboard-tcc.rglg.org"  # ← Substitua pela sua URL
```

**Como encontrar sua URL:**
1. Acesse https://share.streamlit.io
2. Encontre seu app
3. Copie a URL completa (ex: `https://seu-app.streamlit.app`)

---

## 3. Testar os Workflows

### Testar Keep-Alive (Manual)

1. Vá para **Actions** no GitHub
2. Selecione **Keep Streamlit App Alive**
3. Clique em **Run workflow** → **Run workflow**
4. Verifique se o ping funcionou

### Testar Upload Automático (Manual)

1. Vá para **Actions** no GitHub
2. Selecione **Auto-Upload Data to Google Drive**
3. Clique em **Run workflow** → **Run workflow**
4. Verifique os logs para confirmar upload

---

## 4. Como Funciona

### Keep-Alive Workflow

- **Frequência:** A cada 10 minutos
- **Função:** Faz requisição HTTP para manter o app acordado
- **Custo:** ~0 (bem dentro do limite gratuito do GitHub)

**Logs típicos:**
```
🏓 Pinging Streamlit app at Tue Nov 26 14:30:00 UTC 2024
HTTP/1.1 200 OK
✅ App is alive and responding!
```

### Auto-Upload Workflow

- **Triggers:**
  - Quando você faz push de mudanças em `main/results/**`
  - Quando você faz push de mudanças em `main/src/pipeline/**`
  - Manualmente via Actions
- **Função:**
  - Faz upload de CSVs e JSONs para Google Drive
  - Atualiza `drive_files.json` automaticamente
  - Faz commit das mudanças

**Logs típicos:**
```
📝 Setting up Google Drive credentials...
✅ Token OAuth encontrado
🚀 Iniciando upload para Google Drive...
✓ Encontrados 45 arquivos (CSV + JSON)
✓ UPLOAD CONCLUÍDO COM SUCESSO!
🔄 drive_files.json commitado automaticamente
```

---

## 5. Solução de Problemas

### Erro: "GOOGLE_CREDENTIALS not found"

- Verifique se o secret foi criado corretamente
- Nome deve ser **exatamente** `GOOGLE_CREDENTIALS` (case-sensitive)

### Erro: "Authentication failed"

- O `token.json` pode ter expirado
- Execute manualmente: `python main/scripts/upload_to_drive.py`
- Atualize o secret `GOOGLE_TOKEN` com o novo token

### Workflow não executa automaticamente

- Verifique se você fez commit em `main/results/**`
- Verifique a aba **Actions** para ver se o workflow está habilitado
- Em Settings → Actions → General, certifique-se que "Allow all actions" está marcado

### App ainda entra em sleep

- Verifique se keep-alive.yml está executando (aba Actions)
- Verifique se a URL está correta
- Pode levar até 10 minutos para o primeiro ping

---

## 6. Limites e Considerações

### GitHub Actions Limites (Free Tier)

- **2000 minutos/mês** de execução
- Keep-alive: ~10 segundos a cada 10 min = ~4320 exec/mês = **~12 horas/mês** ✅
- Upload: ~30 segundos por execução = **variável** (depende de quantos commits)
- **Total estimado:** < 20 horas/mês (bem dentro do limite)

### Google Drive API Limites

- **10,000 requisições/dia** (queries)
- **1,000 requisições/100 segundos/usuário**
- Upload automático está bem dentro dos limites ✅

---

## 7. Desabilitar Workflows

Se quiser desabilitar temporariamente:

1. Vá para **Actions**
2. Selecione o workflow
3. Clique nos **⋯** (três pontos) → **Disable workflow**

Ou comente as linhas do `on:` no arquivo YAML.

---

## 8. Monitoramento

### Ver Execuções

1. Aba **Actions** no GitHub
2. Veja histórico de todas as execuções
3. Clique em uma execução para ver logs detalhados

### Notificações

Por padrão, você receberá email se um workflow falhar.

Para customizar: Settings → Notifications → Actions

---

## Suporte

Se tiver problemas:
1. Verifique os logs na aba Actions
2. Verifique se os secrets estão configurados
3. Execute manualmente para testar
