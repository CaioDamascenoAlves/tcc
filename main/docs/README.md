# Documentação do Projeto TCC

**Última atualização:** 2026-02-07

Esta pasta contém documentação técnica e conceitual do projeto de análise de redes olímpicas.

---

## 📚 Documentos Mantidos

### Casos de Estudo
- **`casos_de_estudo_FINAL.md`** - Documentação dos 12 casos de estudo selecionados (6 pares M/F)
- **`casos_de_estudo_selecionados.md`** - [VERIFICAR] Possível duplicata

### Explicações Conceituais
- **`explicacao_rede_bipartida_orientadora.md`** - Explicação sobre modelagem de redes para orientadora
- **`possibilidades_modelagem_redes.md`** - Diferentes abordagens de modelagem exploradas

### Validação e Sanitização
- **`SANITIZACAO_VALIDACAO_COMPLETA.md`** - Relatório completo de validação dados vs texto (2026-02-07)

---

## 🗑️ Documentos Removidos (2026-02-07)

Foram removidos 24 arquivos .md obsoletos de documentação de processo:
- Checklists de fases concluídas
- Planos de refatoração executados
- Relatórios de correções pontuais
- Documentos de decisões já implementadas

**Motivo:** Esses documentos eram úteis durante o desenvolvimento mas tornaram-se obsoletos após implementação completa.

**Backups:** Caso necessário, consultar commits anteriores do Git.

---

## 📁 Estrutura de Dados

### Dados Válidos (133 redes per-event)
- `main/results_all_mining/` - Dados minerados das 133 redes
  - `consolidated_all_networks.csv` - Atletas e métricas
  - `consolidated_all_edges.csv` - Arestas das redes
  - `network_metadata.csv` - Metadata das redes
  - `communities_all_networks.csv` - Comunidades detectadas
  - `community_hierarchy_per_event.csv` - Hierarquia de comunidades
  - `rivalries_per_event.csv` - Rivalidades por evento

### Backups
- `*_BACKUP_with_original.csv` - Backups antes da remoção das 16 redes "original" inválidas

---

## ⚠️ Mudanças Recentes

### 2026-02-07: Sanitização e Correção

1. **Removidas 16 redes "original" inválidas**
   - Eram agregações antigas incompatíveis com modelagem per-event
   - Mantidas apenas 133 redes per-event válidas

2. **Corrigida extração de ano**
   - Script de mineração agora extrai ano do campo "games" do GEXF
   - Corrige 30 redes que tinham year=0

3. **Sanitização de documentação**
   - Removidos 24 arquivos .md obsoletos
   - Mantidos apenas documentos conceituais e de referência

---

## 🔍 Como Usar Esta Documentação

**Para entender a modelagem:**
- Leia `explicacao_rede_bipartida_orientadora.md`
- Consulte `possibilidades_modelagem_redes.md` para abordagens alternativas

**Para validar dados:**
- Consulte `SANITIZACAO_VALIDACAO_COMPLETA.md`
- Verifique números citados no texto contra dados reais

**Para ver casos de estudo:**
- Leia `casos_de_estudo_FINAL.md`
- Contém detalhes dos 12 eventos analisados

---

## 📞 Contato

Para dúvidas sobre a documentação, consultar autor do TCC ou orientadora.
