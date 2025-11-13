# Resultados

Este diretório contém todos os resultados gerados pelo pipeline de análise.

## Tamanho Total

Aproximadamente **432 MB** de resultados (não commitados no Git).

## Estrutura

```
results/
├── networks/              # Redes geradas (CSV, GEXF, JSON)
│   ├── consolidated_athletes.csv
│   ├── consolidated_edges.csv
│   ├── summaries.json
│   ├── swimming/
│   ├── basketball/
│   └── football/
│
└── additional_analyses/   # Análises adicionais
    ├── medal_profile_by_community.csv
    ├── community_hierarchy.csv
    ├── inter_community_connectivity.csv
    └── top_rivalry_pairs.csv
```

## Como Gerar

Para regenerar todos os resultados:

```bash
cd src/pipeline
python 01_network_generation.py
python 02a_community_enrichment.py
python 02b_medal_profile.py
python 02c_connectivity.py
python 02d_hierarchy.py
python 02e_rivalries.py
```

Tempo estimado: 10-15 minutos

## Conteúdo

### Networks
- **8 redes olímpicas** (Swimming M/F individual/team, Basketball M/F, Football M/F)
- Formatos: CSV (métricas), GEXF (visualização), JSON (estatísticas)
- Total: ~100 MB de redes + ~332 MB de arestas

### Additional Analyses
- Perfis de medalhas por comunidade
- Hierarquia estrutural das comunidades
- Conectividade e segregação inter-comunidade
- Top rivalidades estruturais
- Total: ~5 MB

## Principais Resultados

- **4.659 atletas** analisados
- **37 comunidades** detectadas
- **0 nós isolados** em todas as redes
- **662 pódios válidos** processados
