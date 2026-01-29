"""
Dashboard Interativo - Análise de Redes Olímpicas.

Dashboard Streamlit para exploração dos resultados de análise de redes.
Usa visualization/ como fonte única de verdade para todos os gráficos.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Adicionar diretórios ao path para imports
project_root = Path(__file__).parent.parent.parent  # main/
src_root = Path(__file__).parent.parent  # main/src/
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_root))

# Usa wrapper que suporta tanto arquivos locais quanto Google Drive
from core.data_loader_wrapper import DataLoader
from core.metrics import MetricsCalculator
from dashboard.visualization import (
    scatter_size_vs_pagerank,
    histogram_dominance,
    heatmap_segregation,
    barplot_top_rivalries,
    cdf_pagerank,
    boxplot_metric_by_category,
    stacked_bar_profile_distribution,
    violin_betweenness_by_sport,
    table_top_athletes,
)
from core.config.constants import SPORTS_LIST
from core.config.paths import PATHS
from dashboard.analysis import render_comparative_table


# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Análise de Redes Olímpicas",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Dashboard de Análise de Redes Complexas aplicada ao Esporte Olímpico"
    }
)

# Aplicar tema UFOP via CSS customizado
st.markdown("""
<style>
    /* Cor primária UFOP (Vinho) para elementos interativos */
    .stButton>button {
        background-color: #8B2635 !important;
        color: white !important;
    }
    .stButton>button:hover {
        background-color: #6B1D2A !important;
    }

    /* Tabs selecionadas */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        border-bottom-color: #8B2635 !important;
        color: #8B2635 !important;
    }

    /* Sliders e controles */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: #8B2635 !important;
    }

    /* Multiselect tags */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #8B2635 !important;
    }

    /* Links */
    a {
        color: #8B2635 !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# CACHE DE DADOS
# ============================================================================

@st.cache_data
def load_data():
    """Carrega todos os dados com cache."""
    loader = DataLoader()
    return loader.load_all()


# ============================================================================
# SIDEBAR - FILTROS GLOBAIS
# ============================================================================

def render_sidebar(data):
    """Renderiza sidebar com filtros globais."""
    st.sidebar.title("Análise de Redes Olímpicas")
    st.sidebar.caption("Sistema de análise de redes complexas")
    st.sidebar.markdown("---")

    # Guia de Interpretação
    with st.sidebar.expander(" Guia de Uso", expanded=False):
        st.markdown("""
        ### Como usar este dashboard

        **1. Filtros (abaixo):**
        - Selecione esportes, sexo e período temporal
        - Filtros aplicam-se a todas as abas
        - Use Ctrl+Click para seleção múltipla

        **2. Navegação:**
        - **Visão Geral:** Estatísticas principais e distribuições
        - **Comunidades:** Estrutura de grupos competitivos
        - **Atletas-Ponte:** Conectores entre comunidades
        - **Rivalidades:** Confrontos entre grupos
        - **Rankings:** Top atletas por métrica
        - **Evolução Temporal:** Mudanças ao longo do tempo

        **3. Convenções Visuais:**
        - **Cor Vinho (#8B2635):** Marca UFOP, valores importantes
        - **Tabelas:** Header vinho, células alternadas
        - **Gráficos interativos:** Hover para detalhes

        **4. Métricas Principais:**
        - **PageRank:** Importância estrutural (vitórias sobre fortes)
        - **Betweenness:** Atletas-ponte entre grupos
        - **Comunidades:** Grupos detectados por Louvain

        **Dica:** Clique nos ícones  e expanders  para explicações detalhadas!
        """)

    st.sidebar.markdown("---")

    st.sidebar.subheader("Filtros Globais")
    st.sidebar.caption("Selecione os dados para análise")

    # Filtro: Esporte
    sports_available = sorted(data['athletes']['sport'].unique())
    selected_sports = st.sidebar.multiselect(
        "Esportes",
        options=sports_available,
        default=sports_available,
        help="Selecione um ou mais esportes para análise"
    )

    # Filtro: Sexo
    sex_options = ['M', 'F']
    selected_sex = st.sidebar.multiselect(
        "Sexo",
        options=sex_options,
        default=sex_options,
        help="Masculino (M) ou Feminino (F)"
    )

    # Filtro: Período Temporal
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtro Temporal")

    # Extrair anos disponíveis
    if 'games' in data['athletes'].columns:
        data['athletes']['year'] = data['athletes']['games'].apply(extract_year_from_games)
        years_available = sorted(data['athletes']['year'].dropna().unique())

        if len(years_available) > 0:
            min_year = int(years_available[0])
            max_year = int(years_available[-1])

            selected_year_range = st.sidebar.slider(
                "Período (anos)",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
                step=4,  # Olimpíadas a cada 4 anos
                help="Selecione o intervalo de anos para análise"
            )
        else:
            selected_year_range = None
    else:
        selected_year_range = None

    st.sidebar.markdown("---")

    # Informações do dataset
    st.sidebar.subheader("Estatísticas do Dataset")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Atletas", f"{len(data['athletes']):,}")
        st.metric("Esportes", len(sports_available))
    with col2:
        num_communities = len(data.get('communities', [])) if 'communities' in data and data['communities'] is not None else 0
        st.metric("Comunidades", f"{num_communities:,}")
        st.metric("Rivalidades", f"{len(data['rivalries']):,}")

    st.sidebar.markdown("---")

    # Download de Dados
    st.sidebar.subheader("Exportar Dados")

    # Botão de download CSV
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv_data = convert_df_to_csv(data['athletes'])

    st.sidebar.download_button(
        label=" Download CSV (Atletas)",
        data=csv_data,
        file_name="olympic_athletes_network.csv",
        mime="text/csv",
        help="Download dos dados de atletas filtrados no formato CSV"
    )

    st.sidebar.markdown("---")

    # Rodapé
    st.sidebar.caption("Dashboard v1.0 | TCC 2024-2026")
    st.sidebar.caption("Análise de Redes Complexas")

    # Dica sobre tema
    with st.sidebar.expander(" Configuração de Tema"):
        st.markdown("""
        **Tema recomendado:** Light

        Se os textos estiverem ilegíveis:
        1. Clique no menu ⋮ (canto superior direito)
        2. Settings > Theme
        3. Selecione: **Light**

        Isso garante melhor contraste com as cores UFOP.
        """)

    return {
        'sports': selected_sports,
        'sex': selected_sex,
        'year_range': selected_year_range,
    }


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def extract_year_from_games(games_str):
    """Extrai ano da coluna 'games' (ex: '1920 Summer' -> 1920)."""
    if pd.isna(games_str):
        return None
    return int(str(games_str).split()[0])


# ============================================================================
# FUNÇÕES DE PADRONIZAÇÃO VISUAL
# ============================================================================

def render_section_title(title: str, subtitle: str = None):
    """
    Renderiza título de seção padronizado.

    Args:
        title: Título principal
        subtitle: Subtítulo opcional (descrição curta)
    """
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)
    st.markdown("---")


def render_subsection(title: str, caption: str = None):
    """
    Renderiza subtítulo padronizado.

    Args:
        title: Título da subseção
        caption: Caption opcional (descrição curta)
    """
    st.markdown(f"**{title}**")
    if caption:
        st.caption(caption)


# ============================================================================
# FUNÇÕES DE FILTRO
# ============================================================================

def filter_data(data, filters):
    """Aplica filtros aos dados."""
    with st.spinner("Aplicando filtros..."):
        filtered = {}

        # Atletas
        df = data['athletes'].copy()

        # Garantir que coluna year existe
        if 'year' not in df.columns and 'games' in df.columns:
            df['year'] = df['games'].apply(extract_year_from_games)

        if filters['sports']:
            df = df[df['sport'].isin(filters['sports'])]
        if filters['sex']:
            df = df[df['sex'].isin(filters['sex'])]
        if filters['year_range'] and 'year' in df.columns:
            df = df[(df['year'] >= filters['year_range'][0]) & (df['year'] <= filters['year_range'][1])]

        filtered['athletes'] = df

        # Medal profile (com fallback se não existir)
        if 'medal_profile' in data:
            df = data['medal_profile'].copy()
            if filters['sports']:
                df = df[df['sport'].isin(filters['sports'])]
            if filters['sex']:
                df = df[df['sex'].isin(filters['sex'])]
            filtered['medal_profile'] = df
        else:
            filtered['medal_profile'] = pd.DataFrame()

        # Communities
        if 'communities' in data:
            df = data['communities'].copy()
            if filters['sports']:
                df = df[df['sport'].isin(filters['sports'])]
            if filters['sex']:
                df = df[df['sex'].isin(filters['sex'])]
            filtered['communities'] = df
        else:
            filtered['communities'] = pd.DataFrame()

        # Hierarchy
        df = data['hierarchy'].copy()
        if filters['sports']:
            df = df[df['sport'].isin(filters['sports'])]
        if filters['sex']:
            df = df[df['sex'].isin(filters['sex'])]
        filtered['hierarchy'] = df

        # Connectivity
        df = data['connectivity'].copy()
        if filters['sports']:
            df = df[df['sport'].isin(filters['sports'])]
        if filters['sex']:
            df = df[df['sex'].isin(filters['sex'])]
        filtered['connectivity'] = df

        # Rivalries
        df = data['rivalries'].copy()
        if filters['sports']:
            df = df[df['sport'].isin(filters['sports'])]
        if filters['sex']:
            df = df[df['sex'].isin(filters['sex'])]
        filtered['rivalries'] = df

    return filtered


# ============================================================================
# TAB 1: VISÃO GERAL
# ============================================================================

def render_overview_tab(data):
    """Tab: Visão Geral."""
    st.header("Visão Geral")
    st.caption("Estatísticas gerais e distribuições fundamentais das redes olímpicas")
    st.markdown("---")

    with st.expander("Sobre esta Análise"):
        st.markdown("""
        Esta seção apresenta uma **visão panorâmica** da rede olímpica construída a partir de relações competitivas entre atletas medalhistas.

        **Métricas Principais:**
        - **PageRank**: Mede a importância de cada atleta baseado em suas conexões e qualidade dos oponentes derrotados
        - **Betweenness Centrality**: Identifica atletas que servem como pontes entre diferentes grupos ou eras

        **Distribuições Estatísticas:**
        - **CDF (Cumulative Distribution Function)**: Mostra como a importância está distribuída - poucos atletas muito importantes vs muitos com importância baixa
        - **Violin Plot**: Revela padrões de distribuição de betweenness por esporte, incluindo valores extremos e mediana
        """)

    # Métricas resumidas
    render_subsection("Indicadores Principais")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Atletas Analisados",
            f"{len(data['athletes']):,}",
            help="Total de atletas medalhistas na seleção atual"
        )

    with col2:
        num_communities = len(data['communities']) if 'communities' in data and data['communities'] is not None else 0
        st.metric(
            "Comunidades Detectadas",
            f"{num_communities:,}",
            help="Comunidades distintas identificadas por Louvain (considerando esporte e gênero)"
        )

    with col3:
        bridges = MetricsCalculator.identify_bridge_athletes(data['athletes'])
        st.metric(
            "Atletas-Ponte",
            f"{len(bridges):,}",
            help="Atletas com alta betweenness centrality (top 10%)"
        )

    with col4:
        avg_pr = data['athletes']['original_pagerank'].mean()
        st.metric(
            "PageRank Médio",
            f"{avg_pr:.6f}",
            help="PageRank médio dos atletas"
        )

    st.markdown("---")

    # Tabela Comparativa
    with st.spinner("Gerando tabela comparativa..."):
        render_comparative_table(data)

    st.markdown("---")

    # Visualizações principais
    render_section_title("Distribuições Estatísticas", "Análise da distribuição de importância e intermediação na rede")

    col1, col2 = st.columns(2)

    with col1:
        with st.container():
            render_subsection("PageRank - Função de Distribuição Acumulada", "CDF mostrando a distribuição de importância dos atletas na rede")
            fig = cdf_pagerank(data['athletes'], interactive=True)
            st.plotly_chart(fig, use_container_width=True, key="overview_cdf_pagerank")

    with col2:
        with st.container():
            render_subsection("Betweenness Centrality por Esporte", "Distribuição dos atletas-ponte (intermediadores) em cada esporte")
            fig = violin_betweenness_by_sport(data['athletes'], interactive=True)
            st.plotly_chart(fig, use_container_width=True, key="overview_violin_betweenness")


# ============================================================================
# TAB 2: COMUNIDADES
# ============================================================================

def render_communities_tab(data):
    """Tab: Análise de Comunidades."""
    st.header("Análise de Comunidades")
    st.caption("Estrutura, hierarquia e características das comunidades detectadas pelo algoritmo de Louvain")
    st.markdown("---")

    with st.expander("Sobre Detecção de Comunidades"):
        st.markdown("""
        As **comunidades** são grupos de atletas densamente conectados entre si, identificados automaticamente pelo **algoritmo de Louvain**.

        **Hierarquia Estrutural:**
        - **Núcleo**: Comunidades com alto PageRank médio - grupos de atletas de elite altamente conectados
        - **Intermediária**: Comunidades com centralidade moderada - grupos competitivos estáveis
        - **Periférica**: Comunidades com baixo PageRank médio - grupos menos centrais ou emergentes

        **Distribuição de Medalhas:**
        - Análise da distribuição de medalhas (ouro, prata, bronze) por comunidade
        - Distribuição aproximadamente equilibrada entre os três tipos
        - Média geral: 31.8% ouro, 33.4% prata, 34.8% bronze

        **Segregação Estrutural:**
        Mede o grau de isolamento entre comunidades. Alta segregação indica pouca interação entre grupos,
        baixa segregação indica confrontos frequentes entre comunidades diferentes.
        """)

    # Subtabs
    subtab1, subtab2, subtab3, subtab4 = st.tabs(["Hierarquia", "Distribuição de Medalhas", "Segregação", "Diversidade Temporal"])

    with subtab1:
        render_subsection("Hierarquia de Comunidades", "Análise da hierarquia estrutural baseada em PageRank médio")
        st.markdown("""
        Comunidades de **Núcleo** têm alta centralidade, **Periféricas** têm baixa.
        """)

        fig = scatter_size_vs_pagerank(data['hierarchy'], interactive=True)
        st.plotly_chart(fig, use_container_width=True, key="communities_hierarchy_scatter")

        st.markdown("---")

        # Estatísticas por nível
        render_subsection("Estatísticas por Nível Hierárquico")

        st.info("""
        **Classificação hierárquica** baseada em centralidade estrutural (PageRank):
        - **Núcleo (20%)**: Comunidades com alta centralidade estrutural (PageRank médio ~0.004)
        - **Intermediária (42%)**: Centralidade moderada (PageRank médio ~0.002)
        - **Periférica (38%)**: Menor centralidade estrutural (PageRank médio ~0.001)

        A centralidade estrutural não equivale necessariamente a volume de medalhas.
        """)

        col1, col2, col3 = st.columns(3)

        # Usar hierarchy que já tem hierarchy_level calculado
        if 'hierarchy' not in data or data['hierarchy'] is None or len(data['hierarchy']) == 0:
            st.warning("Dados de hierarquia não disponíveis. Execute a análise completa para gerar esses dados.")
            return

        hierarchy_df = data['hierarchy'].copy()

        # Contagem por nível
        level_counts = hierarchy_df['hierarchy_level'].value_counts()
        level_stats = hierarchy_df.groupby('hierarchy_level')['pagerank_mean'].mean()

        # Mapa de labels
        label_map = {
            'Núcleo': 'Núcleo',
            'Intermediária': 'Intermediária',
            'Periférica': 'Periférica'
        }

        for i, level in enumerate(['Núcleo', 'Intermediária', 'Periférica']):
            count = level_counts.get(level, 0)
            pr_mean = level_stats.get(level, 0)

            with [col1, col2, col3][i]:
                st.metric(
                    label_map[level],
                    f"{count} comunidades",
                    help=f"PageRank médio: {pr_mean:.6f}" if count > 0 else "Sem dados"
                )

    with subtab2:
        render_subsection("Distribuição de Medalhas por Comunidade", "Estatísticas descritivas da distribuição de medalhas")
        st.markdown("""
        **Padrão predominantemente equilibrado**: Distribuição aproximadamente uniforme caracteriza
        competição sistemática sem monopolização absoluta de posições superiores no pódio.
        """)

        # Verificar se temos dados de communities com medalhas
        if 'communities' in data and data['communities'] is not None and len(data['communities']) > 0:
            medal_data = data['communities']

            # Verificar se as colunas de medalhas existem
            if all(col in medal_data.columns for col in ['gold_count', 'silver_count', 'bronze_count', 'total_medals']):
                # Calcular percentuais
                medal_data = medal_data.copy()
                medal_data['gold_pct'] = (medal_data['gold_count'] / medal_data['total_medals'] * 100).fillna(0)
                medal_data['silver_pct'] = (medal_data['silver_count'] / medal_data['total_medals'] * 100).fillna(0)
                medal_data['bronze_pct'] = (medal_data['bronze_count'] / medal_data['total_medals'] * 100).fillna(0)

                # Estatísticas descritivas
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Média Ouro (%)",
                        f"{medal_data['gold_pct'].mean():.1f}%",
                        help="Percentual médio de medalhas de ouro nas comunidades"
                    )
                with col2:
                    st.metric(
                        "Média Prata (%)",
                        f"{medal_data['silver_pct'].mean():.1f}%",
                        help="Percentual médio de medalhas de prata nas comunidades"
                    )
                with col3:
                    st.metric(
                        "Média Bronze (%)",
                        f"{medal_data['bronze_pct'].mean():.1f}%",
                        help="Percentual médio de medalhas de bronze nas comunidades"
                    )

                st.markdown("---")

                # Visualização da distribuição - usar gráfico simples de barras empilhadas
                import plotly.graph_objects as go

                # Agrupar por esporte
                sport_medals = medal_data.groupby('sport')[['gold_pct', 'silver_pct', 'bronze_pct']].mean()

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Ouro',
                    x=sport_medals.index,
                    y=sport_medals['gold_pct'],
                    marker_color='gold'
                ))
                fig.add_trace(go.Bar(
                    name='Prata',
                    x=sport_medals.index,
                    y=sport_medals['silver_pct'],
                    marker_color='silver'
                ))
                fig.add_trace(go.Bar(
                    name='Bronze',
                    x=sport_medals.index,
                    y=sport_medals['bronze_pct'],
                    marker_color='#CD7F32'
                ))

                fig.update_layout(
                    barmode='stack',
                    title='Distribuição Média de Medalhas por Esporte',
                    xaxis_title='Esporte',
                    yaxis_title='Percentual (%)',
                    yaxis_range=[0, 100],
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True, key="communities_medals_stacked")
            else:
                st.info("Colunas de medalhas não encontradas nos dados de comunidades.")
        else:
            st.info("Dados de distribuição de medalhas não disponíveis para visualização.")

    with subtab3:
        render_subsection("Segregação Estrutural", "Análise da conectividade intra vs inter-comunidade")
        st.markdown("""
        **Alta segregação**: Comunidades isoladas | **Baixa segregação**: Bem conectadas.
        """)

        fig = heatmap_segregation(data['connectivity'], interactive=True)
        st.plotly_chart(fig, use_container_width=True, key="communities_segregation_heatmap")

        st.markdown("---")

        # Tabela de conectividade
        render_subsection("Tabela de Conectividade")
        st.dataframe(
            data['connectivity'][['sport', 'sex', 'intra_edges', 'inter_edges', 'segregation_score']],
            use_container_width=True
        )

    with subtab4:
        render_subsection("Diversidade Temporal (Entropia de Shannon)", "Análise da distribuição temporal de atletas por comunidade")
        st.markdown("""
        **Alta entropia**: Alta diversidade temporal - atletas distribuídos em múltiplas eras
        **Baixa entropia**: Baixa diversidade temporal - atletas concentrados em poucas eras
        """)

        # Verificar se temos dados de community_profiles com entropia
        if 'communities' in data and data['communities'] is not None and len(data['communities']) > 0:
            profiles_df = data['communities']

            # Estatísticas por esporte
            st.markdown("### Entropia Temporal por Esporte")

            entropy_stats = profiles_df.groupby('sport')['temporal_entropy'].agg(['mean', 'min', 'max', 'std']).reset_index()

            col1, col2, col3 = st.columns(3)

            sports = ['Swimming', 'Basketball', 'Football']
            sport_labels = {'Swimming': 'Swimming', 'Basketball': 'Basketball', 'Football': 'Football'}

            for idx, sport in enumerate(sports):
                sport_data = entropy_stats[entropy_stats['sport'] == sport]
                if len(sport_data) > 0:
                    with [col1, col2, col3][idx]:
                        st.metric(
                            sport_labels[sport],
                            f"{sport_data['mean'].values[0]:.2f}",
                            help=f"Entropia temporal média. Min: {sport_data['min'].values[0]:.2f}, Max: {sport_data['max'].values[0]:.2f}"
                        )

            st.markdown("---")

            # Interpretação
            st.info("""
            **Interpretação dos valores (da monografia):**
            - **Swimming (1.60)**: Diversidade temporal moderada - comunidades especializadas por era
            - **Basketball (2.46)**: Alta diversidade temporal - comunidades multi-era
            - **Football (2.53)**: Alta diversidade temporal - comunidades multi-era

            Esportes coletivos apresentam comunidades que agregam atletas de múltiplas décadas devido
            à natureza densamente conectada destas redes.
            """)

            st.markdown("---")

            # Gráfico de distribuição
            import plotly.graph_objects as go

            fig = go.Figure()

            for sport in sports:
                sport_df = profiles_df[profiles_df['sport'] == sport]
                fig.add_trace(go.Box(
                    y=sport_df['temporal_entropy'],
                    name=sport_labels[sport],
                    boxmean='sd'
                ))

            fig.update_layout(
                title='Distribuição de Entropia Temporal por Esporte',
                yaxis_title='Entropia de Shannon (Temporal)',
                xaxis_title='Esporte',
                height=400,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True, key="entropy_boxplot")

            st.markdown("---")

            # Tabela detalhada
            render_subsection("Entropia por Comunidade")

            display_cols = ['sport', 'sex', 'community_id', 'size', 'temporal_entropy', 'geographic_entropy', 'year_start', 'year_end']
            available_cols = [col for col in display_cols if col in profiles_df.columns]

            st.dataframe(
                profiles_df[available_cols].sort_values('temporal_entropy', ascending=False),
                use_container_width=True,
                height=400
            )
        else:
            st.warning("Dados de entropia temporal não disponíveis. Execute a análise completa para gerar esses dados.")


# ============================================================================
# TAB 3: ATLETAS-PONTE
# ============================================================================

def render_bridges_tab(data):
    """Tab: Atletas-Ponte."""
    st.header("Atletas-Ponte")
    st.caption("Atletas que ocupam posições estruturais críticas, conectando diferentes comunidades ou eras competitivas")
    st.markdown("---")

    with st.expander("Sobre Atletas-Ponte"):
        st.markdown("""
        **Atletas-ponte** são identificados por alta **betweenness centrality** (top 10% da distribuição).
        Eles atuam como intermediadores cruciais na rede, conectando grupos que de outra forma seriam menos conectados.
        """)

    # Identificar bridges
    bridges = MetricsCalculator.identify_bridge_athletes(data['athletes'])

    # Métricas em destaque
    render_subsection("Indicadores")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total de Bridges",
            f"{len(bridges):,}",
            help="Número de atletas identificados como pontes estruturais"
        )

    with col2:
        pct = (len(bridges) / len(data['athletes'])) * 100
        st.metric(
            "Percentual",
            f"{pct:.1f}%",
            help="Percentual em relação ao total de atletas"
        )

    with col3:
        max_bet = bridges['original_betweenness_centrality'].max()
        st.metric(
            "Betweenness Máxima",
            f"{max_bet:.4f}",
            help="Maior valor de betweenness centrality encontrado"
        )

    st.markdown("---")

    # Visualizações
    render_section_title("Análises Visuais", "Distribuição e ranking dos atletas-ponte por esporte")

    col1, col2 = st.columns(2)

    with col1:
        with st.container():
            render_subsection("Distribuição por Esporte", "Violin plot mostrando a variação de betweenness em cada esporte")
            fig = violin_betweenness_by_sport(data['athletes'], interactive=True)
            st.plotly_chart(fig, use_container_width=True, key="bridges_violin_betweenness")

    with col2:
        with st.container():
            render_subsection("Top 20 Atletas-Ponte", "Ranking dos atletas com maior betweenness centrality")
            fig = table_top_athletes(
                bridges,
                metric_column='original_betweenness_centrality',
                top_n=20,
                interactive=True
            )
            st.plotly_chart(fig, use_container_width=True, key="bridges_table_top20")

    st.markdown("---")

    # Tabela detalhada
    render_subsection("Atletas-Ponte por Esporte")

    for sport in sorted(data['athletes']['sport'].unique()):
        sport_bridges = bridges[bridges['sport'] == sport].nlargest(5, 'original_betweenness_centrality')

        if len(sport_bridges) > 0:
            with st.expander(f"{sport} ({len(sport_bridges[sport_bridges['sport'] == sport])} bridges)"):
                st.dataframe(
                    sport_bridges[['name', 'noc', 'sex', 'original_betweenness_centrality', 'original_pagerank']],
                    use_container_width=True
                )


# ============================================================================
# TAB 4: RIVALIDADES
# ============================================================================

def render_rivalries_tab(data):
    """Tab: Rivalidades Estruturais."""
    st.header("Rivalidades Estruturais")
    st.caption("Pares de comunidades com padrões intensos de confrontos competitivos diretos")
    st.markdown("---")

    with st.expander("Sobre Rivalidades Estruturais"):
        st.markdown("""
        **Rivalidades estruturais** são identificadas pelo número de arestas (confrontos) entre pares de comunidades.
        Quanto maior o número de confrontos, mais intensa a rivalidade estrutural entre os grupos.

        **Tipos de Rede:**
        - **Individual:** Rivalidades em eventos individuais (ex: natação 100m livre)
        - **Team:** Rivalidades em eventos de equipe (ex: revezamento 4x100m)
        - **All:** Todas as rivalidades combinadas (individual + team)
        """)

    # Filtro de tipo de rede
    render_subsection("Filtros")
    event_type = st.radio(
        "Tipo de Rede",
        options=["all", "individual", "team"],
        format_func=lambda x: {"all": "Todas (Individual + Team)", "individual": "Individual", "team": "Team"}[x],
        horizontal=True,
        help="Filtra rivalidades por tipo de evento"
    )

    # Carregar dados de rivalries específicos para o tipo de rede
    loader = DataLoader()
    rivalries_filtered = loader.load_rivalry_pairs(event_type=event_type)

    st.markdown("---")

    # Métricas
    render_subsection("Indicadores")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Rivalidades Identificadas", f"{len(rivalries_filtered):,}")

    with col2:
        max_confronts = rivalries_filtered['num_confronts'].max()
        st.metric("Máximo de Confrontos", f"{max_confronts:,}")

    with col3:
        avg_confronts = rivalries_filtered['num_confronts'].mean()
        st.metric("Média de Confrontos", f"{avg_confronts:.1f}")

    st.markdown("---")

    # Controle: Top N
    render_subsection("Top Rivalidades")
    top_n = st.slider("Número de rivalidades a exibir", min_value=5, max_value=30, value=10, step=5)

    # Visualização
    fig = barplot_top_rivalries(rivalries_filtered, top_n=top_n, interactive=True)
    st.plotly_chart(fig, use_container_width=True, key="rivalries_bar_top_n")

    st.markdown("---")

    # Heatmap de segregação
    render_section_title("Mapa de Segregação", "Heatmap mostrando a segregação entre comunidades")
    fig = heatmap_segregation(data['connectivity'], interactive=True)
    st.plotly_chart(fig, use_container_width=True, key="rivalries_segregation_heatmap")

    st.markdown("---")

    # Tabela completa
    render_subsection("Tabela Completa de Rivalidades")
    st.dataframe(
        rivalries_filtered.sort_values('num_confronts', ascending=False),
        use_container_width=True
    )


# ============================================================================
# TAB 5: RANKINGS
# ============================================================================

def render_rankings_tab(data):
    """Tab: Rankings de Atletas."""
    st.header("Rankings de Atletas")
    st.caption("Rankings customizáveis baseados em diferentes métricas de centralidade de rede")
    st.markdown("---")

    with st.expander("Sobre as Métricas de Centralidade"):
        st.markdown("""
        Cada métrica captura um aspecto diferente da importância de um atleta na rede competitiva:

        **PageRank:**
        - Baseado no algoritmo do Google
        - Considera não apenas quantas vitórias, mas a **qualidade** dos oponentes derrotados
        - Um atleta ganha mais pontos ao vencer outros atletas importantes

        **Betweenness Centrality:**
        - Mede o quanto um atleta atua como **ponte** entre diferentes grupos
        - Atletas com alto betweenness conectam comunidades ou eras distintas
        - Importante para entender fluxo de informação e influência na rede

        **Closeness Centrality:**
        - Mede a **proximidade média** de um atleta a todos os outros
        - Alto closeness indica capacidade de alcançar rapidamente outros atletas via caminhos curtos
        - Reflete posição central e eficiência de conexão

        **Degree Centrality:**
        - Simplesmente conta o **número de conexões diretas** (vitórias/derrotas)
        - Métrica mais simples, mas ainda útil para entender atividade competitiva
        - Alto degree indica muitos confrontos diretos com diferentes oponentes
        """)

    # Controles
    col1, col2 = st.columns([2, 1])

    with col1:
        # Seleção de métrica
        metric_options = {
            'PageRank': 'original_pagerank',
            'Betweenness Centrality': 'original_betweenness_centrality',
            'Closeness Centrality': 'original_closeness_centrality',
            'Degree Centrality': 'original_degree_centrality',
        }

        selected_metric_name = st.selectbox(
            "Métrica de Ranking",
            options=list(metric_options.keys()),
            help="Selecione a métrica para ordenar os atletas"
        )

        selected_metric = metric_options[selected_metric_name]

    with col2:
        # Top N
        top_n = st.slider("Número de atletas", min_value=10, max_value=50, value=20, step=10)

    st.markdown("---")

    # Tabela
    render_section_title(f"Top {top_n} Atletas", f"Ranking baseado em {selected_metric_name}")
    fig = table_top_athletes(
        data['athletes'],
        metric_column=selected_metric,
        top_n=top_n,
        interactive=True
    )
    st.plotly_chart(fig, use_container_width=True, key="rankings_table_top_n")

    st.markdown("---")

    # Distribuição
    render_section_title(f"Distribuição de {selected_metric_name}", "Análise estatística da métrica selecionada")

    col1, col2 = st.columns(2)

    with col1:
        fig = cdf_pagerank(data['athletes'], interactive=True) if selected_metric == 'original_pagerank' else None
        if fig:
            st.plotly_chart(fig, use_container_width=True, key="rankings_cdf_distribution")

    with col2:
        fig = boxplot_metric_by_category(
            data['athletes'],
            metric_column=selected_metric,
            category_column='sport',
            interactive=True,
            title=f'{selected_metric_name} por Esporte'
        )
        st.plotly_chart(fig, use_container_width=True, key="rankings_boxplot_by_sport")


# ============================================================================
# TAB 6: REDE INTERATIVA
# ============================================================================

def render_network_tab(data):
    """
    Tab: Visualização Interativa da Rede (Versão Melhorada).

    Args:
        data: Dicionário com dados carregados (compatibilidade, não usado diretamente)
    """
    from dashboard.components import render_cosmograph
    import json

    st.header("Redes Interativas")
    st.caption("Explore as redes competitivas olímpicas de forma interativa")
    st.markdown("---")

    # ========================================================================
    # SELETOR DE REDE ESPECÍFICA
    # ========================================================================

    st.subheader("1. Selecione a Rede")

    # Definir as 16 redes disponíveis
    networks = [
        {"id": "swimming_M_individual", "label": "Natação Masculina - Individual", "sport": "Swimming", "sex": "M", "event_type": "individual"},
        {"id": "swimming_M_team", "label": "Natação Masculina - Equipe (Revezamentos)", "sport": "Swimming", "sex": "M", "event_type": "team"},
        {"id": "swimming_F_individual", "label": "Natação Feminina - Individual", "sport": "Swimming", "sex": "F", "event_type": "individual"},
        {"id": "swimming_F_team", "label": "Natação Feminina - Equipe (Revezamentos)", "sport": "Swimming", "sex": "F", "event_type": "team"},
        {"id": "football_M_team", "label": "Futebol Masculino", "sport": "Football", "sex": "M", "event_type": "team"},
        {"id": "football_F_team", "label": "Futebol Feminino", "sport": "Football", "sex": "F", "event_type": "team"},
        {"id": "basketball_M_team", "label": "Basquetebol Masculino", "sport": "Basketball", "sex": "M", "event_type": "team"},
        {"id": "basketball_F_team", "label": "Basquetebol Feminino", "sport": "Basketball", "sex": "F", "event_type": "team"},
        {"id": "athletics_M_individual", "label": "Atletismo Masculino - Individual", "sport": "Athletics", "sex": "M", "event_type": "individual"},
        {"id": "athletics_M_team", "label": "Atletismo Masculino - Equipe (Revezamentos)", "sport": "Athletics", "sex": "M", "event_type": "team"},
        {"id": "athletics_F_individual", "label": "Atletismo Feminino - Individual", "sport": "Athletics", "sex": "F", "event_type": "individual"},
        {"id": "athletics_F_team", "label": "Atletismo Feminino - Equipe (Revezamentos)", "sport": "Athletics", "sex": "F", "event_type": "team"},
        {"id": "judo_M_individual", "label": "Judô Masculino", "sport": "Judo", "sex": "M", "event_type": "individual"},
        {"id": "judo_F_individual", "label": "Judô Feminino", "sport": "Judo", "sex": "F", "event_type": "individual"},
        {"id": "boxing_M_individual", "label": "Boxe Masculino", "sport": "Boxing", "sex": "M", "event_type": "individual"},
        {"id": "boxing_F_individual", "label": "Boxe Feminino", "sport": "Boxing", "sex": "F", "event_type": "individual"},
    ]

    network_labels = [net["label"] for net in networks]
    selected_network_label = st.selectbox(
        "Escolha uma rede para visualizar:",
        network_labels,
        help="Cada rede representa um conjunto específico de atletas e competições"
    )

    # Encontrar a rede selecionada
    selected_network = next(net for net in networks if net["label"] == selected_network_label)

    # ========================================================================
    # CARREGAR DADOS DA REDE SELECIONADA
    # ========================================================================

    sport_lower = selected_network["sport"].lower()
    sex = selected_network["sex"]
    event_type = selected_network["event_type"]

    # Usar DataLoader para carregar (funciona com Drive e local)
    try:
        loader = DataLoader()
        network_data = loader.load_sport_network(sport_lower, sex, event_type)
        df_athletes = network_data['metrics']
        df_edges = network_data['edges']
    except Exception as e:
        st.error(f"Erro ao carregar dados da rede: {e}")
        return

    # Estatísticas básicas da rede (calculadas dos dados carregados)
    num_nodes_total = len(df_athletes)
    num_edges_total = len(df_edges)

    # Carregar summaries para obter modularidade e número correto de comunidades
    summaries_path = PATHS.get('all_summaries', PATHS.get('results_dir').parent / 'all_network_summaries.json')
    modularity = None  # Usar None ao invés de 0.0 para diferenciar "não carregado" de "zero"
    num_communities_from_summary = 0

    if summaries_path and summaries_path.exists():
        try:
            with open(summaries_path, 'r', encoding='utf-8') as f:
                summaries = json.load(f)

            # Buscar a rede específica no JSON (é uma lista, não dict)
            for network_summary in summaries:
                if (network_summary.get('sport') == selected_network["sport"] and
                    network_summary.get('sex') == selected_network["sex"] and
                    network_summary.get('event_type') == selected_network["event_type"]):
                    if 'original_community' in network_summary:
                        modularity = network_summary['original_community'].get('modularity', None)
                        num_communities_from_summary = network_summary['original_community'].get('num_communities', 0)
                    break
        except Exception as e:
            st.warning(f"Aviso ao carregar summaries: {e}")

    # Usar número de comunidades do summary, fallback para contagem no dataframe
    num_communities = num_communities_from_summary if num_communities_from_summary > 0 else (
        df_athletes['original_community'].nunique() if 'original_community' in df_athletes.columns else 0
    )

    # Densidade aproximada
    max_edges = num_nodes_total * (num_nodes_total - 1) if num_nodes_total > 1 else 1
    density = num_edges_total / max_edges if max_edges > 0 else 0

    # ========================================================================
    # MOSTRAR INFORMAÇÕES DA REDE
    # ========================================================================

    st.success(f"**Rede Carregada:** {selected_network_label}")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Atletas (Nós)", f"{num_nodes_total:,}")
    with col2:
        st.metric("Competições (Arestas)", f"{num_edges_total:,}")
    with col3:
        st.metric("Densidade", f"{density:.4f}")
    with col4:
        st.metric("Modularidade", f"{modularity:.3f}" if modularity is not None else "N/A")
    with col5:
        st.metric("Comunidades", num_communities)

    st.markdown("---")

    # ========================================================================
    # FILTROS E OPÇÕES
    # ========================================================================

    st.info(" **Controles**: Todos os controles de visualização (filtros, cores, layout) estão disponíveis no painel interativo dentro do grafo abaixo.")

    # Configurações padrão - SEM filtros! Mostrar TUDO
    show_top_n = num_nodes_total  # TODOS os nós
    min_edge_weight = 1  # TODAS as arestas
    selected_countries = []  # Todos os países
    selected_communities = []  # Todas as comunidades
    node_size_by = "PageRank"
    color_by = "Comunidade"
    color_scheme = "Padrão (UFOP)"  # Corrigido para match do dicionário
    show_labels = False
    edge_opacity = 0.3
    node_scale_range = (5, 30)
    physics_enabled = False
    height = 800
    gravitational_constant = -800
    spring_length = 150
    spring_constant = 0.04
    
    # ========================================================================
    # PREPARAR DADOS DOS NÓS
    # ========================================================================

    df_filtered = df_athletes.copy()

    # DEBUG: Rastrear transformações

    # Aplicar filtro de países
    if selected_countries:
        df_filtered = df_filtered[df_filtered['noc'].isin(selected_countries)]

    # Aplicar filtro de comunidades
    if selected_communities:
        df_filtered = df_filtered[df_filtered['original_community'].isin(selected_communities)]

    # Selecionar top N atletas por PageRank
    if len(df_filtered) > show_top_n:
        df_filtered = df_filtered.nlargest(show_top_n, 'original_pagerank')

    # Remover duplicatas
    antes_drop = len(df_filtered)
    df_filtered = df_filtered.drop_duplicates(subset=['athlete_id'], keep='first')
    depois_drop = len(df_filtered)

    selected_ids = set(df_filtered['athlete_id'].astype(str))

    # Preparar nós com informações completas para tooltip
    nodes = []
    for _, row in df_filtered.iterrows():
        node_id = str(row['athlete_id'])

        # Tamanho do nó
        if node_size_by == "PageRank":
            size = float(row.get('original_pagerank', 0.0001) * 10000)
        elif node_size_by == "Grau Total":
            size = float(row.get('original_total_degree', 1))
        else:  # Betweenness
            size = float(row.get('original_betweenness_centrality', 0.0001) * 100000)

        # Grupo para cor
        if color_by == "Comunidade":
            group = int(row.get('original_community', 0))
        elif color_by == "País (NOC)":
            group = hash(row.get('noc', '')) % 16
        elif color_by == "Década":
            # Extrair ano de 'games' (formato "1920 Summer")
            games_str = str(row.get('games', '2000 Summer'))
            try:
                year = int(games_str.split()[0])
            except:
                year = 2000
            group = (year // 10) % 16  # Década mod 16
        else:  # Tipo de Medalha
            medal = row.get('medal', 'Bronze')
            medal_map = {'Gold': 0, 'Silver': 1, 'Bronze': 2}
            group = medal_map.get(medal, 2)

        # Calcular percentil de PageRank
        pagerank_val = row.get('original_pagerank', 0)
        pagerank_percentile = (df_filtered['original_pagerank'] < pagerank_val).sum() / len(df_filtered) * 100

        # Verificar se é atleta-ponte (betweenness > 75º percentil)
        betweenness_val = row.get('original_betweenness_centrality', 0)
        betweenness_threshold = df_filtered['original_betweenness_centrality'].quantile(0.75)
        is_bridge = betweenness_val > betweenness_threshold

        # Contar medalhas e anos do atleta (usando dados disponíveis na rede)
        athlete_id_val = row['athlete_id']

        # Usar contagens agregadas de medalhas (se disponíveis) ou fallback para medalha única
        medal = row.get('medal', 'Bronze')
        medal_counts = {
            'Gold': int(row.get('gold_medals', 1 if medal == 'Gold' else 0)),
            'Silver': int(row.get('silver_medals', 1 if medal == 'Silver' else 0)),
            'Bronze': int(row.get('bronze_medals', 1 if medal == 'Bronze' else 0))
        }
        total_medals = int(row.get('total_medals', sum(medal_counts.values())))
        
        # Anos de participação (se disponível)
        if 'year' in row:
            years_str = str(row['year'])
        elif 'years' in row:
            years_str = str(row['years'])
        else:
            years_str = 'N/A'

        # Dados completos para tooltip (converter tudo para tipos Python nativos)
        tooltip_data = {
            'name': str(row.get('name', 'N/A')),
            'noc': str(row.get('noc', 'N/A')),
            'team': str(row.get('team', 'N/A')),
            'years': str(years_str),  # Todos os anos de participação
            'years_list': [],  # Lista vazia por enquanto (sem histórico completo)
            'age': int(row.get('age', 0)) if pd.notna(row.get('age')) else 'N/A',
            'height': int(row.get('height', 0)) if pd.notna(row.get('height')) else 'N/A',
            'weight': int(row.get('weight_kg', 0)) if pd.notna(row.get('weight_kg')) else 'N/A',
            'medal_gold': int(medal_counts['Gold']),
            'medal_silver': int(medal_counts['Silver']),
            'medal_bronze': int(medal_counts['Bronze']),
            'medal_total': int(total_medals),
            'pagerank': str(f"{pagerank_val:.6f}"),
            'pagerank_percentile': str(f"{pagerank_percentile:.1f}"),
            'betweenness': str(f"{betweenness_val:.6f}"),
            'is_bridge': True if is_bridge else False,  # Converter para bool Python explicitamente
            'degree_in': int(row.get('original_in_degree', 0)),
            'degree_out': int(row.get('original_out_degree', 0)),
            'degree_total': int(row.get('original_total_degree', 0)),
            'community': int(row.get('original_community', 0)),
        }

        nodes.append({
            'id': node_id,
            'label': row.get('name', f"Atleta {row['athlete_id']}"),
            'size': size,
            'group': group,
            'tooltip_data': tooltip_data
        })


    # Verificar se McLOUGHLIN está nos nodes
    mcl_in_nodes = any('McLOUGHLIN' in n.get('label', '').upper() for n in nodes)

    # ========================================================================
    # PREPARAR DADOS DAS ARESTAS
    # ========================================================================

    links = []

    # Filtrar arestas
    df_edges_filtered = df_edges[
        df_edges['source_id'].astype(str).isin(selected_ids) &
        df_edges['target_id'].astype(str).isin(selected_ids)
    ]

    # Aplicar filtro de peso
    if 'weight' in df_edges_filtered.columns:
        df_edges_filtered = df_edges_filtered[df_edges_filtered['weight'] >= min_edge_weight]
    
    # Otimização adaptativa: limitar arestas baseado no número de nós
    # IMPORTANTE: Se show_top_n == num_nodes_total, NÃO limitar arestas (mostrar TUDO)
    if show_top_n == num_nodes_total:
        # Modo padrão: exibir TODAS as arestas sem limitação
        max_edges = float('inf')
    else:
        # Modo filtrado: aplicar otimização adaptativa
        if len(nodes) > 800:
            max_edges = 1500
        elif len(nodes) > 600:
            max_edges = 2500
        elif len(nodes) > 400:
            max_edges = 4000
        else:
            max_edges = 6000

    if len(df_edges_filtered) > max_edges:
        st.info(f"ℹ Otimização: Exibindo as {max_edges:,} arestas de maior peso (de {len(df_edges_filtered):,} totais). Aumente o peso mínimo para ver conexões mais relevantes.")
        df_edges_filtered = df_edges_filtered.nlargest(max_edges, 'weight')

    for _, edge in df_edges_filtered.iterrows():
        links.append({
            'source': str(edge['source_id']),
            'target': str(edge['target_id']),
            'value': float(edge.get('weight', 1.0))
        })

    # ========================================================================
    # REMOVER NÓS ISOLADOS (sem conexões diretas)
    # ========================================================================

    # Identificar todos os IDs que aparecem nas arestas filtradas
    connected_node_ids = set()
    for link in links:
        connected_node_ids.add(link['source'])
        connected_node_ids.add(link['target'])


    # Filtrar apenas nós que têm pelo menos uma conexão
    nodes_before = len(nodes)
    nodes = [node for node in nodes if node['id'] in connected_node_ids]
    nodes_removed = nodes_before - len(nodes)


    if nodes_removed > 0:
        st.info(f"ℹ Removidos {nodes_removed} nós isolados (sem conexões diretas após filtros)")

    # ========================================================================
    # ESTATÍSTICAS DA REDE VISÍVEL
    # ========================================================================

    st.subheader("3. Visualização da Rede")
    
    # Aviso de desempenho baseado na quantidade real de arestas
    total_elements = len(nodes) + len(links)
    if total_elements > 4000:
        st.error(f" **AVISO:** Renderizando {len(nodes):,} nós e {len(links):,} arestas. A visualização pode ficar lenta. Aumente o peso mínimo das arestas!")
    elif total_elements > 2500:
        st.warning(f" **Atenção:** {len(nodes):,} nós e {len(links):,} arestas. Considere aumentar o peso mínimo das arestas.")
    elif len(links) > 3000:
        st.info(f"ℹ Muitas arestas ({len(links):,}). Se a visualização ficar lenta, aumente o peso mínimo.")
    
    # Aviso sobre física
    if physics_enabled and (len(nodes) > 500 or len(links) > 2000):
        st.warning(" Física ativada com muitos elementos pode causar lentidão significativa.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Nós exibidos", f"{len(nodes):,}")
    with col2:
        st.metric("Arestas exibidas", f"{len(links):,}")
    with col3:
        density_visible = len(links) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0
        st.metric("Densidade visível", f"{density_visible:.4f}")
    with col4:
        avg_degree = (2 * len(links)) / len(nodes) if len(nodes) > 0 else 0
        st.metric("Grau médio", f"{avg_degree:.2f}")

    # ========================================================================
    # LEGENDA DE CORES DINÂMICA
    # ========================================================================

    st.markdown("---")

    # Paleta de cores (replicar a mesma do componente)
    color_schemes_dash = {
        "Padrão (UFOP)": ['#8B2635', '#2E5A88', '#2A7F62', '#D4A017', '#8B4513', '#4B0082', '#008B8B', '#B8860B',
                   '#CD5C5C', '#4682B4', '#9ACD32', '#FF8C00', '#8A2BE2', '#20B2AA', '#CD853F', '#9370DB'],
        "Pastel": ['#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#E0BBE4', '#FFDFD3', '#C9E4DE',
                  '#FFC8DD', '#BDE0FE', '#A2D2FF', '#CDB4DB', '#FEC89A', '#F1FAEE', '#A8DADC', '#E5989B'],
        "Vibrante": ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
                   '#F8B195', '#F67280', '#C06C84', '#6C5B7B', '#355C7D', '#99B898', '#FECEAB', '#FF847C'],
        "Fria": ['#1A535C', '#4ECDC4', '#F7FFF7', '#FF6B6B', '#FFE66D', '#2E86AB', '#A23B72', '#F18F01',
                '#C73E1D', '#6A994E', '#BC4749', '#F2CC8F', '#81B29A', '#3D405B', '#E07A5F', '#F4F1DE'],
        "Quente": ['#D62828', '#F77F00', '#FCBF49', '#EAE2B7', '#003049', '#D9376E', '#FF8C42', '#FFC857',
                '#E5323B', '#F25F5C', '#FFE066', '#50514F', '#247BA0', '#70C1B3', '#B2DBBF', '#F3FFBD']
    }

    selected_palette = color_schemes_dash[color_scheme]

    # Legenda antiga removida - agora está dentro do componente JavaScript interativo

    # ========================================================================
    # RENDERIZAR VISUALIZAÇÃO
    # ========================================================================

    if len(nodes) == 0:
        st.warning("Nenhum atleta encontrado com os filtros aplicados.")
        return

    if len(links) == 0:
        st.warning("Nenhuma aresta encontrada com os filtros aplicados. A visualização mostrará apenas nós isolados.")

    # Mapear nomes de paletas
    color_scheme_map = {
        "Padrão (UFOP)": "default",
        "Pastel": "pastel",
        "Vibrante": "vibrant",
        "Fria": "cool",
        "Quente": "warm"
    }

    # Injetar CSS para forçar iframe a usar largura total
    st.markdown("""
        <style>
        /* Forçar iframe do componente a usar largura total */
        iframe[title="components.html"] {
            width: 100% !important;
        }

        /* Garantir que container do iframe também use largura total */
        .stHtml {
            width: 100% !important;
        }

        /* Se estiver em um bloco, garantir largura total */
        div[data-testid="stVerticalBlock"] > div {
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Renderizar visualização em largura total

    # Verificar novamente McLOUGHLIN antes de passar
    mcl_before_render = any('McLOUGHLIN' in n.get('label', '').upper() for n in nodes)

    render_cosmograph(
        nodes=nodes,
        links=links,
        height=height,
        physics_enabled=physics_enabled,
        show_labels=show_labels,
        color_scheme=color_scheme_map[color_scheme],
        edge_opacity=edge_opacity,
        node_scale_min=node_scale_range[0],
        node_scale_max=node_scale_range[1],
        gravitational_constant=gravitational_constant,
        spring_length=spring_length,
        spring_constant=spring_constant,
        color_by=color_by,
        key="network_interactive"
    )

    # ========================================================================
    # INFORMAÇÕES ADICIONAIS
    # ========================================================================

    with st.expander("ℹ Ajuda e Instruções", expanded=False):
        st.markdown("""
        ### Como usar a visualização interativa:

        - **Navegação:**
          - Arraste com o mouse para mover a câmera
          - Use scroll/pinch para zoom in/out
          - Clique em um nó para selecioná-lo
          - Passe o mouse sobre nós para ver informações (tooltip)

        - **Física:**
          - Com física ativada, os nós se movem seguindo forças de atração/repulsão
          - Com física desativada, o layout é estático (recomendado para redes grandes)
          - A simulação estabiliza automaticamente após alguns segundos

        - **Cores:**
          - Cada cor representa um grupo diferente do atributo selecionado
          - Comunidades são detectadas pelo algoritmo de Louvain
          - Use diferentes paletas para melhor contraste

        - **Performance:**
          - Para redes grandes (>300 nós), recomenda-se desativar física
          - Reduzir opacidade das arestas melhora visualização
          - Desativar labels melhora performance
        """)


def render_temporal_tab(data):
    """Tab: Evolução Temporal."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from core.config.olympic_eras import (
        get_timeline_data,
        get_era_shapes_for_plot,
        get_era_annotations_for_plot,
        OLYMPIC_ERAS
    )
    from visualization.timeline_plots import create_olympic_timeline, create_events_accordion

    st.header("Evolução Temporal")
    st.caption("125 anos de história olímpica: da Belle Époque à Era Profissional Moderna (1896-2021)")
    st.markdown("---")

    # Timeline Visual Interativa com Plotly
    render_section_title("Linha do Tempo Histórica", "4 eras olímpicas de 1896 a 2021")

    st.caption(" **Dica:** Passe o mouse sobre as barras para ver detalhes de cada era")

    # Criar timeline responsiva com Plotly (limpa e objetiva)
    timeline_fig = create_olympic_timeline(OLYMPIC_ERAS, height=350)
    st.plotly_chart(timeline_fig, use_container_width=True, key="olympic_timeline")

    st.markdown("---")

    # Eventos históricos em expanders organizados (4 colunas)
    render_subsection("Eventos Históricos Detalhados", "Expanda cada era para ver os eventos marcantes")

    events_by_era = create_events_accordion(OLYMPIC_ERAS)

    cols = st.columns(4)
    for idx, era_info in enumerate(events_by_era):
        with cols[idx]:
            # Ícone visual da era
            era_icons = {
                'Belle Époque': '',
                'Entre-Guerras': '',
                'Guerra Fria': '',
                'Pós-Guerra Fria': ''
            }
            era_icon = era_icons.get(era_info['name'], '')

            with st.expander(f"{era_icon} **{era_info['name']}**", expanded=False):
                # Badge com período
                st.markdown(f"<div style='background-color: {era_info['color']}; color: white; padding: 8px; border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 10px;'>{era_info['period']}</div>", unsafe_allow_html=True)

                st.markdown(f"*{era_info['description']}*")
                st.markdown("")

                st.markdown("** Características:**")
                for char in era_info['characteristics']:
                    st.markdown(f"• {char}")

                st.markdown("")
                st.markdown("** Eventos-Chave:**")
                for event in era_info['events']:
                    event_icons = {
                        'olympic': '',
                        'political': '',
                        'social': '',
                        'sport': '',
                        'geographic': ''
                    }
                    icon = event_icons.get(event['type'], '')
                    st.markdown(f"**{event['year']}** {icon} *{event['event']}*")

    st.markdown("---")

    with st.expander(" Sobre as Eras Olímpicas", expanded=False):
        st.markdown("""
        A evolução olímpica pode ser dividida em **4 grandes eras históricas**, cada uma com características
        estruturais e competitivas distintas:

        ###  Belle Époque (1896-1912)
        - **Contexto**: Primeiros Jogos Olímpicos da era moderna
        - **Participação**: ~100 atletas por edição, predominância europeia
        - **Características**: Exclusão feminina, esportes tradicionais, amadorismo estrito
        - **Estrutura de Rede**: Pequena, altamente concentrada, poucas conexões internacionais

        ###  Entre-Guerras (1920-1936)
        - **Contexto**: Crescimento pós-Primeira Guerra Mundial
        - **Participação**: ~300-400 atletas, expansão geográfica (América do Sul, Ásia)
        - **Características**: Primeiras participações femininas oficiais, profissionalização incipiente
        - **Estrutura de Rede**: Crescimento moderado, início da diversificação geográfica

        ###  Guerra Fria (1948-1988)
        - **Contexto**: Esporte como campo de batalha ideológica (EUA vs URSS)
        - **Participação**: 400 → 800+ atletas, crescimento exponencial
        - **Características**: Boicotes políticos (1980, 1984), profissionalização em países socialistas
        - **Estrutura de Rede**: Altíssima concentração em blocos, polarização estrutural, PageRank elevado

        ###  Pós-Guerra Fria (1992-2016)
        - **Contexto**: Globalização e democratização do esporte olímpico
        - **Participação**: 800 → 900+ atletas, participação global
        - **Características**: Profissionalização total, avanço feminino (paridade), tecnologia avançada
        - **Estrutura de Rede**: Democratização do PageRank, diversificação geográfica, globalização do esporte

        ---

        ** Como interpretar os gráficos abaixo:**
        - **Faixas coloridas de fundo**: Delimitam cada era histórica
        - **Labels no topo**: Identificam as eras
        - **Anotações nos gráficos**: Destacam transições e eventos importantes
        """)

    # Verificar se temos dados temporais
    if 'year' not in data['athletes'].columns:
        st.warning("Dados temporais não disponíveis. Aplique o filtro temporal na sidebar.")
        return

    with st.spinner("Processando análise temporal..."):
        # Preparar dados agregados por ano
        df = data['athletes'].copy()

        # Preparar dicionário de agregação com colunas disponíveis
        agg_dict = {'athlete_id': 'count'}

        if 'original_pagerank' in df.columns:
            agg_dict['original_pagerank'] = 'mean'
        if 'original_betweenness_centrality' in df.columns:
            agg_dict['original_betweenness_centrality'] = 'mean'
        if 'original_total_degree' in df.columns:
            agg_dict['original_total_degree'] = 'mean'

        df_by_year = df.groupby('year').agg(agg_dict).reset_index()

        # Renomear colunas
        column_mapping = {
            'athlete_id': 'num_athletes',
            'original_pagerank': 'avg_pagerank',
            'original_betweenness_centrality': 'avg_betweenness',
            'original_total_degree': 'avg_degree'
        }
        df_by_year.rename(columns=column_mapping, inplace=True)

    render_subsection("Indicadores Temporais")

    # Métricas resumidas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_years = len(df_by_year)
        st.metric(
            "Anos Analisados",
            f"{total_years}",
            help="Número de edições olímpicas no período selecionado"
        )

    with col2:
        total_athletes = df['athlete_id'].nunique()
        st.metric(
            "Atletas Únicos",
            f"{total_athletes:,}",
            help="Número total de atletas medalhistas únicos"
        )

    with col3:
        avg_athletes_per_year = df_by_year['num_athletes'].mean()
        st.metric(
            "Média de Atletas/Ano",
            f"{avg_athletes_per_year:.0f}",
            help="Média de atletas medalhistas por edição"
        )

    with col4:
        growth_rate = ((df_by_year['num_athletes'].iloc[-1] / df_by_year['num_athletes'].iloc[0]) - 1) * 100 if len(df_by_year) > 1 else 0
        st.metric(
            "Crescimento",
            f"{growth_rate:.0f}%",
            help="Taxa de crescimento entre primeira e última edição"
        )

    st.markdown("---")

    # Visualizações temporais
    render_section_title("Evolução ao Longo do Tempo", "Crescimento da participação e mudanças nas métricas de rede")

    # Gráfico 1: Número de Atletas ao longo do tempo
    col1, col2 = st.columns(2)

    with col1:
        with st.container():
            render_subsection("Crescimento da Participação", "Número de atletas medalhistas por edição olímpica")

            # Determinar range de anos
            years_range = (df_by_year['year'].min(), df_by_year['year'].max())

            fig = go.Figure()

            # Adicionar linha principal
            fig.add_trace(go.Scatter(
                x=df_by_year['year'],
                y=df_by_year['num_athletes'],
                mode='lines+markers',
                name='Atletas',
                line=dict(color='#8B2635', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Atletas: %{y}<extra></extra>'
            ))

            # Adicionar shapes de eras (retângulos de fundo)
            era_shapes = get_era_shapes_for_plot(years_range)

            # Adicionar annotations de eras
            era_annotations = get_era_annotations_for_plot(years_range, y_position=0.98)

            # Calcular estatísticas por era para anotações adicionais
            belle_epoque_data = df_by_year[df_by_year['year'] <= 1912]
            guerra_fria_data = df_by_year[(df_by_year['year'] >= 1948) & (df_by_year['year'] <= 1988)]
            pos_gf_data = df_by_year[df_by_year['year'] >= 1992]

            if len(belle_epoque_data) > 0 and len(pos_gf_data) > 0:
                growth_factor = pos_gf_data['num_athletes'].mean() / belle_epoque_data['num_athletes'].mean()

                # Adicionar anotação de crescimento
                era_annotations.append({
                    'x': 0.02,
                    'y': 0.05,
                    'xref': 'paper',
                    'yref': 'paper',
                    'text': f"<b>Crescimento Belle Époque → Era Moderna:</b><br>{growth_factor:.1f}× mais atletas",
                    'showarrow': False,
                    'font': dict(size=11),
                    'bgcolor': 'rgba(255, 232, 237, 0.9)',
                    'bordercolor': '#8B2635',
                    'borderwidth': 2,
                    'borderpad': 8,
                    'align': 'left',
                    'xanchor': 'left',
                    'yanchor': 'bottom'
                })

            fig.update_layout(
                xaxis_title='Ano',
                yaxis_title='Número de Atletas',
                template='plotly_white',
                hovermode='x unified',
                height=400,
                shapes=era_shapes,
                annotations=era_annotations
            )

            st.plotly_chart(fig, use_container_width=True, key="temporal_athletes_growth")

    with col2:
        if 'avg_pagerank' in df_by_year.columns:
            with st.container():
                render_subsection("Evolução do PageRank Médio", "Mudanças na centralidade média dos atletas ao longo do tempo")

                fig = go.Figure()

                # Adicionar linha principal
                fig.add_trace(go.Scatter(
                    x=df_by_year['year'],
                    y=df_by_year['avg_pagerank'],
                    mode='lines+markers',
                    name='PageRank Médio',
                    line=dict(color='#5A5A5A', width=3),
                    marker=dict(size=8),
                    hovertemplate='<b>%{x}</b><br>PageRank: %{y:.6f}<extra></extra>'
                ))

                # Adicionar shapes e annotations de eras
                era_shapes = get_era_shapes_for_plot(years_range)
                era_annotations = get_era_annotations_for_plot(years_range, y_position=0.98)

                # Calcular estatísticas por era
                entre_guerras_data = df_by_year[(df_by_year['year'] >= 1920) & (df_by_year['year'] <= 1936)]
                guerra_fria_data = df_by_year[(df_by_year['year'] >= 1948) & (df_by_year['year'] <= 1988)]
                pos_gf_data = df_by_year[df_by_year['year'] >= 1992]

                # Encontrar pico da Guerra Fria
                if len(guerra_fria_data) > 0:
                    peak_year = guerra_fria_data.loc[guerra_fria_data['avg_pagerank'].idxmax(), 'year']
                    peak_value = guerra_fria_data['avg_pagerank'].max()

                    # Adicionar anotação do pico
                    era_annotations.append({
                        'x': peak_year,
                        'y': peak_value,
                        'text': f"<b>Pico Guerra Fria</b><br>{peak_year}: {peak_value:.6f}",
                        'showarrow': True,
                        'arrowhead': 2,
                        'arrowsize': 1,
                        'arrowwidth': 2,
                        'arrowcolor': '#8B2635',
                        'ax': 40,
                        'ay': -40,
                        'font': dict(size=10),
                        'bgcolor': 'rgba(255, 232, 237, 0.9)',
                        'bordercolor': '#8B2635',
                        'borderwidth': 2,
                        'borderpad': 4,
                    })

                # Comparar eras
                if len(guerra_fria_data) > 0 and len(pos_gf_data) > 0:
                    gf_avg = guerra_fria_data['avg_pagerank'].mean()
                    pos_avg = pos_gf_data['avg_pagerank'].mean()
                    decrease_pct = ((pos_avg - gf_avg) / gf_avg) * 100

                    era_annotations.append({
                        'x': 0.02,
                        'y': 0.05,
                        'xref': 'paper',
                        'yref': 'paper',
                        'text': f"<b>Democratização Pós-Guerra Fria:</b><br>PageRank médio {abs(decrease_pct):.1f}% menor<br>(Menos concentração de poder)",
                        'showarrow': False,
                        'font': dict(size=11),
                        'bgcolor': 'rgba(255, 255, 255, 0.9)',
                        'bordercolor': '#5A5A5A',
                        'borderwidth': 2,
                        'borderpad': 8,
                        'align': 'left',
                        'xanchor': 'left',
                        'yanchor': 'bottom'
                    })

                fig.update_layout(
                    xaxis_title='Ano',
                    yaxis_title='PageRank Médio',
                    template='plotly_white',
                    hovermode='x unified',
                    height=400,
                    shapes=era_shapes,
                    annotations=era_annotations
                )

                st.plotly_chart(fig, use_container_width=True, key="temporal_pagerank")
        else:
            st.info("Dados de PageRank não disponíveis")

    # Gráfico 2: Betweenness e Degree ao longo do tempo
    if 'avg_betweenness' in df_by_year.columns or 'avg_degree' in df_by_year.columns:
        st.markdown("---")
        render_section_title("Métricas de Centralidade", "Evolução de betweenness e degree ao longo do tempo")

        # Verificar quais colunas existem
        has_betweenness = 'avg_betweenness' in df_by_year.columns
        has_degree = 'avg_degree' in df_by_year.columns

        if has_betweenness and has_degree:
            # Ambas existem - criar subplots
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Betweenness Centrality Médio', 'Degree Centrality Médio')
            )

            # Betweenness
            fig.add_trace(
                go.Scatter(
                    x=df_by_year['year'],
                    y=df_by_year['avg_betweenness'],
                    mode='lines+markers',
                    name='Betweenness',
                    line=dict(color='#8B2635', width=2),
                    marker=dict(size=8),
                    hovertemplate='<b>%{x}</b><br>Betweenness: %{y:.6f}<extra></extra>'
                ),
                row=1, col=1
            )

            # Degree
            fig.add_trace(
                go.Scatter(
                    x=df_by_year['year'],
                    y=df_by_year['avg_degree'],
                    mode='lines+markers',
                    name='Degree',
                    line=dict(color='#5A5A5A', width=2),
                    marker=dict(size=8),
                    hovertemplate='<b>%{x}</b><br>Degree: %{y:.2f}<extra></extra>'
                ),
                row=1, col=2
            )

            fig.update_xaxes(title_text="Ano", row=1, col=1)
            fig.update_xaxes(title_text="Ano", row=1, col=2)

            # Definir range explícito para Betweenness baseado nos dados reais
            betw_min = df_by_year['avg_betweenness'].min()
            betw_max = df_by_year['avg_betweenness'].max()
            betw_margin = (betw_max - betw_min) * 0.1

            fig.update_yaxes(
                title_text="Betweenness Médio",
                row=1, col=1,
                tickformat='.5f',  # 5 casas decimais
                range=[betw_min - betw_margin, betw_max + betw_margin]  # Range explícito com margem
            )
            fig.update_yaxes(title_text="Degree Médio", row=1, col=2)

            # Adicionar shapes de eras (retângulos de fundo) para ambos os subplots
            era_shapes = get_era_shapes_for_plot(years_range)

            # Duplicar shapes para ambos os subplots
            shapes_subplot1 = []
            shapes_subplot2 = []

            for shape in era_shapes:
                # Subplot 1 (Betweenness)
                shape1 = shape.copy()
                shape1['xref'] = 'x'
                shape1['yref'] = 'y'
                shapes_subplot1.append(shape1)

                # Subplot 2 (Degree)
                shape2 = shape.copy()
                shape2['xref'] = 'x2'
                shape2['yref'] = 'y2'
                shapes_subplot2.append(shape2)

            all_shapes = shapes_subplot1 + shapes_subplot2

            # Adicionar annotations de eras
            era_annotations = []

            # Labels das eras para subplot 1
            for era_key, era_data in OLYMPIC_ERAS.items():
                start_year, end_year = era_data['period']

                if end_year < years_range[0] or start_year > years_range[1]:
                    continue

                start_year = max(start_year, years_range[0])
                end_year = min(end_year, years_range[1])
                mid_year = (start_year + end_year) / 2

                # Label para subplot 1
                era_annotations.append({
                    'x': mid_year,
                    'y': 1.05,
                    'xref': 'x',
                    'yref': 'y domain',
                    'text': f"<b>{era_data['name']}</b>",
                    'showarrow': False,
                    'font': dict(size=9, color=era_data['color']),
                    'bgcolor': 'rgba(255, 255, 255, 0.8)',
                    'bordercolor': era_data['color'],
                    'borderwidth': 1,
                    'borderpad': 3,
                })

                # Label para subplot 2
                era_annotations.append({
                    'x': mid_year,
                    'y': 1.05,
                    'xref': 'x2',
                    'yref': 'y2 domain',
                    'text': f"<b>{era_data['name']}</b>",
                    'showarrow': False,
                    'font': dict(size=9, color=era_data['color']),
                    'bgcolor': 'rgba(255, 255, 255, 0.8)',
                    'bordercolor': era_data['color'],
                    'borderwidth': 1,
                    'borderpad': 3,
                })

            # Calcular estatísticas por era para anotações adicionais
            guerra_fria_data = df_by_year[(df_by_year['year'] >= 1948) & (df_by_year['year'] <= 1988)]

            if len(guerra_fria_data) > 0:
                # Adicionar anotação sobre pico de betweenness na Guerra Fria
                peak_between_year = guerra_fria_data.loc[guerra_fria_data['avg_betweenness'].idxmax(), 'year']
                peak_between_value = guerra_fria_data['avg_betweenness'].max()

                era_annotations.append({
                    'x': 0.02,
                    'y': 0.05,
                    'xref': 'x domain',
                    'yref': 'y domain',
                    'text': f"<b>Pico Guerra Fria:</b><br>{peak_between_year}<br>Betweenness: {peak_between_value:.6f}",
                    'showarrow': False,
                    'font': dict(size=10),
                    'bgcolor': 'rgba(255, 232, 237, 0.9)',
                    'bordercolor': '#8B2635',
                    'borderwidth': 2,
                    'borderpad': 6,
                    'align': 'left',
                    'xanchor': 'left',
                    'yanchor': 'bottom'
                })

                # Adicionar anotação sobre degree médio
                avg_degree_gf = guerra_fria_data['avg_degree'].mean()
                avg_degree_pos = pos_gf_data['avg_degree'].mean() if len(pos_gf_data) > 0 else 0

                if avg_degree_pos > 0:
                    change_pct = ((avg_degree_pos - avg_degree_gf) / avg_degree_gf) * 100

                    era_annotations.append({
                        'x': 0.02,
                        'y': 0.05,
                        'xref': 'x2 domain',
                        'yref': 'y2 domain',
                        'text': f"<b>Mudança Pós-GF:</b><br>Degree médio<br>{'+' if change_pct > 0 else ''}{change_pct:.1f}%",
                        'showarrow': False,
                        'font': dict(size=10),
                        'bgcolor': 'rgba(255, 255, 255, 0.9)',
                        'bordercolor': '#5A5A5A',
                        'borderwidth': 2,
                        'borderpad': 6,
                        'align': 'left',
                        'xanchor': 'left',
                        'yanchor': 'bottom'
                    })

            fig.update_layout(
                template='plotly_white',
                height=400,
                showlegend=False,
                shapes=all_shapes,
                annotations=era_annotations
            )

            st.plotly_chart(fig, use_container_width=True, key="temporal_centralities")

        else:
            # Apenas uma existe - gráfico único
            col1, col2 = st.columns(2)

            if has_betweenness:
                with col1:
                    render_subsection("Betweenness Centrality Médio")

                    # Verificar range dos dados
                    betw_min = df_by_year['avg_betweenness'].min()
                    betw_max = df_by_year['avg_betweenness'].max()

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_by_year['year'],
                        y=df_by_year['avg_betweenness'],
                        mode='lines+markers',
                        line=dict(color='#8B2635', width=2),
                        marker=dict(size=8),
                        hovertemplate='<b>%{x}</b><br>Betweenness: %{y:.8f}<extra></extra>'
                    ))

                    # Adicionar shapes e annotations de eras
                    era_shapes = get_era_shapes_for_plot(years_range)
                    era_annotations = get_era_annotations_for_plot(years_range, y_position=0.98)

                    # Encontrar pico
                    guerra_fria_data = df_by_year[(df_by_year['year'] >= 1948) & (df_by_year['year'] <= 1988)]
                    if len(guerra_fria_data) > 0:
                        peak_year = guerra_fria_data.loc[guerra_fria_data['avg_betweenness'].idxmax(), 'year']
                        peak_value = guerra_fria_data['avg_betweenness'].max()

                        era_annotations.append({
                            'x': 0.02,
                            'y': 0.05,
                            'xref': 'paper',
                            'yref': 'paper',
                            'text': f"<b>Pico Guerra Fria:</b><br>{peak_year}: {peak_value:.8f}",
                            'showarrow': False,
                            'font': dict(size=10),
                            'bgcolor': 'rgba(255, 232, 237, 0.9)',
                            'bordercolor': '#8B2635',
                            'borderwidth': 2,
                            'borderpad': 6,
                            'align': 'left',
                            'xanchor': 'left',
                            'yanchor': 'bottom'
                        })

                    # Calcular range com margem de 10%
                    betw_margin = (betw_max - betw_min) * 0.1

                    fig.update_layout(
                        xaxis_title='Ano',
                        yaxis_title='Betweenness Médio',
                        template='plotly_white',
                        height=400,
                        shapes=era_shapes,
                        annotations=era_annotations,
                        yaxis=dict(
                            tickformat='.5f',  # 5 casas decimais
                            range=[betw_min - betw_margin, betw_max + betw_margin]  # Range explícito
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True, key="temporal_betweenness")

            if has_degree:
                with col2:
                    render_subsection("Degree Centrality Médio")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_by_year['year'],
                        y=df_by_year['avg_degree'],
                        mode='lines+markers',
                        line=dict(color='#5A5A5A', width=2),
                        marker=dict(size=6)
                    ))

                    # Adicionar shapes e annotations de eras
                    era_shapes = get_era_shapes_for_plot(years_range)
                    era_annotations = get_era_annotations_for_plot(years_range, y_position=0.98)

                    # Comparar eras
                    guerra_fria_data = df_by_year[(df_by_year['year'] >= 1948) & (df_by_year['year'] <= 1988)]
                    pos_gf_data = df_by_year[df_by_year['year'] >= 1992]

                    if len(guerra_fria_data) > 0 and len(pos_gf_data) > 0:
                        gf_avg = guerra_fria_data['avg_degree'].mean()
                        pos_avg = pos_gf_data['avg_degree'].mean()
                        change_pct = ((pos_avg - gf_avg) / gf_avg) * 100

                        era_annotations.append({
                            'x': 0.02,
                            'y': 0.05,
                            'xref': 'paper',
                            'yref': 'paper',
                            'text': f"<b>Mudança Pós-Guerra Fria:</b><br>Degree médio {'+' if change_pct > 0 else ''}{change_pct:.1f}%",
                            'showarrow': False,
                            'font': dict(size=10),
                            'bgcolor': 'rgba(255, 255, 255, 0.9)',
                            'bordercolor': '#5A5A5A',
                            'borderwidth': 2,
                            'borderpad': 6,
                            'align': 'left',
                            'xanchor': 'left',
                            'yanchor': 'bottom'
                        })

                    fig.update_layout(
                        xaxis_title='Ano',
                        yaxis_title='Degree Médio',
                        template='plotly_white',
                        height=400,
                        shapes=era_shapes,
                        annotations=era_annotations
                    )
                    st.plotly_chart(fig, use_container_width=True, key="temporal_degree")

    # Comparação por esporte
    st.markdown("---")
    render_section_title("Comparação Entre Esportes", "Evolução temporal comparativa de diferentes esportes")

    sports_available = sorted(df['sport'].unique())
    selected_sports_temporal = st.multiselect(
        "Selecione esportes para comparar",
        options=sports_available,
        default=sports_available[:min(3, len(sports_available))],
        help="Selecione até 3 esportes para comparar evolução"
    )

    if selected_sports_temporal:
        # Preparar agregação por esporte
        agg_dict_sports = {'athlete_id': 'count'}
        if 'original_pagerank' in df.columns:
            agg_dict_sports['original_pagerank'] = 'mean'

        df_sports = df[df['sport'].isin(selected_sports_temporal)].groupby(['year', 'sport']).agg(agg_dict_sports).reset_index()

        # Renomear colunas
        column_mapping_sports = {
            'athlete_id': 'num_athletes',
            'original_pagerank': 'avg_pagerank'
        }
        df_sports.rename(columns=column_mapping_sports, inplace=True)

        col1, col2 = st.columns(2)

        with col1:
            render_subsection("Número de Atletas por Esporte")

            fig = go.Figure()
            colors = ['#8B2635', '#5A5A5A', '#A0A0A0']

            for i, sport in enumerate(selected_sports_temporal):
                sport_data = df_sports[df_sports['sport'] == sport]
                fig.add_trace(go.Scatter(
                    x=sport_data['year'],
                    y=sport_data['num_athletes'],
                    mode='lines+markers',
                    name=sport,
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=6)
                ))

            fig.update_layout(
                xaxis_title='Ano',
                yaxis_title='Número de Atletas',
                template='plotly_white',
                hovermode='x unified',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True, key="temporal_sports_athletes")

        with col2:
            if 'avg_pagerank' in df_sports.columns:
                render_subsection("PageRank Médio por Esporte")

                fig = go.Figure()

                for i, sport in enumerate(selected_sports_temporal):
                    sport_data = df_sports[df_sports['sport'] == sport]
                    fig.add_trace(go.Scatter(
                        x=sport_data['year'],
                        y=sport_data['avg_pagerank'],
                        mode='lines+markers',
                        name=sport,
                        line=dict(color=colors[i % len(colors)], width=2),
                        marker=dict(size=6)
                    ))

                fig.update_layout(
                    xaxis_title='Ano',
                    yaxis_title='PageRank Médio',
                    template='plotly_white',
                    hovermode='x unified',
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True, key="temporal_sports_pagerank")
            else:
                st.info("Dados de PageRank não disponíveis para comparação")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Função principal do dashboard."""

    # Carregar dados
    with st.spinner("Carregando dados..."):
        data = load_data()

    # Sidebar com filtros
    filters = render_sidebar(data)

    # Aplicar filtros
    filtered_data = filter_data(data, filters)

    # Verificar se há dados após filtro
    if len(filtered_data['athletes']) == 0:
        st.warning("Nenhum dado disponível com os filtros selecionados. Ajuste os filtros na barra lateral.")
        return

    # Título principal
    # Cabeçalho principal
    st.title("Análise de Redes Olímpicas")
    st.markdown("Modelagem de Relações Competitivas através de Teoria de Redes Complexas")

    # Informações de contexto
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.caption("Dataset: 125 anos de história olímpica (1896-2021)")
    with col2:
        st.caption("Algoritmos: PageRank, Louvain, Métricas de Centralidade")
    with col3:
        st.caption(f"{len(filtered_data['athletes']):,} atletas filtrados")

    st.markdown("---")

    # Tabs principais
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Visão Geral",
        "Comunidades",
        "Atletas-Ponte",
        "Rivalidades",
        "Rankings",
        "Evolução Temporal",
        "Rede Interativa"
    ])

    with tab1:
        render_overview_tab(filtered_data)

    with tab2:
        render_communities_tab(filtered_data)

    with tab3:
        render_bridges_tab(filtered_data)

    with tab4:
        render_rivalries_tab(filtered_data)

    with tab5:
        render_rankings_tab(filtered_data)

    with tab6:
        render_temporal_tab(filtered_data)

    with tab7:
        render_network_tab(filtered_data)


if __name__ == '__main__':
    main()
