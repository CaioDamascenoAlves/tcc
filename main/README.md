# Análise de Redes Complexas Aplicada ao Esporte Olímpico

**Trabalho de Conclusão de Curso (TCC)**
Sistemas de Informação - Universidade Federal de Ouro Preto (UFOP)
2025/2026

---

## Índice

- [Visão Geral](#visão-geral)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Documentação Detalhada](#documentação-detalhada)
- [Início Rápido](#início-rápido)
- [Metodologia](#metodologia)
- [Principais Resultados](#principais-resultados)
- [Licença e Autoria](#licença-e-autoria)

---

## Visão Geral

Este projeto utiliza **teoria de redes complexas** para modelar e analisar relações competitivas entre atletas olímpicos. Através da construção de grafos direcionados ponderados a partir de resultados de pódios compartilhados, aplicamos algoritmos avançados de análise de redes para revelar padrões estruturais, identificar comunidades e quantificar dominância competitiva.

### Características Principais

- **Modelagem de Redes Competitivas**: Transforma resultados olímpicos em grafos direcionados ponderados
- **Extração de Backbone**: Utiliza disparity filter para identificar conexões estatisticamente significativas
- **Detecção de Comunidades**: Algoritmo de Louvain para identificar agrupamentos estruturais
- **Métricas Avançadas**: PageRank, centralidade, modularidade, segregação inter-comunidade
- **Dashboard Interativo**: Interface Streamlit para exploração visual dos resultados
- **Documentação Acadêmica**: Monografia LaTeX completa e apresentação Beamer

### Dados

- **Dataset**: "120 years of Olympic history" (Kaggle)
- **Período**: Atenas 1896 até Rio 2016
- **Esportes Analisados**: Swimming, Basketball, Football
- **Total**: 4.659 atletas, 8 redes (por esporte e gênero)

## Estrutura do Projeto

```
tcc/
├── data/                          # Dados brutos
│   └── athlete_events.csv         # Dataset olímpico completo
│
├── src/                           # Código-fonte
│   ├── core/                      # Módulos reutilizáveis
│   │   ├── config/                # Configurações centralizadas
│   │   ├── data_loader.py         # Carregamento de dados
│   │   └── metrics.py             # Cálculos de métricas
│   │
│   ├── pipeline/                  # Scripts de análise
│   │   ├── 01_network_generation.py      # Geração de redes
│   │   ├── 02a_community_enrichment.py   # Análise de comunidades
│   │   └── ...
│   │
│   ├── dashboard/                 # Dashboard Streamlit
│   │   ├── app.py                 # Aplicação principal
│   │   ├── visualization/         # Gráficos e plots
│   │   └── components/            # Componentes interativos
│   │
│   └── outputs/                   # Geração de figuras/tabelas
│       ├── figures.py             # Figuras para monografia
│       └── tables.py              # Tabelas LaTeX
│
├── results/                       # Resultados das análises
│   ├── networks/                  # Redes geradas (CSV, GEXF, JSON)
│   └── additional_analyses/       # Análises adicionais
│
├── docs/                          # Documentação
│   ├── monografia/                # Documento LaTeX
│   │   ├── main.tex              # Documento principal
│   │   ├── figuras/              # Figuras geradas
│   │   └── tabelas/              # Tabelas LaTeX
│   │
│   └── apresentacao/              # Slides Beamer
│
└── tests/                         # Testes (TODO)
```

## Documentação Detalhada

Este projeto possui documentação modular e detalhada. Cada componente principal tem seu próprio README:

### Código-Fonte
- **[src/](src/README.md)** - Visão geral do código-fonte
  - **[src/core/](src/core/README.md)** - Módulos reutilizáveis (config, data_loader, metrics)
  - **[src/pipeline/](src/pipeline/README.md)** - Scripts de análise numerados (01-02e)
  - **[src/dashboard/](src/dashboard/README.md)** - Dashboard Streamlit interativo
  - **[src/outputs/](src/outputs/)** - Geração de figuras e tabelas para monografia

### Dados e Resultados
- **data/** - Dataset olímpico original (athlete_events.csv)
- **results/** - Todos os resultados gerados
  - **results/networks/** - Redes geradas (CSV, GEXF, JSON)
  - **results/additional_analyses/** - Análises enriquecidas (perfis, hierarquias, rivalidades)

### Documentação Acadêmica
- **docs/monografia/** - Monografia LaTeX completa
- **docs/apresentacao/** - Apresentação Beamer para defesa

### Outros
- **tests/** - Testes unitários (TODO)
- **[CLAUDE.md](CLAUDE.md)** - Instruções para Claude Code

---

## Início Rápido

### Pré-requisitos

```bash
Python 3.10+
pip install pandas numpy networkx matplotlib seaborn plotly streamlit python-louvain scikit-learn
```

### 1. Gerar Redes e Análises

```bash
cd src/pipeline
python 01_network_generation.py
python 02a_community_enrichment.py
python 02b_medal_profile.py
python 02c_connectivity.py
python 02d_hierarchy.py
python 02e_rivalries.py
```

Veja [src/pipeline/README.md](src/pipeline/README.md) para detalhes.

### 2. Visualizar no Dashboard

```bash
# Na raiz do projeto
start_dashboard.bat
```

Acesse: http://localhost:8501

Veja [src/dashboard/README.md](src/dashboard/README.md) para customização.

### 3. Gerar Figuras para Monografia

```bash
cd src/outputs
python figures.py
```

Figuras salvas em: `docs/monografia/figuras/`

### 4. Compilar Monografia

```bash
cd docs/monografia
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Metodologia

### Modelagem de Redes

As redes são construídas onde:
- **Nós** = Atletas medalhistas
- **Arestas** = Conexões direcionadas de atleta de posição inferior → superior no mesmo pódio
- **Pesos** = Baseados na distância no pódio:
  - Ouro ← Prata: peso 3
  - Ouro ← Bronze: peso 5
  - Prata ← Bronze: peso 2

### Pipeline de Análise

1. **Limpeza de Dados**
   - Remoção de duplicatas
   - Filtragem de pódios com <2 atletas (garante 0 nós isolados)

2. **Construção de Redes**
   - Grafos originais ponderados
   - Extração de backbone (disparity filter α=0.2)

3. **Cálculo de Métricas**
   - PageRank (importância estrutural)
   - Centralidade (betweenness, closeness, degree)
   - Comunidades (algoritmo de Louvain)

4. **Análises Enriquecidas**
   - Perfil de medalhas por comunidade (índice de dominância)
   - Hierarquia estrutural (níveis: núcleo, intermediária, periférica)
   - Conectividade inter-comunidade (segregação)
   - Rivalidades estruturais (top pares)

## Principais Resultados

- **37 comunidades** detectadas em 3 esportes e 2 gêneros
- **0 nós isolados** em todas as 8 redes (garantido por filtragem)
- **Swimming**: 26 comunidades (17M + 9F), alta segregação
- **Basketball**: 5 comunidades (3M + 2F), média segregação
- **Football**: 6 comunidades (4M + 2F), baixa segregação
- **Top atleta**: Michael Phelps (PageRank: 0.0255 em Swimming M)

---

## Licença e Autoria

**Licença**: MIT

**Instituição**: Universidade Federal de Ouro Preto (UFOP)
**Curso**: Sistemas de Informação
**Ano**: 2025/2026

**Status do Projeto**: Em desenvolvimento ativo
**Última atualização**: Novembro 2025

---

## Citação

Se utilizar este trabalho, cite:

```bibtex
@misc{tcc_redes_olimpicas_2025,
  author = {Autor},
  title = {Análise de Redes Complexas Aplicada ao Esporte Olímpico},
  year = {2025},
  school = {Universidade Federal de Ouro Preto},
  type = {Trabalho de Conclusão de Curso}
}
```

---

## Navegação da Documentação

**Documentação Principal**
- [README.md](README.md) - Este arquivo (visão geral)
- [CLAUDE.md](CLAUDE.md) - Instruções para Claude Code

**Código-Fonte**
- [src/README.md](src/README.md) - Código-fonte
- [src/core/README.md](src/core/README.md) - Módulos core
- [src/pipeline/README.md](src/pipeline/README.md) - Scripts de análise
- [src/dashboard/README.md](src/dashboard/README.md) - Dashboard

**Documentos Acadêmicos**
- [docs/monografia/](docs/monografia/) - Monografia LaTeX
- [docs/apresentacao/](docs/apresentacao/) - Slides Beamer

**Configuração**
- [.gitignore](.gitignore) - Arquivos ignorados pelo Git
- [start_dashboard.bat](start_dashboard.bat) - Atalho para dashboard
