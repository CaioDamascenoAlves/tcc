#!/usr/bin/env python3
"""
Gera rankings Top 10/20 por evento e globais.
Cria tabelas LaTeX formatadas.
"""

import pandas as pd
from pathlib import Path

class RankingGenerator:
    """Gera rankings e tabelas."""

    def __init__(self, data_dir: str, output_dir: str):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Carregar dados
        self.load_data()

    def load_data(self):
        """Carrega dados minerados."""
        print("Carregando dados...")
        self.pagerank = pd.read_csv(self.data_dir / 'pagerank.csv')
        self.authorities = pd.read_csv(self.data_dir / 'authorities.csv')
        self.betweenness = pd.read_csv(self.data_dir / 'betweenness.csv')
        self.communities = pd.read_csv(self.data_dir / 'communities.csv')
        self.community_stats = pd.read_csv(self.data_dir / 'community_stats.csv')
        print(f"  ✓ {len(self.pagerank)} registros de PageRank")

    def generate_top10_per_event(self):
        """Gera Top 10 PageRank por evento."""
        print("\nGerando Top 10 por evento...")

        for network_id in self.pagerank['network_id'].unique():
            event_data = self.pagerank[self.pagerank['network_id'] == network_id]
            event_name = event_data['network_name'].iloc[0]
            sport = event_data['sport'].iloc[0]

            # Top 10
            top10 = event_data.nlargest(10, 'pagerank')

            # LaTeX
            latex = self._generate_latex_table(top10, event_name)

            # Salvar
            safe_name = event_name.replace(' ', '_').replace('/', '_')
            latex_file = self.output_dir / f'top10_pagerank_{safe_name}.tex'
            with open(latex_file, 'w') as f:
                f.write(latex)

            print(f"  ✓ {event_name}: {latex_file.name}")

    def _generate_latex_table(self, df: pd.DataFrame, title: str) -> str:
        """Gera tabela LaTeX."""
        latex = f"""\\begin{{table}}[h]
    \\centering
    \\caption{{Top 10 Atletas por PageRank - {title}}}
    \\label{{tab:top10_{title.replace(' ', '_').lower()}}}
    \\footnotesize
    \\begin{{tabular}}{{clccc}}
        \\toprule
        \\textbf{{Rank}} & \\textbf{{Atleta}} & \\textbf{{País}} & \\textbf{{PageRank}} & \\textbf{{Medalhas}} \\\\
        \\midrule
"""

        for i, (_, row) in enumerate(df.iterrows(), 1):
            name = row['athlete_name'].replace('_', ' ')
            noc = row['noc']
            pr = row['pagerank']
            medals = int(row['total_medals'])
            latex += f"        {i} & {name} & {noc} & {pr:.4f} & {medals} \\\\\n"

        latex += """        \\bottomrule
    \\end{tabular}
\\end{table}
"""
        return latex

    def generate_top20_global(self):
        """Gera Top 20 global cross-esporte."""
        print("\nGerando Top 20 global...")

        # Top 20 geral
        top20 = self.pagerank.nlargest(20, 'pagerank')

        # Contar por gênero
        gender_count = top20['gender'].value_counts()
        print(f"  Masculino: {gender_count.get('M', 0)}")
        print(f"  Feminino: {gender_count.get('F', 0)}")

        # LaTeX
        latex = """\\begin{table}[h]
    \\centering
    \\caption{Top 20 Atletas Globais por PageRank (Todos os Esportes)}
    \\label{tab:top20_global}
    \\footnotesize
    \\begin{tabular}{clcccc}
        \\toprule
        \\textbf{Rank} & \\textbf{Atleta} & \\textbf{Esporte} & \\textbf{Gênero} & \\textbf{PageRank} & \\textbf{Medalhas} \\\\
        \\midrule
"""

        for i, (_, row) in enumerate(top20.iterrows(), 1):
            name = row['athlete_name'].replace('_', ' ')
            sport = row['sport'].capitalize()
            gender = row['gender']
            pr = row['pagerank']
            medals = int(row['total_medals'])
            latex += f"        {i} & {name} & {sport} & {gender} & {pr:.4f} & {medals} \\\\\n"

        latex += """        \\bottomrule
    \\end{tabular}
\\end{table}
"""

        # Salvar
        latex_file = self.output_dir / 'top20_global.tex'
        with open(latex_file, 'w') as f:
            f.write(latex)

        print(f"  ✓ {latex_file.name}")

        # CSV também
        csv_file = self.output_dir / 'top20_global.csv'
        top20.to_csv(csv_file, index=False)
        print(f"  ✓ {csv_file.name}")

    def generate_betweenness_stats(self):
        """Estatísticas de atletas-ponte."""
        print("\nCalculando estatísticas de Betweenness...")

        # Percentual de atletas-ponte por esporte (betweenness > 0)
        stats = []

        for network_id in self.betweenness['network_id'].unique():
            event_data = self.betweenness[self.betweenness['network_id'] == network_id]
            event_name = event_data['network_name'].iloc[0]
            sport = event_data['sport'].iloc[0]

            total = len(event_data)
            bridges = len(event_data[event_data['betweenness'] > 0])
            pct = bridges / total * 100 if total > 0 else 0

            stats.append({
                'network_id': network_id,
                'network_name': event_name,
                'sport': sport,
                'total_athletes': total,
                'bridge_athletes': bridges,
                'bridge_percentage': pct
            })

        df_stats = pd.DataFrame(stats)

        # Salvar
        csv_file = self.output_dir / 'betweenness_stats.csv'
        df_stats.to_csv(csv_file, index=False)
        print(f"  ✓ {csv_file.name}")

        # Mostrar por esporte
        print("\n  Percentual de atletas-ponte por evento:")
        for _, row in df_stats.iterrows():
            print(f"    {row['network_name']}: {row['bridge_percentage']:.1f}%")

    def generate_community_summary(self):
        """Resumo de comunidades."""
        print("\nGerando resumo de comunidades...")

        # Número de comunidades por evento
        summary = self.community_stats.groupby(['network_id', 'network_name', 'sport', 'gender']).agg({
            'community_id': 'nunique',
            'size': ['mean', 'min', 'max'],
            'gold_pct': 'mean',
            'silver_pct': 'mean',
            'bronze_pct': 'mean'
        }).reset_index()

        summary.columns = ['network_id', 'network_name', 'sport', 'gender',
                          'num_communities', 'avg_size', 'min_size', 'max_size',
                          'avg_gold_pct', 'avg_silver_pct', 'avg_bronze_pct']

        # Salvar
        csv_file = self.output_dir / 'community_summary.csv'
        summary.to_csv(csv_file, index=False)
        print(f"  ✓ {csv_file.name}")

        # Mostrar
        print("\n  Número de comunidades por evento:")
        for _, row in summary.iterrows():
            print(f"    {row['network_name']}: {int(row['num_communities'])} comunidades")

    def run(self):
        """Executa todas as gerações."""
        print("\n" + "="*100)
        print("GERAÇÃO DE RANKINGS E TABELAS")
        print("="*100)

        self.generate_top10_per_event()
        self.generate_top20_global()
        self.generate_betweenness_stats()
        self.generate_community_summary()

        print("\n" + "="*100)
        print("RANKINGS E TABELAS GERADOS!")
        print("="*100)
        print(f"Resultados em: {self.output_dir}")


if __name__ == "__main__":
    generator = RankingGenerator(
        data_dir='../../results_complete_mining/data',
        output_dir='../../results_complete_mining/tables'
    )

    generator.run()
