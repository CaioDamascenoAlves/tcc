"""
Analysis: Análises comparativas e tabelas resumidas.
"""

from .comparative_table import (
    generate_comparative_metrics,
    render_comparative_table,
    export_comparative_table_latex
)

__all__ = [
    'generate_comparative_metrics',
    'render_comparative_table',
    'export_comparative_table_latex'
]
