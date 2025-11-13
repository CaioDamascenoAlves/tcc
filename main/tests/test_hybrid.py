from mineracao import SportsNetworkAnalyzer

# Criar analyzer
analyzer = SportsNetworkAnalyzer(
    data_path='athlete_events.csv',
    selected_sports=['Swimming'],
    base_dir='resultados_teste'
)

# Carregar dados
analyzer.load_and_filter_data()

# Executar apenas a função híbrida
analyzer._create_hybrid_swimming_network()

print("Arquivo híbrido recriado!")