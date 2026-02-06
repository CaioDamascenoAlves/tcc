#!/usr/bin/env python3
"""
Análise de Resiliência e Robustez das Redes

Simula remoção de nós para avaliar:
1. Resiliência a remoção aleatória vs. dirigida (high PageRank)
2. Impacto na conectividade (componentes)
3. Impacto na coesão (clustering)
4. Identificação de atletas críticos (single point of failure)
"""

import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path
from collections import defaultdict

class NetworkResilienceAnalyzer:
    """Análise de resiliência de redes."""

    def __init__(self, networks_dir: str, pagerank_path: str, output_dir: str):
        self.networks_dir = Path(networks_dir)
        self.pagerank_path = Path(pagerank_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 12 casos
        self.case_studies = self._define_cases()

    def _define_cases(self):
        """Define casos de estudo."""
        return [
            {'id': 1, 'sport': 'Football', 'event': 'M Football', 'file': 'football_M_Football_Mens_Football.gexf'},
            {'id': 2, 'sport': 'Football', 'event': 'F Football', 'file': 'football_F_Football_Womens_Football.gexf'},
            {'id': 3, 'sport': 'Basketball', 'event': 'M Basketball', 'file': 'basketball_M_Basketball_Mens_Basketball.gexf'},
            {'id': 4, 'sport': 'Basketball', 'event': 'F Basketball', 'file': 'basketball_F_Basketball_Womens_Basketball.gexf'},
            {'id': 5, 'sport': 'Athletics', 'event': 'M 100m', 'file': 'athletics_M_100m.gexf'},
            {'id': 6, 'sport': 'Athletics', 'event': 'F 100m', 'file': 'athletics_F_100m.gexf'},
            {'id': 7, 'sport': 'Swimming', 'event': 'M 100m Free', 'file': 'swimming_M_100m_Freestyle.gexf'},
            {'id': 8, 'sport': 'Swimming', 'event': 'F 100m Free', 'file': 'swimming_F_100m_Freestyle.gexf'},
            {'id': 9, 'sport': 'Judo', 'event': 'M -90kg', 'file': 'judo_M_-90kg.gexf'},
            {'id': 10, 'sport': 'Judo', 'event': 'F -70kg', 'file': 'judo_F_-70kg.gexf'},
            {'id': 11, 'sport': 'Boxing', 'event': 'M Welter', 'file': 'boxing_M_Welter_63-69kg.gexf'},
            {'id': 12, 'sport': 'Boxing', 'event': 'F Middle', 'file': 'boxing_F_Middle_69-75kg.gexf'}
        ]

    def load_data(self):
        """Carrega dados."""
        print("Carregando dados...")

        self.pagerank = pd.read_csv(self.pagerank_path)

        print(f"  ✓ PageRank carregado para {len(self.pagerank):,} atletas")

    def simulate_node_removal(self, G: nx.DiGraph, removal_strategy: str,
                              removal_fraction: float = 0.1) -> dict:
        """Simula remoção de nós e mede impacto.

        Args:
            G: Grafo original
            removal_strategy: 'random' ou 'targeted' (high PageRank)
            removal_fraction: Fração de nós a remover (default 10%)

        Returns:
            Dicionário com métricas antes/depois
        """
        # Métricas originais
        original_nodes = G.number_of_nodes()
        original_edges = G.number_of_edges()
        original_components = nx.number_weakly_connected_components(G)
        original_largest_cc = len(max(nx.weakly_connected_components(G), key=len))
        original_largest_cc_pct = original_largest_cc / original_nodes * 100

        # Calcular clustering (pode ser lento em redes grandes)
        if original_nodes < 500:
            # Converter para grafo não-direcionado para clustering
            G_undirected = G.to_undirected()
            original_clustering = nx.average_clustering(G_undirected)
        else:
            original_clustering = None

        # Selecionar nós para remover
        num_to_remove = int(original_nodes * removal_fraction)

        if removal_strategy == 'random':
            # Remoção aleatória
            nodes_to_remove = np.random.choice(list(G.nodes()), size=num_to_remove, replace=False)
        else:
            # Remoção dirigida (high degree ou PageRank)
            # Usar degree como proxy se PageRank não disponível
            degrees = dict(G.degree())
            sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
            nodes_to_remove = [n for n, d in sorted_nodes[:num_to_remove]]

        # Criar cópia e remover nós
        G_modified = G.copy()
        G_modified.remove_nodes_from(nodes_to_remove)

        # Métricas após remoção
        modified_nodes = G_modified.number_of_nodes()
        modified_edges = G_modified.number_of_edges()
        modified_components = nx.number_weakly_connected_components(G_modified)

        if modified_nodes > 0:
            modified_largest_cc = len(max(nx.weakly_connected_components(G_modified), key=len))
            modified_largest_cc_pct = modified_largest_cc / modified_nodes * 100
        else:
            modified_largest_cc = 0
            modified_largest_cc_pct = 0

        if modified_nodes < 500 and modified_nodes > 0:
            G_undirected = G_modified.to_undirected()
            modified_clustering = nx.average_clustering(G_undirected)
        else:
            modified_clustering = None

        return {
            'removal_strategy': removal_strategy,
            'removal_fraction': removal_fraction,
            'nodes_removed': num_to_remove,
            'original_nodes': original_nodes,
            'original_edges': original_edges,
            'original_components': original_components,
            'original_largest_cc_pct': original_largest_cc_pct,
            'original_clustering': original_clustering,
            'modified_nodes': modified_nodes,
            'modified_edges': modified_edges,
            'modified_components': modified_components,
            'modified_largest_cc_pct': modified_largest_cc_pct,
            'modified_clustering': modified_clustering,
            'component_increase': modified_components - original_components,
            'largest_cc_decrease': original_largest_cc_pct - modified_largest_cc_pct
        }

    def analyze_resilience(self):
        """Analisa resiliência por remoção de nós."""
        print("\nAnalisando resiliência das redes...")

        results = []

        for case in self.case_studies:
            file_path = self.networks_dir / case['sport'].lower() / case['file']

            if not file_path.exists():
                print(f"  ⚠️  Rede não encontrada: {file_path}")
                continue

            G = nx.read_gexf(file_path)

            # Testar múltiplas frações de remoção
            fractions = [0.05, 0.10, 0.20]

            for fraction in fractions:
                # Remoção aleatória
                random_result = self.simulate_node_removal(G, 'random', fraction)
                random_result.update({
                    'network_id': case['id'],
                    'sport': case['sport'],
                    'event': case['event']
                })
                results.append(random_result)

                # Remoção dirigida
                targeted_result = self.simulate_node_removal(G, 'targeted', fraction)
                targeted_result.update({
                    'network_id': case['id'],
                    'sport': case['sport'],
                    'event': case['event']
                })
                results.append(targeted_result)

            print(f"  ✓ {case['event']}")

        self.resilience_results = pd.DataFrame(results)

        # Comparar random vs targeted
        print("\n  Impacto médio da remoção de 10% dos nós:")
        for strategy in ['random', 'targeted']:
            strategy_data = self.resilience_results[
                (self.resilience_results['removal_strategy'] == strategy) &
                (self.resilience_results['removal_fraction'] == 0.10)
            ]
            if len(strategy_data) > 0:
                mean_component_increase = strategy_data['component_increase'].mean()
                mean_cc_decrease = strategy_data['largest_cc_decrease'].mean()
                print(f"    {strategy.capitalize()}: +{mean_component_increase:.1f} componentes, "
                      f"-{mean_cc_decrease:.1f}% maior CC")

    def identify_critical_nodes(self):
        """Identifica nós críticos (articulação)."""
        print("\nIdentificando nós críticos...")

        results = []

        for case in self.case_studies:
            file_path = self.networks_dir / case['sport'].lower() / case['file']

            if not file_path.exists():
                continue

            G = nx.read_gexf(file_path)

            # Converter para não-direcionado para encontrar pontos de articulação
            G_undirected = G.to_undirected()

            # Pontos de articulação (cuja remoção aumenta o número de componentes)
            if nx.is_connected(G_undirected):
                articulation_points = list(nx.articulation_points(G_undirected))
            else:
                # Para grafos desconectados, encontrar em cada componente
                articulation_points = []
                for component in nx.connected_components(G_undirected):
                    subgraph = G_undirected.subgraph(component)
                    if len(subgraph) > 1:
                        articulation_points.extend(nx.articulation_points(subgraph))

            num_critical = len(articulation_points)
            critical_pct = num_critical / G.number_of_nodes() * 100 if G.number_of_nodes() > 0 else 0

            results.append({
                'network_id': case['id'],
                'sport': case['sport'],
                'event': case['event'],
                'num_critical_nodes': num_critical,
                'critical_nodes_pct': critical_pct
            })

            print(f"  ✓ {case['event']}: {num_critical} nós críticos ({critical_pct:.1f}%)")

        self.critical_nodes = pd.DataFrame(results)

    def calculate_resilience_index(self):
        """Calcula índice de resiliência composto."""
        print("\nCalculando índice de resiliência...")

        # Usar resultados de remoção de 10%
        resilience_10 = self.resilience_results[self.resilience_results['removal_fraction'] == 0.10]

        # Para cada rede, comparar random vs targeted
        indices = []

        for network_id in resilience_10['network_id'].unique():
            network_data = resilience_10[resilience_10['network_id'] == network_id]

            random_data = network_data[network_data['removal_strategy'] == 'random'].iloc[0]
            targeted_data = network_data[network_data['removal_strategy'] == 'targeted'].iloc[0]

            # Índice de resiliência = quanto a rede é MAIS resistente a ataques aleatórios
            # que a ataques direcionados
            # Se random e targeted têm impacto similar, a rede é resiliente
            # Se targeted tem muito mais impacto, a rede é vulnerável a ataques dirigidos

            random_impact = random_data['component_increase']
            targeted_impact = targeted_data['component_increase']

            # Resilience index = 1 - (random_impact / targeted_impact)
            # 1 = muito resiliente (random = targeted)
            # 0 = vulnerável (random << targeted)
            if targeted_impact > 0:
                resilience_index = 1 - (random_impact / targeted_impact)
            else:
                resilience_index = 1.0

            indices.append({
                'network_id': network_id,
                'sport': random_data['sport'],
                'event': random_data['event'],
                'resilience_index': resilience_index,
                'random_component_increase': random_impact,
                'targeted_component_increase': targeted_impact
            })

        self.resilience_indices = pd.DataFrame(indices)

        # Mostrar top 5 mais resilientes
        print("\n  Top 5 redes mais resilientes:")
        top5 = self.resilience_indices.nlargest(5, 'resilience_index')
        for _, row in top5.iterrows():
            print(f"    {row['event']}: {row['resilience_index']:.3f}")

    def export_results(self):
        """Exporta resultados."""
        print("\nExportando resultados...")

        # Resultados de simulação
        sim_path = self.output_dir / 'resilience_simulation.csv'
        self.resilience_results.to_csv(sim_path, index=False)
        print(f"  ✓ {sim_path.name}")

        # Nós críticos
        crit_path = self.output_dir / 'critical_nodes.csv'
        self.critical_nodes.to_csv(crit_path, index=False)
        print(f"  ✓ {crit_path.name}")

        # Índices de resiliência
        idx_path = self.output_dir / 'resilience_indices.csv'
        self.resilience_indices.to_csv(idx_path, index=False)
        print(f"  ✓ {idx_path.name}")

    def run(self):
        """Executa análise completa."""
        print("\n" + "="*100)
        print("ANÁLISE DE RESILIÊNCIA E ROBUSTEZ")
        print("="*100)

        self.load_data()
        self.analyze_resilience()
        self.identify_critical_nodes()
        self.calculate_resilience_index()
        self.export_results()

        print("\n" + "="*100)
        print("ANÁLISE DE RESILIÊNCIA CONCLUÍDA!")
        print("="*100)


if __name__ == "__main__":
    analyzer = NetworkResilienceAnalyzer(
        networks_dir='../../results_per_event_cleaned',
        pagerank_path='../../results_complete_mining/data/pagerank.csv',
        output_dir='../../results_complete_mining/data'
    )

    analyzer.run()
