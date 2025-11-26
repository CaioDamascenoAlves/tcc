# Código-Fonte (`src/`)

Este diretório contém todo o código-fonte do projeto, organizado em módulos especializados.

## Estrutura

```
src/
 core/ # Módulos reutilizáveis e configurações
 pipeline/ # Scripts de análise numerados
 dashboard/ # Aplicação Streamlit interativa
 outputs/ # Geração de figuras e tabelas
```

## Módulos

### `core/` - Núcleo Reutilizável

Módulos compartilhados por todo o projeto. Contém:
- **`config/`**: Configurações centralizadas (paths, constantes, estilos)
- **`data_loader.py`**: Carregamento e cache de dados
- **`metrics.py`**: Cálculos de métricas (dominância, hierarquia, etc.)

**Uso:**
```python
from core.config import PATHS, SPORTS_LIST
from core.data_loader import DataLoader
from core.metrics import MetricsCalculator

loader = DataLoader()
data = loader.load_all()
```

### `pipeline/` - Scripts de Análise

Scripts numerados para execução sequencial:

1. **`01_network_generation.py`**: Gera redes a partir de dados olímpicos
2. **`02a_community_enrichment.py`**: Enriquece análise de comunidades
3. **`02b_medal_profile.py`**: Perfil de medalhas por comunidade
4. **`02c_connectivity.py`**: Conectividade inter-comunidade
5. **`02d_hierarchy.py`**: Hierarquia estrutural de comunidades
6. **`02e_rivalries.py`**: Identifica rivalidades estruturais

**Execução:**
```bash
cd src/pipeline
python 01_network_generation.py
python 02a_community_enrichment.py
# ... executar demais scripts
```

### `dashboard/` - Interface Interativa

Aplicação Streamlit para exploração visual dos resultados.

**Estrutura:**
- **`app.py`**: Aplicação principal
- **`visualization/`**: Gráficos e plots reutilizáveis
- **`components/`**: Componentes interativos (Cosmograph, timeline)
- **`analysis/`**: Análises comparativas e tabelas

**Executar:**
```bash
streamlit run src/dashboard/app.py
```

### `outputs/` - Geração de Artefatos

Scripts para gerar figuras e tabelas para a monografia.

- **`figures.py`**: Gera 9 figuras PNG (300 DPI) para LaTeX
- **`tables.py`**: Gera tabelas LaTeX formatadas

**Uso:**
```bash
cd src/outputs
python figures.py
python tables.py
```

## Convenções de Código

### Imports

Sempre importe a partir de `src/` como raiz:
```python
from core.config import PATHS
from core.data_loader import DataLoader
from dashboard.visualization import scatter_plot
```

### Paths

Use sempre `PATHS` de `core.config.paths`:
```python
from core.config import PATHS

# Correto
df = pd.read_csv(PATHS['consolidated_athletes'])

# Incorreto
df = pd.read_csv('../results/networks/consolidated_athletes.csv')
```

### Executar Scripts

Sempre execute a partir da raiz do projeto (`main/`):
```bash
cd C:\Users\Caio\Desktop\tcc\main
python src/pipeline/01_network_generation.py
streamlit run src/dashboard/app.py
```

## Dependências

Ver `requirements.txt` na raiz do projeto.

Principais:
- `pandas`, `numpy`: Manipulação de dados
- `networkx`: Análise de grafos
- `matplotlib`, `seaborn`, `plotly`: Visualização
- `streamlit`: Dashboard interativo
- `python-louvain`: Detecção de comunidades
