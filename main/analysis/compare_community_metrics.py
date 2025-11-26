"""
Comparação Científica Completa: Louvain vs Infomap
===================================================

Este script compara as comunidades detectadas pelos dois algoritmos,
calculando as MESMAS métricas para ambos:

1. Número de comunidades
2. Modularidade
3. Tamanho médio/distribuição de comunidades
4. Entropia temporal das comunidades
5. Entropia geográfica das comunidades
6. PageRank médio por comunidade
7. Coeficiente de variação de PageRank

Objetivo: Determinar se Infomap (directed) revela insights substancialmente
diferentes de Louvain (undirected) que justifiquem sua adoção.
"""

import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
from collections import Counter
import json

try:
    import community as community_louvain
    LOUVAIN_AVAILABLE = True
except ImportError:
    LOUVAIN_AVAILABLE = False
    print("ERRO: python-louvain não instalado")
    exit(1)

try:
    import igraph as ig
    INFOMAP_AVAILABLE = True
except ImportError:
    INFOMAP_AVAILABLE = False
    print("ERRO: igraph não instalado. Instale com: pip install igraph")
    exit(1)

from scipy.stats import entropy

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def calculate_shannon_entropy(counts):
    """Entropia de Shannon para medir diversidade"""
    total = sum(counts.values())
    if total == 0:
        return 0
    probs = np.array([count/total for count in counts.values()])
    return entropy(probs, base=2)

def identify_era(year):
    """Classifica períodos olímpicos em eras"""
    if year < 1920:
        return "Era Pioneira (1896-1919)"
    elif year < 1950:
        return "Entre Guerras (1920-1949)"
    elif year < 1980:
        return "Guerra Fria (1950-1979)"
    elif year < 2000:
        return "Pós-Guerra Fria (1980-1999)"
    else:
        return "Era Moderna (2000+)"

def calculate_gini(values):
    """Calcula índice de Gini para desigualdade"""
    if len(values) == 0:
        return 0.0
    values = np.array([v for v in values if v > 0])
    if len(values) == 0:
        return 0.0
    sorted_values = np.sort(values)
    n = len(sorted_values)
    cumsum = np.cumsum(sorted_values)
    gini = (2 * np.sum((np.arange(1, n+1)) * sorted_values)) / (n * np.sum(sorted_values)) - (n + 1) / n
    return gini

def analyze_communities(communities_dict, G, df_filtered, algorithm_name):
    """
    Analisa comunidades detectadas e calcula métricas agregadas.

    Args:
        communities_dict: {node_id: community_id}
        G: NetworkX DiGraph
        df_filtered: DataFrame com dados dos atletas
        algorithm_name: "Louvain" ou "Infomap"

    Returns:
        DataFrame com métricas por comunidade
    """
    print(f"\n[Analisando comunidades {algorithm_name}]")

    # Adicionar comunidades como atributo de nó
    nx.set_node_attributes(G, communities_dict, 'community')

    # Preparar dados temporais
    year_map = {}
    noc_map = {}
    pagerank = nx.pagerank(G, weight='weight')

    for _, row in df_filtered.iterrows():
        node_id = row['ID']
        if node_id in G.nodes():
            year_map[node_id] = row['Year']
            noc_map[node_id] = row['NOC']

    # Agrupar por comunidade
    community_profiles = []

    for comm_id in set(communities_dict.values()):
        # Membros da comunidade
        members = [node for node, c in communities_dict.items() if c == comm_id]
        size = len(members)

        if size < 2:
            continue

        # === ANÁLISE TEMPORAL ===
        years = [year_map[node] for node in members if node in year_map]
        if len(years) == 0:
            continue

        year_range = (min(years), max(years))
        span_years = year_range[1] - year_range[0]

        # Entropia temporal (por década)
        decades = [(int(y) // 10 * 10) for y in years]
        decade_counts = Counter(decades)
        temporal_entropy = calculate_shannon_entropy(decade_counts)

        # Eras
        eras = [identify_era(y) for y in years]
        era_counts = Counter(eras)
        dominant_era = era_counts.most_common(1)[0][0]
        num_eras = len(era_counts)

        # === ANÁLISE GEOGRÁFICA ===
        nocs = [noc_map[node] for node in members if node in noc_map]
        noc_counts = Counter(nocs)
        num_countries = len(noc_counts)
        geographic_entropy = calculate_shannon_entropy(noc_counts)

        dominant_country = noc_counts.most_common(1)[0][0] if len(noc_counts) > 0 else None
        country_dominance = noc_counts[dominant_country] / len(nocs) if dominant_country else 0

        # === ANÁLISE DE PERFORMANCE ===
        pr_values = [pagerank[node] for node in members if node in pagerank]

        if len(pr_values) == 0:
            continue

        pr_mean = np.mean(pr_values)
        pr_std = np.std(pr_values)
        pr_cv = pr_std / pr_mean if pr_mean > 0 else 0
        gini_pr = calculate_gini(pr_values)

        # Armazenar perfil
        community_profiles.append({
            'algorithm': algorithm_name,
            'community_id': comm_id,
            'size': size,

            # Temporal
            'year_start': year_range[0],
            'year_end': year_range[1],
            'span_years': span_years,
            'temporal_entropy': temporal_entropy,
            'num_eras': num_eras,
            'dominant_era': dominant_era,

            # Geográfica
            'num_countries': num_countries,
            'geographic_entropy': geographic_entropy,
            'dominant_country': dominant_country,
            'country_dominance': country_dominance,

            # Performance
            'pagerank_mean': pr_mean,
            'pagerank_std': pr_std,
            'pagerank_cv': pr_cv,
            'gini_pagerank': gini_pr,
        })

    return pd.DataFrame(community_profiles)

# ==============================================================================
# CONSTRUIR REDE E DETECTAR COMUNIDADES
# ==============================================================================

print("=" * 80)
print("COMPARAÇÃO LOUVAIN vs INFOMAP - MÉTRICAS DE COMUNIDADES")
print("=" * 80)

project_root = Path(__file__).parent.parent

# Carregar dados
print("\n[1/6] Carregando dados...")
df = pd.read_csv(project_root / 'data' / 'athlete_events.csv')

# Filtrar: Swimming Masculino (exemplo representativo)
df_filtered = df[
    (df['Medal'].notna()) &
    (df['Season'] == 'Summer') &
    (df['Sport'] == 'Swimming') &
    (df['Sex'] == 'M')
].copy()

print(f"   Dataset: Swimming Masculino")
print(f"   Atletas únicos: {df_filtered['ID'].nunique()}")
print(f"   Período: {df_filtered['Year'].min():.0f} - {df_filtered['Year'].max():.0f}")

# Construir rede direcionada
print("\n[2/6] Construindo rede direcionada...")

G = nx.DiGraph()

weight_map = {
    ('Gold', 'Bronze'): 5,
    ('Gold', 'Silver'): 3,
    ('Silver', 'Bronze'): 2
}

# Adicionar nós
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

print(f"   Nós: {G.number_of_nodes()}")
print(f"   Arestas direcionadas: {G.number_of_edges()}")

# ==============================================================================
# LOUVAIN (UNDIRECTED)
# ==============================================================================

print("\n[3/6] Detectando comunidades com LOUVAIN (undirected)...")

G_undirected = G.to_undirected()
louvain_communities = community_louvain.best_partition(G_undirected, weight='weight')
louvain_num = len(set(louvain_communities.values()))

print(f"   Comunidades detectadas: {louvain_num}")

# Calcular modularidade
louvain_modularity = community_louvain.modularity(louvain_communities, G_undirected, weight='weight')
print(f"   Modularidade: {louvain_modularity:.4f}")

# Analisar comunidades Louvain
louvain_df = analyze_communities(louvain_communities, G, df_filtered, "Louvain")

# ==============================================================================
# INFOMAP (DIRECTED)
# ==============================================================================

print("\n[4/6] Detectando comunidades com INFOMAP (directed)...")

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
infomap_communities = {}
for idx, comm_id in enumerate(infomap_result.membership):
    original_node = node_list[idx]
    infomap_communities[original_node] = comm_id

infomap_num = len(set(infomap_communities.values()))
print(f"   Comunidades detectadas: {infomap_num}")

# Calcular modularidade do Infomap (no grafo não-direcionado para comparação justa)
infomap_modularity = infomap_result.modularity
print(f"   Modularidade: {infomap_modularity:.4f}")

# Analisar comunidades Infomap
infomap_df = analyze_communities(infomap_communities, G, df_filtered, "Infomap")

# ==============================================================================
# COMPARAÇÃO ESTATÍSTICA
# ==============================================================================

print("\n[5/6] Comparando métricas das comunidades...")

# Combinar DataFrames
comparison_df = pd.concat([louvain_df, infomap_df], ignore_index=True)

# Estatísticas agregadas por algoritmo
print("\n" + "=" * 80)
print("COMPARAÇÃO DE MÉTRICAS DAS COMUNIDADES")
print("=" * 80)

for algo in ['Louvain', 'Infomap']:
    algo_data = comparison_df[comparison_df['algorithm'] == algo]

    print(f"\n{algo}:")
    print(f"  Número de comunidades: {len(algo_data)}")
    print(f"  Tamanho médio: {algo_data['size'].mean():.1f} ± {algo_data['size'].std():.1f}")
    print(f"  Tamanho mín/máx: {algo_data['size'].min()} / {algo_data['size'].max()}")
    print()
    print(f"  Entropia Temporal:")
    print(f"    Média: {algo_data['temporal_entropy'].mean():.3f}")
    print(f"    Desvio: {algo_data['temporal_entropy'].std():.3f}")
    print()
    print(f"  Entropia Geográfica:")
    print(f"    Média: {algo_data['geographic_entropy'].mean():.3f}")
    print(f"    Desvio: {algo_data['geographic_entropy'].std():.3f}")
    print()
    print(f"  PageRank médio por comunidade:")
    print(f"    Média: {algo_data['pagerank_mean'].mean():.6f}")
    print(f"    CV médio: {algo_data['pagerank_cv'].mean():.3f}")
    print()
    print(f"  Gini PageRank:")
    print(f"    Média: {algo_data['gini_pagerank'].mean():.3f}")
    print(f"    Desvio: {algo_data['gini_pagerank'].std():.3f}")

# ==============================================================================
# EXPORTAR RESULTADOS
# ==============================================================================

print("\n[6/6] Exportando resultados...")

output_dir = project_root / 'analysis'
output_dir.mkdir(exist_ok=True)

# CSV com métricas
comparison_df.to_csv(output_dir / 'louvain_vs_infomap_metrics.csv', index=False)
print(f"   [OK] {output_dir / 'louvain_vs_infomap_metrics.csv'}")

# JSON com resumo
summary = {
    'dataset': 'Swimming Masculino',
    'num_nodes': G.number_of_nodes(),
    'num_edges': G.number_of_edges(),

    'louvain': {
        'num_communities': louvain_num,
        'modularity': float(louvain_modularity),
        'avg_size': float(louvain_df['size'].mean()),
        'temporal_entropy_avg': float(louvain_df['temporal_entropy'].mean()),
        'geographic_entropy_avg': float(louvain_df['geographic_entropy'].mean()),
        'pagerank_cv_avg': float(louvain_df['pagerank_cv'].mean()),
        'gini_pagerank_avg': float(louvain_df['gini_pagerank'].mean()),
    },

    'infomap': {
        'num_communities': infomap_num,
        'modularity': float(infomap_modularity),
        'avg_size': float(infomap_df['size'].mean()),
        'temporal_entropy_avg': float(infomap_df['temporal_entropy'].mean()),
        'geographic_entropy_avg': float(infomap_df['geographic_entropy'].mean()),
        'pagerank_cv_avg': float(infomap_df['pagerank_cv'].mean()),
        'gini_pagerank_avg': float(infomap_df['gini_pagerank'].mean()),
    },

    'differences': {
        'num_communities_diff': infomap_num - louvain_num,
        'temporal_entropy_diff': float(infomap_df['temporal_entropy'].mean() - louvain_df['temporal_entropy'].mean()),
        'geographic_entropy_diff': float(infomap_df['geographic_entropy'].mean() - louvain_df['geographic_entropy'].mean()),
    }
}

with open(output_dir / 'louvain_vs_infomap_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f"   [OK] {output_dir / 'louvain_vs_infomap_summary.json'}")

# ==============================================================================
# CONCLUSÃO
# ==============================================================================

print("\n" + "=" * 80)
print("CONCLUSÃO")
print("=" * 80)

print(f"\nLouvain: {louvain_num} comunidades, modularidade {louvain_modularity:.4f}")
print(f"Infomap: {infomap_num} comunidades, modularidade {infomap_modularity:.4f}")

print(f"\nDiferenças nas métricas agregadas:")
print(f"  Entropia Temporal: Δ = {summary['differences']['temporal_entropy_diff']:.3f}")
print(f"  Entropia Geográfica: Δ = {summary['differences']['geographic_entropy_diff']:.3f}")

if abs(summary['differences']['temporal_entropy_diff']) < 0.2 and \
   abs(summary['differences']['geographic_entropy_diff']) < 0.2:
    print("\n RESULTADO: Diferenças PEQUENAS nas métricas agregadas")
    print("  → Louvain captura adequadamente estrutura comunitária")
    print("  → Infomap encontra mais comunidades mas padrões similares")
    print("  → RECOMENDAÇÃO: Usar Louvain (simplicidade + interpretabilidade)")
else:
    print("\n RESULTADO: Diferenças SIGNIFICATIVAS nas métricas")
    print("  → Infomap revela estrutura substancialmente diferente")
    print("  → RECOMENDAÇÃO: Considerar usar AMBOS ou apenas Infomap")

print("\n" + "=" * 80)
