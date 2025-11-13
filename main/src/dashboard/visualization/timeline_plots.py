"""
Timeline visual usando Plotly - 100% responsiva.

Alternativa ao streamlit-timeline que não funciona corretamente com largura.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime


def create_olympic_timeline(olympic_eras: dict, height: int = 400) -> go.Figure:
    """
    Cria uma timeline visual LIMPA das eras olímpicas usando Plotly.

    Apenas barras coloridas das eras. Eventos ficam nos expanders abaixo.

    Args:
        olympic_eras: Dicionário com estrutura de eras olímpicas
        height: Altura do gráfico em pixels

    Returns:
        Figura Plotly
    """

    fig = go.Figure()

    # Ordenar eras por período
    eras_sorted = sorted(
        olympic_eras.items(),
        key=lambda x: x[1]['period'][0]
    )

    # Adicionar barras para cada era (APENAS BARRAS, SEM MARCADORES)
    for era_key, era_data in eras_sorted:
        start_year, end_year = era_data['period']
        duration = end_year - start_year

        # Criar texto do hover com informações completas
        hover_text = f"<b>{era_data['name']}</b><br>"
        hover_text += f"<b>Período:</b> {start_year}-{end_year} ({duration} anos)<br><br>"
        hover_text += f"<b>Descrição:</b><br>{era_data['description']}<br><br>"
        hover_text += f"<b>Características:</b><br>"
        for char in era_data['characteristics'][:3]:  # Mostrar apenas 3 primeiras
            hover_text += f"• {char}<br>"

        # Barra da era
        fig.add_trace(go.Bar(
            x=[duration],
            y=[era_data['name']],
            base=start_year,
            orientation='h',
            marker=dict(
                color=era_data['color'],
                line=dict(color='white', width=3),
                opacity=0.9
            ),
            name=era_data['name'],
            text=f"<b>{start_year}-{end_year}</b>",
            textposition='inside',
            textfont=dict(size=16, color='white', family='Arial Black'),
            hovertemplate=hover_text + "<extra></extra>",
            showlegend=False
        ))

    # Layout limpo e espaçoso
    fig.update_layout(
        title={
            'text': '<b>Linha do Tempo: 4 Eras Olímpicas (1896-2016)</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2A2A2A', 'family': 'Arial'}
        },
        xaxis=dict(
            title=dict(text='<b>Ano</b>', font=dict(size=14)),
            range=[1890, 2020],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.15)',
            dtick=20,  # Marcação a cada 20 anos para evitar poluição
            tickfont=dict(size=12),
            zeroline=False
        ),
        yaxis=dict(
            title='',
            showgrid=False,
            categoryorder='array',
            categoryarray=['Pós-Guerra Fria', 'Guerra Fria', 'Entre-Guerras', 'Belle Époque'],
            tickfont=dict(size=13, color='#2A2A2A')
        ),
        height=height,
        template='plotly_white',
        hovermode='closest',
        plot_bgcolor='rgba(250, 250, 250, 0.3)',
        bargap=0.25,
        margin=dict(l=180, r=50, t=80, b=60)
    )

    return fig


def create_events_accordion(olympic_eras: dict) -> list:
    """
    Cria uma lista de eventos para exibir como expanders no Streamlit.

    Args:
        olympic_eras: Dicionário com estrutura de eras olímpicas

    Returns:
        Lista de dicionários com eventos organizados
    """

    events_by_era = []

    for era_key, era_data in sorted(
        olympic_eras.items(),
        key=lambda x: x[1]['period'][0]
    ):
        era_info = {
            'name': era_data['name'],
            'period': f"{era_data['period'][0]}-{era_data['period'][1]}",
            'color': era_data['color'],
            'description': era_data['description'],
            'characteristics': era_data['characteristics'],
            'events': era_data['key_events']
        }
        events_by_era.append(era_info)

    return events_by_era
