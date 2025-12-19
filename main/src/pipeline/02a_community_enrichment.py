#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Enriquecida de Comunidades - 188 Comunidades (16 Redes Independentes)

ATUALIZAÇÃO: Este script foi reformulado para processar as 16 redes independentes:
- Swimming/Athletics: separados por event_type (individual/team)
- Outros esportes: separados apenas por gênero

Saídas:
- community_profiles_enriched.csv: Métricas agregadas por comunidade (188 comunidades)
- community_members_detailed.csv: Dados detalhados de cada atleta com flag de comunidade
"""

import pandas as pd
import numpy as np
import os
from collections import Counter

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def calculate_shannon_entropy(series):
    """Calcula entropia de Shannon para uma série de valores."""
    counts = series.value_counts(normalize=True)
    return -np.sum(counts * np.log2(counts + 1e-10))

def extract_year_from_games(games_str):
    """Extrai ano do campo 'games' (ex: '2020 Summer' -> 2020)."""
    try:
        return int(str(games_str).split()[0])
    except:
        return np.nan

def process_network(df, sport, sex, event_type=None):
    """Processa uma rede individual e retorna métricas de suas comunidades."""

    # Filtrar rede
    if event_type:
        net_df = df[(df['sport'] == sport) & (df['sex'] == sex) & (df['event_type'] == event_type)]
        network_label = f"{sport}_{sex}_{event_type}"
    else:
        net_df = df[(df['sport'] == sport) & (df['sex'] == sex)]
        network_label = f"{sport}_{sex}"

    if len(net_df) == 0:
        return [], []

    # Extrair anos
    net_df = net_df.copy()
    net_df['year'] = net_df['games'].apply(extract_year_from_games)

    communities = []
    detailed_members = []

    for comm_id in sorted(net_df['original_community'].unique()):
        comm_df = net_df[net_df['original_community'] == comm_id]

        # ======================================================================
        # MÉTRICAS AGREGADAS DA COMUNIDADE
        # ======================================================================

        # Tamanho
        size = len(comm_df)

        # Anos
        years = comm_df['year'].dropna()
        if len(years) > 0:
            year_start = int(years.min())
            year_end = int(years.max())
            span_years = year_end - year_start
        else:
            year_start = year_end = span_years = np.nan

        # Entropia temporal (por década)
        if len(years) > 0:
            decades = (years // 10) * 10
            temporal_entropy = calculate_shannon_entropy(decades)
        else:
            temporal_entropy = np.nan

        # Era dominante (por década)
        if len(years) > 0:
            decade_counts = Counter((years // 10) * 10)
            dominant_era = decade_counts.most_common(1)[0][0]
            era_concentration = decade_counts.most_common(1)[0][1] / len(years)
        else:
            dominant_era = np.nan
            era_concentration = np.nan

        # Entropia geográfica
        nocs = comm_df['noc'].dropna()
        if len(nocs) > 0:
            geographic_entropy = calculate_shannon_entropy(nocs)
            num_countries = nocs.nunique()

            noc_counts = nocs.value_counts()
            dominant_country = noc_counts.index[0]
            country_dominance = noc_counts.iloc[0] / len(nocs)
            top_countries = ','.join(noc_counts.head(3).index.tolist())
        else:
            geographic_entropy = num_countries = np.nan
            dominant_country = 'N/A'
            country_dominance = np.nan
            top_countries = ''

        # Medalhas
        medals = comm_df['medal'].value_counts()
        gold_count = medals.get('Gold', 0)
        silver_count = medals.get('Silver', 0)
        bronze_count = medals.get('Bronze', 0)
        total_medals = len(comm_df)

        # PageRank
        pr_values = comm_df['original_pagerank'].dropna()
        if len(pr_values) > 0:
            pagerank_mean = pr_values.mean()
            pagerank_median = pr_values.median()
            pagerank_std = pr_values.std()
            pagerank_max = pr_values.max()
            pagerank_min = pr_values.min()
            pagerank_cv = pr_values.std() / pr_values.mean() if pr_values.mean() > 0 else np.nan

            # Top 3 atletas por PageRank
            top_pr = comm_df.nlargest(3, 'original_pagerank')[['name', 'original_pagerank']]
            top1_name = top_pr.iloc[0]['name'] if len(top_pr) > 0 else ''
            top1_pagerank = top_pr.iloc[0]['original_pagerank'] if len(top_pr) > 0 else np.nan
            top2_name = top_pr.iloc[1]['name'] if len(top_pr) > 1 else ''
            top2_pagerank = top_pr.iloc[1]['original_pagerank'] if len(top_pr) > 1 else np.nan
            top3_name = top_pr.iloc[2]['name'] if len(top_pr) > 2 else ''
            top3_pagerank = top_pr.iloc[2]['original_pagerank'] if len(top_pr) > 2 else np.nan
        else:
            pagerank_mean = pagerank_median = pagerank_std = np.nan
            pagerank_max = pagerank_min = pagerank_cv = np.nan
            top1_name = top2_name = top3_name = ''
            top1_pagerank = top2_pagerank = top3_pagerank = np.nan

        # Betweenness
        bw_values = comm_df['original_betweenness_centrality'].dropna()
        if len(bw_values) > 0:
            betweenness_mean = bw_values.mean()
            betweenness_max = bw_values.max()
            num_bridge_athletes = len(bw_values[bw_values > 0])
        else:
            betweenness_mean = betweenness_max = np.nan
            num_bridge_athletes = 0

        communities.append({
            'sport': sport,
            'sex': sex,
            'event_type': event_type if event_type else 'N/A',
            'network_label': network_label,
            'community_id': comm_id,
            'size': size,
            'year_start': year_start,
            'year_end': year_end,
            'span_years': span_years,
            'temporal_entropy': temporal_entropy,
            'dominant_era': dominant_era,
            'era_concentration': era_concentration,
            'num_countries': num_countries,
            'geographic_entropy': geographic_entropy,
            'dominant_country': dominant_country,
            'country_dominance': country_dominance,
            'top_countries': top_countries,
            'gold_count': gold_count,
            'silver_count': silver_count,
            'bronze_count': bronze_count,
            'total_medals': total_medals,
            'pagerank_mean': pagerank_mean,
            'pagerank_median': pagerank_median,
            'pagerank_std': pagerank_std,
            'pagerank_max': pagerank_max,
            'pagerank_min': pagerank_min,
            'pagerank_cv': pagerank_cv,
            'betweenness_mean': betweenness_mean,
            'betweenness_max': betweenness_max,
            'num_bridge_athletes': num_bridge_athletes,
            'top1_name': top1_name,
            'top1_pagerank': top1_pagerank,
            'top2_name': top2_name,
            'top2_pagerank': top2_pagerank,
            'top3_name': top3_name,
            'top3_pagerank': top3_pagerank
        })

        # ======================================================================
        # MEMBROS DETALHADOS (para community_members_detailed.csv)
        # ======================================================================
        for _, athlete in comm_df.iterrows():
            detailed_members.append({
                'athlete_id': athlete['athlete_id'],
                'sport': sport,
                'sex': sex,
                'event_type': event_type if event_type else 'N/A',
                'network_label': network_label,
                'community_id': comm_id,
                'name': athlete['name'],
                'noc': athlete['noc'],
                'year': athlete.get('year', np.nan),
                'pagerank': athlete['original_pagerank'],
                'betweenness': athlete['original_betweenness_centrality'],
                'is_bridge': athlete['original_betweenness_centrality'] > 0 if pd.notna(athlete['original_betweenness_centrality']) else False
            })

    return communities, detailed_members

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Processa todas as 16 redes e gera CSVs consolidados."""

    print("=" * 80)
    print("ANÁLISE ENRIQUECIDA DE COMUNIDADES - 188 COMUNIDADES (16 REDES)")
    print("=" * 80)

    # Determinar paths dinamicamente
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, "..", "..", "..")
    results_dir = os.path.join(project_root, "results")

    # Carregar dados
    athletes_file = os.path.join(results_dir, 'consolidated_sports_network_analysis.csv')
    print(f"\nCarregando dados de: {athletes_file}")
    df = pd.read_csv(athletes_file)
    print(f"✓ Carregados {len(df)} atletas")

    all_communities = []
    all_detailed_members = []

    # Processar esportes mistos (Swimming, Athletics)
    for sport in ['Swimming', 'Athletics']:
        for event_type in ['individual', 'team']:
            for sex in ['M', 'F']:
                print(f"\nProcessando: {sport} {event_type} {sex}")
                communities, members = process_network(df, sport, sex, event_type)
                all_communities.extend(communities)
                all_detailed_members.extend(members)
                print(f"  → {len(communities)} comunidades, {len(members)} atletas")

    # Processar esportes puros (Basketball, Football, Judo, Boxing)
    for sport in ['Basketball', 'Football', 'Judo', 'Boxing']:
        for sex in ['M', 'F']:
            print(f"\nProcessando: {sport} {sex}")
            communities, members = process_network(df, sport, sex)
            all_communities.extend(communities)
            all_detailed_members.extend(members)
            print(f"  → {len(communities)} comunidades, {len(members)} atletas")

    # ===========================================================================
    # EXPORTAR RESULTADOS
    # ===========================================================================

    print("\n" + "=" * 80)
    print("EXPORTANDO RESULTADOS")
    print("=" * 80)

    # 1. Perfis de comunidades (agregado)
    communities_df = pd.DataFrame(all_communities)
    output_communities = os.path.join(results_dir, 'community_profiles_enriched.csv')
    communities_df.to_csv(output_communities, index=False)
    print(f"\n[OK] Perfis de comunidades salvos: {output_communities}")
    print(f"    Total: {len(communities_df)} comunidades")

    # Breakdown por esporte
    print("\n    Breakdown por esporte:")
    for sport in communities_df['sport'].unique():
        sport_count = len(communities_df[communities_df['sport'] == sport])
        print(f"      {sport:15}: {sport_count:3} comunidades")

    # 2. Membros detalhados (todos os atletas com features de comunidade)
    members_df = pd.DataFrame(all_detailed_members)
    output_members = os.path.join(results_dir, 'community_members_detailed.csv')
    members_df.to_csv(output_members, index=False)
    print(f"\n[OK] Membros detalhados salvos: {output_members}")
    print(f"    Total: {len(members_df)} atletas")

    # Mostrar top 10 maiores comunidades
    print("\n" + "=" * 80)
    print("TOP 10 MAIORES COMUNIDADES:")
    print("=" * 80)
    top10 = communities_df.nlargest(10, 'size')
    print(top10[['sport', 'event_type', 'sex', 'community_id', 'size',
                 'span_years', 'temporal_entropy', 'geographic_entropy',
                 'dominant_country']].to_string(index=False))

    print("\n" + "=" * 80)
    print("CONCLUÍDO COM SUCESSO!")
    print("=" * 80)

if __name__ == '__main__':
    main()
