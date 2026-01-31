#!/usr/bin/env python3
"""
Geração de Redes Bipartidas por Esporte e Sexo

MODELAGEM:
- Uma rede separada para cada (Esporte, Sexo)
- Dois tipos de nós: Atletas e Pódios
- Arestas não-direcionadas: Atleta ↔ Pódio (ponderadas por medalha)
- Peso: Gold=5, Silver=3, Bronze=2

VANTAGENS:
- Zero fragmentação em cada rede (totalmente conectada)
- HITS funciona corretamente
- Comparação M vs F possível
- Metodologicamente correto

REDES GERADAS (12 total):
- Swimming M/F, Basketball M/F, Football M/F
- Athletics M/F, Judo M/F, Boxing M/F
"""

import pandas as pd
import networkx as nx
import numpy as np
import os
import json
from collections import Counter

# Pesos por tipo de medalha
MEDAL_WEIGHTS = {'Gold': 5, 'Silver': 3, 'Bronze': 2}


def load_data(data_path, selected_sports):
    """Carrega e limpa os dados."""
    print("="*80)
    print("CARREGANDO DADOS")
    print("="*80)

    df = pd.read_csv(data_path)
    print(f"Total de registros: {len(df):,}")

    # Filtrar esportes e medalhistas
    df = df[(df['Sport'].isin(selected_sports)) & df['Medal'].notna()]
    print(f"Medalhistas selecionados: {len(df):,}")

    # Remover duplicatas
    df = df.drop_duplicates(subset=['Year', 'Sport', 'Event', 'Sex', 'Medal', 'ID'])
    print(f"[OK] Dados limpos: {len(df):,} registros, {df['ID'].nunique():,} atletas\n")

    return df


def create_bipartite_network(sport_data, sport_name, sex):
    """Cria rede bipartida para um esporte/sexo específico."""
    G = nx.Graph()

    # Agregar dados de atletas
    athlete_agg = sport_data.groupby('ID').agg({
        'Name': 'first',
        'NOC': 'first',
        'Team': 'first',
        'Medal': lambda x: {
            'Gold': (x == 'Gold').sum(),
            'Silver': (x == 'Silver').sum(),
            'Bronze': (x == 'Bronze').sum()
        }
    }).reset_index()

    # Adicionar nós de atletas
    for _, row in athlete_agg.iterrows():
        medals = row['Medal']
        G.add_node(
            f"athlete_{row['ID']}",
            bipartite=0,
            node_type='athlete',
            athlete_id=row['ID'],
            name=row['Name'],
            noc=row['NOC'],
            team=row['Team'],
            gold=medals['Gold'],
            silver=medals['Silver'],
            bronze=medals['Bronze'],
            total=medals['Gold'] + medals['Silver'] + medals['Bronze']
        )

    # Agregar pódios
    podium_agg = sport_data.groupby(['Year', 'Event']).agg({
        'City': 'first',
        'Games': 'first',
        'ID': 'nunique'
    }).reset_index()

    # Adicionar nós de pódios
    for _, row in podium_agg.iterrows():
        podium_id = f"podium_{row['Year']}_{row['Event']}"
        podium_id = ''.join(c if c.isalnum() or c == '_' else '_' for c in podium_id)

        G.add_node(
            podium_id,
            bipartite=1,
            node_type='podium',
            year=row['Year'],
            event=row['Event'],
            city=row['City'],
            games=row['Games'],
            num_athletes=row['ID']
        )

    # Adicionar arestas Atleta ↔ Pódio
    for _, row in sport_data.iterrows():
        athlete_node = f"athlete_{row['ID']}"
        podium_id = f"podium_{row['Year']}_{row['Event']}"
        podium_id = ''.join(c if c.isalnum() or c == '_' else '_' for c in podium_id)

        weight = MEDAL_WEIGHTS.get(row['Medal'], 1)

        G.add_edge(
            athlete_node,
            podium_id,
            medal=row['Medal'],
            weight=weight
        )

    return G


def calculate_metrics(G):
    """Calcula métricas da rede bipartida."""
    # Limpar valores None/NaN para evitar erros
    for node in G.nodes():
        for key, value in G.nodes[node].items():
            if value is None or (isinstance(value, float) and np.isnan(value)):
                G.nodes[node][key] = '' if isinstance(value, str) else 0

    metrics = {}

    # HITS
    try:
        hubs, authorities = nx.hits(G, max_iter=1000, normalized=True)
        metrics['hubs'] = hubs
        metrics['authorities'] = authorities
    except:
        metrics['hubs'] = {n: 0 for n in G.nodes()}
        metrics['authorities'] = {n: 0 for n in G.nodes()}

    # PageRank
    metrics['pagerank'] = nx.pagerank(G, weight='weight', max_iter=1000)

    # Degree
    metrics['degree'] = dict(G.degree())
    metrics['degree_weighted'] = dict(G.degree(weight='weight'))

    # Betweenness
    metrics['betweenness'] = nx.betweenness_centrality(G, weight='weight')

    # Closeness
    metrics['closeness'] = nx.closeness_centrality(G)

    # Entropia de Shannon (medalhas)
    metrics['entropy'] = {}
    for node, data in G.nodes(data=True):
        if data.get('bipartite') == 0:  # Atletas
            g = data.get('gold', 0)
            s = data.get('silver', 0)
            b = data.get('bronze', 0)
            total = g + s + b

            if total > 0:
                H = 0
                for count in [g, s, b]:
                    if count > 0:
                        p = count / total
                        H -= p * np.log2(p)
                metrics['entropy'][node] = H
            else:
                metrics['entropy'][node] = 0

    return metrics


def export_results(G, metrics, sport_name, sex, output_dir):
    """Exporta rede e métricas."""
    os.makedirs(output_dir, exist_ok=True)

    # Salvar GEXF
    gexf_file = os.path.join(output_dir, f"{sport_name.lower()}_{sex}_bipartite.gexf")
    nx.write_gexf(G, gexf_file)

    # Extrair métricas de atletas
    athlete_nodes = [n for n, d in G.nodes(data=True) if d.get('bipartite') == 0]

    athlete_rows = []
    for node in athlete_nodes:
        data = G.nodes[node]
        row = {
            'athlete_id': data.get('athlete_id'),
            'name': data.get('name'),
            'noc': data.get('noc'),
            'gold': data.get('gold', 0),
            'silver': data.get('silver', 0),
            'bronze': data.get('bronze', 0),
            'total': data.get('total', 0),
            'authority': metrics['authorities'].get(node, 0),
            'pagerank': metrics['pagerank'].get(node, 0),
            'degree': metrics['degree'].get(node, 0),
            'degree_weighted': metrics['degree_weighted'].get(node, 0),
            'betweenness': metrics['betweenness'].get(node, 0),
            'closeness': metrics['closeness'].get(node, 0),
            'entropy': metrics['entropy'].get(node, 0)
        }
        athlete_rows.append(row)

    df_athletes = pd.DataFrame(athlete_rows)

    # Score de dominância composto
    if len(df_athletes) > 0 and df_athletes['degree_weighted'].max() > 0:
        df_athletes['dominance_score'] = (
            0.4 * df_athletes['authority'] +
            0.3 * df_athletes['degree_weighted'] / df_athletes['degree_weighted'].max() +
            0.2 * (df_athletes['gold'] / (df_athletes['total'] + 1)) +
            0.1 * (1 - df_athletes['entropy'] / np.log2(3))
        )

    # Salvar CSV
    csv_file = os.path.join(output_dir, f"{sport_name.lower()}_{sex}_athletes.csv")
    df_athletes.to_csv(csv_file, index=False)

    # Métricas de pódios
    podium_nodes = [n for n, d in G.nodes(data=True) if d.get('bipartite') == 1]

    podium_rows = []
    for node in podium_nodes:
        data = G.nodes[node]
        row = {
            'podium_id': node,
            'year': data.get('year'),
            'event': data.get('event'),
            'num_athletes': data.get('num_athletes', 0),
            'hub': metrics['hubs'].get(node, 0),
            'pagerank': metrics['pagerank'].get(node, 0),
            'degree': metrics['degree'].get(node, 0),
            'betweenness': metrics['betweenness'].get(node, 0)
        }
        podium_rows.append(row)

    df_podiums = pd.DataFrame(podium_rows)
    podium_csv = os.path.join(output_dir, f"{sport_name.lower()}_{sex}_podiums.csv")
    df_podiums.to_csv(podium_csv, index=False)

    # Resumo
    summary = {
        'sport': sport_name,
        'sex': sex,
        'nodes_total': G.number_of_nodes(),
        'nodes_athletes': len(athlete_nodes),
        'nodes_podiums': len(podium_nodes),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'components': nx.number_connected_components(G),
        'is_connected': nx.is_connected(G),
        'top_5_authority': df_athletes.nlargest(5, 'authority')[['name', 'authority', 'gold']].to_dict('records') if len(df_athletes) > 0 else []
    }

    return summary, df_athletes, df_podiums


def main():
    """Pipeline completo."""
    DATA_PATH = '../../data/athlete_events.csv'
    SELECTED_SPORTS = ['Swimming', 'Basketball', 'Football', 'Athletics', 'Judo', 'Boxing']
    OUTPUT_DIR = '../../results_bipartite'

    # Carregar dados
    df = load_data(DATA_PATH, SELECTED_SPORTS)

    all_summaries = []

    print("="*80)
    print("GERANDO REDES BIPARTIDAS POR ESPORTE E SEXO")
    print("="*80)

    for sport in SELECTED_SPORTS:
        print(f"\n--- {sport} ---")

        for sex in ['M', 'F']:
            sport_sex_data = df[(df['Sport'] == sport) & (df['Sex'] == sex)]

            if len(sport_sex_data) == 0:
                print(f"  {sport} {sex}: Sem dados")
                continue

            print(f"  {sport} {sex}: {len(sport_sex_data)} registros, {sport_sex_data['ID'].nunique()} atletas")

            # Criar rede
            G = create_bipartite_network(sport_sex_data, sport, sex)

            # Calcular métricas
            metrics = calculate_metrics(G)

            # Exportar
            summary, df_athletes, df_podiums = export_results(G, metrics, sport, sex, OUTPUT_DIR)
            all_summaries.append(summary)

            # Print status
            status = "✅ CONECTADA" if summary['is_connected'] else f"⚠️  {summary['components']} componentes"
            print(f"    → {summary['nodes_athletes']} atletas, {summary['nodes_podiums']} pódios, {summary['edges']} arestas [{status}]")

            # Top 3
            if len(df_athletes) > 0:
                top3 = df_athletes.nlargest(3, 'authority')[['name', 'authority']]
                print(f"    → Top 3 Authority: {', '.join(top3['name'].tolist())}")

    # Salvar resumo consolidado
    summary_file = os.path.join(OUTPUT_DIR, 'all_networks_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(all_summaries, f, indent=4, default=str)

    print(f"\n{'='*80}")
    print("ANÁLISE CONCLUÍDA!")
    print("="*80)
    print(f"Total de redes geradas: {len(all_summaries)}")
    print(f"Resultados em: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
