"""
Módulo de configuração centralizada.

Importa todas as configurações para acesso fácil:
    from config import COLORS, PATHS, SPORTS_LIST
"""

from .styles import *
from .paths import PATHS
from .constants import *

__all__ = [
    # styles.py
    'COLORS',
    'PLOT_STYLE_INTERACTIVE',
    'PLOT_STYLE_STATIC',
    'UFOP_CATEGORICAL',
    'WINE_GRADIENT',
    'GRAY_GRADIENT',
    'UFOP_WINE',
    'UFOP_GRAY',

    # paths.py
    'PATHS',

    # constants.py
    'SPORTS_LIST',
    'SEX_LIST',
    'MEDAL_TYPES',
    'MEDAL_WEIGHTS',
    'EDGE_WEIGHTS',
    'DOMINANCE_THRESHOLDS',
    'HIERARCHY_THRESHOLDS',
    'DISPLAY_LIMITS',
    'FIGURE_FORMATS',
    'TABLE_FORMATS',
    'DASHBOARD_CONFIG',
    'DASHBOARD_TABS',
    'PROJECT_METADATA',
]
