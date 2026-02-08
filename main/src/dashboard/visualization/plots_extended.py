"""
Extensões de plots: funções adicionais de visualização.

Complementa plots.py com visualizações avançadas.
"""

import sys
from pathlib import Path
from typing import Union, Optional, List, Dict, Any

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
import plotly.graph_objects as go

# Adicionar config ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config.styles import COLORS, UFOP_CATEGORICAL, WINE_GRADIENT, GRAY_GRADIENT, UFOP_WINE, UFOP_GRAY
from .base import create_plotly_figure, create_matplotlib_figure


# ============================================================================
# BARRAS EMPILHADAS
# ============================================================================

def stacked_bar_profile_distribution(
    df: pd.DataFrame,
    interactive: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6)
) -> Union[go.Figure, matplotlib.figure.Figure]:
    """
    Barras empilhadas: Distribuição de perfis competitivos por esporte.

    Args:
        df: DataFrame com colunas 'sport', 'competitive_profile'
        interactive: Se True, usa Plotly. Se False, usa Matplotlib.
        save_path: Caminho para salvar figura
        figsize: Tamanho da figura para Matplotlib

    Returns:
        Figura Plotly ou Matplotlib
    """
    # Contar perfis por esporte
    profile_counts = df.groupby(['sport', 'competitive_profile']).size().unstack(fill_value=0)

    # Calcular percentuais
    profile_pcts = profile_counts.div(profile_counts.sum(axis=1), axis=0) * 100

    if interactive:
        # Plotly
        fig = go.Figure()

        profiles = ['Elite', 'Competitiva', 'Participante']
        colors_profile = {
            'Elite': COLORS.get('Elite', UFOP_WINE),
            'Competitiva': COLORS.get('Competitiva', UFOP_GRAY),
            'Participante': COLORS.get('Participante', '#8A8A8A'),
        }

        for profile in profiles:
            if profile not in profile_pcts.columns:
                continue

            fig.add_trace(go.Bar(
                name=profile,
                x=profile_pcts.index,
                y=profile_pcts[profile],
                marker_color=colors_profile[profile],
                text=profile_pcts[profile].round(1),
                texttemplate='%{text}%',
                textposition='inside'
            ))

        fig.update_layout(
            barmode='stack',
            title='Distribuição de Perfis Competitivos por Esporte',
            xaxis_title='Esporte',
            yaxis_title='Percentual (%)',
            template='plotly_white',
            legend=dict(title='Perfil')
        )

        if save_path:
            fig.write_html(save_path) if save_path.endswith('.html') else fig.write_image(save_path)

        return fig

    else:
        # Matplotlib
        fig, ax = create_matplotlib_figure(figsize=figsize)

        profiles = ['Participante', 'Competitiva', 'Elite']  # Ordem reversa para empilhamento
        colors_profile = {
            'Elite': COLORS.get('Elite', UFOP_WINE),
            'Competitiva': COLORS.get('Competitiva', UFOP_GRAY),
            'Participante': COLORS.get('Participante', '#8A8A8A'),
        }

        bottom = np.zeros(len(profile_pcts))

        for profile in profiles:
            if profile not in profile_pcts.columns:
                continue

            ax.bar(
                profile_pcts.index,
                profile_pcts[profile],
                bottom=bottom,
                label=profile,
                color=colors_profile[profile],
                alpha=0.8
            )

            bottom += profile_pcts[profile].values

        ax.set_xlabel('Esporte')
        ax.set_ylabel('Percentual (%)')
        ax.set_title('Distribuição de Perfis Competitivos por Esporte')
        ax.legend(title='Perfil')
        ax.grid(axis='y', alpha=0.3)

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

        return fig


# ============================================================================
# VIOLIN PLOTS
# ============================================================================

def violin_betweenness_by_event(
    df: pd.DataFrame,
    interactive: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (12, 8)
) -> Union[go.Figure, matplotlib.figure.Figure]:
    """
    Violin plot: Distribuição de betweenness centrality por EVENTO.
    
    Cada violin = um evento específico (não agrega eventos diferentes).

    Args:
        df: DataFrame com colunas 'event_name', 'original_betweenness_centrality', 'sport'
        interactive: Se True, usa Plotly
        save_path: Caminho para salvar figura
        figsize: Tamanho da figura para Matplotlib

    Returns:
        Figura Plotly ou Matplotlib
    """
    if interactive:
        # Plotly
        fig = create_plotly_figure(
            title='Distribuição de Betweenness Centrality por Evento',
            xaxis_title='Evento',
            yaxis_title='Betweenness Centrality'
        )

        # Agrupar por evento e esporte para cor
        if 'event_name' not in df.columns:
            # Fallback: usar sport se event_name não existir
            return violin_betweenness_by_sport(df, interactive, save_path, figsize)
        
        events = sorted(df['event_name'].unique())
        
        # Limitar a 20 eventos para legibilidade (silenciosamente)
        # O warning será exibido no dashboard, não na função de visualização
        if len(events) > 20:
            events = events[:20]
        
        for i, event in enumerate(events):
            subset = df[df['event_name'] == event]
            if len(subset) == 0:
                continue
            
            # Cor por esporte
            sport = subset['sport'].iloc[0] if 'sport' in subset.columns else None
            color = COLORS.get(sport, UFOP_CATEGORICAL[i % len(UFOP_CATEGORICAL)])

            fig.add_trace(go.Violin(
                y=subset['original_betweenness_centrality'],
                name=event,
                box_visible=True,
                meanline_visible=True,
                fillcolor=color,
                opacity=0.6,
                line_color=color
            ))

        # Rotacionar labels se muitos eventos
        fig.update_xaxes(tickangle=-45)

        if save_path:
            fig.write_html(save_path) if save_path.endswith('.html') else fig.write_image(save_path)

        return fig

    else:
        # Matplotlib
        fig, ax = create_matplotlib_figure(figsize=figsize)

        events = sorted(df['event_name'].unique())[:20]  # Limitar
        colors = [UFOP_CATEGORICAL[i % len(UFOP_CATEGORICAL)] for i in range(len(events))]

        parts = ax.violinplot(
            [df[df['event_name'] == event]['original_betweenness_centrality'].dropna() for event in events],
            positions=range(len(events)),
            showmeans=True,
            showmedians=True
        )

        # Colorir violins
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(colors[i])
            pc.set_alpha(0.6)

        ax.set_xticks(range(len(events)))
        ax.set_xticklabels(events, rotation=45, ha='right')
        ax.set_xlabel('Evento')
        ax.set_ylabel('Betweenness Centrality')
        ax.set_title('Distribuição de Betweenness Centrality por Evento')
        
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig


def violin_betweenness_by_sport(
    df: pd.DataFrame,
    interactive: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6)
) -> Union[go.Figure, matplotlib.figure.Figure]:
    """
    Violin plot: Distribuição de betweenness centrality por esporte.

    Args:
        df: DataFrame com colunas 'sport', 'original_betweenness_centrality'
        interactive: Se True, usa Plotly. Se False, usa Matplotlib.
        save_path: Caminho para salvar figura
        figsize: Tamanho da figura para Matplotlib

    Returns:
        Figura Plotly ou Matplotlib
    """
    if interactive:
        # Plotly
        fig = create_plotly_figure(
            title='Distribuição de Betweenness Centrality por Esporte',
            xaxis_title='Esporte',
            yaxis_title='Betweenness Centrality'
        )

        sports = df['sport'].unique()

        for i, sport in enumerate(sports):
            subset = df[df['sport'] == sport]
            color = COLORS.get(sport, UFOP_CATEGORICAL[i % len(UFOP_CATEGORICAL)])

            fig.add_trace(go.Violin(
                y=subset['original_betweenness_centrality'],
                name=sport,
                box_visible=True,
                meanline_visible=True,
                fillcolor=color,
                opacity=0.6,
                line_color=color
            ))

        if save_path:
            fig.write_html(save_path) if save_path.endswith('.html') else fig.write_image(save_path)

        return fig

    else:
        # Matplotlib (usar boxplot como alternativa)
        fig, ax = create_matplotlib_figure(figsize=figsize)

        sports = df['sport'].unique()
        colors = [COLORS.get(sport, UFOP_GRAY) for sport in sports]

        parts = ax.violinplot(
            [df[df['sport'] == sport]['original_betweenness_centrality'].dropna() for sport in sports],
            positions=range(len(sports)),
            showmeans=True,
            showmedians=True
        )

        # Colorir violins
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(colors[i])
            pc.set_alpha(0.6)

        ax.set_xticks(range(len(sports)))
        ax.set_xticklabels(sports)
        ax.set_xlabel('Esporte')
        ax.set_ylabel('Betweenness Centrality')
        ax.set_title('Distribuição de Betweenness Centrality por Esporte')
        ax.grid(axis='y', alpha=0.3)

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

        return fig


# ============================================================================
# LINHAS (EVOLUÇÃO TEMPORAL)
# ============================================================================

def line_pagerank_evolution(
    df: pd.DataFrame,
    athlete_ids: List[int],
    interactive: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (12, 6)
) -> Union[go.Figure, matplotlib.figure.Figure]:
    """
    Linha: Evolução temporal do PageRank de atletas específicos.

    Args:
        df: DataFrame com colunas 'athlete_id', 'year', 'original_pagerank', 'name'
        athlete_ids: Lista de IDs de atletas para plotar
        interactive: Se True, usa Plotly. Se False, usa Matplotlib.
        save_path: Caminho para salvar figura
        figsize: Tamanho da figura para Matplotlib

    Returns:
        Figura Plotly ou Matplotlib
    """
    if interactive:
        # Plotly
        fig = create_plotly_figure(
            title='Evolução do PageRank ao Longo do Tempo',
            xaxis_title='Ano',
            yaxis_title='PageRank'
        )

        for i, athlete_id in enumerate(athlete_ids):
            subset = df[df['athlete_id'] == athlete_id].sort_values('year')

            if len(subset) == 0:
                continue

            athlete_name = subset.iloc[0]['name']
            color = UFOP_CATEGORICAL[i % len(UFOP_CATEGORICAL)]

            fig.add_trace(go.Scatter(
                x=subset['year'],
                y=subset['original_pagerank'],
                mode='lines+markers',
                name=athlete_name,
                line=dict(color=color, width=2),
                marker=dict(size=8)
            ))

        if save_path:
            fig.write_html(save_path) if save_path.endswith('.html') else fig.write_image(save_path)

        return fig

    else:
        # Matplotlib
        fig, ax = create_matplotlib_figure(figsize=figsize)

        for i, athlete_id in enumerate(athlete_ids):
            subset = df[df['athlete_id'] == athlete_id].sort_values('year')

            if len(subset) == 0:
                continue

            athlete_name = subset.iloc[0]['name']
            color = UFOP_CATEGORICAL[i % len(UFOP_CATEGORICAL)]

            ax.plot(
                subset['year'],
                subset['original_pagerank'],
                marker='o',
                label=athlete_name,
                color=color,
                linewidth=2
            )

        ax.set_xlabel('Ano')
        ax.set_ylabel('PageRank')
        ax.set_title('Evolução do PageRank ao Longo do Tempo')
        ax.legend()
        ax.grid(True, alpha=0.3)

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

        return fig


# ============================================================================
# TABELAS INTERATIVAS (PLOTLY)
# ============================================================================

def table_top_athletes(
    df: pd.DataFrame,
    metric_column: str = 'original_pagerank',
    top_n: int = 20,
    interactive: bool = True,
    save_path: Optional[str] = None
) -> Union[go.Figure, str]:
    """
    Tabela: Top N atletas por métrica.

    Args:
        df: DataFrame de atletas
        metric_column: Coluna para ordenar
        top_n: Número de atletas
        interactive: Se True, retorna Plotly Table. Se False, retorna HTML.
        save_path: Caminho para salvar

    Returns:
        Figura Plotly Table ou string HTML
    """
    from core.config.styles import UFOP_GRAY_LIGHT

    # Top N
    top_df = df.nlargest(top_n, metric_column)[['name', 'noc', 'sport', 'sex', metric_column]].copy()

    if interactive:
        # Plotly Table
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Rank', 'Nome', 'País', 'Esporte', 'Sexo', metric_column],
                fill_color=UFOP_WINE,
                font=dict(color='white', size=12),
                align='left'
            ),
            cells=dict(
                values=[
                    list(range(1, len(top_df) + 1)),
                    top_df['name'],
                    top_df['noc'],
                    top_df['sport'],
                    top_df['sex'],
                    top_df[metric_column].round(6)
                ],
                fill_color=[['white', '#F5F5F5'] * len(top_df)],
                font=dict(color='#2A2A2A', size=11),  # Texto preto/escuro
                align='left',
                height=30
            )
        )])

        fig.update_layout(
            title=f'Top {top_n} Atletas por {metric_column}',
            height=600
        )

        if save_path:
            fig.write_html(save_path)

        return fig

    else:
        # HTML simples
        top_df.insert(0, 'Rank', range(1, len(top_df) + 1))
        html = top_df.to_html(index=False, float_format=lambda x: f'{x:.6f}')

        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html)

        return html


# ============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# ============================================================================

def create_all_plots(
    data: Dict[str, pd.DataFrame],
    output_dir: str,
    interactive: bool = True,
    file_format: str = 'html'
):
    """
    Cria todos os plots principais e salva em diretório.

    Args:
        data: Dicionário com DataFrames (retornado por DataLoader.load_all())
        output_dir: Diretório de saída
        interactive: Se True, usa Plotly. Se False, usa Matplotlib.
        file_format: Formato de arquivo ('html' ou 'png')
    """
    from pathlib import Path
    from .plots import (
        scatter_size_vs_pagerank,
        histogram_dominance,
        heatmap_segregation,
        barplot_top_rivalries,
        cdf_pagerank,
        boxplot_metric_by_category
    )

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)

    print("=" * 80)
    print("GERANDO TODAS AS VISUALIZAÇÕES")
    print("=" * 80)

    # 1. Scatter: Size vs PageRank
    print("\n1. Scatter: Tamanho vs PageRank...")
    scatter_size_vs_pagerank(
        data['hierarchy'],
        interactive=interactive,
        save_path=str(output_path / f'scatter_size_pagerank.{file_format}')
    )

    # 2. Histogram: Dominância
    print("2. Histogram: Dominância...")
    histogram_dominance(
        data['medal_profile'],
        interactive=interactive,
        save_path=str(output_path / f'hist_dominance.{file_format}')
    )

    # 3. Heatmap: Segregação
    print("3. Heatmap: Segregação...")
    heatmap_segregation(
        data['connectivity'],
        interactive=interactive,
        save_path=str(output_path / f'heatmap_segregation.{file_format}')
    )

    # 4. Barplot: Rivalidades
    print("4. Barplot: Rivalidades...")
    barplot_top_rivalries(
        data['rivalries'],
        top_n=10,
        interactive=interactive,
        save_path=str(output_path / f'bar_rivalries.{file_format}')
    )

    # 5. CDF: PageRank
    print("5. CDF: PageRank...")
    cdf_pagerank(
        data['athletes'],
        interactive=interactive,
        save_path=str(output_path / f'cdf_pagerank.{file_format}')
    )

    # 6. Boxplot: Dominância por esporte
    print("6. Boxplot: Dominância por Esporte...")
    boxplot_metric_by_category(
        data['medal_profile'],
        metric_column='dominance_index',
        category_column='sport',
        interactive=interactive,
        save_path=str(output_path / f'box_dominance_sport.{file_format}')
    )

    # 7. Stacked Bar: Perfis
    print("7. Stacked Bar: Perfis Competitivos...")
    stacked_bar_profile_distribution(
        data['medal_profile'],
        interactive=interactive,
        save_path=str(output_path / f'stack_profiles.{file_format}')
    )

    # 8. Violin: Betweenness
    print("8. Violin: Betweenness por Esporte...")
    violin_betweenness_by_sport(
        data['athletes'],
        interactive=interactive,
        save_path=str(output_path / f'violin_betweenness.{file_format}')
    )

    # 9. Table: Top atletas
    print("9. Table: Top 20 Atletas...")
    table_top_athletes(
        data['athletes'],
        metric_column='original_pagerank',
        top_n=20,
        interactive=interactive,
        save_path=str(output_path / f'table_top_athletes.{file_format}')
    )

    print("\n" + "=" * 80)
    print("VISUALIZAÇÕES CRIADAS COM SUCESSO")
    print("=" * 80)
    print(f"\nArquivos salvos em: {output_path}")
    print("=" * 80)
