#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análises Adicionais de Comunidades - Componente 4
==================================================

Implementa 3 análises complementares para enriquecer caracterização de comunidades:

1. Perfil de Medalhas por Comunidade
   - Distribuição Ouro-Prata-Bronze
   - Índice de dominância (3×Ouro + 2×Prata + 1×Bronze / Total)
   - Classificação: Elite (Dom > 2.2) / Competitiva (1.8-2.2) / Participante (< 1.8)

2. Conexões Inter-Comunidade (Rivalidades Estruturais)
   - Matriz de conectividade entre comunidades
   - Identificação de rivalidades (pares mais conectados)
   - Razão densidade intra/inter (segregação)

3. Hierarquia de Comunidades (Central vs Periférica)
   - PageRank médio por comunidade (centralidade)
   - Índice de isolamento (1 - edges_inter / edges_total)
   - Classificação: Núcleo (top 20%) / Intermediária / Periférica (bottom 20%)

Author: TCC Analysis System
Date: October 2025
"""

import os
import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Configuração
RESULTS_DIR = Path(__file__).parent.parent / "../../results"
OUTPUT_DIR = RESULTS_DIR / "additional_analyses"
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 80)
print("ANÁLISES ADICIONAIS DE COMUNIDADES".center(80))
print("=" * 80)


# =============================================================================
# ANÁLISE 1: PERFIL DE MEDALHAS POR COMUNIDADE
# =============================================================================

def analyze_medal_profile():
    """
    Calcula perfil de medalhas por comunidade:
    - Distribuição percentual (Ouro/Prata/Bronze)
    - Índice de dominância ponderado
    - Classificação tipológica
    """
    print("\n[1/3] ANÁLISE DE PERFIL DE MEDALHAS")
    print("-" * 80)

    # Carregar dados
    profiles = pd.read_csv(RESULTS_DIR / "community_profiles_enriched.csv")

    # Calcular proporções percentuais
    profiles['total_medals'] = profiles['gold_count'] + profiles['silver_count'] + profiles['bronze_count']
    profiles['gold_pct'] = (profiles['gold_count'] / profiles['total_medals'] * 100).round(2)
    profiles['silver_pct'] = (profiles['silver_count'] / profiles['total_medals'] * 100).round(2)
    profiles['bronze_pct'] = (profiles['bronze_count'] / profiles['total_medals'] * 100).round(2)

    # Calcular índice de dominância (3×Ouro + 2×Prata + 1×Bronze) / Total
    profiles['dominance_index'] = (
        (3 * profiles['gold_count'] +
         2 * profiles['silver_count'] +
         1 * profiles['bronze_count']) / profiles['total_medals']
    ).round(3)

    # Classificar comunidades por perfil competitivo
    def classify_competitive_profile(dom_idx):
        if dom_idx >= 2.2:
            return 'Elite'
        elif dom_idx >= 1.8:
            return 'Competitiva'
        else:
            return 'Participante'

    profiles['competitive_profile'] = profiles['dominance_index'].apply(classify_competitive_profile)

    # Estatísticas por esporte
    stats_by_sport = profiles.groupby('sport').agg({
        'dominance_index': ['mean', 'std', 'min', 'max'],
        'gold_pct': 'mean',
        'competitive_profile': lambda x: x.value_counts().to_dict()
    }).round(3)

    # Salvar resultados
    output_file = OUTPUT_DIR / "medal_profile_by_community.csv"
    cols_to_save = ['sport', 'sex', 'community_id', 'size',
                    'gold_count', 'silver_count', 'bronze_count', 'total_medals',
                    'gold_pct', 'silver_pct', 'bronze_pct',
                    'dominance_index', 'competitive_profile']
    profiles[cols_to_save].to_csv(output_file, index=False)

    print(f"Arquivo gerado: {output_file.name}")
    print(f"\nDistribuicao de perfis competitivos:")
    print(profiles['competitive_profile'].value_counts())
    print(f"\nIndice de dominancia medio por esporte:")
    print(profiles.groupby('sport')['dominance_index'].agg(['mean', 'std', 'min', 'max']).round(3))

    # Top 5 comunidades mais dominantes
    print(f"\nTOP 5 COMUNIDADES MAIS DOMINANTES:")
    top5 = profiles.nlargest(5, 'dominance_index')[
        ['sport', 'sex', 'community_id', 'dominant_country', 'gold_pct', 'dominance_index', 'competitive_profile']
    ]
    for idx, row in top5.iterrows():
        print(f"  {row['sport']} {row['sex']} C{row['community_id']}: "
              f"{row['dominant_country']} - {row['gold_pct']:.1f}% ouro (Dom: {row['dominance_index']:.2f})")

    return profiles


# =============================================================================
# ANÁLISE 2: CONEXÕES INTER-COMUNIDADE (RIVALIDADES)
# =============================================================================

def analyze_inter_community_connections():
    """
    Analisa conexões entre comunidades:
    - Matriz de conectividade inter-comunidade
    - Identificação de rivalidades (pares mais conectados)
    - Densidade intra vs inter
    """
    print("\n[2/3] ANÁLISE DE CONEXÕES INTER-COMUNIDADE")
    print("-" * 80)

    # Carregar membros detalhados
    members = pd.read_csv(RESULTS_DIR / "community_members_detailed.csv")

    # Encontrar todos os arquivos de edges
    edge_files = list(RESULTS_DIR.glob("**/*_original_edges.csv"))

    inter_community_data = []
    rivalry_pairs = []

    for edge_file in edge_files:
        # Extrair metadata do nome do arquivo
        filename = edge_file.stem  # Ex: basketball_M_team_original_edges
        parts = filename.split('_')

        # Tentar identificar sport e sex
        if 'basketball' in filename.lower():
            sport = 'Basketball'
        elif 'football' in filename.lower():
            sport = 'Football'
        elif 'swimming' in filename.lower():
            sport = 'Swimming'
        else:
            continue

        # Identificar sexo
        sex = 'M' if '_M_' in filename else 'F'

        print(f"\nProcessando: {sport} {sex}")

        # Carregar edges
        try:
            edges = pd.read_csv(edge_file)
        except Exception as e:
            print(f"  Erro ao carregar {edge_file.name}: {e}")
            continue

        # Merge com comunidades
        edges_with_comm = edges.merge(
            members[['athlete_id', 'community_id']],
            left_on='source_id',
            right_on='athlete_id',
            how='left'
        ).rename(columns={'community_id': 'source_comm'})

        edges_with_comm = edges_with_comm.merge(
            members[['athlete_id', 'community_id']],
            left_on='target_id',
            right_on='athlete_id',
            how='left'
        ).rename(columns={'community_id': 'target_comm'})

        # Filtrar apenas edges válidas (com comunidades)
        edges_with_comm = edges_with_comm.dropna(subset=['source_comm', 'target_comm'])

        # Classificar edges: intra vs inter
        edges_with_comm['edge_type'] = edges_with_comm.apply(
            lambda row: 'intra' if row['source_comm'] == row['target_comm'] else 'inter',
            axis=1
        )

        num_intra = (edges_with_comm['edge_type'] == 'intra').sum()
        num_inter = (edges_with_comm['edge_type'] == 'inter').sum()
        total_edges = len(edges_with_comm)

        if total_edges == 0:
            continue

        intra_ratio = num_intra / total_edges
        inter_ratio = num_inter / total_edges

        inter_community_data.append({
            'sport': sport,
            'sex': sex,
            'total_edges': total_edges,
            'intra_edges': num_intra,
            'inter_edges': num_inter,
            'intra_ratio': round(intra_ratio, 4),
            'inter_ratio': round(inter_ratio, 4),
            'segregation_score': round(intra_ratio / (inter_ratio + 0.0001), 2)  # Quanto maior, mais segregada
        })

        print(f"  Total edges: {total_edges}")
        print(f"  Intra-comunidade: {num_intra} ({intra_ratio*100:.1f}%)")
        print(f"  Inter-comunidade: {num_inter} ({inter_ratio*100:.1f}%)")

        # Identificar rivalidades (top pares inter-comunidade)
        inter_edges = edges_with_comm[edges_with_comm['edge_type'] == 'inter']

        if len(inter_edges) > 0:
            rivalry_counts = inter_edges.groupby(['source_comm', 'target_comm']).size().reset_index(name='num_confronts')
            rivalry_counts = rivalry_counts.sort_values('num_confronts', ascending=False).head(5)

            for _, row in rivalry_counts.iterrows():
                rivalry_pairs.append({
                    'sport': sport,
                    'sex': sex,
                    'community_1': int(row['source_comm']),
                    'community_2': int(row['target_comm']),
                    'num_confronts': int(row['num_confronts'])
                })

    # Salvar resultados
    df_inter = pd.DataFrame(inter_community_data)
    df_rivalry = pd.DataFrame(rivalry_pairs)

    output_inter = OUTPUT_DIR / "inter_community_connectivity.csv"
    output_rivalry = OUTPUT_DIR / "top_rivalry_pairs.csv"

    df_inter.to_csv(output_inter, index=False)
    df_rivalry.to_csv(output_rivalry, index=False)

    print(f"\nArquivos gerados:")
    print(f"  - {output_inter.name}")
    print(f"  - {output_rivalry.name}")

    print(f"\nRESUMO GERAL:")
    print(df_inter[['sport', 'sex', 'intra_ratio', 'inter_ratio', 'segregation_score']])

    print(f"\nTOP 5 RIVALIDADES (INTER-COMUNIDADE):")
    for _, row in df_rivalry.head(5).iterrows():
        print(f"  {row['sport']} {row['sex']}: C{row['community_1']} <-> C{row['community_2']} "
              f"({row['num_confronts']} confrontos)")

    return df_inter, df_rivalry


# =============================================================================
# ANÁLISE 3: HIERARQUIA DE COMUNIDADES (CENTRAL VS PERIFÉRICA)
# =============================================================================

def analyze_community_hierarchy():
    """
    Classifica comunidades em hierarquia estrutural:
    - PageRank médio (centralidade)
    - Índice de isolamento
    - Classificação: Núcleo (top 20%) / Intermediária / Periférica
    """
    print("\n[3/3] ANÁLISE DE HIERARQUIA DE COMUNIDADES")
    print("-" * 80)

    # Carregar dados
    profiles = pd.read_csv(RESULTS_DIR / "community_profiles_enriched.csv")

    # Carregar dados de conectividade inter-comunidade
    inter_file = OUTPUT_DIR / "inter_community_connectivity.csv"
    if inter_file.exists():
        inter_data = pd.read_csv(inter_file)

        # Merge para adicionar segregation_score
        profiles = profiles.merge(
            inter_data[['sport', 'sex', 'segregation_score']],
            on=['sport', 'sex'],
            how='left'
        )
    else:
        profiles['segregation_score'] = np.nan

    # Calcular percentis de PageRank médio
    profiles['pagerank_percentile'] = profiles['pagerank_mean'].rank(pct=True) * 100

    # Classificar por hierarquia
    def classify_hierarchy(percentile):
        if percentile >= 80:
            return 'Núcleo'
        elif percentile >= 40:
            return 'Intermediária'
        else:
            return 'Periférica'

    profiles['hierarchy_level'] = profiles['pagerank_percentile'].apply(classify_hierarchy)

    # Calcular score de centralidade (normalizado 0-1)
    pr_min = profiles['pagerank_mean'].min()
    pr_max = profiles['pagerank_mean'].max()
    profiles['centrality_score'] = ((profiles['pagerank_mean'] - pr_min) / (pr_max - pr_min)).round(4)

    # Estatísticas por nível hierárquico
    print(f"\nDistribuição hierárquica:")
    print(profiles['hierarchy_level'].value_counts().sort_index())

    print(f"\nPageRank médio por nível hierárquico:")
    hierarchy_stats = profiles.groupby('hierarchy_level')['pagerank_mean'].agg(['count', 'mean', 'std']).round(6)
    print(hierarchy_stats)

    # Salvar resultados
    output_file = OUTPUT_DIR / "community_hierarchy.csv"
    cols_to_save = ['sport', 'sex', 'community_id', 'size', 'dominant_country',
                    'pagerank_mean', 'pagerank_percentile', 'centrality_score',
                    'segregation_score', 'hierarchy_level']
    profiles[cols_to_save].to_csv(output_file, index=False)

    print(f"\nArquivo gerado: {output_file.name}")

    # Top 5 comunidades do núcleo
    print(f"\nTOP 5 COMUNIDADES DO NUCLEO:")
    nucleo = profiles[profiles['hierarchy_level'] == 'Núcleo'].nlargest(5, 'pagerank_mean')
    for idx, row in nucleo.iterrows():
        print(f"  {row['sport']} {row['sex']} C{row['community_id']}: "
              f"{row['dominant_country']} - PR medio: {row['pagerank_mean']:.6f} "
              f"(P{row['pagerank_percentile']:.0f})")

    # Comunidades mais periféricas
    print(f"\nCOMUNIDADES MAIS PERIFERICAS:")
    perifericas = profiles[profiles['hierarchy_level'] == 'Periférica'].nsmallest(5, 'pagerank_mean')
    for idx, row in perifericas.iterrows():
        print(f"  {row['sport']} {row['sex']} C{row['community_id']}: "
              f"{row['dominant_country']} - PR medio: {row['pagerank_mean']:.6f}")

    return profiles


# =============================================================================
# GERAR RELATÓRIO CONSOLIDADO
# =============================================================================

def generate_consolidated_report(medal_profiles, inter_data, rivalry_data, hierarchy):
    """Gera relatório JSON consolidado com todos os insights."""
    print("\n" + "=" * 80)
    print("GERANDO RELATÓRIO CONSOLIDADO")
    print("=" * 80)

    report = {
        "metadata": {
            "total_communities": int(len(medal_profiles)),
            "total_athletes": int(medal_profiles['size'].sum()),
            "sports": list(medal_profiles['sport'].unique())
        },

        "medal_profile_summary": {
            "by_competitive_profile": medal_profiles['competitive_profile'].value_counts().to_dict(),
            "dominance_index": {
                "mean": float(medal_profiles['dominance_index'].mean().round(3)),
                "std": float(medal_profiles['dominance_index'].std().round(3)),
                "min": float(medal_profiles['dominance_index'].min()),
                "max": float(medal_profiles['dominance_index'].max())
            },
            "gold_percentage": {
                "mean": float(medal_profiles['gold_pct'].mean().round(2)),
                "std": float(medal_profiles['gold_pct'].std().round(2))
            }
        },

        "connectivity_summary": {
            "by_sport": inter_data.astype(object).where(inter_data.notnull(), None).to_dict('records') if not inter_data.empty else [],
            "top_rivalries": [
                {k: int(v) if isinstance(v, (np.integer, np.int64)) else float(v) if isinstance(v, (np.floating, np.float64)) else v
                 for k, v in record.items()}
                for record in rivalry_data.head(10).to_dict('records')
            ] if not rivalry_data.empty else []
        },

        "hierarchy_summary": {
            "by_level": hierarchy['hierarchy_level'].value_counts().to_dict(),
            "nucleus": hierarchy[hierarchy['hierarchy_level'] == 'Núcleo'][
                ['sport', 'sex', 'community_id', 'dominant_country', 'pagerank_mean', 'size']
            ].to_dict('records'),
            "peripheral": hierarchy[hierarchy['hierarchy_level'] == 'Periférica'][
                ['sport', 'sex', 'community_id', 'dominant_country', 'pagerank_mean', 'size']
            ].nsmallest(5, 'pagerank_mean').to_dict('records')
        },

        "key_insights": [
            f"Perfil competitivo: {medal_profiles['competitive_profile'].value_counts().to_dict()}",
            f"Dominância média de medalhas: {medal_profiles['dominance_index'].mean():.2f} (escala 1-3)",
            f"Segregação média: {inter_data['segregation_score'].mean():.2f}x" if not inter_data.empty else "N/A",
            f"Núcleo de elite: {(hierarchy['hierarchy_level'] == 'Núcleo').sum()} comunidades ({(hierarchy['hierarchy_level'] == 'Núcleo').sum()/len(hierarchy)*100:.1f}%)"
        ]
    }

    output_file = OUTPUT_DIR / "consolidated_additional_analyses.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nRelatorio consolidado: {output_file.name}")
    print(f"\nKEY INSIGHTS:")
    for insight in report['key_insights']:
        print(f"  - {insight}")

    return report


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Executa todas as análises adicionais."""

    # Análise 1: Perfil de Medalhas
    medal_profiles = analyze_medal_profile()

    # Análise 2: Conexões Inter-Comunidade
    inter_data, rivalry_data = analyze_inter_community_connections()

    # Análise 3: Hierarquia de Comunidades
    hierarchy = analyze_community_hierarchy()

    # Relatório Consolidado
    report = generate_consolidated_report(medal_profiles, inter_data, rivalry_data, hierarchy)

    print("\n" + "=" * 80)
    print("TODAS AS ANALISES CONCLUIDAS COM SUCESSO!".center(80))
    print("=" * 80)
    print(f"\nArquivos gerados em: {OUTPUT_DIR}")
    print("\nPróximos passos:")
    print("  1. Revisar CSVs gerados em ../../results/additional_analyses/")
    print("  2. Integrar insights na monografia (Seção 3.2)")
    print("  3. Criar visualizações para apresentação")
    print("\n")


if __name__ == "__main__":
    main()
