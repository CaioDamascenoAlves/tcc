# Análise de Redes Complexas para Modelagem de Relações Competitivas no Esporte Olímpico

Trabalho de Conclusão de Curso - Sistemas de Informação
Universidade Federal de Ouro Preto (UFOP) - 2026

[![Compilação Automática](https://github.com/CaioDamascenoAlves/tcc/actions/workflows/compile-monografia.yml/badge.svg)](https://github.com/CaioDamascenoAlves/tcc/actions/workflows/compile-monografia.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Descrição

Este trabalho aplica teoria de redes complexas para analisar competições olímpicas históricas (1896-2016). O projeto modela relações competitivas entre atletas através de grafos direcionados ponderados, utilizando algoritmos de PageRank, detecção de comunidades (Louvain) e métricas de centralidade.

### 📊 Dados do Projeto

**Dataset:** 120 years of Olympic history (Griffin 2018)
**Período analisado:** Atenas 1896 até Rio 2016 (120 anos)
**Atletas no dataset completo:** 135.571 atletas únicos
**Modalidades analisadas:** 6 esportes (Athletics, Swimming, Basketball, Boxing, Football, Judo)
**Atletas medalhistas:** 9.378 medalhistas nas 6 modalidades
**Redes geradas:** 123 redes competitivas (modelagem per-event)
**Casos de estudo:** 12 redes selecionadas via Iconic Score
**Comunidades detectadas:** Múltiplas comunidades estruturais detectadas

---

## Estrutura do Repositório

```
tcc/
├── main/                      # Implementação e código-fonte
│   ├── src/                   # Código Python
│   │   ├── pipeline/          # Pipeline de análise
│   │   ├── dashboard/         # Dashboard Streamlit
│   │   └── data_processing/   # Processamento de dados
│   ├── data/                  # Datasets (137.745 atletas)
│   ├── results_per_event_cleaned/  # 149 redes GEXF
│   ├── analysis/              # Scripts de validação
│   └── README.md
│
├── monografia/                # Documento acadêmico LaTeX
│   ├── textuais/              # Capítulos
│   │   ├── introducao.tex
│   │   ├── revisao.tex
│   │   ├── desenvolvimento.tex
│   │   ├── resultados.tex
│   │   └── conclusao.tex
│   ├── figuras/               # Figuras
│   ├── tabelas/               # Tabelas
│   ├── bib/                   # Referências
│   └── main.pdf               # PDF compilado (79 páginas)
│
├── apresentacao/              # Slides para defesa
│
├── scripts/                   # Utilitários
│
├── .github/workflows/         # CI/CD
│
├── LICENSE                    # MIT License
└── CITATION.cff               # Metadados para citação
```

---

## Início Rápido

### Pré-requisitos

- Python 3.8+
- Dependências em `requirements.txt`
- LaTeX (para compilar monografia)

### Executar Análise

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

Acesse: http://localhost:8501

### Compilar Monografia

```bash
cd monografia
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

PDF pré-compilado disponível: [monografia-latest.pdf](monografia-latest.pdf)

---

## Metodologia

### Hierarquia dos Dados

| Nível | Descrição | Atletas Únicos |
|-------|-----------|----------------|
| Dataset completo | Todos os atletas olímpicos (1896-2016), 66 modalidades | 135.571 |
| Dataset filtrado | Medalhistas nas 6 modalidades selecionadas | 9.378 |
| 123 redes | Redes per-event (Year × Event × Gender) | 9.378 |
| 12 casos de estudo | Redes selecionadas via Iconic Score | Foco central de análise |

### Construção das Redes

- **Nós:** Atletas medalhistas
- **Arestas:** Direcionadas, ponderadas por hierarquia de medalhas
- **Ponderação:** Ouro→Prata (peso 3), Ouro→Bronze (peso 5), Prata→Bronze (peso 2)
- **Modelagem:** Per-event (Year × Event × Gender) para preservar homogeneidade competitiva

### Métricas Aplicadas

**Centralidade:**
- PageRank adaptado para contexto esportivo
- Centralidade de grau (in-degree, out-degree)
- Betweenness centrality (atletas-ponte)
- Closeness centrality

**Estrutura de Comunidades:**
- Detecção: Algoritmo de Louvain
- Validação: Comparação com Infomap (NMI = 0.97)
- Caracterização: Entropia temporal, concentração geográfica, dominância

**Validação Estatística:**
- Teste de Wilcoxon signed-rank (p = 0.031)
- Bootstrap para intervalos de confiança (95%)
- Análise de sensibilidade do sistema de pesos (τ ≈ 1.0)

### Modalidades Analisadas

| Modalidade | Tipo | Atletas Medalhistas | Descrição |
|------------|------|---------------------|-----------|
| **Athletics** | Individual (Performance) | 3.026 | Eventos de corrida, saltos e arremessos |
| **Swimming** | Individual (Performance) | 1.731 | Natação em diferentes distâncias e estilos |
| **Football** | Coletivo | 1.568 | Esporte coletivo com interdependência total |
| **Basketball** | Coletivo | 915 | Esporte coletivo com interdependência total |
| **Boxing** | Individual (Combate) | 912 | Confrontos diretos por categorias de peso |
| **Judo** | Individual (Combate) | 528 | Confrontos diretos por categorias de peso |
| **TOTAL** | - | **8.679** | Seis modalidades em três tipologias |

### Iconic Score

Critério multi-dimensional para seleção dos 12 casos de estudo:

```
IS_e = w_L · L_norm(e) + w_G · G_norm(e) + w_V · V_norm(e) + w_B · B(e)
```

Onde:
- **L_norm**: Longevidade histórica (peso 0.30)
- **G_norm**: Diversidade geográfica (peso 0.30)
- **V_norm**: Volume de participantes (peso 0.20)
- **B**: Equilíbrio de gênero (peso 0.20)

Análise de sensibilidade demonstrou robustez (τ ≈ 1.0) em diferentes sistemas de pesos.

---

## Resultados Principais

### Diferenças Estruturais entre Modalidades

- **Swimming:** Modularidade 0.73, comunidades altamente segregadas por especialização técnica
- **Basketball:** Modularidade 0.003, estrutura global coesa
- **Football:** Modularidade 0.0006, rede densamente interconectada

### Descobertas Contra-Intuitivas

- **Densidade feminina > masculina:** Validado estatisticamente (p = 0.031)
  - Redes femininas são significativamente mais densas em 5 dos 6 esportes
  - Razão média: 1.89 (IC95%: [1.23, 3.15])

- **Comunidades revelam eras e dominância:**
  - Detecção automática de períodos históricos (Guerra Fria, pós-URSS)
  - Identificação de hegemonia geográfica por períodos

### Validação Metodológica

- **Louvain vs Infomap:** NMI médio = 0.9686 (concordância quase perfeita)
- **Sensibilidade de pesos:** Kendall τ ≈ 1.0 (ranking estável)
- **Significância estatística:** Wilcoxon p = 0.031 < 0.05

Detalhes completos na monografia: [monografia/main.pdf](monografia/main.pdf)

---

## Compilação Automática

GitHub Actions compila automaticamente a monografia a cada modificação:
- PDF atualizado: [monografia-latest.pdf](monografia-latest.pdf)
- Releases com timestamp: [Releases](https://github.com/CaioDamascenoAlves/tcc/releases)
- Workflow: [compile-monografia.yml](.github/workflows/compile-monografia.yml)

---

## Citação

```bibtex
@misc{alves2025olympic_networks,
  author  = {Alves, Caio Damasceno},
  title   = {Análise de Redes Complexas aplicada ao Esporte Olímpico},
  year    = {2026},
  school  = {Universidade Federal de Ouro Preto},
  type    = {Trabalho de Conclusão de Curso},
  url     = {https://github.com/CaioDamascenoAlves/tcc}
}
```

Metadados completos: [CITATION.cff](CITATION.cff)

---

## Licenças

- **Código Python:** [MIT License](LICENSE)
- **Monografia LaTeX:** [LPPL 1.3c](monografia/LICENSE)
- **Apresentação:** [LPPL 1.3c](apresentacao/LICENSE)

---

## Documentação

- [main/data/README.md](main/data/README.md) - Documentação completa dos datasets
- [main/README.md](main/README.md) - Documentação técnica (se existir)
- [monografia/README.md](monografia/README.md) - Informações sobre compilação
- [main/src/dashboard/README.md](main/src/dashboard/README.md) - Guia do dashboard

---

## Tecnologias Utilizadas

**Python:**
- NetworkX (redes complexas)
- Pandas/NumPy (processamento de dados)
- Python-Louvain (detecção de comunidades)
- Plotly (visualizações)
- Streamlit (dashboard interativo)
- Scikit-learn (métricas de validação)
- igraph (Infomap)

**LaTeX:**
- abnTeX2 (formatação ABNT)
- BibTeX (referências)
- TikZ/PGFPlots (gráficos)

**CI/CD:**
- GitHub Actions (compilação automática)

---

## Contribuindo

Este é um projeto acadêmico (TCC). Sugestões e feedback são bem-vindos via Issues.

---

**Autor:** Caio Damasceno Alves
**Orientador:** [Nome do Orientador]
**Instituição:** UFOP - Instituto de Ciências Exatas e Aplicadas
**Curso:** Sistemas de Informação
**Ano:** 2026
**Contato:** [seu email]

---

**Status do Projeto:** 🟢 Em desenvolvimento (Defesa prevista para 2026)
