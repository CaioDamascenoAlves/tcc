#!/usr/bin/env python3
"""
Roda validação Louvain vs Infomap nas 12 redes principais do estudo
e gera tabela LaTeX consolidada.
"""

import subprocess
import json
from pathlib import Path
import pandas as pd

# 12 redes principais do estudo
NETWORKS = [
    ("athletics/athletics_M_100m", "Athletics 100m", "M"),
    ("athletics/athletics_F_100m", "Athletics 100m", "F"),
    ("swimming/swimming_M_100m_Freestyle", "Swimming 100m Free", "M"),
    ("swimming/swimming_F_100m_Freestyle", "Swimming 100m Free", "F"),
    ("basketball/basketball_M_Basketball_Mens_Basketball", "Basketball", "M"),
    ("basketball/basketball_F_Basketball_Womens_Basketball", "Basketball", "F"),
    ("football/football_M_Football_Mens_Football", "Football", "M"),
    ("football/football_F_Football_Womens_Football", "Football", "F"),
    ("judo/judo_M_-90kg", "Judo -90kg", "M"),
    ("judo/judo_F_-70kg", "Judo -70kg", "F"),
    # Boxe - vou usar as categorias com mais dados
    ("boxing/boxing_M_Fly_48-52kg", "Boxing Fly", "M"),
    ("boxing/boxing_F_Fly_48-51kg", "Boxing Fly", "F"),
]

RESULTS_DIR = Path(__file__).parent / 'validation_results'
SCRIPT_PATH = Path(__file__).parent / 'validate_louvain_infomap_per_event.py'

def run_validation(network_path):
    """Roda validação para uma rede específica."""
    cmd = [
        'python3',
        str(SCRIPT_PATH),
        '--event', network_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Extrair nome do arquivo JSON gerado
    safe_name = network_path.replace('/', '_')
    json_path = RESULTS_DIR / f'validation_{safe_name}.json'

    if json_path.exists():
        with open(json_path) as f:
            return json.load(f)
    else:
        print(f"ERRO: Arquivo não encontrado {json_path}")
        return None

def main():
    print("=" * 80)
    print("VALIDAÇÃO LOUVAIN vs INFOMAP - 12 REDES PRINCIPAIS")
    print("=" * 80)
    print()

    results = []

    for i, (network_path, sport_name, gender) in enumerate(NETWORKS, 1):
        print(f"[{i}/12] {sport_name} {gender}...")

        data = run_validation(network_path)

        if data:
            results.append({
                'Sport': sport_name,
                'Gender': gender,
                'Nodes': data['network']['nodes'],
                'Edges': data['network']['edges'],
                'NMI': data['comparison']['nmi'],
                'ARI': data['comparison']['ari'],
                'Q_Louvain': data['louvain']['modularity'],
                'Q_Infomap': data['infomap']['modularity'],
                'Comm_L': data['louvain']['num_communities'],
                'Comm_I': data['infomap']['num_communities'],
            })
            print(f"  ✓ NMI={data['comparison']['nmi']:.4f}, Q_L={data['louvain']['modularity']:.4f}")
        else:
            print(f"  ✗ ERRO")

        print()

    # Criar DataFrame
    df = pd.DataFrame(results)

    # Calcular médias
    avg_row = {
        'Sport': '\\textbf{MÉDIA}',
        'Gender': '',
        'Nodes': int(df['Nodes'].mean()),
        'Edges': int(df['Edges'].mean()),
        'NMI': df['NMI'].mean(),
        'ARI': df['ARI'].mean(),
        'Q_Louvain': df['Q_Louvain'].mean(),
        'Q_Infomap': df['Q_Infomap'].mean(),
        'Comm_L': '',
        'Comm_I': '',
    }

    # Gerar tabela LaTeX
    latex = r"""\begin{table}[h]
\centering
\caption{Validação empírica Louvain vs Infomap nas 12 redes principais do estudo}
\label{tab:louvain_infomap_validation_12networks}
\small
\begin{tabular}{llrrcccccc}
\hline
\textbf{Esporte} & \textbf{G} & \textbf{N} & \textbf{E} & \textbf{NMI} & \textbf{ARI} & \textbf{Q(L)} & \textbf{Q(I)} & \textbf{C(L)} & \textbf{C(I)} \\
\hline
"""

    for _, row in df.iterrows():
        latex += f"{row['Sport']} & {row['Gender']} & {row['Nodes']} & {row['Edges']} & "
        latex += f"{row['NMI']:.4f} & {row['ARI']:.4f} & "
        latex += f"{row['Q_Louvain']:.4f} & {row['Q_Infomap']:.4f} & "
        latex += f"{row['Comm_L']} & {row['Comm_I']} \\\\\n"

    latex += r"""\hline
"""
    latex += f"{avg_row['Sport']} & {avg_row['Gender']} & {avg_row['Nodes']} & {avg_row['Edges']} & "
    latex += f"{avg_row['NMI']:.4f} & {avg_row['ARI']:.4f} & "
    latex += f"{avg_row['Q_Louvain']:.4f} & {avg_row['Q_Infomap']:.4f} & "
    latex += f"{avg_row['Comm_L']} & {avg_row['Comm_I']} \\\\\n"

    latex += r"""\hline
\end{tabular}

\vspace{0.3cm}

\footnotesize
\textit{Legenda: G = Gênero (M/F); N = Nós; E = Arestas; NMI = Normalized Mutual Information; ARI = Adjusted Rand Index; Q = Modularidade; C = Comunidades; L = Louvain; I = Infomap. NMI médio de """ + f"{avg_row['NMI']:.4f}" + r""" confirma alta concordância estrutural entre os algoritmos em todas as redes analisadas.}
\end{table}
"""

    # Salvar tabela
    latex_path = RESULTS_DIR / 'validation_12networks_consolidated.tex'
    with open(latex_path, 'w') as f:
        f.write(latex)

    print("=" * 80)
    print("RESULTADOS CONSOLIDADOS")
    print("=" * 80)
    print()
    print(df.to_string(index=False))
    print()
    print(f"NMI médio: {avg_row['NMI']:.4f}")
    print(f"ARI médio: {avg_row['ARI']:.4f}")
    print(f"Q(Louvain) médio: {avg_row['Q_Louvain']:.4f}")
    print(f"Q(Infomap) médio: {avg_row['Q_Infomap']:.4f}")
    print()
    print("=" * 80)
    print(f"Tabela LaTeX salva em: {latex_path}")
    print("=" * 80)

if __name__ == '__main__':
    main()
