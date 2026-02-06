#!/usr/bin/env python3
"""
Normaliza PageRank usando percentis intra-rede para permitir comparações cross-network válidas.

Este script corrige o viés de tamanho de rede, convertendo valores brutos de PageRank
em percentis relativos à posição do atleta dentro de sua própria rede.
"""

import pandas as pd
import numpy as np
from pathlib import Path

class PageRankNormalizer:
    """Normaliza PageRank para comparações cross-network."""

    def __init__(self, data_dir: str, output_dir: str):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self):
        """Carrega dados de PageRank."""
        print("Carregando dados de PageRank...")
        self.df = pd.read_csv(self.data_dir / 'pagerank.csv')
        print(f"  ✓ {len(self.df)} atletas carregados")
        print(f"  ✓ {self.df['network_id'].nunique()} redes únicas")

    def calculate_percentiles(self):
        """Calcula percentis intra-rede."""
        print("\nCalculando percentis intra-rede...")

        # Para cada rede separadamente, calcular percentil
        # Percentil 100 = melhor atleta, Percentil 0 = pior
        self.df['pagerank_percentile'] = self.df.groupby('network_id')['pagerank'].rank(pct=True) * 100

        # Também calcular z-score normalizado
        self.df['pagerank_zscore'] = self.df.groupby('network_id')['pagerank'].transform(
            lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
        )

        print(f"  ✓ Percentis calculados (0-100)")
        print(f"  ✓ Z-scores calculados")

    def calculate_network_stats(self):
        """Calcula estatísticas por rede para contexto."""
        print("\nCalculando estatísticas por rede...")

        network_stats = self.df.groupby('network_id').agg({
            'athlete_name': 'count',
            'pagerank': ['min', 'max', 'mean', 'std']
        }).reset_index()

        network_stats.columns = ['network_id', 'n_athletes', 'pr_min', 'pr_max', 'pr_mean', 'pr_std']

        # Adicionar info de esporte/gênero
        network_info = self.df.groupby('network_id')[['network_name', 'sport', 'gender']].first().reset_index()
        network_stats = network_stats.merge(network_info, on='network_id')

        self.network_stats = network_stats
        print(f"  ✓ Estatísticas calculadas para {len(network_stats)} redes")

    def generate_top20_normalized(self):
        """Gera Top 20 baseado em percentis."""
        print("\nGerando Top 20 por percentil...")

        # Top 20 por percentil (posição relativa)
        top20_percentile = self.df.nlargest(20, 'pagerank_percentile')

        # Salvar CSV
        csv_path = self.output_dir / 'top20_global_normalized.csv'
        top20_percentile.to_csv(csv_path, index=False)
        print(f"  ✓ Salvo: {csv_path}")

        # Análise descritiva
        print(f"\n  Distribuição por gênero (percentil):")
        print(f"    Masculino: {(top20_percentile['gender'] == 'M').sum()}")
        print(f"    Feminino: {(top20_percentile['gender'] == 'F').sum()}")

        print(f"\n  Distribuição por esporte (percentil):")
        sport_counts = top20_percentile['sport'].value_counts()
        for sport, count in sport_counts.items():
            print(f"    {sport.capitalize()}: {count}")

        return top20_percentile

    def generate_top20_original(self):
        """Gera Top 20 baseado em valores brutos (para comparação)."""
        print("\nGerando Top 20 por valores brutos (original)...")

        top20_raw = self.df.nlargest(20, 'pagerank')

        # Salvar CSV
        csv_path = self.output_dir / 'top20_global_raw.csv'
        top20_raw.to_csv(csv_path, index=False)

        print(f"\n  Distribuição por gênero (valores brutos):")
        print(f"    Masculino: {(top20_raw['gender'] == 'M').sum()}")
        print(f"    Feminino: {(top20_raw['gender'] == 'F').sum()}")

        print(f"\n  Distribuição por esporte (valores brutos):")
        sport_counts = top20_raw['sport'].value_counts()
        for sport, count in sport_counts.items():
            print(f"    {sport.capitalize()}: {count}")

        return top20_raw

    def compare_rankings(self, top20_percentile, top20_raw):
        """Compara rankings normalizados vs brutos."""
        print("\n" + "="*80)
        print("COMPARAÇÃO: Percentil vs Valores Brutos")
        print("="*80)

        print("\n🔹 Top 5 por PERCENTIL (posição relativa):")
        for i, row in top20_percentile.head(5).iterrows():
            net_size = self.network_stats[self.network_stats['network_id'] == row['network_id']]['n_athletes'].values[0]
            print(f"  {row['athlete_name']:40s} | {row['sport']:10s} {row['gender']} | "
                  f"Percentil: {row['pagerank_percentile']:6.2f} | "
                  f"PR bruto: {row['pagerank']:.4f} | "
                  f"Rede: {net_size:4d} atletas")

        print("\n🔹 Top 5 por VALORES BRUTOS (original - ENVIESADO):")
        for i, row in top20_raw.head(5).iterrows():
            net_size = self.network_stats[self.network_stats['network_id'] == row['network_id']]['n_athletes'].values[0]
            print(f"  {row['athlete_name']:40s} | {row['sport']:10s} {row['gender']} | "
                  f"PR bruto: {row['pagerank']:.4f} | "
                  f"Percentil: {row.get('pagerank_percentile', 0):6.2f} | "
                  f"Rede: {net_size:4d} atletas")

    def save_all_data(self):
        """Salva dados completos com normalização."""
        print("\nSalvando dados completos...")

        # CSV completo com percentis
        output_path = self.data_dir / 'pagerank_normalized.csv'
        self.df.to_csv(output_path, index=False)
        print(f"  ✓ Salvo: {output_path}")

        # Estatísticas de rede
        stats_path = self.output_dir / 'network_size_stats.csv'
        self.network_stats.to_csv(stats_path, index=False)
        print(f"  ✓ Salvo: {stats_path}")

    def run(self):
        """Executa pipeline completo."""
        print("\n" + "="*80)
        print("NORMALIZAÇÃO DE PAGERANK POR PERCENTIS INTRA-REDE")
        print("="*80)

        self.load_data()
        self.calculate_percentiles()
        self.calculate_network_stats()

        top20_percentile = self.generate_top20_normalized()
        top20_raw = self.generate_top20_original()

        self.compare_rankings(top20_percentile, top20_raw)

        self.save_all_data()

        print("\n" + "="*80)
        print("✅ NORMALIZAÇÃO CONCLUÍDA")
        print("="*80)
        print("\nArquivos gerados:")
        print(f"  • {self.data_dir / 'pagerank_normalized.csv'}")
        print(f"  • {self.output_dir / 'top20_global_normalized.csv'}")
        print(f"  • {self.output_dir / 'top20_global_raw.csv'}")
        print(f"  • {self.output_dir / 'network_size_stats.csv'}")
        print("\nPróximo passo: Regenerar Figura 02 com dados normalizados")


if __name__ == "__main__":
    normalizer = PageRankNormalizer(
        data_dir='../../results_complete_mining/data',
        output_dir='../../results_complete_mining/tables'
    )

    normalizer.run()
