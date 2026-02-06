#!/usr/bin/env python3
"""
Regenera Figura 02 (Top 20 PageRank) usando PERCENTIS normalizados.

Corrige o viés de tamanho de rede, mostrando atletas pela sua posição
relativa dentro de suas próprias redes.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuração LaTeX
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 14,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})


class NormalizedTop20Plotter:
    """Gera visualização normalizada do Top 20."""

    def __init__(self, tables_dir: str, output_dir: str):
        self.tables_dir = Path(tables_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Paleta de cores por esporte
        self.sport_colors = {
            'boxing': '#E63946',
            'judo': '#F77F00',
            'swimming': '#06A77D',
            'athletics': '#2E86AB',
            'basketball': '#9D4EDD',
            'football': '#F72585'
        }

        # Tradução
        self.sport_names = {
            'boxing': 'Boxe',
            'judo': 'Judô',
            'swimming': 'Natação',
            'athletics': 'Atletismo',
            'basketball': 'Basquete',
            'football': 'Futebol'
        }

    def load_data(self):
        """Carrega dados normalizados."""
        print("Carregando dados normalizados...")

        self.top20 = pd.read_csv(self.tables_dir / 'top20_global_normalized.csv')
        self.network_stats = pd.read_csv(self.tables_dir / 'network_size_stats.csv')

        print(f"  ✓ Top 20 carregado ({len(self.top20)} atletas)")
        print(f"  ✓ Estatísticas de {len(self.network_stats)} redes")

    def plot_top20_percentile(self):
        """Plota Top 20 por percentil."""
        print("\nGerando Fig 02 NORMALIZADA (percentil)...")

        fig, ax = plt.subplots(figsize=(10, 11))

        # Preparar dados (inverter para top no topo)
        data = self.top20.copy()
        data = data.iloc[::-1]

        # Adicionar tamanho da rede
        data = data.merge(
            self.network_stats[['network_id', 'n_athletes']],
            on='network_id',
            how='left'
        )

        # Cores por esporte
        colors = [self.sport_colors.get(s.lower(), '#999999') for s in data['sport']]

        # Barras horizontais com PERCENTIL
        y_pos = np.arange(len(data))
        bars = ax.barh(y_pos, data['pagerank_percentile'], color=colors, alpha=0.8,
                      edgecolor='black', linewidth=0.5)

        # Labels
        ax.set_xlabel('Percentil de PageRank (Posição Relativa na Rede)', fontweight='bold')
        ax.set_ylabel('Ranking', fontweight='bold')
        ax.set_title('Top 20 Atletas por Percentil de PageRank (Normalizado)',
                     fontweight='bold', pad=15)
        ax.set_yticks(y_pos)

        # Nome + País + Tamanho da rede
        labels = [f"{row['athlete_name']} ({row['noc']}) [n={int(row['n_athletes'])}]"
                 for _, row in data.iterrows()]
        ax.set_yticklabels(labels, fontsize=8)

        ax.set_xlim(0, 100)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.invert_yaxis()

        # Linha vertical em 99 (top 1%)
        ax.axvline(x=99, color='red', linestyle='--', linewidth=1.5, alpha=0.7,
                  label='Top 1% (Percentil 99)')

        # Legenda de esportes
        from matplotlib.patches import Patch
        legend_sports = [Patch(facecolor=color, edgecolor='black', label=self.sport_names[sport])
                        for sport, color in self.sport_colors.items()]

        # Adicionar linha do percentil 99
        from matplotlib.lines import Line2D
        legend_sports.append(Line2D([0], [0], color='red', linestyle='--', linewidth=1.5,
                                   label='Limiar Top 1%'))

        ax.legend(handles=legend_sports, loc='lower right', frameon=True,
                 fancybox=False, edgecolor='black', ncol=2, fontsize=9)

        # Nota explicativa
        ax.text(0.02, 0.98,
               'Nota: Percentil indica posição relativa dentro da própria rede.\n' +
               'Percentil 100 = melhor atleta da rede, independente do tamanho.\n' +
               '[n=X] = número de atletas na rede de origem.',
               transform=ax.transAxes, fontsize=8, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.tight_layout()

        # Salvar
        pdf_path = self.output_dir / '02_top20_global_pagerank_NORMALIZED.pdf'
        png_path = self.output_dir / '02_top20_global_pagerank_NORMALIZED.png'

        fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
        fig.savefig(png_path, format='png', bbox_inches='tight', dpi=300)

        print(f"  ✓ {pdf_path.name}")
        print(f"  ✓ {png_path.name}")

        plt.close()

    def plot_comparison_raw_vs_normalized(self):
        """Plota comparação: raw vs normalizado."""
        print("\nGerando figura comparativa (raw vs normalized)...")

        # Carregar também o raw
        top20_raw = pd.read_csv(self.tables_dir / 'top20_global_raw.csv')

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))

        # === SUBPLOT 1: RAW (ENVIESADO) ===
        data_raw = top20_raw.head(20).iloc[::-1]
        data_raw = data_raw.merge(
            self.network_stats[['network_id', 'n_athletes']],
            on='network_id',
            how='left'
        )

        colors_raw = [self.sport_colors.get(s.lower(), '#999999') for s in data_raw['sport']]
        y_pos = np.arange(len(data_raw))

        ax1.barh(y_pos, data_raw['pagerank'], color=colors_raw, alpha=0.8,
                edgecolor='black', linewidth=0.5)

        ax1.set_xlabel('PageRank (Valores Brutos)', fontweight='bold')
        ax1.set_ylabel('Ranking', fontweight='bold')
        ax1.set_title('❌ ENVIESADO: Valores Brutos\n(Redes pequenas dominam)',
                     fontweight='bold', pad=15, color='red')
        ax1.set_yticks(y_pos)

        labels_raw = [f"{row['athlete_name']} ({row['noc']}) [n={int(row['n_athletes'])}]"
                     for _, row in data_raw.iterrows()]
        ax1.set_yticklabels(labels_raw, fontsize=8)
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        ax1.invert_yaxis()

        # === SUBPLOT 2: NORMALIZADO (CORRETO) ===
        data_norm = self.top20.iloc[::-1]
        data_norm = data_norm.merge(
            self.network_stats[['network_id', 'n_athletes']],
            on='network_id',
            how='left'
        )

        colors_norm = [self.sport_colors.get(s.lower(), '#999999') for s in data_norm['sport']]

        ax2.barh(y_pos, data_norm['pagerank_percentile'], color=colors_norm, alpha=0.8,
                edgecolor='black', linewidth=0.5)

        ax2.set_xlabel('Percentil de PageRank', fontweight='bold')
        ax2.set_title('✅ CORRETO: Percentis Intra-Rede\n(Posição relativa independente do tamanho)',
                     fontweight='bold', pad=15, color='green')
        ax2.set_yticks(y_pos)

        labels_norm = [f"{row['athlete_name']} ({row['noc']}) [n={int(row['n_athletes'])}]"
                      for _, row in data_norm.iterrows()]
        ax2.set_yticklabels(labels_norm, fontsize=8)
        ax2.set_xlim(0, 100)
        ax2.axvline(x=99, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        ax2.grid(axis='x', alpha=0.3, linestyle='--')
        ax2.invert_yaxis()

        plt.tight_layout()

        # Salvar comparação
        pdf_path = self.output_dir / 'COMPARISON_raw_vs_normalized.pdf'
        png_path = self.output_dir / 'COMPARISON_raw_vs_normalized.png'

        fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
        fig.savefig(png_path, format='png', bbox_inches='tight', dpi=300)

        print(f"  ✓ {pdf_path.name}")
        print(f"  ✓ {png_path.name}")

        plt.close()

    def generate_summary_stats(self):
        """Gera estatísticas resumidas."""
        print("\n" + "="*80)
        print("ESTATÍSTICAS DO TOP 20 NORMALIZADO")
        print("="*80)

        print(f"\n📊 Distribuição por Esporte:")
        sport_counts = self.top20['sport'].value_counts()
        for sport, count in sport_counts.items():
            pct = count / len(self.top20) * 100
            print(f"  {self.sport_names.get(sport, sport):12s}: {count:2d} atletas ({pct:5.1f}%)")

        print(f"\n👥 Distribuição por Gênero:")
        gender_counts = self.top20['gender'].value_counts()
        for gender, count in gender_counts.items():
            pct = count / len(self.top20) * 100
            label = 'Masculino' if gender == 'M' else 'Feminino'
            print(f"  {label:10s}: {count:2d} atletas ({pct:5.1f}%)")

        print(f"\n🏆 Top 5 Atletas:")
        for i, row in self.top20.head(5).iterrows():
            n_athletes = self.network_stats[
                self.network_stats['network_id'] == row['network_id']
            ]['n_athletes'].values[0]
            print(f"  {i+1}. {row['athlete_name']:35s} | {row['sport']:10s} {row['gender']} | "
                  f"Percentil: {row['pagerank_percentile']:6.2f} | Rede: {n_athletes:4d} atletas")

    def run(self):
        """Executa pipeline completo."""
        print("\n" + "="*80)
        print("REGENERAÇÃO DA FIGURA 02 COM NORMALIZAÇÃO")
        print("="*80)

        self.load_data()
        self.plot_top20_percentile()
        self.plot_comparison_raw_vs_normalized()
        self.generate_summary_stats()

        print("\n" + "="*80)
        print("✅ FIGURAS GERADAS")
        print("="*80)
        print(f"\nArquivos criados em: {self.output_dir}")
        print("  • 02_top20_global_pagerank_NORMALIZED.pdf")
        print("  • COMPARISON_raw_vs_normalized.pdf")
        print("\nPróximo passo: Atualizar texto da Seção 4.2.2")


if __name__ == "__main__":
    plotter = NormalizedTop20Plotter(
        tables_dir='../../results_complete_mining/tables',
        output_dir='../../results_complete_mining/figures'
    )

    plotter.run()
