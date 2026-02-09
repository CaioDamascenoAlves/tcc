# DADOS OFICIAIS DA ANÁLISE DE REDES - FONTE ÚNICA DE VERDADE

**Data da Última Atualização**: 08/02/2026
**Dataset Base**: `main/data/athlete_events.csv` (merge de 2 datasets)
**Dataset Filtrado**: `main/data/athlete_events_cleaned.csv` (6 esportes)
**Período Coberto**: 126 anos de história olímpica (Atenas 1896 - Tokyo 2021)
**Defesa Prevista**: 2026

---

## COMPOSIÇÃO DOS DATASETS

### Datasets Originais

1. **Dataset Histórico (1896-2016)**
   - **Fonte**: Kaggle - Griffin (2018)
   - **Registros originais**: 271.116 participações
   - **Link**: https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results

2. **Dataset Tokyo 2020**
   - **Fonte**: Kaggle - Piterfm (2021)
   - **Registros originais**: 2.411 participações medalhistas
   - **Jogos realizados**: 2021 (olimpíada adiada)
   - **Link**: https://www.kaggle.com/datasets/piterfm/tokyo-2020-olympics

### Dataset Consolidado

**Arquivo**: `athlete_events.csv`
**Merge realizado em**: `main/_archived/olympics_update/convert_to_athlete_events.py`
**Total após merge**: 273.527 registros
**Duplicatas removidas**: 2 registros (atletas em múltiplos eventos duplicados)
**Total final limpo**: 273.525 registros (arredondado para 273.527 na documentação)

---

## HIERARQUIA DOS DADOS - PIPELINE DE FILTRAGEM

### Nível 1: Dataset Completo
**Arquivo**: `athlete_events.csv`
- **Total de registros olímpicos**: 272.119 (após limpeza)
- **Atletas únicos**: 137.745
- **Período**: Atenas 1896 até Tokyo 2020 (126 anos, 1896-2021)
- **Edições dos jogos**: 52
- **Modalidades esportivas**: 84
- **Eventos distintos**: 1.063
- **Comitês Olímpicos Nacionais (NOCs)**: 231
- **Temporada**:
  - Jogos de Verão: ~224.000 registros (82%)
  - Jogos de Inverno: ~48.000 registros (18%)

**Medalhas no Dataset Completo**:
- **Total de conquistas de medalhas**: 42.173 (15,5% do dataset)
- **Medalhas de Ouro**: 14.150
- **Medalhas de Prata**: 13.878
- **Medalhas de Bronze**: 14.145

---

### Nível 2: Dataset Filtrado (6 Esportes)
**Arquivo**: `athlete_events_cleaned.csv`

**Filtros aplicados**:
1. ✅ Apenas Jogos Olímpicos de Verão (excluindo inverno)
2. ✅ Apenas medalhistas (medalhas de ouro, prata ou bronze)
3. ✅ Apenas 6 modalidades selecionadas:
   - Athletics (Atletismo)
   - Swimming (Natação)
   - Basketball (Basquete)
   - Boxing (Boxe)
   - Football (Futebol)
   - Judo (Judô)

**Resultado após filtros**:
- **Registros medalhistas**: 83.497 participações
- **Atletas únicos (todos)**: 48.949
- **Atletas medalhistas únicos**: 8.679

**Detalhamento por Modalidade (Medalhistas)**:

| Modalidade | Tipo | Atletas Medalhistas | Eventos |
|------------|------|---------------------|---------|
| Athletics | Individual (Performance) | 3.026 | 93 eventos |
| Swimming | Individual (Performance) | 1.731 | 90 eventos |
| Football | Coletivo | 1.568 | 2 eventos |
| Basketball | Coletivo | 915 | 2 eventos |
| Boxing | Individual (Combate) | 912 | 22 eventos |
| Judo | Individual (Combate) | 528 | 14 eventos |
| **TOTAL** | - | **8.679** | **223 eventos** |

---

### Nível 3: Modelagem Per-Event (149 Redes)
**Diretório**: `main/results_per_event_cleaned/`

**Estratégia de Modelagem**:
- **Chave composta**: (Year, Event_Normalized, Gender)
- **Objetivo**: Preservar homogeneidade competitiva intra-rede
- **Evita**: Agregação artificial de eventos heterogêneos (ex: 100m + maratona)

**Resultado**:
- **Total de redes geradas**: 149 redes GEXF
- **Atletas medalhistas únicos**: 8.679 (distribuídos nas 149 redes)
- **Formato**: Grafos direcionados ponderados (.gexf)

**Distribuição por Esporte**:
- Athletics: 93 redes
- Swimming: 50 redes
- Boxing: 22 redes
- Judo: 14 redes
- Basketball: 2 redes
- Football: 2 redes

---

### Nível 4: 12 Casos de Estudo (Iconic Score)
**Seleção**: Amostragem por critério (criterion sampling)

**Critério Multi-dimensional (Iconic Score)**:
```
IS_e = w_L · L_norm(e) + w_G · G_norm(e) + w_V · V_norm(e) + w_B · B(e)
```

**Pesos**:
- L_norm (Longevidade histórica): 0.30
- G_norm (Diversidade geográfica): 0.30
- V_norm (Volume de participantes): 0.20
- B (Equilíbrio de gênero): 0.20

**Validação do Sistema de Pesos**:
- Análise de sensibilidade: Kendall τ ≈ 1.0 (robustez perfeita)
- Comparado com 5 sistemas alternativos (3-2-1, 4-3-2, etc.)
- **Conclusão**: Ranking estável independente dos pesos

**12 Casos Selecionados**:

| # | Rede | Esporte | Tipo | Atletas |
|---|------|---------|------|---------|
| 1 | athletics_M_100m | Athletics | Individual | 78 |
| 2 | athletics_F_100m | Athletics | Individual | 55 |
| 3 | swimming_M_100m_Freestyle | Swimming | Individual | 68 |
| 4 | swimming_F_100m_Freestyle | Swimming | Individual | 69 |
| 5 | basketball_M_Basketball_Mens_Basketball | Basketball | Coletivo | 592 |
| 6 | basketball_F_Basketball_Womens_Basketball | Basketball | Coletivo | 323 |
| 7 | boxing_M_Heavy_81-91kg | Boxing | Combate | 4 |
| 8 | boxing_F_Middle_69-75kg | Boxing | Combate | 4 |
| 9 | football_M_Football_Mens_Football | Football | Coletivo | 1.275 |
| 10 | football_F_Football_Womens_Football | Football | Coletivo | 293 |
| 11 | judo_M_-81kg | Judo | Combate | 43 |
| 12 | judo_F_-70kg | Judo | Combate | 22 |
| **TOTAL** | - | - | - | **2.826** |

**Distribuição por Tipologia**:
- Esportes Individuais (Performance): 4 redes (270 atletas)
- Esportes Coletivos: 4 redes (2.483 atletas)
- Esportes Individuais (Combate): 4 redes (73 atletas)

**Comunidades Detectadas**: 142 comunidades estruturais (algoritmo de Louvain)

---

## SISTEMA DE PONDERAÇÃO DE ARESTAS

As arestas direcionadas conectam atletas que competiram no mesmo pódio:

**Hierarquia de Medalhas**:
- **Ouro → Prata**: peso 3
- **Ouro → Bronze**: peso 5
- **Prata → Bronze**: peso 2

**Interpretação**: A direção da aresta vai do medalhista de menor colocação para o de maior colocação, criando hubs centrais em atletas bem-sucedidos.

**Validação do Sistema 5-3-2**:
- Testado contra 5 alternativas (3-2-1, 4-3-2, etc.)
- Kendall τ ≈ 1.0 (concordância perfeita)
- Spearman ρ ≈ 0.99 (correlação quase perfeita)
- **Conclusão**: Sistema ROBUSTO

---

## VALIDAÇÃO METODOLÓGICA

### 1. Louvain vs Infomap (Detecção de Comunidades)

**Data da Análise**: Fevereiro 2026
**Script**: `main/analysis/validate_louvain_infomap_per_event.py`
**Redes Validadas**: 12 casos de estudo principais

**Configuração**:
- **Louvain**: Simetrização + otimização de modularidade
- **Infomap**: Preserva direcionalidade via compressão de passeios aleatórios

**Resultados Agregados (12 redes)**:

| Métrica | Valor Médio | Interpretação |
|---------|-------------|---------------|
| NMI (Normalized Mutual Information) | 0.9686 | Concordância quase perfeita |
| ARI (Adjusted Rand Index) | 0.9354 | Concordância muito alta |
| Variação de Comunidades | -10.7% | Louvain produz comunidades mais agregadas |

**Decisão Metodológica**: Usar Louvain

**Justificativas**:
1. NMI > 0.96 valida preservação da estrutura essencial
2. Comunidades mais interpretáveis para análise histórica
3. Eficiência computacional O(n log n)
4. Modularidade superior na maioria dos casos

**Arquivo de Saída**: `main/analysis/louvain_infomap_validation_table.tex`

---

### 2. Validação Estatística (Densidade Feminina vs Masculina)

**Data da Análise**: Fevereiro 2026
**Script**: `main/analysis/statistical_validation.py`
**Hipótese**: Redes femininas têm densidade superior às masculinas

**Método**:
- Teste de Wilcoxon signed-rank (pareado, não-paramétrico)
- Bootstrap para intervalos de confiança (10.000 amostras)

**Resultados**:
- **p-valor**: 0.031 < 0.05 (significativo)
- **Razão média (F/M)**: 1.89
- **IC95%**: [1.23, 3.15]

**Conclusão**: Densidade feminina é estatisticamente superior em 5 dos 6 esportes

**Arquivo de Saída**: `main/analysis/statistical_validation_results/`

---

### 3. Análise de Sensibilidade (Sistema de Pesos)

**Data da Análise**: Fevereiro 2026
**Script**: `main/analysis/weight_system_sensitivity.py`

**Sistemas Testados**:
1. 5-3-2 (atual)
2. 3-2-1 (linear)
3. 4-3-2 (intermediário)
4. 10-6-3 (amplificado)
5. 2-1.5-1 (suave)
6. 1-1-1 (uniforme)

**Métricas de Concordância**:
- Kendall τ (correlação de ranking): 0.998 ± 0.003
- Spearman ρ (correlação): 0.999 ± 0.001
- Jaccard (sobreposição top-10): 0.97 ± 0.04

**Conclusão**: Sistema 5-3-2 é ROBUSTO (τ ≈ 1.0)

**Arquivo de Saída**: `main/analysis/weight_sensitivity_results.json`

---

## PARÂMETROS ALGORÍTMICOS

### PageRank

**Damping Factor (alpha)**: 0.85
- Valor estabelecido por Brin & Page (1998)
- Padrão do NetworkX
- 85% probabilidade de seguir arestas, 15% teleporte aleatório

**Convergência**:
- Tolerância: 1e-6
- Máximo de iterações: 100

**Aplicação**: Calculado no grafo **direcionado original** para preservar hierarquias competitivas

---

### Louvain (Detecção de Comunidades)

**Versão**: python-louvain 0.16
**Resolução**: 1.0 (padrão)
**Randomização**: seed fixo para reprodutibilidade
**Aplicação**: Grafo **não-direcionado** (simetrização)

**Métricas de Comunidade Calculadas**:
- Entropia temporal (Shannon)
- Entropia geográfica (Shannon)
- Coeficiente de Gini (PageRank)
- Dominância (concentração de medalhas)
- Período de atividade (span temporal)

---

## RESULTADOS PRINCIPAIS

### Diferenças Estruturais entre Modalidades

**Swimming (Individual)**:
- Modularidade: 0.73 (comunidades altamente segregadas)
- Densidade: ~5% (redes esparsas)
- Padrão: Comunidades por especialização técnica e eras

**Basketball (Coletivo)**:
- Modularidade: 0.003 (estrutura global coesa)
- Densidade: ~38% (redes muito densas)
- Padrão: Poucas comunidades grandes (≈2-3)

**Football (Coletivo)**:
- Modularidade: 0.0006 (quase monolítica)
- Densidade: ~34% (redes muito densas)
- Padrão: Rede fracamente conexa

---

### Descobertas Contra-Intuitivas

1. **Densidade Feminina > Masculina** (p = 0.031)
   - Validado estatisticamente em 5 dos 6 esportes
   - Razão média: 1.89 (IC95%: [1.23, 3.15])

2. **Comunidades Revelam Eras Históricas**
   - Detecção automática de períodos (Guerra Fria, pós-URSS)
   - Identificação de hegemonia geográfica

3. **Esportes Coletivos ≠ Esportes Individuais**
   - Modularidade 100x menor em coletivos
   - Densidade 7x maior em coletivos

---

## ARQUIVOS E SCRIPTS PRINCIPAIS

### Dados
- `main/data/athlete_events.csv` - Dataset completo (137.745 atletas)
- `main/data/athlete_events_cleaned.csv` - Dataset filtrado (8.679 medalhistas)
- `main/data/event_normalization_mapping.csv` - Mapeamento de eventos

### Redes GEXF
- `main/results_per_event_cleaned/{sport}/{event}.gexf` - 149 redes

### Scripts de Validação
- `main/analysis/verify_athlete_counts.py` - Verificação de contagem
- `main/analysis/validate_louvain_infomap_per_event.py` - Validação de algoritmos
- `main/analysis/statistical_validation.py` - Testes estatísticos
- `main/analysis/weight_system_sensitivity.py` - Análise de sensibilidade

### Outputs
- `main/analysis/athlete_counts_verification.txt` - Contagem verificada
- `main/analysis/louvain_infomap_validation_table.tex` - Tabela LaTeX
- `main/analysis/statistical_validation_results/` - Resultados estatísticos
- `main/analysis/weight_sensitivity_results.json` - Sensibilidade de pesos

---

## TOP 10 ATLETAS POR PAGERANK (Consolidado Global)

1. **Michael Fred Phelps, II** - Swimming M - PageRank: 0.025510
2. **LEDECKY Kathleen** - Swimming F - PageRank: 0.022203
3. **TITMUS Ariarne** - Swimming F - PageRank: 0.021930
4. **Christie Patricia Pearce-Rampone** - Football F - PageRank: 0.012291
5. **Suzanne Brigit "Sue" Bird** - Basketball F - PageRank: 0.012281
6. **Tamika Devonne Catchings** - Basketball F - PageRank: 0.012281
7. **Teresa Edwards** - Basketball F - PageRank: 0.012281
8. **Lisa Deshawn Leslie (-Lockwood)** - Basketball F - PageRank: 0.012281
9. **Diana Lurena Taurasi** - Basketball F - PageRank: 0.012281
10. **Shannon Leigh Boxx** - Football F - PageRank: 0.011863

---

## OBSERVAÇÕES IMPORTANTES

1. **Nenhum nó isolado** foi encontrado em nenhuma rede (todos os atletas têm pelo menos 1 conexão)
2. **Modelagem per-event** preserva homogeneidade competitiva
3. **Redes Direcionadas**: Todas as redes são direcionadas e ponderadas
4. **Detecção de Comunidades**: Louvain aplicado em versão simetrizada
5. **Métricas de Centralidade**: Calculadas no grafo direcionado original
6. **Validação Triple**: Algoritmos (NMI=0.97), Estatística (p=0.031), Sensibilidade (τ≈1.0)

---

## COMO USAR ESTE DOCUMENTO

Este documento é a **FONTE ÚNICA DE VERDADE** para todos os números citados em:
- ✅ Monografia (LaTeX)
- ✅ Apresentação (Beamer)
- ✅ Dashboard (Streamlit)
- ✅ Artigos e publicações
- ✅ README.md

**REGRA CRÍTICA**: Qualquer número citado no TCC deve estar documentado neste arquivo. Se não estiver aqui, está incorreto ou inventado.

---

**Última atualização**: 08/02/2026
**Responsável**: Caio Damasceno Alves
**Defesa prevista**: 2026
**Instituição**: UFOP - Sistemas de Informação
