#!/usr/bin/env python3
"""
Verifica os números exatos de atletas mencionados no TCC
para corrigir inconsistências numéricas.
"""

import pandas as pd
from pathlib import Path

# Paths
project_root = Path(__file__).resolve().parents[1]
data_path = project_root / 'data' / 'athlete_events_cleaned.csv'
results_dir = project_root / 'results_per_event_cleaned'

# Os 6 esportes analisados
SIX_SPORTS = ['athletics', 'swimming', 'basketball', 'boxing', 'football', 'judo']

# Os 12 casos de estudo selecionados
TWELVE_CASES = [
    'athletics_M_100m',
    'athletics_F_100m',
    'swimming_M_100m_Freestyle',
    'swimming_F_100m_Freestyle',
    'basketball_M_Basketball_Mens_Basketball',
    'basketball_F_Basketball_Womens_Basketball',
    'boxing_M_Heavy_81-91kg',
    'boxing_F_Middle_69-75kg',
    'football_M_Football_Mens_Football',
    'football_F_Football_Womens_Football',
    'judo_M_-81kg',
    'judo_F_-70kg'
]

def main():
    print("=" * 80)
    print("VERIFICAÇÃO DE CONTAGEM DE ATLETAS - TCC")
    print("=" * 80)

    # Carregar dataset
    print(f"\n[1] Carregando dataset: {data_path}")
    df = pd.read_csv(data_path)

    # 1. Total de atletas no dataset (todos, incluindo não-medalhistas)
    total_athletes = df['ID'].nunique()
    print(f"\n[RESULTADO 1] Total de atletas no dataset completo: {total_athletes:,}")
    print(f"    - Esperado: 137,745")
    print(f"    - Match: {'✓' if total_athletes == 137745 else '✗'}")

    # 2. Atletas medalhistas nos 6 esportes
    print(f"\n[2] Filtrando medalhistas nos 6 esportes: {SIX_SPORTS}")
    df_six_sports = df[df['Sport'].isin([s.title() for s in SIX_SPORTS])]
    df_six_medalists = df_six_sports[df_six_sports['Medal'].notna()]
    medalists_six_sports = df_six_medalists['ID'].nunique()

    print(f"\n[RESULTADO 2] Atletas medalhistas nos 6 esportes:")
    print(f"    - Total: {medalists_six_sports:,}")
    print(f"    - Esperado: 9,350")
    print(f"    - Match: {'✓' if medalists_six_sports == 9350 else '✗'}")

    # Detalhamento por esporte
    print("\n    Detalhamento por esporte:")
    for sport in SIX_SPORTS:
        sport_df = df_six_medalists[df_six_medalists['Sport'] == sport.title()]
        count = sport_df['ID'].nunique()
        print(f"      - {sport.title()}: {count:,} medalhistas")

    # 3. Atletas medalhistas nos 12 casos de estudo
    print(f"\n[3] Contando atletas nos 12 casos selecionados:")

    # Vamos contar de forma direta pelos arquivos GEXF
    import networkx as nx

    total_nodes_12_cases = 0
    unique_athletes_12_cases = set()

    print("\n    Redes analisadas:")
    for i, case in enumerate(TWELVE_CASES, 1):
        # Determinar caminho do arquivo
        sport = case.split('_')[0]
        gexf_path = results_dir / sport / f"{case}.gexf"

        if gexf_path.exists():
            G = nx.read_gexf(gexf_path)
            nodes = set(G.nodes())
            total_nodes_12_cases += len(nodes)
            unique_athletes_12_cases.update(nodes)
            print(f"      {i:2d}. {case:50s} - {len(nodes):4d} atletas")
        else:
            print(f"      {i:2d}. {case:50s} - ARQUIVO NÃO ENCONTRADO")

    print(f"\n[RESULTADO 3] Atletas nos 12 casos de estudo:")
    print(f"    - Total único: {len(unique_athletes_12_cases):,}")
    print(f"    - Soma (com repetições): {total_nodes_12_cases:,}")
    print(f"    - Esperado: 2,978")
    print(f"    - Match: {'✓' if len(unique_athletes_12_cases) == 2978 else '✗'}")

    # 4. Estatísticas adicionais para clareza
    print("\n" + "=" * 80)
    print("HIERARQUIA DO DATASET")
    print("=" * 80)
    print(f"""
┌─ Dataset Completo (1896-2020)
│  └─ {total_athletes:,} atletas totais (medalhistas + não-medalhistas)
│
├─ 6 Esportes Analisados ({', '.join([s.title() for s in SIX_SPORTS])})
│  ├─ {len(df_six_sports):,} participações
│  └─ {medalists_six_sports:,} atletas medalhistas únicos
│     └─ 149 redes (Year × Event × Gender)
│
└─ 12 Casos de Estudo Selecionados (via Iconic Score)
   └─ {len(unique_athletes_12_cases):,} atletas medalhistas únicos
      └─ 12 redes representativas
    """)

    # 5. Gerar tabela LaTeX
    print("\n" + "=" * 80)
    print("TABELA LATEX PARA INSERIR NO TEXTO")
    print("=" * 80)

    latex_table = r"""
\begin{table}[htbp]
\centering
\caption{Hierarquia e dimensões do conjunto de dados analisado}
\label{tab:dataset_hierarchy}
\begin{tabular}{llr}
\toprule
\textbf{Nível} & \textbf{Descrição} & \textbf{Atletas Únicos} \\
\midrule
Dataset completo & Todos os atletas (1896--2020) & """ + f"{total_athletes:,}" + r""" \\
\addlinespace[0.5em]
6 esportes & Medalhistas em """ + ', '.join(SIX_SPORTS) + r""" & """ + f"{medalists_six_sports:,}" + r""" \\
& (149 redes Year $\times$ Event $\times$ Gender) & \\
\addlinespace[0.5em]
12 casos de estudo & Redes selecionadas via \textit{Iconic Score} & """ + f"{len(unique_athletes_12_cases):,}" + r""" \\
& (subseleção representativa) & \\
\bottomrule
\end{tabular}
\end{table}
"""

    print(latex_table)

    # Salvar resultados
    output_file = project_root / 'analysis' / 'athlete_counts_verification.txt'
    with open(output_file, 'w') as f:
        f.write("VERIFICAÇÃO DE CONTAGEM DE ATLETAS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"1. Dataset completo: {total_athletes:,} atletas\n")
        f.write(f"2. 6 esportes (medalhistas): {medalists_six_sports:,} atletas\n")
        f.write(f"3. 12 casos de estudo: {len(unique_athletes_12_cases):,} atletas\n\n")
        f.write("TABELA LATEX:\n")
        f.write(latex_table)

    print(f"\n✓ Resultados salvos em: {output_file}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
