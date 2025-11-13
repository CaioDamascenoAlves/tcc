# Pipeline - Scripts de Análise

Scripts numerados para execução sequencial do pipeline de análise de redes olímpicas.

## Ordem de Execução

```bash
cd src/pipeline

# 1. Geração das redes (OBRIGATÓRIO - executa primeiro)
python 01_network_generation.py

# 2. Análises adicionais (podem ser executadas em paralelo)
python 02a_community_enrichment.py
python 02b_medal_profile.py
python 02c_connectivity.py
python 02d_hierarchy.py
python 02e_rivalries.py
```

## Scripts

### `01_network_generation.py` - Geração de Redes

**Script principal** que gera todas as redes a partir dos dados olímpicos.

**Entrada:**
- `data/athlete_events.csv` - Dataset olímpico completo

**Saída:**
- `results/networks/consolidated_athletes.csv` - Métricas de todos os atletas
- `results/networks/consolidated_edges.csv` - Todas as arestas
- `results/networks/summaries.json` - Resumos estatísticos
- `results/networks/{sport}/{sport}_{sex}_{type}_*.csv` - Arquivos por rede
- `results/networks/{sport}/{sport}_{sex}_{type}_*.gexf` - Redes em formato GEXF

**Processo:**
1. Carrega dados olímpicos
2. Filtra medalhistas dos 3 esportes
3. **Limpeza de dados:**
   - Remove 2 duplicatas
   - Filtra pódios com <2 atletas (garante 0 nós isolados)
4. Constrói redes direcionadas ponderadas
5. Aplica disparity filter (α=0.2) para extrair backbone
6. Calcula métricas (PageRank, centralidade, comunidades)
7. Exporta resultados em múltiplos formatos

**Redes Geradas:**
- Swimming M individual
- Swimming M team
- Swimming F individual
- Swimming F team
- Basketball M
- Basketball F
- Football M
- Football F

**Total: 8 redes**

### `02a_community_enrichment.py` - Enriquecimento de Comunidades

Adiciona análises detalhadas de comunidades.

**Entrada:**
- Arquivos de métricas gerados por `01_`

**Saída:**
- `results/communities/community_profiles_enriched.csv`
- Métricas adicionais por comunidade

**Análises:**
- Estatísticas descritivas por comunidade
- Distribuição de medalhas
- Concentração de PageRank
- Perfil competitivo

### `02b_medal_profile.py` - Perfil de Medalhas

Analisa distribuição de medalhas por comunidade.

**Entrada:**
- `results/networks/consolidated_athletes.csv`

**Saída:**
- `results/additional_analyses/medal_profile_by_community.csv`

**Métricas Calculadas:**
- Contagem de medalhas (ouro, prata, bronze)
- Percentuais de cada tipo
- **Índice de Dominância** (fórmula 3-2-1)
- Perfil competitivo (Participante/Competitiva/Elite)

**Fórmula do Índice de Dominância:**
```
dominance_index = (3 * gold% + 2 * silver% + 1 * bronze%) / 100
```

**Classificação:**
- `< 1.8`: Participante
- `1.8 - 2.2`: Competitiva
- `> 2.2`: Elite

### `02c_connectivity.py` - Conectividade Inter-Comunidade

Analisa conectividade entre comunidades.

**Entrada:**
- Arquivos de arestas e métricas

**Saída:**
- `results/additional_analyses/inter_community_connectivity.csv`

**Métricas:**
- Arestas intra-comunidade (dentro da mesma)
- Arestas inter-comunidade (entre diferentes)
- Razão intra/inter
- **Índice de Segregação**

**Interpretação:**
- Alta razão intra/inter = Alta segregação (comunidades isoladas)
- Baixa razão = Baixa segregação (comunidades conectadas)

### `02d_hierarchy.py` - Hierarquia Estrutural

Classifica comunidades em níveis hierárquicos.

**Entrada:**
- `results/networks/consolidated_athletes.csv`

**Saída:**
- `results/additional_analyses/community_hierarchy.csv`

**Métricas:**
- PageRank médio da comunidade
- Percentil de PageRank
- **Hierarchy Score**
- País dominante na comunidade

**Classificação:**
- **Núcleo**: PageRank > percentil 75 (comunidades centrais)
- **Intermediária**: PageRank 25-75 (comunidades intermediárias)
- **Periférica**: PageRank < percentil 25 (comunidades periféricas)

### `02e_rivalries.py` - Rivalidades Estruturais

Identifica principais rivalidades entre comunidades.

**Entrada:**
- Arquivos de arestas e métricas

**Saída:**
- `results/additional_analyses/top_rivalry_pairs.csv`

**Análise:**
- Conta confrontos entre pares de comunidades
- Identifica países dominantes em cada comunidade
- Ranqueia top rivalidades por número de confrontos

**Exemplo:**
```
Swimming F: C0 (USA) vs C1 (AUS) - 245 confrontos
Basketball M: C0 (USA) vs C1 (RUS) - 89 confrontos
```

## Dependências entre Scripts

```
01_network_generation.py
    ↓
    ├── 02a_community_enrichment.py
    ├── 02b_medal_profile.py
    ├── 02c_connectivity.py
    ├── 02d_hierarchy.py
    └── 02e_rivalries.py
```

**Importante:** `01_network_generation.py` deve ser executado primeiro. Os scripts `02*` podem ser executados em qualquer ordem depois.

## Execução em Lote

Criar script `run_all.bat`:
```batch
@echo off
cd src\pipeline
python 01_network_generation.py
python 02a_community_enrichment.py
python 02b_medal_profile.py
python 02c_connectivity.py
python 02d_hierarchy.py
python 02e_rivalries.py
echo Pipeline completo executado!
```

Ou em Python `run_all.py`:
```python
import subprocess

scripts = [
    '01_network_generation.py',
    '02a_community_enrichment.py',
    '02b_medal_profile.py',
    '02c_connectivity.py',
    '02d_hierarchy.py',
    '02e_rivalries.py',
]

for script in scripts:
    print(f"\nExecutando {script}...")
    subprocess.run(['python', f'src/pipeline/{script}'], check=True)
```

## Logs e Debug

Todos os scripts imprimem progresso no console:
```
================================================================================
CARREGANDO DADOS
================================================================================
Carregando atletas consolidados de: ...
  [OK] 4659 atletas carregados
  [OK] Esportes: ['Swimming' 'Basketball' 'Football']
...
```

Para salvar logs:
```bash
python 01_network_generation.py > logs/network_generation.log 2>&1
```

## Tempo de Execução

Estimativa em máquina padrão:

- `01_network_generation.py`: ~5-10 min
- `02a_community_enrichment.py`: ~1-2 min
- `02b_medal_profile.py`: ~30 seg
- `02c_connectivity.py`: ~1 min
- `02d_hierarchy.py`: ~30 seg
- `02e_rivalries.py`: ~1 min

**Total: ~10-15 minutos**

## Configuração

Todos os scripts usam `core.config` para configurações:

```python
from core.config import PATHS, SPORTS_LIST

# Esportes analisados
SPORTS_LIST = ['Swimming', 'Basketball', 'Football']

# Diretório de saída
output_dir = PATHS['results_dir']
```

Para modificar esportes analisados, edite `src/core/config/constants.py`.

## TODO

- [ ] Paralelizar execução dos scripts `02*`
- [ ] Adicionar progress bars (tqdm)
- [ ] Implementar modo `--verbose` e `--quiet`
- [ ] Adicionar validação de saída
- [ ] Implementar retry automático em caso de falha
