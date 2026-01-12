"""
Wrapper para compatibilidade: usa data_loader_auto mas mantém interface do DataLoader.

Permite que o código existente funcione sem modificações, mas com suporte ao Google Drive.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import PATHS, SPORTS_LIST
from core.data_loader_auto import get_data_loader


class DataLoader:
    """
    Carregador centralizado de dados com suporte automático ao Google Drive.

    Mantém a mesma interface do DataLoader original, mas usa data_loader_auto
    internamente para detectar se deve usar arquivos locais ou Google Drive.
    """

    def __init__(self, results_dir: Optional[Path] = None):
        """
        Inicializa o data loader.

        Args:
            results_dir: Diretório de resultados (ignorado se usar Drive)
        """
        self.results_dir = results_dir or PATHS.get('results_dir')
        self._cached_data = {}
        
        # Inicializa loader automático
        project_root = Path(__file__).parent.parent.parent  # main/
        self.auto_loader = get_data_loader(project_root)
        
        print(f"Data Loader inicializado em modo: {'Google Drive' if self.auto_loader.use_drive else 'Local'}")

    def _load_csv(self, relative_path: str, cache_key: str) -> pd.DataFrame:
        """Método auxiliar para carregar CSVs com cache."""
        if cache_key in self._cached_data:
            return self._cached_data[cache_key]
        
        # Normaliza caminho: remove prefixos desnecessários
        path = relative_path.replace('\\', '/')
        
        # Remove prefixos comuns se presentes
        for prefix in ['main/results/', 'results/', 'main/']:
            if path.startswith(prefix):
                path = path[len(prefix):]
                break
        
        df = self.auto_loader.load_csv(path)
        self._cached_data[cache_key] = df
        
        print(f"  OK {cache_key}: {len(df)} registros carregados")
        return df

    def load_consolidated_athletes(self) -> pd.DataFrame:
        """
        Carrega dados consolidados de atletas com todas as métricas.

        Returns:
            DataFrame com todas as colunas de métricas de rede
        """
        return self._load_csv('consolidated_sports_network_analysis.csv', 'consolidated_athletes')

    def load_consolidated_edges(self) -> pd.DataFrame:
        """Carrega arestas consolidadas de todos os esportes."""
        return self._load_csv('consolidated_edges_data.csv', 'consolidated_edges')

    def load_swimming_hybrid(self) -> pd.DataFrame:
        """Carrega dados do grafo híbrido de natação."""
        return self._load_csv('swimming_hybrid_network.csv', 'swimming_hybrid')

    def load_community_profiles(self) -> pd.DataFrame:
        """Carrega perfis enriquecidos de comunidades."""
        return self._load_csv('community_profiles_enriched.csv', 'community_profiles')

    def load_community_members(self) -> pd.DataFrame:
        """Carrega membros detalhados de comunidades."""
        return self._load_csv('community_members_detailed.csv', 'community_members')

    def load_community_typology(self) -> pd.DataFrame:
        """Carrega classificação tipológica de comunidades."""
        return self._load_csv('community_typology_classification.csv', 'community_typology')

    def load_medal_profile(self) -> pd.DataFrame:
        """Carrega perfil de medalhas por comunidade."""
        return self._load_csv('additional_analyses/medal_profile_by_community.csv', 'medal_profile')

    def load_rivalry_pairs(self) -> pd.DataFrame:
        """Carrega pares de rivalidade top."""
        return self._load_csv('additional_analyses/top_rivalry_pairs.csv', 'rivalry_pairs')
    
    def load_top_rivalries(self) -> pd.DataFrame:
        """Alias para load_rivalry_pairs (compatibilidade)."""
        return self.load_rivalry_pairs()

    def load_community_hierarchy(self) -> pd.DataFrame:
        """Carrega dados de hierarquia entre comunidades."""
        return self._load_csv('additional_analyses/community_hierarchy.csv', 'community_hierarchy')

    def load_inter_community_connectivity(self) -> pd.DataFrame:
        """Carrega conectividade entre comunidades."""
        return self._load_csv('additional_analyses/inter_community_connectivity.csv', 'inter_community')
    
    def load_inter_connectivity(self) -> pd.DataFrame:
        """Alias para load_inter_community_connectivity (compatibilidade)."""
        return self.load_inter_community_connectivity()

    def load_community_profiles(self) -> pd.DataFrame:
        """Carrega perfis completos de comunidades com métricas de entropia."""
        return self._load_csv('community_profiles_enriched.csv', 'community_profiles')

    def load_consolidated_analysis(self) -> pd.DataFrame:
        """Carrega análise consolidada de redes esportivas."""
        return self._load_csv('consolidated_sports_network_analysis.csv', 'consolidated_analysis')

    def load_sport_network(self, sport: str, sex: str, event_type: str = 'individual') -> Dict:
        """
        Carrega dados de rede específicos de um esporte.

        Args:
            sport: 'swimming', 'basketball', ou 'football'
            sex: 'M' ou 'F'
            event_type: 'individual' ou 'team'

        Returns:
            Dict com 'metrics' e 'edges'
        """
        base_path = f"{sport}/{sport}_{sex}_{event_type}"
        
        return {
            'metrics': self._load_csv(f"{base_path}_detailed_metrics.csv", f"{sport}_{sex}_{event_type}_metrics"),
            'edges': self._load_csv(f"{base_path}_original_edges.csv", f"{sport}_{sex}_{event_type}_edges")
        }

    def load_all(self) -> Dict:
        """
        Carrega todos os dados principais.

        Returns:
            Dict com todos os DataFrames principais
        """
        print("\nCarregando dados...")
        
        data = {
            'athletes': self.load_consolidated_athletes(),
            'edges': self.load_consolidated_edges(),
            'communities': self.load_community_profiles(),
            'community_members': self.load_community_members(),
            'typology': self.load_community_typology(),
            'medal_profile': self.load_medal_profile(),
            'rivalries': self.load_rivalry_pairs(),
            'hierarchy': self.load_community_hierarchy(),
            'connectivity': self.load_inter_community_connectivity(),
            'analysis': self.load_consolidated_analysis(),
        }
        
        print(f"Dados carregados com sucesso!\n")
        return data
