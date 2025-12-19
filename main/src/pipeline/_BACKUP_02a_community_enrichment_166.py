"""
Análise Formal e Enriquecida de Comunidades em Redes Olímpicas

Este script gera análises detalhadas das comunidades detectadas pelo algoritmo de Louvain,
incluindo métricas de dominância temporal, geográfica, estrutural e de performance.

Saídas:
- community_profiles_enriched.csv: Métricas agregadas por comunidade
- community_members_detailed.csv: Dados detalhados de cada atleta com flag de comunidade
- community_summary.json: Resumo em JSON para dashboard
"""

import pandas as pd
import numpy as np
import json
from collections import Counter
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

# ==============================================================================
# CARREGAR DADOS
# ==============================================================================

print("=" * 80)
print("ANÁLISE ENRIQUECIDA DE COMUNIDADES - REDES OLÍMPICAS")
print("=" * 80)

df = pd.read_csv('../../results/consolidated_sports_network_analysis.csv')

# Preparação dos dados
df['year'] = df['games'].str.extract(r'(\d{4})').astype(float)
df['decade'] = (df['year'] // 10 * 10).astype('Int64')
df['era'] = df['year'].apply(identify_era)

print(f"\nDados carregados: {len(df)} atletas")
print(f"Período: {df['year'].min():.0f} - {df['year'].max():.0f}")

# ==============================================================================
# ANÁLISE POR COMUNIDADE
# ==============================================================================

all_communities = []
detailed_members = []

for sport in df['sport'].unique():
    for sex in df['sex'].unique():
        sport_sex_data = df[(df['sport'] == sport) & (df['sex'] == sex)]

        if len(sport_sex_data) == 0:
            continue

        print(f"\nProcessando {sport} - {sex}...")

        communities = sport_sex_data.groupby('original_community')

        for comm_id, comm_data in communities:
            size = len(comm_data)

            # =====================================================
            # ANÁLISE TEMPORAL
            # =====================================================
            year_range = (comm_data['year'].min(), comm_data['year'].max())
            span_years = year_range[1] - year_range[0]

            decade_counts = comm_data['decade'].value_counts().to_dict()
            temporal_entropy = calculate_shannon_entropy(decade_counts)

            era_counts = comm_data['era'].value_counts()
            dominant_era = era_counts.idxmax()
            era_concentration = era_counts.max() / len(comm_data)

            # =====================================================
            # ANÁLISE GEOGRÁFICA
            # =====================================================
            country_counts = comm_data['noc'].value_counts().to_dict()
            num_countries = len(country_counts)
            geographic_entropy = calculate_shannon_entropy(country_counts)

            dominant_country = comm_data['noc'].value_counts().idxmax()
            country_dominance = comm_data['noc'].value_counts().max() / len(comm_data)

            # Top 3 países
            top_countries = comm_data['noc'].value_counts().head(3)
            top_countries_str = '; '.join([f"{noc}({count})" for noc, count in top_countries.items()])

            # =====================================================
            # PERFIL DE PERFORMANCE
            # =====================================================
            medal_dist = comm_data['medal'].value_counts().to_dict()

            pr_stats = {
                'mean': comm_data['original_pagerank'].mean(),
                'median': comm_data['original_pagerank'].median(),
                'std': comm_data['original_pagerank'].std(),
                'max': comm_data['original_pagerank'].max(),
                'min': comm_data['original_pagerank'].min(),
                'cv': comm_data['original_pagerank'].std() / comm_data['original_pagerank'].mean() if comm_data['original_pagerank'].mean() > 0 else 0
            }

            # Top 3 superstars
            top3 = comm_data.nlargest(3, 'original_pagerank')[['name', 'noc', 'year', 'original_pagerank']]

            # =====================================================
            # CENTRALIDADES
            # =====================================================
            betweenness_stats = {
                'mean': comm_data['original_betweenness_centrality'].mean(),
                'max': comm_data['original_betweenness_centrality'].max()
            }

            # Atletas ponte (alto betweenness - top 10%)
            bridge_threshold = comm_data['original_betweenness_centrality'].quantile(0.9)
            bridge_athletes = comm_data[comm_data['original_betweenness_centrality'] > bridge_threshold]

            # =====================================================
            # ARMAZENAR PERFIL DA COMUNIDADE
            # =====================================================
            community_profile = {
                'sport': sport,
                'sex': sex,
                'community_id': int(comm_id),
                'size': size,

                # Temporal
                'year_start': year_range[0],
                'year_end': year_range[1],
                'span_years': span_years,
                'temporal_entropy': temporal_entropy,
                'dominant_era': dominant_era,
                'era_concentration': era_concentration,

                # Geográfica
                'num_countries': num_countries,
                'geographic_entropy': geographic_entropy,
                'dominant_country': dominant_country,
                'country_dominance': country_dominance,
                'top_countries': top_countries_str,

                # Performance
                'gold_count': medal_dist.get('Gold', 0),
                'silver_count': medal_dist.get('Silver', 0),
                'bronze_count': medal_dist.get('Bronze', 0),
                'total_medals': sum(medal_dist.values()),
                'pagerank_mean': pr_stats['mean'],
                'pagerank_median': pr_stats['median'],
                'pagerank_std': pr_stats['std'],
                'pagerank_max': pr_stats['max'],
                'pagerank_min': pr_stats['min'],
                'pagerank_cv': pr_stats['cv'],

                # Centralidades
                'betweenness_mean': betweenness_stats['mean'],
                'betweenness_max': betweenness_stats['max'],
                'num_bridge_athletes': len(bridge_athletes),

                # Top athletes
                'top1_name': top3.iloc[0]['name'] if len(top3) > 0 else None,
                'top1_pagerank': top3.iloc[0]['original_pagerank'] if len(top3) > 0 else None,
                'top2_name': top3.iloc[1]['name'] if len(top3) > 1 else None,
                'top2_pagerank': top3.iloc[1]['original_pagerank'] if len(top3) > 1 else None,
                'top3_name': top3.iloc[2]['name'] if len(top3) > 2 else None,
                'top3_pagerank': top3.iloc[2]['original_pagerank'] if len(top3) > 2 else None,
            }

            all_communities.append(community_profile)

            # =====================================================
            # ARMAZENAR MEMBROS DETALHADOS
            # =====================================================
            for idx, athlete in comm_data.iterrows():
                is_bridge = athlete['original_betweenness_centrality'] > bridge_threshold
                is_top_pagerank = athlete['original_pagerank'] >= comm_data['original_pagerank'].quantile(0.9)

                member_detail = {
                    'athlete_id': athlete['athlete_id'],
                    'name': athlete['name'],
                    'sport': sport,
                    'sex': sex,
                    'community_id': int(comm_id),
                    'community_size': size,
                    'noc': athlete['noc'],
                    'year': athlete['year'],
                    'decade': athlete['decade'],
                    'era': athlete['era'],
                    'medal': athlete['medal'],
                    'pagerank': athlete['original_pagerank'],
                    'betweenness': athlete['original_betweenness_centrality'],
                    'is_bridge_athlete': is_bridge,
                    'is_top_performer': is_top_pagerank,
                    'dominant_country': dominant_country,
                    'dominant_era': dominant_era,
                }

                detailed_members.append(member_detail)

# ==============================================================================
# EXPORTAR RESULTADOS
# ==============================================================================

# 1. Perfis de comunidades (agregado)
results_df = pd.DataFrame(all_communities)
results_df.to_csv('../../results/community_profiles_enriched.csv', index=False)
print(f"\n[OK] Perfis de comunidades salvos: community_profiles_enriched.csv")

# 2. Membros detalhados (todos os atletas com features de comunidade)
members_df = pd.DataFrame(detailed_members)
members_df.to_csv('../../results/community_members_detailed.csv', index=False)
print(f"[OK] Membros detalhados salvos: community_members_detailed.csv")

# 3. Resumo JSON para dashboard
summary = {
    'total_communities': len(all_communities),
    'total_athletes': len(members_df),
    'sports': list(df['sport'].unique()),
    'communities_by_sport': results_df.groupby('sport').size().to_dict(),
    'largest_communities': results_df.nlargest(5, 'size')[['sport', 'sex', 'community_id', 'size', 'dominant_country']].to_dict('records'),
    'most_diverse_temporal': results_df.nlargest(5, 'temporal_entropy')[['sport', 'sex', 'community_id', 'temporal_entropy']].to_dict('records'),
    'most_diverse_geographic': results_df.nlargest(5, 'geographic_entropy')[['sport', 'sex', 'community_id', 'geographic_entropy', 'num_countries']].to_dict('records'),
}

with open('../../results/community_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f"[OK] Resumo JSON salvo: community_summary.json")

# ==============================================================================
# ESTATÍSTICAS GERAIS
# ==============================================================================

print("\n" + "=" * 80)
print("ESTATÍSTICAS GERAIS")
print("=" * 80)

print(f"\n[OK] Total de comunidades analisadas: {len(all_communities)}")
print(f"[OK] Total de atletas processados: {len(members_df)}")

print("\nPor Esporte:")
for sport in results_df['sport'].unique():
    sport_comms = results_df[results_df['sport'] == sport]
    print(f"\n  {sport}:")
    print(f"    • Comunidades: {len(sport_comms)}")
    print(f"    • Tamanho médio: {sport_comms['size'].mean():.1f} atletas")
    print(f"    • Entropia temporal média: {sport_comms['temporal_entropy'].mean():.2f}")
    print(f"    • Entropia geográfica média: {sport_comms['geographic_entropy'].mean():.2f}")
    print(f"    • PageRank CV médio: {sport_comms['pagerank_cv'].mean():.2f}")

print("\n" + "=" * 80)
print("ANÁLISE CONCLUÍDA")
print("=" * 80 + "\n")
