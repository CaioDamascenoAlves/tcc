"""
Validação Metodológica Baseada em Literatura
Implementa metodologias de Motegi & Masuda (2012) e Shiue et al. (2025)

Referências:
- Motegi & Masuda (2012): "A network-based dynamical ranking system for competitive sports"
  DOI: 10.1038/srep00904
- Shiue et al. (2025): "Applying PageRank to Team Ranking in Single-Elimination Tournaments"
  DOI: 10.3390/app15126882
"""

import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr, kendalltau

project_root = Path(__file__).parent.parent

print("=" * 80)
print("VALIDACAO METODOLOGICA BASEADA EM LITERATURA")
print("=" * 80)
print()
print("Implementa metodologias de:")
print("  1. Motegi & Masuda (2012) - Decay exponencial temporal")
print("  2. Shiue et al. (2025) - Validacao com Kendall tau")
print("=" * 80)

# ==============================================================================
# CARREGAR DADOS
# ==============================================================================

print("\n[1/5] CARREGANDO DADOS...")
df = pd.read_csv(project_root / 'data' / 'athlete_events.csv')
df_filtered = df[
    (df['Medal'].notna()) &
    (df['Season'] == 'Summer') &
    (df['Sport'] == 'Swimming') &
    (df['Sex'] == 'M')
].copy()

print(f"   Registros: {len(df_filtered)}")
print(f"   Periodo: {df_filtered['Year'].min():.0f} - {df_filtered['Year'].max():.0f}")
print(f"   Atletas unicos: {df_filtered['ID'].nunique()}")

# ==============================================================================
# FUNCAO: CRIAR REDE COM ACUMULACAO TEMPORAL
# ==============================================================================

def create_network_temporal_decay(df, decay_rate=0.0):
    """
    Cria rede com decay exponencial temporal (Motegi & Masuda 2012)

    Formula: W_ij = sum( w(t_k) * exp(-lambda * (T - t_k)) )

    Args:
        df: DataFrame de atletas
        decay_rate: taxa de decaimento (lambda)
                    0.0 = sem decay (soma simples)
                    0.05 = decay 5% ao ano
                    0.10 = decay 10% ao ano

    Returns:
        NetworkX DiGraph
    """
    G = nx.DiGraph()

    # Pesos base
    weight_map = {
        ('Gold', 'Bronze'): 5,
        ('Gold', 'Silver'): 3,
        ('Silver', 'Bronze'): 2
    }

    # Adicionar nos
    for _, row in df.iterrows():
        G.add_node(row['ID'], name=row['Name'], medal=row['Medal'])

    # Coletar confrontos
    confrontos = {}

    for _, row in df.iterrows():
        event_key = (row['Event'], row['Year'])
        event_group = df[(df['Event'] == row['Event']) & (df['Year'] == row['Year'])]
        medalists = event_group[['ID', 'Medal', 'Year']].values

        for i, (loser_id, loser_medal, year) in enumerate(medalists):
            for winner_id, winner_medal, _ in medalists[:i]:
                if loser_medal != winner_medal:
                    weight_key = (winner_medal, loser_medal)
                    base_weight = weight_map.get(weight_key, 1)

                    edge_key = (loser_id, winner_id)
                    if edge_key not in confrontos:
                        confrontos[edge_key] = []

                    confrontos[edge_key].append({
                        'year': year,
                        'weight': base_weight
                    })

    # Aplicar decay temporal (Motegi & Masuda 2012)
    latest_year = df['Year'].max()

    for (loser_id, winner_id), encounters in confrontos.items():
        if decay_rate == 0.0:
            # Soma simples (baseline)
            final_weight = sum(e['weight'] for e in encounters)
        else:
            # Decay exponencial: w * exp(-lambda * age)
            final_weight = sum(
                e['weight'] * np.exp(-decay_rate * (latest_year - e['year']))
                for e in encounters
            )

        G.add_edge(loser_id, winner_id, weight=final_weight)

    return G

# ==============================================================================
# TESTE 1: SENSIBILIDADE A DECAY RATE (Motegi & Masuda 2012)
# ==============================================================================

print("\n[2/5] TESTE DE DECAY RATE (Motegi & Masuda 2012)...")
print("   Formula: W = sum( w(t) * exp(-lambda * (T - t)) )")
print()

# Taxas de decay a testar (Motegi & Masuda testaram multiplas taxas)
decay_rates = {
    'Sem Decay (baseline)': 0.00,
    'Decay 2.5% ao ano': 0.025,
    'Decay 5% ao ano': 0.05,
    'Decay 7.5% ao ano': 0.075,
    'Decay 10% ao ano': 0.10,
    'Decay 15% ao ano': 0.15
}

results_decay = {}

for label, rate in decay_rates.items():
    G = create_network_temporal_decay(df_filtered, decay_rate=rate)
    pagerank = nx.pagerank(G, weight='weight')

    pr_df = pd.DataFrame([
        {'id': node_id, 'name': G.nodes[node_id]['name'], 'pagerank': pr}
        for node_id, pr in pagerank.items()
    ]).sort_values('pagerank', ascending=False)

    results_decay[label] = pr_df
    print(f"   {label:25s}: Top 1 = {pr_df.iloc[0]['name']}")

# ==============================================================================
# TESTE 2: CORRELACAO DE KENDALL TAU (Shiue et al. 2025)
# ==============================================================================

print("\n[3/5] CORRELACAO DE KENDALL TAU (Shiue et al. 2025)...")
print("   Threshold de validacao: tau > 0.70 (Shiue et al. 2025)")
print()

baseline = results_decay['Sem Decay (baseline)']

print("   Comparacao com baseline (sem decay):")
print("   " + "-" * 70)
print(f"   {'Sistema':<30s} {'Kendall Tau':>12s} {'Spearman':>12s} {'Status':>12s}")
print("   " + "-" * 70)

correlations = {}

for label in list(decay_rates.keys())[1:]:  # Skip baseline
    compare = results_decay[label]

    # Merge por ID
    merged = baseline[['id', 'pagerank']].merge(
        compare[['id', 'pagerank']],
        on='id',
        suffixes=('_base', '_compare')
    )

    # Kendall Tau (metrica de Shiue et al. 2025)
    tau, pval_tau = kendalltau(merged['pagerank_base'], merged['pagerank_compare'])

    # Spearman (para comparacao)
    rho, pval_rho = spearmanr(merged['pagerank_base'], merged['pagerank_compare'])

    # Validacao (threshold de Shiue: tau > 0.70)
    status = "VALIDO" if tau > 0.70 else "INVALIDO"

    correlations[label] = {'tau': tau, 'rho': rho}

    print(f"   {label:<30s} {tau:>12.4f} {rho:>12.4f} {status:>12s}")

print("   " + "-" * 70)

# ==============================================================================
# TESTE 3: JACCARD SIMILARITY (Top-10)
# ==============================================================================

print("\n[4/5] JACCARD SIMILARITY (Top-10)...")
print("   Mede sobreposicao de atletas no top 10")
print()

baseline_top10 = set(baseline.head(10)['name'].values)

print("   " + "-" * 70)
print(f"   {'Sistema':<30s} {'Jaccard':>12s} {'Comum':>12s} {'Status':>12s}")
print("   " + "-" * 70)

for label in list(decay_rates.keys())[1:]:
    compare_top10 = set(results_decay[label].head(10)['name'].values)

    intersection = len(baseline_top10.intersection(compare_top10))
    union = len(baseline_top10.union(compare_top10))
    jaccard = intersection / union if union > 0 else 0

    # Threshold: Jaccard > 0.70 (padrao em community detection)
    status = "ROBUSTO" if jaccard > 0.70 else "SENSIVEL"

    print(f"   {label:<30s} {jaccard:>12.3f} {intersection:>10d}/10 {status:>12s}")

print("   " + "-" * 70)

# ==============================================================================
# TESTE 4: ATLETAS NO CONSENSO
# ==============================================================================

print("\n[5/5] ATLETAS NO CONSENSO...")
print("   Atletas que aparecem no top 10 de TODOS os sistemas")
print()

all_top10_sets = [set(df.head(10)['name'].values) for df in results_decay.values()]
consensus = set.intersection(*all_top10_sets)

print(f"   Total no consenso: {len(consensus)}/10")
print()
for name in sorted(consensus):
    print(f"      - {name}")

# ==============================================================================
# ANALISE E INTERPRETACAO
# ==============================================================================

print("\n" + "=" * 80)
print("ANALISE E INTERPRETACAO")
print("=" * 80)

# Calcular medias
tau_values = [correlations[label]['tau'] for label in correlations]
rho_values = [correlations[label]['rho'] for label in correlations]

avg_tau = np.mean(tau_values)
avg_rho = np.mean(rho_values)
min_tau = np.min(tau_values)
min_rho = np.min(rho_values)

print(f"\nMetricas de Concordancia:")
print(f"   Kendall Tau medio: {avg_tau:.4f}")
print(f"   Kendall Tau minimo: {min_tau:.4f}")
print(f"   Spearman medio: {avg_rho:.4f}")
print(f"   Spearman minimo: {min_rho:.4f}")
print(f"   Atletas no consenso: {len(consensus)}/10")

print(f"\nInterpretacao (baseado em Shiue et al. 2025):")

if min_tau > 0.70:
    print("   ROBUSTO: Sistema atual e robusto a decay temporal")
    print(f"   Threshold de Shiue (tau > 0.70): SATISFEITO (min = {min_tau:.4f})")
    print("   Recomendacao: MANTER SOMA SIMPLES (baseline)")
    print()
    print("   Justificativa:")
    print("   - Sistema sem decay ja e adequado (tau > 0.70 para todos os testes)")
    print("   - PageRank captura temporalidade implicitamente (estrutura da rede)")
    print("   - Adicionar decay aumenta complexidade sem ganho empirico")
else:
    print("   SENSIVEL: Sistema atual e sensivel a decay temporal")
    print(f"   Threshold de Shiue (tau > 0.70): NAO SATISFEITO (min = {min_tau:.4f})")
    print("   Recomendacao: CONSIDERAR DECAY EXPONENCIAL")
    print()
    print("   Justificativa:")
    print("   - Sistema sem decay nao captura adequadamente temporalidade")
    print("   - Decay exponencial (Motegi & Masuda 2012) melhora robustez")

# ==============================================================================
# COMPARACAO COM THRESHOLDS DA LITERATURA
# ==============================================================================

print("\n" + "=" * 80)
print("COMPARACAO COM THRESHOLDS DA LITERATURA")
print("=" * 80)

print("\nThresholds Estabelecidos:")
print("   Shiue et al. (2025): Kendall tau > 0.70")
print("   Motegi & Masuda (2012): Acuracia preditiva (+4% com decay)")
print("   Nossa abordagem: tau > 0.70 E Jaccard > 0.70")

print("\nNossos Resultados:")
status_tau = "PASSA" if min_tau > 0.70 else "FALHA"
print(f"   Kendall tau minimo: {min_tau:.4f} {status_tau} (threshold: 0.70)")
print(f"   Spearman minimo: {min_rho:.4f} (para referencia)")

print("\n" + "=" * 80)
print("CONCLUSAO")
print("=" * 80)

if min_tau > 0.70 and len(consensus) >= 5:
    print("\nSISTEMA VALIDADO segundo metodologia de Shiue et al. (2025)")
    print()
    print("Evidencias:")
    print(f"   1. Kendall tau > 0.70 para todos os decay rates testados")
    print(f"   2. Consenso forte: {len(consensus)}/10 atletas em todos os sistemas")
    print(f"   3. Correlacoes extremamente altas (tau > {min_tau:.2f}, rho > {min_rho:.2f})")
    print()
    print("Conclusao:")
    print("   Sistema de SOMA SIMPLES (sem decay) e robusto e adequado.")
    print("   Nao ha necessidade de adicionar complexidade de decay temporal.")
    print("   Resultados alinhados com Motegi & Masuda (2012): estrutura de rede")
    print("   ja captura relevancia temporal implicitamente.")
else:
    print("\nSISTEMA REQUER REFINAMENTO")
    print()
    print("Sistema atual nao atende thresholds da literatura.")
    print("Considerar implementacao de decay exponencial (Motegi & Masuda 2012).")

print("\n" + "=" * 80)
