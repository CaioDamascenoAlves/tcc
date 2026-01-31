#!/usr/bin/env python3
"""
Análise de eventos icônicos usando dados limpos e normalizados.
"""

import pandas as pd
import numpy as np

# Carregar dados limpos
print("Carregando dados limpos...")
df = pd.read_csv('../../data/athlete_events_cleaned.csv')
df_medalists = df[df['Medal'].notna()].copy()

print(f"Total de medalhistas: {len(df_medalists):,}")
print(f"Atletas únicos: {df_medalists['ID'].nunique():,}")
print(f"Anos: {df_medalists['Year'].min()} - {df_medalists['Year'].max()}")

print("\n" + "="*120)
print("ANÁLISE DE EVENTOS ICÔNICOS (baseado em dados limpos)")
print("="*120)

results = []

for sport in df['Sport'].unique():
    print(f"\n{'='*120}")
    print(f"{sport.upper()}")
    print("="*120)

    sport_df = df_medalists[df_medalists['Sport'] == sport]

    # Análise por evento normalizado
    event_stats = sport_df.groupby('Event_Normalized').agg({
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

    # Calcular "Iconic Score"
    max_editions = event_stats['Num_Editions'].max()
    max_countries = event_stats['Countries'].max()
    max_athletes = event_stats['Athletes'].max()
    max_longevity = event_stats['Longevity'].max()

    event_stats['Iconic_Score'] = (
        0.35 * (event_stats['Num_Editions'] / max_editions) +
        0.15 * (event_stats['Countries'] / max_countries) +
        0.15 * (event_stats['Athletes'] / max_athletes) +
        0.35 * (event_stats['Longevity'] / max_longevity if max_longevity > 0 else 0)
    )

    # Ordenar por Iconic Score
    event_stats = event_stats.sort_values('Iconic_Score', ascending=False)
    event_stats = event_stats.drop('Year_info', axis=1)

    # Mostrar top 10
    print(f"\n{'Event':<60} {'Edições':<10} {'Anos':<20} {'Países':<10} {'Atletas':<10} {'Score':<8}")
    print("-" * 120)

    for idx, row in event_stats.head(15).iterrows():
        years_range = f"{row['First_Year']}-{row['Last_Year']}"
        event_short = row['Event'][:58]
        print(f"{event_short:<60} {row['Num_Editions']:<10} {years_range:<20} {row['Countries']:<10} {row['Athletes']:<10} {row['Iconic_Score']:.3f}")

        # Guardar para relatório
        results.append({
            'Sport': sport,
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
df_results = df_results.sort_values(['Sport', 'Iconic_Score'], ascending=[True, False])
df_results.to_csv('../../results/iconic_events_analysis.csv', index=False)

print("\n\n" + "="*120)
print("RESUMO: TOP 5 EVENTOS POR ESPORTE (Iconic Score)")
print("="*120)

for sport in sorted(df['Sport'].unique()):
    print(f"\n{sport}:")
    sport_results = df_results[df_results['Sport'] == sport].head(5)

    for idx, row in sport_results.iterrows():
        print(f"  {row['Iconic_Score']:.3f} - {row['Event']:<50} ({row['Num_Editions']:>2} edições, {row['First_Year']}-{row['Last_Year']})")

print(f"\n\nRelatório completo salvo em: ../../results/iconic_events_analysis.csv")
