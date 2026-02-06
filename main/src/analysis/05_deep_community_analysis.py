#!/usr/bin/env python3
"""
Análise Profunda de Comunidades

Calcula:
1. Segregação estrutural (arestas intra vs inter-comunidades)
2. Rivalidades inter-comunidades (top confrontos)
3. Hierarquia de comunidades (PageRank médio, tamanho)
4. Perfil de medalhas por comunidade
"""

import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path
from collections import defaultdict

class DeepCommunityAnalyzer:
    """Análise profunda de comunidades."""

    def __init__(self, networks_dir: str, data_dir: str, output_dir: str):
        self.networks_dir = Path(networks_dir)
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Casos de estudo
        self.case_studies = self._define_cases()

        # Cache de redes
        self.networks = {}

    def _define_cases(self):
        """Define casos de estudo."""
        return [
            {'id': 1, 'sport': 'football', 'file': 'football_M_Football_Mens_Football.gexf'},
            {'id': 2, 'sport': 'football', 'file': 'football_F_Football_Womens_Football.gexf'},
            {'id': 3, 'sport': 'basketball', 'file': 'basketball_M_Basketball_Mens_Basketball.gexf'},
            {'id': 4, 'sport': 'basketball', 'file': 'basketball_F_Basketball_Womens_Basketball.gexf'},
            {'id': 5, 'sport': 'athletics', 'file': 'athletics_M_100m.gexf'},
            {'id': 6, 'sport': 'athletics', 'file': 'athletics_F_100m.gexf'},
            {'id': 7, 'sport': 'swimming', 'file': 'swimming_M_100m_Freestyle.gexf'},
            {'id': 8, 'sport': 'swimming', 'file': 'swimming_F_100m_Freestyle.gexf'},
            {'id': 9, 'sport': 'judo', 'file': 'judo_M_-90kg.gexf'},
            {'id': 10, 'sport': 'judo', 'file': 'judo_F_-70kg.gexf'},
            {'id': 11, 'sport': 'boxing', 'file': 'boxing_M_Welter_63-69kg.gexf'},
            {'id': 12, 'sport': 'boxing', 'file': 'boxing_F_Middle_69-75kg.gexf'}
        ]

    def load_network(self, case: dict) -> nx.DiGraph:
        """Carrega rede."""
        if case['id'] in self.networks:
            return self.networks[case['id']]

        file_path = self.networks_dir / case['sport'] / case['file']
        G = nx.read_gexf(file_path)
        self.networks[case['id']] = G
        return G

    def load_data(self):
        """Carrega dados minerados."""
        print("Carregando dados...")
        self.communities = pd.read_csv(self.data_dir / 'communities.csv')
        self.pagerank = pd.read_csv(self.data_dir / 'pagerank.csv')
        self.community_stats = pd.read_csv(self.data_dir / 'community_stats.csv')
        print(f"  ✓ {len(self.communities)} atletas em comunidades")

    def calculate_segregation(self):
        """Calcula índice de segregação por comunidade.

        S = Arestas Intra / Arestas Inter

        S > 1: Segregada (mais conexões internas)
        S < 1: Integrada (mais conexões externas)
        """
        print("\nCalculando segregação estrutural...")

        results = []

        for case in self.case_studies:
            G = self.load_network(case)

            # Comunidades deste evento
            event_comms = self.communities[self.communities['network_id'] == case['id']]

            # Criar mapeamento atleta -> comunidade (converter IDs para string)
            athlete_to_comm = dict(zip(event_comms['athlete_id'].astype(str), event_comms['community_id']))

            # Contar arestas intra e inter por comunidade
            comm_edges = defaultdict(lambda: {'intra': 0, 'inter': 0})

            for u, v in G.edges():
                u_comm = athlete_to_comm.get(str(u))
                v_comm = athlete_to_comm.get(str(v))

                if u_comm is not None and v_comm is not None:
                    if u_comm == v_comm:
                        comm_edges[u_comm]['intra'] += 1
                    else:
                        comm_edges[u_comm]['inter'] += 1
                        comm_edges[v_comm]['inter'] += 1  # Contabilizar para ambas

            # Calcular índice de segregação
            for comm_id, edges in comm_edges.items():
                intra = edges['intra']
                inter = edges['inter']
                total = intra + inter

                segregation_index = intra / inter if inter > 0 else float('inf')

                results.append({
                    'network_id': case['id'],
                    'community_id': comm_id,
                    'intra_edges': intra,
                    'inter_edges': inter,
                    'total_edges': total,
                    'intra_fraction': intra / total if total > 0 else 0,
                    'segregation_index': segregation_index
                })

        self.segregation = pd.DataFrame(results)

        if len(results) == 0:
            print("  ⚠️  Nenhum dado de segregação calculado")
            return

        # Média por evento
        print("\n  Segregação média por evento:")
        for network_id in self.segregation['network_id'].unique():
            event_seg = self.segregation[self.segregation['network_id'] == network_id]
            if len(event_seg) > 0:
                mean_seg = event_seg['segregation_index'].replace([np.inf], 100).mean()
                mean_intra_frac = event_seg['intra_fraction'].mean()
                print(f"    Rede {network_id}: Índice={mean_seg:.2f}, Fração Intra={mean_intra_frac:.2%}")

    def calculate_inter_community_rivalries(self):
        """Calcula rivalidades entre pares de comunidades."""
        print("\nCalculando rivalidades inter-comunidades...")

        results = []

        for case in self.case_studies:
            G = self.load_network(case)

            # Comunidades deste evento
            event_comms = self.communities[self.communities['network_id'] == case['id']]
            athlete_to_comm = dict(zip(event_comms['athlete_id'].astype(str), event_comms['community_id']))

            # Contar arestas entre pares de comunidades
            rivalry_counts = defaultdict(int)

            for u, v in G.edges():
                u_comm = athlete_to_comm.get(str(u))
                v_comm = athlete_to_comm.get(str(v))

                if u_comm is not None and v_comm is not None and u_comm != v_comm:
                    # Ordenar para evitar duplicatas (C1,C2) vs (C2,C1)
                    pair = tuple(sorted([u_comm, v_comm]))
                    rivalry_counts[pair] += 1

            # Guardar top rivalries
            for (comm1, comm2), count in rivalry_counts.items():
                results.append({
                    'network_id': case['id'],
                    'community_1': comm1,
                    'community_2': comm2,
                    'num_edges': count
                })

        self.rivalries = pd.DataFrame(results)

        # Top 10 por evento
        print("\n  Top 5 rivalidades por evento:")
        for case in self.case_studies:
            event_riv = self.rivalries[self.rivalries['network_id'] == case['id']]
            if len(event_riv) > 0:
                top5 = event_riv.nlargest(5, 'num_edges')
                print(f"    Rede {case['id']}:")
                for _, row in top5.iterrows():
                    print(f"      C{row['community_1']} ↔ C{row['community_2']}: {row['num_edges']} confrontos")

    def calculate_community_hierarchy(self):
        """Calcula hierarquia de comunidades (PageRank médio)."""
        print("\nCalculando hierarquia de comunidades...")

        # Juntar PageRank com comunidades
        pr_comm = self.pagerank.merge(
            self.communities[['network_id', 'athlete_id', 'community_id']],
            on=['network_id', 'athlete_id'],
            how='left'
        )

        # PageRank médio por comunidade
        hierarchy = pr_comm.groupby(['network_id', 'community_id']).agg({
            'pagerank': 'mean',
            'athlete_id': 'count'
        }).reset_index()
        hierarchy.columns = ['network_id', 'community_id', 'avg_pagerank', 'size']

        # Classificar em níveis (P80, P40)
        hierarchy['percentile'] = hierarchy.groupby('network_id')['avg_pagerank'].rank(pct=True)
        hierarchy['level'] = 'Periférica'
        hierarchy.loc[hierarchy['percentile'] > 0.40, 'level'] = 'Intermediária'
        hierarchy.loc[hierarchy['percentile'] > 0.80, 'level'] = 'Núcleo'

        self.hierarchy = hierarchy

        # Mostrar núcleos
        print("\n  Comunidades Núcleo (>P80):")
        for network_id in hierarchy['network_id'].unique():
            nucleos = hierarchy[(hierarchy['network_id'] == network_id) &
                               (hierarchy['level'] == 'Núcleo')]
            if len(nucleos) > 0:
                print(f"    Rede {network_id}: {len(nucleos)} comunidades núcleo")

    def export_results(self):
        """Exporta resultados."""
        print("\nExportando resultados...")

        # Segregação
        seg_path = self.output_dir / 'community_segregation.csv'
        self.segregation.to_csv(seg_path, index=False)
        print(f"  ✓ {seg_path.name}")

        # Rivalidades
        riv_path = self.output_dir / 'inter_community_rivalries.csv'
        self.rivalries.to_csv(riv_path, index=False)
        print(f"  ✓ {riv_path.name}")

        # Hierarquia
        hier_path = self.output_dir / 'community_hierarchy.csv'
        self.hierarchy.to_csv(hier_path, index=False)
        print(f"  ✓ {hier_path.name}")

    def run(self):
        """Executa análise completa."""
        print("\n" + "="*100)
        print("ANÁLISE PROFUNDA DE COMUNIDADES")
        print("="*100)

        self.load_data()
        self.calculate_segregation()
        self.calculate_inter_community_rivalries()
        self.calculate_community_hierarchy()
        self.export_results()

        print("\n" + "="*100)
        print("ANÁLISE DE COMUNIDADES CONCLUÍDA!")
        print("="*100)


if __name__ == "__main__":
    analyzer = DeepCommunityAnalyzer(
        networks_dir='../../results_per_event_cleaned',
        data_dir='../../results_complete_mining/data',
        output_dir='../../results_complete_mining/data'
    )

    analyzer.run()
