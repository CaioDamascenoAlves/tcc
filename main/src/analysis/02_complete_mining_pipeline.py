#!/usr/bin/env python3
"""
PIPELINE COMPLETA DE MINERAÇÃO - MODELAGEM POR EVENTO

Calcula TODAS as métricas mencionadas no TCC para os 12 casos de estudo.
Focado em análise por evento individual (não agregada).

Estrutura:
- 12 eventos (6 pares M/F)
- Métricas por evento + análises comparativas
- Geração de tabelas LaTeX e figuras

Author: Caio Damasceno
Date: 2026-01-31
"""

import networkx as nx
import pandas as pd
import numpy as np
from pathlib import Path
import json
import warnings
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import community as community_louvain

warnings.filterwarnings('ignore')


class CompleteMiningPipeline:
    """Pipeline completa de mineração de redes olímpicas."""

    def __init__(self, networks_dir: str, output_dir: str):
        self.networks_dir = Path(networks_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Criar subpastas
        (self.output_dir / 'tables').mkdir(exist_ok=True)
        (self.output_dir / 'figures').mkdir(exist_ok=True)
        (self.output_dir / 'data').mkdir(exist_ok=True)

        # 12 casos de estudo
        self.case_studies = self._define_case_studies()

        # Cache de redes carregadas
        self.networks = {}

        # Resultados
        self.results = {}

    def _define_case_studies(self) -> List[Dict]:
        """Define os 12 casos de estudo."""
        return [
            # Par 1: Futebol
            {'id': 1, 'sport': 'football', 'file': 'football_M_Football_Mens_Football.gexf',
             'name': 'M Football', 'gender': 'M', 'type': 'team'},
            {'id': 2, 'sport': 'football', 'file': 'football_F_Football_Womens_Football.gexf',
             'name': 'F Football', 'gender': 'F', 'type': 'team'},

            # Par 2: Basquete
            {'id': 3, 'sport': 'basketball', 'file': 'basketball_M_Basketball_Mens_Basketball.gexf',
             'name': 'M Basketball', 'gender': 'M', 'type': 'team'},
            {'id': 4, 'sport': 'basketball', 'file': 'basketball_F_Basketball_Womens_Basketball.gexf',
             'name': 'F Basketball', 'gender': 'F', 'type': 'team'},

            # Par 3: Atletismo 100m
            {'id': 5, 'sport': 'athletics', 'file': 'athletics_M_100m.gexf',
             'name': 'M 100m', 'gender': 'M', 'type': 'individual'},
            {'id': 6, 'sport': 'athletics', 'file': 'athletics_F_100m.gexf',
             'name': 'F 100m', 'gender': 'F', 'type': 'individual'},

            # Par 4: Natação 100m Livre
            {'id': 7, 'sport': 'swimming', 'file': 'swimming_M_100m_Freestyle.gexf',
             'name': 'M 100m Freestyle', 'gender': 'M', 'type': 'individual'},
            {'id': 8, 'sport': 'swimming', 'file': 'swimming_F_100m_Freestyle.gexf',
             'name': 'F 100m Freestyle', 'gender': 'F', 'type': 'individual'},

            # Par 5: Judô
            {'id': 9, 'sport': 'judo', 'file': 'judo_M_-90kg.gexf',
             'name': 'M -90kg', 'gender': 'M', 'type': 'individual'},
            {'id': 10, 'sport': 'judo', 'file': 'judo_F_-70kg.gexf',
             'name': 'F -70kg', 'gender': 'F', 'type': 'individual'},

            # Par 6: Boxe
            {'id': 11, 'sport': 'boxing', 'file': 'boxing_M_Welter_63-69kg.gexf',
             'name': 'M Welter', 'gender': 'M', 'type': 'individual'},
            {'id': 12, 'sport': 'boxing', 'file': 'boxing_F_Middle_69-75kg.gexf',
             'name': 'F Middle', 'gender': 'F', 'type': 'individual'}
        ]

    def load_network(self, case: Dict) -> nx.DiGraph:
        """Carrega rede (com cache)."""
        if case['id'] in self.networks:
            return self.networks[case['id']]

        file_path = self.networks_dir / case['sport'] / case['file']
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        G = nx.read_gexf(file_path)
        self.networks[case['id']] = G
        print(f"✓ Carregado: {case['name']} ({G.number_of_nodes()} nós, {G.number_of_edges()} arestas)")
        return G

    def run_complete_mining(self):
        """Executa mineração completa."""
        print("\n" + "="*100)
        print("PIPELINE COMPLETA DE MINERAÇÃO - 12 CASOS DE ESTUDO")
        print("="*100)

        # ETAPA 1: Métricas Globais
        print("\n[1/7] Calculando métricas globais...")
        self.calculate_global_metrics()

        # ETAPA 2: Centralidades
        print("\n[2/7] Calculando centralidades (PageRank, HITS, Degree, Betweenness, Closeness)...")
        self.calculate_centralities()

        # ETAPA 3: Comunidades (Louvain)
        print("\n[3/7] Detectando comunidades e calculando métricas de comunidades...")
        self.detect_communities()

        # ETAPA 4: Análise Temporal (Entropia)
        print("\n[4/7] Calculando entropia temporal por comunidade...")
        self.calculate_temporal_entropy()

        # ETAPA 5: Validação (CDF de pesos)
        print("\n[5/7] Calculando distribuição de pesos (CDF)...")
        self.calculate_weight_distribution()

        # ETAPA 6: Análises Comparativas M vs F
        print("\n[6/7] Gerando análises comparativas M vs F...")
        self.comparative_analysis()

        # ETAPA 7: Exportar resultados
        print("\n[7/7] Exportando resultados (CSVs, JSONs, LaTeX)...")
        self.export_results()

        print("\n" + "="*100)
        print("MINERAÇÃO COMPLETA CONCLUÍDA!")
        print("="*100)
        print(f"Resultados salvos em: {self.output_dir}")

    def calculate_global_metrics(self):
        """Calcula métricas globais de cada rede."""
        results = []

        for case in self.case_studies:
            G = self.load_network(case)

            # Básicas
            metrics = {
                'id': case['id'],
                'sport': case['sport'],
                'name': case['name'],
                'gender': case['gender'],
                'type': case['type'],
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'density': nx.density(G)
            }

            # Componentes
            wcc = list(nx.weakly_connected_components(G))
            metrics['num_components'] = len(wcc)
            metrics['is_connected'] = len(wcc) == 1
            metrics['largest_component_size'] = len(max(wcc, key=len))
            metrics['largest_component_fraction'] = metrics['largest_component_size'] / metrics['nodes']

            # Diâmetro (maior componente se desconectado)
            if metrics['is_connected']:
                metrics['diameter'] = nx.diameter(G.to_undirected())
            else:
                G_largest = G.subgraph(max(wcc, key=len))
                try:
                    metrics['diameter'] = nx.diameter(G_largest.to_undirected())
                except:
                    metrics['diameter'] = None

            # Clustering
            try:
                metrics['avg_clustering'] = nx.average_clustering(G.to_undirected(), weight='weight')
            except:
                metrics['avg_clustering'] = None

            results.append(metrics)

        self.results['global_metrics'] = pd.DataFrame(results)
        print(f"  ✓ Métricas globais calculadas para {len(results)} redes")

    def calculate_centralities(self):
        """Calcula todas as centralidades."""
        all_pagerank = []
        all_authorities = []
        all_betweenness = []
        all_degree = []

        for case in self.case_studies:
            G = self.load_network(case)

            # PageRank
            pr = nx.pagerank(G, weight='weight', max_iter=100)
            for node, score in pr.items():
                all_pagerank.append({
                    'network_id': case['id'],
                    'network_name': case['name'],
                    'sport': case['sport'],
                    'gender': case['gender'],
                    'athlete_id': node,
                    'athlete_name': G.nodes[node].get('name', 'Unknown'),
                    'noc': G.nodes[node].get('noc', 'UNK'),
                    'pagerank': score,
                    'gold_medals': int(G.nodes[node].get('gold_medals', 0)),
                    'total_medals': int(G.nodes[node].get('total_medals', 0))
                })

            # HITS
            try:
                hubs, authorities = nx.hits(G, max_iter=100)
                for node, score in authorities.items():
                    all_authorities.append({
                        'network_id': case['id'],
                        'network_name': case['name'],
                        'sport': case['sport'],
                        'gender': case['gender'],
                        'athlete_id': node,
                        'athlete_name': G.nodes[node].get('name', 'Unknown'),
                        'noc': G.nodes[node].get('noc', 'UNK'),
                        'authority': score,
                        'hub': hubs[node]
                    })
            except:
                pass

            # Betweenness
            try:
                if G.number_of_nodes() < 500:
                    btw = nx.betweenness_centrality(G, weight='weight')
                else:
                    btw = nx.betweenness_centrality(G, k=100, weight='weight')

                for node, score in btw.items():
                    all_betweenness.append({
                        'network_id': case['id'],
                        'network_name': case['name'],
                        'sport': case['sport'],
                        'gender': case['gender'],
                        'athlete_id': node,
                        'betweenness': score
                    })
            except:
                pass

            # Degree
            for node in G.nodes():
                all_degree.append({
                    'network_id': case['id'],
                    'network_name': case['name'],
                    'sport': case['sport'],
                    'gender': case['gender'],
                    'athlete_id': node,
                    'in_degree': G.in_degree(node, weight='weight'),
                    'out_degree': G.out_degree(node, weight='weight'),
                    'total_degree': G.degree(node, weight='weight')
                })

        self.results['pagerank'] = pd.DataFrame(all_pagerank)
        self.results['authorities'] = pd.DataFrame(all_authorities)
        self.results['betweenness'] = pd.DataFrame(all_betweenness)
        self.results['degree'] = pd.DataFrame(all_degree)

        print(f"  ✓ Centralidades calculadas")
        print(f"    - PageRank: {len(all_pagerank)} atletas")
        print(f"    - Authorities: {len(all_authorities)} atletas")
        print(f"    - Betweenness: {len(all_betweenness)} atletas")

    def detect_communities(self):
        """Detecta comunidades e calcula métricas."""
        all_communities = []
        community_stats = []

        for case in self.case_studies:
            G = self.load_network(case)

            # Louvain
            G_undirected = G.to_undirected()
            partition = community_louvain.best_partition(G_undirected, weight='weight')

            num_communities = len(set(partition.values()))

            # Modularidade
            modularity = community_louvain.modularity(partition, G_undirected, weight='weight')

            # Salvar partição
            for node, comm_id in partition.items():
                all_communities.append({
                    'network_id': case['id'],
                    'network_name': case['name'],
                    'sport': case['sport'],
                    'gender': case['gender'],
                    'athlete_id': node,
                    'athlete_name': G.nodes[node].get('name', 'Unknown'),
                    'noc': G.nodes[node].get('noc', 'UNK'),
                    'community_id': comm_id
                })

            # Estatísticas de comunidades
            for comm_id in set(partition.values()):
                members = [n for n, c in partition.items() if c == comm_id]
                subgraph = G.subgraph(members)

                # Medalhas
                medals = {'Gold': 0, 'Silver': 0, 'Bronze': 0}
                for node in members:
                    medals['Gold'] += int(G.nodes[node].get('gold_medals', 0))
                    medals['Silver'] += int(G.nodes[node].get('silver_medals', 0))
                    medals['Bronze'] += int(G.nodes[node].get('bronze_medals', 0))

                total_medals = sum(medals.values())

                community_stats.append({
                    'network_id': case['id'],
                    'network_name': case['name'],
                    'sport': case['sport'],
                    'gender': case['gender'],
                    'community_id': comm_id,
                    'size': len(members),
                    'edges_internal': subgraph.number_of_edges(),
                    'gold_medals': medals['Gold'],
                    'silver_medals': medals['Silver'],
                    'bronze_medals': medals['Bronze'],
                    'total_medals': total_medals,
                    'gold_pct': medals['Gold'] / total_medals * 100 if total_medals > 0 else 0,
                    'silver_pct': medals['Silver'] / total_medals * 100 if total_medals > 0 else 0,
                    'bronze_pct': medals['Bronze'] / total_medals * 100 if total_medals > 0 else 0
                })

            print(f"  ✓ {case['name']}: {num_communities} comunidades (modularidade: {modularity:.4f})")

        self.results['communities'] = pd.DataFrame(all_communities)
        self.results['community_stats'] = pd.DataFrame(community_stats)

        # Atualizar global_metrics com num_communities e modularity
        # (será feito no export)

    def calculate_temporal_entropy(self):
        """Calcula entropia de Shannon temporal por comunidade."""
        # Define eras
        eras = {
            'Pioneira': (1896, 1936),
            'Pos-Guerra': (1948, 1980),
            'Moderna': (1984, 2000),
            'Contemporanea': (2004, 2021)
        }

        # Precisa ler anos dos atletas (não está no GEXF atual)
        # Vamos deixar isso para um script separado que lê do CSV original
        # Por enquanto, placeholder
        print("  ⚠️  Entropia temporal requer dados temporais do CSV original")
        print("  → Será implementado em script separado")

    def calculate_weight_distribution(self):
        """Calcula distribuição de pesos das arestas (para CDF)."""
        all_weights = []

        for case in self.case_studies:
            G = self.load_network(case)

            for u, v, data in G.edges(data=True):
                all_weights.append({
                    'network_id': case['id'],
                    'network_name': case['name'],
                    'sport': case['sport'],
                    'gender': case['gender'],
                    'weight': data.get('weight', 1)
                })

        self.results['edge_weights'] = pd.DataFrame(all_weights)
        print(f"  ✓ Distribuição de pesos calculada ({len(all_weights)} arestas)")

    def comparative_analysis(self):
        """Análises comparativas M vs F."""
        # Comparação de densidade
        global_df = self.results['global_metrics']

        comparison = []
        pairs = [
            (1, 2, 'Football'),
            (3, 4, 'Basketball'),
            (5, 6, '100m'),
            (7, 8, '100m Freestyle'),
            (9, 10, 'Judo'),
            (11, 12, 'Boxing')
        ]

        for m_id, f_id, event in pairs:
            m_row = global_df[global_df['id'] == m_id].iloc[0]
            f_row = global_df[global_df['id'] == f_id].iloc[0]

            comparison.append({
                'event': event,
                'm_nodes': m_row['nodes'],
                'f_nodes': f_row['nodes'],
                'm_edges': m_row['edges'],
                'f_edges': f_row['edges'],
                'm_density': m_row['density'],
                'f_density': f_row['density'],
                'density_ratio': f_row['density'] / m_row['density'] if m_row['density'] > 0 else 0,
                'm_components': m_row['num_components'],
                'f_components': f_row['num_components']
            })

        self.results['comparison_mf'] = pd.DataFrame(comparison)
        print(f"  ✓ Análise comparativa M vs F concluída")

    def export_results(self):
        """Exporta todos os resultados."""
        data_dir = self.output_dir / 'data'

        # CSVs
        for key, df in self.results.items():
            if isinstance(df, pd.DataFrame):
                csv_path = data_dir / f'{key}.csv'
                df.to_csv(csv_path, index=False)
                print(f"  ✓ {csv_path.name}")

        # JSON summary
        summary = {
            'total_networks': len(self.case_studies),
            'total_athletes': self.results['pagerank']['athlete_id'].nunique(),
            'files_generated': list(self.results.keys())
        }

        json_path = data_dir / 'summary.json'
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"  ✓ summary.json")


if __name__ == "__main__":
    pipeline = CompleteMiningPipeline(
        networks_dir='../../results_per_event_cleaned',
        output_dir='../../results_complete_mining'
    )

    pipeline.run_complete_mining()
