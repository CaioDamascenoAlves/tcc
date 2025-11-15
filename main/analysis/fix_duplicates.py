"""
Script para remover duplicatas exatas do athlete_events.csv
"""

import pandas as pd
from pathlib import Path
import shutil

project_root = Path(__file__).parent.parent

print("="*80)
print("CORRECAO DE DUPLICATAS NO DATASET")
print("="*80)

# Carregar dataset
data_path = project_root / 'data' / 'athlete_events.csv'
backup_path = project_root / 'data' / 'athlete_events_BACKUP.csv'

print(f"\n1. Fazendo backup do arquivo original...")
shutil.copy(data_path, backup_path)
print(f"   Backup salvo em: {backup_path}")

print(f"\n2. Carregando dataset...")
df = pd.read_csv(data_path)
print(f"   Registros originais: {len(df):,}")

# Identificar duplicatas exatas
print(f"\n3. Identificando duplicatas exatas...")
duplicates_mask = df.duplicated(subset=['ID', 'Name', 'Sex', 'Year', 'Sport', 'Event', 'Medal'], keep='first')
num_duplicates = duplicates_mask.sum()

print(f"   Duplicatas encontradas: {num_duplicates:,}")

if num_duplicates > 0:
    # Mostrar exemplos
    print(f"\n   Exemplos de duplicatas (primeiros 5):")
    dup_examples = df[duplicates_mask].head(5)
    for idx, row in dup_examples.iterrows():
        print(f"      {row['Name']} - {row['Event']} - {row['Year']:.0f} - {row['Medal']}")

    # Remover duplicatas (manter primeira ocorrencia)
    print(f"\n4. Removendo duplicatas...")
    df_clean = df[~duplicates_mask].copy()
    print(f"   Registros apos limpeza: {len(df_clean):,}")
    print(f"   Removidos: {len(df) - len(df_clean):,}")

    # Salvar dataset limpo
    print(f"\n5. Salvando dataset limpo...")
    df_clean.to_csv(data_path, index=False)
    print(f"   Salvo em: {data_path}")

    # Estatisticas finais
    print(f"\n" + "="*80)
    print("RESUMO")
    print("="*80)
    print(f"   Registros originais: {len(df):,}")
    print(f"   Duplicatas removidas: {num_duplicates:,}")
    print(f"   Registros finais: {len(df_clean):,}")
    print(f"   Backup: {backup_path}")

    # Verificar Tokyo especificamente
    tokyo_original = df[df['Year'] == 2021]
    tokyo_clean = df_clean[df_clean['Year'] == 2021]
    print(f"\n   Tokyo 2020:")
    print(f"      Original: {len(tokyo_original):,}")
    print(f"      Limpo: {len(tokyo_clean):,}")
    print(f"      Removidos: {len(tokyo_original) - len(tokyo_clean):,}")

    print(f"\n   DATASET CORRIGIDO COM SUCESSO!")
else:
    print(f"\n   Nenhuma duplicata encontrada. Dataset ja esta limpo!")

print("="*80)
