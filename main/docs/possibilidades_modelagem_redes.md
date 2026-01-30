# Possibilidades de Modelagem de Redes para Rivalidades Olímpicas

**Documento de referência para trabalhos futuros**
Data: 30 de janeiro de 2026

---

## 1. Rede Bipartida (Atletas ↔ Eventos)

### Estrutura
- **Nós Tipo 1**: Atletas
- **Nós Tipo 2**: Eventos (ou Eventos+Ano)
- **Arestas**: Atleta conquistou medalha no evento

### Narrativas Possíveis
- **Versatilidade**: Atletas que competem em múltiplos eventos (Phelps em várias provas de natação)
- **Especialização vs Generalização**: Quem domina 1 evento vs quem compete em vários
- **Eventos-ponte**: Eventos que conectam comunidades de atletas diferentes
- **Projeção em Atletas**: Rivalidade indireta (competiram nos mesmos eventos, mas não necessariamente juntos)

### Métricas Interessantes
- **Degree do atleta**: Quantos eventos diferentes conquistou medalha
- **Degree do evento**: Quantos medalhistas diferentes (indica competitividade)
- **Centralidade de intermediação**: Atletas que fazem "ponte" entre diferentes eventos

### Exemplo de Aplicação
```python
# Projeção da rede bipartida em atletas
# Peso da aresta entre dois atletas = número de eventos em comum
G_atletas = bipartite.weighted_projected_graph(G_bipartite, atletas)
```

---

## 2. Rede Temporal (Snapshot Networks)

### Estrutura
- Uma rede separada para cada olimpíada
- Analisar evolução ao longo do tempo

### Narrativas Possíveis
- **Emergência de novos dominantes**: Como a rede muda quando Phelps entra/sai
- **Estabilidade de comunidades**: Países/regiões que mantêm domínio ao longo do tempo
- **Transições geracionais**: Quando uma geração de atletas substitui outra
- **Análise de trajetória**: Atletas que participam de múltiplas olimpíadas

### Métricas Interessantes
- **Temporal PageRank**: Influência que se propaga ao longo do tempo
- **Persistência de comunidades**: Detecção de comunidades que se mantêm
- **Taxa de renovação**: Quantos nós novos vs antigos a cada olimpíada
- **Análise de sobrevivência**: Quanto tempo atletas permanecem na elite

### Exemplo de Aplicação
```python
# Criar snapshots por olimpíada
networks_by_year = {}
for year in df['Year'].unique():
    data_year = df[df['Year'] == year]
    networks_by_year[year] = create_network(data_year)

# Analisar evolução de métricas
pagerank_evolution = {year: nx.pagerank(G) for year, G in networks_by_year.items()}
```

---

## 3. Rede Multiplex (Múltiplas Camadas)

### Camadas Possíveis
- **Camada 1**: Competição direta no mesmo pódio (Year+Event)
- **Camada 2**: Competição no mesmo evento em anos diferentes
- **Camada 3**: Competição no mesmo esporte mas eventos diferentes
- **Camada 4**: Mesma nacionalidade (times olímpicos)

### Narrativas Possíveis
- **Rivalidade em múltiplas dimensões**: Brasil vs EUA em natação ao longo dos anos
- **Dominância multi-camada**: Atletas influentes em várias dimensões
- **Análise inter-camadas**: Como rivalidade direta se relaciona com rivalidade histórica

### Métricas Interessantes
- **Multiplex PageRank**: Influência considerando todas as camadas
- **Versatility**: Centralidade em quantas camadas diferentes
- **Layer correlation**: Camadas que tendem a ter estruturas similares
- **Agregação de camadas**: Combinar camadas com pesos diferentes

### Exemplo de Aplicação
```python
# Criar multiplex com 3 camadas
multiplex = {
    'direct': create_network(df, groupby=['Year', 'Event']),
    'historical': create_network(df, groupby=['Event']),
    'national': create_national_network(df)
}

# PageRank multiplex
pagerank_multi = multiplex_pagerank(multiplex, weights={'direct': 0.5, 'historical': 0.3, 'national': 0.2})
```

---

## 4. Rede Ponderada por Performance Relativa

### Estrutura Atual vs Nova

**Atual**: Peso fixo (Ouro→Prata = 3, Ouro→Bronze = 5)

**Opção A - Margem de Vitória**:
- Se tiver dados de tempo/pontuação: peso proporcional à diferença
- Vitória apertada = peso menor, domínio = peso maior
- Exemplo: Phelps ganha por 0.01s → peso 1, ganha por 2s → peso 10

**Opção B - Frequência de Confrontos**:
- Peso = número de vezes que competiram juntos
- Captura rivalidades recorrentes (Phelps vs Lochte)

**Opção C - Contexto da Medalha**:
- Ouro em final olímpica = peso maior
- Bronze em eliminatória = peso menor
- Recordes mundiais = peso extra

### Narrativas Possíveis
- **Rivalidades épicas**: Confrontos repetidos ao longo de múltiplas olimpíadas
- **Domínio absoluto vs vitórias apertadas**
- **Consistência**: Atletas que sempre estão no pódio vs estrelas de uma olimpíada

### Exemplo de Aplicação
```python
# Peso baseado em frequência de confrontos
for (u, v), data in G.edges(data=True):
    confrontos = count_confrontations(u, v, df)
    G[u][v]['weight'] = confrontos
    G[u][v]['avg_margin'] = calculate_margin(u, v, df)
```

---

## 5. Rede Direcionada: Co-ocorrência vs Competição Direta

### Opção A: Rede NÃO-Direcionada (Co-ocorrência)
- Aresta simplesmente indica "competiram juntos"
- Peso = número de vezes que estiveram no mesmo pódio
- **Narrativa**: "Comunidade de campeões" - quem compartilha o palco

### Opção B: Rede Direcionada (Competição - ATUAL)
- Aresta direcionada: perdedor → vencedor
- **Narrativa**: "Hierarquia de dominância" - quem venceu quem

### Opção C: Rede Bidirecional Assimétrica
- Duas arestas com pesos diferentes
- Phelps→Lochte (peso 10), Lochte→Phelps (peso 3)
- **Narrativa**: "Balanço competitivo" - rivalidades equilibradas vs dominação unilateral

### Métricas Comparativas
| Métrica | Direcionada | Não-Direcionada |
|---------|-------------|-----------------|
| PageRank | ✓ | ✗ |
| In/Out-Degree | ✓ | ✗ |
| Betweenness | ✓ | ✓ |
| Clustering | ✗ | ✓ |

---

## 6. Rede Hierárquica por Nível de Medalha

### Estrutura
- **Subgrafo 1**: Apenas medalhistas de ouro (quem venceu quem entre campeões)
- **Subgrafo 2**: Ouro + Prata (batalhas pelo topo)
- **Subgrafo 3**: Completa (incluindo bronze)

### Narrativas Possíveis
- **Elite dos campeões**: Rede só de ouros revela a verdadeira elite
- **Batalha pelo pódio**: Quem sempre está lá vs quem conseguiu 1 bronze
- **Análise estratificada**: Características diferentes entre campeões de ouro vs bronze

### Análise Hierárquica
```python
# Criar redes por nível
G_gold = create_network(df[df['Medal'] == 'Gold'])
G_gold_silver = create_network(df[df['Medal'].isin(['Gold', 'Silver'])])
G_all = create_network(df)

# Comparar estruturas
compare_structures(G_gold, G_gold_silver, G_all)
```

---

## 7. Rede Bipartida Projetada

### Opção A: Projeção em Atletas
```
Atleta A --conectado-a--> Evento X <--conectado-a-- Atleta B
    ↓                                                  ↓
         Atleta A ←----→ Atleta B (rede projetada)
```
- **Peso da aresta**: Número de eventos em comum
- **Narrativa**: Versatilidade compartilhada (atletas que dominam os mesmos tipos de evento)

### Opção B: Projeção em Eventos
```
Evento X --tem--> Atleta A <--participou-- Evento Y
    ↓                                          ↓
         Evento X ←----→ Evento Y (rede projetada)
```
- **Peso da aresta**: Número de atletas que competiram em ambos
- **Narrativa**: Eventos relacionados (atletas que fazem ambos tendem a ser generalistas)

### Aplicação
```python
from networkx.algorithms import bipartite

# Projeção em atletas
G_athletes = bipartite.weighted_projected_graph(B, athlete_nodes)

# Projeção em eventos
G_events = bipartite.weighted_projected_graph(B, event_nodes)
```

---

## 8. Modelagem Especial para Atletismo

### Problema
- Velocista 100m ≠ Saltador em vara
- Mas ambos podem estar no revezamento 4x100m

### Solução 1: Rede Bipartida Atletas-Modalidades
- **Nós tipo 1**: Atletas
- **Nós tipo 2**: Modalidades (corrida, salto, arremesso, etc.)
- **Projeção**: Atletas conectados se compartilham modalidade

### Solução 2: Rede Multiplex
- **Camada "Velocidade"**: 100m, 200m, 400m, revezamentos
- **Camada "Saltos"**: Altura, distância, triplo, vara
- **Camada "Arremessos"**: Peso, disco, dardo, martelo
- **Camada "Resistência"**: 800m+, maratona, marcha

### Solução 3: Agrupamento por Similaridade de Evento
```python
event_groups = {
    'sprints': ['100m', '200m', '400m', '4x100m', '4x400m'],
    'middle_distance': ['800m', '1500m'],
    'long_distance': ['5000m', '10000m', 'Marathon'],
    'hurdles': ['110m Hurdles', '400m Hurdles'],
    'jumps': ['High Jump', 'Long Jump', 'Triple Jump', 'Pole Vault'],
    'throws': ['Shot Put', 'Discus', 'Javelin', 'Hammer']
}

# Criar redes SEPARADAS para cada grupo
for group_name, events in event_groups.items():
    G = create_network(df[df['Event'].isin(events)])
```

---

## 9. Métricas Alternativas ao PageRank

### Por que Phelps pode não ser o mais influente no PageRank?
PageRank considera **estrutura da rede**, não só vitórias:
- Atleta com muitos ouros mas que competiu contra adversários "fracos" → PageRank menor
- Atleta com poucas pratas mas que perdeu para "campeões" → PageRank maior

### Alternativas:

#### A) Eigenvector Centrality
- Importância baseada em estar conectado a nós importantes
- Phelps venceu outros campeões? → Eigenvector alto

#### B) Hub & Authority (HITS)
- **Hub**: Atleta que "perdeu para muitos campeões"
- **Authority**: Atleta que "venceu muitos campeões"
- Phelps seria alta Authority (venceu muitos)

#### C) Degree Centrality Ponderado
- **In-Degree**: Quantos perderam para você (= quantos você venceu)
- **Out-Degree**: Para quantos você perdeu
- **Ratio In/Out**: Phelps teria ratio altíssimo (13 ouros, 1 bronze, 2 pratas)

#### D) Medalha-Weighted Score
```python
score = (gold * 3) + (silver * 2) + (bronze * 1)
```
- Simples mas efetivo

#### E) Dominance Score
```python
dominance = (weighted_in_degree) / (weighted_out_degree + 1)
```
- Quanto você venceu vs quanto perdeu

### Comparação de Métricas
```python
metrics = {
    'pagerank': nx.pagerank(G, weight='weight'),
    'eigenvector': nx.eigenvector_centrality(G, weight='weight'),
    'in_degree': dict(G.in_degree(weight='weight')),
    'dominance': calculate_dominance(G)
}

# Comparar rankings
compare_rankings(metrics)
```

---

## 10. Modelagem Híbrida: Rede Dupla

### Proposta
**Duas redes complementares**:

1. **Rede Síncrona (Year+Event)**: Rivalidades diretas, competições reais
   - Captura quem REALMENTE se enfrentou
   - Menor densidade, mais precisa
   - Fragmentada por natureza

2. **Rede Diacrônica (Event)**: Domínio histórico, comparação cross-geracional
   - Captura quem é o "GOAT" de cada evento
   - Maior densidade, mais especulativa
   - Conecta gerações diferentes

### Métricas Derivadas
- **Dominância Síncrona**: Influência em competições diretas
- **Dominância Diacrônica**: Influência histórica no evento
- **Score Composto**: Média ponderada das duas

### Narrativa para Apresentação
"Modelamos duas perspectivas complementares:
- **Rivalidade direta**: Quem realmente se enfrentou no mesmo pódio
- **Domínio histórico**: Quem é o maior nome de cada evento ao longo das décadas"

### Implementação
```python
# Rede 1: Rivalidades diretas (Year+Event)
G_direct = create_network(df, groupby=['Year', 'Event'])

# Rede 2: Domínio histórico (Event apenas)
G_historical = create_network(df, groupby=['Event'])

# Métricas combinadas
pagerank_direct = nx.pagerank(G_direct, weight='weight')
pagerank_historical = nx.pagerank(G_historical, weight='weight')

combined_score = {
    node: 0.6 * pagerank_direct.get(node, 0) + 0.4 * pagerank_historical.get(node, 0)
    for node in set(G_direct.nodes()) | set(G_historical.nodes())
}
```

---

## 11. Rede de Sucessão (Quem Sucedeu Quem)

### Conceito
- Modelar **transições de domínio** ao longo do tempo
- Aresta direcionada: Atleta A → Atleta B se B ganhou ouro no evento DEPOIS de A

### Narrativa
- **Linhagem de campeões**: Quem herdou o trono de quem
- **Eras de domínio**: Períodos de domínio de atletas específicos
- **Longevidade**: Atletas que dominaram por múltiplas olimpíadas

### Exemplo
```
100m Livre Masculino:
Spitz (1972) → Jager (1976) → ... → Phelps (2004-2008) → Dressel (2020)
```

---

## 12. Rede Geográfica (Países e Regiões)

### Estrutura
- **Nós**: Países (NOC)
- **Arestas**: Rivalidades agregadas entre países
- **Peso**: Soma dos confrontos entre atletas dos dois países

### Narrativas
- **Rivalidade geopolítica**: USA vs USSR, Brasil vs Argentina
- **Blocos regionais**: Europa vs Américas
- **Domínio por esporte**: Quênia no atletismo, USA no basquete

### Métricas
- **Centralidade de país**: Quais países são mais conectados
- **Modularidade geográfica**: Comunidades correspondem a regiões?
- **Evolução histórica**: Como rivalidades mudaram após Guerra Fria

---

## Considerações Finais

### Trade-offs Fundamentais

| Modelagem | Precisão Histórica | Riqueza Relacional | Interpretabilidade | Complexidade Computacional |
|-----------|-------------------|-------------------|-------------------|---------------------------|
| Rede Pontual (Year+Event) | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Rede Histórica (Event) | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Rede Bipartida | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Rede Multiplex | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Rede Temporal | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### Recomendações por Objetivo

**Para análise de rivalidades diretas**: Rede Pontual (Year+Event)
**Para comparação cross-geracional**: Rede Histórica ou Temporal
**Para análise de versatilidade**: Rede Bipartida
**Para análise multidimensional**: Rede Multiplex
**Para evolução ao longo do tempo**: Rede Temporal

---

**Documento compilado por**: Claude Sonnet 4.5
**Baseado em**: Discussões sobre modelagem de redes olímpicas
**Contexto**: TCC - Análise de Redes Complexas no Esporte Olímpico
