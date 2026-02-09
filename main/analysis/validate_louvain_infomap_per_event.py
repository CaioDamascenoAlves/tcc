#!/usr/bin/env python3
"""
VALIDAÇÃO LOUVAIN vs INFOMAP - REDES PER-EVENT
================================================

REFATORADO de compare_community_metrics.py para:
1. CARREGAR redes .gexf prontas (per-event)
2. Rodar validação completa com NMI, ARI, métricas agregadas
3. Gerar relatório LaTeX para monografia

Uso:
    python validate_louvain_infomap_per_event.py --event "swimming_M_Mens_100m_Freestyle"
"""

import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
from collections import Counter
import json
import argparse
from scipy.stats import entropy
from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score

try:
    import community as community_louvain
    LOUVAIN_AVAILABLE = True
except ImportError:
    print("ERRO: python-louvain não instalado. Execute: pip install python-louvain")
    exit(1)

try:
    import igraph as ig
    INFOMAP_AVAILABLE = True
except ImportError:
    print("ERRO: igraph não instalado. Execute: pip install igraph")
    exit(1)

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================

project_root = Path(__file__).parent.parent
RESULTS_DIR = project_root / 'results_per_event_cleaned'
OUTPUT_DIR = project_root / 'analysis' / 'validation_results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

def load_network(event_name):
    """
    Carrega rede .gexf do diretório de resultados.

    Args:
        event_name: Nome do arquivo (ex: "swimming_M_Mens_100m_Freestyle")
                    ou caminho relativo (ex: "swimming/swimming_original_M_individual")

    Returns:
        NetworkX DiGraph
    """
    # Se contém '/', trata como caminho relativo
    if '/' in event_name:
        network_path = RESULTS_DIR / f"{event_name}.gexf"
    else:
        # Inferir sport do nome
        sport = event_name.split('_')[0]
        network_path = RESULTS_DIR / sport / f"{event_name}.gexf"

    if not network_path.exists():
        raise FileNotFoundError(f"Rede não encontrada: {network_path}")

    print(f"Carregando rede: {network_path}")
    G = nx.read_gexf(network_path)

    # Converter para DiGraph se necessário
    if not isinstance(G, nx.DiGraph):
        G = G.to_directed()

    return G

def run_louvain(G):
    """
    Detecta comunidades com Louvain (undirected).

    Returns:
        communities_dict, modularity, num_communities
    """
    print("\n[Louvain] Detectando comunidades (undirected)...")

    G_undirected = G.to_undirected()
    communities = community_louvain.best_partition(G_undirected, weight='weight')
    modularity = community_louvain.modularity(communities, G_undirected, weight='weight')
    num_communities = len(set(communities.values()))

    # Estatísticas
    sizes = Counter(communities.values())
    avg_size = np.mean(list(sizes.values()))

    print(f"  Comunidades: {num_communities}")
    print(f"  Modularidade: {modularity:.4f}")
    print(f"  Tamanho médio: {avg_size:.1f} nós")

    return communities, modularity, num_communities

def run_infomap(G):
    """
    Detecta comunidades com Infomap (directed via igraph).

    Returns:
        communities_dict, modularity, num_communities
    """
    print("\n[Infomap] Detectando comunidades (directed)...")

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
    result = g_ig.community_infomap(edge_weights='weight')

    # Extrair comunidades
    communities = {}
    for idx, comm_id in enumerate(result.membership):
        original_node = node_list[idx]
        communities[original_node] = comm_id

    modularity = result.modularity
    num_communities = len(set(communities.values()))

    # Estatísticas
    sizes = Counter(communities.values())
    avg_size = np.mean(list(sizes.values()))

    print(f"  Comunidades: {num_communities}")
    print(f"  Modularidade: {modularity:.4f}")
    print(f"  Tamanho médio: {avg_size:.1f} nós")

    return communities, modularity, num_communities

def compare_partitions(louvain_comms, infomap_comms):
    """
    Compara partições com NMI e ARI.

    Returns:
        dict com métricas de concordância
    """
    print("\n[Comparação] Calculando concordância estrutural...")

    # Alinhar labels
    common_nodes = set(louvain_comms.keys()) & set(infomap_comms.keys())
    louvain_labels = [louvain_comms[node] for node in common_nodes]
    infomap_labels = [infomap_comms[node] for node in common_nodes]

    # Métricas
    nmi = normalized_mutual_info_score(louvain_labels, infomap_labels)
    ari = adjusted_rand_score(louvain_labels, infomap_labels)

    # Atletas que mudaram
    num_changed = sum(1 for node in common_nodes if louvain_comms[node] != infomap_comms[node])
    pct_changed = 100 * num_changed / len(common_nodes)

    print(f"  NMI (Normalized Mutual Information): {nmi:.4f}")
    print(f"  ARI (Adjusted Rand Index): {ari:.4f}")
    print(f"  Nós que mudaram de comunidade: {num_changed}/{len(common_nodes)} ({pct_changed:.1f}%)")

    if nmi > 0.8:
        print(f"  → ALTA concordância - algoritmos convergem")
    elif nmi > 0.5:
        print(f"  → MODERADA concordância")
    else:
        print(f"  → BAIXA concordância - algoritmos divergem")

    return {
        'nmi': nmi,
        'ari': ari,
        'num_changed': num_changed,
        'pct_changed': pct_changed,
        'num_common_nodes': len(common_nodes)
    }

def analyze_communities_metrics(communities, G, algorithm_name):
    """
    Calcula métricas agregadas das comunidades.

    Returns:
        dict com estatísticas
    """
    sizes = Counter(communities.values())

    # PageRank para análise de performance
    pagerank = nx.pagerank(G, weight='weight')

    # PageRank por comunidade
    pr_by_comm = {}
    for node, comm_id in communities.items():
        if node in pagerank:
            if comm_id not in pr_by_comm:
                pr_by_comm[comm_id] = []
            pr_by_comm[comm_id].append(pagerank[node])

    # Gini de PageRank por comunidade
    gini_values = [calculate_gini(values) for values in pr_by_comm.values()]

    return {
        'algorithm': algorithm_name,
        'num_communities': len(sizes),
        'size_mean': float(np.mean(list(sizes.values()))),
        'size_std': float(np.std(list(sizes.values()))),
        'size_min': int(min(sizes.values())),
        'size_max': int(max(sizes.values())),
        'gini_pagerank_mean': float(np.mean(gini_values)) if gini_values else 0.0,
        'gini_pagerank_std': float(np.std(gini_values)) if gini_values else 0.0,
    }

def generate_latex_table(results):
    """
    Gera tabela LaTeX para incluir na monografia.
    """
    louvain_num = results['louvain']['num_communities']
    infomap_num = results['infomap']['num_communities']
    louvain_mod = results['louvain']['modularity']
    infomap_mod = results['infomap']['modularity']
    louvain_size = results['louvain']['size_mean']
    infomap_size = results['infomap']['size_mean']
    nmi = results['comparison']['nmi']
    ari = results['comparison']['ari']
    pct_changed = results['comparison']['pct_changed']

    latex = f"""\\begin{{table}}[h]
\\centering
\\caption{{Validação empírica: Louvain vs Infomap}}
\\label{{tab:louvain_infomap_validation}}
\\begin{{tabular}}{{lcc}}
\\hline
\\textbf{{Métrica}} & \\textbf{{Louvain}} & \\textbf{{Infomap}} \\\\
\\hline
Número de comunidades & {louvain_num} & {infomap_num} \\\\
Modularidade & {louvain_mod:.4f} & {infomap_mod:.4f} \\\\
Tamanho médio (nós) & {louvain_size:.1f} & {infomap_size:.1f} \\\\
\\hline
\\multicolumn{{3}}{{l}}{{\\textbf{{Concordância Estrutural}}}} \\\\
\\hline
NMI & \\multicolumn{{2}}{{c}}{{{nmi:.4f}}} \\\\
ARI & \\multicolumn{{2}}{{c}}{{{ari:.4f}}} \\\\
Nós que mudaram & \\multicolumn{{2}}{{c}}{{{pct_changed:.1f}\\%}} \\\\
\\hline
\\end{{tabular}}
\\end{{table}}
"""
    return latex

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description='Validar Louvain vs Infomap em rede per-event')
    parser.add_argument('--event', type=str,
                        default='swimming_M_Mens_100m_Freestyle',
                        help='Nome do arquivo de rede (sem .gexf)')
    args = parser.parse_args()

    print("=" * 80)
    print("VALIDAÇÃO LOUVAIN vs INFOMAP - REDES PER-EVENT")
    print("=" * 80)
    print(f"\nEvento: {args.event}")

    # ==============================================================================
    # 1. CARREGAR REDE
    # ==============================================================================

    print("\n[1/5] Carregando rede...")
    try:
        G = load_network(args.event)
    except FileNotFoundError as e:
        print(f"\nERRO: {e}")
        print("\nRedes disponíveis:")
        for sport_dir in RESULTS_DIR.iterdir():
            if sport_dir.is_dir() and sport_dir.name in ['swimming', 'athletics', 'basketball', 'football', 'judo', 'boxing']:
                print(f"\n  {sport_dir.name}/")
                for gexf_file in sport_dir.glob("*.gexf"):
                    print(f"    - {gexf_file.stem}")
        return

    print(f"  Nós: {G.number_of_nodes()}")
    print(f"  Arestas direcionadas: {G.number_of_edges()}")
    print(f"  Densidade: {nx.density(G):.4f}")

    # ==============================================================================
    # 2. LOUVAIN
    # ==============================================================================

    print("\n[2/5] Louvain (undirected)...")
    louvain_comms, louvain_mod, louvain_num = run_louvain(G)
    louvain_metrics = analyze_communities_metrics(louvain_comms, G, "Louvain")
    louvain_metrics['modularity'] = louvain_mod

    # ==============================================================================
    # 3. INFOMAP
    # ==============================================================================

    print("\n[3/5] Infomap (directed)...")
    infomap_comms, infomap_mod, infomap_num = run_infomap(G)
    infomap_metrics = analyze_communities_metrics(infomap_comms, G, "Infomap")
    infomap_metrics['modularity'] = infomap_mod

    # ==============================================================================
    # 4. COMPARAÇÃO
    # ==============================================================================

    print("\n[4/5] Comparação...")
    comparison = compare_partitions(louvain_comms, infomap_comms)

    # ==============================================================================
    # 5. EXPORTAR RESULTADOS
    # ==============================================================================

    print("\n[5/5] Exportando resultados...")

    # Estrutura completa de resultados
    results = {
        'event': args.event,
        'network': {
            'nodes': G.number_of_nodes(),
            'edges': G.number_of_edges(),
            'density': float(nx.density(G))
        },
        'louvain': louvain_metrics,
        'infomap': infomap_metrics,
        'comparison': comparison
    }

    # Salvar JSON (sanitizar nome do arquivo)
    safe_event_name = args.event.replace('/', '_')
    json_path = OUTPUT_DIR / f'validation_{safe_event_name}.json'
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  [OK] {json_path}")

    # Gerar tabela LaTeX
    latex_table = generate_latex_table(results)
    latex_path = OUTPUT_DIR / f'validation_{safe_event_name}_table.tex'
    with open(latex_path, 'w') as f:
        f.write(latex_table)
    print(f"  [OK] {latex_path}")

    # ==============================================================================
    # CONCLUSÃO
    # ==============================================================================

    print("\n" + "=" * 80)
    print("CONCLUSÃO")
    print("=" * 80)

    print(f"\nLouvain: {louvain_num} comunidades (Q = {louvain_mod:.4f})")
    print(f"Infomap: {infomap_num} comunidades (Q = {infomap_mod:.4f})")
    print(f"\nConcordância: NMI = {comparison['nmi']:.4f}, ARI = {comparison['ari']:.4f}")

    if comparison['nmi'] > 0.8:
        print("\n✅ RESULTADO: Algoritmos CONVERGEM")
        print("   → Estrutura comunitária robusta independente de direção")
        print("   → Louvain (undirected) captura adequadamente agrupamentos")
        print("   → JUSTIFICA uso de Louvain com simetrização na monografia")
    elif comparison['nmi'] > 0.5:
        print("\n⚠️  RESULTADO: Concordância MODERADA")
        print("   → Infomap revela nuances não capturadas por Louvain")
        print("   → Considerar reportar AMBAS as abordagens")
    else:
        print("\n❌ RESULTADO: Algoritmos DIVERGEM")
        print("   → Direção é CRÍTICA para estrutura comunitária")
        print("   → RECONSIDERAR uso exclusivo de Louvain")

    print("\n" + "=" * 80)
    print(f"\nArquivos gerados:")
    print(f"  - {json_path}")
    print(f"  - {latex_path}")
    print("\nPróximo passo: Copiar tabela LaTeX para monografia/textuais/desenvolvimento.tex")
    print("=" * 80)

if __name__ == '__main__':
    main()
