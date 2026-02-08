"""
Módulo de Visualização: gráficos interativos e estáticos.

Fonte única de verdade para todas as visualizações.
Suporta tanto dashboard (Plotly interativo) quanto exportação LaTeX (Matplotlib estático).
"""

from .plots import (
    scatter_size_vs_pagerank,
    histogram_dominance,
    heatmap_segregation,
    barplot_top_rivalries,
    cdf_pagerank,
    cdf_pagerank_by_sport,
    boxplot_metric_by_category,
)

from .plots_extended import (
    stacked_bar_profile_distribution,
    violin_betweenness_by_sport,
    violin_betweenness_by_event,
    line_pagerank_evolution,
    table_top_athletes,
    create_all_plots,
)

__all__ = [
    # Plots principais
    'scatter_size_vs_pagerank',
    'histogram_dominance',
    'heatmap_segregation',
    'barplot_top_rivalries',
    'cdf_pagerank',
    'cdf_pagerank_by_sport',
    'boxplot_metric_by_category',

    # Plots estendidos
    'stacked_bar_profile_distribution',
    'violin_betweenness_by_sport',
    'violin_betweenness_by_event',
    'line_pagerank_evolution',
    'table_top_athletes',

    # Utilitários
    'create_all_plots',
]
