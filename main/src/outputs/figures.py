"""
Script para gerar figuras estaticas de alta qualidade para a monografia.
Gera arquivos PNG (300 DPI) prontos para inclusao em LaTeX.

Uso:
    python generate_plots_for_paper.py

Saida:
    Figuras salvas em ../monografia/figuras/
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Adicionar project ao path para importar metrics e config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.metrics import MetricsCalculator
from core.config.constants import MEDAL_WEIGHTS, DOMINANCE_THRESHOLDS

# Configuracao global para qualidade de publicacao
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13

# Paleta de cores consistente
COLORS = {
    'Swimming': '#1f77b4',
    'Basketball': '#ff7f0e',
    'Football': '#2ca02c',
    'M': '#3498db',
    'F': '#e74c3c',
    'Nucleo': '#e74c3c',
    'Intermediaria': '#f39c12',
    'Periferica': '#3498db',
    'Elite': '#8e44ad',
    'Competitiva': '#27ae60',
    'Participante': '#95a5a6'
}


def setup_output_dir():
    """Cria diretorio de saida para as figuras."""
    output_dir = Path('../../../monografia/figuras')
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def load_data():
    """Carrega todos os arquivos CSV das analises."""
    base_dir = '../../../results'

    print("Carregando dados...")

    # Tentar carregar arquivos de análises adicionais
    # Prioriza arquivos em additional_analyses/, fallback para base_dir
    additional_dir = f'{base_dir}/additional_analyses'

    try:
        medal_df = pd.read_csv(f'{additional_dir}/medal_profile_by_community.csv')
        print("  [OK] medal_profile carregado de additional_analyses/")
    except:
        try:
            medal_df = pd.read_csv(f'{base_dir}/community_profiles_enriched.csv')
            print("  [OK] usando community_profiles_enriched.csv como fallback")
        except Exception as e:
            print(f"  [ERRO] Nao foi possivel carregar perfis: {e}")
            raise

    try:
        inter_df = pd.read_csv(f'{additional_dir}/inter_community_connectivity.csv')
        print("  [OK] inter_community carregado")
    except:
        inter_df = None

    try:
        hierarchy_df = pd.read_csv(f'{additional_dir}/community_hierarchy.csv')
        print("  [OK] hierarchy carregado")
    except:
        hierarchy_df = None

    try:
        rivalry_df = pd.read_csv(f'{additional_dir}/top_rivalry_pairs.csv')
        print("  [OK] rivalry carregado")
    except:
        rivalry_df = None

    # Carregar dados consolidados para metricas de atletas
    consolidated_df = pd.read_csv(f'{base_dir}/consolidated_sports_network_analysis.csv')

    # CALCULAR dominance_index se nao existir (formula 3-2-1)
    if 'dominance_index' not in medal_df.columns:
        print("  [CALCULO] Adicionando dominance_index usando MetricsCalculator...")

        # Calcular percentuais de cada tipo de medalha
        medal_df['gold_pct'] = (medal_df['gold_count'] / medal_df['total_medals']) * 100
        medal_df['silver_pct'] = (medal_df['silver_count'] / medal_df['total_medals']) * 100
        medal_df['bronze_pct'] = (medal_df['bronze_count'] / medal_df['total_medals']) * 100

        # Calcular dominance_index usando funcao centralizada
        medal_df['dominance_index'] = medal_df.apply(
            lambda row: MetricsCalculator.calculate_dominance_index(
                row['gold_pct'], row['silver_pct'], row['bronze_pct']
            ),
            axis=1
        )

    # CALCULAR segregation_ratio se tiver dados de cohesion
    try:
        cohesion_df = pd.read_csv(f'{base_dir}/community_cohesion_metrics.csv')
        medal_df = medal_df.merge(
            cohesion_df[['sport', 'sex', 'community_id', 'intra_inter_ratio']],
            on=['sport', 'sex', 'community_id'],
            how='left'
        )
        medal_df.rename(columns={'intra_inter_ratio': 'segregation_ratio'}, inplace=True)
        print("  [OK] segregation_ratio adicionado de cohesion_metrics")
    except:
        print("  [AVISO] Nao foi possivel adicionar segregation_ratio")

    print(f"  - {len(medal_df)} comunidades (perfil de medalhas)")
    if inter_df is not None:
        print(f"  - {len(inter_df)} pares inter-comunidade")
    else:
        print("  - inter-comunidade: arquivo nao encontrado")

    if hierarchy_df is not None:
        print(f"  - {len(hierarchy_df)} comunidades (hierarquia)")
    else:
        print("  - hierarquia: arquivo nao encontrado")

    if rivalry_df is not None:
        print(f"  - {len(rivalry_df)} rivalidades estruturais")
    else:
        print("  - rivalidades: arquivo nao encontrado")

    print(f"  - {len(consolidated_df)} atletas (metricas)")

    return medal_df, inter_df, hierarchy_df, rivalry_df, consolidated_df


def fig1_size_vs_pagerank(hierarchy_df, medal_df, output_dir):
    """
    Figura 1: Scatter plot Tamanho vs PageRank Medio
    Mostra que tamanho != centralidade estrutural
    """
    print("\nGerando Figura 1: Tamanho vs PageRank...")

    # hierarchy_df ja tem todas as colunas necessarias (size, pagerank_mean, etc)
    fig, ax = plt.subplots(figsize=(10, 6))

    # Normalizar nomes de niveis (remover acentos)
    hierarchy_df = hierarchy_df.copy()
    hierarchy_df['hierarchy_level'] = hierarchy_df['hierarchy_level'].str.replace('Núcleo', 'Nucleo')
    hierarchy_df['hierarchy_level'] = hierarchy_df['hierarchy_level'].str.replace('Intermediária', 'Intermediaria')
    hierarchy_df['hierarchy_level'] = hierarchy_df['hierarchy_level'].str.replace('Periférica', 'Periferica')

    # Plot por nivel hierarquico
    for level in ['Nucleo', 'Intermediaria', 'Periferica']:
        data = hierarchy_df[hierarchy_df['hierarchy_level'] == level]
        ax.scatter(
            data['size'],
            data['pagerank_mean'],
            c=COLORS[level],
            s=100,
            alpha=0.7,
            edgecolors='black',
            linewidth=0.5,
            label=level
        )

    # Anotacoes para comunidades interessantes
    for idx, row in hierarchy_df.iterrows():
        if row['dominant_country'] in ['Brazil', 'Germany', 'United States']:
            ax.annotate(
                f"{row['dominant_country']}\n{row['sport']}-{row['sex']}",
                xy=(row['size'], row['pagerank_mean']),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=7,
                alpha=0.7
            )

    ax.set_xlabel('Tamanho da Comunidade (numero de atletas)')
    ax.set_ylabel('PageRank Medio')
    ax.set_title('Tamanho vs Centralidade Estrutural das Comunidades')
    ax.legend(title='Nivel Hierarquico', loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(output_dir / 'fig_size_vs_pagerank.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Salvo: fig_size_vs_pagerank.png")


def fig2_dominance_distribution(medal_df, output_dir):
    """
    Figura 2: Histograma de Indice de Dominancia
    Mostra que 96% sao 'Competitivas'
    """
    print("\nGerando Figura 2: Distribuicao de Dominancia...")

    fig, ax = plt.subplots(figsize=(14, 3.5))

    # Histograma
    n, bins, patches = ax.hist(
        medal_df['dominance_index'],
        bins=20,
        edgecolor='black',
        alpha=0.7,
        color='steelblue'
    )

    # Colorir regioes por perfil
    for i, patch in enumerate(patches):
        bin_center = (bins[i] + bins[i+1]) / 2
        if bin_center < 1.8:
            patch.set_facecolor(COLORS['Participante'])
        elif bin_center < 2.2:
            patch.set_facecolor(COLORS['Competitiva'])
        else:
            patch.set_facecolor(COLORS['Elite'])

    # Linhas verticais nos thresholds
    ax.axvline(x=1.8, color='orange', linestyle='--', linewidth=1.5,
               label='Limite 1.8', alpha=0.8)
    ax.axvline(x=2.2, color='red', linestyle='--', linewidth=1.5,
               label='Limite 2.2', alpha=0.8)

    # Remover tooltips sobrepostos - apenas adicionar info basica no titulo
    total = len(medal_df)
    participante = len(medal_df[medal_df['dominance_index'] < 1.8])
    competitiva = len(medal_df[(medal_df['dominance_index'] >= 1.8) &
                                (medal_df['dominance_index'] < 2.2)])
    elite = len(medal_df[medal_df['dominance_index'] >= 2.2])

    ax.set_xlabel('Indice de Dominancia (escala 3-2-1)', fontsize=10)
    ax.set_ylabel('Frequencia', fontsize=10)
    ax.set_title(f'Distribuicao do Indice de Dominancia: Participante {participante} ({100*participante/total:.1f}%), Competitiva {competitiva} ({100*competitiva/total:.1f}%), Elite {elite} ({100*elite/total:.1f}%)',
                 fontsize=10, pad=10)
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

    plt.tight_layout()
    plt.savefig(output_dir / 'fig_dominance_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Salvo: fig_dominance_distribution.png")


def fig3_segregation_heatmap(inter_df, output_dir):
    """
    Figura 3: Heatmap de Segregacao por Esporte/Sexo
    Matriz 3x2 mostrando razao intra/inter
    """
    print("\nGerando Figura 3: Heatmap de Segregacao...")

    # Calcular segregacao por esporte/sexo
    segregation_data = []
    for sport in ['Swimming', 'Basketball', 'Football']:
        for sex in ['M', 'F']:
            subset = inter_df[(inter_df['sport'] == sport) & (inter_df['sex'] == sex)]
            if len(subset) > 0:
                intra_ratio = subset['intra_ratio'].mean()
                inter_ratio = subset['inter_ratio'].mean()
                ratio = intra_ratio / (inter_ratio + 0.01)  # Evitar divisao por zero
                segregation_data.append({
                    'sport': sport,
                    'sex': sex,
                    'intra_ratio': intra_ratio,
                    'inter_ratio': inter_ratio,
                    'ratio': ratio
                })

    seg_df = pd.DataFrame(segregation_data)

    # Criar matriz pivot
    pivot = seg_df.pivot(index='sport', columns='sex', values='ratio')

    fig, ax = plt.subplots(figsize=(8, 6))

    sns.heatmap(
        pivot,
        annot=True,
        fmt='.2f',
        cmap='RdYlGn_r',  # Vermelho = segregado, Verde = integrado
        center=1.0,
        vmin=0,
        vmax=3,
        cbar_kws={'label': 'Razao Intra/Inter'},
        linewidths=1,
        linecolor='black',
        ax=ax
    )

    ax.set_xlabel('Sexo')
    ax.set_ylabel('Esporte')
    ax.set_title('Indice de Segregacao por Esporte e Sexo\n(valores altos = alta segregacao)')

    plt.tight_layout()
    plt.savefig(output_dir / 'fig_segregation_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Salvo: fig_segregation_heatmap.png")


def fig4_top10_dominance(medal_df, hierarchy_df, output_dir):
    """
    Figura 4: Top 10 Comunidades por Dominancia
    Barplot horizontal
    """
    print("\nGerando Figura 4: Top 10 Dominancia...")

    # Top 10 e merge com hierarchy para obter dominant_country
    top10 = medal_df.nlargest(10, 'dominance_index').copy()
    top10 = top10.merge(
        hierarchy_df[['sport', 'sex', 'community_id', 'dominant_country']],
        on=['sport', 'sex', 'community_id'],
        how='left'
    )
    top10['label'] = top10.apply(
        lambda row: f"{row['sport']}-{row['sex']}-C{row['community_id']}\n({row['dominant_country']})",
        axis=1
    )

    fig, ax = plt.subplots(figsize=(10, 7))

    # Cores por perfil
    colors = [COLORS[p] for p in top10['competitive_profile']]

    bars = ax.barh(range(len(top10)), top10['dominance_index'], color=colors, edgecolor='black')

    ax.set_yticks(range(len(top10)))
    ax.set_yticklabels(top10['label'])
    ax.set_xlabel('Indice de Dominancia (escala 3-2-1)')
    ax.set_title('Top 10 Comunidades por Indice de Dominancia')
    ax.grid(True, alpha=0.3, linestyle='--', axis='x')

    # Legenda de perfil
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS['Elite'], label='Elite'),
        Patch(facecolor=COLORS['Competitiva'], label='Competitiva'),
        Patch(facecolor=COLORS['Participante'], label='Participante')
    ]
    ax.legend(handles=legend_elements, title='Perfil Competitivo', loc='lower right')

    plt.tight_layout()
    plt.savefig(output_dir / 'fig_top10_dominance.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Salvo: fig_top10_dominance.png")


def fig5_top10_rivalries(rivalry_df, output_dir):
    """
    Figura 5: Top 10 Rivalidades Estruturais
    Barplot horizontal
    """
    print("\nGerando Figura 5: Top 10 Rivalidades...")

    # Top 10
    top10 = rivalry_df.nlargest(10, 'num_confronts').copy()
    top10['label'] = top10.apply(
        lambda row: f"{row['sport']}-{row['sex']}\nC{row['community_1']} vs C{row['community_2']}",
        axis=1
    )

    fig, ax = plt.subplots(figsize=(10, 7))

    # Cores por esporte
    colors = [COLORS[sport] for sport in top10['sport']]

    bars = ax.barh(range(len(top10)), top10['num_confronts'], color=colors, edgecolor='black')

    ax.set_yticks(range(len(top10)))
    ax.set_yticklabels(top10['label'])
    ax.set_xlabel('Numero de Confrontos (soma bidirecional)')
    ax.set_title('Top 10 Rivalidades Estruturais Inter-Comunidade')
    ax.grid(True, alpha=0.3, linestyle='--', axis='x')

    # Legenda de esporte
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS['Swimming'], label='Swimming'),
        Patch(facecolor=COLORS['Basketball'], label='Basketball'),
        Patch(facecolor=COLORS['Football'], label='Football')
    ]
    ax.legend(handles=legend_elements, title='Esporte', loc='lower right')

    plt.tight_layout()
    plt.savefig(output_dir / 'fig_top10_rivalries.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Salvo: fig_top10_rivalries.png")


def fig6_community_counts(medal_df, output_dir):
    """
    Figura 6: Numero de Comunidades por Esporte/Sexo
    Barplot agrupado
    """
    print("\nGerando Figura 6: Contagem de Comunidades...")

    # Contar comunidades
    counts = medal_df.groupby(['sport', 'sex']).size().reset_index(name='count')

    fig, ax = plt.subplots(figsize=(10, 6))

    # Barplot agrupado
    sports = counts['sport'].unique()
    x = np.arange(len(sports))
    width = 0.35

    m_counts = [counts[(counts['sport'] == s) & (counts['sex'] == 'M')]['count'].values[0]
                if len(counts[(counts['sport'] == s) & (counts['sex'] == 'M')]) > 0 else 0
                for s in sports]
    f_counts = [counts[(counts['sport'] == s) & (counts['sex'] == 'F')]['count'].values[0]
                if len(counts[(counts['sport'] == s) & (counts['sex'] == 'F')]) > 0 else 0
                for s in sports]

    bars1 = ax.bar(x - width/2, m_counts, width, label='Masculino',
                   color=COLORS['M'], edgecolor='black')
    bars2 = ax.bar(x + width/2, f_counts, width, label='Feminino',
                   color=COLORS['F'], edgecolor='black')

    # Adicionar valores nas barras
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=9)

    ax.set_xlabel('Esporte')
    ax.set_ylabel('Numero de Comunidades Detectadas')
    ax.set_title('Distribuicao de Comunidades por Esporte e Sexo')
    ax.set_xticks(x)
    ax.set_xticklabels(sports)
    ax.legend()
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

    plt.tight_layout()
    plt.savefig(output_dir / 'fig_community_counts.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Salvo: fig_community_counts.png")


def fig7_pagerank_cdf_by_sport(consolidated_df, output_dir):
    """
    Figura 7: CDF de PageRank por Esporte
    Mostra concentracao de centralidade para os 6 esportes analisados
    """
    print("\nGerando Figura 7: CDF de PageRank (6 esportes)...")

    fig, ax = plt.subplots(figsize=(12, 7))

    # Definir paleta de cores para os 6 esportes
    sport_colors = {
        'Swimming': '#1f77b4',      # Azul
        'Athletics': '#2ca02c',     # Verde
        'Basketball': '#ff7f0e',    # Laranja
        'Football': '#d62728',      # Vermelho
        'Judo': '#9467bd',          # Roxo
        'Boxing': '#8c564b'         # Marrom
    }

    # Ordem de plotagem (do menor para maior médio PageRank)
    sports_order = ['Football', 'Basketball', 'Athletics', 'Judo', 'Swimming', 'Boxing']

    for sport in sports_order:
        data = consolidated_df[consolidated_df['sport'] == sport]['original_pagerank'].dropna().sort_values()
        if len(data) > 0:
            y = np.arange(1, len(data) + 1) / len(data)
            ax.plot(data, y, label=sport, linewidth=2.5, color=sport_colors[sport], alpha=0.8)

    ax.set_xlabel('PageRank', fontsize=12)
    ax.set_ylabel('Probabilidade Acumulada', fontsize=12)
    ax.set_xscale('log')
    ax.set_title('CDF da Distribuição de PageRank por Esporte', fontsize=14, weight='bold')
    ax.legend(loc='lower right', fontsize=11, framealpha=0.95)
    ax.grid(True, alpha=0.3, which='both', linestyle='--')

    plt.tight_layout()
    plt.savefig(output_dir / 'fig_pagerank_cdf_by_sport.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Salvo: fig_pagerank_cdf_by_sport.png")


def fig8_dominance_vs_segregation(medal_df, inter_df, output_dir):
    """
    Figura 8: Scatter Dominancia vs Segregacao
    Mostra relacao entre perfil competitivo e isolamento
    """
    print("\nGerando Figura 8: Dominancia vs Segregacao...")

    # Usar segregation_score diretamente do CSV (ja calculado por esporte/sexo)
    seg_by_sport_sex = inter_df[['sport', 'sex', 'segregation_score']].drop_duplicates()

    # Merge medal_df com segregation_score
    merged = medal_df.merge(
        seg_by_sport_sex,
        on=['sport', 'sex'],
        how='left'
    )
    merged['segregation_ratio'] = merged['segregation_score']

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot por esporte
    for sport in ['Swimming', 'Basketball', 'Football']:
        data = merged[merged['sport'] == sport]

        # Separar por sexo (formas diferentes)
        m_data = data[data['sex'] == 'M']
        f_data = data[data['sex'] == 'F']

        if len(m_data) > 0:
            ax.scatter(m_data['dominance_index'], m_data['segregation_ratio'],
                      c=COLORS[sport], marker='o', s=100, alpha=0.7,
                      edgecolors='black', linewidth=0.5, label=f'{sport} M')
        if len(f_data) > 0:
            ax.scatter(f_data['dominance_index'], f_data['segregation_ratio'],
                      c=COLORS[sport], marker='^', s=100, alpha=0.7,
                      edgecolors='black', linewidth=0.5, label=f'{sport} F')

    ax.set_xlabel('Indice de Dominancia (escala 3-2-1)')
    ax.set_ylabel('Razao de Segregacao (Intra/Inter)')
    ax.set_title('Relacao entre Dominancia Competitiva e Segregacao Estrutural')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(output_dir / 'fig_dominance_vs_segregation.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Salvo: fig_dominance_vs_segregation.png")


def fig9_basketball_rivalry_matrix(rivalry_df, output_dir):
    """
    Figura 9: Matriz de Rivalidades Basketball M
    Heatmap assimetrico mostrando confrontos direcionados C0-C1-C2
    """
    print("\nGerando Figura 9: Matriz de Rivalidades Basketball M...")

    # Filtrar Basketball M
    bball_m = rivalry_df[(rivalry_df['sport'] == 'Basketball') & (rivalry_df['sex'] == 'M')].copy()

    if len(bball_m) == 0:
        print("  AVISO: Nenhuma rivalidade encontrada para Basketball M")
        return

    # Obter todas as comunidades unicas
    all_comms = sorted(set(bball_m['community_1'].unique()) | set(bball_m['community_2'].unique()))

    # Criar matriz de confrontos DIRECIONADOS (A→B)
    matrix = pd.DataFrame(0.0, index=all_comms, columns=all_comms)

    for _, row in bball_m.iterrows():
        # Confrontos direcionados: community_1 → community_2
        matrix.loc[row['community_1'], row['community_2']] = row['num_confronts']

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(
        matrix,
        annot=True,
        fmt='.0f',  # Formato de ponto flutuante sem decimais
        cmap='Blues',
        cbar_kws={'label': 'Numero de Confrontos'},
        linewidths=1,
        linecolor='black',
        ax=ax
    )

    ax.set_xlabel('Comunidade B')
    ax.set_ylabel('Comunidade A')
    ax.set_title('Matriz de Rivalidades Estruturais - Basketball Masculino\n(valores = confrontos direcionados A → B)')

    plt.tight_layout()
    plt.savefig(output_dir / 'fig_basketball_rivalry_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Salvo: fig_basketball_rivalry_matrix.png")


def main():
    """Executa geracao de todas as figuras."""
    print("=" * 60)
    print("GERACAO DE FIGURAS PARA MONOGRAFIA")
    print("=" * 60)

    # Setup
    output_dir = setup_output_dir()
    print(f"\nDiretorio de saida: {output_dir}")

    # Carregar dados
    medal_df, inter_df, hierarchy_df, rivalry_df, consolidated_df = load_data()

    # Gerar figuras
    print("\n" + "=" * 60)
    print("GERANDO FIGURAS...")
    print("=" * 60)

    # Figuras que dependem de hierarchy_df
    if hierarchy_df is not None:
        fig1_size_vs_pagerank(hierarchy_df, medal_df, output_dir)
        fig4_top10_dominance(medal_df, hierarchy_df, output_dir)
    else:
        print("\n[AVISO] Pulando figuras 1 e 4 (hierarchy_df ausente)")

    # Figuras que dependem apenas de medal_df
    fig2_dominance_distribution(medal_df, output_dir)
    fig6_community_counts(medal_df, output_dir)

    # Figuras que dependem de inter_df
    if inter_df is not None:
        fig3_segregation_heatmap(inter_df, output_dir)
        fig8_dominance_vs_segregation(medal_df, inter_df, output_dir)
    else:
        print("\n[AVISO] Pulando figuras 3 e 8 (inter_df ausente)")

    # Figuras que dependem de rivalry_df
    if rivalry_df is not None:
        fig5_top10_rivalries(rivalry_df, output_dir)
        fig9_basketball_rivalry_matrix(rivalry_df, output_dir)
    else:
        print("\n[AVISO] Pulando figuras 5 e 9 (rivalry_df ausente)")

    # Figuras que dependem de consolidated_df
    fig7_pagerank_cdf_by_sport(consolidated_df, output_dir)

    print("\n" + "=" * 60)
    print("CONCLUIDO!")
    print("=" * 60)
    print(f"\nTodas as figuras foram salvas em: {output_dir}")
    print("\nPara incluir no LaTeX, use:")
    print("  \\begin{figure}[htbp]")
    print("    \\centering")
    print("    \\includegraphics[width=0.8\\textwidth]{figuras/fig_size_vs_pagerank.png}")
    print("    \\caption{Relacao entre tamanho e centralidade estrutural das comunidades}")
    print("    \\label{fig:size_pagerank}")
    print("  \\end{figure}")


if __name__ == '__main__':
    main()
