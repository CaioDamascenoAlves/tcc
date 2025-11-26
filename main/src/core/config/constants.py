"""
Constantes do projeto.
"""

# ============================================================================
# CONSTANTES DO DOMÍNIO
# ============================================================================

SPORTS_LIST = ['Swimming', 'Basketball', 'Football']
SEX_LIST = ['M', 'F']
MEDAL_TYPES = ['Gold', 'Silver', 'Bronze']

# Sistema de ponderação de medalhas (Fibonacci 3-2-1)
MEDAL_WEIGHTS = {
    'Gold': 3,
    'Silver': 2,
    'Bronze': 1,
}

# Sistema de ponderação de arestas (distância competitiva)
EDGE_WEIGHTS = {
    ('Gold', 'Silver'): 3,
    ('Gold', 'Bronze'): 5,
    ('Silver', 'Bronze'): 2,
}

# ============================================================================
# THRESHOLDS E CLASSIFICAÇÕES
# ============================================================================

# Perfil de Dominância
DOMINANCE_THRESHOLDS = {
    'Elite': 2.2,           # D >= 2.2
    'Competitiva_min': 1.8, # 1.8 <= D < 2.2
    'Participante': 1.8,    # D < 1.8
}

# Hierarquia de Comunidades (percentis)
HIERARCHY_THRESHOLDS = {
    'Nucleo': 80,           # >= 80th percentile
    'Intermediaria': 40,    # 40-80th percentile
    'Periferica': 40,       # < 40th percentile
}

# Filtros de visualização
DISPLAY_LIMITS = {
    'top_n_default': 10,
    'top_n_max': 50,
    'network_nodes_threshold': 100,  # Filtrar redes grandes
    'min_betweenness_bridge': 0.01,  # Threshold para atletas-ponte
}

# ============================================================================
# FORMATOS DE EXPORT
# ============================================================================

FIGURE_FORMATS = {
    'latex': {
        'format': 'png',
        'dpi': 300,
        'bbox_inches': 'tight',
    },
    'presentation': {
        'format': 'svg',
        'dpi': 150,
        'bbox_inches': 'tight',
    },
}

TABLE_FORMATS = {
    'latex': {
        'float_format': '%.4f',
        'index': False,
        'escape': True,
    },
}

# ============================================================================
# CONFIGURAÇÕES DO DASHBOARD
# ============================================================================

DASHBOARD_CONFIG = {
    'page_title': 'Análise de Redes Olímpicas',
    'page_icon': '',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
}

# Tabs do dashboard
DASHBOARD_TABS = [
    'Visão Geral',
    'Comunidades',
    'Atletas-Ponte',
    'Rivalidades',
    'Hierarquia',
    'Redes',
]

# ============================================================================
# METADADOS
# ============================================================================

PROJECT_METADATA = {
    'name': 'Olympic Networks Analysis',
    'version': '2.0.0',
    'author': 'TCC Project',
    'description': 'Análise de redes complexas aplicada a competições olímpicas',
    'data_period': '1896-2016',
    'sports_analyzed': ['Swimming', 'Basketball', 'Football'],
}
