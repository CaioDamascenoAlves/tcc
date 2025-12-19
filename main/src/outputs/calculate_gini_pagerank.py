#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cálculo do Índice de GINI da Distribuição de PageRank por Rede

O índice de GINI mede desigualdade/concentração na distribuição de PageRank:
- GINI = 0: Perfeita igualdade (todos atletas têm mesmo PageRank)
- GINI = 1: Máxima concentração (um atleta tem todo PageRank)

Interpretação para redes:
- GINI < 0.4: Distribuição relativamente igualitária
- GINI 0.4-0.6: Concentração moderada
- GINI > 0.6: Alta concentração (hierarquia forte)
"""

import pandas as pd
import numpy as np
import os

def calculate_gini(values):
    """
    Calcula índice de GINI para uma série de valores.

    Fórmula: GINI = (2 * sum(i * x_i)) / (n * sum(x_i)) - (n + 1) / n
    onde x_i são valores ordenados em ordem crescente.

    Args:
        values: array ou série de valores numéricos

    Returns:
        float: índice de GINI (0 a 1)
    """
    values = np.array(values)
    values = values[~np.isnan(values)]  # Remover NaN

    if len(values) == 0:
        return np.nan

    if len(values) == 1:
        return 0.0

    # Ordenar valores
    sorted_values = np.sort(values)
    n = len(sorted_values)

    # Calcular GINI
    index = np.arange(1, n + 1)
    gini = (2 * np.sum(index * sorted_values)) / (n * np.sum(sorted_values)) - (n + 1) / n

    return gini

def main():
    """Calcula GINI para cada uma das 16 redes."""

    print("=" * 80)
    print("CÁLCULO DO ÍNDICE DE GINI - DISTRIBUIÇÃO DE PAGERANK POR REDE")
    print("=" * 80)

    # Carregar dados
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, "..", "..", "..")
    results_dir = os.path.join(project_root, "results")
    athletes_file = os.path.join(results_dir, 'consolidated_sports_network_analysis.csv')

    print(f"\nCarregando dados de: {athletes_file}")
    df = pd.read_csv(athletes_file)
    print(f"✓ Carregados {len(df)} atletas")

    gini_results = []

    # Processar esportes mistos (Swimming, Athletics)
    for sport in ['Swimming', 'Athletics']:
        for event_type in ['individual', 'team']:
            for sex in ['M', 'F']:
                network_label = f"{sport}_{sex}_{event_type}"
                net_df = df[(df['sport'] == sport) &
                           (df['sex'] == sex) &
                           (df['event_type'] == event_type)]

                if len(net_df) == 0:
                    continue

                pr_values = net_df['original_pagerank'].dropna()
                gini = calculate_gini(pr_values)

                print(f"\n{network_label:30} | n={len(net_df):4} | GINI={gini:.4f}")

                gini_results.append({
                    'sport': sport,
                    'sex': sex,
                    'event_type': event_type,
                    'network_label': network_label,
                    'network_size': len(net_df),
                    'gini_pagerank': gini,
                    'pagerank_mean': pr_values.mean(),
                    'pagerank_std': pr_values.std(),
                    'pagerank_max': pr_values.max(),
                    'pagerank_min': pr_values.min()
                })

    # Processar esportes puros (Basketball, Football, Judo, Boxing)
    for sport in ['Basketball', 'Football', 'Judo', 'Boxing']:
        for sex in ['M', 'F']:
            network_label = f"{sport}_{sex}"
            net_df = df[(df['sport'] == sport) & (df['sex'] == sex)]

            if len(net_df) == 0:
                continue

            pr_values = net_df['original_pagerank'].dropna()
            gini = calculate_gini(pr_values)

            print(f"\n{network_label:30} | n={len(net_df):4} | GINI={gini:.4f}")

            gini_results.append({
                'sport': sport,
                'sex': sex,
                'event_type': 'N/A',
                'network_label': network_label,
                'network_size': len(net_df),
                'gini_pagerank': gini,
                'pagerank_mean': pr_values.mean(),
                'pagerank_std': pr_values.std(),
                'pagerank_max': pr_values.max(),
                'pagerank_min': pr_values.min()
            })

    # Exportar resultados
    print("\n" + "=" * 80)
    print("EXPORTANDO RESULTADOS")
    print("=" * 80)

    gini_df = pd.DataFrame(gini_results)
    output_file = os.path.join(results_dir, 'gini_pagerank_by_network.csv')
    gini_df.to_csv(output_file, index=False)
    print(f"\n[OK] GINI por rede salvo: {output_file}")

    # Análise estatística
    print("\n" + "=" * 80)
    print("ANÁLISE ESTATÍSTICA - GINI POR CATEGORIA")
    print("=" * 80)

    print(f"\nGINI médio geral: {gini_df['gini_pagerank'].mean():.4f} ± {gini_df['gini_pagerank'].std():.4f}")
    print(f"GINI mínimo: {gini_df['gini_pagerank'].min():.4f} ({gini_df.loc[gini_df['gini_pagerank'].idxmin(), 'network_label']})")
    print(f"GINI máximo: {gini_df['gini_pagerank'].max():.4f} ({gini_df.loc[gini_df['gini_pagerank'].idxmax(), 'network_label']})")

    print("\n--- GINI médio por esporte ---")
    for sport in gini_df['sport'].unique():
        sport_gini = gini_df[gini_df['sport'] == sport]['gini_pagerank'].mean()
        print(f"{sport:15}: {sport_gini:.4f}")

    print("\n--- GINI médio por gênero ---")
    for sex in ['M', 'F']:
        sex_gini = gini_df[gini_df['sex'] == sex]['gini_pagerank'].mean()
        label = 'Masculino' if sex == 'M' else 'Feminino'
        print(f"{label:15}: {sex_gini:.4f}")

    print("\n--- Redes ordenadas por GINI (maior → menor) ---")
    sorted_df = gini_df.sort_values('gini_pagerank', ascending=False)
    print(sorted_df[['network_label', 'network_size', 'gini_pagerank']].to_string(index=False))

    print("\n" + "=" * 80)
    print("CONCLUÍDO COM SUCESSO!")
    print("=" * 80)

if __name__ == '__main__':
    main()
