"""
Validacao Profunda do Merge de Datasets
Verifica se o merge entre dataset base (1896-2016) e Tokyo 2020 foi feito corretamente
"""

import pandas as pd
import numpy as np
from pathlib import Path

project_root = Path(__file__).parent.parent

print("="*80)
print("VALIDACAO PROFUNDA DO MERGE DE DATASETS")
print("="*80)

# ============================================================================
# 1. CARREGAR DATASET FINAL
# ============================================================================
print("\n1. CARREGANDO DATASET FINAL...")
final_path = project_root / 'data' / 'athlete_events.csv'
df = pd.read_csv(final_path)

print(f"   Total de registros: {len(df):,}")
print(f"   Periodo: {df['Year'].min():.0f} - {df['Year'].max():.0f}")

# ============================================================================
# 2. VERIFICAR ANOS PRESENTES
# ============================================================================
print("\n" + "="*80)
print("2. ANALISE TEMPORAL")
print("="*80)

year_counts = df['Year'].value_counts().sort_index()
print(f"\nDistribuicao de registros por ano:")
print(f"   Anos unicos: {df['Year'].nunique()}")
print(f"   Primeiro ano: {df['Year'].min():.0f}")
print(f"   Ultimo ano: {df['Year'].max():.0f}")

# Verificar anos criticos
print(f"\nAnos criticos:")
print(f"   2016 (Rio): {len(df[df['Year'] == 2016]):,} registros")
print(f"   2020 (Tokyo planejado): {len(df[df['Year'] == 2020]):,} registros")
print(f"   2021 (Tokyo real): {len(df[df['Year'] == 2021]):,} registros")

if len(df[df['Year'] == 2020]) > 0:
    print("\n   ALERTA: Existem registros em 2020 (deveria ser 2021)")
    tokyo_2020 = df[df['Year'] == 2020]
    print(f"   Games: {tokyo_2020['Games'].unique()}")
else:
    print("\n   OK: Nenhum registro em 2020 (correto)")

if len(df[df['Year'] == 2021]) > 0:
    print(f"\n   OK: {len(df[df['Year'] == 2021]):,} registros em 2021 (Tokyo 2020)")
    tokyo_2021 = df[df['Year'] == 2021]
    print(f"   Games: {tokyo_2021['Games'].unique()}")
    print(f"   City: {tokyo_2021['City'].unique()}")
    print(f"   Season: {tokyo_2021['Season'].unique()}")
else:
    print("\n   ERRO: Nenhum registro em 2021 (Tokyo 2020 nao encontrado)")

# ============================================================================
# 3. VERIFICAR ESTRUTURA DAS COLUNAS
# ============================================================================
print("\n" + "="*80)
print("3. ESTRUTURA DE COLUNAS")
print("="*80)

expected_columns = [
    'ID', 'Name', 'Sex', 'Age', 'Height', 'Weight', 'Team', 'NOC',
    'Games', 'Year', 'Season', 'City', 'Sport', 'Event', 'Medal'
]

print(f"\nColunas esperadas: {len(expected_columns)}")
print(f"Colunas presentes: {len(df.columns)}")

missing = set(expected_columns) - set(df.columns)
extra = set(df.columns) - set(expected_columns)

if missing:
    print(f"\nALERTA - Colunas faltando: {missing}")
else:
    print(f"\nOK - Todas as colunas esperadas presentes")

if extra:
    print(f"ALERTA - Colunas extras: {extra}")
else:
    print(f"OK - Nenhuma coluna extra")

# ============================================================================
# 4. VERIFICAR CONSISTENCIA DE VALORES
# ============================================================================
print("\n" + "="*80)
print("4. CONSISTENCIA DE VALORES")
print("="*80)

# Sex deve ser M ou F
print(f"\nSex values:")
sex_values = df['Sex'].value_counts()
for sex, count in sex_values.items():
    print(f"   {sex}: {count:,} ({count/len(df)*100:.1f}%)")

invalid_sex = df[~df['Sex'].isin(['M', 'F'])]['Sex'].unique()
if len(invalid_sex) > 0:
    print(f"   ALERTA: Valores invalidos encontrados: {invalid_sex}")
else:
    print(f"   OK: Apenas M e F")

# Season deve ser Summer ou Winter
print(f"\nSeason values:")
season_values = df['Season'].value_counts()
for season, count in season_values.items():
    print(f"   {season}: {count:,} ({count/len(df)*100:.1f}%)")

invalid_season = df[~df['Season'].isin(['Summer', 'Winter'])]['Season'].unique()
if len(invalid_season) > 0:
    print(f"   ALERTA: Valores invalidos encontrados: {invalid_season}")
else:
    print(f"   OK: Apenas Summer e Winter")

# Medal deve ser Gold, Silver, Bronze ou NaN
print(f"\nMedal values (apenas medalhistas):")
medal_values = df[df['Medal'].notna()]['Medal'].value_counts()
for medal, count in medal_values.items():
    print(f"   {medal}: {count:,}")

invalid_medal = df[df['Medal'].notna() & ~df['Medal'].isin(['Gold', 'Silver', 'Bronze'])]['Medal'].unique()
if len(invalid_medal) > 0:
    print(f"   ALERTA: Valores invalidos encontrados: {invalid_medal}")
else:
    print(f"   OK: Apenas Gold, Silver, Bronze")

# ============================================================================
# 5. VERIFICAR TOKYO 2020 ESPECIFICAMENTE
# ============================================================================
print("\n" + "="*80)
print("5. ANALISE DETALHADA TOKYO 2020")
print("="*80)

tokyo = df[df['Year'] == 2021].copy()

if len(tokyo) > 0:
    print(f"\nRegistros Tokyo 2020 (2021): {len(tokyo):,}")

    # Medalhas
    tokyo_medals = tokyo[tokyo['Medal'].notna()]
    print(f"   Medalhas: {len(tokyo_medals):,}")
    print(f"      Gold: {len(tokyo_medals[tokyo_medals['Medal'] == 'Gold']):,}")
    print(f"      Silver: {len(tokyo_medals[tokyo_medals['Medal'] == 'Silver']):,}")
    print(f"      Bronze: {len(tokyo_medals[tokyo_medals['Medal'] == 'Bronze']):,}")

    # Esportes
    print(f"\n   Esportes representados: {tokyo['Sport'].nunique()}")
    print(f"   Top 5 esportes por registros:")
    top_sports = tokyo['Sport'].value_counts().head(5)
    for sport, count in top_sports.items():
        print(f"      {sport}: {count:,}")

    # Verificar esportes de interesse (Swimming, Basketball, Football)
    print(f"\n   Esportes de interesse (para analise de redes):")
    for sport in ['Swimming', 'Basketball', 'Football']:
        sport_data = tokyo[tokyo['Sport'] == sport]
        medals_count = sport_data[sport_data['Medal'].notna()]
        print(f"      {sport}: {len(sport_data):,} registros, {len(medals_count):,} medalhas")

    # Verificar NOCs
    print(f"\n   Paises (NOCs): {tokyo['NOC'].nunique()}")
    print(f"   Top 5 paises por registros:")
    top_nocs = tokyo['NOC'].value_counts().head(5)
    for noc, count in top_nocs.items():
        print(f"      {noc}: {count:,}")

    # Verificar missing values
    print(f"\n   Missing values em Tokyo 2020:")
    for col in ['Age', 'Height', 'Weight']:
        missing_pct = tokyo[col].isna().sum() / len(tokyo) * 100
        print(f"      {col}: {missing_pct:.1f}%")
else:
    print("\nERRO: Nenhum dado de Tokyo 2020 encontrado!")

# ============================================================================
# 6. VERIFICAR DUPLICATAS
# ============================================================================
print("\n" + "="*80)
print("6. VERIFICACAO DE DUPLICATAS")
print("="*80)

# Duplicatas por (ID, Event, Medal, Year, Sex)
duplicates = df[df.duplicated(subset=['ID', 'Event', 'Medal', 'Year', 'Sex'], keep=False)]
print(f"\nDuplicatas por (ID, Event, Medal, Year, Sex): {len(duplicates):,}")

if len(duplicates) > 0:
    print(f"   ALERTA: Duplicatas encontradas!")
    print(f"\n   Exemplos (primeiros 5):")
    for idx, row in duplicates.head(5).iterrows():
        print(f"      {row['Name']} - {row['Event']} - {row['Year']:.0f} - {row['Medal']}")
else:
    print(f"   OK: Nenhuma duplicata encontrada")

# Duplicatas em Tokyo especificamente
if len(tokyo) > 0:
    tokyo_dups = tokyo[tokyo.duplicated(subset=['ID', 'Event', 'Medal'], keep=False)]
    print(f"\nDuplicatas em Tokyo 2020: {len(tokyo_dups):,}")
    if len(tokyo_dups) > 0:
        print(f"   ALERTA: Duplicatas em Tokyo!")
    else:
        print(f"   OK: Nenhuma duplicata em Tokyo")

# ============================================================================
# 7. COMPARAR COM NUMEROS ESPERADOS
# ============================================================================
print("\n" + "="*80)
print("7. COMPARACAO COM NUMEROS ESPERADOS")
print("="*80)

expected_total = 273527
expected_base = 271116
expected_tokyo = 2411

actual_total = len(df)
actual_tokyo = len(df[df['Year'] == 2021])
actual_base = actual_total - actual_tokyo

print(f"\nTotal de registros:")
print(f"   Esperado: {expected_total:,}")
print(f"   Real: {actual_total:,}")
print(f"   Diferenca: {actual_total - expected_total:+,}")

if actual_total == expected_total:
    print(f"   OK - Total confere!")
else:
    print(f"   ALERTA - Total nao confere!")

print(f"\nDataset base (1896-2016):")
print(f"   Esperado: {expected_base:,}")
print(f"   Real: {actual_base:,}")
print(f"   Diferenca: {actual_base - expected_base:+,}")

print(f"\nTokyo 2020:")
print(f"   Esperado: ~{expected_tokyo:,}")
print(f"   Real: {actual_tokyo:,}")
print(f"   Diferenca: {actual_tokyo - expected_tokyo:+,}")

# ============================================================================
# 8. VERIFICAR IDS DE TOKYO
# ============================================================================
print("\n" + "="*80)
print("8. VERIFICACAO DE IDs")
print("="*80)

print(f"\nAtletas unicos no dataset completo: {df['ID'].nunique():,}")
print(f"Total de registros: {len(df):,}")
print(f"Ratio registros/atletas: {len(df)/df['ID'].nunique():.2f}")

if len(tokyo) > 0:
    tokyo_unique_ids = tokyo['ID'].nunique()
    print(f"\nAtletas unicos em Tokyo 2020: {tokyo_unique_ids:,}")
    print(f"Total de registros Tokyo: {len(tokyo):,}")
    print(f"Ratio registros/atletas: {len(tokyo)/tokyo_unique_ids:.2f}")

    # Verificar se IDs de Tokyo sao diferentes dos historicos
    base_ids = set(df[df['Year'] < 2021]['ID'].unique())
    tokyo_ids = set(tokyo['ID'].unique())
    overlap = base_ids.intersection(tokyo_ids)

    print(f"\nOverlap de IDs (atletas em Tokyo e em edicoes anteriores):")
    print(f"   IDs em comum: {len(overlap):,}")
    print(f"   % de atletas Tokyo que participaram antes: {len(overlap)/len(tokyo_ids)*100:.1f}%")

    if len(overlap) > 0:
        print(f"\n   Exemplos de atletas que participaram antes e em Tokyo:")
        for athlete_id in list(overlap)[:5]:
            athlete_data = df[df['ID'] == athlete_id]
            name = athlete_data.iloc[0]['Name']
            years = sorted(athlete_data['Year'].dropna().unique())
            print(f"      {name}: {len(years)} edicoes ({years[0]:.0f}-{years[-1]:.0f})")

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("\n" + "="*80)
print("RESUMO DA VALIDACAO")
print("="*80)

issues = []
warnings = []
success = []

# Checks
if len(df[df['Year'] == 2020]) > 0:
    issues.append("Existem registros em 2020 (deveria ser 2021)")
else:
    success.append("Nenhum registro em 2020")

if len(df[df['Year'] == 2021]) > 0:
    success.append(f"Tokyo 2020 presente ({len(df[df['Year'] == 2021]):,} registros)")
else:
    issues.append("Tokyo 2020 nao encontrado")

if missing or extra:
    issues.append("Colunas inconsistentes")
else:
    success.append("Estrutura de colunas correta")

if len(invalid_sex) > 0:
    issues.append("Valores invalidos em Sex")
else:
    success.append("Sex values validos (M/F)")

if len(duplicates) > 0:
    warnings.append(f"{len(duplicates):,} duplicatas encontradas")
else:
    success.append("Nenhuma duplicata")

if actual_total == expected_total:
    success.append(f"Total de registros confere ({expected_total:,})")
else:
    warnings.append(f"Total diferente do esperado ({actual_total:,} vs {expected_total:,})")

print(f"\nSUCESSOS ({len(success)}):")
for s in success:
    print(f"   [OK] {s}")

if warnings:
    print(f"\nALERTAS ({len(warnings)}):")
    for w in warnings:
        print(f"   [!] {w}")

if issues:
    print(f"\nPROBLEMAS CRITICOS ({len(issues)}):")
    for i in issues:
        print(f"   [X] {i}")
    print(f"\n   MERGE PRECISA DE CORRECAO!")
else:
    print(f"\n   MERGE VALIDADO COM SUCESSO!")

print("="*80)
