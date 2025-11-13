"""
Definição de Eras Olímpicas e Eventos Históricos.

Estrutura de dados para visualização em timeline e anotações em gráficos temporais.
"""

# ============================================================================
# ERAS OLÍMPICAS
# ============================================================================

OLYMPIC_ERAS = {
    'belle_epoque': {
        'name': 'Belle Époque',
        'period': (1896, 1912),
        'color': '#D4A574',  # Dourado antigo
        'description': 'Primeiros Jogos Olímpicos da era moderna. Participação limitada, predominância europeia.',
        'characteristics': [
            'Participação limitada (~100 atletas por edição)',
            'Predominância europeia e norte-americana',
            'Esportes tradicionais (atletismo, natação, ginástica)',
            'Exclusão feminina total',
        ],
        'key_events': [
            {'year': 1896, 'event': 'Primeira Olimpíada Moderna (Atenas)', 'type': 'olympic'},
            {'year': 1900, 'event': 'Primeira participação feminina (Paris - não oficial)', 'type': 'social'},
            {'year': 1908, 'event': 'Primeira Olimpíada com natação em piscina', 'type': 'sport'},
            {'year': 1912, 'event': 'Primeira participação feminina oficial (Estocolmo)', 'type': 'social'},
        ]
    },
    'entre_guerras': {
        'name': 'Entre-Guerras',
        'period': (1920, 1936),
        'color': '#8B7355',  # Marrom sépia
        'description': 'Crescimento pós-Primeira Guerra. Expansão geográfica, mas ainda eurocêntrica.',
        'characteristics': [
            'Crescimento moderado (~300-400 atletas)',
            'Expansão geográfica (América do Sul, Ásia)',
            'Profissionalização incipiente',
            'Crescimento da participação feminina',
        ],
        'key_events': [
            {'year': 1920, 'event': 'Retorno pós-Primeira Guerra (Antuérpia)', 'type': 'olympic'},
            {'year': 1924, 'event': 'Primeira participação do Brasil', 'type': 'geographic'},
            {'year': 1928, 'event': 'Primeiro recorde mundial de atletismo feminino', 'type': 'sport'},
            {'year': 1936, 'event': 'Jogos de Berlim - Propaganda Nazista', 'type': 'political'},
        ]
    },
    'guerra_fria': {
        'name': 'Guerra Fria',
        'period': (1948, 1988),
        'color': '#8B2635',  # Vinho UFOP (tensão)
        'description': 'Polarização EUA vs URSS. Esporte como campo de batalha ideológica.',
        'characteristics': [
            'Crescimento exponencial (400 → 800+ atletas)',
            'Polarização ideológica EUA vs URSS',
            'Boicotes políticos (1980 Moscou, 1984 Los Angeles)',
            'Profissionalização de atletas em países socialistas',
            'Concentração de medalhas nos blocos',
        ],
        'key_events': [
            {'year': 1948, 'event': 'Retorno pós-Segunda Guerra (Londres)', 'type': 'olympic'},
            {'year': 1952, 'event': 'Primeira participação da URSS', 'type': 'political'},
            {'year': 1968, 'event': 'Massacre do México - Manifestações políticas', 'type': 'political'},
            {'year': 1972, 'event': 'Atentado de Munique', 'type': 'political'},
            {'year': 1980, 'event': 'Boicote dos EUA (Moscou)', 'type': 'political'},
            {'year': 1984, 'event': 'Boicote da URSS (Los Angeles)', 'type': 'political'},
        ]
    },
    'pos_guerra_fria': {
        'name': 'Pós-Guerra Fria',
        'period': (1992, 2016),
        'color': '#5A5A5A',  # Cinza UFOP (globalização)
        'description': 'Globalização e profissionalização. Democratização do acesso e diversificação geográfica.',
        'characteristics': [
            'Crescimento contínuo (800 → 900+ atletas)',
            'Globalização: participação de todos os continentes',
            'Profissionalização total (fim do amadorismo)',
            'Diversificação de esportes',
            'Avanço feminino (paridade em muitos esportes)',
            'Tecnologia e ciência do esporte',
        ],
        'key_events': [
            {'year': 1992, 'event': 'Primeira Olimpíada pós-URSS (Barcelona)', 'type': 'political'},
            {'year': 1992, 'event': 'Dream Team - Profissionais na NBA', 'type': 'sport'},
            {'year': 2000, 'event': 'Primeira Olimpíada do século XXI (Sydney)', 'type': 'olympic'},
            {'year': 2008, 'event': 'Jogos de Pequim - Ascensão da China', 'type': 'political'},
            {'year': 2012, 'event': 'Primeira Olimpíada com todas as nações enviando mulheres', 'type': 'social'},
            {'year': 2016, 'event': 'Primeira Olimpíada na América do Sul (Rio)', 'type': 'geographic'},
        ]
    }
}

# ============================================================================
# THRESHOLDS DE ANOS PARA ANOTAÇÕES
# ============================================================================

ERA_TRANSITIONS = [
    1912,  # Belle Époque → Entre-Guerras
    1936,  # Entre-Guerras → (hiato Segunda Guerra)
    1948,  # Retorno → Guerra Fria
    1988,  # Guerra Fria → Pós-Guerra Fria
]

# ============================================================================
# DADOS PARA TIMELINE VISUAL (formato timeline.js)
# ============================================================================

def get_timeline_data():
    """
    Retorna dados formatados para streamlit-timeline.

    Formato: Lista de eventos para timeline.js
    """
    events = []

    # Adicionar eventos de todas as eras
    for era_key, era_data in OLYMPIC_ERAS.items():
        # Evento de início da era
        events.append({
            'start_date': {
                'year': era_data['period'][0]
            },
            'end_date': {
                'year': era_data['period'][1]
            },
            'text': {
                'headline': era_data['name'],
                'text': f"<p>{era_data['description']}</p><ul>{''.join([f'<li>{char}</li>' for char in era_data['characteristics']])}</ul>"
            },
            'background': {
                'color': era_data['color']
            }
        })

        # Adicionar eventos-chave da era
        for key_event in era_data['key_events']:
            event_type_icons = {
                'olympic': '🏅',
                'political': '⚔️',
                'social': '👥',
                'sport': '🏆',
                'geographic': '🌍'
            }
            icon = event_type_icons.get(key_event['type'], '📌')

            events.append({
                'start_date': {
                    'year': key_event['year']
                },
                'text': {
                    'headline': f"{icon} {key_event['event']}",
                    'text': f"<p><b>Era:</b> {era_data['name']}<br><b>Ano:</b> {key_event['year']}</p>"
                }
            })

    # Ordenar por ano
    events.sort(key=lambda x: x['start_date']['year'])

    return {
        'title': {
            'text': {
                'headline': '120 Anos de História Olímpica',
                'text': '<p>Da Belle Époque à Era Profissional Moderna (1896-2016)</p>'
            }
        },
        'events': events
    }

# ============================================================================
# HELPERS PARA ANOTAÇÕES EM GRÁFICOS
# ============================================================================

def get_era_for_year(year: int) -> dict:
    """
    Retorna a era olímpica correspondente a um ano.

    Args:
        year: Ano olímpico

    Returns:
        Dicionário com dados da era, ou None se não encontrado
    """
    for era_key, era_data in OLYMPIC_ERAS.items():
        if era_data['period'][0] <= year <= era_data['period'][1]:
            return era_data

    # Caso especial: hiato da Segunda Guerra (1937-1947)
    if 1937 <= year <= 1947:
        return {
            'name': 'Segunda Guerra Mundial',
            'color': '#2A2A2A',
            'description': 'Jogos Olímpicos cancelados (1940 e 1944)'
        }

    return None


def get_era_shapes_for_plot(years_range: tuple = (1896, 2016)):
    """
    Retorna lista de shapes (retângulos) do Plotly para destacar eras em gráficos.

    Args:
        years_range: Tupla (ano_inicial, ano_final)

    Returns:
        Lista de dicts formatados para fig.update_layout(shapes=...)
    """
    shapes = []

    for era_key, era_data in OLYMPIC_ERAS.items():
        start_year, end_year = era_data['period']

        # Verificar se a era está dentro do range
        if end_year < years_range[0] or start_year > years_range[1]:
            continue

        # Ajustar limites se necessário
        start_year = max(start_year, years_range[0])
        end_year = min(end_year, years_range[1])

        shapes.append({
            'type': 'rect',
            'xref': 'x',
            'yref': 'paper',
            'x0': start_year,
            'x1': end_year,
            'y0': 0,
            'y1': 1,
            'fillcolor': era_data['color'],
            'opacity': 0.1,
            'layer': 'below',
            'line_width': 0,
        })

    return shapes


def get_era_annotations_for_plot(years_range: tuple = (1896, 2016), y_position: float = 0.98):
    """
    Retorna lista de annotations do Plotly para rotular eras em gráficos.

    Args:
        years_range: Tupla (ano_inicial, ano_final)
        y_position: Posição vertical da anotação (0-1, relativa ao papel)

    Returns:
        Lista de dicts formatados para fig.update_layout(annotations=...)
    """
    annotations = []

    for era_key, era_data in OLYMPIC_ERAS.items():
        start_year, end_year = era_data['period']

        # Verificar se a era está dentro do range
        if end_year < years_range[0] or start_year > years_range[1]:
            continue

        # Ajustar limites se necessário
        start_year = max(start_year, years_range[0])
        end_year = min(end_year, years_range[1])

        # Ponto médio da era
        mid_year = (start_year + end_year) / 2

        annotations.append({
            'x': mid_year,
            'y': y_position,
            'xref': 'x',
            'yref': 'paper',
            'text': f"<b>{era_data['name']}</b>",
            'showarrow': False,
            'font': dict(size=10, color=era_data['color']),
            'bgcolor': 'rgba(255, 255, 255, 0.8)',
            'bordercolor': era_data['color'],
            'borderwidth': 1,
            'borderpad': 4,
        })

    return annotations
