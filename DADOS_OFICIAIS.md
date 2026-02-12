# DADOS OFICIAIS DA ANÁLISE DE REDES - FONTE ÚNICA DE VERDADE

**Data da Última Atualização**: 12/02/2026
**Dataset Base**: `main/data/athlete_events.csv` (Griffin 2018)
**Dataset Filtrado**: `main/data/athlete_events_cleaned.csv` (6 esportes)
**Período Coberto**: 120 anos de história olímpica (Atenas 1896 - Rio 2016)
**Defesa Prevista**: 2026

---

## COMPOSIÇÃO DOS DATASETS

### Dataset Original

**Dataset Histórico (1896-2016)**
- **Fonte**: Kaggle - Griffin (2018)
- **Registros originais**: 271.116 participações
- **Link**: https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results

### Dataset Limpo

**Arquivo**: `athlete_events.csv`
**Limpeza**: Remoção de duplicatas e registros inválidos
**Total final limpo**: 269.718 registros

---

## HIERARQUIA DOS DADOS - PIPELINE DE FILTRAGEM

### Nível 1: Dataset Completo
**Arquivo**: `athlete_events.csv`
- **Total de registros olímpicos**: 269.718 (após limpeza)
- **Atletas únicos**: 135.571
- **Período**: Atenas 1896 até Rio 2016 (120 anos)
- **Edições dos jogos**: 51
- **Modalidades esportivas**: 66
- **Eventos distintos**: 765
- **Comitês Olímpicos Nacionais (NOCs)**: 230
- **Temporada**: Apenas Jogos de Verão

**Medalhas no Dataset Completo**:
- **Total de conquistas de medalhas**: 39.772 (14,7% do dataset)
- **Medalhas distribuídas**: Ouro, Prata e Bronze ao longo de 120 anos

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
- **Atletas medalhistas únicos**: 9.378

**Detalhamento por Modalidade (Medalhistas)**:

| Modalidade | Tipo | Atletas Medalhistas | Descrição |
|------------|------|---------------------|-----------|
| Athletics | Individual (Performance) | ~3.000 | Corrida, saltos, arremessos |
| Swimming | Individual (Performance) | ~1.700 | Diversos estilos e distâncias |
| Football | Coletivo | ~1.600 | Futebol masculino e feminino |
| Basketball | Coletivo | ~900 | Basquete masculino e feminino |
| Boxing | Individual (Combate) | ~900 | Diversas categorias de peso |
| Judo | Individual (Combate) | ~500 | Categorias de peso por gênero |
| **TOTAL** | - | **9.378** | Seis modalidades selecionadas |

---

### Nível 3: Modelagem Per-Event (123 Redes)
**Diretório**: `main/results_all_mining/`

**Estratégia de Modelagem**:
- **Chave composta**: (Year, Event_Normalized)
- **Objetivo**: Preservar homogeneidade competitiva intra-rede
- **Evita**: Agregação artificial de eventos heterogêneos (ex: 100m + maratona)

**Resultado**:
- **Total de redes geradas**: 123 redes competitivas
- **Atletas medalhistas únicos**: 9.378 (distribuídos nas 123 redes)
- **Formato**: Grafos direcionados ponderados

**Distribuição por Esporte**:
- Athletics: Múltiplas redes por evento específico
- Swimming: Múltiplas redes por estilo/distância
- Boxing: Redes por categoria de peso
- Judo: Redes por categoria de peso
- Basketball: 2 redes (M/F)
- Football: 2 redes (M/F)

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

| # | Rede | Esporte | Tipo |
|---|------|---------|------|
| 1 | Athletics 100m M | Athletics | Individual (Performance) |
| 2 | Athletics 100m F | Athletics | Individual (Performance) |
| 3 | Swimming 100m Freestyle M | Swimming | Individual (Performance) |
| 4 | Swimming 100m Freestyle F | Swimming | Individual (Performance) |
| 5 | Basketball M | Basketball | Coletivo |
| 6 | Basketball F | Basketball | Coletivo |
| 7 | Boxing Welterweight M | Boxing | Individual (Combate) |
| 8 | Boxing Middleweight F | Boxing | Individual (Combate) |
| 9 | Football M | Football | Coletivo |
| 10 | Football F | Football | Coletivo |
| 11 | Judo -90kg M | Judo | Individual (Combate) |
| 12 | Judo -70kg F | Judo | Individual (Combate) |

**Distribuição por Tipologia**:
- Esportes Individuais (Performance): 4 redes
- Esportes Coletivos: 4 redes
- Esportes Individuais (Combate): 4 redes

**Comunidades Detectadas**: Múltiplas comunidades estruturais (algoritmo de Louvain)

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

**Última atualização**: 12/02/2026
**Responsável**: Caio Damasceno Alves
**Defesa prevista**: 2026
**Instituição**: UFOP - Sistemas de Informação
**Período dos dados**: 1896-2016 (120 anos - Atenas até Rio)
