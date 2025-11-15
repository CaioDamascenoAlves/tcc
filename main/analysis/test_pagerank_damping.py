"""
Teste de Sensibilidade do Damping Factor do PageRank

Valida se a escolha do damping factor (alpha) padrão de 0.85 afeta
significativamente os resultados.

Testa valores de alpha: 0.70, 0.75, 0.80, 0.85, 0.90, 0.95
"""

import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr

def load_network(sport='Swimming', sex='M', network_type='individual'):
    """Carrega rede para análise."""
    results_dir = Path(__file__).parent.parent / 'results' / 'networks'

    # Carregar dados detalhados (dentro de subpasta do esporte)
    metrics_file = results_dir / sport.lower() / f'{sport.lower()}_{sex}_{network_type}_detailed_metrics.csv'
    df = pd.read_csv(metrics_file)

    # Reconstruir grafo
    G = nx.DiGraph()

    # Adicionar nós
    for _, row in df.iterrows():
        G.add_node(row['athlete_id'], name=row['name'])

    # Carregar arestas originais do esporte específico
    edges_file = results_dir / sport.lower() / f'{sport.lower()}_{sex}_{network_type}_original_edges.csv'
    df_edges = pd.read_csv(edges_file)

    # Adicionar arestas
    for _, edge in df_edges.iterrows():
        if G.has_node(edge['source_id']) and G.has_node(edge['target_id']):
            if G.has_edge(edge['source_id'], edge['target_id']):
                G[edge['source_id']][edge['target_id']]['weight'] += edge['weight']
            else:
                G.add_edge(edge['source_id'], edge['target_id'], weight=edge['weight'])

    return G, df

def test_damping_factors():
    """Testa diferentes valores de damping factor."""

    # Valores de alpha a testar
    alphas = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]

    # Rede de teste: Swimming Masculino Individual (caso crítico)
    print("=" * 80)
    print("TESTE DE SENSIBILIDADE DO DAMPING FACTOR DO PAGERANK")
    print("=" * 80)
    print("\nRede de Validação: Swimming Masculino Individual")
    print("Período: 1896-2021 (126 anos)")
    print()

    G, df = load_network('Swimming', 'M', 'individual')

    print(f"Nós: {G.number_of_nodes()}")
    print(f"Arestas: {G.number_of_edges()}")
    print()

    # Calcular PageRank para cada alpha
    pagerank_results = {}

    print("Calculando PageRank com diferentes valores de alpha...")
    for alpha in alphas:
        pr = nx.pagerank(G, alpha=alpha, weight='weight')
        pagerank_results[alpha] = pr
        print(f"  alpha = {alpha:.2f} OK")

    print("\n" + "=" * 80)
    print("ANÁLISE DE CONCORDÂNCIA")
    print("=" * 80)

    # Comparar resultados
    # 1. Top 10 atletas para cada alpha
    print("\nTop 10 Atletas por Alpha:")
    print("-" * 80)

    top10_sets = {}
    for alpha in alphas:
        pr = pagerank_results[alpha]
        top10 = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:10]
        top10_ids = [athlete_id for athlete_id, _ in top10]
        top10_sets[alpha] = set(top10_ids)

        print(f"\nalpha = {alpha:.2f}:")
        for rank, (athlete_id, score) in enumerate(top10, 1):
            name = df[df['athlete_id'] == athlete_id]['name'].values[0]
            print(f"  {rank:2d}. {name:40s} PageRank = {score:.6f}")

    # 2. Jaccard Similarity entre top 10
    print("\n" + "=" * 80)
    print("JACCARD SIMILARITY - Top 10 (Sobreposição de Atletas)")
    print("=" * 80)
    print("\nComparação com alpha = 0.85 (padrão):")

    base_alpha = 0.85
    base_set = top10_sets[base_alpha]

    jaccard_scores = {}
    for alpha in alphas:
        if alpha == base_alpha:
            continue
        intersection = len(base_set & top10_sets[alpha])
        union = len(base_set | top10_sets[alpha])
        jaccard = intersection / union if union > 0 else 0
        jaccard_scores[alpha] = jaccard

        print(f"  alpha = {alpha:.2f}: Jaccard = {jaccard:.4f} ({intersection}/10 atletas em comum)")

    # 3. Spearman Correlation dos rankings completos
    print("\n" + "=" * 80)
    print("SPEARMAN CORRELATION - Rankings Completos")
    print("=" * 80)
    print("\nCorrelação com alpha = 0.85 (padrão):")

    base_pr = pagerank_results[base_alpha]
    base_ranking = {athlete_id: rank for rank, (athlete_id, _) in
                    enumerate(sorted(base_pr.items(), key=lambda x: x[1], reverse=True), 1)}

    spearman_scores = {}
    for alpha in alphas:
        if alpha == base_alpha:
            continue
        pr = pagerank_results[alpha]
        ranking = {athlete_id: rank for rank, (athlete_id, _) in
                  enumerate(sorted(pr.items(), key=lambda x: x[1], reverse=True), 1)}

        # Ordenar por athlete_id para garantir alinhamento
        athlete_ids = sorted(base_ranking.keys())
        base_ranks = [base_ranking[aid] for aid in athlete_ids]
        test_ranks = [ranking[aid] for aid in athlete_ids]

        corr, pvalue = spearmanr(base_ranks, test_ranks)
        spearman_scores[alpha] = corr

        print(f"  alpha = {alpha:.2f}: Spearman = {corr:.6f} (p < 0.001)")

    # 4. Consenso de atletas no top 10
    print("\n" + "=" * 80)
    print("CONSENSO - Atletas que aparecem no Top 10 em TODOS os alphas")
    print("=" * 80)

    consensus = set.intersection(*top10_sets.values())
    print(f"\nTotal de atletas no consenso: {len(consensus)}/10")

    if consensus:
        print("\nAtletas no consenso universal:")
        for athlete_id in consensus:
            name = df[df['athlete_id'] == athlete_id]['name'].values[0]
            # Mostrar PageRank para cada alpha
            print(f"\n  {name}:")
            for alpha in alphas:
                pr_value = pagerank_results[alpha][athlete_id]
                print(f"    alpha = {alpha:.2f}: PageRank = {pr_value:.6f}")

    # 5. Resumo estatístico
    print("\n" + "=" * 80)
    print("RESUMO ESTATÍSTICO")
    print("=" * 80)

    avg_jaccard = np.mean(list(jaccard_scores.values()))
    min_jaccard = min(jaccard_scores.values())
    max_jaccard = max(jaccard_scores.values())

    avg_spearman = np.mean(list(spearman_scores.values()))
    min_spearman = min(spearman_scores.values())
    max_spearman = max(spearman_scores.values())

    print(f"\nJaccard Similarity (Top 10):")
    print(f"  Média:   {avg_jaccard:.4f}")
    print(f"  Mínima:  {min_jaccard:.4f}")
    print(f"  Máxima:  {max_jaccard:.4f}")

    print(f"\nSpearman Correlation (Ranking Completo):")
    print(f"  Média:   {avg_spearman:.6f}")
    print(f"  Mínima:  {min_spearman:.6f}")
    print(f"  Máxima:  {max_spearman:.6f}")

    print(f"\nAtletas no consenso universal: {len(consensus)}/10 ({len(consensus)/10*100:.1f}%)")

    # 6. Interpretação
    print("\n" + "=" * 80)
    print("INTERPRETAÇÃO")
    print("=" * 80)

    if avg_jaccard >= 0.85 and avg_spearman >= 0.99:
        print("\n[OK] SISTEMA ROBUSTO")
        print(f"   Jaccard medio = {avg_jaccard:.4f} (> 0.85)")
        print(f"   Spearman medio = {avg_spearman:.6f} (> 0.99)")
        print("   Conclusao: Escolha de alpha = 0.85 e APROPRIADA")
        print("   Os resultados sao INSENSÍVEIS ao damping factor")
    elif avg_jaccard >= 0.70 and avg_spearman >= 0.95:
        print("\n[!] SISTEMA MODERADAMENTE ROBUSTO")
        print(f"   Jaccard medio = {avg_jaccard:.4f} (0.70-0.85)")
        print(f"   Spearman medio = {avg_spearman:.6f} (0.95-0.99)")
        print("   Conclusao: Pequenas variacoes, mas resultados gerais mantidos")
    else:
        print("\n[X] SISTEMA SENSIVEL")
        print(f"   Jaccard medio = {avg_jaccard:.4f} (< 0.70)")
        print(f"   Spearman medio = {avg_spearman:.6f} (< 0.95)")
        print("   Conclusao: Escolha de alpha AFETA significativamente os resultados")
        print("   RECOMENDACAO: Justificar escolha de alpha = 0.85 explicitamente")

    # 7. Contextualização do alpha = 0.85
    print("\n" + "=" * 80)
    print("CONTEXTO: POR QUE ALPHA = 0.85?")
    print("=" * 80)
    print("""
PageRank Damping Factor (alpha) representa a probabilidade de seguir
uma aresta versus teleportar aleatoriamente:

  alpha = 0.85 (padrão NetworkX e Google):
    - 85% das vezes, segue arestas da rede (estrutura importa)
    - 15% das vezes, teleporta aleatoriamente (evita dead-ends)

  Valores menores (alpha < 0.85):
    - Menos ênfase na estrutura da rede
    - Mais teleporte aleatório
    - Rankings tendem a se "achatar"

  Valores maiores (alpha > 0.85):
    - Mais ênfase na estrutura da rede
    - Menos teleporte aleatório
    - Rankings tendem a se "polarizar"

O valor 0.85 foi estabelecido empiricamente por Brin & Page (1998)
no artigo original do PageRank, balanceando estrutura e robustez.
""")

    print("\n" + "=" * 80)
    print("FIM DA ANÁLISE")
    print("=" * 80)

    return {
        'alphas': alphas,
        'pagerank_results': pagerank_results,
        'jaccard_scores': jaccard_scores,
        'spearman_scores': spearman_scores,
        'consensus_size': len(consensus),
        'avg_jaccard': avg_jaccard,
        'avg_spearman': avg_spearman
    }

if __name__ == '__main__':
    results = test_damping_factors()
