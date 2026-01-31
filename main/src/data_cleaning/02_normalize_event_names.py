#!/usr/bin/env python3
"""
Normaliza nomes de eventos olímpicos.
Remove eventos históricos obsoletos.
Padroniza nomenclatura.
"""

import pandas as pd
import re

# Carregar dados
print("Carregando dados...")
df = pd.read_csv('../../data/athlete_events.csv')

original_len = len(df)
print(f"Total de registros originais: {original_len:,}")

# Filtrar esportes
selected_sports = ['Swimming', 'Basketball', 'Football', 'Athletics', 'Judo', 'Boxing']
df = df[df['Sport'].isin(selected_sports)]

print(f"Registros dos 6 esportes: {len(df):,}")

print("\n" + "="*100)
print("PASSO 1: REMOVER EVENTOS HISTÓRICOS OBSOLETOS")
print("="*100)

# Eventos para EXCLUIR (históricos/obsoletos)
# IMPORTANTE: Usar strings completas para evitar falsos positivos
obsolete_patterns = [
    r'\byard\b',  # Eventos em yards (1904)
    r'\bYard\b',
    'For Sailors',
    'Underwater',
    'Obstacle',
    'Plunge',
    'Team Swimming',
    r'^Swimming Men\'s 1,200 metres',  # Distâncias estranhas específicas de natação
    r'^Swimming Men\'s 500 metres Freestyle$',
    r'^Swimming Men\'s 1,000 metres Freestyle$',
    r'^Swimming Men\'s 4,000 metres Freestyle$',
    r'^Swimming Women\'s 300 metres Freestyle$',
    'One Mile Freestyle',
    r'4 x 250 metres'  # Revezamento 4x250m (1906 único)
]

events_before = df['Event'].nunique()

for pattern in obsolete_patterns:
    removed = df[df['Event'].str.contains(pattern, case=True, na=False, regex=True)]
    if len(removed) > 0:
        print(f"Removendo eventos com padrão '{pattern}': {removed['Event'].nunique()} eventos, {len(removed)} registros")
        df = df[~df['Event'].str.contains(pattern, case=True, na=False, regex=True)]

events_after = df['Event'].nunique()
print(f"\nEventos antes: {events_before}, depois: {events_after} (removidos: {events_before - events_after})")

print("\n" + "="*100)
print("PASSO 2: NORMALIZAR NOMENCLATURA")
print("="*100)

# Criar coluna normalizada
df['Event_Normalized'] = df['Event'].copy()

# REGRA 1: Padronizar "metres" -> "m"
df['Event_Normalized'] = df['Event_Normalized'].str.replace(' metres', 'm', regex=False)
df['Event_Normalized'] = df['Event_Normalized'].str.replace(' Metres', 'm', regex=False)

# REGRA 2: Remover prefixo "Swimming/Judo/Boxing Men's/Women's"
df['Event_Normalized'] = df['Event_Normalized'].str.replace(r'^(Swimming|Judo|Boxing|Athletics)\s+(Men\'s|Women\'s)\s+', '', regex=True)

# REGRA 3: Adicionar sexo como prefixo padronizado (M/F)
def add_sex_prefix(row):
    event = row['Event_Normalized']
    sex = row['Sex']

    # Já tem prefixo M/F?
    if event.startswith("Men's ") or event.startswith("Women's "):
        event = event.replace("Men's ", "M ")
        event = event.replace("Women's ", "F ")
        return event

    # Adicionar prefixo baseado no sexo
    if sex == 'M':
        return f"M {event}"
    elif sex == 'F':
        return f"F {event}"
    else:
        return event  # Mixed events

df['Event_Normalized'] = df.apply(add_sex_prefix, axis=1)

# REGRA 4: Normalizar vírgulas em números (1,200 -> 1200, 1,500 -> 1500)
df['Event_Normalized'] = df['Event_Normalized'].str.replace(',', '', regex=False)

print("Normalizações aplicadas:")
print("  - 'metres' -> 'm'")
print("  - Removido prefixo 'Swimming/Judo/Boxing Men's/Women's'")
print("  - Adicionado prefixo 'M/F' baseado no sexo")
print("  - Removidas vírgulas de números")

print("\n" + "="*100)
print("PASSO 3: MAPEAMENTO MANUAL DE EVENTOS QUE MUDARAM")
print("="*100)

# Mapear categorias de Judô que mudaram
judo_mapping = {
    # Masculino
    'M Extra-Lightweight': 'M -60kg',
    'M Half-Lightweight': 'M -66kg',
    'M Lightweight': 'M -73kg',
    'M Half-Middleweight': 'M -81kg',
    'M Middleweight': 'M -90kg',
    'M Half-Heavyweight': 'M -100kg',
    'M Heavyweight': 'M +100kg',
    'M Open Class': 'M Open',

    # Feminino
    'F Extra-Lightweight': 'F -48kg',
    'F Half-Lightweight': 'F -52kg',
    'F Lightweight': 'F -57kg',
    'F Half-Middleweight': 'F -63kg',
    'F Middleweight': 'F -70kg',
    'F Half-Heavyweight': 'F -78kg',
    'F Heavyweight': 'F +78kg'
}

# Mapear categorias de Boxe que mudaram
boxing_mapping = {
    # Masculino
    'M Flyweight': 'M Fly (48-52kg)',
    'M Bantamweight': 'M Bantam (52-57kg)',
    'M Featherweight': 'M Feather (52-57kg)',
    'M Lightweight': 'M Light (57-63kg)',
    'M Light-Welterweight': 'M Welter (63-69kg)',
    'M Welterweight': 'M Welter (63-69kg)',
    'M Light-Middleweight': 'M Middle (69-75kg)',
    'M Middleweight': 'M Middle (69-75kg)',
    'M Light-Heavyweight': 'M Light Heavy (75-81kg)',
    'M Heavyweight': 'M Heavy (81-91kg)',
    'M Super-Heavyweight': 'M Super Heavy (+91kg)',
    'M Light-Flyweight': 'M Fly (48-52kg)',

    # Feminino
    'F Flyweight': 'F Fly (48-51kg)',
    'F Lightweight': 'F Light (57-60kg)',
    'F Middleweight': 'F Middle (69-75kg)'
}

# Aplicar mapeamentos
for old_name, new_name in judo_mapping.items():
    mask = df['Event_Normalized'] == old_name
    if mask.sum() > 0:
        print(f"Judô: '{old_name}' -> '{new_name}' ({mask.sum()} registros)")
        df.loc[mask, 'Event_Normalized'] = new_name

for old_name, new_name in boxing_mapping.items():
    mask = df['Event_Normalized'] == old_name
    if mask.sum() > 0:
        print(f"Boxe: '{old_name}' -> '{new_name}' ({mask.sum()} registros)")
        df.loc[mask, 'Event_Normalized'] = new_name

print("\n" + "="*100)
print("RESULTADO FINAL")
print("="*100)

print(f"\nRegistros originais: {original_len:,}")
print(f"Registros após limpeza: {len(df):,}")
print(f"Removidos: {original_len - len(df):,} ({(original_len - len(df)) / original_len * 100:.2f}%)")

print(f"\nEventos únicos antes da normalização: {df['Event'].nunique()}")
print(f"Eventos únicos após normalização: {df['Event_Normalized'].nunique()}")

# Salvar dataset limpo
output_path = '../../data/athlete_events_cleaned.csv'
df.to_csv(output_path, index=False)
print(f"\nDataset limpo salvo em: {output_path}")

# Salvar mapeamento de eventos
print("\n" + "="*100)
print("MAPEAMENTO DE EVENTOS (antes -> depois)")
print("="*100)

event_mapping = df[['Sport', 'Event', 'Event_Normalized']].drop_duplicates().sort_values(['Sport', 'Event'])
mapping_output = '../../data/event_normalization_mapping.csv'
event_mapping.to_csv(mapping_output, index=False)
print(f"Mapeamento salvo em: {mapping_output}")

# Mostrar algumas transformações de exemplo
print("\nExemplos de transformações:")
for sport in selected_sports:
    sport_mapping = event_mapping[event_mapping['Sport'] == sport]
    if len(sport_mapping) > 0:
        print(f"\n{sport}:")
        for _, row in sport_mapping.head(5).iterrows():
            if row['Event'] != row['Event_Normalized']:
                print(f"  {row['Event'][:50]:<50} -> {row['Event_Normalized']}")
