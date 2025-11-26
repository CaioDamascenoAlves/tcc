# Documentação Acadêmica

Este diretório contém toda a documentação acadêmica formal do projeto TCC.

## Estrutura

```
docs/
 monografia/ # Monografia LaTeX (documento principal)
 apresentacao/ # Apresentação Beamer (defesa)
```

## Monografia

### Localização
`docs/monografia/`

### Compilação

```bash
cd docs/monografia
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Saída: `main.pdf`

### Estrutura da Monografia

```
monografia/
 main.tex # Documento principal
 preambulo/ # Elementos pré-textuais
 capa.tex
 folha_rosto.tex
 resumo.tex
 abstract.tex
 textuais/ # Conteúdo principal
 introducao.tex
 revisao.tex
 desenvolvimento.tex
 resultados.tex
 conclusao.tex
 postextuais/ # Elementos pós-textuais
 referencias.bib
 apendices.tex
 figuras/ # Figuras geradas (PNG 300 DPI)
 tabelas/ # Tabelas LaTeX geradas
```

### Gerar Figuras e Tabelas

```bash
# Gerar figuras
cd src/outputs
python figures.py

# Gerar tabelas
python tables.py
```

Figuras salvas em: `docs/monografia/figuras/`
Tabelas salvas em: `docs/monografia/tabelas/`

### Dependências LaTeX

Pacotes necessários:
- abntex2 (formatação ABNT)
- babel (português)
- graphicx (imagens)
- amsmath (matemática)
- booktabs (tabelas profissionais)
- hyperref (links e PDF metadata)

## Apresentação

### Localização
`docs/apresentacao/`

### Compilação

```bash
cd docs/apresentacao
pdflatex main.tex
```

Saída: `main.pdf`

### Estrutura da Apresentação

```
apresentacao/
 main.tex # Slides Beamer
 figuras/ # Figuras para slides
 logos/ # Logos institucionais
```

### Tema Beamer

Usa tema customizado com:
- Cores institucionais UFOP (vinho)
- Layout limpo e profissional
- Navegação clara
- Blocos para destaques

## Padrões de Formatação

### Figuras

**Formato**: PNG, 300 DPI (qualidade de publicação)
**Tamanho**: Ajustado para caber na largura do texto

Inclusão em LaTeX:
```latex
\begin{figure}[htbp]
 \centering
 \includegraphics[width=0.8\textwidth]{figuras/fig_size_vs_pagerank.png}
 \caption{Relação entre tamanho e centralidade estrutural das comunidades}
 \label{fig:size_pagerank}
\end{figure}
```

### Tabelas

**Formato**: LaTeX (booktabs)
**Estilo**: Linhas horizontais, sem linhas verticais

Inclusão em LaTeX:
```latex
\begin{table}[htbp]
 \centering
 \caption{Estatísticas das comunidades detectadas}
 \label{tab:comunidades}
 \input{tabelas/tab_comunidades_summary.tex}
\end{table}
```

### Referências Bibliográficas

**Formato**: BibTeX
**Estilo**: ABNT (abntex2cite)

Arquivo: `monografia/postextuais/referencias.bib`

Citação em LaTeX:
```latex
\cite{newman2010networks}
\citeonline{barabasi2016network}
```

## Normas ABNT

A monografia segue as normas ABNT:
- NBR 14724:2011 (Trabalhos acadêmicos)
- NBR 6023:2018 (Referências)
- NBR 10520:2002 (Citações)
- NBR 6028:2003 (Resumo)

Implementadas pelo pacote abntex2.

## Controle de Versão

Arquivos compilados (.aux, .log, .pdf) são ignorados pelo Git (.gitignore).

Comite apenas:
- Arquivos .tex fonte
- Arquivos .bib
- Figuras finais em figuras/
- Tabelas finais em tabelas/

## Workflow Recomendado

1. **Desenvolver análises** em `src/pipeline/`
2. **Gerar figuras** com `src/outputs/figures.py`
3. **Gerar tabelas** com `src/outputs/tables.py`
4. **Escrever texto** em `docs/monografia/textuais/`
5. **Incluir figuras/tabelas** no LaTeX
6. **Compilar** e revisar
7. **Iterar** até finalização

## Notas

- Sempre compile 2x após modificar texto
- Compile 3x após modificar referências
- Use `bibtex` após adicionar novas citações
- Verifique avisos (warnings) no console do LaTeX
- Revise hyperlinks e referências cruzadas

## TODO

- [ ] Adicionar template para apêndices
- [ ] Criar script de compilação automática
- [ ] Adicionar verificação de referências quebradas
- [ ] Implementar contagem de palavras
