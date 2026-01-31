#!/usr/bin/env python3
"""
Análise exploratória para identificar eventos icônicos.
Critérios:
- Número de edições olímpicas (longevidade)
- Número de países participantes (alcance global)
- Número de atletas únicos (competitividade)
- Consistência ao longo do tempo
"""

import pandas as pd
import numpy as np
from collections import Counter

# Carregar dados
print("Carregando dados...")
df = pd.read_csv('../../data/athlete_events.csv')

# Filtrar esportes e medalhistas
selected_sports = ['Swimming', 'Basketball', 'Football', 'Athletics', 'Judo', 'Boxing']
df = df[df['Sport'].isin(selected_sports)]
df_medalists = df[df['Medal'].notna()].copy()

print(f"Total de registros de medalhistas: {len(df_medalists):,}")
print(f"Atletas únicos: {df_medalists['ID'].nunique():,}")
print(f"Anos cobertos: {df_medalists['Year'].min()} - {df_medalists['Year'].max()}")

print("\n" + "="*100)
print("ANÁLISE DE EVENTOS ICÔNICOS")
print("="*100)

results = []

for sport in selected_sports:
    print(f"\n{'='*100}")
    print(f"{sport.upper()}")
    print("="*100)

    sport_df = df_medalists[df_medalists['Sport'] == sport]

    # Análise por evento e sexo
    for sex in ['M', 'F']:
        sex_df = sport_df[sport_df['Sex'] == sex]

        if len(sex_df) == 0:
            continue

        print(f"\n{sex} - Masculino" if sex == 'M' else f"\n{sex} - Feminino")
        print("-" * 100)

        # Agrupar por evento
        event_stats = sex_df.groupby('Event').agg({
            'Year': lambda x: (x.nunique(), x.min(), x.max(), sorted(x.unique())),
            'NOC': 'nunique',
            'ID': 'nunique',
            'Medal': 'count'
        }).reset_index()

        event_stats.columns = ['Event', 'Year_info', 'Countries', 'Athletes', 'Medals']

        # Desempacotar info de ano
        event_stats['Num_Editions'] = event_stats['Year_info'].apply(lambda x: x[0])
        event_stats['First_Year'] = event_stats['Year_info'].apply(lambda x: x[1])
        event_stats['Last_Year'] = event_stats['Year_info'].apply(lambda x: x[2])
        event_stats['Years_List'] = event_stats['Year_info'].apply(lambda x: x[3])
        event_stats['Longevity'] = event_stats['Last_Year'] - event_stats['First_Year']

        # Calcular "Iconic Score" (métrica composta)
        # Normalizar cada métrica
        max_editions = event_stats['Num_Editions'].max()
        max_countries = event_stats['Countries'].max()
        max_athletes = event_stats['Athletes'].max()
        max_longevity = event_stats['Longevity'].max()

        event_stats['Iconic_Score'] = (
            0.3 * (event_stats['Num_Editions'] / max_editions) +
            0.2 * (event_stats['Countries'] / max_countries) +
            0.2 * (event_stats['Athletes'] / max_athletes) +
            0.3 * (event_stats['Longevity'] / max_longevity if max_longevity > 0 else 0)
        )

        # Ordenar por Iconic Score
        event_stats = event_stats.sort_values('Iconic_Score', ascending=False)

        # Remover coluna Year_info
        event_stats = event_stats.drop('Year_info', axis=1)

        # Mostrar top 10
        print(f"\n{'Event':<50} {'Edições':<10} {'Anos':<15} {'Países':<10} {'Atletas':<10} {'Score':<8}")
        print("-" * 100)

        for idx, row in event_stats.head(10).iterrows():
            years_range = f"{row['First_Year']}-{row['Last_Year']}"
            print(f"{row['Event'][:48]:<50} {row['Num_Editions']:<10} {years_range:<15} {row['Countries']:<10} {row['Athletes']:<10} {row['Iconic_Score']:.3f}")

            # Guardar para relatório final
            results.append({
                'Sport': sport,
                'Sex': sex,
                'Event': row['Event'],
                'Num_Editions': row['Num_Editions'],
                'First_Year': row['First_Year'],
                'Last_Year': row['Last_Year'],
                'Longevity': row['Longevity'],
                'Countries': row['Countries'],
                'Athletes': row['Athletes'],
                'Medals': row['Medals'],
                'Iconic_Score': row['Iconic_Score'],
                'Years_List': ','.join(map(str, row['Years_List']))
            })

# Salvar resultados
df_results = pd.DataFrame(results)
df_results = df_results.sort_values(['Sport', 'Sex', 'Iconic_Score'], ascending=[True, True, False])
df_results.to_csv('../../results/iconic_events_analysis.csv', index=False)

print("\n\n" + "="*100)
print("RESUMO: TOP 3 EVENTOS POR ESPORTE (baseado em Iconic Score)")
print("="*100)

for sport in selected_sports:
    print(f"\n{sport}:")
    sport_results = df_results[df_results['Sport'] == sport]

    for sex in ['M', 'F']:
        sex_results = sport_results[sport_results['Sex'] == sex]
        if len(sex_results) == 0:
            continue

        print(f"  {sex}:")
        for idx, row in sex_results.head(3).iterrows():
            print(f"    {row['Iconic_Score']:.3f} - {row['Event']} ({row['Num_Editions']} edições, {row['First_Year']}-{row['Last_Year']})")

print(f"\n\nRelatório completo salvo em: ../../results/iconic_events_analysis.csv")
