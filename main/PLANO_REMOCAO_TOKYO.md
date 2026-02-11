# PLANO DE REMOÇÃO DOS DADOS DE TOKYO 2020/2021

**Data:** 2026-02-10
**Objetivo:** Remover completamente os dados de Tokyo 2020 (realizados em 2021) devido a problemas críticos de normalização de nomes.
**Escopo:** Reverter para base histórica limpa (1896-2016) e regenerar toda a pipeline.

---

## 📋 TODO - CHECKLIST GERAL

### **FASE 1: Limpeza e Preparação de Dados**
- [ ] 1.1. Criar backup da base atual
- [ ] 1.2. Filtrar athlete_events.csv original (remover Year == 2021)
- [ ] 1.3. Criar athlete_events_clean.csv (1896-2016 apenas)
- [ ] 1.4. Validar dados limpos (verificar anos, consistência)
- [ ] 1.5. Deletar athlete_events_normalized.csv

### **FASE 2: Atualização de Scripts**
- [ ] 2.1. Atualizar 01b_network_generation_per_event.py → usar athlete_events_clean.csv
- [ ] 2.2. Verificar outros scripts que usam athlete_events.csv
- [ ] 2.3. Atualizar imports e caminhos de dados

### **FASE 3: Regeneração de Redes (GEXFs)**
- [ ] 3.1. Limpar diretório results/ (backup antes!)
- [ ] 3.2. Executar 01b_network_generation_per_event.py
- [ ] 3.3. Validar GEXFs gerados (verificar anos, quantidade)

### **FASE 4: Regeneração de Mineração**
- [ ] 4.1. Limpar results_all_mining/ (backup antes!)
- [ ] 4.2. Executar 12_mine_all_networks.py
- [ ] 4.3. Validar CSVs consolidados (verificar anos máximo = 2016)

### **FASE 5: Regeneração de Análises**
- [ ] 5.1. Executar temporal_dynamics_12networks.py
- [ ] 5.2. Executar geographic_dominance_12networks.py
- [ ] 5.3. Executar outlier_analysis_12networks.py
- [ ] 5.4. Verificar se todas as figuras foram regeneradas

### **FASE 6: Atualização da Monografia**
- [ ] 6.1. Atualizar introducao.tex (remover menção a Tokyo 2020)
- [ ] 6.2. Atualizar revisao.tex (se mencionar Tokyo)
- [ ] 6.3. Atualizar desenvolvimento.tex (metodologia e período temporal)
- [ ] 6.4. Atualizar resultados.tex (todos os números e estatísticas)
- [ ] 6.5. Atualizar conclusao.tex (se mencionar Tokyo)
- [ ] 6.6. Atualizar resumo/abstract (período temporal)
- [ ] 6.7. Compilar LaTeX e verificar PDF

### **FASE 7: Validação Final**
- [ ] 7.1. Verificar que não há Year > 2016 em nenhum CSV
- [ ] 7.2. Verificar que não há menção a 2020/2021 na monografia
- [ ] 7.3. Verificar que todos os números batem (atletas, redes, etc.)
- [ ] 7.4. Testar dashboard com novos dados
- [ ] 7.5. Criar commit Git com todas as mudanças

---

## 📊 IMPACTO ESPERADO

### **Antes (com Tokyo 2020/2021):**
- Período: 1896-2021 (125 anos)
- Último evento: Tokyo 2020 (realizado em 2021)
- Total de atletas: ~19,103 (estimado)
- Problema: Normalização de nomes inconsistente

### **Depois (sem Tokyo):**
- Período: 1896-2016 (120 anos)
- Último evento: Rio 2016
- Total de atletas: ~16,710 (estimado, menos ~2,393 de Tokyo)
- Benefício: Base 100% consistente e limpa

---

## 🔍 SCRIPTS E ARQUIVOS IDENTIFICADOS

### **1. Scripts de Pipeline (src/pipeline/)**
```
01b_network_generation_per_event.py  ← PRINCIPAL para GEXFs
  └─ Usa: athlete_events.csv
  └─ Gera: results/{sport}/*.gexf
```

### **2. Scripts de Análise (src/analysis/)**
```
12_mine_all_networks.py              ← PRINCIPAL para mineração
  └─ Lê: results/**/*.gexf
  └─ Gera: results_all_mining/*.csv

temporal_dynamics_12networks.py      ← Análise temporal
  └─ Lê: results_all_mining/consolidated_all_*.csv
  └─ Gera: results_complete_mining/data/temporal_*.csv
          results_complete_mining/figures/temporal_*.png

geographic_dominance_12networks.py   ← Análise geográfica
  └─ Lê: results_all_mining/consolidated_all_*.csv
  └─ Gera: results_complete_mining/data/geographic_*.csv
          results_complete_mining/figures/geographic_*.png

outlier_analysis_12networks.py       ← Análise de outliers
  └─ Lê: results_complete_mining/data/master_comparative_table.csv
  └─ Gera: results_complete_mining/data/outlier_*.csv
          results_complete_mining/figures/outlier_*.png
```

### **3. Dados Consolidados (results_all_mining/)**
```
consolidated_all_networks.csv        ← Todos os atletas com métricas
consolidated_all_edges.csv           ← Todas as arestas
network_metadata.csv                 ← Metadata das 149 redes
communities_all_networks.csv         ← Comunidades
```

### **4. Dados de Análises (results_complete_mining/data/)**
```
pagerank.csv
betweenness.csv
communities.csv
global_metrics.csv
temporal_entropy.csv
geographic_dominance.csv
outlier_detection.csv
... (30+ arquivos)
```

### **5. Figuras (results_complete_mining/figures/)**
```
temporal_*.png                       ← Gráficos de evolução temporal
geographic_*.png                     ← Mapas de dominância
outlier_*.png                        ← Análises de outliers
```

### **6. Seções da Monografia**
```
monografia/textuais/introducao.tex   ← Menciona "125 anos" e "Tokyo 2020"
monografia/textuais/revisao.tex      ← Verificar menções
monografia/textuais/desenvolvimento.tex ← Metodologia e período
monografia/textuais/resultados.tex   ← TODOS os números e estatísticas
monografia/textuais/conclusao.tex    ← Síntese final
monografia/elementos-pre-textuais/resumo.tex ← Período temporal
```

---

## 🔧 COMANDOS PRINCIPAIS

### **1. Criar dados limpos (sem Tokyo):**
```python
import pandas as pd

# Carregar base original
df = pd.read_csv('data/athlete_events.csv')

# Filtrar: manter apenas até 2016
df_clean = df[df['Year'] <= 2016].copy()

# Salvar
df_clean.to_csv('data/athlete_events_clean.csv', index=False)

print(f"Registros originais: {len(df):,}")
print(f"Registros limpos (até 2016): {len(df_clean):,}")
print(f"Removidos (Tokyo 2021): {len(df) - len(df_clean):,}")
```

### **2. Regenerar GEXFs:**
```bash
cd /home/caio/Desktop/tcc/main
python3 src/pipeline/01b_network_generation_per_event.py
```

### **3. Regenerar Mineração:**
```bash
python3 src/analysis/12_mine_all_networks.py
```

### **4. Regenerar Análises:**
```bash
python3 src/analysis/temporal_dynamics_12networks.py
python3 src/analysis/geographic_dominance_12networks.py
python3 src/analysis/outlier_analysis_12networks.py
```

### **5. Compilar LaTeX:**
```bash
cd monografia
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

---

## 📝 MUDANÇAS NO TEXTO

### **introducao.tex - Linha 8:**
**ANTES:**
> "Desde a primeira olimpíada moderna em Atenas 1896, mais de 137 mil atletas competiram por medalhas olímpicas ao longo de 125 anos de história (até Tokyo 2020, realizado em 2021)."

**DEPOIS:**
> "Desde a primeira olimpíada moderna em Atenas 1896, mais de 135 mil atletas competiram por medalhas olímpicas ao longo de 120 anos de história (até Rio 2016)."

### **introducao.tex - Linha 16:**
**ANTES:**
> "Esta abordagem gerou 149 redes competitivas direcionadas e ponderadas construídas pela chave composta (Ano, Evento_Normalizado)"

**DEPOIS:**
> "Esta abordagem gerou [NÚMERO_NOVO] redes competitivas direcionadas e ponderadas construídas pela chave composta (Ano, Evento_Normalizado)"

### **desenvolvimento.tex:**
- Atualizar seção de "Coleta de Dados"
- Mudar período de "1896-2021" para "1896-2016"
- Remover qualquer menção a "pandemia", "adiamento", ou "Tokyo 2020"

### **resultados.tex:**
- Atualizar TODOS os números estatísticos
- Recontar redes, atletas, comunidades, arestas
- Regenerar todas as tabelas

---

## ⚠️ PONTOS DE ATENÇÃO

### **1. Backups Críticos:**
- `results/` → `results_BACKUP_COM_TOKYO/`
- `results_all_mining/` → `results_all_mining_BACKUP_COM_TOKYO/`
- `athlete_events.csv` → `athlete_events_COM_TOKYO.csv`

### **2. Validações Necessárias:**
- Verificar que Year máximo = 2016 em todos os CSVs
- Conferir que número de redes reduziu (Tokyo contribuía com ~10-15 redes)
- Garantir que não há "2020" ou "2021" em nenhum campo 'games'

### **3. Números que Vão Mudar:**
- Total de atletas: redução de ~2,393 (atletas de Tokyo)
- Total de redes: redução de ~10-15 redes
- Período temporal: 125 anos → 120 anos
- Anos de análise: 1896-2021 → 1896-2016

---

## 🎯 RESULTADO ESPERADO

**Ao final deste plano:**

✅ Base de dados 100% limpa e consistente (1896-2016)
✅ Todos os GEXFs regenerados sem Tokyo
✅ Todos os CSVs consolidados atualizados
✅ Todas as análises reprocessadas
✅ Todas as figuras regeneradas
✅ Monografia completamente atualizada
✅ Nenhuma menção a Tokyo 2020/2021
✅ Números e estatísticas corretos
✅ Dashboard funcional com dados limpos

**Benefícios:**
- ✅ Eliminação do problema de normalização de nomes
- ✅ Base histórica consistente por 120 anos
- ✅ Todos os atletas multi-edição corretamente conectados
- ✅ Análises confiáveis e replicáveis

---

## 🚀 PRÓXIMOS PASSOS

1. **Revisar e aprovar este plano**
2. **Executar FASE 1** (criar dados limpos)
3. **Executar FASES 2-5** (regenerar pipeline)
4. **Executar FASE 6** (atualizar monografia)
5. **Executar FASE 7** (validação final)

---

**Estimativa de tempo:**
- Fase 1-5: ~30-45 minutos (automático)
- Fase 6: ~2-3 horas (manual, revisão de texto)
- Fase 7: ~30 minutos (validação)

**Total: ~3-4 horas de trabalho**
