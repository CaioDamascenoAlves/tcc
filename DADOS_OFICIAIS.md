# DADOS OFICIAIS DA ANÁLISE DE REDES - FONTE ÚNICA DE VERDADE

**Data da Execução**: 14/11/2025
**Pipeline**: `main/src/pipeline/01_network_generation.py`
**Fonte dos Dados**: `main/data/athlete_events.csv` (merge de 2 datasets)
**Período Coberto**: 126 anos de história olímpica (Atenas 1896 - Tokyo 2021)

**Composição do Dataset**:
- **Dataset Base**: 1896-2016 (Kaggle - Griffin 2018) - 271.116 registros (original)
- **Dataset Tokyo 2020**: Jogos de 2021 (Kaggle - Piterfm 2021) - 2.411 registros (original)
- **Merge realizado em**: `main/_archived/olympics_update/convert_to_athlete_events.py`
- **Total após merge**: 273.527 registros (antes da limpeza)
- **Duplicatas removidas**: 1.408 registros (atletas em múltiplos eventos duplicados)
- **Total final limpo**: 272.119 registros

---

## ESTATÍSTICAS GERAIS

### Dataset Original Completo (athlete_events.csv - após limpeza)
- **Total de registros olímpicos**: 272.119 (após remover 1.408 duplicatas)
- **Atletas únicos**: 137.745
- **Período**: 1896-2021 (126 anos)
- **Edições dos jogos**: 52
- **Modalidades esportivas**: 84
- **Eventos distintos**: 1.063
- **Comitês Olímpicos Nacionais (NOCs)**: 231
- **Temporada**:
  - Jogos de Verão: ~224.000 registros (82%)
  - Jogos de Inverno: ~48.000 registros (18%)

### Medalhas no Dataset Completo
- **Total de conquistas de medalhas**: 42.173 (15.5% do dataset)
- **Medalhas de Ouro**: 14.150
- **Medalhas de Prata**: 13.878
- **Medalhas de Bronze**: 14.145

### Filtros Aplicados no Pipeline
**Critérios de Seleção**:
- Apenas medalhistas (42.194 registros)
- Apenas jogos de verão (excluindo inverno)
- Apenas 3 esportes: Swimming, Basketball, Football
- Separação por gênero (masculino e feminino)

**Resultado Após Filtros**:
- **Medalhistas dos 3 esportes selecionados**: 6.113
- **Registros duplicados removidos**: 2
- **Registros após limpeza**: 6.111
- **Atletas únicos (inicial)**: 4.264
- **Pódios válidos**: 662

### Dataset Analisado (após geração de redes)
- **Total de atletas nas redes**: 4.659
- **Distribuição por sexo**:
  - Masculino: 3.059 atletas
  - Feminino: 1.600 atletas
- **Distribuição por esporte (atletas únicos antes de criar redes)**:
  - Swimming: 1.781 atletas (90 eventos)
  - Basketball: 915 atletas (2 eventos)
  - Football: 1.568 atletas (2 eventos)

---

## ESPORTES ANALISADOS

### 1. SWIMMING (Natação)
**Classificação**: Mixed (eventos individuais + coletivos)
- **Eventos individuais**: 74
- **Eventos coletivos**: 16
- **Total de registros**: 3.240

#### Swimming Masculino - Individual
- **Atletas**: 511 nós
- **Conexões**: 10.708 arestas
- **Densidade**: 0.041 (4.1%)
- **Grau médio**: 41.91
- **Grau mínimo**: 1
- **Grau máximo**: 174
- **Componentes fortemente conexos**: 294
- **Componentes fracamente conexos**: 13
- **Modularidade**: 0.731
- **Comunidades detectadas**: 17
- **Tamanho médio de comunidade**: 30.06 atletas

#### Swimming Masculino - Team (Revezamentos)
- **Atletas**: 681 nós
- **Conexões**: 69.210 arestas
- **Densidade**: 0.149 (14.9%)
- **Grau médio**: 203.26
- **Grau mínimo**: 8
- **Grau máximo**: 656
- **Componentes fortemente conexos**: 433
- **Componentes fracamente conexos**: 3
- **Modularidade**: 0.372
- **Comunidades detectadas**: 7
- **Tamanho médio de comunidade**: 97.29 atletas

#### Swimming Feminino - Individual
- **Atletas**: 411 nós
- **Conexões**: 8.974 arestas
- **Densidade**: 0.053 (5.3%)
- **Grau médio**: 43.67
- **Grau mínimo**: 2
- **Grau máximo**: 144
- **Componentes fortemente conexos**: 224
- **Componentes fracamente conexos**: 4
- **Modularidade**: 0.608
- **Comunidades detectadas**: 9
- **Tamanho médio de comunidade**: 45.67 atletas

#### Swimming Feminino - Team (Revezamentos)
- **Atletas**: 573 nós
- **Conexões**: 56.077 arestas
- **Densidade**: 0.171 (17.1%)
- **Grau médio**: 195.73
- **Grau mínimo**: 11
- **Grau máximo**: 615
- **Componentes fortemente conexos**: 345
- **Componentes fracamente conexos**: 2
- **Modularidade**: 0.299
- **Comunidades detectadas**: 4
- **Tamanho médio de comunidade**: 143.25 atletas

#### Swimming - Rede Híbrida (Individual + Team combinados)
- **Atletas**: 1.781 nós
- **Conexões**: 142.975 arestas

---

### 2. BASKETBALL (Basquete)
**Classificação**: Team Only (apenas eventos coletivos)
- **Eventos coletivos**: 2
- **Total de registros**: 1.152

#### Basketball Masculino
- **Atletas**: 592 nós
- **Conexões**: 133.320 arestas
- **Densidade**: 0.381 (38.1%)
- **Grau médio**: 450.41
- **Grau mínimo**: 404
- **Grau máximo**: 832
- **Componentes fortemente conexos**: 353
- **Componentes fracamente conexos**: 1 (rede fracamente conexa)
- **Modularidade**: 0.003
- **Comunidades detectadas**: 2
- **Tamanho médio de comunidade**: 296.0 atletas

#### Basketball Feminino
- **Atletas**: 323 nós
- **Conexões**: 41.164 arestas
- **Densidade**: 0.396 (39.6%)
- **Grau médio**: 254.89
- **Grau mínimo**: 228
- **Grau máximo**: 466
- **Componentes fortemente conexos**: 181
- **Componentes fracamente conexos**: 1 (rede fracamente conexa)
- **Modularidade**: 0.005
- **Comunidades detectadas**: 3
- **Tamanho médio de comunidade**: 107.67 atletas

---

### 3. FOOTBALL (Futebol)
**Classificação**: Team Only (apenas eventos coletivos)
- **Eventos coletivos**: 2
- **Total de registros**: 1.703

#### Football Masculino
- **Atletas**: 1.275 nós
- **Conexões**: 556.966 arestas
- **Densidade**: 0.343 (34.3%)
- **Grau médio**: 873.67
- **Grau mínimo**: 830
- **Grau máximo**: 1.706
- **Componentes fortemente conexos**: 845
- **Componentes fracamente conexos**: 1 (rede fracamente conexa)
- **Modularidade**: 0.001
- **Comunidades detectadas**: 2
- **Tamanho médio de comunidade**: 637.5 atletas

#### Football Feminino
- **Atletas**: 293 nós
- **Conexões**: 31.557 arestas
- **Densidade**: 0.369 (36.9%)
- **Grau médio**: 215.41
- **Grau mínimo**: 198
- **Grau máximo**: 414
- **Componentes fortemente conexos**: 173
- **Componentes fracamente conexos**: 1 (rede fracamente conexa)
- **Modularidade**: 0.002
- **Comunidades detectadas**: 3
- **Tamanho médio de comunidade**: 97.67 atletas

---

## TOP 10 ATLETAS POR PAGERANK

1. **Michael Fred Phelps, II** - Swimming M - Gold - PageRank: 0.025510
2. **LEDECKY Kathleen** - Swimming F - Gold - PageRank: 0.022203
3. **TITMUS Ariarne** - Swimming F - Silver - PageRank: 0.021930
4. **Christie Patricia Pearce-Rampone** - Football F - Gold - PageRank: 0.012291
5. **Suzanne Brigit "Sue" Bird** - Basketball F - Gold - PageRank: 0.012281
6. **Tamika Devonne Catchings** - Basketball F - Gold - PageRank: 0.012281
7. **Teresa Edwards** - Basketball F - Gold - PageRank: 0.012281
8. **Lisa Deshawn Leslie (-Lockwood)** - Basketball F - Gold - PageRank: 0.012281
9. **Diana Lurena Taurasi** - Basketball F - Gold - PageRank: 0.012281
10. **Shannon Leigh Boxx** - Football F - Gold - PageRank: 0.011863

---

## SISTEMA DE PONDERAÇÃO DE ARESTAS

As arestas direcionadas conectam atletas que competiram no mesmo evento:
- **Ouro ← Prata**: peso 3
- **Ouro ← Bronze**: peso 5
- **Prata ← Bronze**: peso 2

Isso cria redes onde atletas bem-sucedidos se tornam hubs centrais recebendo conexões de competidores que derrotaram.

---

## ARQUIVOS GERADOS

### Arquivos Consolidados
- `main/results/consolidated_sports_network_analysis.csv` - 4.660 linhas (todos os atletas com métricas)
- `main/results/consolidated_edges_data.csv` - Todas as arestas para análise CDF/CCDF
- `main/results/all_network_summaries.json` - Estatísticas resumidas de todas as redes

### Arquivos por Esporte/Gênero
Cada combinação esporte-gênero-tipo gera:
- `{sport}_{sex}_{type}_detailed_metrics.csv` - Métricas detalhadas dos atletas
- `{sport}_{sex}_{type}.gexf` - Arquivo de rede para Gephi/visualização
- `{sport}_network_summary.json` - Resumo estatístico da rede

---

## PADRÕES OBSERVADOS

### Esportes Individuais vs Coletivos
- **Individuais (Swimming)**: Modularidade alta (0.6-0.7), muitas comunidades pequenas
- **Coletivos (Basketball/Football)**: Modularidade baixa (0.001-0.005), poucas comunidades grandes

### Densidade das Redes
- **Swimming Individual**: 4-5% (redes esparsas)
- **Swimming Team**: 15-17% (redes moderadamente densas)
- **Basketball/Football**: 34-40% (redes muito densas)

### Conectividade
- **Esportes Coletivos**: Redes fracamente conexas (1 componente fraco)
- **Esportes Individuais**: Múltiplos componentes (fragmentação por eras/regiões)

---

## VALIDAÇÃO METODOLÓGICA: LOUVAIN vs INFOMAP

**Data da Análise**: 15/11/2025
**Script**: `main/analysis/compare_community_metrics.py`
**Rede de Validação**: Swimming Masculino (caso crítico - esporte individual, 126 anos de história)

### Configuração do Teste
- **Nós**: 973 atletas
- **Arestas direcionadas**: 5.572
- **Período**: 1896-2021
- **Algoritmos comparados**:
  - **Louvain**: Simetrização + otimização de modularidade
  - **Infomap**: Preserva direcionalidade via compressão de passeios aleatórios

### Resultados da Comparação

#### Número de Comunidades
- **Louvain**: 39 comunidades
- **Infomap**: 68 comunidades (+74% fragmentação)

#### Qualidade da Partição
- **Louvain Modularidade**: 0.7973 ✓ SUPERIOR
- **Infomap Modularidade**: 0.7423 (-6.9%)

#### Concordância Estrutural
- **NMI (Normalized Mutual Information)**: 0.8521 (ALTA concordância)
- **ARI (Adjusted Rand Index)**: 0.7832
- **Interpretação**: Ambos capturam essencialmente a mesma estrutura comunitária

#### Tamanho Médio das Comunidades
- **Louvain**: 24.9 ± 38.8 atletas
- **Infomap**: 14.3 ± 16.0 atletas
- **Conclusão**: Louvain produz comunidades mais interpretáveis para análise histórica (125 anos)

#### Métricas Agregadas das Comunidades

| Métrica | Louvain | Infomap | Diferença |
|---------|---------|---------|-----------|
| Entropia Temporal | 0.253 ± 0.449 | 0.183 ± 0.364 | -27.7% |
| Entropia Geográfica | 1.697 ± 0.894 | 1.656 ± 0.686 | -2.4% ✓ |
| Gini PageRank | 0.296 ± 0.103 | 0.316 ± 0.125 | +6.7% ✓ |

✓ = Diferença pequena (< 7%)

### Conclusão da Validação

**DECISÃO: Usar Louvain com Simetrização**

**Justificativas Científicas**:
1. **Modularidade superior** (0.7973 > 0.7423, +7.4%)
2. **NMI alto** (0.8521) valida que simetrização preserva estrutura essencial
3. **Métricas agregadas similares** (diferenças < 7% em geografia e Gini)
4. **Comunidades mais interpretáveis** (25 vs 14 atletas médio)
5. **Eficiência computacional** O(n log n) permite escalar para multi-esporte

**Ressalva Importante**: Métricas de centralidade individual (PageRank, betweenness) são calculadas no grafo **direcionado original** para preservar hierarquias de dominância competitiva.

**Arquivo de Saída**: `main/analysis/louvain_vs_infomap_summary.json`

---

## OBSERVAÇÕES IMPORTANTES

1. **Nenhum nó isolado** foi encontrado em nenhuma rede (todos os atletas têm pelo menos 1 conexão)
2. **Swimming é tratado como Mixed**: Separação em redes individual e team para análise adequada
3. **Basketball e Football são Team Only**: Apenas eventos coletivos
4. **Redes Direcionadas**: Todas as redes são direcionadas e ponderadas
5. **Algoritmo de Comunidades**: Louvain aplicado em versão não-direcionada (validado empiricamente vs Infomap)
6. **Centralidade Individual**: PageRank e betweenness calculados no grafo direcionado original

---

## COMO USAR ESTE DOCUMENTO

Este documento é a **FONTE ÚNICA DE VERDADE** para todos os números citados em:
- Monografia (LaTeX)
- Apresentação (Beamer)
- Dashboard (Streamlit)
- Artigos e publicações

**REGRA**: Qualquer número citado deve estar documentado aqui. Se não estiver, é provável que esteja incorreto ou inventado.

---

**Última atualização**: 14/11/2025
**Pipeline executado em**: `main/src/pipeline/01_network_generation.py`
