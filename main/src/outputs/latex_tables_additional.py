"""
Gera tabelas LaTeX adicionais para análises de comunidades.

Tabelas geradas:
1. Top 10 Comunidades por Dominância
2. Segregação por Esporte/Sexo
3. Top 5 Comunidades Nucleares
4. Top 10 Rivalidades Estruturais
5. Perfis Competitivos (Resumo)

Uso:
    python scripts/generate_additional_latex_tables.py
"""

import pandas as pd
import os


def generate_latex_table_header(caption, label, columns):
    """Gera cabeçalho padrão de tabela LaTeX."""
    col_spec = 'l' * len(columns)  # Alinhamento à esquerda

    header = f"""\\begin{{table}}[htbp]
\\centering
\\caption{{{caption}}}
\\label{{{label}}}
\\begin{{tabular}}{{{col_spec}}}
\\hline
"""

    # Adicionar nomes das colunas
    header += ' & '.join(columns) + ' \\\\\n'
    header += '\\hline\n'

    return header


def generate_latex_table_footer():
    """Gera rodapé padrão de tabela LaTeX."""
    return """\\hline
\\end{tabular}
\\end{table}

"""


def escape_latex(text):
    """Escapa caracteres especiais do LaTeX."""
    if pd.isna(text):
        return ''

    text = str(text)
    replacements = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def tab1_top10_dominance():
    """Tabela 1: Top 10 Comunidades por Dominância."""
    print("Gerando Tabela 1: Top 10 Dominância...")

    # Carregar dados
    df = pd.read_csv('resultados_teste/additional_analyses/medal_profile_by_community.csv')

    # Merge com hierarquia para obter país dominante
    hierarchy = pd.read_csv('resultados_teste/additional_analyses/community_hierarchy.csv')
    df = df.merge(
        hierarchy[['sport', 'sex', 'community_id', 'dominant_country']],
        on=['sport', 'sex', 'community_id'],
        how='left'
    )

    # Top 10
    top10 = df.nlargest(10, 'dominance_index')

    # Montar tabela LaTeX
    latex = generate_latex_table_header(
        caption='Top 10 comunidades ordenadas por índice de dominância. '
                'O índice varia de 1,0 (todas bronze) até 3,0 (todas ouro).',
        label='tab:top10_dominance',
        columns=['Rank', 'Esporte', 'Sexo', 'Comunidade', 'País', 'Tamanho',
                'Ouro\\%', 'Prata\\%', 'Bronze\\%', 'Dominância', 'Perfil']
    )

    for rank, (idx, row) in enumerate(top10.iterrows(), 1):
        comm_label = f"C{row['community_id']}"

        latex += f"{rank} & "
        latex += f"{escape_latex(row['sport'])} & "
        latex += f"{row['sex']} & "
        latex += f"{comm_label} & "
        latex += f"{escape_latex(row['dominant_country'])} & "
        latex += f"{row['size']} & "
        latex += f"{row['gold_pct']:.1f} & "
        latex += f"{row['silver_pct']:.1f} & "
        latex += f"{row['bronze_pct']:.1f} & "
        latex += f"{row['dominance_index']:.3f} & "
        latex += f"{escape_latex(row['competitive_profile'])} \\\\\n"

    latex += generate_latex_table_footer()

    return latex


def tab2_segregation_by_sport():
    """Tabela 2: Segregação por Esporte/Sexo."""
    print("Gerando Tabela 2: Segregação...")

    df = pd.read_csv('resultados_teste/additional_analyses/inter_community_connectivity.csv')

    latex = generate_latex_table_header(
        caption='Índice de segregação estrutural por esporte e sexo. '
                'Razão Intra/Inter > 1,0 indica comunidade segregada; '
                '< 1,0 indica alta integração.',
        label='tab:segregation',
        columns=['Esporte', 'Sexo', 'Arestas Intra', 'Arestas Inter',
                'Razão Intra\\%', 'Razão Inter\\%', 'Segregação']
    )

    for idx, row in df.iterrows():
        latex += f"{escape_latex(row['sport'])} & "
        latex += f"{row['sex']} & "
        latex += f"{row['intra_edges']:,} & "
        latex += f"{row['inter_edges']:,} & "
        latex += f"{row['intra_ratio']*100:.1f} & "
        latex += f"{row['inter_ratio']*100:.1f} & "
        latex += f"{row['segregation_score']:.2f} \\\\\n"

    latex += generate_latex_table_footer()

    return latex


def tab3_nucleus_communities():
    """Tabela 3: Top 5 Comunidades Nucleares."""
    print("Gerando Tabela 3: Comunidades Nucleares...")

    df = pd.read_csv('resultados_teste/additional_analyses/community_hierarchy.csv')

    # Filtrar núcleo e ordenar por PageRank médio
    nucleus = df[df['hierarchy_level'] == 'Nucleo'].nlargest(5, 'pagerank_mean')

    latex = generate_latex_table_header(
        caption='Top 5 comunidades nucleares ordenadas por PageRank médio. '
                'Comunidades nucleares ocupam posições centrais na estrutura global da rede.',
        label='tab:nucleus_communities',
        columns=['Esporte', 'Sexo', 'Comunidade', 'País', 'Tamanho',
                'PageRank Médio', 'Percentil', 'Score']
    )

    for idx, row in nucleus.iterrows():
        comm_label = f"C{row['community_id']}"

        latex += f"{escape_latex(row['sport'])} & "
        latex += f"{row['sex']} & "
        latex += f"{comm_label} & "
        latex += f"{escape_latex(row['dominant_country'])} & "
        latex += f"{row['size']} & "
        latex += f"{row['pagerank_mean']:.6f} & "
        latex += f"{row['pagerank_percentile']:.1f} & "
        latex += f"{row['centrality_score']:.3f} \\\\\n"

    latex += generate_latex_table_footer()

    return latex


def tab4_top10_rivalries():
    """Tabela 4: Top 10 Rivalidades Estruturais."""
    print("Gerando Tabela 4: Rivalidades...")

    df = pd.read_csv('resultados_teste/additional_analyses/top_rivalry_pairs.csv')

    # Top 10
    top10 = df.nlargest(10, 'num_confronts')

    latex = generate_latex_table_header(
        caption='Top 10 rivalidades estruturais inter-comunidade. '
                'Número de confronts representa confrontos direcionados (A→B + B→A).',
        label='tab:top10_rivalries',
        columns=['Rank', 'Esporte', 'Sexo', 'Comunidade A', 'Comunidade B', 'Confrontos']
    )

    for rank, (idx, row) in enumerate(top10.iterrows(), 1):
        comm_a = f"C{row['community_1']}"
        comm_b = f"C{row['community_2']}"

        latex += f"{rank} & "
        latex += f"{escape_latex(row['sport'])} & "
        latex += f"{row['sex']} & "
        latex += f"{comm_a} & "
        latex += f"{comm_b} & "
        latex += f"{row['num_confronts']:,} \\\\\n"

    latex += generate_latex_table_footer()

    return latex


def tab5_competitive_profiles_summary():
    """Tabela 5: Resumo de Perfis Competitivos."""
    print("Gerando Tabela 5: Perfis Competitivos...")

    df = pd.read_csv('resultados_teste/additional_analyses/medal_profile_by_community.csv')

    # Resumo por perfil
    summary = df.groupby('competitive_profile').agg({
        'community_id': 'count',
        'size': 'mean',
        'gold_pct': 'mean',
        'silver_pct': 'mean',
        'bronze_pct': 'mean',
        'dominance_index': ['mean', 'min', 'max']
    }).reset_index()

    # Achatar colunas
    summary.columns = ['Perfil', 'Contagem', 'Tamanho Médio', 'Ouro% Médio',
                      'Prata% Médio', 'Bronze% Médio', 'D Médio', 'D Mínimo', 'D Máximo']

    latex = generate_latex_table_header(
        caption='Resumo estatístico dos perfis competitivos. '
                'Elite (D $\\geq$ 2,2), Competitiva (1,8 $\\leq$ D $<$ 2,2), '
                'Participante (D $<$ 1,8).',
        label='tab:profiles_summary',
        columns=['Perfil', 'N', 'Tam. Médio', 'Ouro\\%', 'Prata\\%', 'Bronze\\%',
                'D Médio', 'D Mín', 'D Máx']
    )

    for idx, row in summary.iterrows():
        latex += f"{escape_latex(row['Perfil'])} & "
        latex += f"{int(row['Contagem'])} & "
        latex += f"{row['Tamanho Médio']:.1f} & "
        latex += f"{row['Ouro% Médio']:.1f} & "
        latex += f"{row['Prata% Médio']:.1f} & "
        latex += f"{row['Bronze% Médio']:.1f} & "
        latex += f"{row['D Médio']:.3f} & "
        latex += f"{row['D Mínimo']:.3f} & "
        latex += f"{row['D Máximo']:.3f} \\\\\n"

    latex += generate_latex_table_footer()

    return latex


def main():
    """Gera todas as tabelas LaTeX adicionais."""
    print("=" * 60)
    print("GERANDO TABELAS LATEX ADICIONAIS")
    print("=" * 60)

    # Verificar se dados existem
    if not os.path.exists('resultados_teste/additional_analyses'):
        print("\nERRO: Diretório 'resultados_teste/additional_analyses' não encontrado!")
        print("Execute primeiro: python scripts/community_additional_analyses.py")
        return

    # Gerar tabelas
    tables = {
        'tab_top10_dominance.tex': tab1_top10_dominance(),
        'tab_segregation.tex': tab2_segregation_by_sport(),
        'tab_nucleus_communities.tex': tab3_nucleus_communities(),
        'tab_top10_rivalries.tex': tab4_top10_rivalries(),
        'tab_profiles_summary.tex': tab5_competitive_profiles_summary()
    }

    # Salvar arquivos
    output_dir = 'tabelas_latex'
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'=' * 60}")
    print("SALVANDO TABELAS...")
    print("=" * 60)

    for filename, content in tables.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [OK] {filename}")

    print(f"\n{'=' * 60}")
    print("CONCLUÍDO!")
    print("=" * 60)
    print(f"\nTabelas salvas em: {output_dir}/")
    print("\nPara incluir no LaTeX:")
    print("  \\input{tabelas_latex/tab_top10_dominance.tex}")
    print("\nOu copiar o conteúdo diretamente para resultados.tex")


if __name__ == '__main__':
    main()
