#!/usr/bin/env python3
"""
Script para comparar métricas antes e depois da correção do agrupamento.
Compara results_old/ (agrupamento só por Event) vs results/ (agrupamento por Year+Event)
"""

import pandas as pd
import json
import os
from pathlib import Path

def load_consolidated_metrics(results_dir):
    """Carrega métricas consolidadas de um diretório."""
    csv_path = os.path.join(results_dir, 'consolidated_sports_network_analysis.csv')
    if not os.path.exists(csv_path):
        print(f"Arquivo não encontrado: {csv_path}")
        return None
    return pd.read_csv(csv_path)

def load_network_summaries(results_dir):
    """Carrega resumos das redes."""
    json_path = os.path.join(results_dir, 'all_network_summaries.json')
    if not os.path.exists(json_path):
        print(f"Arquivo não encontrado: {json_path}")
        return None
    with open(json_path, 'r') as f:
        return json.load(f)

def compare_basic_stats(old_df, new_df):
    """Compara estatísticas básicas."""
    print("\n" + "="*80)
    print("COMPARAÇÃO DE ESTATÍSTICAS BÁSICAS")
    print("="*80)

    print(f"\n{'Métrica':<40} {'ANTES':<20} {'DEPOIS':<20} {'DIFERENÇA':<15}")
    print("-"*95)

    # Total de atletas
    old_athletes = old_df['athlete_id'].nunique()
    new_athletes = new_df['athlete_id'].nunique()
    diff = new_athletes - old_athletes
    pct = (diff / old_athletes * 100) if old_athletes > 0 else 0
    print(f"{'Total de atletas únicos':<40} {old_athletes:<20,} {new_athletes:<20,} {diff:+,} ({pct:+.1f}%)")

    # Total de registros
    old_records = len(old_df)
    new_records = len(new_df)
    diff = new_records - old_records
    pct = (diff / old_records * 100) if old_records > 0 else 0
    print(f"{'Total de registros':<40} {old_records:<20,} {new_records:<20,} {diff:+,} ({pct:+.1f}%)")

def compare_network_metrics(old_summaries, new_summaries):
    """Compara métricas de rede (nós, arestas, densidade)."""
    print("\n" + "="*80)
    print("COMPARAÇÃO DE MÉTRICAS DE REDE POR ESPORTE/SEXO")
    print("="*80)

    # Criar dicionário para fácil acesso
    def make_key(summary):
        sport = summary.get('sport', '')
        sex = summary.get('sex', '')
        event_type = summary.get('event_type', 'combined')
        return f"{sport}_{sex}_{event_type}"

    old_dict = {make_key(s): s for s in old_summaries}
    new_dict = {make_key(s): s for s in new_summaries}

    # Cabeçalho
    print(f"\n{'Rede':<30} {'Métrica':<20} {'ANTES':<15} {'DEPOIS':<15} {'DIFERENÇA':<15}")
    print("-"*95)

    for key in sorted(set(old_dict.keys()) | set(new_dict.keys())):
        old = old_dict.get(key, {})
        new = new_dict.get(key, {})

        old_basic = old.get('original_network', {})
        new_basic = new.get('original_network', {})

        # Nós
        old_nodes = old_basic.get('num_nodes', 0)
        new_nodes = new_basic.get('num_nodes', 0)
        diff_nodes = new_nodes - old_nodes
        pct_nodes = (diff_nodes / old_nodes * 100) if old_nodes > 0 else 0

        # Arestas
        old_edges = old_basic.get('num_edges', 0)
        new_edges = new_basic.get('num_edges', 0)
        diff_edges = new_edges - old_edges
        pct_edges = (diff_edges / old_edges * 100) if old_edges > 0 else 0

        # Densidade
        old_density = old_basic.get('density', 0)
        new_density = new_basic.get('density', 0)
        diff_density = new_density - old_density

        if old_nodes > 0 or new_nodes > 0:
            print(f"{key:<30} {'Nós':<20} {old_nodes:<15,} {new_nodes:<15,} {diff_nodes:+,} ({pct_nodes:+.1f}%)")
            print(f"{'':<30} {'Arestas':<20} {old_edges:<15,} {new_edges:<15,} {diff_edges:+,} ({pct_edges:+.1f}%)")
            print(f"{'':<30} {'Densidade':<20} {old_density:<15.6f} {new_density:<15.6f} {diff_density:+.6f}")
            print()

def compare_top_pagerank(old_df, new_df, top_n=10):
    """Compara top N atletas por PageRank."""
    print("\n" + "="*80)
    print(f"TOP {top_n} ATLETAS POR PAGERANK - COMPARAÇÃO")
    print("="*80)

    # Top ANTES
    old_top = old_df.nlargest(top_n, 'original_pagerank')[['name', 'sport', 'sex', 'original_pagerank', 'total_medals']]
    old_top = old_top.copy()
    old_top.columns = ['Nome', 'Esporte', 'Sexo', 'PageRank', 'Medalhas']

    # Top DEPOIS
    new_top = new_df.nlargest(top_n, 'original_pagerank')[['name', 'sport', 'sex', 'original_pagerank', 'total_medals']]
    new_top = new_top.copy()
    new_top.columns = ['Nome', 'Esporte', 'Sexo', 'PageRank', 'Medalhas']

    print("\n### ANTES (agrupamento só por Event) ###")
    print(old_top.to_string(index=False))

    print("\n### DEPOIS (agrupamento por Year+Event) ###")
    print(new_top.to_string(index=False))

    # Mudanças no top 10
    old_names = set(old_top['Nome'])
    new_names = set(new_top['Nome'])

    entered = new_names - old_names
    left = old_names - new_names

    if entered:
        print(f"\n🔼 ENTRARAM no top {top_n}: {', '.join(entered)}")
    if left:
        print(f"🔽 SAÍRAM do top {top_n}: {', '.join(left)}")

def compare_degree_distribution(old_df, new_df):
    """Compara distribuição de graus."""
    print("\n" + "="*80)
    print("DISTRIBUIÇÃO DE GRAUS (IN-DEGREE E OUT-DEGREE)")
    print("="*80)

    print(f"\n{'Métrica':<40} {'ANTES':<20} {'DEPOIS':<20}")
    print("-"*80)

    # In-Degree
    print(f"{'In-Degree médio':<40} {old_df['original_in_degree'].mean():<20.2f} {new_df['original_in_degree'].mean():<20.2f}")
    print(f"{'In-Degree máximo':<40} {old_df['original_in_degree'].max():<20,} {new_df['original_in_degree'].max():<20,}")
    print(f"{'In-Degree mediano':<40} {old_df['original_in_degree'].median():<20.1f} {new_df['original_in_degree'].median():<20.1f}")

    # Out-Degree
    print(f"{'Out-Degree médio':<40} {old_df['original_out_degree'].mean():<20.2f} {new_df['original_out_degree'].mean():<20.2f}")
    print(f"{'Out-Degree máximo':<40} {old_df['original_out_degree'].max():<20,} {new_df['original_out_degree'].max():<20,}")
    print(f"{'Out-Degree mediano':<40} {old_df['original_out_degree'].median():<20.1f} {new_df['original_out_degree'].median():<20.1f}")

def main():
    base_dir = Path(__file__).parent.parent.parent  # main/

    # Carregar dados antigos
    print("\nCarregando resultados ANTIGOS (agrupamento só por Event)...")
    old_df = load_consolidated_metrics(base_dir / 'results_old')
    old_summaries = load_network_summaries(base_dir / 'results_old')

    # Carregar dados novos
    print("Carregando resultados NOVOS (agrupamento por Year+Event)...")
    new_df = load_consolidated_metrics(base_dir / 'results')
    new_summaries = load_network_summaries(base_dir / 'results')

    if old_df is None or new_df is None:
        print("\n❌ Erro: Não foi possível carregar os arquivos necessários.")
        return

    # Comparações
    compare_basic_stats(old_df, new_df)

    if old_summaries and new_summaries:
        compare_network_metrics(old_summaries, new_summaries)

    compare_top_pagerank(old_df, new_df, top_n=15)
    compare_degree_distribution(old_df, new_df)

    print("\n" + "="*80)
    print("ANÁLISE CONCLUÍDA")
    print("="*80)

if __name__ == "__main__":
    main()
