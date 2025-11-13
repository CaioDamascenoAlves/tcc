"""
Metrics Calculator: funções reutilizáveis para cálculo de métricas.

Centraliza toda lógica de cálculo, evitando duplicação.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import sys
from pathlib import Path

# Adicionar config ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import (
    DOMINANCE_THRESHOLDS,
    HIERARCHY_THRESHOLDS,
    MEDAL_WEIGHTS,
    DISPLAY_LIMITS
)


class MetricsCalculator:
    """
    Calculadora de métricas reutilizáveis.

    Todas as funções são estáticas para facilitar uso sem instanciação.
    """

    # ========================================================================
    # PERFIL DE MEDALHAS E DOMINÂNCIA
    # ========================================================================

    @staticmethod
    def calculate_dominance_index(gold_pct: float, silver_pct: float, bronze_pct: float) -> float:
        """
        Calcula índice de dominância baseado em distribuição de medalhas.

        Fórmula: D = 3*gold% + 2*silver% + 1*bronze%

        Args:
            gold_pct: Percentual de medalhas de ouro (0-100)
            silver_pct: Percentual de medalhas de prata (0-100)
            bronze_pct: Percentual de medalhas de bronze (0-100)

        Returns:
            Índice de dominância (1.0 a 3.0)
        """
        # Converter percentuais para proporções
        gold_prop = gold_pct / 100.0
        silver_prop = silver_pct / 100.0
        bronze_prop = bronze_pct / 100.0

        dominance = (
            MEDAL_WEIGHTS['Gold'] * gold_prop +
            MEDAL_WEIGHTS['Silver'] * silver_prop +
            MEDAL_WEIGHTS['Bronze'] * bronze_prop
        )

        return dominance

    @staticmethod
    def classify_competitive_profile(dominance: float) -> str:
        """
        Classifica perfil competitivo baseado em índice de dominância.

        Args:
            dominance: Índice de dominância (1.0 a 3.0)

        Returns:
            Perfil: 'Elite', 'Competitiva', ou 'Participante'
        """
        if dominance >= DOMINANCE_THRESHOLDS['Elite']:
            return 'Elite'
        elif dominance >= DOMINANCE_THRESHOLDS['Competitiva_min']:
            return 'Competitiva'
        else:
            return 'Participante'

    # ========================================================================
    # HIERARQUIA DE COMUNIDADES
    # ========================================================================

    @staticmethod
    def calculate_percentile_rank(values: pd.Series) -> pd.Series:
        """
        Calcula percentil de cada valor na série.

        Args:
            values: Série de valores numéricos

        Returns:
            Série com percentis (0-100)
        """
        return values.rank(pct=True) * 100

    @staticmethod
    def classify_hierarchy_level(percentile: float) -> str:
        """
        Classifica nível hierárquico baseado em percentil.

        Args:
            percentile: Percentil do PageRank (0-100)

        Returns:
            Nível: 'Nucleo', 'Intermediaria', ou 'Periferica'
        """
        if percentile >= HIERARCHY_THRESHOLDS['Nucleo']:
            return 'Nucleo'
        elif percentile >= HIERARCHY_THRESHOLDS['Intermediaria']:
            return 'Intermediaria'
        else:
            return 'Periferica'

    @staticmethod
    def calculate_hierarchy_score(pagerank_mean: float, pagerank_percentile: float) -> float:
        """
        Calcula score composto de hierarquia.

        Combina PageRank absoluto com posição relativa (percentil).

        Args:
            pagerank_mean: PageRank médio da comunidade
            pagerank_percentile: Percentil do PageRank

        Returns:
            Score de hierarquia (ponderado)
        """
        # Ponderação: 60% percentil (posição relativa) + 40% valor absoluto
        normalized_pr = pagerank_mean / 0.01  # Normalizar (assumindo max ~0.01)
        score = 0.6 * pagerank_percentile + 0.4 * normalized_pr * 100
        return min(score, 100.0)  # Cap em 100

    # ========================================================================
    # SEGREGAÇÃO E CONECTIVIDADE
    # ========================================================================

    @staticmethod
    def calculate_segregation_score(intra_edges: int, inter_edges: int) -> float:
        """
        Calcula score de segregação estrutural.

        Args:
            intra_edges: Número de arestas intra-comunidade
            inter_edges: Número de arestas inter-comunidade

        Returns:
            Score de segregação (razão intra/inter)
        """
        epsilon = 1e-6
        segregation = intra_edges / (inter_edges + epsilon)
        return segregation

    @staticmethod
    def calculate_connectivity_ratio(intra_edges: int, inter_edges: int) -> Tuple[float, float]:
        """
        Calcula razões de conectividade intra e inter-comunidade.

        Args:
            intra_edges: Número de arestas intra-comunidade
            inter_edges: Número de arestas inter-comunidade

        Returns:
            Tupla (intra_ratio, inter_ratio) em percentuais
        """
        total = intra_edges + inter_edges

        if total == 0:
            return 0.0, 0.0

        intra_ratio = (intra_edges / total) * 100
        inter_ratio = (inter_edges / total) * 100

        return intra_ratio, inter_ratio

    # ========================================================================
    # ATLETAS-PONTE (BETWEENNESS)
    # ========================================================================

    @staticmethod
    def identify_bridge_athletes(
        df: pd.DataFrame,
        threshold_percentile: float = 90.0
    ) -> pd.DataFrame:
        """
        Identifica atletas-ponte baseado em betweenness centrality.

        Args:
            df: DataFrame com coluna 'original_betweenness_centrality'
            threshold_percentile: Percentil mínimo para ser considerado ponte

        Returns:
            DataFrame filtrado com apenas atletas-ponte
        """
        threshold = df['original_betweenness_centrality'].quantile(threshold_percentile / 100.0)
        bridges = df[df['original_betweenness_centrality'] >= threshold].copy()

        return bridges

    @staticmethod
    def calculate_bridge_proportion(df: pd.DataFrame, sport: str) -> float:
        """
        Calcula proporção de atletas-ponte em um esporte.

        Args:
            df: DataFrame consolidado de atletas
            sport: Nome do esporte

        Returns:
            Proporção de atletas-ponte (0-100%)
        """
        sport_df = df[df['sport'] == sport]
        bridges = MetricsCalculator.identify_bridge_athletes(sport_df)

        proportion = (len(bridges) / len(sport_df)) * 100
        return proportion

    # ========================================================================
    # AGREGAÇÕES E ESTATÍSTICAS
    # ========================================================================

    @staticmethod
    def aggregate_by_community(
        df: pd.DataFrame,
        metric_column: str,
        agg_funcs: List[str] = ['mean', 'median', 'std']
    ) -> pd.DataFrame:
        """
        Agrega métricas por comunidade.

        Args:
            df: DataFrame de atletas
            metric_column: Nome da coluna a agregar
            agg_funcs: Funções de agregação

        Returns:
            DataFrame agregado por (sport, sex, community_id)
        """
        grouped = df.groupby(['sport', 'sex', 'original_community'])[metric_column].agg(agg_funcs)
        grouped.columns = [f'{metric_column}_{func}' for func in agg_funcs]

        return grouped.reset_index()

    @staticmethod
    def calculate_summary_stats(series: pd.Series) -> Dict[str, float]:
        """
        Calcula estatísticas resumidas de uma série.

        Args:
            series: Série de valores numéricos

        Returns:
            Dicionário com estatísticas
        """
        return {
            'count': len(series),
            'mean': series.mean(),
            'median': series.median(),
            'std': series.std(),
            'min': series.min(),
            'max': series.max(),
            'q25': series.quantile(0.25),
            'q75': series.quantile(0.75),
        }

    # ========================================================================
    # RANKINGS E TOP-N
    # ========================================================================

    @staticmethod
    def get_top_n(
        df: pd.DataFrame,
        metric_column: str,
        n: int = 10,
        ascending: bool = False
    ) -> pd.DataFrame:
        """
        Retorna top N registros por métrica.

        Args:
            df: DataFrame
            metric_column: Coluna para ordenar
            n: Número de registros
            ascending: Ordem (False = maiores primeiro)

        Returns:
            DataFrame com top N
        """
        n = min(n, DISPLAY_LIMITS['top_n_max'])  # Cap no máximo configurado

        return df.nlargest(n, metric_column) if not ascending else df.nsmallest(n, metric_column)

    @staticmethod
    def add_rank_column(
        df: pd.DataFrame,
        metric_column: str,
        rank_column_name: str = 'rank',
        ascending: bool = False
    ) -> pd.DataFrame:
        """
        Adiciona coluna de ranking ao DataFrame.

        Args:
            df: DataFrame
            metric_column: Coluna para ranquear
            rank_column_name: Nome da nova coluna
            ascending: Ordem

        Returns:
            DataFrame com coluna de rank adicionada
        """
        df = df.copy()
        df[rank_column_name] = df[metric_column].rank(ascending=ascending, method='min').astype(int)

        return df

    # ========================================================================
    # NORMALIZAÇÃO E TRANSFORMAÇÕES
    # ========================================================================

    @staticmethod
    def normalize_to_range(
        series: pd.Series,
        new_min: float = 0.0,
        new_max: float = 1.0
    ) -> pd.Series:
        """
        Normaliza série para range específico (min-max scaling).

        Args:
            series: Série de valores
            new_min: Novo mínimo
            new_max: Novo máximo

        Returns:
            Série normalizada
        """
        old_min = series.min()
        old_max = series.max()

        if old_max == old_min:
            return pd.Series([new_min] * len(series), index=series.index)

        normalized = (series - old_min) / (old_max - old_min)
        scaled = normalized * (new_max - new_min) + new_min

        return scaled

    @staticmethod
    def z_score_normalize(series: pd.Series) -> pd.Series:
        """
        Normalização Z-score (média 0, desvio padrão 1).

        Args:
            series: Série de valores

        Returns:
            Série normalizada
        """
        return (series - series.mean()) / series.std()

    # ========================================================================
    # VALIDAÇÕES
    # ========================================================================

    @staticmethod
    def validate_percentages(gold_pct: float, silver_pct: float, bronze_pct: float) -> bool:
        """
        Valida se percentuais de medalhas somam aproximadamente 100%.

        Args:
            gold_pct, silver_pct, bronze_pct: Percentuais

        Returns:
            True se válido (soma ~100), False caso contrário
        """
        total = gold_pct + silver_pct + bronze_pct
        return 99.0 <= total <= 101.0  # Tolerância para erros de arredondamento

    @staticmethod
    def validate_metric_range(
        value: float,
        min_value: float,
        max_value: float,
        metric_name: str = 'metric'
    ) -> bool:
        """
        Valida se valor está dentro do range esperado.

        Args:
            value: Valor a validar
            min_value: Mínimo esperado
            max_value: Máximo esperado
            metric_name: Nome da métrica (para mensagem de erro)

        Returns:
            True se válido, False caso contrário
        """
        if not (min_value <= value <= max_value):
            print(f"WARNING: {metric_name} = {value} fora do range [{min_value}, {max_value}]")
            return False
        return True


# ============================================================================
# FUNÇÕES DE CONVENIÊNCIA (WRAPPERS)
# ============================================================================

def calc_dominance(gold_pct: float, silver_pct: float, bronze_pct: float) -> float:
    """Wrapper para cálculo de dominância."""
    return MetricsCalculator.calculate_dominance_index(gold_pct, silver_pct, bronze_pct)

def classify_profile(dominance: float) -> str:
    """Wrapper para classificação de perfil."""
    return MetricsCalculator.classify_competitive_profile(dominance)

def classify_hierarchy(percentile: float) -> str:
    """Wrapper para classificação de hierarquia."""
    return MetricsCalculator.classify_hierarchy_level(percentile)

def get_top_athletes(df: pd.DataFrame, metric: str = 'original_pagerank', n: int = 10) -> pd.DataFrame:
    """Wrapper para top N atletas."""
    return MetricsCalculator.get_top_n(df, metric, n)

def get_bridge_athletes(df: pd.DataFrame) -> pd.DataFrame:
    """Wrapper para identificar atletas-ponte."""
    return MetricsCalculator.identify_bridge_athletes(df)
