"""
Base classes para visualizações.

Fornece interface comum para gráficos interativos (Plotly) e estáticos (Matplotlib).
"""

import sys
from pathlib import Path
from typing import Union, Optional, Dict, Any
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import matplotlib
import plotly.graph_objects as go

# Adicionar config ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config.styles import (
    PLOT_STYLE_INTERACTIVE,
    PLOT_STYLE_STATIC,
    COLORS,
    UFOP_CATEGORICAL,
    WINE_GRADIENT,
    GRAY_GRADIENT,
)


class BasePlot(ABC):
    """
    Classe base abstrata para visualizações.

    Suporta dois modos:
    - interactive=True: gera gráficos Plotly para dashboard
    - interactive=False: gera gráficos Matplotlib para exportação LaTeX
    """

    def __init__(self, interactive: bool = True):
        """
        Inicializa plot base.

        Args:
            interactive: Se True, usa Plotly. Se False, usa Matplotlib.
        """
        self.interactive = interactive

        if not interactive:
            # Configurar estilo Matplotlib para LaTeX
            self._configure_matplotlib()

    def _configure_matplotlib(self):
        """Configura estilo Matplotlib para publicação em LaTeX."""
        matplotlib.rcParams.update(PLOT_STYLE_STATIC)

    @abstractmethod
    def create(self, *args, **kwargs) -> Union[go.Figure, matplotlib.figure.Figure]:
        """
        Cria visualização.

        Método abstrato a ser implementado por subclasses.

        Returns:
            Plotly Figure (se interactive) ou Matplotlib Figure (se estático)
        """
        pass

    def save(
        self,
        fig: Union[go.Figure, matplotlib.figure.Figure],
        filename: str,
        dpi: int = 300,
        width: Optional[int] = None,
        height: Optional[int] = None
    ):
        """
        Salva figura em arquivo.

        Args:
            fig: Figura Plotly ou Matplotlib
            filename: Nome do arquivo (com extensão)
            dpi: DPI para figuras Matplotlib (padrão: 300)
            width: Largura em pixels (Plotly) ou polegadas (Matplotlib)
            height: Altura em pixels (Plotly) ou polegadas (Matplotlib)
        """
        if self.interactive:
            # Plotly: salvar como HTML ou PNG
            if filename.endswith('.html'):
                fig.write_html(filename)
            elif filename.endswith('.png'):
                fig.write_image(filename, width=width, height=height)
            else:
                # Default: HTML
                fig.write_html(filename + '.html')
        else:
            # Matplotlib: salvar como PNG/PDF/SVG
            if width and height:
                fig.set_size_inches(width, height)

            fig.savefig(filename, dpi=dpi, bbox_inches='tight')
            plt.close(fig)

    def _get_color_palette(self, n_colors: int = 8) -> list:
        """
        Retorna paleta de cores UFOP.

        Args:
            n_colors: Número de cores desejadas

        Returns:
            Lista de cores hex
        """
        if n_colors <= len(UFOP_CATEGORICAL):
            return UFOP_CATEGORICAL[:n_colors]
        else:
            # Repetir paleta se necessário
            repeats = (n_colors // len(UFOP_CATEGORICAL)) + 1
            return (UFOP_CATEGORICAL * repeats)[:n_colors]


# ============================================================================
# FUNÇÕES AUXILIARES PARA CRIAÇÃO DE FIGURAS
# ============================================================================

def create_plotly_figure(
    title: str = '',
    xaxis_title: str = '',
    yaxis_title: str = '',
    **kwargs
) -> go.Figure:
    """
    Cria figura Plotly com estilo UFOP padrão.

    Args:
        title: Título do gráfico
        xaxis_title: Título do eixo X
        yaxis_title: Título do eixo Y
        **kwargs: Argumentos adicionais para layout

    Returns:
        Figura Plotly configurada
    """
    fig = go.Figure()

    # Layout padrão
    layout = {
        'template': PLOT_STYLE_INTERACTIVE['template'],
        'title': {
            'text': title,
            'font': {
                'size': PLOT_STYLE_INTERACTIVE['title_font_size'],
                'family': PLOT_STYLE_INTERACTIVE['font_family'],
            }
        },
        'xaxis': {
            'title': xaxis_title,
            'showgrid': True,
            'gridcolor': 'rgba(0,0,0,0.1)',
        },
        'yaxis': {
            'title': yaxis_title,
            'showgrid': True,
            'gridcolor': 'rgba(0,0,0,0.1)',
        },
        'hovermode': PLOT_STYLE_INTERACTIVE['hover_mode'],
        'dragmode': PLOT_STYLE_INTERACTIVE['dragmode'],
        'margin': PLOT_STYLE_INTERACTIVE['margin'],
        'font': {
            'family': PLOT_STYLE_INTERACTIVE['font_family'],
            'size': PLOT_STYLE_INTERACTIVE['font_size'],
        },
    }

    # Merge com kwargs
    layout.update(kwargs)

    fig.update_layout(**layout)

    return fig


def create_matplotlib_figure(
    figsize: tuple = (8, 6),
    **kwargs
) -> tuple:
    """
    Cria figura Matplotlib com estilo UFOP padrão.

    Args:
        figsize: Tamanho da figura (largura, altura) em polegadas
        **kwargs: Argumentos adicionais para plt.subplots

    Returns:
        Tupla (fig, ax) com figura e eixos
    """
    fig, ax = plt.subplots(figsize=figsize, **kwargs)

    return fig, ax


def format_tooltip(template_name: str, data: Dict[str, Any]) -> str:
    """
    Formata tooltip usando template.

    Args:
        template_name: Nome do template ('athlete', 'community', 'rivalry')
        data: Dicionário com dados para preencher template

    Returns:
        String HTML formatada para tooltip
    """
    from core.config.styles import TOOLTIP_TEMPLATES

    template = TOOLTIP_TEMPLATES.get(template_name, '')

    try:
        return template.format(**data)
    except KeyError as e:
        print(f"Warning: Missing key in tooltip data: {e}")
        return template
