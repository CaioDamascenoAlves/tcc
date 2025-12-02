# Analise de Redes Complexas para Modelagem de Relacoes Competitivas no Esporte Olimpico

Trabalho de Conclusao de Curso - Sistemas de Informacao
Universidade Federal de Ouro Preto (UFOP) - 2025

[![Compilacao Automatica](https://github.com/CaioDamascenoAlves/tcc/actions/workflows/compile-monografia.yml/badge.svg)](https://github.com/CaioDamascenoAlves/tcc/actions/workflows/compile-monografia.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Descricao

Este trabalho aplica teoria de redes complexas para analisar competicoes olimpicas. O projeto modela relacoes competitivas entre atletas atraves de grafos direcionados ponderados, utilizando algoritmos de PageRank, deteccao de comunidades (Louvain) e metricas de centralidade.

**Dataset principal:** 120 years of Olympic history (Kaggle)
**Periodo analisado:** 1896-2021
**Atletas medalhistas:** 4.659 atletas em Swimming, Basketball e Football

---

## Estrutura do Repositorio

```
tcc/
├── main/                      # Implementacao e codigo-fonte
│   ├── src/                   # Codigo Python
│   ├── data/                  # Datasets
│   ├── results/               # Resultados de analise
│   └── README.md
│
├── monografia/                # Documento academico LaTeX
│   ├── textuais/              # Capitulos
│   ├── figuras/               # Figuras
│   ├── tabelas/               # Tabelas
│   ├── bib/                   # Referencias
│   └── main.pdf               # PDF compilado
│
├── apresentacao/              # Slides para defesa
│
├── scripts/                   # Utilitarios
│
├── .github/workflows/         # CI/CD
│
├── LICENSE                    # MIT License
└── CITATION.cff               # Metadados para citacao
```

---

## Inicio Rapido

### Prerequisitos

Python 3.8+, dependencias em requirements.txt

### Executar Analise

```bash
cd main/src/pipeline
python 01_network_generation.py
python 02_centrality_analysis.py
python 03_community_detection.py
```

### Dashboard Interativo

```bash
cd main/src/dashboard
streamlit run app.py
```

### Compilar Monografia

```bash
cd monografia
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

PDF pre-compilado disponivel: [monografia-latest.pdf](monografia-latest.pdf)

---

## Metodologia

### Construcao das Redes

- **Nos:** Atletas medalhistas
- **Arestas:** Direcionadas, ponderadas por hierarquia de medalhas
- **Ponderacao:** Ouro-Prata (3), Ouro-Bronze (5), Prata-Bronze (2)

### Metricas Aplicadas

- PageRank adaptado para contexto esportivo
- Centralidade de grau (in-degree, out-degree)
- Betweenness centrality
- Modularidade e deteccao de comunidades (Louvain)

### Esportes Analisados

- **Swimming:** 2.176 atletas, eventos individuais + coletivos
- **Basketball:** 558 atletas, esporte coletivo
- **Football:** 1.925 atletas, esporte coletivo

---

## Resultados Principais

- **36 comunidades detectadas** nas tres modalidades
- **Diferencas estruturais:** Swimming apresenta modularidade 0.73 vs 0.003 (Basketball) e 0.0006 (Football)
- **Atletas-ponte identificados** via betweenness centrality
- **Hierarquias de performance** reveladas por PageRank

Detalhes completos na monografia: [monografia/main.pdf](monografia/main.pdf)

---

## Compilacao Automatica

GitHub Actions compila automaticamente a monografia a cada modificacao:
- PDF atualizado: [monografia-latest.pdf](monografia-latest.pdf)
- Releases com timestamp: [Releases](https://github.com/CaioDamascenoAlves/tcc/releases)
- Workflow: [compile-monografia.yml](.github/workflows/compile-monografia.yml)

---

## Citacao

```bibtex
@misc{alves2025olympic_networks,
  author  = {Alves, Caio Damasceno},
  title   = {Analise de Redes Complexas aplicada ao Esporte Olimpico},
  year    = {2025},
  school  = {Universidade Federal de Ouro Preto},
  type    = {Trabalho de Conclusao de Curso},
  url     = {https://github.com/CaioDamascenoAlves/tcc}
}
```

Metadados completos: [CITATION.cff](CITATION.cff)

---

## Licencas

- **Codigo Python:** [MIT License](LICENSE)
- **Monografia LaTeX:** [LPPL 1.3c](monografia/LICENSE)
- **Apresentacao:** [LPPL 1.3c](apresentacao/LICENSE)

---

## Documentacao

- [main/README.md](main/README.md) - Documentacao tecnica
- [monografia/README.md](monografia/README.md) - Informacoes sobre compilacao
- [main/src/dashboard/README.md](main/src/dashboard/README.md) - Guia do dashboard

---

**Autor:** Caio Damasceno Alves
**Instituicao:** UFOP - Instituto de Ciencias Exatas e Aplicadas
**Curso:** Sistemas de Informacao
**Ano:** 2025
