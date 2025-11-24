"""
Caminhos de arquivos centralizados.

FONTE ÚNICA DE VERDADE para todos os caminhos do projeto.
"""

from pathlib import Path

# Diretório base do projeto
# __file__ = main/src/core/config/paths.py
CONFIG_DIR = Path(__file__).parent           # main/src/core/config/
CORE_DIR = CONFIG_DIR.parent                 # main/src/core/
SRC_DIR = CORE_DIR.parent                    # main/src/
MAIN_ROOT = SRC_DIR.parent                   # main/
PROJECT_ROOT = SRC_DIR                       # main/src/ (para compatibilidade)

# ============================================================================
# DADOS DE ENTRADA
# ============================================================================

PATHS = {
    # Resultados da mineração (input principal)
    'results_dir': MAIN_ROOT / 'results' / 'networks',
    'consolidated_athletes': MAIN_ROOT / 'results' / 'networks' / 'consolidated_athletes.csv',
    'consolidated_edges': MAIN_ROOT / 'results' / 'networks' / 'consolidated_edges.csv',
    'network_summaries': MAIN_ROOT / 'results' / 'networks' / 'summaries.json',
    'all_summaries': MAIN_ROOT / 'results' / 'all_network_summaries.json',

    # Análises adicionais
    'additional_analyses_dir': MAIN_ROOT / 'results' / 'additional_analyses',
    'medal_profile': MAIN_ROOT / 'results' / 'additional_analyses' / 'medal_profile_by_community.csv',
    'inter_connectivity': MAIN_ROOT / 'results' / 'additional_analyses' / 'inter_community_connectivity.csv',
    'community_hierarchy': MAIN_ROOT / 'results' / 'additional_analyses' / 'community_hierarchy.csv',
    'top_rivalries': MAIN_ROOT / 'results' / 'additional_analyses' / 'top_rivalry_pairs.csv',
    'community_profiles': MAIN_ROOT / 'results' / 'community_profiles_enriched.csv',

    # Dados base
    'athlete_events': MAIN_ROOT / 'data' / 'athlete_events.csv',

    # ========================================================================
    # SAÍDAS - MONOGRAFIA
    # ========================================================================

    # Figuras para LaTeX
    'monografia_figuras': MAIN_ROOT / 'docs' / 'monografia' / 'figuras',

    # Tabelas para LaTeX
    'monografia_tabelas': MAIN_ROOT / 'docs' / 'monografia' / 'tabelas',

    # ========================================================================
    # SAÍDAS - DASHBOARD
    # ========================================================================

    # Cache do dashboard (se implementarmos)
    'dashboard_cache': PROJECT_ROOT / '.cache',

    # ========================================================================
    # LOGS E TEMPORÁRIOS
    # ========================================================================

    'logs_dir': PROJECT_ROOT / 'logs',
    'temp_dir': PROJECT_ROOT / 'temp',
}

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def ensure_directories():
    """Cria diretórios que não existem."""
    for key, path in PATHS.items():
        if 'dir' in key or key in ['monografia_figuras', 'monografia_tabelas']:
            path.mkdir(parents=True, exist_ok=True)

def get_path(key: str) -> Path:
    """Retorna Path object para chave."""
    if key not in PATHS:
        raise KeyError(f"Path '{key}' não encontrado em PATHS")
    return PATHS[key]

def get_sport_dir(sport: str, sex: str) -> Path:
    """Retorna diretório de resultados para esporte específico."""
    sport_lower = sport.lower()
    return PATHS['results_dir'] / sport_lower
