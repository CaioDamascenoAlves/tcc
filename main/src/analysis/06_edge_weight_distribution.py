#!/usr/bin/env python3
"""
Análise de Distribuição de Pesos de Arestas

Calcula:
1. Distribuição de pesos por evento (frequência de cada peso: 2, 3, 5)
2. CDF (Cumulative Distribution Function) de pesos
3. Validação da modelagem (se os pesos seguem a hierarquia esperada)
4. Análise comparativa entre esportes

Pesos esperados:
- Gold → Bronze: 5
- Gold → Silver: 3
- Silver → Bronze: 2
"""

import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path
from collections import Counter

class EdgeWeightAnalyzer:
    """Análise de distribuição de pesos das arestas."""

    def __init__(self, networks_dir: str, output_dir: str):
        self.networks_dir = Path(networks_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 12 casos de estudo
        self.case_studies = self._define_cases()

    def _define_cases(self):
        """Define casos de estudo."""
        return [
            {'id': 1, 'sport': 'football', 'file': 'football_M_Football_Mens_Football.gexf'},
            {'id': 2, 'sport': 'football', 'file': 'football_F_Football_Womens_Football.gexf'},
            {'id': 3, 'sport': 'basketball', 'file': 'basketball_M_Basketball_Mens_Basketball.gexf'},
            {'id': 4, 'sport': 'basketball', 'file': 'basketball_F_Basketball_Womens_Basketball.gexf'},
            {'id': 5, 'sport': 'athletics', 'file': 'athletics_M_100m.gexf'},
            {'id': 6, 'sport': 'athletics', 'file': 'athletics_F_100m.gexf'},
            {'id': 7, 'sport': 'swimming', 'file': 'swimming_M_100m_Freestyle.gexf'},
            {'id': 8, 'sport': 'swimming', 'file': 'swimming_F_100m_Freestyle.gexf'},
            {'id': 9, 'sport': 'judo', 'file': 'judo_M_-90kg.gexf'},
            {'id': 10, 'sport': 'judo', 'file': 'judo_F_-70kg.gexf'},
            {'id': 11, 'sport': 'boxing', 'file': 'boxing_M_Welter_63-69kg.gexf'},
            {'id': 12, 'sport': 'boxing', 'file': 'boxing_F_Middle_69-75kg.gexf'}
        ]

    def analyze_edge_weights(self):
        """Analisa distribuição de pesos por evento."""
        print("\nAnalisando distribuição de pesos das arestas...")

        results = []
        all_weights = []

        for case in self.case_studies:
            file_path = self.networks_dir / case['sport'] / case['file']

            if not file_path.exists():
                print(f"  ⚠️  Arquivo não encontrado: {file_path}")
                continue

            G = nx.read_gexf(file_path)

            # Coletar todos os pesos
            weights = []
            for u, v, data in G.edges(data=True):
                weight = data.get('weight', 1.0)
                if isinstance(weight, str):
                    weight = float(weight)
                weights.append(weight)
                all_weights.append({'network_id': case['id'], 'weight': weight})

            if len(weights) == 0:
                print(f"  ⚠️  Sem arestas: {case['file']}")
                continue

            # Contar frequências
            weight_counts = Counter(weights)
            total_edges = len(weights)

            # Calcular percentuais
            pct_weight_2 = (weight_counts.get(2.0, 0) / total_edges * 100) if total_edges > 0 else 0
            pct_weight_3 = (weight_counts.get(3.0, 0) / total_edges * 100) if total_edges > 0 else 0
            pct_weight_5 = (weight_counts.get(5.0, 0) / total_edges * 100) if total_edges > 0 else 0

            # Verificar se existem pesos inesperados
            expected_weights = {2.0, 3.0, 5.0}
            unexpected = set(weight_counts.keys()) - expected_weights

            results.append({
                'network_id': case['id'],
                'sport': case['sport'],
                'total_edges': total_edges,
                'weight_2_count': weight_counts.get(2.0, 0),
                'weight_3_count': weight_counts.get(3.0, 0),
                'weight_5_count': weight_counts.get(5.0, 0),
                'weight_2_pct': pct_weight_2,
                'weight_3_pct': pct_weight_3,
                'weight_5_pct': pct_weight_5,
                'mean_weight': np.mean(weights),
                'median_weight': np.median(weights),
                'std_weight': np.std(weights),
                'unexpected_weights': len(unexpected) > 0,
                'unexpected_values': str(unexpected) if unexpected else 'None'
            })

            print(f"  ✓ {case['sport']}: {total_edges} arestas (W2: {pct_weight_2:.1f}%, W3: {pct_weight_3:.1f}%, W5: {pct_weight_5:.1f}%)")

        self.weight_distribution = pd.DataFrame(results)
        self.all_weights_df = pd.DataFrame(all_weights)

        # Estatísticas globais
        print("\n  Estatísticas globais:")
        print(f"    Total de arestas analisadas: {len(all_weights):,}")
        global_counts = Counter([w['weight'] for w in all_weights])
        total_global = len(all_weights)
        print(f"    Peso 2: {global_counts.get(2.0, 0):,} ({global_counts.get(2.0, 0)/total_global*100:.1f}%)")
        print(f"    Peso 3: {global_counts.get(3.0, 0):,} ({global_counts.get(3.0, 0)/total_global*100:.1f}%)")
        print(f"    Peso 5: {global_counts.get(5.0, 0):,} ({global_counts.get(5.0, 0)/total_global*100:.1f}%)")

    def calculate_cdf_data(self):
        """Calcula dados para CDF por evento."""
        print("\nCalculando dados CDF...")

        cdf_results = []

        for network_id in self.all_weights_df['network_id'].unique():
            weights = self.all_weights_df[self.all_weights_df['network_id'] == network_id]['weight'].values

            # Ordenar pesos
            sorted_weights = np.sort(weights)

            # Calcular CDF
            cdf = np.arange(1, len(sorted_weights) + 1) / len(sorted_weights)

            # Guardar pontos da CDF
            for w, c in zip(sorted_weights, cdf):
                cdf_results.append({
                    'network_id': network_id,
                    'weight': w,
                    'cdf': c
                })

        self.cdf_data = pd.DataFrame(cdf_results)
        print(f"  ✓ CDF calculada para {len(self.all_weights_df['network_id'].unique())} eventos")

    def validate_modeling(self):
        """Valida se os pesos seguem a hierarquia esperada."""
        print("\nValidando modelagem...")

        validation_results = []

        for case in self.case_studies:
            file_path = self.networks_dir / case['sport'] / case['file']

            if not file_path.exists():
                continue

            G = nx.read_gexf(file_path)

            # Verificar se todos os pesos estão no conjunto esperado
            expected = {2.0, 3.0, 5.0}
            actual_weights = set()

            for u, v, data in G.edges(data=True):
                weight = float(data.get('weight', 1.0))
                actual_weights.add(weight)

            is_valid = actual_weights.issubset(expected)
            unexpected = actual_weights - expected

            validation_results.append({
                'network_id': case['id'],
                'sport': case['sport'],
                'is_valid': is_valid,
                'has_all_weights': expected.issubset(actual_weights),
                'unexpected_weights': str(unexpected) if unexpected else 'None'
            })

            status = "✓" if is_valid else "✗"
            print(f"  {status} Rede {case['id']}: {'Válida' if is_valid else f'Inválida - pesos inesperados: {unexpected}'}")

        self.validation = pd.DataFrame(validation_results)

    def calculate_weight_ratios(self):
        """Calcula razões entre diferentes pesos."""
        print("\nCalculando razões de pesos...")

        ratios = []

        for _, row in self.weight_distribution.iterrows():
            w2 = row['weight_2_count']
            w3 = row['weight_3_count']
            w5 = row['weight_5_count']

            # Razões
            ratio_5_2 = w5 / w2 if w2 > 0 else float('inf')
            ratio_5_3 = w5 / w3 if w3 > 0 else float('inf')
            ratio_3_2 = w3 / w2 if w2 > 0 else float('inf')

            ratios.append({
                'network_id': row['network_id'],
                'sport': row['sport'],
                'ratio_5_2': ratio_5_2 if ratio_5_2 != float('inf') else None,
                'ratio_5_3': ratio_5_3 if ratio_5_3 != float('inf') else None,
                'ratio_3_2': ratio_3_2 if ratio_3_2 != float('inf') else None
            })

        self.weight_ratios = pd.DataFrame(ratios)

        # Mostrar médias
        print("\n  Razões médias (cross-esporte):")
        print(f"    W5/W2: {self.weight_ratios['ratio_5_2'].mean():.2f}")
        print(f"    W5/W3: {self.weight_ratios['ratio_5_3'].mean():.2f}")
        print(f"    W3/W2: {self.weight_ratios['ratio_3_2'].mean():.2f}")

    def export_results(self):
        """Exporta resultados."""
        print("\nExportando resultados...")

        # Distribuição de pesos
        dist_path = self.output_dir / 'edge_weight_distribution.csv'
        self.weight_distribution.to_csv(dist_path, index=False)
        print(f"  ✓ {dist_path.name}")

        # Dados CDF
        cdf_path = self.output_dir / 'edge_weight_cdf.csv'
        self.cdf_data.to_csv(cdf_path, index=False)
        print(f"  ✓ {cdf_path.name}")

        # Validação
        val_path = self.output_dir / 'edge_weight_validation.csv'
        self.validation.to_csv(val_path, index=False)
        print(f"  ✓ {val_path.name}")

        # Razões
        ratio_path = self.output_dir / 'edge_weight_ratios.csv'
        self.weight_ratios.to_csv(ratio_path, index=False)
        print(f"  ✓ {ratio_path.name}")

        # Todos os pesos (para plotting)
        all_path = self.output_dir / 'all_edge_weights.csv'
        self.all_weights_df.to_csv(all_path, index=False)
        print(f"  ✓ {all_path.name}")

    def run(self):
        """Executa análise completa."""
        print("\n" + "="*100)
        print("ANÁLISE DE DISTRIBUIÇÃO DE PESOS DAS ARESTAS")
        print("="*100)

        self.analyze_edge_weights()
        self.calculate_cdf_data()
        self.validate_modeling()
        self.calculate_weight_ratios()
        self.export_results()

        print("\n" + "="*100)
        print("ANÁLISE DE PESOS CONCLUÍDA!")
        print("="*100)


if __name__ == "__main__":
    analyzer = EdgeWeightAnalyzer(
        networks_dir='../../results_per_event_cleaned',
        output_dir='../../results_complete_mining/data'
    )

    analyzer.run()
