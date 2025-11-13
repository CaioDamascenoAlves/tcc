"""
Script para testar se o dashboard carrega os dados corretamente
"""
import pandas as pd
import os

def test_dashboard_data():
    """Testa se os dados estão prontos para o dashboard."""

    print("Testando dados para o dashboard...")

    base_dir = 'resultados_teste'

    # 1. Verificar CSV consolidado
    csv_path = os.path.join(base_dir, 'consolidated_sports_network_analysis.csv')

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"CSV consolidado encontrado: {len(df)} atletas")
        print(f"  Colunas: {len(df.columns)}")
        print(f"  Esportes: {df['sport'].unique()}")
        print(f"  Sexos: {df['sex'].unique()}")

        # Verificar se tem as colunas esperadas
        required_cols = ['original_pagerank', 'original_betweenness_centrality', 'backbone_pagerank']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            print(f"Colunas faltando: {missing_cols}")
        else:
            print("Todas as colunas principais presentes")

        # Top 5 atletas por PageRank
        top_pagerank = df.nlargest(5, 'original_pagerank')[['name', 'sport', 'sex', 'original_pagerank']]
        print(f"\nTop 5 atletas por PageRank:")
        for idx, row in top_pagerank.iterrows():
            print(f"  {row['name']} ({row['sport']} {row['sex']}) - {row['original_pagerank']:.4f}")

    else:
        print(f"CSV consolidado nao encontrado: {csv_path}")
        return False

    # 2. Verificar CSV de arestas
    edges_path = os.path.join(base_dir, 'consolidated_edges_data.csv')

    if os.path.exists(edges_path):
        edges_df = pd.read_csv(edges_path)
        print(f"\nCSV de arestas encontrado: {len(edges_df)} arestas")
        print(f"  Pesos unicos: {edges_df['weight'].nunique()}")
    else:
        print(f"\nCSV de arestas nao encontrado: {edges_path}")

    # 3. Verificar JSON de resumos
    json_path = os.path.join(base_dir, 'all_network_summaries.json')

    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            summaries = pd.json_normalize(pd.read_json(json_path))
        print(f"\nJSON de resumos encontrado: {len(summaries)} redes")
    else:
        print(f"\nJSON de resumos nao encontrado: {json_path}")

    print(f"\nDashboard pode ser testado com:")
    print(f"cd main && streamlit run dashboard.py")

    return True

if __name__ == "__main__":
    test_dashboard_data()