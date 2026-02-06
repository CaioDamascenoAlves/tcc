#!/usr/bin/env python3
"""
Análise de Perfil de Medalhas

Analisa o perfil de medalhas dos atletas em diferentes níveis:
1. Por comunidade: qual o perfil dominante (Ouro, Prata, Bronze, Misto)
2. Por nível hierárquico: Núcleo vs Periferia
3. Por era temporal
4. Índice de Especialização (Gold/Total ratio)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter

class MedalProfileAnalyzer:
    """Análise de perfil de medalhas."""

    def __init__(self, data_cleaned_path: str, communities_path: str,
                 hierarchy_path: str, pagerank_path: str, output_dir: str):
        self.data_cleaned_path = Path(data_cleaned_path)
        self.communities_path = Path(communities_path)
        self.hierarchy_path = Path(hierarchy_path)
        self.pagerank_path = Path(pagerank_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 12 casos
        self.case_studies = self._define_cases()

    def _define_cases(self):
        """Define casos de estudo."""
        return [
            {'id': 1, 'sport': 'Football', 'event': 'M Football Men\'s Football', 'gender': 'M'},
            {'id': 2, 'sport': 'Football', 'event': 'F Football Women\'s Football', 'gender': 'F'},
            {'id': 3, 'sport': 'Basketball', 'event': 'M Basketball Men\'s Basketball', 'gender': 'M'},
            {'id': 4, 'sport': 'Basketball', 'event': 'F Basketball Women\'s Basketball', 'gender': 'F'},
            {'id': 5, 'sport': 'Athletics', 'event': 'M 100m', 'gender': 'M'},
            {'id': 6, 'sport': 'Athletics', 'event': 'F 100m', 'gender': 'F'},
            {'id': 7, 'sport': 'Swimming', 'event': 'M 100m Freestyle', 'gender': 'M'},
            {'id': 8, 'sport': 'Swimming', 'event': 'F 100m Freestyle', 'gender': 'F'},
            {'id': 9, 'sport': 'Judo', 'event': 'M -90kg', 'gender': 'M'},
            {'id': 10, 'sport': 'Judo', 'event': 'F -70kg', 'gender': 'F'},
            {'id': 11, 'sport': 'Boxing', 'event': 'M Welter (63-69kg)', 'gender': 'M'},
            {'id': 12, 'sport': 'Boxing', 'event': 'F Middle (69-75kg)', 'gender': 'F'}
        ]

    def load_data(self):
        """Carrega dados."""
        print("Carregando dados...")

        self.df = pd.read_csv(self.data_cleaned_path)
        self.df = self.df[self.df['Medal'].notna()]

        self.communities = pd.read_csv(self.communities_path)
        self.hierarchy = pd.read_csv(self.hierarchy_path)
        self.pagerank = pd.read_csv(self.pagerank_path)

        print(f"  ✓ {len(self.df):,} registros de medalhistas")
        print(f"  ✓ {len(self.communities):,} atletas em comunidades")

    def calculate_medal_profiles_by_community(self):
        """Calcula perfil de medalhas por comunidade."""
        print("\nCalculando perfil de medalhas por comunidade...")

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

            # Comunidades deste evento
            event_communities = self.communities[self.communities['network_id'] == case['id']]

            # Calcular perfil por comunidade
            for comm_id in event_communities['community_id'].unique():
                # Atletas desta comunidade
                comm_athletes = event_communities[event_communities['community_id'] == comm_id]['athlete_id'].tolist()

                # Dados desses atletas
                comm_data = event_df[event_df['ID'].isin(comm_athletes)]

                if len(comm_data) == 0:
                    continue

                # Contar medalhas
                medal_counts = comm_data['Medal'].value_counts().to_dict()

                gold = medal_counts.get('Gold', 0)
                silver = medal_counts.get('Silver', 0)
                bronze = medal_counts.get('Bronze', 0)
                total = gold + silver + bronze

                # Índice de especialização (quanto mais próximo de 1, mais especializado em ouro)
                gold_specialization = gold / total if total > 0 else 0

                # Perfil dominante
                if total == 0:
                    dominant_profile = 'None'
                elif gold > silver and gold > bronze:
                    dominant_profile = 'Gold'
                elif silver > gold and silver > bronze:
                    dominant_profile = 'Silver'
                elif bronze > gold and bronze > silver:
                    dominant_profile = 'Bronze'
                else:
                    dominant_profile = 'Mixed'

                # Diversidade de medalhas (Shannon entropy)
                medal_diversity = self._calculate_entropy([gold, silver, bronze])

                results.append({
                    'network_id': case['id'],
                    'sport': case['sport'],
                    'gender': case['gender'],
                    'community_id': comm_id,
                    'gold_count': gold,
                    'silver_count': silver,
                    'bronze_count': bronze,
                    'total_medals': total,
                    'gold_pct': gold / total * 100 if total > 0 else 0,
                    'silver_pct': silver / total * 100 if total > 0 else 0,
                    'bronze_pct': bronze / total * 100 if total > 0 else 0,
                    'gold_specialization': gold_specialization,
                    'medal_diversity': medal_diversity,
                    'dominant_profile': dominant_profile
                })

        self.medal_profiles = pd.DataFrame(results)

        # Distribuição de perfis dominantes
        print("\n  Distribuição de perfis dominantes:")
        profile_dist = self.medal_profiles['dominant_profile'].value_counts()
        for profile, count in profile_dist.items():
            print(f"    {profile}: {count} comunidades")

    def _calculate_entropy(self, counts):
        """Calcula entropia de Shannon para distribuição de medalhas."""
        total = sum(counts)
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in counts:
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)

        return entropy

    def analyze_profiles_by_hierarchy(self):
        """Analisa perfis de medalhas por nível hierárquico."""
        print("\nAnalisando perfis por nível hierárquico...")

        # Juntar perfis com hierarquia
        profiles_hierarchy = self.medal_profiles.merge(
            self.hierarchy[['network_id', 'community_id', 'level']],
            on=['network_id', 'community_id'],
            how='left'
        )

        # Estatísticas por nível
        hierarchy_stats = profiles_hierarchy.groupby('level').agg({
            'gold_specialization': 'mean',
            'medal_diversity': 'mean',
            'total_medals': 'sum'
        }).reset_index()

        self.hierarchy_medal_stats = hierarchy_stats

        print("\n  Especialização em ouro por nível:")
        for _, row in hierarchy_stats.iterrows():
            print(f"    {row['level']}: {row['gold_specialization']:.2%}")

    def analyze_profiles_by_pagerank_tier(self):
        """Analisa perfis de medalhas por tier de PageRank."""
        print("\nAnalisando perfis por tier de PageRank...")

        # Juntar perfis com comunidades e PageRank
        comm_pr = self.communities.merge(
            self.pagerank[['network_id', 'athlete_id', 'pagerank']],
            on=['network_id', 'athlete_id'],
            how='left'
        )

        # PageRank médio por comunidade
        comm_pr_avg = comm_pr.groupby(['network_id', 'community_id'])['pagerank'].mean().reset_index()
        comm_pr_avg.columns = ['network_id', 'community_id', 'avg_pagerank']

        # Classificar em tiers (Top 20%, Middle 60%, Bottom 20%)
        comm_pr_avg['pr_percentile'] = comm_pr_avg.groupby('network_id')['avg_pagerank'].rank(pct=True)
        comm_pr_avg['pr_tier'] = 'Middle'
        comm_pr_avg.loc[comm_pr_avg['pr_percentile'] > 0.80, 'pr_tier'] = 'Top'
        comm_pr_avg.loc[comm_pr_avg['pr_percentile'] <= 0.20, 'pr_tier'] = 'Bottom'

        # Juntar com perfis
        profiles_pr = self.medal_profiles.merge(
            comm_pr_avg[['network_id', 'community_id', 'pr_tier']],
            on=['network_id', 'community_id'],
            how='left'
        )

        # Estatísticas por tier
        tier_stats = profiles_pr.groupby('pr_tier').agg({
            'gold_specialization': 'mean',
            'medal_diversity': 'mean',
            'total_medals': 'sum'
        }).reset_index()

        self.pr_tier_medal_stats = tier_stats

        print("\n  Especialização em ouro por tier de PageRank:")
        for _, row in tier_stats.iterrows():
            print(f"    {row['pr_tier']}: {row['gold_specialization']:.2%}")

    def export_results(self):
        """Exporta resultados."""
        print("\nExportando resultados...")

        # Perfis por comunidade
        profiles_path = self.output_dir / 'medal_profiles_by_community.csv'
        self.medal_profiles.to_csv(profiles_path, index=False)
        print(f"  ✓ {profiles_path.name}")

        # Estatísticas por hierarquia
        hier_path = self.output_dir / 'medal_profiles_by_hierarchy.csv'
        self.hierarchy_medal_stats.to_csv(hier_path, index=False)
        print(f"  ✓ {hier_path.name}")

        # Estatísticas por tier de PageRank
        tier_path = self.output_dir / 'medal_profiles_by_pr_tier.csv'
        self.pr_tier_medal_stats.to_csv(tier_path, index=False)
        print(f"  ✓ {tier_path.name}")

    def run(self):
        """Executa análise completa."""
        print("\n" + "="*100)
        print("ANÁLISE DE PERFIL DE MEDALHAS")
        print("="*100)

        self.load_data()
        self.calculate_medal_profiles_by_community()
        self.analyze_profiles_by_hierarchy()
        self.analyze_profiles_by_pagerank_tier()
        self.export_results()

        print("\n" + "="*100)
        print("ANÁLISE DE PERFIL DE MEDALHAS CONCLUÍDA!")
        print("="*100)


if __name__ == "__main__":
    analyzer = MedalProfileAnalyzer(
        data_cleaned_path='../../data/athlete_events_cleaned.csv',
        communities_path='../../results_complete_mining/data/communities.csv',
        hierarchy_path='../../results_complete_mining/data/community_hierarchy.csv',
        pagerank_path='../../results_complete_mining/data/pagerank.csv',
        output_dir='../../results_complete_mining/data'
    )

    analyzer.run()
