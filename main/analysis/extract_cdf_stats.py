"""
Script para extrair estatísticas REAIS das CDFs para apresentação
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Caminho
EDGES_FILE = Path(__file__).parent.parent / 'results' / 'networks' / 'consolidated_edges.csv'

def calculate_cdf_stats(sport, sex):
    """Calcula estatísticas reais da CDF para um esporte/sexo"""
    df = pd.read_csv(EDGES_FILE)

    # Filtra por esporte e sexo
    mask = (df['sport'] == sport) & (df['sex'] == sex)
    weights = df[mask]['weight'].values

    if len(weights) == 0:
        return None

    # Calcula percentuais para valores específicos
    stats = {
        'total_edges': len(weights),
        'min': weights.min(),
        'max': weights.max(),
        'mean': weights.mean(),
        'median': np.median(weights),
    }

    # Percentual de arestas até cada threshold
    for threshold in [2, 3, 5, 8, 10, 15, 20, 25, 30, 40, 50]:
        pct = (weights <= threshold).sum() / len(weights) * 100
        stats[f'le_{threshold}'] = pct

    return stats

def main():
    """Extrai estatísticas reais para cada esporte/sexo"""

    sports_config = {
        'Football': [('Football', 'M'), ('Football', 'F')],
        'Basketball': [('Basketball', 'M'), ('Basketball', 'F')],
        'Swimming': [('Swimming', 'M'), ('Swimming', 'F')],
    }

    print("=" * 80)
    print("ESTATÍSTICAS REAIS DAS CDFs - DADOS VALIDADOS")
    print("=" * 80)

    for sport_name, configs in sports_config.items():
        print(f"\n{'=' * 80}")
        print(f"{sport_name.upper()}")
        print("=" * 80)

        for sport, sex in configs:
            stats = calculate_cdf_stats(sport, sex)

            if stats is None:
                print(f"\n  {sport} {sex}: SEM DADOS")
                continue

            print(f"\n  {sport} {sex}:")
            print(f"    Total de arestas: {stats['total_edges']:,}")
            print(f"    Min: {stats['min']:.1f}, Max: {stats['max']:.1f}")
            print(f"    Média: {stats['mean']:.2f}, Mediana: {stats['median']:.1f}")
            print(f"\n    Percentual acumulado (para slides):")

            # Mostra os percentuais principais
            for threshold in [2, 5, 10, 15, 20, 30]:
                key = f'le_{threshold}'
                if key in stats:
                    pct = stats[key]
                    if 20 <= pct <= 95:  # Mostra apenas valores relevantes
                        print(f"      {pct:5.1f}% dos pesos <= {threshold}")

if __name__ == '__main__':
    main()
