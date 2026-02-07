#!/usr/bin/env python3
"""
Script de validação do dashboard após refatoração.
Testa carregamento de dados e estruturas esperadas.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data_loader_wrapper import DataLoader


def test_load_all():
    """Testa carregamento completo de dados."""
    print("=" * 70)
    print("TESTE DE CARREGAMENTO DE DADOS")
    print("=" * 70)

    loader = DataLoader()
    data = loader.load_all()

    # Verificações básicas
    assert 'athletes' in data, "❌ athletes não carregado"
    assert 'metadata' in data, "❌ metadata não carregado"
    assert not data['metadata'].empty, "❌ metadata vazio"
    assert 'network_id' in data['athletes'].columns, "❌ network_id ausente em athletes"

    # Estatísticas
    n_athletes = len(data['athletes'])
    n_networks = len(data['metadata'])
    n_unique_network_ids = data['athletes']['network_id'].nunique()
    n_sports = data['athletes']['sport'].nunique()

    print(f"\n✓ Carregamento bem-sucedido!")
    print(f"  • {n_athletes:,} atletas carregados")
    print(f"  • {n_networks} redes carregadas (metadata)")
    print(f"  • {n_unique_network_ids} network_ids únicos em athletes")
    print(f"  • {n_sports} esportes disponíveis")

    # Mostrar colunas disponíveis
    print(f"\n📋 Colunas disponíveis em athletes ({len(data['athletes'].columns)} total):")
    for i, col in enumerate(sorted(data['athletes'].columns), 1):
        print(f"  {i:2d}. {col}")

    # Verificar estrutura mínima necessária
    required_columns = ['network_id', 'sport']
    # Aceitar 'sex' ou 'gender'
    has_sex_col = 'sex' in data['athletes'].columns or 'gender' in data['athletes'].columns

    missing_cols = [col for col in required_columns if col not in data['athletes'].columns]
    if missing_cols:
        print(f"\n❌ Colunas OBRIGATÓRIAS ausentes em athletes: {missing_cols}")
    elif not has_sex_col:
        print(f"\n❌ Coluna 'sex' ou 'gender' ausente em athletes")
    else:
        sex_col = 'sex' if 'sex' in data['athletes'].columns else 'gender'
        print(f"\n✓ Todas as colunas obrigatórias presentes em athletes (sexo: {sex_col})")

    # Verificar metadata
    metadata_cols = ['network_id', 'sport', 'gender', 'event_name', 'n_athletes', 'n_edges']
    missing_meta_cols = [col for col in metadata_cols if col not in data['metadata'].columns]
    if missing_meta_cols:
        print(f"⚠️  Colunas ausentes em metadata: {missing_meta_cols}")
    else:
        print(f"✓ Todas as colunas essenciais presentes em metadata")

    # Verificar consistência
    print(f"\n{'=' * 70}")
    print("VERIFICAÇÃO DE CONSISTÊNCIA")
    print("=" * 70)

    # Todos network_ids em athletes devem existir em metadata
    athlete_network_ids = set(data['athletes']['network_id'].unique())
    metadata_network_ids = set(data['metadata']['network_id'].unique())

    orphan_ids = athlete_network_ids - metadata_network_ids
    if orphan_ids:
        print(f"⚠️  {len(orphan_ids)} network_ids em athletes sem metadata: {orphan_ids}")
    else:
        print(f"✓ Todos network_ids em athletes existem em metadata")

    print(f"\n{'=' * 70}")
    print("RESUMO POR ESPORTE")
    print("=" * 70)

    # Usar athlete_id ou index para contar atletas
    count_column = 'athlete_id' if 'athlete_id' in data['athletes'].columns else data['athletes'].index.name or 'index'
    sex_column = 'sex' if 'sex' in data['athletes'].columns else 'gender'

    if count_column == 'index':
        # Se não há athlete_id, usar reset_index temporário
        sports_summary = data['athletes'].reset_index().groupby('sport').agg({
            'network_id': 'nunique',
            'index': 'count',
            sex_column: lambda x: sorted(x.unique())
        }).rename(columns={'network_id': 'n_networks', 'index': 'n_athletes', sex_column: 'genders'})
    else:
        sports_summary = data['athletes'].groupby('sport').agg({
            'network_id': 'nunique',
            count_column: 'count',
            sex_column: lambda x: sorted(x.unique())
        }).rename(columns={'network_id': 'n_networks', count_column: 'n_athletes', sex_column: 'genders'})

    for sport, row in sports_summary.iterrows():
        print(f"  {sport.title():15s} | {row['n_networks']:3d} redes | {row['n_athletes']:5d} atletas | Sexos: {row['genders']}")

    print(f"\n{'=' * 70}")
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 70)

    return True


if __name__ == '__main__':
    try:
        test_load_all()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ ERRO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
