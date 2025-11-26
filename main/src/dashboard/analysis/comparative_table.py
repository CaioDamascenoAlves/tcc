"""
Tabela Comparativa: Análise resumida comparando todos os esportes.

Este módulo gera uma tabela comparativa abrangente com todas as métricas
principais, formatação visual profissional e insights automáticos.
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List, Tuple
import sys
from pathlib import Path

# Adicionar projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.metrics import MetricsCalculator
from core.config.styles import UFOP_WINE


# ============================================================================
# DICIONÁRIO DE EXPLICAÇÕES DAS MÉTRICAS
# ============================================================================

METRIC_EXPLANATIONS = {
    'Atletas': {
        'title': 'Número de Atletas',
        'description': 'Total de atletas únicos que competiram no esporte ao longo de todas as edições olímpicas analisadas.',
        'interpretation': 'Indica o tamanho da rede. Redes maiores tendem a ser mais complexas e fragmentadas.'
    },
    'Comunidades': {
        'title': 'Número de Comunidades',
        'description': 'Quantidade de grupos (comunidades) detectados na rede usando o algoritmo Louvain.',
        'interpretation': 'Muitas comunidades indicam fragmentação; poucas sugerem maior coesão global.'
    },
    'Densidade': {
        'title': 'Densidade da Rede (%)',
        'description': 'Proporção de conexões existentes em relação ao total de conexões possíveis na rede.',
        'interpretation': 'Alta densidade = rede altamente conectada; Baixa densidade = rede esparsa com grupos isolados.'
    },
    'PageRank Médio': {
        'title': 'PageRank Médio',
        'description': 'Média da métrica PageRank de todos os atletas. PageRank mede a importância de um nó baseado em suas conexões.',
        'interpretation': 'Valores mais altos indicam distribuição mais uniforme de importância; valores baixos sugerem concentração em poucos atletas.'
    },
    'Concentração Top10': {
        'title': 'Concentração no Top 10%',
        'description': 'Percentual do PageRank total acumulado pelos 10% atletas mais importantes da rede.',
        'interpretation': 'Alta concentração (>50%) = rede hierárquica dominada por poucos; Baixa (<30%) = importância distribuída.'
    },
    'Betweenness Médio': {
        'title': 'Betweenness Médio',
        'description': 'Média da centralidade de intermediação. Mede quantas vezes um nó aparece no caminho mais curto entre outros nós.',
        'interpretation': 'Valores altos indicam presença de atletas-ponte cruciais para conectar diferentes grupos.'
    },
    'Modularidade': {
        'title': 'Modularidade',
        'description': 'Classificação qualitativa da estrutura modular: Alta (comunidades pequenas e bem definidas), Média, ou Baixa (comunidades grandes e difusas).',
        'interpretation': 'Baseada no tamanho médio das comunidades: <50 atletas = Alta, 50-150 = Média, >150 = Baixa.'
    },
    'Segregação': {
        'title': 'Segregação entre Comunidades',
        'description': 'Grau de isolamento entre comunidades. Mede o quão separados estão os diferentes grupos.',
        'interpretation': 'Alta (>0.7) = comunidades isoladas; Média (0.4-0.7) = alguma interação; Baixa (<0.4) = grupos integrados.'
    },
    'Perfil': {
        'title': 'Perfil Competitivo Predominante',
        'description': 'Tipo de perfil mais comum entre os atletas: Especialista (foca em um esporte), Multiesportista, ou Dominante.',
        'interpretation': 'Revela se o esporte atrai atletas especializados ou versáteis que competem em múltiplas modalidades.'
    },
    'Hierarquia': {
        'title': 'Distribuição Hierárquica',
        'description': 'Distribuição das comunidades por nível hierárquico: N=Núcleo (centrais), I=Intermediárias, P=Periféricas.',
        'interpretation': 'Formato N:X I:Y P:Z mostra quantas comunidades estão em cada camada da hierarquia da rede.'
    },
    'Bridges': {
        'title': 'Atletas-Ponte (Número Absoluto)',
        'description': 'Número de atletas que atuam como pontes entre comunidades diferentes.',
        'interpretation': 'Atletas-ponte são cruciais para integração da rede, conectando grupos que de outra forma estariam isolados.'
    },
    'Bridges %': {
        'title': 'Atletas-Ponte (Percentual)',
        'description': 'Percentual de atletas-ponte em relação ao total de atletas do esporte.',
        'interpretation': 'Alta % (>10%) = rede bem integrada; Baixa % (<5%) = comunidades mais isoladas.'
    },
    'Período': {
        'title': 'Período de Análise',
        'description': 'Intervalo temporal coberto pelos dados, do primeiro ao último ano olímpico analisado para o esporte.',
        'interpretation': 'Mostra a amplitude histórica dos dados e permite análises de evolução temporal.'
    },
    'Crescimento': {
        'title': 'Crescimento de Participação (%)',
        'description': 'Variação percentual no número de atletas entre a primeira e última edição olímpica analisada.',
        'interpretation': 'Positivo = esporte em expansão; Negativo = retração; Próximo de 0 = estável.'
    }
}


def create_table_with_tooltips(df_transposed, metric_explanations):
    """
    Cria uma tabela HTML com tooltips integrados em cada célula de métrica.
    
    Args:
        df_transposed: DataFrame transposto com métricas no índice
        metric_explanations: Dicionário com explicações das métricas
    
    Returns:
        String HTML com a tabela
    """
    # CSS para tooltips
    css = """
    <style>
        .tooltip-table {
            width: 100%;
            border-collapse: collapse;
            font-family: "Source Sans Pro", sans-serif;
            font-size: 14px;
        }
        .tooltip-table th, .tooltip-table td {
            border: 1px solid #ddd;
            padding: 12px 8px;
            text-align: left;
        }
        .tooltip-table th {
            background-color: #f0f2f6;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        .tooltip-table tr:hover {
            background-color: #f8f9fa;
        }
        .metric-cell {
            position: relative;
            font-weight: 600;
            cursor: help;
        }
        .metric-cell .tooltip-icon {
            display: inline-block;
            margin-left: 5px;
            color: #666;
            font-size: 12px;
        }
        .metric-cell .tooltip-text {
            visibility: hidden;
            width: 300px;
            background-color: #333;
            color: #fff;
            text-align: left;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1000;
            left: 100%;
            top: 50%;
            transform: translateY(-50%);
            margin-left: 10px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 12px;
            font-weight: normal;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .metric-cell .tooltip-text::after {
            content: "";
            position: absolute;
            top: 50%;
            right: 100%;
            margin-top: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: transparent #333 transparent transparent;
        }
        .metric-cell:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
        }
    </style>
    """
    
    # Construir HTML da tabela
    html = css + '<table class="tooltip-table">'
    
    # Cabeçalho
    html += '<thead><tr><th>Métrica</th>'
    for col in df_transposed.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead>'
    
    # Corpo
    html += '<tbody>'
    for metric in df_transposed.index:
        html += '<tr>'
        
        # Célula da métrica com tooltip
        tooltip_text = metric_explanations.get(metric, {}).get('description', '')
        html += f'<td class="metric-cell">{metric}'
        if tooltip_text:
            html += f' <span class="tooltip-icon"></span>'
            html += f'<span class="tooltip-text">{tooltip_text}</span>'
        html += '</td>'
        
        # Células de dados
        for col in df_transposed.columns:
            value = df_transposed.loc[metric, col]
            html += f'<td>{value}</td>'
        
        html += '</tr>'
    html += '</tbody></table>'
    
    return html


def generate_comparative_metrics(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Gera métricas comparativas para todos os esportes.

    Args:
        data: Dicionário com DataFrames (athletes, hierarchy, etc.)

    Returns:
        DataFrame com métricas comparativas por esporte
    """
    athletes_df = data['athletes']
    communities_df = data.get('communities', data.get('hierarchy', pd.DataFrame()))  # Usar communities, fallback para hierarchy
    medal_profile_df = data['medal_profile']

    # Esportes disponíveis
    sports = sorted(athletes_df['sport'].unique())

    metrics = []

    for sport in sports:
        # Filtrar dados do esporte
        sport_athletes = athletes_df[athletes_df['sport'] == sport]
        sport_communities = communities_df[communities_df['sport'] == sport]
        sport_profile = medal_profile_df[medal_profile_df['sport'] == sport]

        # === ESTRUTURA DA REDE ===
        num_athletes = len(sport_athletes)
        num_communities = len(sport_communities)

        # Densidade (aproximada via degree médio / total possível)
        avg_degree = sport_athletes['original_total_degree'].mean() if 'original_total_degree' in sport_athletes.columns else 0
        max_possible_edges = num_athletes * (num_athletes - 1)
        density = (avg_degree / num_athletes * 100) if num_athletes > 1 else 0

        # === CENTRALIDADE ===
        avg_pagerank = sport_athletes['original_pagerank'].mean() if 'original_pagerank' in sport_athletes.columns else 0

        # Concentração: % do PageRank total nos top 10%
        if 'original_pagerank' in sport_athletes.columns:
            top_10_pct = int(num_athletes * 0.1)
            top_pagerank_sum = sport_athletes.nlargest(top_10_pct, 'original_pagerank')['original_pagerank'].sum()
            total_pagerank_sum = sport_athletes['original_pagerank'].sum()
            concentration = (top_pagerank_sum / total_pagerank_sum * 100) if total_pagerank_sum > 0 else 0
        else:
            concentration = 0

        avg_betweenness = sport_athletes['original_betweenness_centrality'].mean() if 'original_betweenness_centrality' in sport_athletes.columns else 0

        # === COMUNIDADES ===
        # Modularidade estimada pelo tamanho médio das comunidades
        avg_community_size = sport_communities['size'].mean() if 'size' in sport_communities.columns else 0
        modularity_label = (
            "Alta" if avg_community_size < 50 else
            "Média" if avg_community_size < 150 else
            "Baixa"
        )

        # Segregação média
        avg_segregation = sport_communities['segregation_score'].mean() if 'segregation_score' in sport_communities.columns else 0
        segregation_label = (
            "Alta" if avg_segregation > 0.7 else
            "Média" if avg_segregation > 0.4 else
            "Baixa"
        )

        # Perfil predominante
        if len(sport_profile) > 0:
            profile_counts = sport_profile['competitive_profile'].value_counts()
            predominant_profile = profile_counts.idxmax() if len(profile_counts) > 0 else "N/A"
        else:
            predominant_profile = "N/A"

        # === ATLETAS-PONTE ===
        bridges = MetricsCalculator.identify_bridge_athletes(sport_athletes)
        num_bridges = len(bridges)
        pct_bridges = (num_bridges / num_athletes * 100) if num_athletes > 0 else 0

        # === TEMPORAL ===
        if 'year' in sport_athletes.columns:
            years = sorted(sport_athletes['year'].dropna().unique())
            if len(years) > 1:
                year_range = f"{int(years[0])}-{int(years[-1])}"

                # Crescimento
                first_year_athletes = len(sport_athletes[sport_athletes['year'] == years[0]])
                last_year_athletes = len(sport_athletes[sport_athletes['year'] == years[-1]])
                growth = ((last_year_athletes / first_year_athletes) - 1) * 100 if first_year_athletes > 0 else 0
            else:
                year_range = "N/A"
                growth = 0
        else:
            year_range = "N/A"
            growth = 0

        # === HIERARQUIA ===
        if 'hierarchy_level' in sport_communities.columns:
            # Normalizar para remover acentos
            hierarchy_norm = sport_communities.copy()
            hierarchy_norm['hierarchy_level_norm'] = hierarchy_norm['hierarchy_level'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

            nucleo_count = len(hierarchy_norm[hierarchy_norm['hierarchy_level_norm'] == 'Nucleo'])
            intermediaria_count = len(hierarchy_norm[hierarchy_norm['hierarchy_level_norm'] == 'Intermediaria'])
            periferica_count = len(hierarchy_norm[hierarchy_norm['hierarchy_level_norm'] == 'Periferica'])

            hierarchy_distribution = f"N:{nucleo_count} I:{intermediaria_count} P:{periferica_count}"
        else:
            hierarchy_distribution = "N/A"

        # Compilar métricas (mantendo tipos numéricos)
        metrics.append({
            'Esporte': sport,

            # Estrutura
            'Atletas': num_athletes,
            'Comunidades': num_communities,
            'Densidade': round(density, 2),

            # Centralidade
            'PageRank Médio': round(avg_pagerank, 6),
            'Concentração Top10': round(concentration, 1),
            'Betweenness Médio': round(avg_betweenness, 6),

            # Comunidades
            'Modularidade': modularity_label,
            'Segregação': segregation_label,
            'Perfil': predominant_profile,
            'Hierarquia': hierarchy_distribution,

            # Atletas-Ponte
            'Bridges': num_bridges,
            'Bridges %': round(pct_bridges, 1),

            # Temporal
            'Período': year_range,
            'Crescimento': round(growth, 0),
        })

    return pd.DataFrame(metrics)


def style_comparative_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica estilo visual à tabela comparativa.

    Args:
        df: DataFrame com métricas comparativas

    Returns:
        DataFrame estilizado
    """
    def highlight_max_min(col):
        """Destaca valores máximos e mínimos."""
        if col.name in ['Atletas', 'Comunidades', 'Concentração Top10', 'Bridges', 'Bridges %']:
            # Para essas colunas, destacar máximo
            try:
                values = pd.to_numeric(col, errors='coerce')
                is_max = values == values.max()
                return ['background-color: #FFE8ED; font-weight: bold' if v else '' for v in is_max]
            except:
                return ['' for _ in col]
        return ['' for _ in col]

    # Aplicar estilo
    styled = df.style.apply(highlight_max_min, axis=0)

    # Configurar formato
    styled = styled.set_properties(**{
        'text-align': 'center',
        'font-size': '11pt',
        'border': '1px solid #ddd'
    })

    # Estilo do cabeçalho
    styled = styled.set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#8B2635'),
            ('color', 'white'),
            ('font-weight', 'bold'),
            ('text-align', 'center'),
            ('padding', '12px')
        ]},
        {'selector': 'td', 'props': [
            ('padding', '8px')
        ]}
    ])

    return styled


def create_plotly_table(df: pd.DataFrame, title: str, add_info_icon: bool = True, add_highlights: bool = True) -> go.Figure:
    """
    Cria uma tabela Plotly com estilo UFOP padronizado.

    Args:
        df: DataFrame com dados (índice = Esporte, colunas = métricas)
        title: Título da tabela
        add_info_icon: Se True, adiciona  no header para indicar que há explicações
        add_highlights: Se True, destaca valores máximos/mínimos

    Returns:
        Figura Plotly
    """
    # Resetar índice para ter Esporte como coluna
    df_reset = df.reset_index()

    # Adicionar ícone de info nos headers (exceto Esporte)
    if add_info_icon:
        header_values = []
        for col in df_reset.columns:
            if col == 'Esporte':
                header_values.append(col)
            else:
                header_values.append(f"{col} ")
    else:
        header_values = list(df_reset.columns)

    # Preparar valores das células
    cell_values = [df_reset[col].tolist() for col in df_reset.columns]

    # Criar cores de fundo com highlights
    if add_highlights:
        cell_colors = []
        for col in df_reset.columns:
            if col == 'Esporte':
                # Primeira coluna: cores alternadas sem highlights
                colors = ['white' if i % 2 == 0 else '#F5F5F5' for i in range(len(df_reset))]
            else:
                # Verificar se coluna é numérica
                try:
                    numeric_values = pd.to_numeric(df_reset[col], errors='coerce')
                    if not numeric_values.isna().all():
                        max_val = numeric_values.max()
                        min_val = numeric_values.min()

                        colors = []
                        for i, val in enumerate(numeric_values):
                            base_color = 'white' if i % 2 == 0 else '#F5F5F5'

                            if pd.notna(val):
                                # Máximo: verde claro
                                if val == max_val and max_val != min_val:
                                    colors.append('#D4EDDA')  # Verde claro
                                # Mínimo: vermelho claro
                                elif val == min_val and max_val != min_val:
                                    colors.append('#F8D7DA')  # Vermelho claro
                                else:
                                    colors.append(base_color)
                            else:
                                colors.append(base_color)
                    else:
                        # Não numérica: cores alternadas normais
                        colors = ['white' if i % 2 == 0 else '#F5F5F5' for i in range(len(df_reset))]
                except:
                    # Erro ao converter: cores alternadas normais
                    colors = ['white' if i % 2 == 0 else '#F5F5F5' for i in range(len(df_reset))]

            cell_colors.append(colors)
    else:
        # Sem highlights: apenas cores alternadas
        cell_colors = [['white' if i % 2 == 0 else '#F5F5F5' for i in range(len(df_reset))]
                       for _ in df_reset.columns]

    # Criar figura
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=header_values,
            fill_color=UFOP_WINE,
            font=dict(color='white', size=12, family='Arial'),
            align='left',
            height=40
        ),
        cells=dict(
            values=cell_values,
            fill_color=cell_colors,
            font=dict(color='#2A2A2A', size=11, family='Arial'),
            align='left',
            height=35
        )
    )])

    fig.update_layout(
        title=title,
        height=min(600, 100 + len(df_reset) * 35),
        margin=dict(l=0, r=0, t=60, b=0)
    )

    return fig


def render_metric_explanations(metrics: list):
    """
    Renderiza um expander com explicações detalhadas das métricas.

    Args:
        metrics: Lista de nomes de métricas para explicar
    """
    with st.expander(" Sobre as Métricas da Tabela"):
        st.markdown("Clique em cada métrica para ver sua explicação detalhada:")

        for metric in metrics:
            if metric in METRIC_EXPLANATIONS:
                info = METRIC_EXPLANATIONS[metric]
                with st.expander(f"**{info['title']}**"):
                    st.markdown(f"**Descrição:** {info['description']}")
                    st.markdown(f"**Interpretação:** {info['interpretation']}")
                    st.markdown("---")
            else:
                st.caption(f"ℹ {metric}: Métrica calculada a partir dos dados da rede")


def render_comparative_table(data: Dict[str, pd.DataFrame]):
    """
    Renderiza a tabela comparativa no Streamlit com formatação profissional.

    Args:
        data: Dicionário com DataFrames (athletes, hierarchy, etc.)
    """
    st.subheader("Tabela Comparativa dos Esportes")
    st.caption("Resumo executivo de todas as métricas de rede por esporte")

    # Gerar métricas
    df = generate_comparative_metrics(data)

    # Botão de download
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(df)
    st.download_button(
        label=" Download Tabela Comparativa (CSV)",
        data=csv,
        file_name="tabela_comparativa_esportes.csv",
        mime="text/csv",
        help="Exportar tabela comparativa completa em formato CSV"
    )

    if len(df) == 0:
        st.warning("Nenhum dado disponível para comparação.")
        return

    # Tabs para diferentes visualizações
    tab1, tab2, tab3 = st.tabs([
        "Visão Completa",
        "Estrutura & Centralidade",
        "Comunidades & Temporal"
    ])

    with tab1:
        st.markdown("**Todas as Métricas por Esporte**")

        # Explicações das métricas
        all_metrics = [col for col in df.columns if col != 'Esporte']
        render_metric_explanations(all_metrics)

        # Criar tabela com todas as métricas
        df_display = df.set_index('Esporte')
        fig = create_plotly_table(df_display, "Comparação Completa dos Esportes")
        st.plotly_chart(fig, use_container_width=True, key="comparative_table_full")

        # Legenda de cores
        st.markdown("---")
        st.caption("**Legenda:**  Verde = Valor máximo |  Vermelho = Valor mínimo")

        # Insights automáticos
        st.markdown("**Destaques Principais**")

        col1, col2, col3 = st.columns(3)

        with col1:
            max_athletes_sport = df.loc[df['Atletas'].idxmax(), 'Esporte']
            max_athletes = df['Atletas'].max()
            st.metric(
                "Maior Rede",
                max_athletes_sport,
                f"{max_athletes:,} atletas",
                help="Esporte com maior número de atletas na rede"
            )

        with col2:
            max_communities_sport = df.loc[df['Comunidades'].idxmax(), 'Esporte']
            max_communities = df['Comunidades'].max()
            st.metric(
                "Mais Comunidades",
                max_communities_sport,
                f"{max_communities} comunidades",
                help="Esporte com maior fragmentação em grupos distintos"
            )

        with col3:
            max_bridges_sport = df.loc[df['Bridges %'].idxmax(), 'Esporte']
            max_bridges_pct = df['Bridges %'].max()
            st.metric(
                "Mais Bridges",
                max_bridges_sport,
                f"{max_bridges_pct:.1f}%",
                help="Esporte com maior percentual de atletas-ponte conectando comunidades"
            )

    with tab2:
        st.markdown("**Estrutura da Rede & Centralidade**")

        # Explicações das métricas
        structure_metrics = ['Atletas', 'Comunidades', 'Densidade', 'PageRank Médio', 'Concentração Top10', 'Betweenness Médio']
        render_metric_explanations(structure_metrics)

        # Selecionar colunas relevantes
        df_structure = df[['Esporte', 'Atletas', 'Comunidades', 'Densidade',
                           'PageRank Médio', 'Concentração Top10', 'Betweenness Médio']].set_index('Esporte')

        fig = create_plotly_table(df_structure, "Métricas de Estrutura e Centralidade")
        st.plotly_chart(fig, use_container_width=True, key="comparative_table_structure")

        # Insights rápidos
        st.markdown("---")
        st.markdown("**Destaques**")
        col1, col2, col3 = st.columns(3)

        with col1:
            max_density_sport = df.loc[df['Densidade'].idxmax(), 'Esporte']
            max_density = df['Densidade'].max()
            st.metric(
                "Rede Mais Densa",
                max_density_sport,
                f"{max_density:.2f}%",
                help="Maior proporção de conexões existentes vs possíveis"
            )

        with col2:
            max_conc_sport = df.loc[df['Concentração Top10'].idxmax(), 'Esporte']
            max_conc = df['Concentração Top10'].max()
            st.metric(
                "Maior Concentração",
                max_conc_sport,
                f"{max_conc:.1f}%",
                help="Maior concentração de PageRank no top 10%"
            )

        with col3:
            max_bet_sport = df.loc[df['Betweenness Médio'].idxmax(), 'Esporte']
            max_bet = df['Betweenness Médio'].max()
            st.metric(
                "Maior Betweenness",
                max_bet_sport,
                f"{max_bet:.6f}",
                help="Maior potencial de intermediação entre grupos"
            )

    with tab3:
        st.markdown("**Comunidades & Evolução Temporal**")

        # Explicações das métricas
        community_metrics = ['Modularidade', 'Segregação', 'Perfil', 'Hierarquia', 'Bridges', 'Bridges %', 'Período', 'Crescimento']
        render_metric_explanations(community_metrics)

        # Selecionar colunas relevantes
        df_communities = df[['Esporte', 'Modularidade', 'Segregação', 'Perfil',
                            'Hierarquia', 'Bridges', 'Bridges %', 'Período', 'Crescimento']].set_index('Esporte')

        fig = create_plotly_table(df_communities, "Métricas de Comunidades e Evolução")
        st.plotly_chart(fig, use_container_width=True, key="comparative_table_communities")

        # Insights rápidos
        st.markdown("---")
        st.markdown("**Destaques**")
        col1, col2, col3 = st.columns(3)

        with col1:
            max_bridges_pct_sport = df.loc[df['Bridges %'].idxmax(), 'Esporte']
            max_bridges_pct = df['Bridges %'].max()
            st.metric(
                "Mais Bridges",
                max_bridges_pct_sport,
                f"{max_bridges_pct:.1f}%",
                help="Maior percentual de atletas-ponte"
            )

        with col2:
            max_growth_sport = df.loc[df['Crescimento'].idxmax(), 'Esporte']
            max_growth = df['Crescimento'].max()
            st.metric(
                "Maior Crescimento",
                max_growth_sport,
                f"{max_growth:.0f}%",
                help="Maior evolução de participação entre primeira e última edição"
            )

        with col3:
            # Contar perfis predominantes
            profile_counts = df['Perfil'].value_counts()
            most_common_profile = profile_counts.idxmax() if len(profile_counts) > 0 else "N/A"
            st.metric(
                "Perfil Mais Comum",
                most_common_profile,
                f"{profile_counts.max()} esportes",
                help="Perfil competitivo mais frequente entre os esportes"
            )


def export_comparative_table_latex(data: Dict[str, pd.DataFrame], output_path: str):
    """
    Exporta a tabela comparativa para LaTeX.

    Args:
        data: Dicionário com DataFrames
        output_path: Caminho do arquivo .tex de saída
    """
    df = generate_comparative_metrics(data)

    # Selecionar métricas principais para LaTeX (compacto)
    df_latex = df[[
        'Esporte', 'Atletas', 'Comunidades',
        'PageRank Médio', 'Concentração Top10',
        'Modularidade', 'Perfil',
        'Bridges %', 'Crescimento'
    ]]

    # Converter para LaTeX
    latex_str = df_latex.to_latex(
        index=False,
        caption='Comparação das Redes Esportivas Analisadas',
        label='tab:comparative_sports',
        position='htbp',
        column_format='l' + 'c' * (len(df_latex.columns) - 1),
        escape=False
    )

    # Salvar
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_str)

    print(f"Tabela LaTeX exportada: {output_path}")
