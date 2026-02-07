"""
Plots: visualizações reutilizáveis para dashboard e exportação LaTeX.

FONTE ÚNICA DE VERDADE para todas as visualizações.
Suporta modo interativo (Plotly) e estático (Matplotlib).
"""

import sys
from pathlib import Path
from typing import Union, Optional, List, Dict, Any

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Adicionar src ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config.styles import (
    COLORS,
    UFOP_CATEGORICAL,
    WINE_GRADIENT,
    GRAY_GRADIENT,
    UFOP_WINE,
    UFOP_GRAY,
)
from .base import create_plotly_figure, create_matplotlib_figure, format_tooltip


# ============================================================================
# SCATTER PLOTS
# ============================================================================

def scatter_size_vs_pagerank(
    df: pd.DataFrame,
    interactive: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6)
) -> Union[go.Figure, matplotlib.figure.Figure]:
    """
    Scatter plot: Tamanho da comunidade vs PageRank médio.

    Análise de hierarquia estrutural.

    Args:
        df: DataFrame com colunas 'size', 'pagerank_mean', 'hierarchy_level', 'sport', 'sex'
        interactive: Se True, usa Plotly. Se False, usa Matplotlib.
        save_path: Caminho para salvar figura (opcional)
        figsize: Tamanho da figura para Matplotlib

    Returns:
        Figura Plotly ou Matplotlib
    """
    # Normalizar hierarchy_level (remover acentos)
    df = df.copy()
    df['hierarchy_level'] = df['hierarchy_level'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    if interactive:
        # Plotly
        fig = create_plotly_figure(
            title='Hierarquia de Comunidades: Tamanho vs PageRank Médio',
            xaxis_title='Tamanho da Comunidade (atletas)',
            yaxis_title='PageRank Médio'
        )

        # Mapear cores por hierarquia
        color_map = {
            'Nucleo': COLORS.get('Nucleo', UFOP_WINE),
            'Intermediaria': COLORS.get('Intermediaria', UFOP_GRAY),
            'Periferica': COLORS.get('Periferica', COLORS.get('Periferica', '#8A8A8A')),
        }

        # Mapa de nomes com acento para legenda
        label_map = {
            'Periferica': 'Periférica',
            'Intermediaria': 'Intermediária',
            'Nucleo': 'Núcleo'
        }

        # Scatter por hierarquia
        for hierarchy_level in ['Periferica', 'Intermediaria', 'Nucleo']:
            subset = df[df['hierarchy_level'] == hierarchy_level]

            if len(subset) == 0:
                continue

            # Criar hover text
            hover_texts = []
            for _, row in subset.iterrows():
                text = f"<b>{row.get('sport', 'N/A')} {row.get('sex', 'N/A')}</b><br>"
                text += f"Comunidade: C{row.get('community_id', 'N/A')}<br>"
                text += f"Tamanho: {row['size']}<br>"
                text += f"PageRank Médio: {row['pagerank_mean']:.6f}<br>"
                text += f"Hierarquia: {label_map[hierarchy_level]}"
                hover_texts.append(text)

            fig.add_trace(go.Scatter(
                x=subset['size'],
                y=subset['pagerank_mean'],
                mode='markers',
                name=label_map[hierarchy_level],  # Nome com acento na legenda
                marker=dict(
                    size=10,
                    color=color_map[hierarchy_level],
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                hovertext=hover_texts,
                hoverinfo='text'
            ))

        # Calcular estatísticas por hierarquia para anotações
        stats_by_hierarchy = {}
        for hierarchy_level in ['Periferica', 'Intermediaria', 'Nucleo']:
            subset = df[df['hierarchy_level'] == hierarchy_level]
            if len(subset) > 0:
                stats_by_hierarchy[hierarchy_level] = {
                    'mean_pagerank': subset['pagerank_mean'].mean(),
                    'mean_size': subset['size'].mean(),
                    'count': len(subset)
                }

        # Adicionar anotação com resumo de hierarquias
        if stats_by_hierarchy:
            annotation_text = "<b>Estrutura Hierárquica:</b><br>"
            label_map_inv = {'Periferica': 'Periférica', 'Intermediaria': 'Intermediária', 'Nucleo': 'Núcleo'}

            for hierarchy_level in ['Nucleo', 'Intermediaria', 'Periferica']:
                if hierarchy_level in stats_by_hierarchy:
                    stats = stats_by_hierarchy[hierarchy_level]
                    annotation_text += (f"{label_map_inv[hierarchy_level]}: {stats['count']} comunidades<br>"
                                      f"  PR médio: {stats['mean_pagerank']:.6f}<br>")

            fig.add_annotation(
                x=0.02,
                y=0.98,
                xref="paper",
                yref="paper",
                text=annotation_text.rstrip('<br>'),
                showarrow=False,
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="#8B2635",
                borderwidth=2,
                borderpad=8,
                font=dict(size=10),
                align="left",
                xanchor="left",
                yanchor="top"
            )

            # Adicionar insight sobre relação tamanho-pagerank
            if 'Nucleo' in stats_by_hierarchy and 'Periferica' in stats_by_hierarchy:
                nucleo_pr = stats_by_hierarchy['Nucleo']['mean_pagerank']
                periferia_pr = stats_by_hierarchy['Periferica']['mean_pagerank']
                pr_ratio = nucleo_pr / periferia_pr if periferia_pr > 0 else 0

                fig.add_annotation(
                    x=0.98,
                    y=0.02,
                    xref="paper",
                    yref="paper",
                    text=f"<b>Hierarquia de Prestígio:</b><br>Núcleo tem PageRank {pr_ratio:.1f}× maior<br>que a Periférica",
                    showarrow=False,
                    bgcolor="rgba(255, 232, 237, 0.9)",
                    bordercolor="#8B2635",
                    borderwidth=2,
                    borderpad=8,
                    font=dict(size=11),
                    align="right",
                    xanchor="right",
                    yanchor="bottom"
                )

        if save_path:
            fig.write_html(save_path) if save_path.endswith('.html') else fig.write_image(save_path)

        return fig

    else:
        # Matplotlib
        fig, ax = create_matplotlib_figure(figsize=figsize)

        # Mapear cores por hierarquia
        color_map = {
            'Nucleo': COLORS.get('Nucleo', UFOP_WINE),
            'Intermediaria': COLORS.get('Intermediaria', UFOP_GRAY),
            'Periferica': COLORS.get('Periferica', '#8A8A8A'),
        }

        # Mapa de nomes com acento para legenda
        label_map = {
            'Periferica': 'Periférica',
            'Intermediaria': 'Intermediária',
            'Nucleo': 'Núcleo'
        }

        for hierarchy_level in ['Periferica', 'Intermediaria', 'Nucleo']:
            subset = df[df['hierarchy_level'] == hierarchy_level]

            if len(subset) == 0:
                continue

            ax.scatter(
                subset['size'],
                subset['pagerank_mean'],
                label=label_map[hierarchy_level],  # Nome com acento na legenda
                color=color_map[hierarchy_level],
                alpha=0.7,
                s=100,
                edgecolors='white',
                linewidths=1
            )

        ax.set_xlabel('Tamanho da Comunidade (atletas)')
        ax.set_ylabel('PageRank Médio')
        ax.set_title('Hierarquia de Comunidades: Tamanho vs PageRank Médio')
        ax.legend(title='Nível Hierárquico')
        ax.grid(True, alpha=0.3)

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

        return fig


# ============================================================================
# HISTOGRAMAS
# ============================================================================

def histogram_dominance(
    df: pd.DataFrame,
    interactive: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6),
    bins: int = 20
) -> Union[go.Figure, matplotlib.figure.Figure]:
    """
    Histograma: Distribuição do índice de dominância.

    Args:
        df: DataFrame com coluna 'dominance_index'
        interactive: Se True, usa Plotly. Se False, usa Matplotlib.
        save_path: Caminho para salvar figura
        figsize: Tamanho da figura para Matplotlib
        bins: Número de bins

    Returns:
        Figura Plotly ou Matplotlib
    """
    if interactive:
        # Plotly
        fig = create_plotly_figure(
            title='Distribuição do Índice de Dominância',
            xaxis_title='Índice de Dominância',
            yaxis_title='Frequência'
        )

        fig.add_trace(go.Histogram(
            x=df['dominance_index'],
            nbinsx=bins,
            marker_color=UFOP_WINE,
            opacity=0.7,
            name='Dominância'
        ))

        # Adicionar linhas verticais para thresholds
        from core.config.constants import DOMINANCE_THRESHOLDS

        fig.add_vline(
            x=DOMINANCE_THRESHOLDS['Elite'],
            line_dash="dash",
            line_color=UFOP_GRAY,
            annotation_text="Elite",
            annotation_position="top"
        )

        fig.add_vline(
            x=DOMINANCE_THRESHOLDS['Competitiva_min'],
            line_dash="dash",
            line_color=UFOP_GRAY,
            annotation_text="Competitiva",
            annotation_position="top"
        )

        # Calcular percentuais por categoria
        dominance_values = df['dominance_index'].dropna()
        total = len(dominance_values)

        if total > 0:
            participante_pct = (dominance_values < DOMINANCE_THRESHOLDS['Participante']).sum() / total * 100
            competitiva_pct = ((dominance_values >= DOMINANCE_THRESHOLDS['Competitiva_min']) &
                             (dominance_values < DOMINANCE_THRESHOLDS['Elite'])).sum() / total * 100
            elite_pct = (dominance_values >= DOMINANCE_THRESHOLDS['Elite']).sum() / total * 100

            # Adicionar anotação com resumo de distribuição
            fig.add_annotation(
                x=0.98,
                y=0.95,
                xref="paper",
                yref="paper",
                text=(f"<b>Perfis de Dominância:</b><br>"
                      f"Participante (D < 1.8): {participante_pct:.1f}%<br>"
                      f"Competitiva (1.8 ≤ D < 2.2): {competitiva_pct:.1f}%<br>"
                      f"Elite (D ≥ 2.2): {elite_pct:.1f}%"),
                showarrow=False,
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="#8B2635",
                borderwidth=2,
                borderpad=8,
                font=dict(size=11),
                align="left",
                xanchor="right",
                yanchor="top"
            )

            # Adicionar anotação do perfil dominante
            dominant_profile = max(
                [('Participante', participante_pct),
                 ('Competitiva', competitiva_pct),
                 ('Elite', elite_pct)],
                key=lambda x: x[1]
            )

            fig.add_annotation(
                x=0.02,
                y=0.95,
                xref="paper",
                yref="paper",
                text=f"<b>Perfil Dominante:</b><br>{dominant_profile[0]} ({dominant_profile[1]:.1f}%)",
                showarrow=False,
                bgcolor="rgba(255, 232, 237, 0.9)",
                bordercolor="#8B2635",
                borderwidth=2,
                borderpad=8,
                font=dict(size=11),
                align="left",
                xanchor="left",
                yanchor="top"
            )

        if save_path:
            fig.write_html(save_path) if save_path.endswith('.html') else fig.write_image(save_path)

        return fig

    else:
        # Matplotlib
        fig, ax = create_matplotlib_figure(figsize=figsize)

        ax.hist(
            df['dominance_index'],
            bins=bins,
            color=UFOP_WINE,
            alpha=0.7,
            edgecolor='white'
        )

        # Adicionar linhas verticais para thresholds
        from core.config.constants import DOMINANCE_THRESHOLDS

        ax.axvline(
            DOMINANCE_THRESHOLDS['Elite'],
            color=UFOP_GRAY,
            linestyle='--',
            label='Elite'
        )

        ax.axvline(
            DOMINANCE_THRESHOLDS['Competitiva_min'],
            color=UFOP_GRAY,
            linestyle='--',
            label='Competitiva'
        )

        ax.set_xlabel('Índice de Dominância')
        ax.set_ylabel('Frequência')
        ax.set_title('Distribuição do Índice de Dominância')
        ax.legend()
        ax.grid(True, alpha=0.3)

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

        return fig


# ============================================================================
# HEATMAPS
# ============================================================================

def heatmap_segregation(
    df: pd.DataFrame,
    interactive: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (8, 6)
) -> Union[go.Figure, matplotlib.figure.Figure]:
    """
    Heatmap: Segregação estrutural por esporte e sexo.

    Args:
        df: DataFrame com colunas 'sport', 'sex', 'segregation_score'
        interactive: Se True, usa Plotly. Se False, usa Matplotlib.
        save_path: Caminho para salvar figura
        figsize: Tamanho da figura para Matplotlib

    Returns:
        Figura Plotly ou Matplotlib
    """
    # Preparar dados em formato pivotado
    pivot = df.pivot_table(
        values='segregation_score',
        index='sport',
        columns='sex',
        aggfunc='mean'
    )

    if interactive:
        # Plotly
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale=[
                [0, GRAY_GRADIENT[0]],    # Baixa segregação (claro)
                [0.5, WINE_GRADIENT[3]],  # Média
                [1, WINE_GRADIENT[6]]     # Alta segregação (escuro)
            ],
            text=pivot.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 12},
            colorbar=dict(title="Score de<br>Segregação")
        ))

        fig.update_layout(
            title='Segregação Estrutural por Esporte e Sexo',
            xaxis_title='Sexo',
            yaxis_title='Esporte',
            template='plotly_white'
        )

        # Calcular estatísticas para anotações
        max_val = pivot.values.max()
        min_val = pivot.values.min()
        mean_val = pivot.values.mean()

        # Encontrar posição do máximo
        max_pos = np.unravel_index(np.argmax(pivot.values), pivot.values.shape)
        max_sport = pivot.index[max_pos[0]]
        max_sex = pivot.columns[max_pos[1]]

        # Encontrar posição do mínimo
        min_pos = np.unravel_index(np.argmin(pivot.values), pivot.values.shape)
        min_sport = pivot.index[min_pos[0]]
        min_sex = pivot.columns[min_pos[1]]

        # Adicionar anotação com estatísticas
        fig.add_annotation(
            x=1.15,
            y=0.95,
            xref="paper",
            yref="paper",
            text=(f"<b>Segregação:</b><br>"
                  f"Máxima: {max_val:.2f}<br>"
                  f"({max_sport} {max_sex})<br><br>"
                  f"Média: {mean_val:.2f}<br><br>"
                  f"Mínima: {min_val:.2f}<br>"
                  f"({min_sport} {min_sex})"),
            showarrow=False,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#8B2635",
            borderwidth=2,
            borderpad=8,
            font=dict(size=10),
            align="left",
            xanchor="left",
            yanchor="top"
        )

        if save_path:
            fig.write_html(save_path) if save_path.endswith('.html') else fig.write_image(save_path)

        return fig

    else:
        # Matplotlib
        import seaborn as sns

        fig, ax = create_matplotlib_figure(figsize=figsize)

        sns.heatmap(
            pivot,
            annot=True,
            fmt='.2f',
            cmap=sns.color_palette([GRAY_GRADIENT[0], WINE_GRADIENT[3], WINE_GRADIENT[6]], as_cmap=True),
            cbar_kws={'label': 'Score de Segregação'},
            ax=ax
        )

        ax.set_title('Segregação Estrutural por Esporte e Sexo')
        ax.set_xlabel('Sexo')
        ax.set_ylabel('Esporte')

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

        return fig


# ============================================================================
# BARPLOTS
# ============================================================================

def barplot_top_rivalries(
    df: pd.DataFrame,
    top_n: int = 10,
    interactive: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6)
) -> Union[go.Figure, matplotlib.figure.Figure]:
    """
    Barplot: Top N rivalidades estruturais.

    Args:
        df: DataFrame com colunas 'sport', 'sex', 'community_1', 'community_2', 'num_confronts'
        top_n: Número de rivalidades a mostrar
        interactive: Se True, usa Plotly. Se False, usa Matplotlib.
        save_path: Caminho para salvar figura
        figsize: Tamanho da figura para Matplotlib

    Returns:
        Figura Plotly ou Matplotlib
    """
    # Validar DataFrame não vazio
    if df.empty or len(df) == 0:
        # Retornar figura vazia com mensagem
        if interactive:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhuma rivalidade encontrada com os filtros atuais",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=400
            )
            return fig
        else:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "Nenhuma rivalidade encontrada",
                   ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
            return fig

    # Top N por número de confrontos
    top_df = df.nlargest(top_n, 'num_confronts').copy()

    # Validar se ainda há dados após nlargest
    if top_df.empty or len(top_df) == 0:
        if interactive:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhuma rivalidade encontrada com os filtros atuais",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=400
            )
            return fig
        else:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "Nenhuma rivalidade encontrada",
                   ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
            return fig

    # Criar label para rivalidade
    top_df['rivalry_label'] = top_df.apply(
        lambda row: f"{row['sport']} {row['sex']}: C{row['community_1']}-C{row['community_2']}",
        axis=1
    )

    if interactive:
        # Plotly
        fig = create_plotly_figure(
            title=f'Top {top_n} Rivalidades Estruturais',
            xaxis_title='Número de Confrontos',
            yaxis_title='Rivalidade'
        )

        # Cores por esporte
        colors = [COLORS.get(sport, UFOP_GRAY) for sport in top_df['sport']]

        fig.add_trace(go.Bar(
            x=top_df['num_confronts'],
            y=top_df['rivalry_label'],
            orientation='h',
            marker_color=colors,
            opacity=0.8,
            text=top_df['num_confronts'],
            textposition='outside',
            texttemplate='%{text:.0f}'
        ))

        fig.update_layout(yaxis={'categoryorder': 'total ascending'})

        # Calcular estatísticas para anotações
        max_confronts = top_df['num_confronts'].max()
        min_confronts = top_df['num_confronts'].min()
        mean_confronts = top_df['num_confronts'].mean()
        top_rivalry = top_df.iloc[-1]  # Última linha (maior valor)

        # Adicionar anotação com estatísticas
        fig.add_annotation(
            x=0.98,
            y=0.98,
            xref="paper",
            yref="paper",
            text=(f"<b>Estatísticas de Rivalidades:</b><br>"
                  f"Máximo: {max_confronts:.0f} confrontos<br>"
                  f"Média: {mean_confronts:.1f} confrontos<br>"
                  f"Mínimo: {min_confronts:.0f} confrontos"),
            showarrow=False,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#8B2635",
            borderwidth=2,
            borderpad=8,
            font=dict(size=11),
            align="left",
            xanchor="right",
            yanchor="top"
        )

        # Adicionar destaque para rivalidade mais intensa
        fig.add_annotation(
            x=0.02,
            y=0.02,
            xref="paper",
            yref="paper",
            text=(f"<b>Rivalidade Mais Intensa:</b><br>"
                  f"{top_rivalry['sport']} {top_rivalry['sex']}<br>"
                  f"C{top_rivalry['community_1']} vs C{top_rivalry['community_2']}<br>"
                  f"{top_rivalry['num_confronts']:.0f} confrontos"),
            showarrow=False,
            bgcolor="rgba(255, 232, 237, 0.9)",
            bordercolor="#8B2635",
            borderwidth=2,
            borderpad=8,
            font=dict(size=11),
            align="left",
            xanchor="left",
            yanchor="bottom"
        )

        if save_path:
            fig.write_html(save_path) if save_path.endswith('.html') else fig.write_image(save_path)

        return fig

    else:
        # Matplotlib
        fig, ax = create_matplotlib_figure(figsize=figsize)

        # Cores por esporte
        colors = [COLORS.get(sport, UFOP_GRAY) for sport in top_df['sport']]

        y_pos = np.arange(len(top_df))

        ax.barh(y_pos, top_df['num_confronts'], color=colors, alpha=0.8, edgecolor='white')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(top_df['rivalry_label'])
        ax.set_xlabel('Número de Confrontos')
        ax.set_ylabel('Rivalidade')
        ax.set_title(f'Top {top_n} Rivalidades Estruturais')
        ax.grid(axis='x', alpha=0.3)

        # Adicionar valores nas barras
        for i, v in enumerate(top_df['num_confronts']):
            ax.text(v + max(top_df['num_confronts']) * 0.01, i, f'{v:.0f}', va='center')

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

        return fig


# ============================================================================
# CDF / CCDF
# ============================================================================

def cdf_pagerank_by_sport(
    df: pd.DataFrame,
    interactive: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6),
    log_scale: bool = True
) -> Union[go.Figure, matplotlib.figure.Figure]:
    """
    CDF (Cumulative Distribution Function) do PageRank separado por esporte.

    Cria múltiplas curvas (uma para cada esporte) para comparação.

    Args:
        df: DataFrame com colunas 'original_pagerank' e 'sport'
        interactive: Se True, usa Plotly. Se False, usa Matplotlib.
        save_path: Caminho para salvar figura
        figsize: Tamanho da figura para Matplotlib
        log_scale: Se True, usa escala logarítmica (padrão: True para CDF por esporte)

    Returns:
        Figura Plotly ou Matplotlib
    """
    # Cores para cada esporte
    colors = {
        'Football': '#8B2635',      # Vinho UFOP
        'Basketball': '#5A5A5A',    # Cinza
        'Swimming': '#2E8B57'       # Verde mar
    }

    if interactive:
        # Plotly
        fig = create_plotly_figure(
            title='CDF do PageRank por Esporte',
            xaxis_title='PageRank',
            yaxis_title='P(PageRank ≤ x)'
        )

        # Adicionar curva para cada esporte
        for sport in ['Football', 'Basketball', 'Swimming']:
            sport_data = df[df['sport'] == sport]

            if len(sport_data) == 0:
                continue

            # Calcular CDF para este esporte
            sorted_pr = np.sort(sport_data['original_pagerank'].dropna())
            cdf = np.arange(1, len(sorted_pr) + 1) / len(sorted_pr)

            fig.add_trace(go.Scatter(
                x=sorted_pr,
                y=cdf,
                mode='lines',
                line=dict(color=colors.get(sport, '#000000'), width=2.5),
                name=sport
            ))

        # Configurar escala log-log se solicitado
        if log_scale:
            fig.update_xaxes(type='log')
            fig.update_yaxes(type='log')

        # Ajustar layout
        fig.update_layout(
            legend=dict(
                x=0.02,
                y=0.98,
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='#5A5A5A',
                borderwidth=1
            )
        )

        if save_path:
            fig.write_html(save_path) if save_path.endswith('.html') else fig.write_image(save_path)

        return fig

    else:
        # Matplotlib
        fig, ax = plt.subplots(figsize=figsize)

        for sport in ['Football', 'Basketball', 'Swimming']:
            sport_data = df[df['sport'] == sport]

            if len(sport_data) == 0:
                continue

            sorted_pr = np.sort(sport_data['original_pagerank'].dropna())
            cdf = np.arange(1, len(sorted_pr) + 1) / len(sorted_pr)

            ax.plot(sorted_pr, cdf, label=sport,
                   color=colors.get(sport, '#000000'), linewidth=2.5)

        if log_scale:
            ax.set_xscale('log')
            ax.set_yscale('log')

        ax.set_xlabel('PageRank', fontsize=12, fontweight='bold')
        ax.set_ylabel('P(PageRank ≤ x)', fontsize=12, fontweight='bold')
        ax.set_title('CDF do PageRank por Esporte', fontsize=14, fontweight='bold')
        ax.legend(loc='lower right', framealpha=0.9)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            return fig


def cdf_pagerank(
    df: pd.DataFrame,
    interactive: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6),
    log_scale: bool = False
) -> Union[go.Figure, matplotlib.figure.Figure]:
    """
    CDF (Cumulative Distribution Function) do PageRank.

    Args:
        df: DataFrame com coluna 'original_pagerank'
        interactive: Se True, usa Plotly. Se False, usa Matplotlib.
        save_path: Caminho para salvar figura
        figsize: Tamanho da figura para Matplotlib
        log_scale: Se True, usa escala logarítmica no eixo X

    Returns:
        Figura Plotly ou Matplotlib
    """
    # Calcular CDF
    sorted_pr = np.sort(df['original_pagerank'].dropna())
    cdf = np.arange(1, len(sorted_pr) + 1) / len(sorted_pr)

    if interactive:
        # Plotly
        fig = create_plotly_figure(
            title='CDF do PageRank',
            xaxis_title='PageRank',
            yaxis_title='P(PageRank ≤ x)'
        )

        fig.add_trace(go.Scatter(
            x=sorted_pr,
            y=cdf,
            mode='lines',
            line=dict(color=UFOP_WINE, width=2),
            name='CDF'
        ))

        # Calcular percentis importantes
        p50 = np.percentile(sorted_pr, 50)  # Mediana
        p90 = np.percentile(sorted_pr, 90)  # Top 10%
        p95 = np.percentile(sorted_pr, 95)  # Top 5%

        # Adicionar linhas verticais nos percentis
        fig.add_vline(
            x=p50,
            line_dash="dash",
            line_color="#5A5A5A",
            line_width=1,
            annotation_text=f"50% dos atletas<br>PR ≤ {p50:.6f}",
            annotation_position="top right",
            annotation=dict(
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#5A5A5A",
                borderwidth=1
            )
        )

        fig.add_vline(
            x=p90,
            line_dash="dash",
            line_color="#8B2635",
            line_width=1.5,
            annotation_text=f"Top 10%<br>PR > {p90:.6f}",
            annotation_position="top right",
            annotation=dict(
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#8B2635",
                borderwidth=1
            )
        )

        # Adicionar anotação de concentração
        top10_sum = sorted_pr[int(len(sorted_pr) * 0.9):].sum()
        total_sum = sorted_pr.sum()
        concentration_pct = (top10_sum / total_sum * 100) if total_sum > 0 else 0

        fig.add_annotation(
            x=0.98,
            y=0.05,
            xref="paper",
            yref="paper",
            text=f"<b>Concentração Top 10%:</b><br>{concentration_pct:.1f}% do PageRank total",
            showarrow=False,
            bgcolor="rgba(255, 232, 237, 0.9)",
            bordercolor="#8B2635",
            borderwidth=2,
            borderpad=8,
            font=dict(size=11),
            align="right",
            xanchor="right"
        )

        if log_scale:
            fig.update_xaxes(type='log')

        if save_path:
            fig.write_html(save_path) if save_path.endswith('.html') else fig.write_image(save_path)

        return fig

    else:
        # Matplotlib
        fig, ax = create_matplotlib_figure(figsize=figsize)

        ax.plot(sorted_pr, cdf, color=UFOP_WINE, linewidth=2)
        ax.set_xlabel('PageRank')
        ax.set_ylabel('P(PageRank ≤ x)')
        ax.set_title('CDF do PageRank')
        ax.grid(True, alpha=0.3)

        if log_scale:
            ax.set_xscale('log')

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

        return fig


# ============================================================================
# BOXPLOTS
# ============================================================================

def boxplot_metric_by_category(
    df: pd.DataFrame,
    metric_column: str,
    category_column: str,
    interactive: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6),
    title: Optional[str] = None
) -> Union[go.Figure, matplotlib.figure.Figure]:
    """
    Boxplot: Métrica por categoria.

    Args:
        df: DataFrame
        metric_column: Nome da coluna com métrica
        category_column: Nome da coluna com categoria
        interactive: Se True, usa Plotly. Se False, usa Matplotlib.
        save_path: Caminho para salvar figura
        figsize: Tamanho da figura para Matplotlib
        title: Título do gráfico (opcional)

    Returns:
        Figura Plotly ou Matplotlib
    """
    if title is None:
        title = f'{metric_column} por {category_column}'

    if interactive:
        # Plotly
        fig = create_plotly_figure(
            title=title,
            xaxis_title=category_column,
            yaxis_title=metric_column
        )

        categories = df[category_column].unique()

        # Calcular estatísticas por categoria para anotações
        stats_by_cat = {}
        for cat in categories:
            subset = df[df[category_column] == cat][metric_column].dropna()
            if len(subset) > 0:
                stats_by_cat[cat] = {
                    'median': subset.median(),
                    'mean': subset.mean(),
                    'std': subset.std(),
                    'min': subset.min(),
                    'max': subset.max()
                }

        for i, cat in enumerate(categories):
            subset = df[df[category_column] == cat]

            color = UFOP_CATEGORICAL[i % len(UFOP_CATEGORICAL)]

            fig.add_trace(go.Box(
                y=subset[metric_column],
                name=str(cat),
                marker_color=color,
                boxmean='sd'  # Mostrar média e desvio padrão
            ))

        # Adicionar anotações com estatísticas
        if stats_by_cat:
            # Encontrar categoria com maior mediana
            max_median_cat = max(stats_by_cat.items(), key=lambda x: x[1]['median'])
            min_median_cat = min(stats_by_cat.items(), key=lambda x: x[1]['median'])

            # Calcular range global
            global_min = min(s['min'] for s in stats_by_cat.values())
            global_max = max(s['max'] for s in stats_by_cat.values())
            global_range = global_max - global_min

            fig.add_annotation(
                x=0.98,
                y=0.98,
                xref="paper",
                yref="paper",
                text=(f"<b>Comparativo:</b><br>"
                      f"Maior mediana:<br>"
                      f"  {max_median_cat[0]} ({max_median_cat[1]['median']:.4f})<br>"
                      f"Menor mediana:<br>"
                      f"  {min_median_cat[0]} ({min_median_cat[1]['median']:.4f})<br>"
                      f"Range total: {global_range:.4f}"),
                showarrow=False,
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="#8B2635",
                borderwidth=2,
                borderpad=8,
                font=dict(size=10),
                align="left",
                xanchor="right",
                yanchor="top"
            )

        if save_path:
            fig.write_html(save_path) if save_path.endswith('.html') else fig.write_image(save_path)

        return fig

    else:
        # Matplotlib
        fig, ax = create_matplotlib_figure(figsize=figsize)

        categories = df[category_column].unique()
        data_by_cat = [df[df[category_column] == cat][metric_column].dropna() for cat in categories]

        bp = ax.boxplot(
            data_by_cat,
            labels=categories,
            patch_artist=True,
            showmeans=True
        )

        # Colorir boxes
        for i, box in enumerate(bp['boxes']):
            color = UFOP_CATEGORICAL[i % len(UFOP_CATEGORICAL)]
            box.set_facecolor(color)
            box.set_alpha(0.7)

        ax.set_xlabel(category_column)
        ax.set_ylabel(metric_column)
        ax.set_title(title)
        ax.grid(axis='y', alpha=0.3)

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

        return fig
