"""
COMPARACAO CIENTIFICA: Louvain vs Infomap
Investiga impacto de preservar direcao na deteccao de comunidades
"""

import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
from collections import Counter
import community as community_louvain
import igraph as ig
from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score

project_root = Path(__file__).parent.parent

print("=" * 80)
print("COMPARACAO LOUVAIN vs INFOMAP")
print("=" * 80)
print()

# ==============================================================================
# CARREGAR E CONSTRUIR REDE
# ==============================================================================

print("[1/5] Construindo rede Swimming Masculino...")
df = pd.read_csv(project_root / 'data' / 'athlete_events.csv')
df_filtered = df[
    (df['Medal'].notna()) &
    (df['Season'] == 'Summer') &
    (df['Sport'] == 'Swimming') &
    (df['Sex'] == 'M')
].copy()

G = nx.DiGraph()
weight_map = {
    ('Gold', 'Bronze'): 5,
    ('Gold', 'Silver'): 3,
    ('Silver', 'Bronze'): 2
}

# Adicionar nos
for _, row in df_filtered.iterrows():
    G.add_node(row['ID'], name=row['Name'])

# Adicionar arestas
for event_name in df_filtered['Event'].unique():
    for year in df_filtered['Year'].unique():
        event_group = df_filtered[
            (df_filtered['Event'] == event_name) &
            (df_filtered['Year'] == year)
        ]
        if len(event_group) < 2:
            continue

        medalists = event_group[['ID', 'Medal']].values
        for i, (loser_id, loser_medal) in enumerate(medalists):
            for winner_id, winner_medal in medalists[:i]:
                if loser_medal != winner_medal:
                    weight = weight_map.get((winner_medal, loser_medal), 1)
                    if G.has_edge(loser_id, winner_id):
                        G[loser_id][winner_id]['weight'] += weight
                    else:
                        G.add_edge(loser_id, winner_id, weight=weight)

print(f"   Nos: {G.number_of_nodes()}")
print(f"   Arestas direcionadas: {G.number_of_edges()}")
print()

# ==============================================================================
# LOUVAIN (UNDIRECTED)
# ==============================================================================

print("[2/5] Louvain (undirected)...")
G_undirected = G.to_undirected()
louvain_comms = community_louvain.best_partition(G_undirected, weight='weight')
louvain_num = len(set(louvain_comms.values()))
print(f"   Comunidades: {louvain_num}")
print()

# ==============================================================================
# INFOMAP (DIRECTED) via igraph
# ==============================================================================

print("[3/5] Infomap (directed) via igraph...")

# Converter NetworkX -> igraph
node_list = list(G.nodes())
node_to_idx = {node: idx for idx, node in enumerate(node_list)}

edges = []
weights = []
for u, v, data in G.edges(data=True):
    edges.append((node_to_idx[u], node_to_idx[v]))
    weights.append(data.get('weight', 1.0))

g_ig = ig.Graph(directed=True)
g_ig.add_vertices(len(node_list))
g_ig.add_edges(edges)
g_ig.es['weight'] = weights

# Rodar Infomap
infomap_result = g_ig.community_infomap(edge_weights='weight')

# Extrair comunidades
infomap_comms = {}
for idx, comm_id in enumerate(infomap_result.membership):
    original_node = node_list[idx]
    infomap_comms[original_node] = comm_id

infomap_num = len(set(infomap_comms.values()))
print(f"   Comunidades: {infomap_num}")
print()

# ==============================================================================
# COMPARACAO
# ==============================================================================

print("[4/5] Comparando particoes...")

# Alinhar labels
common_nodes = set(louvain_comms.keys()) & set(infomap_comms.keys())
louvain_labels = [louvain_comms[node] for node in common_nodes]
infomap_labels = [infomap_comms[node] for node in common_nodes]

# Metricas
nmi = normalized_mutual_info_score(louvain_labels, infomap_labels)
ari = adjusted_rand_score(louvain_labels, infomap_labels)

print(f"   NMI (Normalized Mutual Information): {nmi:.4f}")
print(f"   ARI (Adjusted Rand Index): {ari:.4f}")
print()

if nmi > 0.8:
    print("   Interpretacao: ALTA concordancia - algoritmos convergem")
elif nmi > 0.5:
    print("   Interpretacao: MODERADA concordancia")
else:
    print("   Interpretacao: BAIXA concordancia - algoritmos divergem!")
print()

# ==============================================================================
# ANALISE DE MUDANCAS
# ==============================================================================

print("[5/5] Analisando mudancas...")

comparison = []
for node in common_nodes:
    comparison.append({
        'athlete_id': node,
        'name': G.nodes[node]['name'],
        'louvain': louvain_comms[node],
        'infomap': infomap_comms[node],
        'changed': louvain_comms[node] != infomap_comms[node]
    })

df_comp = pd.DataFrame(comparison)
num_changed = df_comp['changed'].sum()
pct_changed = 100 * num_changed / len(df_comp)

print(f"   Atletas que mudaram: {num_changed}/{len(df_comp)} ({pct_changed:.1f}%)")
print()

if num_changed > 0:
    print("   Exemplos de mudancas:")
    for _, row in df_comp[df_comp['changed']].head(5).iterrows():
        print(f"      {row['name']}: Louvain C{row['louvain']} -> Infomap C{row['infomap']}")
print()

# ==============================================================================
# CONCLUSAO
# ==============================================================================

print("=" * 80)
print("CONCLUSAO")
print("=" * 80)
print()

print(f"Louvain (undirected):  {louvain_num} comunidades")
print(f"Infomap (directed):    {infomap_num} comunidades")
print(f"Concordancia (NMI):    {nmi:.4f}")
print(f"Atletas que mudaram:   {pct_changed:.1f}%")
print()

if nmi > 0.8:
    print("RESULTADO: Estrutura comunitaria e ROBUSTA a direcao")
    print("- Louvain (undirected) captura adequadamente agrupamentos")
    print("- Preservar direcao nao altera fundamentalmente comunidades")
    print("- JUSTIFICA uso de Louvain com simetrizacao")
elif nmi > 0.5:
    print("RESULTADO: Direcao tem impacto MODERADO")
    print("- Infomap revela nuances nao capturadas por Louvain")
    print("- Considerar reportar AMBOS os resultados")
else:
    print("RESULTADO: Direcao e CRITICA!")
    print("- Louvain mascara hierarquias reais")
    print("- RECONSIDERAR uso exclusivo de Louvain")

print()
print("=" * 80)
