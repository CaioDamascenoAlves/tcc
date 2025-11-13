"""
Estilos visuais centralizados: cores, paletas, fontes.

FONTE ÚNICA DE VERDADE para todos os aspectos visuais.
Cores baseadas na identidade visual da UFOP (Vinho e Cinza).
"""

from .ufop_colors import (
    UFOP_WINE, UFOP_WINE_DARK, UFOP_WINE_LIGHT,
    UFOP_GRAY, UFOP_GRAY_DARK, UFOP_GRAY_LIGHT,
    COLORS_SPORTS, COLORS_SEX, COLORS_HIERARCHY, COLORS_PROFILE,
    UFOP_CATEGORICAL, WINE_GRADIENT, GRAY_GRADIENT
)

# ============================================================================
# CORES POR CATEGORIA (UFOP)
# ============================================================================

COLORS = {
    # Esportes (Vinho e Cinza)
    'Swimming': COLORS_SPORTS['Swimming'],
    'Basketball': COLORS_SPORTS['Basketball'],
    'Football': COLORS_SPORTS['Football'],

    # Sexo
    'M': COLORS_SEX['M'],
    'F': COLORS_SEX['F'],

    # Hierarquia de Comunidades
    'Nucleo': COLORS_HIERARCHY['Nucleo'],
    'Intermediaria': COLORS_HIERARCHY['Intermediaria'],
    'Periferica': COLORS_HIERARCHY['Periferica'],

    # Perfil Competitivo
    'Elite': COLORS_PROFILE['Elite'],
    'Competitiva': COLORS_PROFILE['Competitiva'],
    'Participante': COLORS_PROFILE['Participante'],
}

# Paletas alternativas para gradientes
PALETTES = {
    'swimming': ['#cfe2f3', '#6fa8dc', '#3d85c6', '#0b5394'],
    'basketball': ['#fce5cd', '#f9cb9c', '#f6b26b', '#e69138'],
    'football': ['#d9ead3', '#b6d7a8', '#93c47d', '#6aa84f'],
    'hierarchy': ['#3498db', '#f39c12', '#e74c3c'],  # Periférica → Núcleo
    'dominance': ['#ecf0f1', '#95a5a6', '#7f8c8d', '#34495e'],  # Claro → Escuro
}

# ============================================================================
# CONFIGURAÇÕES DE PLOTLY (INTERATIVO)
# ============================================================================

PLOT_STYLE_INTERACTIVE = {
    'template': 'plotly_white',
    'font_family': 'Arial',
    'font_size': 12,
    'title_font_size': 16,
    'hover_mode': 'closest',
    'dragmode': 'zoom',
    'margin': dict(l=60, r=40, t=80, b=60),
}

# ============================================================================
# CONFIGURAÇÕES DE MATPLOTLIB (ESTÁTICO PARA LATEX)
# ============================================================================

PLOT_STYLE_STATIC = {
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'font.size': 10,
    'font.family': 'serif',
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 13,
    'lines.linewidth': 1.5,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
}

# ============================================================================
# TOOLTIPS ENRIQUECIDOS
# ============================================================================

TOOLTIP_TEMPLATES = {
    'athlete': """
<b>{name}</b><br>
País: {noc}<br>
Medalhas: {gold}🥇 {silver}🥈 {bronze}🥉<br>
PageRank: {pagerank:.4f} (Top {percentile:.1f}%)<br>
Comunidade: C{community_id} - {dominant_country}<br>
Era: {min_year}-{max_year}
""",

    'community': """
<b>{sport} {sex} - C{community_id}</b><br>
País Dominante: {dominant_country}<br>
Tamanho: {size} atletas<br>
Dominância: {dominance:.2f} ({profile})<br>
PageRank Médio: {pagerank_mean:.4f}<br>
Hierarquia: {hierarchy_level}
""",

    'rivalry': """
<b>Rivalidade Estrutural</b><br>
{sport} {sex}<br>
Comunidade A: C{comm1} - {country1}<br>
Comunidade B: C{comm2} - {country2}<br>
Confrontos: {edge_count}<br>
Peso Total: {total_weight}
""",
}

# ============================================================================
# CONFIGURAÇÕES DE REDE (NETWORK PLOTS)
# ============================================================================

NETWORK_STYLE = {
    'node_size_range': (50, 500),
    'edge_width_range': (0.5, 3.0),
    'node_opacity': 0.7,
    'edge_opacity': 0.3,
    'layout_algorithm': 'force_directed',  # ou 'kamada_kawai'
    'k_repulsion': 0.1,  # Força de repulsão entre nós
}

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_color_by_sport(sport: str) -> str:
    """Retorna cor para esporte."""
    return COLORS.get(sport, '#95a5a6')

def get_color_by_profile(profile: str) -> str:
    """Retorna cor para perfil competitivo."""
    return COLORS.get(profile, '#95a5a6')

def get_color_by_hierarchy(level: str) -> str:
    """Retorna cor para nível hierárquico."""
    # Normalizar acentos
    level = level.replace('Núcleo', 'Nucleo')
    level = level.replace('Intermediária', 'Intermediaria')
    level = level.replace('Periférica', 'Periferica')
    return COLORS.get(level, '#95a5a6')
