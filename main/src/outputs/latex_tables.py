#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para gerar tabelas LaTeX a partir dos resultados da análise de redes.
Gera:
1. Top 20 atletas por PageRank
2. Métricas de rede por esporte/gênero
3. Características das maiores comunidades
"""

import pandas as pd
import json
import os

# Caminhos dos arquivos
RESULTS_DIR = "../../results"
ATHLETES_FILE = os.path.join(RESULTS_DIR, "consolidated_sports_network_analysis.csv")
COMMUNITIES_FILE = os.path.join(RESULTS_DIR, "community_profiles_enriched.csv")
OUTPUT_DIR = "../../docs/monografia/tabelas"

# Criar diretório de saída se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    """Carrega os dados dos arquivos CSV"""
    athletes_df = pd.read_csv(ATHLETES_FILE)
    communities_df = pd.read_csv(COMMUNITIES_FILE)
    return athletes_df, communities_df

def generate_top_pagerank_table(df, n=20):
    """Gera tabela com top N atletas por PageRank"""

    # Ordenar por PageRank e pegar top N
    top_athletes = df.nlargest(n, 'original_pagerank')[
        ['name', 'sport', 'noc', 'original_pagerank']
    ].copy()

    # Renomear colunas
    top_athletes.columns = ['Atleta', 'Esporte', 'País', 'PageRank']

    # Formatar PageRank com 4 casas decimais
    top_athletes['PageRank'] = top_athletes['PageRank'].apply(lambda x: f"{x:.4f}")

    # Traduzir esportes
    sport_translation = {
        'Swimming': 'Natação',
        'Basketball': 'Basquetebol',
        'Football': 'Futebol'
    }
    top_athletes['Esporte'] = top_athletes['Esporte'].map(sport_translation)

    # Gerar LaTeX
    latex_code = r"""\begin{table}[htbp]
\caption{Top 20 atletas por PageRank global}
\label{tab:top20_pagerank}
\centering
\footnotesize
\begin{tabular}{rp{6cm}llr}
\toprule
\textbf{Pos.} & \textbf{Atleta} & \textbf{Esporte} & \textbf{País} & \textbf{PageRank} \\
\midrule
"""

    for idx, row in enumerate(top_athletes.itertuples(index=False), 1):
        latex_code += f"{idx} & {row.Atleta} & {row.Esporte} & {row.País} & {row.PageRank} \\\\\n"

    latex_code += r"""\bottomrule
\end{tabular}
\end{table}
"""

    # Salvar arquivo
    output_file = os.path.join(OUTPUT_DIR, "tab_top20_pagerank.tex")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_code)

    print(f"[OK] Tabela Top 20 PageRank gerada: {output_file}")
    return latex_code

def generate_network_metrics_table(df):
    """Gera tabela com métricas de rede por esporte/gênero"""

    # Agrupar por esporte e gênero
    metrics_data = []

    for sport in ['Swimming', 'Basketball', 'Football']:
        for sex in ['M', 'F']:
            subset = df[(df['sport'] == sport) & (df['sex'] == sex)]

            if len(subset) == 0:
                continue

            n_athletes = len(subset)
            n_communities = subset['original_community'].nunique()

            # Métricas médias
            avg_pagerank = subset['original_pagerank'].mean()
            avg_degree = subset['original_total_degree'].mean()
            avg_betweenness = subset['original_betweenness_centrality'].mean()

            # Traduzir esporte
            sport_pt = {'Swimming': 'Natação', 'Basketball': 'Basquetebol', 'Football': 'Futebol'}[sport]
            sex_pt = {'M': 'Masculino', 'F': 'Feminino'}[sex]

            metrics_data.append({
                'Esporte': sport_pt,
                'Gênero': sex_pt,
                'N. Atletas': n_athletes,
                'N. Comunidades': n_communities,
                'PageRank Médio': f"{avg_pagerank:.6f}",
                'Grau Médio': f"{avg_degree:.1f}",
                'Betweenness Médio': f"{avg_betweenness:.6f}"
            })

    metrics_df = pd.DataFrame(metrics_data)

    # Gerar LaTeX
    latex_code = r"""\begin{table}[htbp]
\caption{Métricas de rede por esporte e gênero}
\label{tab:network_metrics}
\centering
\small
\begin{tabular}{llrrrr}
\toprule
\textbf{Esporte} & \textbf{Gênero} & \textbf{Atletas} & \textbf{Comunidades} & \textbf{PR Médio} & \textbf{Grau Médio} \\
\midrule
"""

    for row in metrics_df.itertuples(index=False):
        latex_code += f"{row.Esporte} & {row.Gênero} & {row[2]} & {row[3]} & {row[4]} & {row[5]} \\\\\n"

    latex_code += r"""\bottomrule
\end{tabular}
\end{table}
"""

    # Salvar arquivo
    output_file = os.path.join(OUTPUT_DIR, "tab_network_metrics.tex")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_code)

    print(f"[OK] Tabela de métricas de rede gerada: {output_file}")
    return latex_code

def generate_communities_table(communities_df, n=10):
    """Gera tabela com características das maiores comunidades"""

    # Ordenar por tamanho e pegar top N
    top_communities = communities_df.nlargest(n, 'size')[
        ['sport', 'sex', 'community_id', 'size', 'span_years',
         'temporal_entropy', 'geographic_hhi', 'pagerank_mean', 'dominant_country']
    ].copy()

    # Traduzir esportes
    sport_translation = {
        'Swimming': 'Natação',
        'Basketball': 'Basquetebol',
        'Football': 'Futebol'
    }
    top_communities['sport'] = top_communities['sport'].map(sport_translation)

    # Gerar LaTeX
    latex_code = r"""\begin{table}[htbp]
\caption{Características das 10 maiores comunidades}
\label{tab:top_communities}
\centering
\footnotesize
\begin{tabular}{llrrrrrl}
\toprule
\textbf{Esporte} & \textbf{Gênero} & \textbf{ID} & \textbf{Tamanho} & \textbf{Anos} & \textbf{Entropia} & \textbf{HHI} & \textbf{País Dom.} \\
\midrule
"""

    for row in top_communities.itertuples(index=False):
        latex_code += f"{row.sport} & {row.sex} & {row.community_id} & {row.size} & {int(row.span_years)} & {row.temporal_entropy:.2f} & {row.geographic_hhi:.2f} & {row.dominant_country} \\\\\n"

    latex_code += r"""\bottomrule
\end{tabular}
\end{table}
"""

    # Salvar arquivo
    output_file = os.path.join(OUTPUT_DIR, "tab_top_communities.tex")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_code)

    print(f"[OK] Tabela de comunidades gerada: {output_file}")
    return latex_code

def main():
    """Função principal"""
    print("Gerando tabelas LaTeX a partir dos resultados...")
    print(f"Diretório de entrada: {RESULTS_DIR}")
    print(f"Diretório de saída: {OUTPUT_DIR}\n")

    # Carregar dados
    athletes_df, communities_df = load_data()
    print(f"[OK] Dados carregados: {len(athletes_df)} atletas, {len(communities_df)} comunidades\n")

    # Gerar tabelas
    generate_top_pagerank_table(athletes_df, n=20)
    generate_network_metrics_table(athletes_df)
    generate_communities_table(communities_df, n=10)

    print("\n[OK] Todas as tabelas foram geradas com sucesso!")
    print(f"Arquivos salvos em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
