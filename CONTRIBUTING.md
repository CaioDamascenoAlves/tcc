# Guia de Contribuicao

Este repositorio contem um Trabalho de Conclusao de Curso academico. Contribuicoes sao bem-vindas para melhorar a implementacao tecnica e a qualidade da pesquisa.

## Como Contribuir

### Reportar Problemas

Ao encontrar erros ou problemas:

1. Verifique se o problema ja foi reportado em [Issues](https://github.com/CaioDamascenoAlves/tcc/issues)
2. Crie uma nova issue descrevendo:
   - O que esperava acontecer
   - O que realmente aconteceu
   - Passos para reproduzir o problema
   - Ambiente (sistema operacional, versao do Python)

### Propor Melhorias

Para sugerir melhorias na implementacao ou analise:

1. Abra uma issue explicando a proposta
2. Aguarde discussao antes de implementar mudancas significativas
3. Referencie literatura academica relevante quando aplicavel

### Submeter Alteracoes

1. Faca fork do repositorio
2. Crie um branch para sua alteracao: `git checkout -b minha-melhoria`
3. Faca commit das mudancas com mensagens claras
4. Execute os testes para verificar que nada quebrou
5. Faca push para seu fork: `git push origin minha-melhoria`
6. Abra um Pull Request descrevendo as mudancas

## Estrutura do Codigo

### Python (main/src/)

- Siga PEP 8 para estilo de codigo
- Adicione docstrings para funcoes e classes
- Mantenha dependencias atualizadas em requirements.txt

### LaTeX (monografia/)

- Siga padroes ABNT (NBR 14724:2011)
- Use abnTeX2 para formatacao
- Verifique referencias bibliograficas (DOIs validos)
- Consulte `monografia/CLAUDE.md` para diretrizes de revisao

### Dados e Resultados

- Nao commite dados brutos (respeitando .gitignore)
- Arquivos grandes devem ir para Google Drive (veja workflows)
- Resultados de analise podem ser commitados se pequenos

## Padroes de Qualidade

### Codigo Python

- Teste seu codigo antes de submeter
- Documente parametros e retornos de funcoes
- Evite hardcoding de caminhos (use paths relativos)

### Documentacao LaTeX

- Referencias devem ter DOI valido
- Foco em redes complexas e analise esportiva
- Evite citacoes fora do escopo tematico
- Mantenha linguagem academica clara e direta

### Commits

- Mensagens descritivas em portugues
- Um commit por mudanca logica
- Evite commits de arquivos temporarios

## Diretrizes Academicas

Este e um trabalho academico em andamento:

- Respeite direitos autorais do dataset (Kaggle/IOC)
- Cite fontes apropriadamente
- Mantenha integridade cientifica
- Discussoes devem ser construtivas e embasadas

## Licenciamento

- Codigo Python: MIT License
- Monografia LaTeX: LPPL 1.3c
- Apresentacao: LPPL 1.3c

Contribuicoes ao codigo seguem MIT. Contribuicoes ao texto academico devem respeitar a LPPL 1.3c.

## Duvidas

Para duvidas sobre:
- Implementacao tecnica: Abra uma issue
- Metodologia academica: Consulte a monografia
- Estrutura do projeto: Veja README.md principal

---

**Importante**: Este repositorio documenta pesquisa academica. Mudancas na metodologia ou interpretacao dos resultados devem ser discutidas antes da implementacao.
