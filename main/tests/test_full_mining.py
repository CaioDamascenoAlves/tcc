from mineracao import SportsNetworkAnalyzer
import os

def test_full_mining():
    """Testa a mineração completa para gerar as 16 redes."""
    print("Iniciando teste de mineração completa...")

    analyzer = SportsNetworkAnalyzer(
        data_path='athlete_events.csv',
        selected_sports=['Swimming', 'Basketball', 'Football'],
        base_dir='resultados_teste'
    )

    # Executar análise completa
    results_df, summaries = analyzer.run_complete_analysis()

    print("\n" + "="*50)
    print("VERIFICANDO ARQUIVOS GERADOS")
    print("="*50)

    # Listar arquivos GEXF gerados
    base_dir = 'resultados_teste'
    gexf_files = []

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.gexf'):
                gexf_files.append(os.path.join(root, file))

    print(f"\nArquivos GEXF encontrados: {len(gexf_files)}")
    for file in sorted(gexf_files):
        print(f"  - {file}")

    # Verificar se temos as 16 redes esperadas
    expected_files = [
        # Swimming - 8 arquivos (M/F x individual/team x original/backbone)
        'swimming/swimming_original_M_individual.gexf',
        'swimming/swimming_backbone_M_individual.gexf',
        'swimming/swimming_original_M_team.gexf',
        'swimming/swimming_backbone_M_team.gexf',
        'swimming/swimming_original_F_individual.gexf',
        'swimming/swimming_backbone_F_individual.gexf',
        'swimming/swimming_original_F_team.gexf',
        'swimming/swimming_backbone_F_team.gexf',

        # Basketball - 4 arquivos (M/F x original/backbone)
        'basketball/basketball_original_M.gexf',
        'basketball/basketball_backbone_M.gexf',
        'basketball/basketball_original_F.gexf',
        'basketball/basketball_backbone_F.gexf',

        # Football - 4 arquivos (M/F x original/backbone)
        'football/football_original_M.gexf',
        'football/football_backbone_M.gexf',
        'football/football_original_F.gexf',
        'football/football_backbone_F.gexf',
    ]

    print(f"\nArquivos esperados: {len(expected_files)}")

    found_count = 0
    missing_files = []

    for expected in expected_files:
        full_path = os.path.join(base_dir, expected)
        if os.path.exists(full_path):
            found_count += 1
            print(f"   {expected}")
        else:
            missing_files.append(expected)
            print(f"   {expected}")

    print(f"\n{'='*50}")
    print(f"RESULTADO: {found_count}/{len(expected_files)} arquivos encontrados")

    if missing_files:
        print(f"\nArquivos faltando:")
        for missing in missing_files:
            print(f"  - {missing}")
    else:
        print("\n SUCESSO! Todas as 16 redes foram geradas!")

    return found_count == len(expected_files)

if __name__ == "__main__":
    success = test_full_mining()