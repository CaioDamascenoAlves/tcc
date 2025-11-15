"""
Script para extrair estatísticas completas do dataset original
Gera números para validação da monografia e documentação oficial
"""

import pandas as pd
import sys
from pathlib import Path

# Adicionar caminho do projeto
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / 'src'))

def extract_complete_stats():
    """Extrai estatísticas completas do dataset olímpico"""

    print("="*80)
    print("EXTRAÇÃO DE ESTATÍSTICAS DO DATASET ORIGINAL")
    print("="*80)

    # Carregar dataset
    data_path = project_root / 'data' / 'athlete_events.csv'
    print(f"\nCarregando dataset: {data_path}")
    df = pd.read_csv(data_path)

    print(f"\n{'='*80}")
    print("ESTATÍSTICAS GERAIS DO DATASET")
    print(f"{'='*80}")

    # Estatísticas básicas
    total_records = len(df)
    unique_athletes = df['ID'].nunique()
    unique_sports = df['Sport'].nunique()
    unique_events = df['Event'].nunique()
    unique_nocs = df['NOC'].nunique()
    unique_games = df['Games'].nunique()

    print(f"\nREGISTROS E ATLETAS:")
    print(f"   Total de registros: {total_records:,}")
    print(f"   Atletas únicos: {unique_athletes:,}")

    print(f"\nMEDALHAS:")
    medalists = df[df['Medal'].notna()]
    total_medals = len(medalists)
    pct_medals = (total_medals / total_records) * 100

    print(f"   Total de conquistas de medalhas: {total_medals:,} ({pct_medals:.1f}%)")

    gold = len(medalists[medalists['Medal'] == 'Gold'])
    silver = len(medalists[medalists['Medal'] == 'Silver'])
    bronze = len(medalists[medalists['Medal'] == 'Bronze'])

    print(f"   Medalhas de Ouro: {gold:,}")
    print(f"   Medalhas de Prata: {silver:,}")
    print(f"   Medalhas de Bronze: {bronze:,}")

    print(f"\nMODALIDADES E EVENTOS:")
    print(f"   Modalidades esportivas: {unique_sports}")
    print(f"   Eventos distintos: {unique_events:,}")

    print(f"\nREPRESENTACAO:")
    print(f"   Comitês Olímpicos Nacionais (NOCs): {unique_nocs}")
    print(f"   Edições dos jogos: {unique_games}")

    print(f"\nPERIODO TEMPORAL:")
    years = df['Year'].dropna().astype(int)
    min_year = years.min()
    max_year = years.max()
    years_span = max_year - min_year + 1

    print(f"   Primeira edição: {min_year}")
    print(f"   Última edição: {max_year}")
    print(f"   Período: {years_span} anos ({min_year}-{max_year})")

    print(f"\nTEMPORADA:")
    season_counts = df['Season'].value_counts()
    for season, count in season_counts.items():
        pct = (count / total_records) * 100
        print(f"   {season}: {count:,} registros ({pct:.1f}%)")

    print(f"\n{'='*80}")
    print("FILTROS APLICADOS NO PIPELINE")
    print(f"{'='*80}")

    # Filtros do pipeline
    selected_sports = ['Swimming', 'Basketball', 'Football']
    filtered = df[
        (df['Medal'].notna()) &
        (df['Season'] == 'Summer') &
        (df['Sport'].isin(selected_sports))
    ].copy()

    print(f"\nESPORTES SELECIONADOS: {', '.join(selected_sports)}")
    print(f"   Apenas medalhistas: Sim")
    print(f"   Apenas jogos de verão: Sim")

    print(f"\nDATASET FILTRADO:")
    print(f"   Total de registros: {len(filtered):,}")
    print(f"   Atletas únicos: {filtered['ID'].nunique():,}")

    print(f"\nDISTRIBUICAO POR ESPORTE:")
    for sport in selected_sports:
        sport_data = filtered[filtered['Sport'] == sport]
        athletes = sport_data['ID'].nunique()
        records = len(sport_data)
        events = sport_data['Event'].nunique()
        print(f"   {sport}:")
        print(f"      Registros: {records:,}")
        print(f"      Atletas únicos: {athletes:,}")
        print(f"      Eventos distintos: {events}")

    print(f"\nDISTRIBUICAO POR GENERO:")
    sex_counts = filtered['Sex'].value_counts()
    for sex, count in sex_counts.items():
        athletes = filtered[filtered['Sex'] == sex]['ID'].nunique()
        print(f"   {sex}: {count:,} registros, {athletes:,} atletas únicos")

    print(f"\n{'='*80}")
    print("VALIDACAO CONTRA PIPELINE")
    print(f"{'='*80}")

    # Números do pipeline (de DADOS_OFICIAIS.md)
    pipeline_initial = 6113
    pipeline_duplicates = 2
    pipeline_clean = 6111
    pipeline_athletes = 4264
    pipeline_podiums = 662
    pipeline_final_athletes = 4659

    print(f"\nCOMPARACAO:")
    print(f"   Pipeline reportou: {pipeline_initial:,} medalhistas iniciais")
    print(f"   Dataset filtrado mostra: {len(filtered):,} registros")
    if len(filtered) == pipeline_initial:
        print(f"   OK - MATCH!")
    else:
        diff = len(filtered) - pipeline_initial
        print(f"   ATENCAO - DIFERENCA: {diff:+,} registros")

    print(f"\n   Pipeline removeu: {pipeline_duplicates} duplicados")
    print(f"   Pipeline apos limpeza: {pipeline_clean:,} registros")
    print(f"   Pipeline atletas unicos (inicial): {pipeline_athletes:,}")
    print(f"   Pipeline podios validos: {pipeline_podiums}")
    print(f"   Pipeline atletas finais (em redes): {pipeline_final_athletes:,}")

    print(f"\n{'='*80}")
    print("ESTATISTICAS PARA ATUALIZAR NA MONOGRAFIA")
    print(f"{'='*80}")

    print(f"""
NUMEROS CORRETOS PARA USAR:

Dataset Base (Kaggle - Griffin 2018):
   - Período: {min_year}-{max_year} ({years_span} anos de história olímpica)
   - Total de registros: {total_records:,}
   - Atletas únicos: {unique_athletes:,}
   - Modalidades esportivas: {unique_sports}
   - Eventos distintos: {unique_events:,}
   - Comitês Olímpicos Nacionais: {unique_nocs}
   - Edições dos jogos: {unique_games}

Medalhistas:
   - Total de conquistas: {total_medals:,} ({pct_medals:.1f}% do dataset)
   - Ouro: {gold:,}
   - Prata: {silver:,}
   - Bronze: {bronze:,}

Filtros Aplicados (Swimming, Basketball, Football - Apenas Medalhistas de Verão):
   - Registros iniciais: {len(filtered):,}
   - Após limpeza: {pipeline_clean:,}
   - Atletas únicos nas redes: {pipeline_final_athletes:,}
   - Pódios válidos: {pipeline_podiums}
    """)

    print(f"{'='*80}\n")

if __name__ == '__main__':
    extract_complete_stats()
