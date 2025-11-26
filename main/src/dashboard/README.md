# Dashboard - Interface Interativa

Dashboard Streamlit para exploração visual e interativa dos resultados de análise de redes olímpicas.

## Estrutura

```
dashboard/
 app.py # Aplicação principal Streamlit
 visualization/ # Gráficos e plots reutilizáveis
 base.py # Funções base de visualização
 plots.py # Plots principais
 plots_extended.py # Plots adicionais
 timeline_plots.py # Visualizações temporais
 components/ # Componentes interativos
 cosmograph_network.py # Visualização de rede 3D
 timeline_fullwidth.py # Timeline full-width
 analysis/ # Análises e tabelas
 comparative_table.py # Tabelas comparativas
```

## Executar Dashboard

```bash
# Na raiz do projeto
start_dashboard.bat

# Ou diretamente
cd C:\Users\Caio\Desktop\tcc\main
streamlit run src/dashboard/app.py
```

Acesse: http://localhost:8501

## Abas do Dashboard

### 1. Visão Geral
- Resumo do projeto
- Estatísticas gerais
- Seleção de esporte/gênero

### 2. Análise de Comunidades
- Distribuição de comunidades
- Perfil de medalhas
- Índice de dominância
- Top comunidades

### 3. Hierarquia Estrutural
- Níveis hierárquicos (Núcleo/Intermediária/Periférica)
- PageRank médio por comunidade
- Scatter: Tamanho vs Centralidade

### 4. Conectividade
- Conectividade inter-comunidade
- Índice de segregação
- Heatmaps de conectividade

### 5. Rivalidades
- Top rivalidades estruturais
- Matriz de confrontos
- Análise de pares

### 6. Atletas
- Ranking de atletas
- Filtros por esporte/gênero/métrica
- Top atletas por PageRank

### 7. Distribuições Estatísticas
- CDF/CCDF de métricas
- Distribuições de grau
- Boxplots por categoria

### 8. Rede Interativa
- Visualização 3D com Cosmograph
- Filtros interativos
- Informações de atletas ao hover

### 9. Evolução Temporal
- Timeline olímpica (1896-2024)
- Eras olímpicas marcadas
- Gráficos de evolução

## Arquitetura

### `app.py` - Aplicação Principal

**Estrutura:**
```python
def main():
 # 1. Configuração da página
 st.set_page_config(...)

 # 2. Carregar dados (com cache)
 data = load_data()

 # 3. Sidebar com filtros
 render_sidebar(data)

 # 4. Renderizar abas
 tabs = st.tabs([...])
 with tabs[0]:
 render_overview_tab(data)
 with tabs[1]:
 render_communities_tab(data)
 # ...
```

**Cache de Dados:**
```python
@st.cache_data
def load_data():
 loader = DataLoader()
 return loader.load_all()
```

### `visualization/` - Gráficos Reutilizáveis

Funções que retornam objetos de plot (matplotlib, seaborn, plotly):

```python
from dashboard.visualization import scatter_size_vs_pagerank

fig = scatter_size_vs_pagerank(
 data=hierarchy_df,
 title="Tamanho vs PageRank",
 colors=COLORS
)
st.pyplot(fig)
```

**Principais Plots:**
- `scatter_size_vs_pagerank()`: Scatter tamanho vs centralidade
- `histogram_dominance()`: Histograma de índice de dominância
- `heatmap_segregation()`: Heatmap de segregação
- `barplot_top_rivalries()`: Top rivalidades
- `cdf_pagerank()`: CDF de PageRank

### `components/` - Componentes Interativos

Componentes complexos que encapsulam lógica e visualização:

```python
from dashboard.components import render_cosmograph

render_cosmograph(
 network_file="results/networks/swimming/swimming_M_individual.gexf",
 metrics_file="results/networks/swimming/swimming_M_individual_detailed_metrics.csv"
)
```

### `analysis/` - Análises Especializadas

Funções de análise que não são apenas visualização:

```python
from dashboard.analysis import render_comparative_table

render_comparative_table(
 data=athletes_df,
 sports=['Swimming', 'Basketball'],
 metric='original_pagerank'
)
```

## Customização

### Adicionar Nova Aba

1. Criar função de renderização em `app.py`:
```python
def render_minha_aba(data):
 st.header("Minha Análise")
 # ... lógica da aba
```

2. Adicionar à lista de tabs:
```python
tabs = st.tabs([
 "Visão Geral",
 # ... outras abas
 "Minha Aba" # Nova aba
])

# ... outras abas
with tabs[8]:
 render_minha_aba(data)
```

### Adicionar Novo Plot

1. Criar função em `visualization/plots.py`:
```python
def meu_plot(data, title="", colors=None):
 fig, ax = plt.subplots(figsize=(10, 6))
 # ... lógica do plot
 return fig
```

2. Exportar em `visualization/__init__.py`:
```python
from .plots import meu_plot

__all__ = [
 # ... outros
 'meu_plot',
]
```

3. Usar no dashboard:
```python
from dashboard.visualization import meu_plot

fig = meu_plot(data)
st.pyplot(fig)
```

## Performance

### Cache Agressivo
```python
@st.cache_data(ttl=3600) # Cache por 1 hora
def load_heavy_data():
 # ... operação pesada
 return data
```

### Lazy Loading
Carregue dados apenas quando necessário:
```python
if st.button("Mostrar análise detalhada"):
 # Só carrega quando usuário clica
 detailed_data = load_detailed_analysis()
 st.dataframe(detailed_data)
```

### Limitar Visualizações
```python
# Mostrar apenas top 100 para performance
top_100 = df.nlargest(100, 'pagerank')
st.dataframe(top_100)
```

## Dependências

- `streamlit`: Framework do dashboard
- `pandas`: Manipulação de dados
- `plotly`: Gráficos interativos
- `matplotlib`, `seaborn`: Gráficos estáticos
- `core.data_loader`: Carregamento de dados
- `core.config`: Configurações e estilos

## Desenvolvimento

### Modo de Desenvolvimento
```bash
streamlit run src/dashboard/app.py --server.runOnSave true
```

### Debug
```python
# Mostrar variáveis na sidebar
st.sidebar.write("Debug:", st.session_state)

# Expandir para ver dados
with st.expander("Ver dados brutos"):
 st.dataframe(df)
```

## TODO

- [ ] Adicionar testes de componentes
- [ ] Implementar modo claro/escuro
- [ ] Adicionar export de visualizações
- [ ] Cache persistente entre sessões
- [ ] Autenticação (se necessário)
