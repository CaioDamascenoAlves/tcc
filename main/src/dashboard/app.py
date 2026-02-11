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
    violin_betweenness_by_event,
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
        - **Rede Interativa:** Visualização gráfica das conexões

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

    # Filtro: Eventos Específicos (NOVO - per-event modeling)
    st.sidebar.markdown("---")
    st.sidebar.subheader("Eventos Específicos")

    # Obter metadata das redes se disponível
    if 'metadata' in data and data['metadata'] is not None and not data['metadata'].empty:
        metadata = data['metadata']

        # Filtrar metadata baseado nos filtros anteriores
        available_networks = metadata[
            (metadata['sport'].isin(selected_sports)) &
            (metadata['gender'].isin(selected_sex))
        ]

        # Lista de eventos disponíveis
        event_options = sorted(available_networks['event_name'].unique())

        selected_events = st.sidebar.multiselect(
            "Eventos",
            options=event_options,
            default=event_options,  # Todos por padrão
            help="Selecione eventos específicos para análise. Cada evento é uma rede independente."
        )

        # Info: quantas redes selecionadas
        n_selected_networks = len(available_networks[
            available_networks['event_name'].isin(selected_events)
        ])

        st.sidebar.info(f"📊 {n_selected_networks} redes selecionadas de {len(metadata)} disponíveis")
    else:
        # Fallback: metadata não carregada (erro de configuração)
        selected_events = []
        st.sidebar.error("⚠️ Metadata não carregada. Verifique DataLoader.")

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

            # Se min==max (um único evento), não usar slider
            if min_year == max_year:
                st.sidebar.info(f"Período: {min_year}")
                selected_year_range = (min_year, max_year)
            else:
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
        'events': selected_events,  # NOVO
        'year_range': selected_year_range,
    }


def render_filter_summary(filtered_data):
    """Renderiza resumo dos dados filtrados na sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Dados Selecionados")

    if 'athletes' not in filtered_data or filtered_data['athletes'].empty:
        st.sidebar.warning("Nenhum dado selecionado")
        return

    df = filtered_data['athletes']

    # Calcular estatísticas
    n_athletes = len(df)
    n_sports = df['sport'].nunique()

    # Usar 'sex' ou 'gender' (compatibilidade)
    sex_col = 'sex' if 'sex' in df.columns else 'gender'
    n_genders = df[sex_col].nunique() if sex_col in df.columns else 0

    # Contar redes selecionadas
    n_networks = df['network_id'].nunique() if 'network_id' in df.columns else 0

    # Exibir métricas em colunas
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Atletas", f"{n_athletes:,}")
        st.metric("Esportes", n_sports)
    with col2:
        st.metric("Redes", n_networks)
        st.metric("Sexos", n_genders)

    # Lista de esportes selecionados
    sports_list = sorted(df['sport'].unique())
    if len(sports_list) <= 6:
        sports_str = ", ".join([s.title() for s in sports_list])
        st.sidebar.caption(f"🏅 {sports_str}")
    else:
        st.sidebar.caption(f"🏅 {len(sports_list)} esportes selecionados")


def show_data_context(data):
    """Exibe contexto dos dados filtrados no topo do tab."""
    if 'athletes' not in data or data['athletes'].empty:
        return

    df = data['athletes']
    n_athletes = len(df)
    n_networks = df['network_id'].nunique() if 'network_id' in df.columns else 0
    n_sports = df['sport'].nunique()

    # Construir mensagem contextual
    if n_networks > 0:
        msg = f"📊 **{n_athletes:,} atletas** de **{n_networks} redes** ({n_sports} esporte{'s' if n_sports > 1 else ''})"
    else:
        msg = f"📊 **{n_athletes:,} atletas** ({n_sports} esporte{'s' if n_sports > 1 else ''})"

    st.info(msg)


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

        # Aplicar filtros
        if filters['sports']:
            df = df[df['sport'].isin(filters['sports'])]

        # Filtro por sexo/gênero (compatibilidade com ambos os nomes de coluna)
        if filters['sex']:
            if 'sex' in df.columns:
                df = df[df['sex'].isin(filters['sex'])]
            elif 'gender' in df.columns:
                df = df[df['gender'].isin(filters['sex'])]

        # NOVO: Filtro por eventos específicos (per-event modeling)
        # Apenas aplicar se eventos foram especificamente selecionados E é uma lista não-vazia
        if filters.get('events') is not None and len(filters.get('events', [])) > 0 and 'metadata' in data and not data['metadata'].empty and 'network_id' in df.columns:
            # Obter network_ids correspondentes aos eventos selecionados
            # CRÍTICO: filtrar metadata pelos mesmos critérios de sport/sex ANTES de buscar network_ids
            metadata = data['metadata'].copy()
            
            # Aplicar filtros de sport e sex no metadata primeiro
            if filters['sports']:
                metadata = metadata[metadata['sport'].isin(filters['sports'])]
            if filters['sex']:
                metadata = metadata[metadata['gender'].isin(filters['sex'])]
            
            # Agora buscar network_ids dos eventos selecionados no metadata já filtrado
            valid_network_ids = metadata[
                metadata['event_name'].isin(filters['events'])
            ]['network_id'].unique()

            if len(valid_network_ids) > 0:
                df = df[df['network_id'].isin(valid_network_ids)]
                print(f"DEBUG: Filtro de eventos aplicado - {len(valid_network_ids)} redes, {len(df)} atletas")
            else:
                print(f"DEBUG: Nenhum network_id válido para eventos selecionados - metadata filtrado tem {len(metadata)} redes")

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
        # Nota: communities tem network_id mas pode não ter sport/sex direto
        if 'communities' in data:
            df = data['communities'].copy()
            # Filtrar por network_id baseado nos atletas filtrados
            if 'network_id' in df.columns and 'network_id' in filtered['athletes'].columns and len(filtered['athletes']) > 0:
                valid_network_ids = filtered['athletes']['network_id'].unique()
                df = df[df['network_id'].isin(valid_network_ids)]
            # Se não conseguiu filtrar por network_id ou athletes está vazio, manter todos
            filtered['communities'] = df
        else:
            filtered['communities'] = pd.DataFrame()

        # Hierarchy
        # Nota: hierarchy tem network_id mas não tem sport/sex
        # Filtrar por network_id baseado nos atletas filtrados
        df = data['hierarchy'].copy()
        if 'network_id' in df.columns and 'network_id' in filtered['athletes'].columns:
            valid_network_ids = filtered['athletes']['network_id'].unique()
            df = df[df['network_id'].isin(valid_network_ids)]
        filtered['hierarchy'] = df

        # Connectivity
        df = data['connectivity'].copy()
        if filters['sports'] and 'sport' in df.columns:
            df = df[df['sport'].isin(filters['sports'])]
        if filters['sex'] and 'sex' in df.columns:
            df = df[df['sex'].isin(filters['sex'])]
        filtered['connectivity'] = df

        # Rivalries (ATUALIZADO: agora per-event com network_id)
        df = data['rivalries'].copy()
        if filters['sports'] and 'sport' in df.columns:
            df = df[df['sport'].isin(filters['sports'])]
        if filters['sex'] and 'sex' in df.columns:
            df = df[df['sex'].isin(filters['sex'])]
        # NOVO: Filtrar por network_id (per-event)
        if 'network_id' in df.columns:
            valid_network_ids = filtered['athletes']['network_id'].unique()
            df = df[df['network_id'].isin(valid_network_ids)]
        filtered['rivalries'] = df

        # Metadata (IMPORTANTE: necessário para tab Network)
        if 'metadata' in data:
            df = data['metadata'].copy()
            if filters['sports']:
                df = df[df['sport'].isin(filters['sports'])]
            if filters['sex']:
                # Metadata usa 'gender', não 'sex'
                df = df[df['gender'].isin(filters['sex'])]
            if filters.get('events'):
                df = df[df['event_name'].isin(filters['events'])]
            filtered['metadata'] = df
        else:
            filtered['metadata'] = pd.DataFrame()

        # Edges (passar sem filtrar - será filtrado por network_id quando necessário)
        filtered['edges'] = data.get('edges', pd.DataFrame())

        # Analysis consolidated
        filtered['analysis'] = data.get('analysis', pd.DataFrame())

        # Community members
        filtered['community_members'] = data.get('community_members', pd.DataFrame())

        # Typology
        filtered['typology'] = data.get('community_typology', pd.DataFrame())

    return filtered


# ============================================================================
# TAB 1: VISÃO GERAL
# ============================================================================

def render_overview_tab(data):
    """Tab: Visão Geral."""
    st.header("Visão Geral")
    st.caption("Estatísticas gerais e distribuições fundamentais das redes olímpicas")
    show_data_context(data)
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
        # Contar comunidades TOTAL (soma por rede, não nunique global)
        # Cada rede tem suas próprias comunidades numeradas de 0...N
        if 'athletes' in data and 'original_community' in data['athletes'].columns and 'network_id' in data['athletes'].columns:
            # Contar comunidades únicas por rede e somar
            num_communities = data['athletes'].groupby('network_id')['original_community'].nunique().sum()
        elif 'communities' in data and data['communities'] is not None and len(data['communities']) > 0:
            num_communities = len(data['communities'])
        elif 'metadata' in data and 'n_communities' in data['metadata'].columns:
            # Fallback: somar do metadata
            num_communities = int(data['metadata']['n_communities'].sum())
        else:
            num_communities = 0
        
        st.metric(
            "Comunidades Detectadas",
            f"{num_communities:,}",
            help="Total de comunidades nas redes SELECIONADAS pelos filtros da sidebar. "
                 "Cada rede tem comunidades próprias (IDs reiniciam em 0 por rede)."
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
        n_sports = data['athletes']['sport'].nunique()
        help_text = "PageRank médio dos atletas"
        if n_sports > 1:
            help_text += f" ({n_sports} esportes - agregado, use com cautela)"
        st.metric(
            "PageRank Médio",
            f"{avg_pr:.6f}",
            help=help_text
        )

    st.markdown("---")

    # Tabela Comparativa
    with st.spinner("Gerando tabela comparativa..."):
        render_comparative_table(data)

    st.markdown("---")

    # Visualizações principais
    render_section_title("Distribuições Estatísticas", "Análise da distribuição de intermediação na rede")

    # Nota: CDF de PageRank global foi REMOVIDO (comparação cross-esporte enviesada)
    # Mantemos apenas Betweenness por esporte (comparação válida)

    with st.container():
        render_subsection("Betweenness Centrality por Evento", "Distribuição dos atletas-ponte por evento específico")
        
        # Warning metodológico
        if 'athletes' in data and 'event_name' in data['athletes'].columns:
            n_events = data['athletes']['event_name'].nunique()
            if n_events > 1:
                st.warning(f"""
                Atenção: {n_events} eventos selecionados. Betweenness é calculado por rede.
                Filtre um único evento na sidebar para análise precisa.
                """)
            
            # Warning de limitação de visualização
            if n_events > 20:
                st.info(f"Mostrando os 20 primeiros eventos de {n_events} para legibilidade. Use filtros para selecionar eventos específicos.")
        
        # Usar evento como agrupamento, não esporte
        fig = violin_betweenness_by_event(data['athletes'], interactive=True)
        st.plotly_chart(fig, use_container_width=True, key="overview_violin_betweenness")


# ============================================================================
# TAB 2: COMUNIDADES
# ============================================================================

def render_communities_tab(data):
    """Tab: Análise de Comunidades."""
    st.header("Análise de Comunidades")
    st.caption("Estrutura, hierarquia e características das comunidades detectadas pelo algoritmo de Louvain")
    show_data_context(data)
    st.markdown("---")

    with st.expander("Sobre Detecção de Comunidades"):
        st.markdown("""
        As **comunidades** são grupos de atletas densamente conectados entre si, identificados automaticamente pelo **algoritmo de Louvain**.

        **Hierarquia Estrutural:**
        - **Núcleo (top 20%)**: Comunidades com alto PageRank médio - grupos de elite altamente conectados
        - **Intermediária (60%)**: Comunidades com centralidade moderada - grupos competitivos estáveis  
        - **Periférica (20%)**: Comunidades com baixo PageRank médio - grupos menos centrais

        **Tamanho das Comunidades:**
        Distribuição de atletas por comunidade. Comunidades pequenas (2-10 atletas) são mais comuns,
        representando grupos especializados de competidores frequentes. Comunidades grandes (>20 atletas)
        indicam eventos com alta recorrência de confrontos entre os mesmos atletas.
        
        **IMPORTANTE:** Cada rede (evento) tem suas próprias comunidades independentes. 
        Filtre UMA rede específica para análise detalhada de um evento individual.
        """)

    # Subtabs
    subtab1, subtab2 = st.tabs(["Hierarquia", "Tamanho das Comunidades"])

    with subtab1:
        render_subsection("Hierarquia de Comunidades", "Análise da hierarquia estrutural baseada em PageRank médio")
        
        n_networks = data['athletes']['network_id'].nunique() if 'network_id' in data['athletes'].columns else 0
        if n_networks > 1:
            st.warning(f"⚠️ **{n_networks} redes selecionadas.** Hierarquia calculada DENTRO de cada rede. Use filtros para analisar rede individual.")
        
        st.markdown("""
        Comunidades de **Núcleo** têm alta centralidade, **Periféricas** têm baixa.
        """)

        # Aviso sobre comparabilidade
        if 'athletes' in data and data['athletes']['sport'].nunique() > 1:
            st.warning("⚠️ **Atenção:** PageRank é específico a cada rede. "
                       "Comunidades de esportes diferentes não são diretamente comparáveis. "
                       "Use os filtros da sidebar para analisar esportes separadamente.")

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

        # Aviso se múltiplos esportes selecionados
        if 'athletes' in data and data['athletes']['sport'].nunique() > 1:
            st.info("💡 Múltiplos esportes selecionados. Hierarquia baseada em PageRank é mais significativa "
                    "dentro de cada esporte. Use os filtros para analisar esportes separadamente.")

        hierarchy_df = data['hierarchy'].copy()

        # Converter hierarquia numérica para categórica se necessário
        if hierarchy_df['hierarchy_level'].dtype in ['int64', 'float64']:
            hierarchy_df['hierarchy_level'] = hierarchy_df['hierarchy_level'].map({
                1: 'Núcleo',
                2: 'Intermediária',
                3: 'Periférica'
            })

        # Contagem por nível
        level_counts = hierarchy_df['hierarchy_level'].value_counts()
        level_stats = hierarchy_df.groupby('hierarchy_level')['pagerank_mean'].mean()
        
        # Adicionar explicação sobre os números
        total_hier = level_counts.sum()
        st.info(f"""
        **Classificação hierárquica:** {int(total_hier):,} comunidades classificadas em 3 níveis.
        
        Este número representa a soma das comunidades de TODAS as redes selecionadas pelos filtros da sidebar.
        Cada comunidade é classificada dentro de sua rede (top 20% = Núcleo, meio 60% = Intermediária, bottom 20% = Periférica).
        """)

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
        render_subsection("Tamanho das Comunidades", "Distribuição de atletas por comunidade")
        
        st.markdown("""
        **Análise estrutural**: Comunidades variam em tamanho desde grupos pequenos (2-3 atletas) 
        até grandes redes de dezenas de atletas conectados por competições.
        """)

        # Verificar se temos dados de communities
        if 'communities' in data and data['communities'] is not None and len(data['communities']) > 0:
            community_data = data['communities']

            # Verificar se tem coluna size
            if 'size' in community_data.columns:
                import plotly.express as px
                
                # Estatísticas descritivas de tamanho
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Total Comunidades",
                        f"{len(community_data):,}",
                        help="Número total de comunidades nas redes selecionadas"
                    )
                with col2:
                    st.metric(
                        "Tamanho Médio",
                        f"{community_data['size'].mean():.1f}",
                        help="Média de atletas por comunidade"
                    )
                with col3:
                    st.metric(
                        "Menor Comunidade",
                        f"{int(community_data['size'].min())}",
                        help="Comunidade com menos atletas"
                    )
                with col4:
                    st.metric(
                        "Maior Comunidade",
                        f"{int(community_data['size'].max())}",
                        help="Comunidade com mais atletas"
                    )

                st.markdown("---")

                # Histograma de distribuição de tamanhos
                fig = px.histogram(
                    community_data,
                    x='size',
                    nbins=30,
                    title='Distribuição de Tamanho das Comunidades',
                    labels={'size': 'Número de Atletas', 'count': 'Número de Comunidades'},
                    color_discrete_sequence=['#1f77b4']
                )
                fig.update_layout(
                    xaxis_title='Número de Atletas na Comunidade',
                    yaxis_title='Frequência (Número de Comunidades)',
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True, key="communities_size_histogram")
                
                st.caption("""
                **Interpretação**: A maioria das comunidades são pequenas (2-10 atletas), 
                refletindo grupos especializados de competidores frequentes. 
                Comunidades grandes (>20 atletas) são raras e indicam eventos com alta recorrência de confrontos.
                """)
            else:
                st.info("Coluna 'size' não encontrada nos dados de comunidades.")
        else:
            st.info("Dados de comunidades não disponíveis para visualização.")


# ============================================================================
# TAB 3: ATLETAS-PONTE
# ============================================================================

def render_bridges_tab(data):
    """Tab: Atletas-Ponte."""
    st.header("Atletas-Ponte")
    st.caption("Atletas que ocupam posições estruturais críticas, conectando diferentes comunidades ou eras competitivas")
    show_data_context(data)
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
            
            # Warning metodológico: agregação de múltiplos eventos
            if 'athletes' in data and data['athletes']['event_name'].nunique() > 1:
                st.info("""
                📊 **Nota:** Esta distribuição agrega múltiplos eventos. 
                Betweenness é calculado por rede. Padrões mostram diferenças estruturais entre esportes.
                """)
            
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

    # Tabela detalhada com granularidade por evento
    render_subsection("Atletas-Ponte Detalhados", "Visualização com informação de evento e ano")
    
    # Opção de agrupamento
    groupby_option = st.radio(
        "Agrupar por:",
        ["Esporte", "Evento", "Período (Cold War / Pós-Guerra Fria)"],
        horizontal=True,
        help="Escolha o nível de granularidade da análise"
    )
    
    # Preparar colunas para exibição
    display_cols_base = ['name', 'noc', 'sport', 'sex']
    
    # Adicionar event_name e year se disponíveis
    if 'event_name' in bridges.columns:
        display_cols_base.append('event_name')
    if 'year' in bridges.columns:
        display_cols_base.append('year')
    
    display_cols_base.extend(['original_betweenness_centrality', 'original_pagerank'])
    
    # Filtrar apenas colunas que existem
    display_cols = [col for col in display_cols_base if col in bridges.columns]
    
    if groupby_option == "Esporte":
        st.markdown("**Top 5 atletas-ponte por esporte:**")
        for sport in sorted(bridges['sport'].unique()):
            sport_bridges = bridges[bridges['sport'] == sport].nlargest(5, 'original_betweenness_centrality')

            if len(sport_bridges) > 0:
                with st.expander(f"🏆 {sport.title()} ({len(bridges[bridges['sport'] == sport])} bridges no total)"):
                    st.dataframe(
                        sport_bridges[display_cols],
                        use_container_width=True,
                        hide_index=True
                    )
    
    elif groupby_option == "Evento":
        st.markdown("**Top 3 atletas-ponte por evento específico:**")
        
        # Verificar se event_name existe
        if 'event_name' not in bridges.columns:
            st.warning("⚠️ Coluna 'event_name' não disponível nos dados. Mostrando por esporte.")
        else:
            # Agrupar por esporte primeiro para organização
            for sport in sorted(bridges['sport'].unique()):
                sport_bridges = bridges[bridges['sport'] == sport]
                events_in_sport = sport_bridges['event_name'].unique()
                
                with st.expander(f"🏆 {sport.title()} ({len(events_in_sport)} eventos)"):
                    for event in sorted(events_in_sport)[:10]:  # Limitar a 10 eventos por esporte
                        event_bridges = sport_bridges[sport_bridges['event_name'] == event].nlargest(3, 'original_betweenness_centrality')
                        
                        if len(event_bridges) > 0:
                            st.markdown(f"**{event}**")
                            st.dataframe(
                                event_bridges[display_cols],
                                use_container_width=True,
                                hide_index=True
                            )
                            st.markdown("---")
    
    elif groupby_option == "Período (Cold War / Pós-Guerra Fria)":
        st.markdown("**Atletas-ponte por período histórico:**")
        
        # Verificar se year existe
        if 'year' not in bridges.columns:
            st.warning("⚠️ Coluna 'year' não disponível nos dados. Mostrando por esporte.")
        else:
            # Definir períodos
            bridges_with_period = bridges.copy()
            bridges_with_period['periodo'] = bridges_with_period['year'].apply(
                lambda y: "Pré-Guerra Fria (até 1947)" if y < 1948 else 
                         ("Guerra Fria (1948-1991)" if y <= 1991 else "Pós-Guerra Fria (1992+)")
            )
            
            for periodo in ["Pré-Guerra Fria (até 1947)", "Guerra Fria (1948-1991)", "Pós-Guerra Fria (1992+)"]:
                periodo_bridges = bridges_with_period[bridges_with_period['periodo'] == periodo].nlargest(10, 'original_betweenness_centrality')
                
                if len(periodo_bridges) > 0:
                    with st.expander(f"🕐 {periodo} ({len(bridges_with_period[bridges_with_period['periodo'] == periodo])} bridges)"):
                        st.dataframe(
                            periodo_bridges[display_cols],
                            use_container_width=True,
                            hide_index=True
                        )
    
    # Nota metodológica
    st.info("""
    💡 **Interpretação:** Betweenness centrality identifica atletas que conectam diferentes grupos. 
    Valores mais altos indicam maior importância estrutural na rede do evento específico.
    """)


# ============================================================================
# TAB 4: RIVALIDADES
# ============================================================================

def render_rivalries_tab(filtered_data):
    """Tab: Rivalidades Estruturais."""
    st.header("Rivalidades Estruturais")
    st.caption("Pares de comunidades com padrões intensos de confrontos competitivos diretos")

    # Info sobre seleção atual
    if 'metadata' in filtered_data and not filtered_data['metadata'].empty:
        n_redes = filtered_data['metadata']['network_id'].nunique()
        n_atletas = len(filtered_data['athletes'])
        st.info(f"📊 Analisando **{n_atletas:,} atletas** de **{n_redes} redes** selecionadas")

    st.markdown("---")

    with st.expander("ℹ️ Sobre Rivalidades Estruturais"):
        st.markdown("""
        **Rivalidades estruturais** são identificadas pelo número de arestas (confrontos) entre pares de comunidades **dentro de cada evento**.
        Quanto maior o número de confrontos, mais intensa a rivalidade estrutural entre os grupos.

        **Nota:** As rivalidades mostradas respeitam os filtros globais selecionados na sidebar.
        
        ✅ **Atualização:** Os dados de rivalidades agora são calculados **POR EVENTO** (per-event modeling).
        Cada rivalidade pertence a uma rede específica (evento + ano), permitindo análise granular.
        """)

    # Usar dados já filtrados (não carregar novamente!)
    rivalries_filtered = filtered_data.get('rivalries', pd.DataFrame())

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

    # Heatmap de segregação (usar dados filtrados)
    render_section_title("Mapa de Segregação", "Heatmap mostrando a segregação entre comunidades")

    # Avisar se múltiplos esportes selecionados
    if 'athletes' in filtered_data and filtered_data['athletes']['sport'].nunique() > 1:
        st.warning("⚠️ **Atenção:** Múltiplos esportes selecionados. "
                   "Segregação é mais significativa dentro de cada esporte.")

    connectivity_filtered = filtered_data.get('connectivity', pd.DataFrame())
    if not connectivity_filtered.empty:
        fig = heatmap_segregation(connectivity_filtered, interactive=True)
        st.plotly_chart(fig, use_container_width=True, key="rivalries_segregation_heatmap")
    else:
        st.info("Sem dados de conectividade para os filtros selecionados")

    st.markdown("---")

    # Tabela completa
    render_subsection("Tabela Completa de Rivalidades")
    
    # Preparar DataFrame para exibição
    display_df = rivalries_filtered.sort_values('num_confronts', ascending=False).copy()
    
    # Selecionar colunas relevantes (se existirem)
    cols_to_show = []
    if 'event_name' in display_df.columns:
        cols_to_show.append('event_name')
    if 'sport' in display_df.columns:
        cols_to_show.append('sport')
    if 'sex' in display_df.columns:
        cols_to_show.append('sex')
    
    cols_to_show.extend(['community_1', 'community_2', 'num_confronts'])
    
    # Renomear colunas para português
    rename_map = {
        'event_name': 'Evento',
        'sport': 'Esporte',
        'sex': 'Sexo',
        'community_1': 'Comunidade 1',
        'community_2': 'Comunidade 2',
        'num_confronts': 'Confrontos'
    }
    
    display_df = display_df[[col for col in cols_to_show if col in display_df.columns]]
    display_df = display_df.rename(columns=rename_map)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================================
# TAB 5: RANKINGS
# ============================================================================

def render_rankings_tab(data):
    """Tab: Rankings de Atletas."""
    st.header("Rankings de Atletas")
    st.caption("Rankings customizáveis baseados em diferentes métricas de centralidade de rede")
    show_data_context(data)
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

    # Rankings por evento (per-event modeling)
    st.markdown(f"### Top {top_n} por Evento")
    st.info(f"📊 **{selected_metric_name}** é calculado independentemente para cada rede (evento). "
            "Rankings são apresentados por evento para análise granular.")

    # Verifica se há dados filtrados
    if 'athletes' not in data or data['athletes'].empty:
        st.warning("⚠️ Nenhum dado disponível com os filtros atuais.")
        return

    # Verificar se tem event_name nos dados
    if 'event_name' not in data['athletes'].columns:
        st.error("❌ Coluna 'event_name' não encontrada nos dados. Impossível agrupar por evento.")
        return

    # Agrupar por evento (event_name é único por network_id)
    available_events = sorted(data['athletes']['event_name'].dropna().unique())

    if len(available_events) == 0:
        st.warning("⚠️ Nenhum evento disponível nos dados filtrados.")
        return

    for event in available_events:
        with st.expander(f"🏅 {event}", expanded=False):
            event_data = data['athletes'][data['athletes']['event_name'] == event].copy()

            # Pegar informações do evento
            event_sport = event_data['sport'].iloc[0] if 'sport' in event_data.columns else 'N/A'
            event_sex = event_data['sex'].iloc[0] if 'sex' in event_data.columns else event_data['gender'].iloc[0] if 'gender' in event_data.columns else 'N/A'
            
            st.caption(f"**Esporte:** {event_sport} | **Sexo:** {event_sex}")
            
            # Mostrar ranking do evento
            if not event_data.empty:
                fig = table_top_athletes(
                    event_data,
                    metric_column=selected_metric,
                    top_n=top_n,
                    interactive=True
                )
                st.plotly_chart(fig, use_container_width=True, key=f"ranking_{event.replace(' ', '_')}")
            else:
                st.info("Sem dados para este evento")

    st.markdown("---")

    # Distribuição por evento (não por esporte)
    render_section_title(f"Distribuição de {selected_metric_name}", "Análise estatística da métrica selecionada por evento")

    # Aviso para PageRank
    if selected_metric == 'original_pagerank':
        st.info("📊 **PageRank** é calculado independentemente para cada evento (rede). "
                "A distribuição mostra variação entre todos os eventos selecionados.")

    # Boxplot por evento (limitado para não poluir)
    n_events = data['athletes']['event_name'].nunique() if 'event_name' in data['athletes'].columns else 0
    
    if n_events > 0 and n_events <= 10:
        fig = boxplot_metric_by_category(
            data['athletes'],
            metric_column=selected_metric,
            category_column='event_name',
            interactive=True,
            title=f'{selected_metric_name} por Evento'
        )
        st.plotly_chart(fig, use_container_width=True, key="rankings_boxplot_by_event")
    elif n_events > 10:
        st.warning(f"⚠️ Muitos eventos selecionados ({n_events}). Use os filtros da sidebar para reduzir e visualizar a distribuição.")
    else:
        st.info("Sem dados de eventos para visualizar distribuição.")


# ============================================================================
# TAB 6: REDE INTERATIVA
# ============================================================================

def render_network_tab(filtered_data):
    """
    Tab: Visualização Interativa da Rede (Refatorada para usar filtros).

    Args:
        filtered_data: Dados já filtrados pela sidebar
    """
    from dashboard.components import render_cosmograph
    import json

    st.header("Redes Interativas")
    st.caption("Explore as redes competitivas olímpicas de forma interativa")

    # Info sobre seleção atual
    if 'metadata' in filtered_data and not filtered_data['metadata'].empty:
        n_redes = filtered_data['metadata']['network_id'].nunique()
        n_atletas = len(filtered_data['athletes'])
        st.info(f"📊 **{n_atletas:,} atletas** de **{n_redes} redes** disponíveis após filtros")

    st.markdown("---")

    # ========================================================================
    # VERIFICAR SE HÁ METADATA E REDES DISPONÍVEIS
    # ========================================================================

    if 'metadata' not in filtered_data or filtered_data['metadata'].empty:
        st.warning("⚠️ Metadata não disponível. Certifique-se de que a mineração completa foi executada.")
        st.info("Execute: `python main/src/analysis/12_mine_all_networks.py`")
        return

    metadata = filtered_data['metadata']

    if len(metadata) == 0:
        st.warning("⚠️ Nenhuma rede disponível com os filtros selecionados. Ajuste os filtros na sidebar.")
        return

    # ========================================================================
    # GERAR LISTA DINÂMICA DE REDES (baseada nos filtros)
    # ========================================================================

    st.subheader("1. Selecione a Rede")

    # Criar opções de rede a partir da metadata filtrada
    network_options = []
    for _, row in metadata.iterrows():
        label = f"{row['sport'].title()} {row['gender']} - {row['event_name']}"
        network_options.append({
            'network_id': row['network_id'],
            'label': label,
            'sport': row['sport'],
            'gender': row['gender'],
            'event_name': row['event_name'],
            'n_athletes': row['n_athletes'],
            'n_edges': row['n_edges']
        })

    # Ordenar por esporte, depois por gênero, depois por evento
    network_options = sorted(network_options, key=lambda x: (x['sport'], x['gender'], x['event_name']))

    if not network_options:
        st.warning("Nenhuma rede disponível após filtros")
        return

    network_labels = [net["label"] for net in network_options]
    selected_network_label = st.selectbox(
        "Escolha uma rede para visualizar:",
        network_labels,
        help="Redes disponíveis com base nos filtros selecionados na sidebar"
    )

    # Encontrar a rede selecionada
    selected_network = next(net for net in network_options if net["label"] == selected_network_label)

    # ========================================================================
    # CARREGAR DADOS DA REDE SELECIONADA (usa filtered_data)
    # ========================================================================

    network_id = selected_network['network_id']

    # Filtrar atletas da rede selecionada
    df_athletes = filtered_data['athletes'][
        filtered_data['athletes']['network_id'] == network_id
    ].copy()

    if df_athletes.empty:
        st.error(f"⚠️ Nenhum atleta encontrado para a rede selecionada (network_id={network_id})")
        return

    # Tentar carregar arestas (edges) se disponível
    # Nota: edges podem não estar filtrados por network_id, então vamos filtrar localmente
    if 'edges' in filtered_data and not filtered_data['edges'].empty:
        # Assumindo que edges tem network_id ou podemos filtrar por source/target que estão em df_athletes
        df_edges = filtered_data['edges']
        # Filtrar edges cujos source e target estão em df_athletes
        # Usar 'name' (coluna renomeada de 'athlete_name')
        athlete_names = set(df_athletes['name'].unique())
        # Edges usa 'source_name' e 'target_name'
        df_edges = df_edges[
            (df_edges['source_name'].isin(athlete_names)) &
            (df_edges['target_name'].isin(athlete_names))
        ].copy()
    else:
        # Sem dados de edges, criar DataFrame vazio
        df_edges = pd.DataFrame()
        st.warning("⚠️ Dados de arestas (edges) não disponíveis para esta rede")

    # Estatísticas básicas da rede
    num_nodes_total = len(df_athletes)
    num_edges_total = len(df_edges) if not df_edges.empty else 0

    # Obter modularidade e número de comunidades da metadata
    network_row = metadata[metadata['network_id'] == network_id].iloc[0]
    modularity = network_row.get('modularity', None)
    num_communities_from_metadata = network_row.get('n_communities', 0)

    # Usar número de comunidades da metadata, fallback para contagem no dataframe
    num_communities = num_communities_from_metadata if num_communities_from_metadata > 0 else (
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
    show_labels = True  # Mostrar nomes dos atletas por padrão
    edge_opacity = 0.4  # Aumentado para melhor visualização das setas
    node_scale_range = (5, 30)
    physics_enabled = True  # Ativar física Force Atlas por padrão
    show_arrows = True  # Mostrar setas direcionais por padrão
    height = 800
    gravitational_constant = -1200  # Mais repulsão = mais espalhamento
    spring_length = 200  # Distância maior entre nós conectados
    spring_constant = 0.02  # Molas mais fracas = layout mais solto
    
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

    # Remover duplicatas (usar name+noc para garantir unicidade)
    antes_drop = len(df_filtered)
    df_filtered = df_filtered.drop_duplicates(subset=['name', 'noc'], keep='first')
    depois_drop = len(df_filtered)

    # Criar IDs únicos baseados no index
    df_filtered = df_filtered.reset_index(drop=True)
    df_filtered['temp_id'] = df_filtered.index
    selected_ids = set(df_filtered['temp_id'].astype(str))

    # Também criar set de nomes para filtrar edges
    selected_names = set(df_filtered['name'].unique())

    # Criar mapeamento name → temp_id para construir links
    name_to_id = dict(zip(df_filtered['name'], df_filtered['temp_id'].astype(str)))

    # Preparar nós com informações completas para tooltip
    nodes = []
    for _, row in df_filtered.iterrows():
        node_id = str(row['temp_id'])

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
        athlete_name = row.get('name', 'N/A')

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
            'label': str(row.get('name', f"Atleta {node_id}")),  # Garantir que seja string
            'size': size,
            'group': group,
            'tooltip_data': tooltip_data
        })


    # Verificar se McLOUGHLIN está nos nodes
    mcl_in_nodes = any('McLOUGHLIN' in str(n.get('label', '')).upper() for n in nodes)

    # ========================================================================
    # PREPARAR DADOS DAS ARESTAS
    # ========================================================================

    links = []

    # Filtrar arestas (usar source_name e target_name)
    df_edges_filtered = df_edges[
        df_edges['source_name'].isin(selected_names) &
        df_edges['target_name'].isin(selected_names)
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
        # Mapear source_name e target_name para temp_ids
        source_id = name_to_id.get(edge['source_name'])
        target_id = name_to_id.get(edge['target_name'])

        # Só adicionar se ambos os nós existem
        if source_id is not None and target_id is not None:
            links.append({
                'source': source_id,
                'target': target_id,
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
    mcl_before_render = any('McLOUGHLIN' in str(n.get('label', '')).upper() for n in nodes)

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
        show_arrows=show_arrows,
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


# ==============================================================================
# FUNÇÃO DESABILITADA: render_temporal_tab
# ==============================================================================
# MOTIVO: Incompatível com modelagem per-event atual
#
# A aba "Evolução Temporal" foi removida porque a modelagem per-event agrega
# todos os anos de um evento em uma única rede (ex: "Athletics_Mens_10000m"
# contém atletas de 1912-2021).
#
# Para análise temporal válida seria necessário criar redes separadas por ano
# (ex: "Athletics_Mens_10000m_1992", "Athletics_Mens_10000m_1996", etc.),
# recalcular métricas para cada ano, e então comparar evolução.
#
# Removido em: 2026-02-07
# ==============================================================================

def render_temporal_tab(data):
    """Tab: Evolução Temporal. [DESABILITADA - Ver comentário acima]"""
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
    show_data_context(data)
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

    # Verificar se temos dados temporais REAIS (não apenas coluna year = 0)
    has_temporal_data = False
    if 'year' in data['athletes'].columns:
        valid_years = data['athletes'][data['athletes']['year'] > 0]
        has_temporal_data = len(valid_years) > 0

    if not has_temporal_data:
        st.error("❌ **Dados temporais não disponíveis**")
        st.warning("""
        **Por quê?**

        Os dados filtrados não contêm informação temporal válida (coluna `year` ausente ou = 0).

        **Possíveis causas:**
        - Apenas dados antigos (12 casos agregados) selecionados nos filtros
        - Dados sem informação de ano nas redes originais

        **Para análise temporal você precisa:**
        - Selecionar redes per-event (149 redes) nos filtros da barra lateral
        - Escolher esportes que tenham dados temporais (athletics, swimming, etc.)

        Esta aba permanece no dashboard para referência futura, caso dados temporais sejam adicionados.
        """)

        st.info("💡 **Sugestão:** Use as outras abas para análise estrutural das redes (sem dimensão temporal).")
        return

    # ========================================
    # SELETOR DE EVENTO ESPECÍFICO
    # ========================================

    st.markdown("---")
    render_subsection("⚙️ Configuração de Análise Temporal", "Selecione o evento para visualizar sua evolução ao longo do tempo")

    # Filtrar apenas dados com year > 0 (ignorar dados antigos sem info temporal)
    df_all = data['athletes'][data['athletes']['year'] > 0].copy()

    if len(df_all) == 0:
        st.error("❌ Nenhum dado temporal disponível após filtros aplicados.")
        return

    # Obter lista de eventos disponíveis
    sex_col = 'sex' if 'sex' in df_all.columns else 'gender'
    df_all['event_full'] = df_all['sport'] + ' - ' + df_all['event_name'] + ' (' + df_all[sex_col] + ')'
    available_events = sorted(df_all['event_full'].unique())

    # Contar anos por evento
    event_year_counts = df_all.groupby('event_full')['year'].nunique().to_dict()

    # Opções de seleção
    col_sel1, col_sel2 = st.columns([3, 1])

    with col_sel1:
        selected_event_full = st.selectbox(
            "Selecione um evento específico",
            options=available_events,
            help="Escolha qual evento você quer analisar temporalmente. Cada evento é uma rede independente."
        )

    with col_sel2:
        n_years = event_year_counts.get(selected_event_full, 0)
        st.metric(
            "Edições",
            f"{n_years}",
            help="Número de anos olímpicos com dados para este evento"
        )

    # Extrair sport, event_name, sex do selecionado
    parts = selected_event_full.split(' - ')
    selected_sport = parts[0]
    event_and_sex = parts[1]
    selected_sex = event_and_sex[-2] if event_and_sex.endswith('(M)') or event_and_sex.endswith('(F)') else None
    selected_event = event_and_sex.rsplit(' (', 1)[0]

    # Filtrar dados do evento selecionado
    df = df_all[
        (df_all['sport'] == selected_sport) &
        (df_all['event_name'] == selected_event) &
        (df_all[sex_col] == selected_sex)
    ].copy()

    if len(df) == 0:
        st.error(f"❌ Nenhum dado encontrado para {selected_event_full}")
        return

    st.info(f"📊 Analisando **{len(df):,} atletas** em **{df['year'].nunique()} edições** de **{selected_event_full}**")

    # ========================================
    # PROCESSAR DADOS TEMPORAIS
    # ========================================

    with st.spinner("Processando análise temporal..."):
        # Preparar dicionário de agregação com colunas disponíveis
        count_col = 'name' if 'name' in df.columns else ('noc' if 'noc' in df.columns else df.columns[0])
        agg_dict = {count_col: 'count'}

        if 'original_pagerank' in df.columns:
            agg_dict['original_pagerank'] = 'mean'
        if 'original_betweenness_centrality' in df.columns:
            agg_dict['original_betweenness_centrality'] = 'mean'
        if 'original_total_degree' in df.columns:
            agg_dict['original_total_degree'] = 'mean'

        # Agrupar por ano (já filtrado para evento específico)
        df_by_year = df.groupby('year').agg(agg_dict).reset_index()

        # Renomear colunas
        column_mapping = {
            count_col: 'num_athletes',
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
        # Contar atletas únicos por name (ou name+noc se disponível)
        if 'name' in df.columns and 'noc' in df.columns:
            total_athletes = df.groupby(['name', 'noc']).ngroups
        elif 'name' in df.columns:
            total_athletes = df['name'].nunique()
        else:
            total_athletes = len(df)

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
        # Preparar agregação por esporte (usar 'name' para contar)
        count_col = 'name' if 'name' in df.columns else df.columns[0]
        agg_dict_sports = {count_col: 'count'}
        if 'original_pagerank' in df.columns:
            agg_dict_sports['original_pagerank'] = 'mean'

        df_sports = df[df['sport'].isin(selected_sports_temporal)].groupby(['year', 'sport']).agg(agg_dict_sports).reset_index()

        # Renomear colunas
        column_mapping_sports = {
            count_col: 'num_athletes',
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

    # Exibir resumo dos dados filtrados na sidebar
    render_filter_summary(filtered_data)

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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Visão Geral",
        "Comunidades",
        "Atletas-Ponte",
        "Rivalidades",
        "Rankings",
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
        render_network_tab(filtered_data)


if __name__ == '__main__':
    main()
