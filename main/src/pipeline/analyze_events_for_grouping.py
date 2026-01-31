#!/usr/bin/env python3
"""
Análise de eventos para propor agrupamentos em super-eventos.
Agrupa eventos por características técnicas/físicas similares.
"""

import pandas as pd
import json

# Carregar dados
df = pd.read_csv('../../data/athlete_events.csv')
df = df[df['Sport'].isin(['Swimming', 'Basketball', 'Football', 'Athletics', 'Judo', 'Boxing'])]
df = df[df['Medal'].notna()]

# Analisar eventos por esporte
sports = ['Swimming', 'Athletics', 'Judo', 'Boxing']

print("="*80)
print("ANÁLISE DE EVENTOS PARA AGRUPAMENTO")
print("="*80)

for sport in sports:
    sport_df = df[df['Sport'] == sport]
    events = sorted(sport_df['Event'].unique())

    print(f"\n{'='*80}")
    print(f"{sport.upper()} - {len(events)} eventos únicos")
    print("="*80)

    for event in events:
        count = len(sport_df[sport_df['Event'] == event])
        print(f"  {event:<70} ({count:>4} medalhas)")

# Propor agrupamentos
print("\n\n" + "="*80)
print("PROPOSTA DE AGRUPAMENTO EM SUPER-EVENTOS")
print("="*80)

super_events = {
    'Swimming': {
        'Freestyle_Sprint': {
            'description': 'Nado livre - Velocidade (50m, 100m)',
            'keywords': ['50', '100', 'Freestyle', 'Free', 'Yard'],
            'exclude': ['200', '400', '800', '1500', '1,', 'Relay', 'Team', 'Medley']
        },
        'Freestyle_Middle': {
            'description': 'Nado livre - Média distância (200m, 400m)',
            'keywords': ['200', '400', 'Freestyle', 'Free'],
            'exclude': ['Relay', 'Team', 'Medley']
        },
        'Freestyle_Distance': {
            'description': 'Nado livre - Longa distância (800m, 1500m+)',
            'keywords': ['800', '1500', '1,', 'Mile', 'kilometres', 'Freestyle', 'Free'],
            'exclude': ['Relay', 'Team']
        },
        'Backstroke': {
            'description': 'Nado costas (todas as distâncias)',
            'keywords': ['Backstroke', 'Back'],
            'exclude': ['Relay', 'Medley']
        },
        'Breaststroke': {
            'description': 'Nado peito (todas as distâncias)',
            'keywords': ['Breaststroke', 'Breast'],
            'exclude': ['Relay', 'Medley']
        },
        'Butterfly': {
            'description': 'Nado borboleta (todas as distâncias)',
            'keywords': ['Butterfly'],
            'exclude': ['Relay', 'Medley']
        },
        'Medley': {
            'description': 'Medley individual (todas as distâncias)',
            'keywords': ['Medley'],
            'exclude': ['Relay', 'Team']
        },
        'Relays': {
            'description': 'Revezamentos (todos os tipos)',
            'keywords': ['Relay', 'Team'],
            'exclude': []
        },
        'Other': {
            'description': 'Eventos históricos diversos',
            'keywords': ['Obstacle', 'Underwater', 'Plunge', 'Sailors'],
            'exclude': []
        }
    },
    'Athletics': {
        'Sprints': {
            'description': 'Velocidade pura (100m, 200m)',
            'keywords': ['100', '200'],
            'exclude': ['Hurdles', 'Relay', '1,', '2,', '10,000', 'Walk', 'Steeplechase', 'Team']
        },
        'Middle_Distance': {
            'description': 'Média distância (400m, 800m, 1500m)',
            'keywords': ['400', '800', '1,500', '1500', '1,600'],
            'exclude': ['Hurdles', 'Relay', 'Walk', 'Steeplechase', 'Team']
        },
        'Long_Distance': {
            'description': 'Longa distância (5000m, 10000m, Maratona)',
            'keywords': ['5,000', '5000', '10,000', '10000', 'Marathon', 'Cross'],
            'exclude': ['Walk', 'Relay', 'Team']
        },
        'Hurdles': {
            'description': 'Barreiras (100m, 110m, 400m)',
            'keywords': ['Hurdles'],
            'exclude': ['Relay', 'Team']
        },
        'Steeplechase': {
            'description': 'Steeplechase (obstáculos)',
            'keywords': ['Steeplechase'],
            'exclude': []
        },
        'Race_Walk': {
            'description': 'Marcha atlética (todas as distâncias)',
            'keywords': ['Walk'],
            'exclude': ['Relay']
        },
        'High_Jump': {
            'description': 'Salto em altura',
            'keywords': ['High Jump'],
            'exclude': []
        },
        'Pole_Vault': {
            'description': 'Salto com vara',
            'keywords': ['Pole Vault'],
            'exclude': []
        },
        'Long_Jump': {
            'description': 'Salto em distância',
            'keywords': ['Long Jump'],
            'exclude': ['Triple']
        },
        'Triple_Jump': {
            'description': 'Salto triplo',
            'keywords': ['Triple Jump'],
            'exclude': []
        },
        'Shot_Put': {
            'description': 'Arremesso de peso',
            'keywords': ['Shot Put'],
            'exclude': []
        },
        'Discus': {
            'description': 'Arremesso de disco',
            'keywords': ['Discus'],
            'exclude': []
        },
        'Hammer': {
            'description': 'Arremesso de martelo',
            'keywords': ['Hammer'],
            'exclude': []
        },
        'Javelin': {
            'description': 'Arremesso de dardo',
            'keywords': ['Javelin'],
            'exclude': []
        },
        'Combined_Events': {
            'description': 'Eventos combinados (Decatlo, Heptatlo, Pentatlo)',
            'keywords': ['Decathlon', 'Heptathlon', 'Pentathlon'],
            'exclude': []
        },
        'Relays': {
            'description': 'Revezamentos (4x100m, 4x400m, etc.)',
            'keywords': ['Relay'],
            'exclude': []
        }
    },
    'Judo': {
        'Lightweight': {
            'description': 'Categorias leves (-60kg, -66kg, -73kg para M; -48kg, -52kg, -57kg para F)',
            'keywords': ['-48', '-52', '-57', '-60', '-66', '-73', 'Extra-Lightweight', 'Half-Lightweight', 'Lightweight'],
            'exclude': []
        },
        'Middleweight': {
            'description': 'Categorias médias (-81kg, -90kg para M; -63kg, -70kg para F)',
            'keywords': ['-63', '-70', '-81', '-90', 'Half-Middleweight', 'Middleweight'],
            'exclude': ['Heavyweight']
        },
        'Heavyweight': {
            'description': 'Categorias pesadas (-100kg, +100kg para M; -78kg, +78kg para F)',
            'keywords': ['-78', '-100', '+78', '+100', 'Heavyweight', 'Half-Heavyweight'],
            'exclude': []
        },
        'Open': {
            'description': 'Categoria aberta (todas as categorias)',
            'keywords': ['Open'],
            'exclude': []
        }
    },
    'Boxing': {
        'Flyweight': {
            'description': 'Pesos mosca e leves (-52kg)',
            'keywords': ['Fly', '-48', '-51', '-52'],
            'exclude': []
        },
        'Lightweight': {
            'description': 'Pesos leves (-60kg, -63kg)',
            'keywords': ['Light', 'Feather', '-54', '-57', '-60', '-63'],
            'exclude': ['Welter', 'Middle', 'Heavy']
        },
        'Welterweight': {
            'description': 'Pesos meio-médios (-69kg)',
            'keywords': ['Welter', '-64', '-69'],
            'exclude': []
        },
        'Middleweight': {
            'description': 'Pesos médios (-75kg, -81kg)',
            'keywords': ['Middle', '-69', '-75', '-81'],
            'exclude': ['Light', 'Welter', 'Heavy']
        },
        'Heavyweight': {
            'description': 'Pesos pesados (+81kg)',
            'keywords': ['Heavy', '-91', '+91', 'Super'],
            'exclude': []
        }
    }
}

# Salvar proposta
output_file = '../../docs/super_events_proposal.json'
with open(output_file, 'w') as f:
    json.dump(super_events, f, indent=2)

print(f"\n\nProposta salva em: {output_file}")

# Imprimir resumo
print("\n\nRESUMO DA PROPOSTA:")
print("="*80)

for sport, groups in super_events.items():
    print(f"\n{sport}:")
    for group_name, config in groups.items():
        print(f"  - {group_name}: {config['description']}")

print("\n\nVANTAGENS:")
print("- Conecta atletas de eventos tecnicamente similares")
print("- Reduz fragmentação drasticamente")
print("- Mantém coerência física/técnica (velocistas juntos, saltadores juntos)")
print("- Permite análise de 'versatilidade' (atletas que competem em múltiplos grupos)")

print("\nDESVANTAGENS:")
print("- Perde granularidade (100m vs 200m são tratados igual)")
print("- Decisões de agrupamento são subjetivas")
print("- Pode misturar atletas que nunca competiram juntos")

print("\n" + "="*80)
