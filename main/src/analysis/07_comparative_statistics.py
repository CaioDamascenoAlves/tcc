#!/usr/bin/env python3
"""
Estatísticas Comparativas Globais

Compara os 12 eventos em múltiplas dimensões:
1. Métricas de rede (nós, arestas, densidade, componentes)
2. Métricas de centralidade (PageRank, Betweenness médios)
3. Métricas de comunidades (número, tamanho, segregação)
4. Métricas temporais (entropia, span)
5. Análise de gênero (M vs F em cada esporte)
"""

import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path

class ComparativeAnalyzer:
    """Análise comparativa entre eventos."""

    def __init__(self, networks_dir: str, data_dir: str, output_dir: str):
        self.networks_dir = Path(networks_dir)
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 12 casos
        self.case_studies = self._define_cases()

    def _define_cases(self):
        """Define casos de estudo."""
        return [
            {'id': 1, 'sport': 'Football', 'gender': 'M', 'event': 'M Football', 'file': 'football_M_Football_Mens_Football.gexf'},
            {'id': 2, 'sport': 'Football', 'gender': 'F', 'event': 'F Football', 'file': 'football_F_Football_Womens_Football.gexf'},
            {'id': 3, 'sport': 'Basketball', 'gender': 'M', 'event': 'M Basketball', 'file': 'basketball_M_Basketball_Mens_Basketball.gexf'},
            {'id': 4, 'sport': 'Basketball', 'gender': 'F', 'event': 'F Basketball', 'file': 'basketball_F_Basketball_Womens_Basketball.gexf'},
            {'id': 5, 'sport': 'Athletics', 'gender': 'M', 'event': 'M 100m', 'file': 'athletics_M_100m.gexf'},
            {'id': 6, 'sport': 'Athletics', 'gender': 'F', 'event': 'F 100m', 'file': 'athletics_F_100m.gexf'},
            {'id': 7, 'sport': 'Swimming', 'gender': 'M', 'event': 'M 100m Free', 'file': 'swimming_M_100m_Freestyle.gexf'},
            {'id': 8, 'sport': 'Swimming', 'gender': 'F', 'event': 'F 100m Free', 'file': 'swimming_F_100m_Freestyle.gexf'},
            {'id': 9, 'sport': 'Judo', 'gender': 'M', 'event': 'M -90kg', 'file': 'judo_M_-90kg.gexf'},
            {'id': 10, 'sport': 'Judo', 'gender': 'F', 'event': 'F -70kg', 'file': 'judo_F_-70kg.gexf'},
            {'id': 11, 'sport': 'Boxing', 'gender': 'M', 'event': 'M Welter', 'file': 'boxing_M_Welter_63-69kg.gexf'},
            {'id': 12, 'sport': 'Boxing', 'gender': 'F', 'event': 'F Middle', 'file': 'boxing_F_Middle_69-75kg.gexf'}
        ]

    def load_data(self):
        """Carrega dados minerados."""
        print("Carregando dados...")

        self.global_metrics = pd.read_csv(self.data_dir / 'global_metrics.csv')
        self.pagerank = pd.read_csv(self.data_dir / 'pagerank.csv')
        self.betweenness = pd.read_csv(self.data_dir / 'betweenness.csv')
        self.communities = pd.read_csv(self.data_dir / 'communities.csv')
        self.community_stats = pd.read_csv(self.data_dir / 'community_stats.csv')
        self.segregation = pd.read_csv(self.data_dir / 'community_segregation.csv')
        self.hierarchy = pd.read_csv(self.data_dir / 'community_hierarchy.csv')
        self.temporal_entropy = pd.read_csv(self.data_dir / 'temporal_entropy.csv')

        print(f"  ✓ Dados carregados")

    def calculate_network_stats(self):
        """Estatísticas de topologia de rede."""
        print("\nCalculando estatísticas de rede...")

        results = []

        for case in self.case_studies:
            file_path = self.networks_dir / case['sport'].lower() / case['file']

            if not file_path.exists():
                print(f"  ⚠️  Rede não encontrada: {file_path}")
                continue

            G = nx.read_gexf(file_path)

            # Métricas básicas
            num_nodes = G.number_of_nodes()
            num_edges = G.number_of_edges()
            density = nx.density(G)

            # Componentes
            num_components = nx.number_weakly_connected_components(G)
            largest_cc = max(nx.weakly_connected_components(G), key=len)
            largest_cc_size = len(largest_cc)
            largest_cc_pct = largest_cc_size / num_nodes * 100 if num_nodes > 0 else 0

            # Graus
            in_degrees = [d for n, d in G.in_degree()]
            out_degrees = [d for n, d in G.out_degree()]

            results.append({
                'network_id': case['id'],
                'sport': case['sport'],
                'gender': case['gender'],
                'event': case['event'],
                'num_nodes': num_nodes,
                'num_edges': num_edges,
                'density': density,
                'num_components': num_components,
                'largest_cc_size': largest_cc_size,
                'largest_cc_pct': largest_cc_pct,
                'avg_in_degree': np.mean(in_degrees) if in_degrees else 0,
                'avg_out_degree': np.mean(out_degrees) if out_degrees else 0,
                'max_in_degree': max(in_degrees) if in_degrees else 0,
                'max_out_degree': max(out_degrees) if out_degrees else 0
            })

            print(f"  ✓ {case['event']}: {num_nodes} nós, {num_edges} arestas")

        self.network_stats = pd.DataFrame(results)

    def calculate_centrality_stats(self):
        """Estatísticas de centralidade agregadas."""
        print("\nCalculando estatísticas de centralidade...")

        # PageRank médio por evento
        pr_stats = self.pagerank.groupby(['network_id']).agg({
            'pagerank': ['mean', 'std', 'min', 'max'],
            'athlete_id': 'count'
        }).reset_index()
        pr_stats.columns = ['network_id', 'pr_mean', 'pr_std', 'pr_min', 'pr_max', 'num_athletes']

        # Betweenness médio por evento
        bt_stats = self.betweenness.groupby(['network_id']).agg({
            'betweenness': ['mean', 'std', 'min', 'max']
        }).reset_index()
        bt_stats.columns = ['network_id', 'bt_mean', 'bt_std', 'bt_min', 'bt_max']

        # Percentual de atletas-ponte (betweenness > 0)
        bridge_pct = []
        for network_id in self.betweenness['network_id'].unique():
            event_data = self.betweenness[self.betweenness['network_id'] == network_id]
            total = len(event_data)
            bridges = len(event_data[event_data['betweenness'] > 0])
            pct = bridges / total * 100 if total > 0 else 0
            bridge_pct.append({'network_id': network_id, 'bridge_pct': pct})

        bridge_df = pd.DataFrame(bridge_pct)

        # Juntar tudo
        self.centrality_stats = pr_stats.merge(bt_stats, on='network_id').merge(bridge_df, on='network_id')

        print(f"  ✓ Estatísticas calculadas para {len(self.centrality_stats)} eventos")

    def calculate_community_stats_summary(self):
        """Estatísticas de comunidades agregadas."""
        print("\nCalculando estatísticas de comunidades...")

        # Número de comunidades por evento
        num_comms = self.communities.groupby('network_id')['community_id'].nunique().reset_index()
        num_comms.columns = ['network_id', 'num_communities']

        # Tamanho médio de comunidades
        comm_sizes = self.community_stats.groupby('network_id').agg({
            'size': ['mean', 'std', 'min', 'max']
        }).reset_index()
        comm_sizes.columns = ['network_id', 'comm_size_mean', 'comm_size_std', 'comm_size_min', 'comm_size_max']

        # Segregação média
        seg_stats = self.segregation.groupby('network_id').agg({
            'segregation_index': lambda x: x.replace([np.inf], 100).mean(),
            'intra_fraction': 'mean'
        }).reset_index()
        seg_stats.columns = ['network_id', 'seg_index_mean', 'intra_frac_mean']

        # Número de comunidades núcleo
        nucleos = self.hierarchy[self.hierarchy['level'] == 'Núcleo'].groupby('network_id').size().reset_index()
        nucleos.columns = ['network_id', 'num_core_communities']

        # Juntar tudo
        self.comm_stats_summary = num_comms.merge(comm_sizes, on='network_id')\
                                           .merge(seg_stats, on='network_id')\
                                           .merge(nucleos, on='network_id', how='left')
        self.comm_stats_summary['num_core_communities'] = self.comm_stats_summary['num_core_communities'].fillna(0)

        print(f"  ✓ Estatísticas de comunidades calculadas")

    def calculate_temporal_stats_summary(self):
        """Estatísticas temporais agregadas."""
        print("\nCalculando estatísticas temporais...")

        temp_stats = self.temporal_entropy.groupby(['network_id']).agg({
            'temporal_entropy': ['mean', 'std', 'min', 'max'],
            'num_eras': 'mean',
            'year_span': 'mean',
            'first_year': 'min',
            'last_year': 'max'
        }).reset_index()

        temp_stats.columns = ['network_id', 'entropy_mean', 'entropy_std', 'entropy_min', 'entropy_max',
                             'avg_num_eras', 'avg_year_span', 'first_year', 'last_year']

        self.temporal_stats = temp_stats

        print(f"  ✓ Estatísticas temporais calculadas")

    def create_master_table(self):
        """Cria tabela mestre com todas as estatísticas."""
        print("\nCriando tabela mestre...")

        # Começar com info dos casos
        master = pd.DataFrame(self.case_studies)[['id', 'sport', 'gender', 'event']]
        master.columns = ['network_id', 'sport', 'gender', 'event']

        # Adicionar métricas de rede
        master = master.merge(self.network_stats, on=['network_id', 'sport', 'gender', 'event'], how='left')

        # Adicionar centralidade
        master = master.merge(self.centrality_stats, on='network_id', how='left')

        # Adicionar comunidades
        master = master.merge(self.comm_stats_summary, on='network_id', how='left')

        # Adicionar temporal
        master = master.merge(self.temporal_stats, on='network_id', how='left')

        # Adicionar métricas globais (clustering, diameter)
        global_subset = self.global_metrics[['id', 'avg_clustering', 'diameter']].copy()
        global_subset.columns = ['network_id', 'avg_clustering', 'diameter']
        master = master.merge(global_subset, on='network_id', how='left')

        self.master_table = master

        print(f"  ✓ Tabela mestre criada: {len(master)} eventos, {len(master.columns)} métricas")

    def analyze_gender_differences(self):
        """Analisa diferenças entre gêneros dentro de cada esporte."""
        print("\nAnalisando diferenças por gênero...")

        gender_comparisons = []

        for sport in self.master_table['sport'].unique():
            sport_data = self.master_table[self.master_table['sport'] == sport]

            m_data = sport_data[sport_data['gender'] == 'M']
            f_data = sport_data[sport_data['gender'] == 'F']

            if len(m_data) == 0 or len(f_data) == 0:
                continue

            m_row = m_data.iloc[0]
            f_row = f_data.iloc[0]

            comparison = {
                'sport': sport,
                'm_nodes': m_row['num_nodes'],
                'f_nodes': f_row['num_nodes'],
                'm_edges': m_row['num_edges'],
                'f_edges': f_row['num_edges'],
                'm_density': m_row['density'],
                'f_density': f_row['density'],
                'density_ratio': f_row['density'] / m_row['density'] if m_row['density'] > 0 else 0,
                'm_components': m_row['num_components'],
                'f_components': f_row['num_components'],
                'm_communities': m_row['num_communities'],
                'f_communities': f_row['num_communities'],
                'm_segregation': m_row['seg_index_mean'],
                'f_segregation': f_row['seg_index_mean'],
                'm_entropy': m_row['entropy_mean'],
                'f_entropy': f_row['entropy_mean']
            }

            gender_comparisons.append(comparison)

            print(f"  ✓ {sport}: Densidade F/M = {comparison['density_ratio']:.2f}")

        self.gender_comparisons = pd.DataFrame(gender_comparisons)

    def export_results(self):
        """Exporta resultados."""
        print("\nExportando resultados...")

        # Tabela mestre
        master_path = self.output_dir / 'master_comparative_table.csv'
        self.master_table.to_csv(master_path, index=False)
        print(f"  ✓ {master_path.name}")

        # Comparações de gênero
        gender_path = self.output_dir / 'gender_comparisons.csv'
        self.gender_comparisons.to_csv(gender_path, index=False)
        print(f"  ✓ {gender_path.name}")

        # Rankings por diferentes métricas
        rankings = []

        # Top 5 por densidade
        top_density = self.master_table.nlargest(5, 'density')[['event', 'density']]
        rankings.append(("Densidade", top_density))

        # Top 5 por PageRank médio
        top_pr = self.master_table.nlargest(5, 'pr_mean')[['event', 'pr_mean']]
        rankings.append(("PageRank Médio", top_pr))

        # Top 5 por segregação
        top_seg = self.master_table.nlargest(5, 'seg_index_mean')[['event', 'seg_index_mean']]
        rankings.append(("Segregação", top_seg))

        # Top 5 por entropia temporal
        top_entropy = self.master_table.nlargest(5, 'entropy_mean')[['event', 'entropy_mean']]
        rankings.append(("Entropia Temporal", top_entropy))

        # Salvar rankings
        with open(self.output_dir / 'comparative_rankings.txt', 'w') as f:
            for metric, data in rankings:
                f.write(f"\n{'='*60}\n")
                f.write(f"TOP 5: {metric}\n")
                f.write(f"{'='*60}\n")
                f.write(data.to_string(index=False))
                f.write("\n")

        print(f"  ✓ comparative_rankings.txt")

    def run(self):
        """Executa análise completa."""
        print("\n" + "="*100)
        print("ESTATÍSTICAS COMPARATIVAS GLOBAIS")
        print("="*100)

        self.load_data()
        self.calculate_network_stats()
        self.calculate_centrality_stats()
        self.calculate_community_stats_summary()
        self.calculate_temporal_stats_summary()
        self.create_master_table()
        self.analyze_gender_differences()
        self.export_results()

        print("\n" + "="*100)
        print("ANÁLISE COMPARATIVA CONCLUÍDA!")
        print("="*100)


if __name__ == "__main__":
    analyzer = ComparativeAnalyzer(
        networks_dir='../../results_per_event_cleaned',
        data_dir='../../results_complete_mining/data',
        output_dir='../../results_complete_mining/data'
    )

    analyzer.run()
