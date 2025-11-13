from mineracao import SportsNetworkAnalyzer

def test_simple_classification():
    """Testa a classificação simples dos esportes."""
    print("Testando classificação simples...")

    analyzer = SportsNetworkAnalyzer(
        data_path='athlete_events.csv',
        selected_sports=['Swimming', 'Basketball', 'Football'],
        base_dir='resultados_teste'
    )

    # Carregar dados e aplicar classificação
    analyzer.load_and_filter_data()

    print("\nClassificação final:")
    for sport, info in analyzer.sport_types.items():
        print(f"\n{sport}:")
        print(f"  Tipo: {info['type']}")
        print(f"  Eventos individuais: {len(info['individual_events'])}")
        print(f"  Eventos coletivos: {len(info['team_events'])}")

    print("\nTeste concluído!")

if __name__ == "__main__":
    test_simple_classification()