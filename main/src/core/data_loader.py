"""
Data Loader: carregamento e validação de dados.

Centraliza todo o acesso a dados, garantindo consistência.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import PATHS, SPORTS_LIST


class DataLoader:
    """
    Carregador centralizado de dados.

    Carrega todos os CSVs/JSONs de resultados e valida integridade.
    """

    def __init__(self, results_dir: Optional[Path] = None):
        """
        Inicializa o data loader.

        Args:
            results_dir: Diretório de resultados (padrão: PATHS['results_dir'])
        """
        self.results_dir = results_dir or PATHS['results_dir']
        self._cached_data = {}

    def load_consolidated_athletes(self) -> pd.DataFrame:
        """
        Carrega dados consolidados de atletas com todas as métricas.

        Returns:
            DataFrame com colunas:
            - athlete_id, sport, sex, name, noc, ...
            - original_pagerank, original_betweenness_centrality, ...
            - original_community, ...
        """
        cache_key = 'consolidated_athletes'

        if cache_key in self._cached_data:
            return self._cached_data[cache_key]

        path = PATHS['consolidated_athletes']

        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        print(f"Carregando atletas consolidados de: {path}")
        df = pd.read_csv(path)

        print(f"  [OK] {len(df)} atletas carregados")
        print(f"  [OK] Esportes: {df['sport'].unique()}")
        print(f"  [OK] Sexos: {df['sex'].unique()}")

        self._cached_data[cache_key] = df
        return df

    def load_medal_profile(self) -> pd.DataFrame:
        """
        Carrega perfil de medalhas por comunidade.

        Returns:
            DataFrame com colunas:
            - sport, sex, community_id
            - size, gold_pct, silver_pct, bronze_pct
            - dominance_index, competitive_profile
        """
        cache_key = 'medal_profile'

        if cache_key in self._cached_data:
            return self._cached_data[cache_key]

        path = PATHS['medal_profile']

        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        print(f"Carregando perfil de medalhas de: {path}")
        df = pd.read_csv(path)

        print(f"  [OK] {len(df)} comunidades carregadas")

        self._cached_data[cache_key] = df
        return df

    def load_community_hierarchy(self) -> pd.DataFrame:
        """
        Carrega hierarquia de comunidades.

        Returns:
            DataFrame com colunas:
            - sport, sex, community_id
            - size, pagerank_mean, pagerank_percentile
            - hierarchy_level, hierarchy_score
            - dominant_country
        """
        cache_key = 'community_hierarchy'

        if cache_key in self._cached_data:
            return self._cached_data[cache_key]

        path = PATHS['community_hierarchy']

        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        print(f"Carregando hierarquia de comunidades de: {path}")
        df = pd.read_csv(path)

        print(f"  [OK] {len(df)} comunidades carregadas")

        self._cached_data[cache_key] = df
        return df

    def load_inter_connectivity(self) -> pd.DataFrame:
        """
        Carrega conectividade inter-comunidade.

        Returns:
            DataFrame com colunas:
            - sport, sex
            - intra_edges, inter_edges
            - intra_ratio, inter_ratio, segregation_score
        """
        cache_key = 'inter_connectivity'

        if cache_key in self._cached_data:
            return self._cached_data[cache_key]

        path = PATHS['inter_connectivity']

        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        print(f"Carregando conectividade inter-comunidade de: {path}")
        df = pd.read_csv(path)

        print(f"  [OK] {len(df)} registros carregados")

        self._cached_data[cache_key] = df
        return df

    def load_top_rivalries(self) -> pd.DataFrame:
        """
        Carrega top rivalidades estruturais.

        Returns:
            DataFrame com colunas:
            - sport, sex
            - comm1, comm2, edge_count, total_weight
            - dominant_country1, dominant_country2
        """
        cache_key = 'top_rivalries'

        if cache_key in self._cached_data:
            return self._cached_data[cache_key]

        path = PATHS['top_rivalries']

        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        print(f"Carregando rivalidades de: {path}")
        df = pd.read_csv(path)

        print(f"  [OK] {len(df)} rivalidades carregadas")

        self._cached_data[cache_key] = df
        return df

    def load_community_profiles(self) -> pd.DataFrame:
        """
        Carrega perfis completos de comunidades com métricas de entropia.

        Returns:
            DataFrame com colunas:
            - sport, sex, community_id, size
            - temporal_entropy, geographic_entropy
            - year_start, year_end, span_years
            - dominant_era, dominant_country
            - medal counts, pagerank stats, etc.
        """
        cache_key = 'community_profiles'

        if cache_key in self._cached_data:
            return self._cached_data[cache_key]

        path = PATHS['community_profiles']

        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        print(f"Carregando perfis de comunidades de: {path}")
        df = pd.read_csv(path)

        print(f"  [OK] {len(df)} comunidades carregadas com entropia temporal/geográfica")

        self._cached_data[cache_key] = df
        return df

    def load_all(self) -> Dict[str, pd.DataFrame]:
        """
        Carrega TODOS os datasets de uma vez.

        Returns:
            Dicionário com chaves:
            - 'athletes': DataFrame consolidado de atletas
            - 'medal_profile': Perfil de medalhas
            - 'hierarchy': Hierarquia de comunidades
            - 'connectivity': Conectividade inter-comunidade
            - 'rivalries': Rivalidades estruturais
        """
        print("=" * 80)
        print("CARREGANDO TODOS OS DADOS")
        print("=" * 80)

        data = {
            'athletes': self.load_consolidated_athletes(),
            'medal_profile': self.load_medal_profile(),
            'hierarchy': self.load_community_hierarchy(),
            'connectivity': self.load_inter_connectivity(),
            'rivalries': self.load_top_rivalries(),
            'community_profiles': self.load_community_profiles(),
        }

        print("\n" + "=" * 80)
        print("DADOS CARREGADOS COM SUCESSO")
        print("=" * 80)

        return data

    def clear_cache(self):
        """Limpa cache de dados."""
        self._cached_data = {}
        print("Cache limpo.")


# ============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# ============================================================================

def load_all_data() -> Dict[str, pd.DataFrame]:
    """
    Função de conveniência para carregar todos os dados.

    Returns:
        Dicionário com todos os DataFrames
    """
    loader = DataLoader()
    return loader.load_all()


# ============================================================================
# VALIDAÇÃO DE DADOS
# ============================================================================

def validate_data(data: Dict[str, pd.DataFrame]) -> bool:
    """
    Valida integridade dos dados carregados.

    Args:
        data: Dicionário retornado por load_all_data()

    Returns:
        True se válido, False caso contrário
    """
    required_keys = ['athletes', 'medal_profile', 'hierarchy', 'connectivity', 'rivalries']

    for key in required_keys:
        if key not in data:
            print(f"ERRO: Dataset '{key}' não encontrado")
            return False

        if data[key].empty:
            print(f"ERRO: Dataset '{key}' está vazio")
            return False

    print("[OK] Dados validados com sucesso")
    return True
