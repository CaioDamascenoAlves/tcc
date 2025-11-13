"""
Paleta de cores UFOP (Universidade Federal de Ouro Preto).

Cores institucionais: Vinho (Bordeaux) e Cinza
Tema: Light (fundo claro)
"""

# ============================================================================
# CORES PRINCIPAIS UFOP
# ============================================================================

# Cores institucionais primárias
UFOP_WINE = '#8B2635'      # Vinho/Bordeaux principal (vermelho amarronzado)
UFOP_WINE_DARK = '#6B1F2A'  # Vinho escuro
UFOP_WINE_LIGHT = '#A53C4C' # Vinho claro

UFOP_GRAY = '#5A5A5A'      # Cinza médio
UFOP_GRAY_DARK = '#3A3A3A' # Cinza escuro
UFOP_GRAY_LIGHT = '#8A8A8A' # Cinza claro

# Cores neutras para complemento
UFOP_WHITE = '#FFFFFF'
UFOP_OFF_WHITE = '#F5F5F5'
UFOP_BLACK = '#2A2A2A'

# ============================================================================
# PALETA EXPANDIDA PARA VISUALIZAÇÕES
# ============================================================================

# Gradiente de Vinho (para gráficos)
WINE_GRADIENT = [
    '#F4E4E6',  # Vinho muito claro
    '#D4A8B0',  # Vinho claro
    '#B46C7A',  # Vinho médio-claro
    '#943044',  # Vinho médio
    '#8B2635',  # Vinho principal
    '#6B1F2A',  # Vinho escuro
    '#4B151D',  # Vinho muito escuro
]

# Gradiente de Cinza (para gráficos)
GRAY_GRADIENT = [
    '#F0F0F0',  # Cinza muito claro
    '#D0D0D0',  # Cinza claro
    '#AAAAAA',  # Cinza médio-claro
    '#8A8A8A',  # Cinza médio
    '#5A5A5A',  # Cinza principal
    '#3A3A3A',  # Cinza escuro
    '#2A2A2A',  # Cinza muito escuro
]

# Paleta combinada (Vinho + Cinza) para múltiplas categorias
UFOP_CATEGORICAL = [
    UFOP_WINE,       # 1. Vinho
    UFOP_GRAY,       # 2. Cinza
    '#A53C4C',       # 3. Vinho claro
    '#8A8A8A',       # 4. Cinza claro
    '#6B1F2A',       # 5. Vinho escuro
    '#3A3A3A',       # 6. Cinza escuro
    '#C97883',       # 7. Vinho mais claro
    '#B0B0B0',       # 8. Cinza mais claro
]

# ============================================================================
# MAPEAMENTO PARA ESPORTES (mantendo identidade UFOP)
# ============================================================================

COLORS_SPORTS = {
    'Swimming': UFOP_WINE,      # Vinho para natação
    'Basketball': UFOP_GRAY,    # Cinza para basquete
    'Football': UFOP_WINE_DARK, # Vinho escuro para futebol
}

# ============================================================================
# MAPEAMENTO PARA SEXO
# ============================================================================

COLORS_SEX = {
    'M': UFOP_GRAY_DARK,  # Cinza escuro para masculino
    'F': UFOP_WINE,       # Vinho para feminino
}

# ============================================================================
# MAPEAMENTO PARA HIERARQUIA
# ============================================================================

COLORS_HIERARCHY = {
    'Nucleo': UFOP_WINE,           # Vinho (destaque)
    'Intermediaria': UFOP_GRAY,    # Cinza
    'Periferica': UFOP_GRAY_LIGHT, # Cinza claro
}

# ============================================================================
# MAPEAMENTO PARA PERFIL COMPETITIVO
# ============================================================================

COLORS_PROFILE = {
    'Elite': UFOP_WINE_DARK,      # Vinho escuro (elite)
    'Competitiva': UFOP_GRAY,     # Cinza (maioria)
    'Participante': UFOP_GRAY_LIGHT, # Cinza claro
}

# ============================================================================
# CORES PARA ELEMENTOS DE UI (Dashboard)
# ============================================================================

UI_COLORS = {
    # Fundo
    'background': UFOP_WHITE,
    'background_secondary': UFOP_OFF_WHITE,

    # Texto
    'text_primary': UFOP_BLACK,
    'text_secondary': UFOP_GRAY,

    # Acentos
    'accent_primary': UFOP_WINE,
    'accent_secondary': UFOP_GRAY,

    # Estados
    'success': '#28A745',  # Verde (mantido para clareza)
    'warning': '#FFC107',  # Amarelo (mantido para clareza)
    'error': UFOP_WINE_DARK,  # Vinho escuro como erro
    'info': UFOP_GRAY,

    # Bordas e divisores
    'border': UFOP_GRAY_LIGHT,
    'divider': '#E0E0E0',
}

# ============================================================================
# CONFIGURAÇÃO STREAMLIT (Temas Light e Dark)
# ============================================================================

# Cores para tema Dark
UFOP_DARK_BG = '#1E1E1E'        # Fundo escuro principal
UFOP_DARK_BG_SECONDARY = '#2A2A2A'  # Fundo escuro secundário
UFOP_DARK_TEXT = '#E0E0E0'      # Texto claro
UFOP_WINE_BRIGHT = '#C97883'    # Vinho mais claro para contraste em fundo escuro

# Tema Light (padrão)
STREAMLIT_THEME_LIGHT = {
    'primaryColor': UFOP_WINE,        # Cor principal (botões, links)
    'backgroundColor': UFOP_WHITE,    # Fundo principal
    'secondaryBackgroundColor': UFOP_OFF_WHITE,  # Fundo secundário (sidebar)
    'textColor': UFOP_BLACK,          # Cor do texto
    'font': 'sans-serif',             # Fonte padrão
}

# Tema Dark
STREAMLIT_THEME_DARK = {
    'primaryColor': UFOP_WINE_BRIGHT,     # Vinho mais claro para contraste
    'backgroundColor': UFOP_DARK_BG,      # Fundo escuro
    'secondaryBackgroundColor': UFOP_DARK_BG_SECONDARY,  # Sidebar escuro
    'textColor': UFOP_DARK_TEXT,          # Texto claro
    'font': 'sans-serif',                 # Fonte padrão
}

# Alias para compatibilidade (default: light)
STREAMLIT_THEME = STREAMLIT_THEME_LIGHT

# Gerar arquivo .streamlit/config.toml (Light)
STREAMLIT_CONFIG_TOML_LIGHT = f"""
[theme]
base = "light"
primaryColor = "{UFOP_WINE}"
backgroundColor = "{UFOP_WHITE}"
secondaryBackgroundColor = "{UFOP_OFF_WHITE}"
textColor = "{UFOP_BLACK}"
font = "sans-serif"

[server]
headless = true
port = 8501

[client]
showErrorDetails = true
"""

# Gerar arquivo .streamlit/config.toml (Dark)
STREAMLIT_CONFIG_TOML_DARK = f"""
[theme]
base = "dark"
primaryColor = "{UFOP_WINE_BRIGHT}"
backgroundColor = "{UFOP_DARK_BG}"
secondaryBackgroundColor = "{UFOP_DARK_BG_SECONDARY}"
textColor = "{UFOP_DARK_TEXT}"
font = "sans-serif"

[server]
headless = true
port = 8501

[client]
showErrorDetails = true
"""

# Alias para compatibilidade (default: light)
STREAMLIT_CONFIG_TOML = STREAMLIT_CONFIG_TOML_LIGHT

# ============================================================================
# CONFIGURAÇÕES MATPLOTLIB (Estático para LaTeX)
# ============================================================================

MATPLOTLIB_STYLE = {
    'figure.facecolor': UFOP_WHITE,
    'axes.facecolor': UFOP_WHITE,
    'axes.edgecolor': UFOP_GRAY,
    'axes.labelcolor': UFOP_BLACK,
    'text.color': UFOP_BLACK,
    'xtick.color': UFOP_GRAY,
    'ytick.color': UFOP_GRAY,
    'grid.color': UFOP_GRAY_LIGHT,
    'grid.alpha': 0.3,

    # Ciclo de cores padrão (usar paleta UFOP)
    'axes.prop_cycle': f"cycler('color', {UFOP_CATEGORICAL})",
}

# ============================================================================
# CONFIGURAÇÕES PLOTLY (Interativo para Dashboard)
# ============================================================================

PLOTLY_TEMPLATE = {
    'layout': {
        'colorway': UFOP_CATEGORICAL,  # Paleta de cores padrão
        'font': {'family': 'Arial, sans-serif', 'color': UFOP_BLACK},
        'title': {'font': {'size': 18, 'color': UFOP_WINE}},
        'paper_bgcolor': UFOP_WHITE,
        'plot_bgcolor': UFOP_OFF_WHITE,
        'xaxis': {
            'gridcolor': UFOP_GRAY_LIGHT,
            'linecolor': UFOP_GRAY,
            'tickcolor': UFOP_GRAY,
        },
        'yaxis': {
            'gridcolor': UFOP_GRAY_LIGHT,
            'linecolor': UFOP_GRAY,
            'tickcolor': UFOP_GRAY,
        },
    }
}

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_color_by_sport(sport: str) -> str:
    """Retorna cor UFOP para esporte."""
    return COLORS_SPORTS.get(sport, UFOP_GRAY)

def get_color_by_sex(sex: str) -> str:
    """Retorna cor UFOP para sexo."""
    return COLORS_SEX.get(sex, UFOP_GRAY)

def get_color_by_hierarchy(level: str) -> str:
    """Retorna cor UFOP para hierarquia."""
    level = level.replace('Núcleo', 'Nucleo')
    level = level.replace('Intermediária', 'Intermediaria')
    level = level.replace('Periférica', 'Periferica')
    return COLORS_HIERARCHY.get(level, UFOP_GRAY)

def get_color_by_profile(profile: str) -> str:
    """Retorna cor UFOP para perfil."""
    return COLORS_PROFILE.get(profile, UFOP_GRAY)

def get_wine_gradient(n_colors: int = 5) -> list:
    """
    Retorna gradiente de vinho com N cores.

    Args:
        n_colors: Número de cores desejadas

    Returns:
        Lista de códigos hex
    """
    if n_colors <= len(WINE_GRADIENT):
        # Retornar subset igualmente espaçado
        indices = [int(i * (len(WINE_GRADIENT) - 1) / (n_colors - 1)) for i in range(n_colors)]
        return [WINE_GRADIENT[i] for i in indices]
    else:
        return WINE_GRADIENT

def get_gray_gradient(n_colors: int = 5) -> list:
    """
    Retorna gradiente de cinza com N cores.

    Args:
        n_colors: Número de cores desejadas

    Returns:
        Lista de códigos hex
    """
    if n_colors <= len(GRAY_GRADIENT):
        indices = [int(i * (len(GRAY_GRADIENT) - 1) / (n_colors - 1)) for i in range(n_colors)]
        return [GRAY_GRADIENT[i] for i in indices]
    else:
        return GRAY_GRADIENT

def create_streamlit_config_file(output_dir: str = '.', theme: str = 'light'):
    """
    Cria arquivo .streamlit/config.toml com tema UFOP.

    Args:
        output_dir: Diretório onde criar a pasta .streamlit
        theme: Tema a usar ('light' ou 'dark'). Padrão: 'light'
    """
    import os
    from pathlib import Path

    streamlit_dir = Path(output_dir) / '.streamlit'
    streamlit_dir.mkdir(exist_ok=True)

    config_path = streamlit_dir / 'config.toml'

    # Selecionar conteúdo baseado no tema
    if theme.lower() == 'dark':
        config_content = STREAMLIT_CONFIG_TOML_DARK
        print(f"Criando configuração com tema DARK (UFOP)")
    else:
        config_content = STREAMLIT_CONFIG_TOML_LIGHT
        print(f"Criando configuração com tema LIGHT (UFOP)")

    with open(config_path, 'w') as f:
        f.write(config_content)

    print(f"Arquivo de configuração criado: {config_path}")
