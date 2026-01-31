#!/usr/bin/env python3
"""
Investiga variações e inconsistências nos nomes de eventos.
Identifica eventos para normalização.
"""

import pandas as pd
import re
from collections import defaultdict

# Carregar dados
print("Carregando dados...")
df = pd.read_csv('../../data/athlete_events.csv')

# Filtrar esportes
selected_sports = ['Swimming', 'Basketball', 'Football', 'Athletics', 'Judo', 'Boxing']
df = df[df['Sport'].isin(selected_sports)]

print("="*100)
print("INVESTIGAÇÃO DE NOMES DE EVENTOS")
print("="*100)

for sport in selected_sports:
    print(f"\n{'='*100}")
    print(f"{sport.upper()}")
    print("="*100)

    sport_df = df[df['Sport'] == sport]

    # Listar todos eventos únicos com info de anos
    events_info = sport_df.groupby('Event').agg({
        'Year': lambda x: (x.min(), x.max(), x.nunique()),
        'Sex': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown',
        'Medal': lambda x: x.notna().sum()
    }).reset_index()

    events_info.columns = ['Event', 'Year_Info', 'Sex', 'Medals']
    events_info['First_Year'] = events_info['Year_Info'].apply(lambda x: x[0])
    events_info['Last_Year'] = events_info['Year_Info'].apply(lambda x: x[1])
    events_info['Num_Editions'] = events_info['Year_Info'].apply(lambda x: x[2])
    events_info = events_info.drop('Year_Info', axis=1)
    events_info = events_info.sort_values(['Sex', 'First_Year', 'Event'])

    print(f"\nTotal de eventos únicos: {len(events_info)}")
    print(f"\n{'Event':<70} {'Sexo':<6} {'Anos':<20} {'Edições':<10} {'Medalhas':<10}")
    print("-"*100)

    for _, row in events_info.iterrows():
        years_range = f"{row['First_Year']}-{row['Last_Year']}"
        event_name = row['Event'][:68]

        # Destacar eventos suspeitos
        suspicious = ''
        if 'yard' in event_name.lower():
            suspicious = ' [YARDS]'
        elif 'metre' in event_name.lower() and 'meters' not in event_name.lower():
            suspicious = ' [METRE]'
        elif any(word in event_name.lower() for word in ['plunge', 'underwater', 'obstacle', 'sailors', 'soldiers']):
            suspicious = ' [HISTÓRICO]'
        elif row['Last_Year'] < 1950:
            suspicious = ' [ANTIGO]'

        print(f"{event_name:<70} {row['Sex']:<6} {years_range:<20} {row['Num_Editions']:<10} {row['Medals']:<10}{suspicious}")

print("\n\n" + "="*100)
print("CATEGORIAS DE PROBLEMAS IDENTIFICADOS")
print("="*100)

print("""
1. UNIDADES ANTIGAS:
   - 'yards' vs 'metres' vs 'meters' vs 'm'
   - '100 metres' vs '100m'

2. EVENTOS HISTÓRICOS EXTINTOS:
   - Plunge for Distance
   - Underwater Swimming
   - Obstacle Race
   - Events específicos para marinheiros/soldados

3. VARIAÇÕES DE NOMENCLATURA:
   - "Men's" vs sem prefixo
   - "100 metres Freestyle" vs "100m Freestyle"
   - Inconsistências de capitalização

4. EVENTOS QUE MUDARAM:
   - Categorias de peso que mudaram de faixa ao longo do tempo
   - Distâncias que mudaram (1500m vs 1500 metres vs Mile)

PRÓXIMO PASSO:
Criar um mapeamento de normalização manual/semi-automático.
""")
