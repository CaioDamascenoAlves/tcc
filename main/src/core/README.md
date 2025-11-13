# Core - Módulos Reutilizáveis

Biblioteca interna de módulos compartilhados por todo o projeto.

## Estrutura

```
core/
├── config/           # Configurações centralizadas
│   ├── paths.py      # Caminhos de arquivos
│   ├── constants.py  # Constantes do projeto
│   ├── styles.py     # Estilos de visualização
│   └── __init__.py   # Exporta tudo
│
├── data_loader.py    # Carregamento de dados com cache
├── metrics.py        # Cálculos de métricas
└── __init__.py       # Exporta DataLoader e MetricsCalculator
```

## Módulos

### `config/` - Configurações Centralizadas

**FONTE ÚNICA DE VERDADE** para todas as configurações do projeto.

#### `paths.py`
Define todos os caminhos de arquivos:
```python
from core.config import PATHS

# Dados de entrada
PATHS['athlete_events']           # data/athlete_events.csv
PATHS['consolidated_athletes']    # results/networks/consolidated_athletes.csv

# Análises adicionais
PATHS['medal_profile']            # results/additional_analyses/medal_profile_by_community.csv
PATHS['community_hierarchy']      # results/additional_analyses/community_hierarchy.csv

# Saídas
PATHS['monografia_figuras']       # docs/monografia/figuras/
PATHS['monografia_tabelas']       # docs/monografia/tabelas/
```

#### `constants.py`
Constantes do projeto:
```python
from core.config import SPORTS_LIST, MEDAL_WEIGHTS, DOMINANCE_THRESHOLDS

SPORTS_LIST = ['Swimming', 'Basketball', 'Football']

MEDAL_WEIGHTS = {
    'Gold': 3,
    'Silver': 2,
    'Bronze': 1
}

DOMINANCE_THRESHOLDS = {
    'participante': 1.8,
    'competitiva': 2.2,
    'elite': float('inf')
}
```

#### `styles.py`
Paletas de cores e estilos de visualização:
```python
from core.config import COLORS, UFOP_WINE, PLOT_STYLE_INTERACTIVE

COLORS = {
    'Swimming': '#1f77b4',
    'Basketball': '#ff7f0e',
    'Football': '#2ca02c',
}

UFOP_WINE = '#6F1D1D'  # Vinho institucional UFOP
```

### `data_loader.py` - Carregamento de Dados

Classe centralizada para carregar todos os datasets com cache automático.

**Uso:**
```python
from core.data_loader import DataLoader

# Carregar todos os dados
loader = DataLoader()
data = loader.load_all()

# data = {
#     'athletes': DataFrame,
#     'medal_profile': DataFrame,
#     'hierarchy': DataFrame,
#     'connectivity': DataFrame,
#     'rivalries': DataFrame,
# }

# Carregar dados específicos
athletes_df = loader.load_consolidated_athletes()
medal_df = loader.load_medal_profile()
```

**Características:**
- Cache automático (evita recarregamento)
- Validação de integridade
- Mensagens informativas de progresso
- Função de conveniência: `load_all_data()`

### `metrics.py` - Cálculo de Métricas

Cálculos padronizados de métricas usadas em todo o projeto.

**Uso:**
```python
from core.metrics import MetricsCalculator

calc = MetricsCalculator()

# Índice de Dominância (fórmula 3-2-1)
dominance = calc.calculate_dominance_index(
    gold_pct=50.0,
    silver_pct=30.0,
    bronze_pct=20.0
)
# dominance = 2.3 (elite)

# Classificar perfil competitivo
profile = calc.classify_competitive_profile(dominance)
# profile = 'Elite'

# Classificar nível hierárquico
level = calc.classify_hierarchy_level(pagerank_percentile=95.0)
# level = 'Núcleo'
```

**Métricas Disponíveis:**
- `calculate_dominance_index()`: Índice 3-2-1 de dominância
- `classify_competitive_profile()`: Participante/Competitiva/Elite
- `calculate_hierarchy_score()`: Score de hierarquia
- `classify_hierarchy_level()`: Núcleo/Intermediária/Periférica
- `calculate_segregation_score()`: Razão intra/inter comunidade

## Importação Simplificada

O `__init__.py` exporta os principais componentes:

```python
# Em vez de:
from core.config.paths import PATHS
from core.config.constants import SPORTS_LIST
from core.data_loader import DataLoader

# Pode usar:
from core.config import PATHS, SPORTS_LIST
from core import DataLoader, MetricsCalculator
```

## Dependências

- `pandas`: Manipulação de dados
- `pathlib`: Gerenciamento de caminhos
- Nenhuma dependência de módulos do próprio projeto (exceto config)

## Testes

TODO: Implementar testes unitários em `tests/core/`
