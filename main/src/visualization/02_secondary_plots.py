#!/usr/bin/env python3
"""
Visualizações Secundárias para LaTeX (Prioridade 2)

Gera 5 figuras importantes:
6. CDF de distribuição de pesos
7. PageRank vs Total de Medalhas (scatter)
8. Especialização em ouro por hierarquia
9. Entropia temporal por esporte (box plot)
10. Percentual de nós críticos
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats

# Configuração para LaTeX
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

class SecondaryPlotter:
    """Gerador de visualizações secundárias."""

    def __init__(self, data_dir: str, tables_dir: str, output_dir: str):
        self.data_dir = Path(data_dir)
        self.tables_dir = Path(tables_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Paleta de cores para esportes
        self.sport_colors = {
            'football': '#F72585',
            'basketball': '#9D4EDD',
            'athletics': '#2E86AB',
            'swimming': '#06A77D',
            'judo': '#F77F00',
            'boxing': '#E63946'
        }

        # Dicionário de tradução de esportes
        self.sport_translation = {
            'football': 'Futebol',
            'basketball': 'Basquete',
            'athletics': 'Atletismo',
            'swimming': 'Natação',
            'judo': 'Judô',
            'boxing': 'Boxe'
        }

    def load_data(self):
        """Carrega dados."""
        print("Carregando dados...")

        self.edge_cdf = pd.read_csv(self.data_dir / 'edge_weight_cdf.csv')
        self.pagerank = pd.read_csv(self.data_dir / 'pagerank.csv')
        self.medal_hierarchy = pd.read_csv(self.data_dir / 'medal_profiles_by_hierarchy.csv')
        self.temporal_entropy = pd.read_csv(self.data_dir / 'temporal_entropy.csv')
        self.critical_nodes = pd.read_csv(self.data_dir / 'critical_nodes.csv')

        print(f"  ✓ Dados carregados")

    def save_figure(self, fig, filename: str):
        """Salva figura em PDF e PNG."""
        pdf_path = self.output_dir / f"{filename}.pdf"
        fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)

        png_path = self.output_dir / f"{filename}.png"
        fig.savefig(png_path, format='png', bbox_inches='tight', dpi=300)

        print(f"  ✓ {filename}.pdf + .png")

    def plot_edge_weight_cdf(self):
        """Fig 6: CDF de distribuição de pesos."""
        print("\nGerando Fig 6: CDF de Pesos...")

        fig, ax = plt.subplots(figsize=(8, 5))

        # Mapear network_id para nome curto
        event_names = {
            1: 'Futebol Masc.', 2: 'Futebol Fem.',
            3: 'Basquete Masc.', 4: 'Basquete Fem.',
            5: 'Atletismo 100m Masc.', 6: 'Atletismo 100m Fem.',
            7: 'Natação 100m Livre Masc.', 8: 'Natação 100m Livre Fem.',
            9: 'Judô Masc.', 10: 'Judô Fem.',
            11: 'Boxe Masc.', 12: 'Boxe Fem.'
        }

        # Plotar CDF para cada evento (selecionar apenas alguns para clareza)
        selected_events = [1, 5, 7, 9]  # Alguns exemplos representativos
        colors = ['#F72585', '#2E86AB', '#06A77D', '#F77F00']

        for network_id, color in zip(selected_events, colors):
            event_data = self.edge_cdf[self.edge_cdf['network_id'] == network_id]

            if len(event_data) == 0:
                continue

            event_name = event_names.get(network_id, f'Event {network_id}')

            ax.plot(event_data['weight'], event_data['cdf'],
                   linewidth=2, label=event_name, color=color, alpha=0.8)

        # Labels
        ax.set_xlabel('Peso da Aresta', fontweight='bold')
        ax.set_ylabel('Probabilidade Acumulada', fontweight='bold')
        ax.set_title('Função de Distribuição Acumulada (CDF) de Pesos das Arestas', fontweight='bold', pad=15)
        ax.set_xlim(0, max(self.edge_cdf['weight'].max(), 15))
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.3, linestyle='--')
        ax.legend(frameon=True, fancybox=False, edgecolor='black', loc='lower right')

        # Linhas verticais nos pesos base
        for weight, label in [(2, '2'), (3, '3'), (5, '5')]:
            ax.axvline(x=weight, color='gray', linestyle=':', linewidth=1, alpha=0.5)
            ax.text(weight, 0.05, label, ha='center', fontsize=9, color='gray')

        plt.tight_layout()
        self.save_figure(fig, '06_edge_weight_cdf')
        plt.close()

    def plot_pagerank_vs_medals(self):
        """Fig 7: PageRank vs Total de Medalhas."""
        print("Gerando Fig 7: PageRank vs Medalhas...")

        fig, ax = plt.subplots(figsize=(8, 6))

        # Preparar dados
        data = self.pagerank.copy()

        # Cores por esporte
        colors = [self.sport_colors.get(sport.lower(), '#999999')
                 for sport in data['sport']]

        # Tamanho proporcional ao número de ouros
        sizes = data['gold_medals'] * 50 + 20  # Escala visual

        # Scatter plot
        scatter = ax.scatter(data['total_medals'], data['pagerank'],
                           c=colors, s=sizes, alpha=0.6,
                           edgecolors='black', linewidth=0.5)

        # Linha de regressão
        mask = data['total_medals'].notna() & data['pagerank'].notna()
        x = data.loc[mask, 'total_medals']
        y = data.loc[mask, 'pagerank']

        if len(x) > 0:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            line_x = np.array([x.min(), x.max()])
            line_y = slope * line_x + intercept
            ax.plot(line_x, line_y, 'r--', linewidth=2, alpha=0.7,
                   label=f'Regressão Linear (R²={r_value**2:.3f})')

        # Labels
        ax.set_xlabel('Total de Medalhas', fontweight='bold')
        ax.set_ylabel('PageRank', fontweight='bold')
        ax.set_title('PageRank vs Total de Medalhas', fontweight='bold', pad=15)
        ax.grid(alpha=0.3, linestyle='--')

        # Legenda de esportes
        from matplotlib.patches import Patch
        legend_sports = [Patch(facecolor=color, edgecolor='black', label=self.sport_translation[sport])
                        for sport, color in self.sport_colors.items()]

        # Duas legendas: esportes e regressão
        legend1 = ax.legend(handles=legend_sports, loc='upper left',
                           frameon=True, fancybox=False, edgecolor='black',
                           title='Esporte', ncol=2, fontsize=9)
        ax.add_artist(legend1)

        # Legenda da regressão
        ax.legend(loc='lower right', frameon=True, fancybox=False, edgecolor='black')

        plt.tight_layout()
        self.save_figure(fig, '07_pagerank_vs_medals')
        plt.close()

    def plot_gold_specialization_by_hierarchy(self):
        """Fig 8: Especialização em ouro por hierarquia."""
        print("Gerando Fig 8: Especialização por Hierarquia...")

        fig, ax = plt.subplots(figsize=(7, 5))

        # Dados
        data = self.medal_hierarchy.copy()

        # Ordenar níveis
        level_order = ['Periférica', 'Intermediária', 'Núcleo']
        data['level'] = pd.Categorical(data['level'], categories=level_order, ordered=True)
        data = data.sort_values('level')

        # Cores degradê
        colors = ['#FCA311', '#E85D04', '#DC2F02']

        # Barras
        bars = ax.bar(data['level'], data['gold_specialization'] * 100,
                     color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)

        # Labels
        ax.set_xlabel('Nível Hierárquico da Comunidade', fontweight='bold')
        ax.set_ylabel('Especialização em Ouro (%)', fontweight='bold')
        ax.set_title('Especialização em Medalhas de Ouro por Nível Hierárquico', fontweight='bold', pad=15)
        ax.set_ylim(0, 40)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Anotações de valores
        for i, (bar, val) in enumerate(zip(bars, data['gold_specialization'] * 100)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{val:.1f}%', ha='center', fontsize=11, fontweight='bold')

        plt.tight_layout()
        self.save_figure(fig, '08_gold_specialization_hierarchy')
        plt.close()

    def plot_temporal_entropy_boxplot(self):
        """Fig 9: Entropia temporal por esporte."""
        print("Gerando Fig 9: Entropia Temporal...")

        fig, ax = plt.subplots(figsize=(8, 5))

        # Preparar dados
        data = self.temporal_entropy.copy()

        # Ordenar esportes por entropia média
        sport_order = data.groupby('sport')['temporal_entropy'].mean().sort_values(ascending=False).index.tolist()
        data['sport'] = pd.Categorical(data['sport'], categories=sport_order, ordered=True)

        # Box plot
        sports = data['sport'].unique()
        colors = [self.sport_colors.get(s.lower(), '#999999') for s in sports]

        bp = ax.boxplot([data[data['sport'] == sport]['temporal_entropy'].values for sport in sports],
                       labels=[self.sport_translation.get(s.lower(), s.capitalize()) for s in sports],
                       patch_artist=True,
                       widths=0.6,
                       medianprops=dict(color='red', linewidth=2),
                       boxprops=dict(edgecolor='black', linewidth=1),
                       whiskerprops=dict(color='black', linewidth=1),
                       capprops=dict(color='black', linewidth=1))

        # Colorir boxes
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        # Labels
        ax.set_xlabel('Esporte', fontweight='bold')
        ax.set_ylabel('Entropia de Shannon', fontweight='bold')
        ax.set_title('Diversidade Temporal das Comunidades por Esporte', fontweight='bold', pad=15)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()
        self.save_figure(fig, '09_temporal_entropy_boxplot')
        plt.close()

    def plot_critical_nodes_percentage(self):
        """Fig 10: Percentual de nós críticos."""
        print("Gerando Fig 10: Nós Críticos...")

        fig, ax = plt.subplots(figsize=(8, 6))

        # Ordenar por percentual
        data = self.critical_nodes.sort_values('critical_nodes_pct', ascending=True)

        # Cores por gênero
        colors = ['#2E86AB' if 'Masc.' in event else '#E63946' for event in data['event']]

        # Barras horizontais
        y_pos = np.arange(len(data))
        bars = ax.barh(y_pos, data['critical_nodes_pct'], color=colors,
                      alpha=0.8, edgecolor='black', linewidth=0.5)

        # Labels
        ax.set_xlabel('Percentual de Nós Críticos (%)', fontweight='bold')
        ax.set_ylabel('Evento', fontweight='bold')
        ax.set_title('Percentual de Nós Críticos (Articulação) por Evento', fontweight='bold', pad=15)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(data['event'], fontsize=9)
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        # Legenda
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#2E86AB', edgecolor='black', label='Masculino'),
            Patch(facecolor='#E63946', edgecolor='black', label='Feminino')
        ]
        ax.legend(handles=legend_elements, loc='lower right', frameon=True,
                 fancybox=False, edgecolor='black')

        # Anotações de valores para os maiores
        for i, (idx, row) in enumerate(data.iterrows()):
            if row['critical_nodes_pct'] > 5:  # Destacar > 5%
                ax.text(row['critical_nodes_pct'] + 0.5, i,
                       f"{row['critical_nodes_pct']:.1f}%",
                       va='center', fontsize=9, fontweight='bold')

        plt.tight_layout()
        self.save_figure(fig, '10_critical_nodes_percentage')
        plt.close()

    def run(self):
        """Gera todas as visualizações."""
        print("\n" + "="*100)
        print("GERAÇÃO DE VISUALIZAÇÕES SECUNDÁRIAS PARA LATEX")
        print("="*100)

        self.load_data()

        self.plot_edge_weight_cdf()
        self.plot_pagerank_vs_medals()
        self.plot_gold_specialization_by_hierarchy()
        self.plot_temporal_entropy_boxplot()
        self.plot_critical_nodes_percentage()

        print("\n" + "="*100)
        print("VISUALIZAÇÕES SECUNDÁRIAS GERADAS!")
        print(f"Localização: {self.output_dir}")
        print("="*100)


if __name__ == "__main__":
    plotter = SecondaryPlotter(
        data_dir='../../results_complete_mining/data',
        tables_dir='../../results_complete_mining/tables',
        output_dir='../../results_complete_mining/figures'
    )

    plotter.run()
