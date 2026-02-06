#!/usr/bin/env python3
"""
Visualizações Essenciais para LaTeX (Prioridade 1)

Gera 5 figuras fundamentais:
1. Comparação de densidade M vs F
2. Top 20 Global PageRank
3. Índice de segregação por evento
4. Evolução da concentração geográfica
5. Impacto de remoção de nós (resiliência)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

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
    'pdf.fonttype': 42,  # TrueType fonts
    'ps.fonttype': 42,
})

class EssentialPlotter:
    """Gerador de visualizações essenciais."""

    def __init__(self, data_dir: str, output_dir: str):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Paleta de cores
        self.color_male = '#2E86AB'    # Azul
        self.color_female = '#E63946'  # Coral
        self.color_random = '#06A77D'  # Verde
        self.color_targeted = '#D62828' # Vermelho escuro

    def load_data(self):
        """Carrega todos os dados necessários."""
        print("Carregando dados...")

        self.gender_comp = pd.read_csv(self.data_dir / 'gender_comparisons.csv')
        self.top20 = pd.read_csv(self.data_dir.parent / 'tables' / 'top20_global.csv')
        self.segregation = pd.read_csv(self.data_dir / 'community_segregation.csv')
        self.noc_concentration = pd.read_csv(self.data_dir / 'noc_concentration_by_era.csv')
        self.resilience = pd.read_csv(self.data_dir / 'resilience_simulation.csv')

        print(f"  ✓ Dados carregados")

    def save_figure(self, fig, filename: str):
        """Salva figura em PDF e PNG."""
        # PDF (vetorial)
        pdf_path = self.output_dir / f"{filename}.pdf"
        fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)

        # PNG (raster)
        png_path = self.output_dir / f"{filename}.png"
        fig.savefig(png_path, format='png', bbox_inches='tight', dpi=300)

        print(f"  ✓ {filename}.pdf + .png")

    def plot_density_comparison(self):
        """Fig 1: Comparação de densidade M vs F."""
        print("\nGerando Fig 1: Densidade M vs F...")

        fig, ax = plt.subplots(figsize=(8, 5))

        # Dicionário de tradução
        sport_translation = {
            'football': 'Futebol',
            'basketball': 'Basquete',
            'athletics': 'Atletismo',
            'swimming': 'Natação',
            'judo': 'Judô',
            'boxing': 'Boxe'
        }

        # Preparar dados
        sports_raw = self.gender_comp['sport'].values
        sports = [sport_translation.get(s.lower(), s) for s in sports_raw]
        m_density = self.gender_comp['m_density'].values
        f_density = self.gender_comp['f_density'].values

        x = np.arange(len(sports))
        width = 0.35

        # Barras
        bars1 = ax.bar(x - width/2, m_density, width, label='Masculino',
                      color=self.color_male, alpha=0.8, edgecolor='black', linewidth=0.5)
        bars2 = ax.bar(x + width/2, f_density, width, label='Feminino',
                      color=self.color_female, alpha=0.8, edgecolor='black', linewidth=0.5)

        # Labels
        ax.set_xlabel('Esporte', fontweight='bold')
        ax.set_ylabel('Densidade', fontweight='bold')
        ax.set_title('Comparação de Densidade: Masculino vs Feminino', fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(sports, rotation=45, ha='right')
        ax.legend(frameon=True, fancybox=False, edgecolor='black')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Anotações de ratio em casos extremos
        for i, sport in enumerate(sports):
            ratio = self.gender_comp.loc[i, 'density_ratio']
            if ratio > 5:  # Destacar ratios muito grandes
                ax.annotate(f'{ratio:.1f}x', xy=(i + width/2, f_density[i]),
                           xytext=(0, 5), textcoords='offset points',
                           ha='center', fontsize=9, color='red', fontweight='bold')

        plt.tight_layout()
        self.save_figure(fig, '01_density_comparison_mf')
        plt.close()

    def plot_top20_global(self):
        """Fig 2: Top 20 Global PageRank."""
        print("Gerando Fig 2: Top 20 Global PageRank...")

        fig, ax = plt.subplots(figsize=(8, 10))

        # Preparar dados (inverter ordem para top no topo)
        data = self.top20.copy()
        data = data.iloc[::-1]  # Reverter

        # Cores por esporte
        sport_colors = {
            'boxing': '#E63946',
            'judo': '#F77F00',
            'swimming': '#06A77D',
            'athletics': '#2E86AB',
            'basketball': '#9D4EDD',
            'football': '#F72585'
        }

        # Tradução dos nomes de esportes
        sport_names = {
            'boxing': 'Boxe',
            'judo': 'Judô',
            'swimming': 'Natação',
            'athletics': 'Atletismo',
            'basketball': 'Basquete',
            'football': 'Futebol'
        }

        colors = [sport_colors.get(s.lower(), '#999999') for s in data['sport']]

        # Barras horizontais
        y_pos = np.arange(len(data))
        bars = ax.barh(y_pos, data['pagerank'], color=colors, alpha=0.8,
                      edgecolor='black', linewidth=0.5)

        # Labels
        ax.set_xlabel('PageRank', fontweight='bold')
        ax.set_ylabel('Ranking', fontweight='bold')
        ax.set_title('Top 20 Atletas Globais por PageRank', fontweight='bold', pad=15)
        ax.set_yticks(y_pos)

        # Nome + País
        labels = [f"{row['athlete_name']} ({row['noc']})"
                 for _, row in data.iterrows()]
        ax.set_yticklabels(labels, fontsize=9)

        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.invert_yaxis()

        # Legenda de esportes
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color, edgecolor='black', label=sport_names[sport])
                          for sport, color in sport_colors.items()]
        ax.legend(handles=legend_elements, loc='lower right', frameon=True,
                 fancybox=False, edgecolor='black', ncol=2)

        plt.tight_layout()
        self.save_figure(fig, '02_top20_global_pagerank')
        plt.close()

    def plot_segregation_index(self):
        """Fig 3: Índice de segregação por evento."""
        print("Gerando Fig 3: Índice de Segregação...")

        fig, ax = plt.subplots(figsize=(8, 6))

        # Calcular média por evento
        seg_avg = self.segregation.groupby('network_id').agg({
            'segregation_index': lambda x: x.replace([np.inf], 100).mean(),
            'intra_fraction': 'mean'
        }).reset_index()

        # Mapear network_id para nome de evento
        event_names = {
            1: 'Futebol Masc.', 2: 'Futebol Fem.',
            3: 'Basquete Masc.', 4: 'Basquete Fem.',
            5: 'Atletismo 100m Masc.', 6: 'Atletismo 100m Fem.',
            7: 'Natação 100m Livre Masc.', 8: 'Natação 100m Livre Fem.',
            9: 'Judô -90kg Masc.', 10: 'Judô -70kg Fem.',
            11: 'Boxe Welter Masc.', 12: 'Boxe Médio Fem.'
        }
        seg_avg['event'] = seg_avg['network_id'].map(event_names)

        # Ordenar por segregação
        seg_avg = seg_avg.sort_values('segregation_index', ascending=True)

        # Cores por gênero
        colors = [self.color_male if 'Masc.' in name else self.color_female
                 for name in seg_avg['event']]

        # Barras horizontais
        y_pos = np.arange(len(seg_avg))
        bars = ax.barh(y_pos, seg_avg['segregation_index'], color=colors,
                      alpha=0.8, edgecolor='black', linewidth=0.5)

        # Labels
        ax.set_xlabel('Índice de Segregação (Intra / Inter)', fontweight='bold')
        ax.set_ylabel('Evento', fontweight='bold')
        ax.set_title('Índice de Segregação Estrutural por Evento', fontweight='bold', pad=15)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(seg_avg['event'], fontsize=9)
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        # Linha vertical em 1.0 (equilíbrio)
        ax.axvline(x=1.0, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Equilíbrio (1.0)')

        # Legenda
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.color_male, edgecolor='black', label='Masculino'),
            Patch(facecolor=self.color_female, edgecolor='black', label='Feminino')
        ]
        ax.legend(handles=legend_elements, loc='lower right', frameon=True,
                 fancybox=False, edgecolor='black')

        plt.tight_layout()
        self.save_figure(fig, '03_segregation_index')
        plt.close()

    def plot_noc_concentration_evolution(self):
        """Fig 4: Evolução da concentração geográfica."""
        print("Gerando Fig 4: Concentração Geográfica Temporal...")

        fig, ax = plt.subplots(figsize=(8, 5))

        # Calcular média e desvio padrão por era
        evolution = self.noc_concentration.groupby('era')['top3_concentration'].agg(['mean', 'std']).reset_index()

        # Ordenar eras cronologicamente
        era_order = ['Pioneira', 'Pos-Guerra', 'Moderna', 'Contemporanea']
        evolution['era'] = pd.Categorical(evolution['era'], categories=era_order, ordered=True)
        evolution = evolution.sort_values('era')

        # Linha principal
        x = np.arange(len(evolution))
        ax.plot(x, evolution['mean'], marker='o', linewidth=2.5,
               color='#2E86AB', markersize=8, label='Concentração Média (Top 3)')

        # Área de desvio padrão
        ax.fill_between(x,
                        evolution['mean'] - evolution['std'],
                        evolution['mean'] + evolution['std'],
                        alpha=0.3, color='#2E86AB', label='± 1 Desvio Padrão')

        # Labels
        ax.set_xlabel('Era Olímpica', fontweight='bold')
        ax.set_ylabel('% de Medalhas (Top 3 Países)', fontweight='bold')
        ax.set_title('Evolução da Concentração Geográfica ao Longo das Eras', fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(evolution['era'])
        ax.set_ylim(0, 100)
        ax.grid(alpha=0.3, linestyle='--')
        ax.legend(frameon=True, fancybox=False, edgecolor='black')

        # Anotações de valores
        for i, row in evolution.iterrows():
            ax.annotate(f"{row['mean']:.1f}%",
                       xy=(i, row['mean']),
                       xytext=(0, 10), textcoords='offset points',
                       ha='center', fontsize=9, fontweight='bold')

        plt.tight_layout()
        self.save_figure(fig, '04_noc_concentration_evolution')
        plt.close()

    def plot_resilience_removal_impact(self):
        """Fig 5: Impacto de remoção de nós."""
        print("Gerando Fig 5: Impacto de Remoção (Resiliência)...")

        fig, ax = plt.subplots(figsize=(10, 6))

        # Filtrar apenas remoção de 10%
        data = self.resilience[self.resilience['removal_fraction'] == 0.10].copy()

        # Mapear network_id para nome
        event_names = {
            1: 'Futebol Masc.', 2: 'Futebol Fem.',
            3: 'Basquete Masc.', 4: 'Basquete Fem.',
            5: 'Atletismo 100m Masc.', 6: 'Atletismo 100m Fem.',
            7: 'Natação 100m Livre Masc.', 8: 'Natação 100m Livre Fem.',
            9: 'Judô Masc.', 10: 'Judô Fem.',
            11: 'Boxe Masc.', 12: 'Boxe Fem.'
        }
        data['event'] = data['network_id'].map(event_names)

        # Pivotar para ter random e targeted lado a lado
        pivot = data.pivot(index='event', columns='removal_strategy', values='component_increase')
        pivot = pivot.reset_index()

        # Ordenar por impacto targeted
        pivot = pivot.sort_values('targeted', ascending=False)

        # Barras agrupadas
        x = np.arange(len(pivot))
        width = 0.35

        bars1 = ax.bar(x - width/2, pivot['random'], width, label='Remoção Aleatória',
                      color=self.color_random, alpha=0.8, edgecolor='black', linewidth=0.5)
        bars2 = ax.bar(x + width/2, pivot['targeted'], width, label='Remoção Dirigida',
                      color=self.color_targeted, alpha=0.8, edgecolor='black', linewidth=0.5)

        # Labels
        ax.set_xlabel('Evento', fontweight='bold')
        ax.set_ylabel('Aumento no Número de Componentes', fontweight='bold')
        ax.set_title('Impacto da Remoção de 10% dos Nós: Aleatória vs Dirigida', fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(pivot['event'], rotation=45, ha='right', fontsize=9)
        ax.legend(frameon=True, fancybox=False, edgecolor='black')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()
        self.save_figure(fig, '05_resilience_removal_impact')
        plt.close()

    def run(self):
        """Gera todas as visualizações."""
        print("\n" + "="*100)
        print("GERAÇÃO DE VISUALIZAÇÕES ESSENCIAIS PARA LATEX")
        print("="*100)

        self.load_data()

        self.plot_density_comparison()
        self.plot_top20_global()
        self.plot_segregation_index()
        self.plot_noc_concentration_evolution()
        self.plot_resilience_removal_impact()

        print("\n" + "="*100)
        print("VISUALIZAÇÕES ESSENCIAIS GERADAS!")
        print(f"Localização: {self.output_dir}")
        print("="*100)


if __name__ == "__main__":
    plotter = EssentialPlotter(
        data_dir='../../results_complete_mining/data',
        output_dir='../../results_complete_mining/figures'
    )

    plotter.run()
