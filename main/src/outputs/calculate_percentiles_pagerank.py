#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cálculo de Percentis Intra-Rede para PageRank

Converte PageRank absoluto em percentis intra-rede (0-100), permitindo
comparações válidas cross-network de posição relativa dos atletas.

Percentil = (rank / network_size) * 100
onde rank=1 é o MENOR PageRank (posição mais baixa)

Percentil 99+ = Top 1% da rede
Percentil 95+ = Top 5% da rede
Percentil 90+ = Top 10% da rede
"""

import pandas as pd
import numpy as np
import os
from scipy.stats import rankdata

def calculate_percentiles_for_network(df, sport, sex, event_type=None):
    """
    Calcula percentis de PageRank para uma rede específica.

    Args:
        df: DataFrame com dados dos atletas
        sport: Modalidade esportiva
        sex: Gênero (M/F)
        event_type: Tipo de evento (individual/team) ou None

    Returns:
        DataFrame com athlete_id, pagerank, percentile, rank
    """
    # Filtrar rede
    if event_type:
        net_df = df[(df['sport'] == sport) &
                   (df['sex'] == sex) &
                   (df['event_type'] == event_type)].copy()
        network_label = f"{sport}_{sex}_{event_type}"
    else:
        net_df = df[(df['sport'] == sport) & (df['sex'] == sex)].copy()
        network_label = f"{sport}_{sex}"

    if len(net_df) == 0:
        return pd.DataFrame()

    # Calcular ranks (1 = menor PageRank, n = maior PageRank)
    # method='average' para lidar com empates
    net_df['pagerank_rank'] = rankdata(net_df['original_pagerank'], method='average')

    # Calcular percentil: (rank / n) * 100
    n = len(net_df)
    net_df['pagerank_percentile'] = (net_df['pagerank_rank'] / n) * 100

    # Adicionar metadados
    net_df['network_label'] = network_label
    net_df['network_size'] = n

    # Classificar por elite tiers
    net_df['elite_tier'] = pd.cut(
        net_df['pagerank_percentile'],
        bins=[0, 50, 90, 95, 99, 100],
        labels=['bottom_50', 'top_50', 'top_10', 'top_5', 'top_1']
    )

    return net_df[[
        'athlete_id', 'name', 'noc', 'sport', 'sex', 'event_type',
        'network_label', 'network_size',
        'original_pagerank', 'pagerank_rank', 'pagerank_percentile', 'elite_tier'
    ]]

def main():
    """Calcula percentis para todos os 9,350 atletas nas 16 redes."""

    print("=" * 80)
    print("CÁLCULO DE PERCENTIS INTRA-REDE - PAGERANK")
    print("=" * 80)

    # Carregar dados
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, "..", "..", "..")
    results_dir = os.path.join(project_root, "results")
    athletes_file = os.path.join(results_dir, 'consolidated_sports_network_analysis.csv')

    print(f"\nCarregando dados de: {athletes_file}")
    df = pd.read_csv(athletes_file)
    print(f"✓ Carregados {len(df)} atletas")

    all_percentiles = []

    # Processar esportes mistos (Swimming, Athletics)
    print("\n" + "=" * 80)
    print("PROCESSANDO REDES MISTAS (Swimming, Athletics)")
    print("=" * 80)

    for sport in ['Swimming', 'Athletics']:
        for event_type in ['individual', 'team']:
            for sex in ['M', 'F']:
                print(f"\nProcessando: {sport} {event_type} {sex}")
                percentiles_df = calculate_percentiles_for_network(df, sport, sex, event_type)

                if len(percentiles_df) > 0:
                    all_percentiles.append(percentiles_df)

                    # Mostrar top 3
                    top3 = percentiles_df.nlargest(3, 'pagerank_percentile')
                    print(f"  Top 3:")
                    for _, athlete in top3.iterrows():
                        print(f"    {athlete['name']:30} | Percentil: {athlete['pagerank_percentile']:.2f} | PR: {athlete['original_pagerank']:.6f}")

    # Processar esportes puros (Basketball, Football, Judo, Boxing)
    print("\n" + "=" * 80)
    print("PROCESSANDO ESPORTES PUROS")
    print("=" * 80)

    for sport in ['Basketball', 'Football', 'Judo', 'Boxing']:
        for sex in ['M', 'F']:
            print(f"\nProcessando: {sport} {sex}")
            percentiles_df = calculate_percentiles_for_network(df, sport, sex)

            if len(percentiles_df) > 0:
                all_percentiles.append(percentiles_df)

                # Mostrar top 3
                top3 = percentiles_df.nlargest(3, 'pagerank_percentile')
                print(f"  Top 3:")
                for _, athlete in top3.iterrows():
                    print(f"    {athlete['name']:30} | Percentil: {athlete['pagerank_percentile']:.2f} | PR: {athlete['original_pagerank']:.6f}")

    # Consolidar resultados
    print("\n" + "=" * 80)
    print("CONSOLIDANDO RESULTADOS")
    print("=" * 80)

    percentiles_full = pd.concat(all_percentiles, ignore_index=True)

    # Exportar arquivo completo
    output_full = os.path.join(results_dir, 'pagerank_percentiles_all_athletes.csv')
    percentiles_full.to_csv(output_full, index=False)
    print(f"\n[OK] Percentis de todos os atletas salvos: {output_full}")
    print(f"    Total: {len(percentiles_full)} atletas")

    # Criar ranking cross-network por percentil (Top 100)
    print("\n" + "=" * 80)
    print("TOP 100 ATLETAS CROSS-NETWORK (por percentil intra-rede)")
    print("=" * 80)

    top100 = percentiles_full.nlargest(100, 'pagerank_percentile')
    output_top100 = os.path.join(results_dir, 'pagerank_top100_by_percentile.csv')
    top100.to_csv(output_top100, index=False)
    print(f"\n[OK] Top 100 cross-network salvo: {output_top100}")

    # Mostrar top 20
    print("\nTOP 20 ATLETAS (cross-network):")
    print("-" * 100)
    print(f"{'Rank':>4} | {'Nome':30} | {'Esporte':15} | {'Rede':25} | {'Percentil':>10} | {'PageRank':>10}")
    print("-" * 100)

    for i, (_, athlete) in enumerate(top100.head(20).iterrows(), 1):
        print(f"{i:4} | {athlete['name']:30} | {athlete['sport']:15} | {athlete['network_label']:25} | "
              f"{athlete['pagerank_percentile']:10.2f} | {athlete['original_pagerank']:10.6f}")

    # Estatísticas por tier
    print("\n" + "=" * 80)
    print("DISTRIBUIÇÃO POR ELITE TIER")
    print("=" * 80)

    tier_counts = percentiles_full['elite_tier'].value_counts().sort_index()
    print("\nNúmero de atletas por tier:")
    for tier, count in tier_counts.items():
        pct = (count / len(percentiles_full)) * 100
        print(f"  {tier:15}: {count:5} atletas ({pct:5.1f}%)")

    # Top 1% por esporte
    print("\n" + "=" * 80)
    print("TOP 1% POR ESPORTE (Percentil 99+)")
    print("=" * 80)

    elite_1pct = percentiles_full[percentiles_full['pagerank_percentile'] >= 99.0]
    print(f"\nTotal de atletas no percentil 99+: {len(elite_1pct)}")

    for sport in elite_1pct['sport'].unique():
        sport_elite = elite_1pct[elite_1pct['sport'] == sport]
        print(f"\n{sport} ({len(sport_elite)} atletas):")
        for _, athlete in sport_elite.nlargest(5, 'pagerank_percentile').iterrows():
            print(f"  {athlete['name']:30} | {athlete['network_label']:25} | "
                  f"Percentil: {athlete['pagerank_percentile']:.2f}")

    print("\n" + "=" * 80)
    print("CONCLUÍDO COM SUCESSO!")
    print("=" * 80)

if __name__ == '__main__':
    main()
