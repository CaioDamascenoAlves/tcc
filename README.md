# TCC - Análise de Redes Complexas Aplicada ao Esporte Olímpico

**Trabalho de Conclusão de Curso**
Ciência da Computação - Universidade Federal de Ouro Preto (UFOP)
2024

---

## Estrutura do Repositório

Este repositório contém todo o material do TCC, organizado em 3 componentes principais:

### 1. Código e Análises - [main/](main/)

Implementação completa do projeto:
- **Código-fonte** Python organizado em módulos
- **Pipeline de análise** de redes olímpicas
- **Dashboard interativo** Streamlit
- **Geração de figuras** e tabelas para monografia
- **Documentação técnica** completa

Ver: **[main/README.md](main/README.md)** para detalhes

### 2. Monografia - [monografia/](monografia/)

Documento acadêmico em LaTeX:
- Texto completo do TCC
- Seguindo normas ABNT (abntex2)
- Figuras e tabelas geradas automaticamente
- Referencias bibliograficas

### 3. Apresentação - [apresentacao/](apresentacao/)

Slides para defesa:
- Apresentação em Beamer
- Resumo executivo do trabalho
- Principais resultados e visualizações

---

## Início Rápido

### Executar Análises

```bash
cd main/src/pipeline
python 01_network_generation.py
```

### Visualizar Dashboard

```bash
cd main
start_dashboard.bat
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

---

## Documentação

- **[main/README.md](main/README.md)** - Documentação técnica completa
- **[CLAUDE.md](CLAUDE.md)** - Instruções para Claude Code
- **[main/src/](main/src/)** - Documentação de módulos individuais

---

## Arquivos Arquivados

Documentos temporários e de desenvolvimento foram movidos para:
- **[_archived_docs/](_archived_docs/)** - MDs de análises e planejamento

---

## Dependências

```bash
Python 3.10+
pip install pandas numpy networkx matplotlib seaborn plotly streamlit python-louvain scikit-learn
```

LaTeX: abntex2, babel, graphicx, amsmath, booktabs, hyperref

---

## Licença

MIT License - Ver arquivo LICENSE

**Instituição**: UFOP
**Ano**: 2024
