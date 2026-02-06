#!/usr/bin/env python3
"""
Análise de Entropia Temporal (Diversidade Temporal das Comunidades)

Calcula Entropia de Shannon para medir diversidade temporal:
- Distribui atletas em 4 eras olímpicas
- Calcula entropia por comunidade
- Alta entropia = participação distribuída em múltiplos períodos

Eras:
- Pioneira: 1896-1936
- Pós-Guerra: 1948-1980
- Moderna: 1984-2000
- Contemporânea: 2004-2021
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import networkx as nx

class TemporalEntropyAnalyzer:
    """Análise de entropia temporal."""

    def __init__(self, data_cleaned_path: str, networks_dir: str,
                 communities_path: str, output_dir: str):
        self.data_cleaned_path = Path(data_cleaned_path)
        self.networks_dir = Path(networks_dir)
        self.communities_path = Path(communities_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Definir eras
        self.eras = {
            'Pioneira': (1896, 1936),
            'Pos-Guerra': (1948, 1980),
            'Moderna': (1984, 2000),
            'Contemporanea': (2004, 2021)
        }

        # 12 casos de estudo
        self.case_studies = self._define_cases()

    def _define_cases(self):
        """Define os 12 casos."""
        return [
            {'id': 1, 'sport': 'football', 'event': 'M Football Men\'s Football', 'gender': 'M'},
            {'id': 2, 'sport': 'football', 'event': 'F Football Women\'s Football', 'gender': 'F'},
            {'id': 3, 'sport': 'basketball', 'event': 'M Basketball Men\'s Basketball', 'gender': 'M'},
            {'id': 4, 'sport': 'basketball', 'event': 'F Basketball Women\'s Basketball', 'gender': 'F'},
            {'id': 5, 'sport': 'athletics', 'event': 'M 100m', 'gender': 'M'},
            {'id': 6, 'sport': 'athletics', 'event': 'F 100m', 'gender': 'F'},
            {'id': 7, 'sport': 'swimming', 'event': 'M 100m Freestyle', 'gender': 'M'},
            {'id': 8, 'sport': 'swimming', 'event': 'F 100m Freestyle', 'gender': 'F'},
            {'id': 9, 'sport': 'judo', 'event': 'M -90kg', 'gender': 'M'},
            {'id': 10, 'sport': 'judo', 'event': 'F -70kg', 'gender': 'F'},
            {'id': 11, 'sport': 'boxing', 'event': 'M Welter (63-69kg)', 'gender': 'M'},
            {'id': 12, 'sport': 'boxing', 'event': 'F Middle (69-75kg)', 'gender': 'F'}
        ]

    def load_data(self):
        """Carrega dados limpos e comunidades."""
        print("Carregando dados...")

        # Dados limpos com anos
        self.df = pd.read_csv(self.data_cleaned_path)
        self.df = self.df[self.df['Medal'].notna()]

        # Comunidades detectadas
        self.communities = pd.read_csv(self.communities_path)

        print(f"  ✓ {len(self.df):,} registros de medalhistas")
        print(f"  ✓ {len(self.communities):,} atletas em comunidades")

    def assign_era(self, year: int) -> str:
        """Atribui era a um ano."""
        for era_name, (start, end) in self.eras.items():
            if start <= year <= end:
                return era_name
        return 'Unknown'

    def calculate_shannon_entropy(self, distribution: dict) -> float:
        """Calcula entropia de Shannon.

        H = -Σ p_i * log2(p_i)

        Alta entropia = alta diversidade
        """
        total = sum(distribution.values())
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in distribution.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)

        return entropy

    def analyze_temporal_diversity(self):
        """Analisa diversidade temporal por comunidade."""
        print("\nCalculando entropia temporal por comunidade...")

        results = []

        for case in self.case_studies:
            # Filtrar dados do evento
            if case['sport'] == 'football':
                event_df = self.df[(self.df['Sport'] == 'Football') &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'basketball':
                event_df = self.df[(self.df['Sport'] == 'Basketball') &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'athletics':
                event_df = self.df[(self.df['Sport'] == 'Athletics') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'swimming':
                event_df = self.df[(self.df['Sport'] == 'Swimming') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'judo':
                event_df = self.df[(self.df['Sport'] == 'Judo') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'boxing':
                event_df = self.df[(self.df['Sport'] == 'Boxing') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            else:
                continue

            if len(event_df) == 0:
                print(f"  ⚠️  Sem dados para {case['event']}")
                continue

            # Atribuir eras
            event_df['Era'] = event_df['Year'].apply(self.assign_era)

            # Comunidades deste evento
            event_communities = self.communities[self.communities['network_id'] == case['id']]

            # Calcular entropia por comunidade
            for comm_id in event_communities['community_id'].unique():
                # Atletas desta comunidade
                comm_athletes = event_communities[event_communities['community_id'] == comm_id]['athlete_id'].tolist()

                # Dados desses atletas
                comm_data = event_df[event_df['ID'].isin(comm_athletes)]

                if len(comm_data) == 0:
                    continue

                # Distribuição por era
                era_dist = comm_data['Era'].value_counts().to_dict()

                # Entropia
                entropy = self.calculate_shannon_entropy(era_dist)

                # Estatísticas temporais
                years = comm_data['Year'].unique()

                results.append({
                    'network_id': case['id'],
                    'network_name': case['event'],
                    'sport': case['sport'],
                    'gender': case['gender'],
                    'community_id': comm_id,
                    'size': len(comm_data['ID'].unique()),
                    'temporal_entropy': entropy,
                    'num_eras': len([v for v in era_dist.values() if v > 0]),
                    'num_years': len(years),
                    'first_year': years.min(),
                    'last_year': years.max(),
                    'year_span': years.max() - years.min(),
                    **{f'era_{era}': era_dist.get(era, 0) for era in self.eras.keys()}
                })

            print(f"  ✓ {case['event']}: {len(event_communities['community_id'].unique())} comunidades")

        self.entropy_results = pd.DataFrame(results)

        # Estatísticas por esporte
        print("\n  Entropia média por esporte:")
        for sport in self.entropy_results['sport'].unique():
            sport_data = self.entropy_results[self.entropy_results['sport'] == sport]
            mean_entropy = sport_data['temporal_entropy'].mean()
            min_entropy = sport_data['temporal_entropy'].min()
            max_entropy = sport_data['temporal_entropy'].max()
            print(f"    {sport.capitalize()}: {mean_entropy:.2f} (min: {min_entropy:.2f}, max: {max_entropy:.2f})")

    def export_results(self):
        """Exporta resultados."""
        print("\nExportando resultados...")

        # CSV
        csv_path = self.output_dir / 'temporal_entropy.csv'
        self.entropy_results.to_csv(csv_path, index=False)
        print(f"  ✓ {csv_path}")

        # Estatísticas agregadas por esporte
        stats = self.entropy_results.groupby(['sport', 'gender']).agg({
            'temporal_entropy': ['mean', 'std', 'min', 'max'],
            'num_eras': 'mean',
            'year_span': 'mean'
        }).round(2)

        stats_csv = self.output_dir / 'temporal_entropy_by_sport.csv'
        stats.to_csv(stats_csv)
        print(f"  ✓ {stats_csv}")

    def run(self):
        """Executa análise completa."""
        print("\n" + "="*100)
        print("ANÁLISE DE ENTROPIA TEMPORAL")
        print("="*100)

        self.load_data()
        self.analyze_temporal_diversity()
        self.export_results()

        print("\n" + "="*100)
        print("ANÁLISE DE ENTROPIA CONCLUÍDA!")
        print("="*100)


if __name__ == "__main__":
    analyzer = TemporalEntropyAnalyzer(
        data_cleaned_path='../../data/athlete_events_cleaned.csv',
        networks_dir='../../results_per_event_cleaned',
        communities_path='../../results_complete_mining/data/communities.csv',
        output_dir='../../results_complete_mining/data'
    )

    analyzer.run()
