#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera Radar Charts para comparação de redes competitivas olímpicas.

Gera 2 figuras:
1. Radar Chart de Esportes Mistos (8 redes: Swimming/Athletics × Individual/Team × M/F)
2. Radar Chart de Comparação Tipológica (3 perfis médios)

Métricas (6 eixos):
- Modularidade
- Densidade
- N. Comunidades (normalizado)
- Entropia Geográfica (normalizado)
- PageRank CV (normalizado)
- Razão Intra/Inter (normalizado)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi
import os
import json

# Configurações de estilo
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10

# Caminhos
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..", "..", "..")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "monografia", "figuras")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Carregar dados
athletes_df = pd.read_csv(os.path.join(RESULTS_DIR, "consolidated_sports_network_analysis.csv"))
cohesion_df = pd.read_csv(os.path.join(RESULTS_DIR, "community_cohesion_metrics.csv"))

print(f"✓ Dados carregados: {len(athletes_df)} atletas")

def load_network_metrics():
    """Carrega e processa métricas das 16 redes."""

    metrics = []

    for sport in ['Swimming', 'Athletics', 'Basketball', 'Football', 'Judo', 'Boxing']:
        sport_lower = sport.lower()

        if sport in ['Swimming', 'Athletics']:
            # Esportes mistos: têm event_type
            for sex in ['M', 'F']:
                for event_type in ['individual', 'team']:
                    # Filtrar dados
                    sport_data = athletes_df[
                        (athletes_df['sport'] == sport) &
                        (athletes_df['sex'] == sex) &
                        (athletes_df['event_type'] == event_type)
                    ]

                    if len(sport_data) == 0:
                        continue

                    # Buscar métricas de coesão
                    cohesion_sport = cohesion_df[
                        (cohesion_df['sport'] == sport_lower) &
                        (cohesion_df['sex'] == sex) &
                        (cohesion_df['event_type'] == event_type)
                    ]

                    # Calcular métricas
                    n_nodes = len(sport_data)
                    n_communities = sport_data['original_community'].nunique()

                    if len(cohesion_sport) > 0:
                        modularity = cohesion_sport['subcommunity_modularity'].mean()
                        density = cohesion_sport['density'].mean()
                        intra_inter_ratio = cohesion_sport['intra_inter_ratio'].mean()
                    else:
                        # Buscar do JSON
                        json_file = os.path.join(RESULTS_DIR, sport_lower,
                                                f"{sport_lower}_{sex}_{event_type}_network_summary.json")
                        if os.path.exists(json_file):
                            with open(json_file, 'r') as f:
                                data = json.load(f)
                                modularity = data.get('original_community', {}).get('modularity', 0.0)
                                density = data.get('original_network', {}).get('density', 0.0)
                                intra_inter_ratio = cohesion_sport['intra_inter_ratio'].mean() if len(cohesion_sport) > 0 else 1.0
                        else:
                            modularity = 0.0
                            density = 0.0
                            intra_inter_ratio = 1.0

                    # Métricas derivadas
                    pagerank_cv = sport_data['original_pagerank'].std() / sport_data['original_pagerank'].mean()
                    geo_entropy = sport_data.groupby('original_community')['noc'].nunique().mean()
                    geo_entropy = np.log2(geo_entropy) if geo_entropy > 1 else 0  # Aproximação de entropia

                    metrics.append({
                        'sport': sport,
                        'sex': sex,
                        'event_type': event_type,
                        'type_label': 'Misto',
                        'n_nodes': n_nodes,
                        'n_communities': n_communities,
                        'modularity': modularity,
                        'density': density,
                        'pagerank_cv': pagerank_cv,
                        'geo_entropy': geo_entropy,
                        'intra_inter_ratio': intra_inter_ratio,
                        'label': f"{sport} {event_type.title()} {sex}"
                    })
        else:
            # Outros esportes
            type_label = 'Coletivo' if sport in ['Basketball', 'Football'] else 'Individual'

            for sex in ['M', 'F']:
                sport_data = athletes_df[
                    (athletes_df['sport'] == sport) &
                    (athletes_df['sex'] == sex)
                ]

                if len(sport_data) == 0:
                    continue

                # Buscar métricas
                cohesion_sport = cohesion_df[
                    (cohesion_df['sport'] == sport_lower) &
                    (cohesion_df['sex'] == sex)
                ]

                n_nodes = len(sport_data)
                n_communities = sport_data['original_community'].nunique()

                if len(cohesion_sport) > 0:
                    modularity = cohesion_sport['subcommunity_modularity'].mean()
                    density = cohesion_sport['density'].mean()
                    intra_inter_ratio = cohesion_sport['intra_inter_ratio'].mean()
                else:
                    json_file = os.path.join(RESULTS_DIR, sport_lower,
                                            f"{sport_lower}_{sex}_network_summary.json")
                    if os.path.exists(json_file):
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            modularity = data.get('original_community', {}).get('modularity', 0.0)
                            density = data.get('original_network', {}).get('density', 0.0)
                            intra_inter_ratio = 1.0
                    else:
                        modularity = 0.0
                        density = 0.0
                        intra_inter_ratio = 1.0

                pagerank_cv = sport_data['original_pagerank'].std() / sport_data['original_pagerank'].mean()
                geo_entropy = sport_data.groupby('original_community')['noc'].nunique().mean()
                geo_entropy = np.log2(geo_entropy) if geo_entropy > 1 else 0

                metrics.append({
                    'sport': sport,
                    'sex': sex,
                    'event_type': None,
                    'type_label': type_label,
                    'n_nodes': n_nodes,
                    'n_communities': n_communities,
                    'modularity': modularity,
                    'density': density,
                    'pagerank_cv': pagerank_cv,
                    'geo_entropy': geo_entropy,
                    'intra_inter_ratio': intra_inter_ratio,
                    'label': f"{sport} {sex}"
                })

    return pd.DataFrame(metrics)

def normalize_metrics(df):
    """Normaliza métricas para escala 0-1 usando min-max."""
    df_norm = df.copy()

    # Normalizar cada métrica
    for col in ['modularity', 'density', 'pagerank_cv', 'geo_entropy', 'intra_inter_ratio']:
        min_val = df[col].min()
        max_val = df[col].max()
        df_norm[f'{col}_norm'] = (df[col] - min_val) / (max_val - min_val) if max_val > min_val else 0.5

    # N. comunidades normalizado
    min_comm = df['n_communities'].min()
    max_comm = df['n_communities'].max()
    df_norm['n_communities_norm'] = (df['n_communities'] - min_comm) / (max_comm - min_comm) if max_comm > min_comm else 0.5

    return df_norm

def create_radar_chart(data, labels, title, filename, colors, legend_labels):
    """Cria um radar chart."""

    # Número de variáveis
    categories = ['Modularidade', 'Densidade', 'N. Comunidades',
                  'Entropia Geográfica', 'PageRank CV', 'Razão Intra/Inter']
    N = len(categories)

    # Ângulos para cada eixo
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]  # Fechar o círculo

    # Criar figura
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

    # Plotar cada rede
    for i, (values, color, label) in enumerate(zip(data, colors, legend_labels)):
        values = list(values)
        values += values[:1]  # Fechar o polígono

        ax.plot(angles, values, 'o-', linewidth=2, color=color, label=label, alpha=0.8)
        ax.fill(angles, values, alpha=0.15, color=color)

    # Configurar eixos
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=11, weight='bold')
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], size=9, color='gray')
    ax.grid(True, linestyle='--', alpha=0.5)

    # Título e legenda
    plt.title(title, size=14, weight='bold', pad=30)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    print(f"✓ Radar chart salvo: {filename}")
    plt.close()

def main():
    print("\n" + "="*60)
    print("GERANDO RADAR CHARTS DE REDES COMPETITIVAS")
    print("="*60 + "\n")

    # Carregar métricas
    print("1. Carregando métricas das 16 redes...")
    metrics_df = load_network_metrics()
    print(f"   ✓ {len(metrics_df)} redes carregadas")

    # Normalizar
    print("\n2. Normalizando métricas (min-max 0-1)...")
    metrics_norm = normalize_metrics(metrics_df)
    print("   ✓ Normalização concluída")

    # ========================================
    # RADAR 1: Esportes Mistos (8 redes)
    # ========================================
    print("\n3. Gerando Radar 1: Esportes Mistos (8 redes)...")

    mixed_sports = metrics_norm[metrics_norm['type_label'] == 'Misto'].copy()

    # Preparar dados
    radar1_data = []
    radar1_labels = []
    radar1_colors = []

    # Cores DISTINTAS para cada rede (8 cores bem diferentes)
    color_map = {
        'Swimming': {
            'individual': {'M': '#1f77b4', 'F': '#9467bd'},  # Azul forte, Roxo
            'team': {'M': '#ff7f0e', 'F': '#e377c2'}         # Laranja, Rosa
        },
        'Athletics': {
            'individual': {'M': '#2ca02c', 'F': '#17becf'},  # Verde, Ciano
            'team': {'M': '#d62728', 'F': '#bcbd22'}         # Vermelho, Amarelo-esverdeado
        }
    }

    for idx, row in mixed_sports.iterrows():
        values = [
            row['modularity_norm'],
            row['density_norm'],
            row['n_communities_norm'],
            row['geo_entropy_norm'],
            row['pagerank_cv_norm'],
            row['intra_inter_ratio_norm']
        ]
        radar1_data.append(values)

        # Label: Sport + Type + Sex
        type_short = 'Ind.' if row['event_type'] == 'individual' else 'Rev.'
        label = f"{row['sport']} {type_short} {row['sex']}"
        radar1_labels.append(label)

        # Cor (agora inclui sexo para 8 cores distintas)
        radar1_colors.append(color_map[row['sport']][row['event_type']][row['sex']])

    create_radar_chart(
        data=radar1_data,
        labels=radar1_labels,
        title='Perfis Estruturais de Esportes Mistos\n(Swimming e Athletics)',
        filename='fig_radar_mixed_sports.png',
        colors=radar1_colors,
        legend_labels=radar1_labels
    )

    # ========================================
    # RADAR 2: Comparação Tipológica (3 perfis)
    # ========================================
    print("\n4. Gerando Radar 2: Comparação Tipológica (3 perfis)...")

    # Calcular médias por tipo
    type_avg = metrics_norm.groupby('type_label').agg({
        'modularity_norm': 'mean',
        'density_norm': 'mean',
        'n_communities_norm': 'mean',
        'geo_entropy_norm': 'mean',
        'pagerank_cv_norm': 'mean',
        'intra_inter_ratio_norm': 'mean'
    }).reset_index()

    radar2_data = []
    radar2_labels = []
    radar2_colors = {'Misto': '#1f77b4', 'Coletivo': '#2ca02c', 'Individual': '#d62728'}

    for idx, row in type_avg.iterrows():
        values = [
            row['modularity_norm'],
            row['density_norm'],
            row['n_communities_norm'],
            row['geo_entropy_norm'],
            row['pagerank_cv_norm'],
            row['intra_inter_ratio_norm']
        ]
        radar2_data.append(values)
        radar2_labels.append(f"Esportes {row['type_label']}s")

    create_radar_chart(
        data=radar2_data,
        labels=radar2_labels,
        title='Comparação Tipológica de Redes Competitivas\n(Perfis Médios)',
        filename='fig_radar_typology.png',
        colors=[radar2_colors['Misto'], radar2_colors['Coletivo'], radar2_colors['Individual']],
        legend_labels=radar2_labels
    )

    print("\n" + "="*60)
    print("✓ RADAR CHARTS GERADOS COM SUCESSO!")
    print("="*60)
    print(f"\nArquivos salvos em: {OUTPUT_DIR}")
    print("  - fig_radar_mixed_sports.png")
    print("  - fig_radar_typology.png\n")

if __name__ == "__main__":
    main()
