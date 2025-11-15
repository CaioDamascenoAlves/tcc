"""
Comparacao Cientifica: Louvain vs Infomap para Deteccao de Comunidades
Objetivo: Investigar impacto de preservar direcao nas comunidades detectadas
"""

import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
from collections import Counter

try:
    import community as community_louvain  # python-louvain
    LOUVAIN_AVAILABLE = True
except ImportError:
    LOUVAIN_AVAILABLE = False
    print("AVISO: python-louvain nao instalado")

try:
    import infomap
    INFOMAP_AVAILABLE = True
except ImportError:
    INFOMAP_AVAILABLE = False
    print("AVISO: infomap nao instalado. Instale com: pip install infomap")

project_root = Path(__file__).parent.parent

print("=" * 80)
print("COMPARACAO CIENTIFICA: LOUVAIN vs INFOMAP")
print("=" * 80)
print()
print("Objetivo: Investigar se preservar direcao muda estrutura comunitaria")
print("=" * 80)
print()

# ==============================================================================
# CARREGAR DADOS
# ==============================================================================

print("[1/6] CARREGANDO DADOS...")
df = pd.read_csv(project_root / 'data' / 'athlete_events.csv')

# Filtrar: Swimming Masculino (mesma base dos testes de validacao)
df_filtered = df[
    (df['Medal'].notna()) &
    (df['Season'] == 'Summer') &
    (df['Sport'] == 'Swimming') &
    (df['Sex'] == 'M')
].copy()

print(f"   Dataset: Swimming Masculino")
print(f"   Registros: {len(df_filtered)}")
print(f"   Periodo: {df_filtered['Year'].min():.0f} - {df_filtered['Year'].max():.0f}")
print(f"   Atletas unicos: {df_filtered['ID'].nunique()}")
print()

# ==============================================================================
# CRIAR REDE DIRECIONADA E PONDERADA
# ==============================================================================

print("[2/6] CONSTRUINDO REDE DIRECIONADA PONDERADA...")

G_directed = nx.DiGraph()

# Pesos
weight_map = {
    ('Gold', 'Bronze'): 5,
    ('Gold', 'Silver'): 3,
    ('Silver', 'Bronze'): 2
}

# Adicionar nos com atributos
for _, row in df_filtered.iterrows():
    G_directed.add_node(
        row['ID'],
        name=row['Name'],
        year=row['Year'],
        team=row['Team']
    )

# Adicionar arestas direcionadas
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
                    weight_key = (winner_medal, loser_medal)
                    weight = weight_map.get(weight_key, 1)

                    if G_directed.has_edge(loser_id, winner_id):
                        G_directed[loser_id][winner_id]['weight'] += weight
                    else:
                        G_directed.add_edge(loser_id, winner_id, weight=weight)

print(f"   Nos: {G_directed.number_of_nodes()}")
print(f"   Arestas direcionadas: {G_directed.number_of_edges()}")
print()

# ==============================================================================
# DETECCAO DE COMUNIDADES: LOUVAIN (UNDIRECTED)
# ==============================================================================

print("[3/6] LOUVAIN (grafo nao-direcionado)...")

if not LOUVAIN_AVAILABLE:
    print("   ERRO: python-louvain nao instalado!")
    print("   Instale com: pip install python-louvain")
    exit(1)

# Converter para nao-direcionado (simetrizacao)
G_undirected = G_directed.to_undirected()

# Rodar Louvain
louvain_communities = community_louvain.best_partition(G_undirected, weight='weight')

# Estatisticas
louvain_num_communities = len(set(louvain_communities.values()))
louvain_sizes = Counter(louvain_communities.values())

print(f"   Comunidades detectadas: {louvain_num_communities}")
print(f"   Tamanho medio: {np.mean(list(louvain_sizes.values())):.1f} atletas")
print(f"   Tamanho minimo: {min(louvain_sizes.values())} atletas")
print(f"   Tamanho maximo: {max(louvain_sizes.values())} atletas")
print()

# ==============================================================================
# DETECCAO DE COMUNIDADES: INFOMAP (DIRECTED)
# ==============================================================================

print("[4/6] INFOMAP (grafo direcionado)...")

if not INFOMAP_AVAILABLE:
    print("   ERRO: infomap nao instalado!")
    print("   Instale com: pip install infomap")
    exit(1)

# Criar objeto Infomap
im = infomap.Infomap("--directed --two-level")

# Adicionar arestas (Infomap usa IDs internos)
node_to_id = {node: idx for idx, node in enumerate(G_directed.nodes())}
id_to_node = {idx: node for node, idx in node_to_id.items()}

for source, target, data in G_directed.edges(data=True):
    weight = data.get('weight', 1.0)
    im.add_link(node_to_id[source], node_to_id[target], weight)

# Rodar algoritmo
im.run()

# Extrair comunidades
infomap_communities = {}
for node in im.tree:
    if node.is_leaf:
        original_node_id = id_to_node[node.node_id]
        infomap_communities[original_node_id] = node.module_id

# Estatisticas
infomap_num_communities = len(set(infomap_communities.values()))
infomap_sizes = Counter(infomap_communities.values())

print(f"   Comunidades detectadas: {infomap_num_communities}")
print(f"   Tamanho medio: {np.mean(list(infomap_sizes.values())):.1f} atletas")
print(f"   Tamanho minimo: {min(infomap_sizes.values())} atletas")
print(f"   Tamanho maximo: {max(infomap_sizes.values())} atletas")
print()

# ==============================================================================
# COMPARACAO: NMI (Normalized Mutual Information)
# ==============================================================================

print("[5/6] COMPARANDO PARTICOES...")

from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score

# Criar listas alinhadas
common_nodes = set(louvain_communities.keys()) & set(infomap_communities.keys())
louvain_labels = [louvain_communities[node] for node in common_nodes]
infomap_labels = [infomap_communities[node] for node in common_nodes]

# Metricas de comparacao
nmi = normalized_mutual_info_score(louvain_labels, infomap_labels)
ari = adjusted_rand_score(louvain_labels, infomap_labels)

print(f"   Normalized Mutual Information (NMI): {nmi:.4f}")
print(f"   Adjusted Rand Index (ARI): {ari:.4f}")
print()
print("   Interpretacao:")
print(f"   - NMI = 1.0: Particoes identicas")
print(f"   - NMI = 0.0: Particoes independentes")
print(f"   - NMI = {nmi:.4f}: ", end="")

if nmi > 0.8:
    print("ALTA concordancia - algoritmos convergem")
elif nmi > 0.5:
    print("MODERADA concordancia - algumas diferencas")
else:
    print("BAIXA concordancia - algoritmos divergem significativamente")

print()

# ==============================================================================
# ANALISE: QUAIS ATLETAS MUDARAM DE COMUNIDADE?
# ==============================================================================

print("[6/6] ANALISANDO MUDANCAS...")

# Criar DataFrame de comparacao
comparison = []
for node in common_nodes:
    comparison.append({
        'athlete_id': node,
        'name': G_directed.nodes[node]['name'],
        'louvain_community': louvain_communities[node],
        'infomap_community': infomap_communities[node],
        'changed': louvain_communities[node] != infomap_communities[node]
    })

df_comparison = pd.DataFrame(comparison)

# Estatisticas de mudanca
num_changed = df_comparison['changed'].sum()
pct_changed = 100 * num_changed / len(df_comparison)

print(f"   Atletas que mudaram de comunidade: {num_changed}/{len(df_comparison)} ({pct_changed:.1f}%)")
print()

# Mostrar alguns exemplos de mudancas
if num_changed > 0:
    print("   Exemplos de atletas que mudaram:")
    changed_athletes = df_comparison[df_comparison['changed']].head(10)
    for _, row in changed_athletes.iterrows():
        print(f"      {row['name']}: Louvain C{row['louvain_community']} -> Infomap C{row['infomap_community']}")
    print()

# ==============================================================================
# CONCLUSAO
# ==============================================================================

print("=" * 80)
print("CONCLUSAO")
print("=" * 80)
print()

if nmi > 0.8:
    print("RESULTADO: Algoritmos CONVERGEM")
    print()
    print("Interpretacao:")
    print("- Estrutura comunitaria e robusta independente de direcao")
    print("- Louvain (undirected) captura adequadamente agrupamentos estruturais")
    print("- Preservar direcao (Infomap) nao revela comunidades radicalmente diferentes")
    print()
    print("Implicacao para TCC:")
    print("- Justifica uso de Louvain com simetrizacao")
    print("- Direcao importa para PageRank (dominancia individual)")
    print("- Direcao menos critica para comunidades (agrupamentos estruturais)")

elif nmi > 0.5:
    print("RESULTADO: Algoritmos PARCIALMENTE CONCORDAM")
    print()
    print("Interpretacao:")
    print("- Estrutura comunitaria possui componente direcional relevante")
    print("- Infomap revela nuances nao capturadas por Louvain")
    print("- Diferenca pode indicar hierarquias de dominancia dentro de eras")
    print()
    print("Implicacao para TCC:")
    print("- Considerar reportar AMBAS as particoes")
    print("- Comparacao metodologica pode ser contribuicao cientifica")
    print("- Discutir diferenca no contexto de dominancia vs co-ocorrencia")

else:
    print("RESULTADO: Algoritmos DIVERGEM SIGNIFICATIVAMENTE")
    print()
    print("Interpretacao:")
    print("- Direcao e CRITICA para estrutura comunitaria")
    print("- Louvain (undirected) mascara hierarquias reais")
    print("- Infomap revela estrutura profundamente diferente baseada em dominancia")
    print()
    print("Implicacao para TCC:")
    print("- RECONSIDERAR uso exclusivo de Louvain")
    print("- Infomap pode ser metodologia principal")
    print("- Diferenca fundamental deve ser explorada cientificamente")

print()
print("=" * 80)
print()
print("PROXIMOS PASSOS:")
print("1. Analisar comunidades especificas que divergem")
print("2. Investigar se Infomap detecta 'dominadores' vs 'competidores'")
print("3. Validar interpretacao com exemplos concretos de atletas")
print("4. Decidir qual algoritmo (ou ambos) reportar na monografia")
print()
print("=" * 80)
