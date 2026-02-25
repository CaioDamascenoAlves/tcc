#!/usr/bin/env python3
"""
Análise Temporal Dinâmica - 12 Redes Individuais

Para cada uma das 12 redes principais, calcula métricas estruturais
em janelas temporais (décadas), revelando evolução ao longo do tempo:
- Densidade
- Clustering médio
- PageRank médio
- Modularidade
- Número de componentes

Objetivo: Identificar pontos de mudança estrutural e padrões de evolução.
"""

import pandas as pd
import numpy as np
import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

print("=" * 80)
print("ANÁLISE TEMPORAL DINÂMICA - 12 REDES INDIVIDUAIS")
print("=" * 80)

# ====================
# 1. CONFIGURAÇÃO
# ====================

# As 12 redes principais do estudo
NETWORKS_CONFIG = [
    {'sport': 'Football', 'event': "Men's Football", 'gender': 'M', 'name': 'Futebol M'},
    {'sport': 'Football', 'event': "Women's Football", 'gender': 'F', 'name': 'Futebol F'},
    {'sport': 'Basketball', 'event': "Men's Basketball", 'gender': 'M', 'name': 'Basquete M'},
    {'sport': 'Basketball', 'event': "Women's Basketball", 'gender': 'F', 'name': 'Basquete F'},
    {'sport': 'Athletics', 'event': "Athletics Men's 100 metres", 'gender': 'M', 'name': 'Atletismo 100m M'},
    {'sport': 'Athletics', 'event': "Athletics Women's 100 metres", 'gender': 'F', 'name': 'Atletismo 100m F'},
    {'sport': 'Swimming', 'event': "Swimming Men's 100 metres Freestyle", 'gender': 'M', 'name': 'Natação 100m Livre M'},
    {'sport': 'Swimming', 'event': "Swimming Women's 100 metres Freestyle", 'gender': 'F', 'name': 'Natação 100m Livre F'},
    {'sport': 'Judo', 'event': "Judo Men's Middleweight", 'gender': 'M', 'name': 'Judô -90kg M'},
    {'sport': 'Judo', 'event': "Judo Women's Half-Middleweight", 'gender': 'F', 'name': 'Judô -70kg F'},
    {'sport': 'Boxing', 'event': "Boxing Men's Welterweight", 'gender': 'M', 'name': 'Boxe Welter M'},
    {'sport': 'Boxing', 'event': "Boxing Women's Middleweight", 'gender': 'F', 'name': 'Boxe Médio F'},
]

# Janelas temporais (décadas) - ATÉ RIO 2016 (SEM Tokyo 2020)
DECADES = [(1890, 1909), (1910, 1919), (1920, 1929), (1930, 1939), (1940, 1949),
           (1950, 1959), (1960, 1969), (1970, 1979), (1980, 1989), (1990, 1999),
           (2000, 2009), (2010, 2016)]

# ====================
# 2. CARREGAR DADOS
# ====================

print("\n📂 Carregando dados originais...")

try:
    # Tentar carregar dataset limpo (SEM Tokyo 2020)
    df = pd.read_csv('../data/athlete_events_clean.csv')
    print(f"✓ Dataset carregado: {len(df)} registros")
except FileNotFoundError:
    print("❌ Arquivo athlete_events_clean.csv não encontrado")
    print("   Tentando carregar do diretório principal...")
    try:
        df = pd.read_csv('data/athlete_events_clean.csv')
        print(f"✓ Dataset carregado: {len(df)} registros")
    except FileNotFoundError:
        print("❌ Dataset não encontrado em nenhum local esperado")
        exit(1)

# Filtrar apenas medalhistas de verão
df = df[(df['Medal'].notna()) & (df['Season'] == 'Summer')].copy()
print(f"✓ Medalhistas de verão: {len(df)} registros")

# ====================
# 3. FUNÇÕES AUXILIARES
# ====================

def build_network_until_year(df_filtered, max_year, weighting='5-3-2'):
    """
    Constrói rede acumulada até max_year (inclusive).
    """
    df_period = df_filtered[df_filtered['Year'] <= max_year].copy()

    if len(df_period) == 0:
        return None

    # Agrupar por (Year, Event) para construir edges
    edges = []
    weights_map = {'Gold': 5, 'Silver': 3, 'Bronze': 2} if weighting == '5-3-2' else {'Gold': 1, 'Silver': 1, 'Bronze': 1}

    for (year, event), group in df_period.groupby(['Year', 'Event']):
        medalists = group['Name'].unique()
        medals = group.set_index('Name')['Medal']

        # Criar arestas direcionadas entre medalhistas
        for i, athlete_from in enumerate(medalists):
            for athlete_to in medalists[i+1:]:
                # Determinar direção baseada em medalhas
                medal_from = medals[athlete_from] if athlete_from in medals.index else 'Bronze'
                medal_to = medals[athlete_to] if athlete_to in medals.index else 'Bronze'

                # Direção: medalha superior -> medalha inferior
                medal_order = {'Gold': 3, 'Silver': 2, 'Bronze': 1}
                if medal_order[medal_from] > medal_order[medal_to]:
                    edges.append((athlete_from, athlete_to, weights_map[medal_from]))
                elif medal_order[medal_to] > medal_order[medal_from]:
                    edges.append((athlete_to, athlete_from, weights_map[medal_to]))
                else:
                    # Mesma medalha: ambas direções
                    edges.append((athlete_from, athlete_to, weights_map[medal_from]))
                    edges.append((athlete_to, athlete_from, weights_map[medal_to]))

    # Criar grafo direcionado
    G = nx.DiGraph()
    for source, target, weight in edges:
        if G.has_edge(source, target):
            G[source][target]['weight'] += weight
        else:
            G.add_edge(source, target, weight=weight)

    return G

def calculate_metrics(G):
    """
    Calcula métricas estruturais de uma rede.
    """
    if G is None or G.number_of_nodes() == 0:
        return None

    # Converter para não-direcionado para algumas métricas
    G_undirected = G.to_undirected()

    metrics = {
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'avg_clustering': nx.average_clustering(G_undirected),
        'num_components': nx.number_weakly_connected_components(G),
    }

    # PageRank médio (com tratamento para grafos pequenos)
    try:
        pr = nx.pagerank(G, max_iter=100, tol=1e-4)
        metrics['avg_pagerank'] = np.mean(list(pr.values()))
    except:
        metrics['avg_pagerank'] = np.nan

    # Modularidade (se rede tem mais de 2 nós)
    try:
        if G_undirected.number_of_nodes() > 2:
            import community.community_louvain as community_louvain
            partition = community_louvain.best_partition(G_undirected)
            metrics['modularity'] = community_louvain.modularity(partition, G_undirected)
        else:
            metrics['modularity'] = np.nan
    except:
        metrics['modularity'] = np.nan

    return metrics

# ====================
# 4. ANÁLISE POR REDE
# ====================

all_results = []

for net_config in NETWORKS_CONFIG:
    print(f"\n{'='*80}")
    print(f"🔍 Analisando: {net_config['name']} ({net_config['sport']})")
    print(f"{'='*80}")

    # Filtrar dados para esta rede
    if 'Football' in net_config['event']:
        df_net = df[(df['Sport'] == 'Football') & (df['Sex'] == net_config['gender'])].copy()
    elif 'Basketball' in net_config['event']:
        df_net = df[(df['Sport'] == 'Basketball') & (df['Sex'] == net_config['gender'])].copy()
    elif 'Athletics' in net_config['event']:
        df_net = df[(df['Event'] == net_config['event'])].copy()
    elif 'Swimming' in net_config['event']:
        df_net = df[(df['Event'] == net_config['event'])].copy()
    elif 'Judo' in net_config['event']:
        df_net = df[(df['Event'] == net_config['event'])].copy()
    elif 'Boxing' in net_config['event']:
        df_net = df[(df['Event'] == net_config['event'])].copy()
    else:
        continue

    if len(df_net) == 0:
        print(f"   ⚠️  Sem dados para {net_config['name']}")
        continue

    print(f"   ✓ {len(df_net)} registros | Anos: {df_net['Year'].min()}-{df_net['Year'].max()}")

    # Calcular métricas por década
    for decade_start, decade_end in DECADES:
        # Construir rede acumulada até o final da década
        G = build_network_until_year(df_net, decade_end)

        if G is None or G.number_of_nodes() < 3:
            continue  # Pular décadas sem dados suficientes

        metrics = calculate_metrics(G)

        if metrics is not None:
            result = {
                'network_name': net_config['name'],
                'sport': net_config['sport'],
                'gender': net_config['gender'],
                'decade': f"{decade_start}s",
                'decade_end_year': decade_end,
                **metrics
            }
            all_results.append(result)

            print(f"   {decade_start}s: {metrics['nodes']} nodes, density={metrics['density']:.4f}")

# ====================
# 5. CONSOLIDAR RESULTADOS
# ====================

df_results = pd.DataFrame(all_results)

print(f"\n{'='*80}")
print(f"✓ Análise temporal concluída: {len(df_results)} pontos temporais")
print(f"{'='*80}")

# Salvar CSV
output_csv = '../results_complete_mining/data/temporal_dynamics_12networks.csv'
df_results.to_csv(output_csv, index=False)
print(f"\n✓ Salvo: {output_csv}")

# ====================
# 6. VISUALIZAÇÕES
# ====================

print(f"\n{'='*80}")
print("📊 Gerando visualizações...")
print(f"{'='*80}")

# Configurar estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

# Para cada métrica, criar gráfico de evolução temporal
metrics_to_plot = ['density', 'avg_clustering', 'avg_pagerank', 'modularity', 'nodes']
metric_labels = {
    'density': 'Densidade',
    'avg_clustering': 'Coef. Clustering Médio',
    'avg_pagerank': 'PageRank Médio',
    'modularity': 'Modularidade',
    'nodes': 'Número de Atletas'
}

for metric in metrics_to_plot:
    if metric not in df_results.columns:
        continue

    fig, axes = plt.subplots(4, 3, figsize=(18, 16))
    fig.suptitle(f'Evolução Temporal: {metric_labels[metric]} (12 Redes)', fontsize=16, fontweight='bold')

    for idx, net_config in enumerate(NETWORKS_CONFIG):
        ax = axes[idx // 3, idx % 3]

        # Filtrar dados desta rede
        df_net = df_results[df_results['network_name'] == net_config['name']].copy()

        if len(df_net) == 0:
            ax.text(0.5, 0.5, 'Sem dados', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(net_config['name'])
            continue

        # Plotar evolução
        df_net = df_net.sort_values('decade_end_year')

        color = 'blue' if net_config['gender'] == 'M' else 'red'
        ax.plot(df_net['decade_end_year'], df_net[metric], marker='o', linewidth=2, color=color, alpha=0.7)

        ax.set_title(f"{net_config['name']}", fontweight='bold')
        ax.set_xlabel('Ano')
        ax.set_ylabel(metric_labels[metric])
        ax.grid(True, alpha=0.3)

        # Rotacionar labels do eixo x
        ax.tick_params(axis='x', rotation=45)

    plt.tight_layout()

    # Salvar figura
    output_fig = f'../results_complete_mining/figures/temporal_evolution_{metric}.pdf'
    plt.savefig(output_fig, dpi=300, bbox_inches='tight')
    print(f"✓ Figura salva: {output_fig}")
    plt.close()

# ====================
# 7. IDENTIFICAR PONTOS DE MUDANÇA
# ====================

print(f"\n{'='*80}")
print("🔍 Identificando pontos de mudança estrutural...")
print(f"{'='*80}")

change_points = []

for net_config in NETWORKS_CONFIG:
    df_net = df_results[df_results['network_name'] == net_config['name']].copy()

    if len(df_net) < 3:
        continue

    df_net = df_net.sort_values('decade_end_year')

    # Calcular variação percentual em densidade
    df_net['density_change'] = df_net['density'].pct_change() * 100

    # Identificar maiores mudanças (> 50%)
    big_changes = df_net[abs(df_net['density_change']) > 50]

    for _, row in big_changes.iterrows():
        change_points.append({
            'network': net_config['name'],
            'decade': row['decade'],
            'year': row['decade_end_year'],
            'density_change_pct': row['density_change'],
            'density_new': row['density']
        })

if len(change_points) > 0:
    df_changes = pd.DataFrame(change_points)
    output_changes = '../results_complete_mining/data/structural_change_points.csv'
    df_changes.to_csv(output_changes, index=False)
    print(f"\n✓ Pontos de mudança identificados: {len(change_points)}")
    print(f"✓ Salvo: {output_changes}")

    print("\n📊 Principais mudanças estruturais:")
    for _, row in df_changes.head(10).iterrows():
        print(f"   {row['network']:25s} | {row['decade']:8s} | Δdensity: {row['density_change_pct']:+7.1f}%")
else:
    print("\n⚠️  Nenhum ponto de mudança estrutural significativo identificado")

print(f"\n{'='*80}")
print("✅ ANÁLISE TEMPORAL DINÂMICA CONCLUÍDA")
print(f"{'='*80}")
