#!/usr/bin/env python3
"""
Gera rankings de PageRank SEPARADOS por esporte.

Evita comparações cross-esporte problemáticas, focando em:
- Top 5 atletas por esporte
- Comparação M vs F dentro do mesmo esporte
- Apresentação descritiva, não analítica
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuração LaTeX
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.titlesize': 12,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})


class SportSpecificRankings:
    """Gera rankings separados por esporte."""

    def __init__(self, data_dir: str, output_dir: str):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Cores
        self.color_male = '#2E86AB'
        self.color_female = '#E63946'

        # Tradução
        self.sport_names = {
            'football': 'Futebol',
            'basketball': 'Basquete',
            'athletics': 'Atletismo',
            'swimming': 'Natação',
            'judo': 'Judô',
            'boxing': 'Boxe'
        }

    def load_data(self):
        """Carrega dados de PageRank."""
        print("Carregando dados...")
        self.df = pd.read_csv(self.data_dir / 'pagerank.csv')
        print(f"  ✓ {len(self.df)} atletas")
        print(f"  ✓ {self.df['sport'].nunique()} esportes")

    def generate_top5_by_sport(self):
        """Gera top 5 por esporte e gênero."""
        print("\nGerando Top 5 por esporte...")

        sports = self.df['sport'].unique()

        all_rankings = []

        for sport in sports:
            sport_data = self.df[self.df['sport'] == sport]

            for gender in ['M', 'F']:
                gender_data = sport_data[sport_data['gender'] == gender]

                if len(gender_data) == 0:
                    continue

                # Top 5
                top5 = gender_data.nlargest(5, 'pagerank')

                for rank, (_, row) in enumerate(top5.iterrows(), 1):
                    all_rankings.append({
                        'sport': sport,
                        'gender': gender,
                        'rank': rank,
                        'athlete_name': row['athlete_name'],
                        'noc': row['noc'],
                        'pagerank': row['pagerank'],
                        'gold_medals': row['gold_medals'],
                        'total_medals': row['total_medals']
                    })

        self.rankings_df = pd.DataFrame(all_rankings)

        # Salvar CSV
        csv_path = self.output_dir / 'top5_by_sport_gender.csv'
        self.rankings_df.to_csv(csv_path, index=False)
        print(f"  ✓ Salvo: {csv_path}")

    def plot_rankings_grid(self):
        """Plota grid com 6 esportes (2x3)."""
        print("\nGerando figura de rankings por esporte...")

        sports = sorted(self.df['sport'].unique())

        fig, axes = plt.subplots(3, 2, figsize=(12, 14))
        axes = axes.flatten()

        for idx, sport in enumerate(sports):
            ax = axes[idx]

            sport_rankings = self.rankings_df[self.rankings_df['sport'] == sport]

            # Separar M e F
            male_rankings = sport_rankings[sport_rankings['gender'] == 'M']
            female_rankings = sport_rankings[sport_rankings['gender'] == 'F']

            # Preparar dados para plot
            y_positions = []
            labels = []
            values = []
            colors = []

            # Masculino
            for _, row in male_rankings.iterrows():
                y_positions.append(len(y_positions))
                labels.append(f"{row['rank']}. {row['athlete_name'][:20]} ({row['noc']}) M")
                values.append(row['pagerank'])
                colors.append(self.color_male)

            # Separador visual
            if len(male_rankings) > 0 and len(female_rankings) > 0:
                y_positions.append(len(y_positions))
                labels.append("---")
                values.append(0)
                colors.append('white')

            # Feminino
            for _, row in female_rankings.iterrows():
                y_positions.append(len(y_positions))
                labels.append(f"{row['rank']}. {row['athlete_name'][:20]} ({row['noc']}) F")
                values.append(row['pagerank'])
                colors.append(self.color_female)

            # Plot barras horizontais
            y_positions = list(range(len(labels)))[::-1]  # Inverter para top no topo

            bars = ax.barh(y_positions, values, color=colors, alpha=0.8,
                          edgecolor='black', linewidth=0.5)

            # Labels
            ax.set_yticks(y_positions)
            ax.set_yticklabels(labels, fontsize=7)
            ax.set_xlabel('PageRank', fontsize=9)
            ax.set_title(f'{self.sport_names.get(sport, sport)}',
                        fontweight='bold', fontsize=11)
            ax.grid(axis='x', alpha=0.3, linestyle='--')

            # Limitar eixo X
            max_val = max(values) if values else 0.1
            ax.set_xlim(0, max_val * 1.1)

        plt.tight_layout()

        # Salvar
        pdf_path = self.output_dir / '02_top5_pagerank_by_sport.pdf'
        png_path = self.output_dir / '02_top5_pagerank_by_sport.png'

        fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
        fig.savefig(png_path, format='png', bbox_inches='tight', dpi=300)

        print(f"  ✓ {pdf_path.name}")
        print(f"  ✓ {png_path.name}")

        plt.close()

    def plot_rankings_compact(self):
        """Versão compacta: apenas top 3 por esporte, layout mais denso."""
        print("\nGerando figura COMPACTA (top 3)...")

        sports = sorted(self.df['sport'].unique())

        fig, axes = plt.subplots(2, 3, figsize=(14, 8))
        axes = axes.flatten()

        for idx, sport in enumerate(sports):
            ax = axes[idx]

            sport_data = self.df[self.df['sport'] == sport]

            # Top 3 M e F
            top3_m = sport_data[sport_data['gender'] == 'M'].nlargest(3, 'pagerank')
            top3_f = sport_data[sport_data['gender'] == 'F'].nlargest(3, 'pagerank')

            y_pos = 0
            y_positions = []
            labels = []
            values = []
            colors = []

            # Masculino
            for i, (_, row) in enumerate(top3_m.iterrows(), 1):
                y_positions.append(y_pos)
                name_short = row['athlete_name'].split()[-1]  # Sobrenome
                labels.append(f"{i}M. {name_short} ({row['noc']})")
                values.append(row['pagerank'])
                colors.append(self.color_male)
                y_pos += 1

            # Feminino
            for i, (_, row) in enumerate(top3_f.iterrows(), 1):
                y_positions.append(y_pos)
                name_short = row['athlete_name'].split()[-1]
                labels.append(f"{i}F. {name_short} ({row['noc']})")
                values.append(row['pagerank'])
                colors.append(self.color_female)
                y_pos += 1

            # Plot
            bars = ax.barh(y_positions, values, color=colors, alpha=0.85,
                          edgecolor='black', linewidth=0.5)

            ax.set_yticks(y_positions)
            ax.set_yticklabels(labels, fontsize=7)
            ax.set_xlabel('PageRank', fontsize=8)
            ax.set_title(self.sport_names.get(sport, sport),
                        fontweight='bold', fontsize=10, pad=8)
            ax.grid(axis='x', alpha=0.3, linestyle='--')
            ax.invert_yaxis()

            # Ajustar xlim
            if values:
                ax.set_xlim(0, max(values) * 1.15)

        # Legenda global
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.color_male, edgecolor='black', label='Masculino'),
            Patch(facecolor=self.color_female, edgecolor='black', label='Feminino')
        ]
        fig.legend(handles=legend_elements, loc='lower center',
                  ncol=2, frameon=True, fontsize=9, bbox_to_anchor=(0.5, -0.02))

        plt.suptitle('Top 3 Atletas por PageRank em Cada Esporte',
                    fontweight='bold', fontsize=13, y=0.995)

        plt.tight_layout(rect=[0, 0.02, 1, 0.99])

        # Salvar
        pdf_path = self.output_dir / '02_top3_pagerank_by_sport_COMPACT.pdf'
        png_path = self.output_dir / '02_top3_pagerank_by_sport_COMPACT.png'

        fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
        fig.savefig(png_path, format='png', bbox_inches='tight', dpi=300)

        print(f"  ✓ {pdf_path.name}")
        print(f"  ✓ {png_path.name}")

        plt.close()

    def generate_latex_table(self):
        """Gera tabela LaTeX com top 3 por esporte."""
        print("\nGerando tabela LaTeX...")

        sports = sorted(self.df['sport'].unique())

        latex = """\\begin{table}[H]
    \\centering
    \\caption{Top 3 Atletas por PageRank em Cada Esporte}
    \\label{tab:top3_by_sport}
    \\footnotesize
    \\begin{tabular}{llclcc}
        \\toprule
        \\textbf{Esporte} & \\textbf{Gênero} & \\textbf{Rank} & \\textbf{Atleta} & \\textbf{País} & \\textbf{PageRank} \\\\
        \\midrule
"""

        for sport in sports:
            sport_name = self.sport_names.get(sport, sport)
            sport_rankings = self.rankings_df[
                (self.rankings_df['sport'] == sport) &
                (self.rankings_df['rank'] <= 3)
            ]

            for _, row in sport_rankings.iterrows():
                gender_label = 'M' if row['gender'] == 'M' else 'F'
                name = row['athlete_name'].replace('_', ' ')

                latex += f"        {sport_name} & {gender_label} & {row['rank']} & {name} & {row['noc']} & {row['pagerank']:.4f} \\\\\n"

            latex += "        \\midrule\n"

        latex += """        \\bottomrule
    \\end{tabular}
    \\begin{tablenotes}
        \\footnotesize
        \\item Nota: Rankings são independentes por esporte. Valores de PageRank não são comparáveis entre esportes devido a diferenças estruturais.
    \\end{tablenotes}
\\end{table}
"""

        # Salvar
        tex_path = self.output_dir / 'tab_top3_by_sport.tex'
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex)

        print(f"  ✓ {tex_path.name}")

    def generate_summary_stats(self):
        """Estatísticas resumidas."""
        print("\n" + "="*80)
        print("RESUMO: TOP 5 POR ESPORTE")
        print("="*80)

        for sport in sorted(self.df['sport'].unique()):
            sport_name = self.sport_names.get(sport, sport)
            print(f"\n📊 {sport_name}:")

            sport_rankings = self.rankings_df[
                (self.rankings_df['sport'] == sport) &
                (self.rankings_df['rank'] <= 3)
            ]

            for _, row in sport_rankings.iterrows():
                gender_label = 'M' if row['gender'] == 'M' else 'F'
                print(f"  {row['rank']}{gender_label}. {row['athlete_name']:35s} | "
                      f"{row['noc']:3s} | PR: {row['pagerank']:.4f} | "
                      f"Medalhas: {int(row['total_medals'])}")

    def run(self):
        """Executa pipeline completo."""
        print("\n" + "="*80)
        print("RANKINGS DE PAGERANK POR ESPORTE")
        print("="*80)

        self.load_data()
        self.generate_top5_by_sport()
        self.plot_rankings_grid()
        self.plot_rankings_compact()
        self.generate_latex_table()
        self.generate_summary_stats()

        print("\n" + "="*80)
        print("✅ FIGURAS E TABELAS GERADAS")
        print("="*80)
        print(f"\nArquivos criados:")
        print(f"  • {self.output_dir / 'top5_by_sport_gender.csv'}")
        print(f"  • {self.output_dir / '02_top5_pagerank_by_sport.pdf'}")
        print(f"  • {self.output_dir / '02_top3_pagerank_by_sport_COMPACT.pdf'} ← Recomendado")
        print(f"  • {self.output_dir / 'tab_top3_by_sport.tex'}")


if __name__ == "__main__":
    plotter = SportSpecificRankings(
        data_dir='../../results_complete_mining/data',
        output_dir='../../results_complete_mining/figures'
    )

    plotter.run()
