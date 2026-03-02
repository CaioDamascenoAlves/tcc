#!/usr/bin/env python3
"""
Calcula e plota rivalidades inter-comunidade apenas das 12 redes de estudo.
Roda Louvain em cada rede, conta arestas entre comunidades distintas,
e gera fig_top10_rivalries.png com legendas em português.
"""

import sys
import random
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from collections import defaultdict

try:
    import community as community_louvain
except ImportError:
    print("Instale python-louvain: pip install python-louvain")
    sys.exit(1)

random.seed(42)
np.random.seed(42)

BASE = Path(__file__).parent

# ---------------------------------------------------------------------------
# 12 casos de estudo: (rótulo_pt, caminho_gexf, cor)
# ---------------------------------------------------------------------------
CASES = [
    # Futebol
    ("Futebol M",     BASE / "results/football/football_M_Football_Mens_Football.gexf",                        "#1f77b4"),
    ("Futebol F",     BASE / "results/football/football_F_Football_Womens_Football.gexf",                      "#aec7e8"),
    # Basquete
    ("Basquete M",    BASE / "results/basketball/basketball_M_Basketball_Mens_Basketball.gexf",                 "#ff7f0e"),
    ("Basquete F",    BASE / "results/basketball/basketball_F_Basketball_Womens_Basketball.gexf",               "#ffbb78"),
    # Atletismo 100m
    ("Atletismo 100m M", BASE / "results_per_event_cleaned/athletics/athletics_M_100m.gexf",                   "#2ca02c"),
    ("Atletismo 100m F", BASE / "results_per_event_cleaned/athletics/athletics_F_100m.gexf",                   "#98df8a"),
    # Natação 100m Livre
    ("Natação 100m M",   BASE / "results_per_event_cleaned/swimming/swimming_M_100m_Freestyle.gexf",           "#d62728"),
    ("Natação 100m F",   BASE / "results_per_event_cleaned/swimming/swimming_F_100m_Freestyle.gexf",           "#ff9896"),
    # Judô
    ("Judô -90kg M",     BASE / "results_per_event_cleaned/judo/judo_M_-90kg.gexf",                           "#9467bd"),
    ("Judô -70kg F",     BASE / "results_per_event_cleaned/judo/judo_F_-70kg.gexf",                           "#c5b0d5"),
    # Boxe
    ("Boxe Welter M",    BASE / "results_per_event_cleaned/boxing/boxing_M_Welter_63-69kg.gexf",               "#8c564b"),
    ("Boxe Médio F",     BASE / "results_per_event_cleaned/boxing/boxing_F_Middle_69-75kg.gexf",               "#c49c94"),
]

# ---------------------------------------------------------------------------
# Para cada rede: carrega, detecta comunidades, conta arestas inter-comunidade
# ---------------------------------------------------------------------------
results = []   # (label, cor, num_pares, confrontos_total, top_par, top_count)

for label, gexf_path, cor in CASES:
    if not gexf_path.exists():
        print(f"[AVISO] Arquivo não encontrado: {gexf_path}")
        continue

    G = nx.read_gexf(str(gexf_path))
    print(f"\n{label}: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")

    # Louvain precisa de grafo não-dirigido e ponderado
    G_sym = G.to_undirected()
    # garantir peso nas arestas
    for u, v, d in G_sym.edges(data=True):
        if 'weight' not in d:
            d['weight'] = 1.0

    partition = community_louvain.best_partition(G_sym, random_state=42)
    n_communities = len(set(partition.values()))
    print(f"  Comunidades detectadas: {n_communities}")

    # Contar arestas inter-comunidade (direcionado original)
    inter_counts = defaultdict(int)
    total_inter = 0
    for u, v in G.edges():
        cu = partition.get(u, -1)
        cv = partition.get(v, -1)
        if cu != cv:
            inter_counts[(cu, cv)] += 1
            total_inter += 1

    if not inter_counts:
        print(f"  Sem arestas inter-comunidade")
        results.append((label, cor, 0, 0, None, 0))
        continue

    top_pair = max(inter_counts, key=inter_counts.get)
    top_count = inter_counts[top_pair]
    print(f"  Total inter-comunidade: {total_inter}")
    print(f"  Par mais intenso: C{top_pair[0]}→C{top_pair[1]} = {top_count}")

    results.append((label, cor, len(inter_counts), total_inter, top_pair, top_count))

# ---------------------------------------------------------------------------
# Ordenar pelo total de confrontos inter-comunidade (decrescente)
# ---------------------------------------------------------------------------
results.sort(key=lambda x: x[3], reverse=True)

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
labels   = [r[0] for r in results]
totais   = [r[3] for r in results]
cores    = [r[1] for r in results]

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.barh(range(len(labels)), totais, color=cores, edgecolor='white', height=0.7)

# Rótulos de valor nas barras
for i, (bar, val) in enumerate(zip(bars, totais)):
    ax.text(bar.get_width() + max(totais)*0.01, bar.get_y() + bar.get_height()/2,
            f'{val:,}'.replace(',', '.'),
            va='center', ha='left', fontsize=9, color='#333333')

ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels, fontsize=10)
ax.invert_yaxis()
ax.set_xlabel('Total de confrontos inter-comunidade', fontsize=11)
ax.set_title('Top Rivalidades Estruturais entre Comunidades\n(12 Redes de Estudo)', fontsize=13, fontweight='bold')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(axis='x', labelsize=9)

# Ajustar limite x para caber rótulos
ax.set_xlim(0, max(totais) * 1.18)

plt.tight_layout()

out = Path("/home/caio/Desktop/tcc/monografia/figuras/fig_top10_rivalries.png")
fig.savefig(str(out), dpi=150, bbox_inches='tight')
print(f"\nFigura salva em: {out}")

# ---------------------------------------------------------------------------
# CSV corrigido (top par por rede)
# ---------------------------------------------------------------------------
import csv
csv_out = BASE / "results_v2_individual_team/additional_analyses/top_rivalry_pairs_12redes.csv"
with open(csv_out, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['modalidade', 'total_inter', 'top_par', 'top_par_confrontos'])
    for r in results:
        label, cor, n_pares, total, top_pair, top_count = r
        par_str = f"C{top_pair[0]}→C{top_pair[1]}" if top_pair else "—"
        w.writerow([label, total, par_str, top_count])

print(f"CSV salvo em: {csv_out}")

# Imprimir resumo para atualizar slides/tabela
print("\n=== RESUMO PARA APRESENTAÇÃO ===")
for r in results:
    label, cor, n_pares, total, top_pair, top_count = r
    par_str = f"C{top_pair[0]}→C{top_pair[1]}: {top_count}" if top_pair else "sem inter"
    print(f"{label:20s}  total={total:5d}  top_par={par_str}")
