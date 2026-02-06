#!/usr/bin/env python3
"""
Análise de Evolução Temporal

Analisa como as redes evoluem ao longo do tempo:
1. Crescimento da rede (nós, arestas) por década/era
2. Evolução da densidade ao longo do tempo
3. Surgimento e permanência de comunidades
4. Concentração geográfica (NOCs) ao longo do tempo
5. Análise de "gerações" de atletas
"""

import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path
from collections import defaultdict

class TemporalEvolutionAnalyzer:
    """Análise de evolução temporal das redes."""

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

        # 12 casos
        self.case_studies = self._define_cases()

    def _define_cases(self):
        """Define casos de estudo."""
        return [
            {'id': 1, 'sport': 'Football', 'event': 'M Football Men\'s Football', 'gender': 'M', 'file': 'football_M_Football_Mens_Football.gexf'},
            {'id': 2, 'sport': 'Football', 'event': 'F Football Women\'s Football', 'gender': 'F', 'file': 'football_F_Football_Womens_Football.gexf'},
            {'id': 3, 'sport': 'Basketball', 'event': 'M Basketball Men\'s Basketball', 'gender': 'M', 'file': 'basketball_M_Basketball_Mens_Basketball.gexf'},
            {'id': 4, 'sport': 'Basketball', 'event': 'F Basketball Women\'s Basketball', 'gender': 'F', 'file': 'basketball_F_Basketball_Womens_Basketball.gexf'},
            {'id': 5, 'sport': 'Athletics', 'event': 'M 100m', 'gender': 'M', 'file': 'athletics_M_100m.gexf'},
            {'id': 6, 'sport': 'Athletics', 'event': 'F 100m', 'gender': 'F', 'file': 'athletics_F_100m.gexf'},
            {'id': 7, 'sport': 'Swimming', 'event': 'M 100m Freestyle', 'gender': 'M', 'file': 'swimming_M_100m_Freestyle.gexf'},
            {'id': 8, 'sport': 'Swimming', 'event': 'F 100m Freestyle', 'gender': 'F', 'file': 'swimming_F_100m_Freestyle.gexf'},
            {'id': 9, 'sport': 'Judo', 'event': 'M -90kg', 'gender': 'M', 'file': 'judo_M_-90kg.gexf'},
            {'id': 10, 'sport': 'Judo', 'event': 'F -70kg', 'gender': 'F', 'file': 'judo_F_-70kg.gexf'},
            {'id': 11, 'sport': 'Boxing', 'event': 'M Welter (63-69kg)', 'gender': 'M', 'file': 'boxing_M_Welter_63-69kg.gexf'},
            {'id': 12, 'sport': 'Boxing', 'event': 'F Middle (69-75kg)', 'gender': 'F', 'file': 'boxing_F_Middle_69-75kg.gexf'}
        ]

    def load_data(self):
        """Carrega dados."""
        print("Carregando dados...")

        self.df = pd.read_csv(self.data_cleaned_path)
        self.df = self.df[self.df['Medal'].notna()]

        self.communities = pd.read_csv(self.communities_path)

        print(f"  ✓ {len(self.df):,} registros de medalhistas")

    def assign_era(self, year: int) -> str:
        """Atribui era a um ano."""
        for era_name, (start, end) in self.eras.items():
            if start <= year <= end:
                return era_name
        return 'Unknown'

    def analyze_growth_by_era(self):
        """Analisa crescimento da rede por era."""
        print("\nAnalisando crescimento por era...")

        results = []

        for case in self.case_studies:
            # Filtrar dados do evento
            if case['sport'] == 'Football':
                event_df = self.df[(self.df['Sport'] == 'Football') &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Basketball':
                event_df = self.df[(self.df['Sport'] == 'Basketball') &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Athletics':
                event_df = self.df[(self.df['Sport'] == 'Athletics') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Swimming':
                event_df = self.df[(self.df['Sport'] == 'Swimming') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Judo':
                event_df = self.df[(self.df['Sport'] == 'Judo') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Boxing':
                event_df = self.df[(self.df['Sport'] == 'Boxing') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            else:
                continue

            if len(event_df) == 0:
                continue

            # Atribuir eras
            event_df['Era'] = event_df['Year'].apply(self.assign_era)

            # Estatísticas por era
            for era_name in self.eras.keys():
                era_data = event_df[event_df['Era'] == era_name]

                if len(era_data) == 0:
                    continue

                # Contar atletas únicos, países, edições
                num_athletes = era_data['ID'].nunique()
                num_countries = era_data['NOC'].nunique()
                num_editions = era_data['Year'].nunique()
                total_medals = len(era_data)

                results.append({
                    'network_id': case['id'],
                    'sport': case['sport'],
                    'gender': case['gender'],
                    'event': case['event'],
                    'era': era_name,
                    'num_athletes': num_athletes,
                    'num_countries': num_countries,
                    'num_editions': num_editions,
                    'total_medals': total_medals,
                    'medals_per_edition': total_medals / num_editions if num_editions > 0 else 0,
                    'athletes_per_edition': num_athletes / num_editions if num_editions > 0 else 0
                })

            print(f"  ✓ {case['event']}")

        self.growth_by_era = pd.DataFrame(results)

    def analyze_noc_concentration(self):
        """Analisa concentração geográfica (NOCs) ao longo do tempo."""
        print("\nAnalisando concentração geográfica...")

        results = []

        for case in self.case_studies:
            # Filtrar dados do evento
            if case['sport'] == 'Football':
                event_df = self.df[(self.df['Sport'] == 'Football') &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Basketball':
                event_df = self.df[(self.df['Sport'] == 'Basketball') &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Athletics':
                event_df = self.df[(self.df['Sport'] == 'Athletics') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Swimming':
                event_df = self.df[(self.df['Sport'] == 'Swimming') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Judo':
                event_df = self.df[(self.df['Sport'] == 'Judo') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Boxing':
                event_df = self.df[(self.df['Sport'] == 'Boxing') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            else:
                continue

            if len(event_df) == 0:
                continue

            # Atribuir eras
            event_df['Era'] = event_df['Year'].apply(self.assign_era)

            # Concentração por era
            for era_name in self.eras.keys():
                era_data = event_df[event_df['Era'] == era_name]

                if len(era_data) == 0:
                    continue

                # Distribuição de medalhas por país
                noc_counts = era_data['NOC'].value_counts()

                # Top 3 países (% de medalhas)
                total_medals = len(era_data)
                top3_medals = noc_counts.head(3).sum()
                top3_concentration = top3_medals / total_medals * 100 if total_medals > 0 else 0

                # Índice Herfindahl-Hirschman (HHI) para concentração
                # HHI = Σ (share_i)^2
                # HHI próximo de 10000 = alta concentração (monopólio)
                # HHI próximo de 0 = baixa concentração (dispersão)
                shares = noc_counts / total_medals
                hhi = (shares ** 2).sum() * 10000

                results.append({
                    'network_id': case['id'],
                    'sport': case['sport'],
                    'gender': case['gender'],
                    'era': era_name,
                    'num_countries': len(noc_counts),
                    'top3_concentration': top3_concentration,
                    'hhi': hhi,
                    'top_country': noc_counts.index[0] if len(noc_counts) > 0 else 'N/A',
                    'top_country_medals': noc_counts.values[0] if len(noc_counts) > 0 else 0
                })

        self.noc_concentration = pd.DataFrame(results)

        # Mostrar evolução média de concentração
        print("\n  Concentração média (Top 3) por era:")
        for era in ['Pioneira', 'Pos-Guerra', 'Moderna', 'Contemporanea']:
            era_data = self.noc_concentration[self.noc_concentration['era'] == era]
            if len(era_data) > 0:
                mean_conc = era_data['top3_concentration'].mean()
                print(f"    {era}: {mean_conc:.1f}%")

    def analyze_athlete_generations(self):
        """Analisa gerações de atletas (sobreposição temporal)."""
        print("\nAnalisando gerações de atletas...")

        results = []

        for case in self.case_studies:
            # Filtrar dados do evento
            if case['sport'] == 'Football':
                event_df = self.df[(self.df['Sport'] == 'Football') &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Basketball':
                event_df = self.df[(self.df['Sport'] == 'Basketball') &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Athletics':
                event_df = self.df[(self.df['Sport'] == 'Athletics') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Swimming':
                event_df = self.df[(self.df['Sport'] == 'Swimming') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Judo':
                event_df = self.df[(self.df['Sport'] == 'Judo') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            elif case['sport'] == 'Boxing':
                event_df = self.df[(self.df['Sport'] == 'Boxing') &
                                   (self.df['Event_Normalized'] == case['event']) &
                                   (self.df['Sex'] == case['gender'])]
            else:
                continue

            if len(event_df) == 0:
                continue

            # Para cada atleta, calcular span de anos
            athlete_spans = event_df.groupby('ID')['Year'].agg(['min', 'max', 'count']).reset_index()
            athlete_spans.columns = ['athlete_id', 'first_year', 'last_year', 'num_appearances']
            athlete_spans['career_span'] = athlete_spans['last_year'] - athlete_spans['first_year']

            # Estatísticas de carreira
            avg_span = athlete_spans['career_span'].mean()
            avg_appearances = athlete_spans['num_appearances'].mean()
            max_span = athlete_spans['career_span'].max()

            # Atletas multi-geração (span > 12 anos = 3+ Olimpíadas)
            multi_gen = len(athlete_spans[athlete_spans['career_span'] >= 12])
            multi_gen_pct = multi_gen / len(athlete_spans) * 100 if len(athlete_spans) > 0 else 0

            results.append({
                'network_id': case['id'],
                'sport': case['sport'],
                'gender': case['gender'],
                'event': case['event'],
                'avg_career_span': avg_span,
                'max_career_span': max_span,
                'avg_appearances': avg_appearances,
                'multi_generation_count': multi_gen,
                'multi_generation_pct': multi_gen_pct
            })

            print(f"  ✓ {case['event']}: {multi_gen} atletas multi-geração ({multi_gen_pct:.1f}%)")

        self.athlete_generations = pd.DataFrame(results)

    def export_results(self):
        """Exporta resultados."""
        print("\nExportando resultados...")

        # Crescimento por era
        growth_path = self.output_dir / 'temporal_growth_by_era.csv'
        self.growth_by_era.to_csv(growth_path, index=False)
        print(f"  ✓ {growth_path.name}")

        # Concentração geográfica
        noc_path = self.output_dir / 'noc_concentration_by_era.csv'
        self.noc_concentration.to_csv(noc_path, index=False)
        print(f"  ✓ {noc_path.name}")

        # Gerações de atletas
        gen_path = self.output_dir / 'athlete_generations.csv'
        self.athlete_generations.to_csv(gen_path, index=False)
        print(f"  ✓ {gen_path.name}")

    def run(self):
        """Executa análise completa."""
        print("\n" + "="*100)
        print("ANÁLISE DE EVOLUÇÃO TEMPORAL")
        print("="*100)

        self.load_data()
        self.analyze_growth_by_era()
        self.analyze_noc_concentration()
        self.analyze_athlete_generations()
        self.export_results()

        print("\n" + "="*100)
        print("ANÁLISE DE EVOLUÇÃO TEMPORAL CONCLUÍDA!")
        print("="*100)


if __name__ == "__main__":
    analyzer = TemporalEvolutionAnalyzer(
        data_cleaned_path='../../data/athlete_events_cleaned.csv',
        networks_dir='../../results_per_event_cleaned',
        communities_path='../../results_complete_mining/data/communities.csv',
        output_dir='../../results_complete_mining/data'
    )

    analyzer.run()
