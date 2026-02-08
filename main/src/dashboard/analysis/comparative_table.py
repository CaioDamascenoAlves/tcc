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
    Gera métricas comparativas POR EVENTO (não por esporte agregado).
    
    RIGOR ACADÊMICO: Cada linha = uma rede independente (evento específico).
    Não agregamos eventos diferentes - cada um tem suas métricas próprias.

    Args:
        data: Dicionário com DataFrames (metadata, athletes, etc.)

    Returns:
        DataFrame com métricas por EVENTO individual
    """
    # Usar metadata como fonte principal (149 redes)
    metadata_df = data.get('metadata', pd.DataFrame())
    
    if metadata_df.empty:
        st.warning("⚠️ Metadata não disponível. Tabela comparativa desabilitada.")
        return pd.DataFrame()
    
    # Dados de atletas (para métricas complementares)
    athletes_df = data.get('athletes', pd.DataFrame())
    
    metrics = []
    
    for _, network in metadata_df.iterrows():
        network_id = network['network_id']
        sport = network['sport']
        gender = network.get('gender', network.get('sex', 'N/A'))
        event_name = network['event_name']
        
        # Identificador único do evento
        event_label = f"{sport.title()} {gender.upper()} - {event_name}"
        
        # === FILTRAR ATHLETES PARA ESTA REDE (usado em múltiplos lugares) ===
        network_athletes = athletes_df[athletes_df['network_id'] == network_id] if not athletes_df.empty else pd.DataFrame()
        
        # === ESTRUTURA DA REDE (direto do metadata) ===
        num_athletes = network.get('n_athletes', 0)
        num_edges = network.get('n_edges', 0)
        density = network.get('density', 0) * 100  # Converter para %
        num_communities = network.get('n_communities', 0)
        modularity = network.get('modularity', 0)
        
        # === CENTRALIDADE (do athletes_df já filtrado acima) ===
        if not network_athletes.empty and len(network_athletes) > 0:
            # PageRank médio
            avg_pagerank = network_athletes['original_pagerank'].mean() if 'original_pagerank' in network_athletes.columns else 0
            
            # Concentração Top 10%
            if 'original_pagerank' in network_athletes.columns:
                top_10_pct = max(1, int(len(network_athletes) * 0.1))
                top_pagerank_sum = network_athletes.nlargest(top_10_pct, 'original_pagerank')['original_pagerank'].sum()
                total_pagerank_sum = network_athletes['original_pagerank'].sum()
                concentration = (top_pagerank_sum / total_pagerank_sum * 100) if total_pagerank_sum > 0 else 0
            else:
                concentration = 0
            
            # Betweenness médio
            avg_betweenness = network_athletes['original_betweenness_centrality'].mean() if 'original_betweenness_centrality' in network_athletes.columns else 0
            
            # Atletas-ponte
            bridges = MetricsCalculator.identify_bridge_athletes(network_athletes)
            num_bridges = len(bridges)
            pct_bridges = (num_bridges / len(network_athletes) * 100) if len(network_athletes) > 0 else 0
        else:
            avg_pagerank = 0
            concentration = 0
            avg_betweenness = 0
            num_bridges = 0
            pct_bridges = 0
        
        # === CLASSIFICAÇÃO QUALITATIVA ===
        # Modularidade
        modularity_label = (
            "Alta" if modularity > 0.6 else
            "Média" if modularity > 0.3 else
            "Baixa"
        )
        
        # Densidade
        density_label = (
            "Densa" if density > 30 else
            "Moderada" if density > 10 else
            "Esparsa"
        )
        
        # Compilar métricas
        metrics.append({
            'Evento': event_label,
            'Esporte': sport.title(),
            'Sexo': gender.upper(),
            
            # Estrutura
            'Atletas': int(num_athletes),
            'Arestas': int(num_edges),
            'Densidade': round(density, 2),
            'Classe Densidade': density_label,
            
            # Comunidades
            'Comunidades': int(num_communities),
            'Modularidade': round(modularity, 3),
            'Classe Modularidade': modularity_label,
            
            # Centralidade
            'PageRank Médio': round(avg_pagerank, 6),
            'Concentração Top10%': round(concentration, 1),
            'Betweenness Médio': round(avg_betweenness, 6),
            
            # Bridges
            'Bridges': int(num_bridges),
            'Bridges %': round(pct_bridges, 1),
        })
    
    df = pd.DataFrame(metrics)
    
    # Ordenar por esporte, depois sexo, depois evento
    df = df.sort_values(['Esporte', 'Sexo', 'Evento'])
    
    return df


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
    Renderiza tabela comparativa POR EVENTO (149 redes independentes).
    
    RIGOR ACADÊMICO: Mostra cada rede como linha individual.
    Cada evento (ex: "Athletics M - 100m") é tratado separadamente.

    Args:
        data: Dicionário com DataFrames (metadata, athletes, etc.)
    """
    st.subheader("Tabela Comparativa por Evento")
    st.caption("Cada linha representa uma rede independente (evento específico em modalidade específica)")

    # Warning metodológico
    st.warning("""
    ⚠️ **Metodologia per-event:** Cada linha é uma rede INDEPENDENTE.
    
    - Não agregamos eventos diferentes
    - Cada evento tem suas próprias métricas de centralidade
    - PageRank/Betweenness não são comparáveis entre linhas diferentes
    - **Comparações válidas:** Densidade, Modularidade, Número de comunidades
    """)

    # Gerar métricas
    df = generate_comparative_metrics(data)

    # Botão de download
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(df)
    st.download_button(
        label="📥 Download Tabela Completa (CSV)",
        data=csv,
        file_name="tabela_comparativa_eventos.csv",
        mime="text/csv",
        help="Exportar tabela comparativa completa com todos os eventos"
    )

    if len(df) == 0:
        st.warning("Nenhum dado disponível para comparação.")
        return

    # Filtros adicionais
    st.markdown("### Filtros de Visualização")
    col1, col2 = st.columns(2)
    
    with col1:
        sports_filter = st.multiselect(
            "Esportes",
            options=sorted(df['Esporte'].unique()),
            default=[],
            help="Filtrar por esportes específicos (vazio = todos)"
        )
    
    with col2:
        sex_filter = st.multiselect(
            "Sexo",
            options=sorted(df['Sexo'].unique()),
            default=[],
            help="Filtrar por sexo (vazio = todos)"
        )
    
    # Aplicar filtros
    df_filtered = df.copy()
    if sports_filter:
        df_filtered = df_filtered[df_filtered['Esporte'].isin(sports_filter)]
    if sex_filter:
        df_filtered = df_filtered[df_filtered['Sexo'].isin(sex_filter)]
    
    st.info(f"Mostrando {len(df_filtered)} de {len(df)} redes")

    # Tabs para diferentes visualizações
    tab1, tab2, tab3 = st.tabs([
        "Tabela Completa",
        "Estrutura da Rede",
        "Estatísticas Resumidas"
    ])

    with tab1:
        st.markdown("**Todos os Eventos e Métricas**")
        
        # Mostrar tabela paginada
        st.dataframe(
            df_filtered,
            use_container_width=True,
            height=600,
            column_config={
                "Evento": st.column_config.TextColumn("Evento", width="large"),
                "Densidade": st.column_config.NumberColumn("Densidade (%)", format="%.2f%%"),
                "Modularidade": st.column_config.NumberColumn("Modularidade", format="%.3f"),
                "PageRank Médio": st.column_config.NumberColumn("PageRank Médio", format="%.6f"),
                "Concentração Top10%": st.column_config.NumberColumn("Conc. Top10%", format="%.1f%%"),
                "Bridges %": st.column_config.NumberColumn("Bridges %", format="%.1f%%"),
            }
        )

    with tab2:
        st.markdown("**Métricas Estruturais (Comparáveis Entre Eventos)**")
        
        # Selecionar apenas métricas estruturais válidas
        structural_cols = ['Evento', 'Esporte', 'Sexo', 'Atletas', 'Arestas', 
                          'Densidade', 'Comunidades', 'Modularidade', 'Classe Densidade', 'Classe Modularidade']
        df_structural = df_filtered[structural_cols]
        
        st.dataframe(
            df_structural,
            use_container_width=True,
            height=600,
            column_config={
                "Densidade": st.column_config.NumberColumn("Densidade (%)", format="%.2f%%"),
                "Modularidade": st.column_config.NumberColumn("Modularidade", format="%.3f"),
            }
        )
        
        st.info("""
        Interpretação: Estas métricas são comparáveis entre eventos:
        - Densidade: percentual de conexões existentes vs possíveis
        - Modularidade: quão bem definidas estão as comunidades
        - Número de comunidades: fragmentação da rede
        """)

    with tab3:
        st.markdown("**Estatísticas Agregadas por Esporte**")
        
        # Agregar por esporte para estatísticas DESCRITIVAS (não de centralidade)
        stats_by_sport = df_filtered.groupby('Esporte').agg({
            'Atletas': ['count', 'mean', 'sum'],
            'Densidade': 'mean',
            'Modularidade': 'mean',
            'Comunidades': 'mean',
        }).round(2)
        
        stats_by_sport.columns = ['N Eventos', 'Média Atletas/Evento', 'Total Atletas', 
                                  'Densidade Média', 'Modularidade Média', 'Comunidades Média']
        stats_by_sport = stats_by_sport.reset_index()
        
        st.dataframe(stats_by_sport, use_container_width=True)
        
        st.info("""
        Nota: Esta agregação por esporte mostra padrões gerais:
        - Quantos eventos cada esporte tem nos dados
        - Médias de métricas estruturais (válido para comparação)
        - Não inclui PageRank/Betweenness (não são agregáveis)
        """)
        
        # Destaques
        st.markdown("---")
        st.markdown("**Destaques**")
        col1, col2, col3 = st.columns(3)

        with col1:
            max_density_event = df_filtered.loc[df_filtered['Densidade'].idxmax(), 'Evento']
            max_density = df_filtered['Densidade'].max()
            st.metric(
                "Rede Mais Densa",
                max_density_event,
                f"{max_density:.2f}%",
                help="Evento com maior proporção de conexões"
            )

        with col2:
            max_modularity_event = df_filtered.loc[df_filtered['Modularidade'].idxmax(), 'Evento']
            max_modularity = df_filtered['Modularidade'].max()
            st.metric(
                "Maior Modularidade",
                max_modularity_event,
                f"{max_modularity:.3f}",
                help="Comunidades mais bem definidas"
            )

        with col3:
            max_athletes_event = df_filtered.loc[df_filtered['Atletas'].idxmax(), 'Evento']
            max_athletes = df_filtered['Atletas'].max()
            st.metric(
                "Maior Rede",
                max_athletes_event,
                f"{max_athletes:,} atletas",
                help="Evento com mais atletas"
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
