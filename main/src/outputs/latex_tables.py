#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para gerar tabelas LaTeX a partir dos resultados da análise de redes.
Gera:
1. Top 20 atletas por PageRank
2. Métricas de rede por esporte/gênero
3. Características das maiores comunidades
4. Atletas-ponte (bridge athletes)
5. Top 10 rivalidades estruturais
"""

import pandas as pd
import json
import os

# Caminhos dos arquivos (relativos ao diretório raiz do projeto)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..", "..", "..")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
ATHLETES_FILE = os.path.join(RESULTS_DIR, "consolidated_sports_network_analysis.csv")
COMMUNITIES_FILE = os.path.join(RESULTS_DIR, "community_profiles_enriched.csv")
RIVALRIES_FILE = os.path.join(RESULTS_DIR, "additional_analyses", "top_rivalry_pairs.csv")
COHESION_FILE = os.path.join(RESULTS_DIR, "community_cohesion_metrics.csv")
NETWORK_SUMMARY_FILE = os.path.join(RESULTS_DIR, "all_network_summaries.json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "monografia", "tabelas")

# Criar diretório de saída se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    """Carrega os dados dos arquivos CSV"""
    athletes_df = pd.read_csv(ATHLETES_FILE)
    communities_df = pd.read_csv(COMMUNITIES_FILE)
    return athletes_df, communities_df

def generate_structural_metrics_summary(df, communities_df):
    """Gera tabela síntese com métricas estruturais para as 16 redes (incluindo event_type para Swimming/Athletics)"""

    # Traduzir esportes
    sport_translation = {
        'Swimming': 'Natação',
        'Athletics': 'Atletismo',
        'Basketball': 'Basquetebol',
        'Football': 'Futebol',
        'Judo': 'Judô',
        'Boxing': 'Boxe'
    }

    event_translation = {
        'individual': 'Individual',
        'team': 'Revezamento'
    }

    # Organizar dados por tipologia
    sport_order = ['Swimming', 'Athletics', 'Basketball', 'Football', 'Judo', 'Boxing']
    rows = []

    # Calcular métricas agregadas por esporte/sexo a partir dos dados de coesão
    cohesion_df = pd.read_csv(COHESION_FILE)

    for sport in sport_order:
        # Swimming e Athletics têm event_type (individual/team)
        if sport in ['Swimming', 'Athletics']:
            for sex in ['M', 'F']:
                for event_type in ['individual', 'team']:
                    # Filtrar atletas deste esporte/sexo/event_type
                    sport_data = df[
                        (df['sport'] == sport) &
                        (df['sex'] == sex) &
                        (df['event_type'] == event_type)
                    ]

                    if len(sport_data) == 0:
                        continue

                    n_nodes = len(sport_data)
                    n_communities = sport_data['original_community'].nunique()

                    # Buscar modularidade e densidade dos dados de coesão
                    sport_lower = sport.lower()
                    cohesion_sport = cohesion_df[
                        (cohesion_df['sport'] == sport_lower) &
                        (cohesion_df['sex'] == sex) &
                        (cohesion_df['event_type'] == event_type)
                    ]

                    # Calcular médias ponderadas por tamanho de comunidade
                    if len(cohesion_sport) > 0:
                        modularity = cohesion_sport['subcommunity_modularity'].mean()
                        density = cohesion_sport['density'].mean()
                    else:
                        # Buscar do JSON específico
                        json_file = os.path.join(RESULTS_DIR, sport_lower, f"{sport_lower}_{sex}_{event_type}_network_summary.json")
                        if os.path.exists(json_file):
                            with open(json_file, 'r') as f:
                                data = json.load(f)
                                modularity = data.get('original_community', {}).get('modularity', 0.0)
                                density = data.get('original_network', {}).get('density', 0.0)
                        else:
                            modularity = 0.0
                            density = 0.0

                    rows.append({
                        'sport': sport_translation[sport],
                        'event': event_translation[event_type],
                        'sex': sex,
                        'n_nodes': n_nodes,
                        'n_communities': n_communities,
                        'modularity': modularity,
                        'density': density
                    })
        else:
            # Outros esportes: apenas M/F
            for sex in ['M', 'F']:
                # Filtrar atletas deste esporte/sexo
                sport_data = df[(df['sport'] == sport) & (df['sex'] == sex)]

                if len(sport_data) == 0:
                    continue

                n_nodes = len(sport_data)
                n_communities = sport_data['original_community'].nunique()

                # Buscar modularidade e densidade dos dados de coesão
                sport_lower = sport.lower()
                cohesion_sport = cohesion_df[
                    (cohesion_df['sport'] == sport_lower) &
                    (cohesion_df['sex'] == sex)
                ]

                # Calcular médias ponderadas por tamanho de comunidade
                if len(cohesion_sport) > 0:
                    modularity = cohesion_sport['subcommunity_modularity'].mean()
                    density = cohesion_sport['density'].mean()
                else:
                    modularity = 0.0
                    density = 0.0

                # Para Judo e Boxing, buscar dos arquivos JSON individuais (dados de coesão estão incorretos)
                if sport in ['Judo', 'Boxing'] and (modularity == 0.0 or density == 0.0):
                    json_file = os.path.join(RESULTS_DIR, sport_lower, f"{sport_lower}_{sex}_individual_network_summary.json")
                    if os.path.exists(json_file):
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            modularity = data.get('original_community', {}).get('modularity', 0.0)
                            density = data.get('original_network', {}).get('density', 0.0)

                rows.append({
                    'sport': sport_translation[sport],
                    'event': '—',  # Outros esportes não têm event_type
                    'sex': sex,
                    'n_nodes': n_nodes,
                    'n_communities': n_communities,
                    'modularity': modularity,
                    'density': density
                })

    # Gerar LaTeX
    latex_code = r"""\begin{table}[htbp]
\caption{Métricas estruturais das 16 redes competitivas por esporte, tipo de evento e gênero. Modularidade quantifica segregação comunitária (valores altos indicam comunidades bem definidas), densidade mede interconectividade global. Esportes mistos (Natação, Atletismo) segregam eventos individuais e revezamentos.}
\label{tab:structural_metrics_summary}
\centering
\footnotesize
\begin{tabular}{lllrrrr}
\toprule
\textbf{Esporte} & \textbf{Tipo} & \textbf{Gênero} & \textbf{Atletas} & \textbf{Comunidades} & \textbf{Modularidade} & \textbf{Densidade} \\
\midrule
"""

    for row in rows:
        latex_code += f"{row['sport']} & {row['event']} & {row['sex']} & {row['n_nodes']} & {row['n_communities']} & {row['modularity']:.3f} & {row['density']:.3f} \\\\\n"

    latex_code += r"""\bottomrule
\end{tabular}
\end{table}
"""

    # Salvar arquivo
    output_file = os.path.join(OUTPUT_DIR, "tab_structural_metrics_summary.tex")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_code)

    print(f"[OK] Tabela de métricas estruturais (resumo) gerada: {output_file}")
    return latex_code

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
        'Football': 'Futebol',
        'Athletics': 'Atletismo',
        'Judo': 'Judô',
        'Boxing': 'Boxe'
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
    """Gera tabela com métricas de rede por esporte/gênero/tipo (para Swimming e Athletics)"""

    # Agrupar por esporte e gênero
    metrics_data = []

    for sport in ['Swimming', 'Athletics', 'Basketball', 'Football', 'Judo', 'Boxing']:
        # Swimming e Athletics têm event_type
        if sport in ['Swimming', 'Athletics']:
            for sex in ['M', 'F']:
                for event_type in ['individual', 'team']:
                    subset = df[
                        (df['sport'] == sport) &
                        (df['sex'] == sex) &
                        (df['event_type'] == event_type)
                    ]

                    if len(subset) == 0:
                        continue

                    n_athletes = len(subset)
                    n_communities = subset['original_community'].nunique()

                    # Métricas médias
                    avg_pagerank = subset['original_pagerank'].mean()
                    avg_degree = subset['original_total_degree'].mean()
                    avg_betweenness = subset['original_betweenness_centrality'].mean()

                    # Traduzir esporte e tipo
                    sport_pt = {
                        'Swimming': 'Natação',
                        'Athletics': 'Atletismo'
                    }[sport]
                    sex_pt = {'M': 'Masculino', 'F': 'Feminino'}[sex]
                    type_pt = {'individual': 'Individual', 'team': 'Revezamento'}[event_type]

                    metrics_data.append({
                        'Esporte': sport_pt,
                        'Tipo': type_pt,
                        'Gênero': sex_pt,
                        'N. Atletas': n_athletes,
                        'N. Comunidades': n_communities,
                        'PageRank Médio': f"{avg_pagerank:.6f}",
                        'Grau Médio': f"{avg_degree:.1f}",
                        'Betweenness Médio': f"{avg_betweenness:.6f}"
                    })
        else:
            # Outros esportes sem event_type
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
                sport_pt = {
                    'Basketball': 'Basquetebol',
                    'Football': 'Futebol',
                    'Judo': 'Judô',
                    'Boxing': 'Boxe'
                }[sport]
                sex_pt = {'M': 'Masculino', 'F': 'Feminino'}[sex]

                metrics_data.append({
                    'Esporte': sport_pt,
                    'Tipo': '—',
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
\caption{Métricas de rede por esporte, tipo e gênero. Para esportes mistos (Natação, Atletismo), diferencia eventos individuais e revezamentos.}
\label{tab:network_metrics}
\centering
\footnotesize
\begin{tabular}{lllrrrr}
\toprule
\textbf{Esporte} & \textbf{Tipo} & \textbf{Gênero} & \textbf{Atletas} & \textbf{Comunidades} & \textbf{PR Médio} & \textbf{Grau Médio} \\
\midrule
"""

    for row in metrics_df.itertuples(index=False):
        latex_code += f"{row.Esporte} & {row.Tipo} & {row.Gênero} & {row[3]} & {row[4]} & {row[5]} & {row[6]} \\\\\n"

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

def generate_communities_table(communities_df, athletes_df, n=10):
    """Gera tabela com características das maiores comunidades (incluindo event_type para Swimming/Athletics)"""

    # Ordenar por tamanho e pegar top N
    top_communities = communities_df.nlargest(n, 'size')[
        ['sport', 'sex', 'community_id', 'size', 'span_years',
         'temporal_entropy', 'geographic_entropy', 'pagerank_mean', 'dominant_country']
    ].copy()

    # Adicionar event_type para Swimming e Athletics
    event_types = []
    for idx, row in top_communities.iterrows():
        if row['sport'] in ['Swimming', 'Athletics']:
            # Buscar event_type dos atletas desta comunidade
            community_athletes = athletes_df[
                (athletes_df['sport'] == row['sport']) &
                (athletes_df['sex'] == row['sex']) &
                (athletes_df['original_community'] == row['community_id'])
            ]
            if len(community_athletes) > 0 and 'event_type' in community_athletes.columns:
                event_type = community_athletes['event_type'].mode()[0]  # Mais comum
                event_types.append({'individual': 'Ind.', 'team': 'Revez.'}[event_type])
            else:
                event_types.append('—')
        else:
            event_types.append('—')

    top_communities['event_type_label'] = event_types

    # Traduzir esportes
    sport_translation = {
        'Swimming': 'Natação',
        'Basketball': 'Basquetebol',
        'Football': 'Futebol',
        'Athletics': 'Atletismo',
        'Judo': 'Judô',
        'Boxing': 'Boxe'
    }
    top_communities['sport'] = top_communities['sport'].map(sport_translation)

    # Gerar LaTeX
    latex_code = r"""\begin{table}[htbp]
\caption{Características das 10 maiores comunidades. Para esportes mistos, indica tipo de evento (Ind. = Individual, Revez. = Revezamento).}
\label{tab:top_communities}
\centering
\footnotesize
\begin{tabular}{lllrrrrrl}
\toprule
\textbf{Esporte} & \textbf{Tipo} & \textbf{Gênero} & \textbf{ID} & \textbf{Tamanho} & \textbf{Anos} & \textbf{Entropia} & \textbf{HHI} & \textbf{País Dom.} \\
\midrule
"""

    for row in top_communities.itertuples(index=False):
        latex_code += f"{row.sport} & {row.event_type_label} & {row.sex} & {row.community_id} & {row.size} & {int(row.span_years)} & {row.temporal_entropy:.2f} & {row.geographic_entropy:.2f} & {row.dominant_country} \\\\\n"

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

def generate_bridge_athletes_table(df, n_per_sport=3):
    """Gera tabela com atletas-ponte (maior betweenness centrality) por esporte"""

    # Traduzir esportes
    sport_translation = {
        'Swimming': 'Natação',
        'Basketball': 'Basquetebol',
        'Football': 'Futebol',
        'Athletics': 'Atletismo',
        'Judo': 'Judô',
        'Boxing': 'Boxe'
    }

    bridge_athletes = []

    # Para cada esporte, pegar os N atletas com maior betweenness
    for sport in ['Swimming', 'Athletics', 'Basketball', 'Football', 'Judo', 'Boxing']:
        sport_data = df[df['sport'] == sport].copy()

        # Filtrar atletas com betweenness > 0
        sport_data = sport_data[sport_data['original_betweenness_centrality'] > 0]

        if len(sport_data) == 0:
            continue

        # Pegar top N
        top_bridges = sport_data.nlargest(n_per_sport, 'original_betweenness_centrality')[
            ['name', 'noc', 'sex', 'original_betweenness_centrality']
        ]

        for _, row in top_bridges.iterrows():
            bridge_athletes.append({
                'Esporte': sport_translation[sport],
                'Nome': row['name'],
                'País': row['noc'],
                'Sexo': row['sex'],
                'Betweenness': f"{row['original_betweenness_centrality']:.4f}"
            })

    # Gerar LaTeX
    latex_code = r"""\begin{table}[htbp]
\centering
\caption{Atletas-ponte com maior betweenness centrality por modalidade. Atletas-ponte ocupam posições estruturais críticas conectando diferentes comunidades ou eras competitivas.}
\label{tab:bridge_athletes}
\footnotesize
\begin{tabular}{@{}llllr@{}}
\toprule
\textbf{Esporte} & \textbf{Nome} & \textbf{País} & \textbf{Sexo} & \textbf{Betweenness} \\
\midrule
"""

    for athlete in bridge_athletes:
        latex_code += f"{athlete['Esporte']} & {athlete['Nome']} & {athlete['País']} & {athlete['Sexo']} & {athlete['Betweenness']} \\\\\n"

    latex_code += r"""\bottomrule
\end{tabular}
\end{table}
"""

    # Salvar arquivo
    output_file = os.path.join(OUTPUT_DIR, "tab_bridge_athletes.tex")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_code)

    print(f"[OK] Tabela de atletas-ponte gerada: {output_file}")
    return latex_code

def generate_top_rivalries_table(athletes_df, n=10):
    """Gera tabela com top N rivalidades estruturais (incluindo event_type para Swimming/Athletics)"""

    # Ler arquivo de rivalidades
    rivalries_df = pd.read_csv(RIVALRIES_FILE)

    # Traduzir esportes
    sport_translation = {
        'Swimming': 'Natação',
        'Basketball': 'Basquetebol',
        'Football': 'Futebol',
        'Athletics': 'Atletismo',
        'Judo': 'Judô',
        'Boxing': 'Boxe'
    }

    # Ordenar por número de confrontos e pegar top N
    top_rivalries = rivalries_df.nlargest(n, 'num_confronts')[
        ['sport', 'sex', 'community_1', 'community_2', 'num_confronts']
    ].copy()

    # Adicionar event_type para Swimming e Athletics
    event_types = []
    for idx, row in top_rivalries.iterrows():
        if row['sport'] in ['Swimming', 'Athletics']:
            # Buscar event_type dos atletas destas comunidades
            community_athletes = athletes_df[
                (athletes_df['sport'] == row['sport']) &
                (athletes_df['sex'] == row['sex']) &
                ((athletes_df['original_community'] == row['community_1']) |
                 (athletes_df['original_community'] == row['community_2']))
            ]
            if len(community_athletes) > 0 and 'event_type' in community_athletes.columns:
                event_type = community_athletes['event_type'].mode()[0]
                event_types.append({'individual': 'Ind.', 'team': 'Revez.'}[event_type])
            else:
                event_types.append('—')
        else:
            event_types.append('—')

    top_rivalries['event_type_label'] = event_types

    # Traduzir esporte
    top_rivalries['sport'] = top_rivalries['sport'].map(sport_translation)

    # Formatar número de confrontos
    top_rivalries['num_confronts'] = top_rivalries['num_confronts'].apply(lambda x: f"{x:,}".replace(',', '.'))

    # Gerar LaTeX
    latex_code = r"""\begin{table}[htbp]
\centering
\caption{Top 10 rivalidades estruturais inter-comunidade. Número de confrontos representa confrontos direcionados (A→B). Para esportes mistos, indica tipo de evento.}
\label{tab:top10_rivalries}
\small
\begin{tabular}{rlllccr}
\toprule
\textbf{Rank} & \textbf{Esporte} & \textbf{Tipo} & \textbf{Sexo} & \textbf{Com. A} & \textbf{Com. B} & \textbf{Confrontos} \\
\midrule
"""

    for idx, row in enumerate(top_rivalries.itertuples(index=False), 1):
        latex_code += f"{idx} & {row.sport} & {row.event_type_label} & {row.sex} & C{row.community_1} & C{row.community_2} & {row.num_confronts} \\\\\n"

    latex_code += r"""\bottomrule
\end{tabular}
\end{table}
"""

    # Salvar arquivo
    output_file = os.path.join(OUTPUT_DIR, "tab_top10_rivalries.tex")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_code)

    print(f"[OK] Tabela de rivalidades gerada: {output_file}")
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
    generate_structural_metrics_summary(athletes_df, communities_df)  # Tabela nova para início dos resultados
    generate_top_pagerank_table(athletes_df, n=20)
    generate_network_metrics_table(athletes_df)
    generate_communities_table(communities_df, athletes_df, n=10)
    generate_bridge_athletes_table(athletes_df, n_per_sport=3)
    generate_top_rivalries_table(athletes_df, n=10)

    print("\n[OK] Todas as tabelas foram geradas com sucesso!")
    print(f"Arquivos salvos em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
