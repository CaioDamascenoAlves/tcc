#!/usr/bin/env python3
"""
Análise Geográfica - 12 Redes Individuais

Para cada uma das 12 redes principais, calcula e visualiza:
- Top 10 países por número de medalhas
- Dominância geográfica (% medalhas dos top 3 países)
- Diversidade regional (entropia geográfica)
- Mapas de calor de distribuição mundial

Objetivo: Revelar padrões de dominância regional e evolução geográfica.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from pathlib import Path

print("=" * 80)
print("ANÁLISE GEOGRÁFICA - 12 REDES INDIVIDUAIS")
print("=" * 80)

# ====================
# 1. CONFIGURAÇÃO
# ====================

# As 12 redes principais do estudo
NETWORKS_CONFIG = [
    {'sport': 'Football', 'event': "Men's Football", 'gender': 'M', 'name': 'M Football'},
    {'sport': 'Football', 'event': "Women's Football", 'gender': 'F', 'name': 'F Football'},
    {'sport': 'Basketball', 'event': "Men's Basketball", 'gender': 'M', 'name': 'M Basketball'},
    {'sport': 'Basketball', 'event': "Women's Basketball", 'gender': 'F', 'name': 'F Basketball'},
    {'sport': 'Athletics', 'event': "Athletics Men's 100 metres", 'gender': 'M', 'name': 'M 100m'},
    {'sport': 'Athletics', 'event': "Athletics Women's 100 metres", 'gender': 'F', 'name': 'F 100m'},
    {'sport': 'Swimming', 'event': "Swimming Men's 100 metres Freestyle", 'gender': 'M', 'name': 'M 100m Freestyle'},
    {'sport': 'Swimming', 'event': "Swimming Women's 100 metres Freestyle", 'gender': 'F', 'name': 'F 100m Freestyle'},
    {'sport': 'Judo', 'event': "Judo Men's Middleweight", 'gender': 'M', 'name': 'M -90kg'},
    {'sport': 'Judo', 'event': "Judo Women's Half-Middleweight", 'gender': 'F', 'name': 'F -70kg'},
    {'sport': 'Boxing', 'event': "Boxing Men's Welterweight", 'gender': 'M', 'name': 'M Welter (63-69kg)'},
    {'sport': 'Boxing', 'event': "Boxing Women's Middleweight", 'gender': 'F', 'name': 'F Middle (69-75kg)'},
]

# ====================
# 2. CARREGAR DADOS
# ====================

print("\n📂 Carregando dados originais...")

try:
    df = pd.read_csv('../data/athlete_events_clean.csv')
    print(f"✓ Dataset carregado: {len(df)} registros")
except FileNotFoundError:
    try:
        df = pd.read_csv('data/athlete_events_clean.csv')
        print(f"✓ Dataset carregado: {len(df)} registros")
    except FileNotFoundError:
        print("❌ Dataset não encontrado")
        exit(1)

# Filtrar apenas medalhistas de verão
df = df[(df['Medal'].notna()) & (df['Season'] == 'Summer')].copy()
print(f"✓ Medalhistas de verão: {len(df)} registros")

# ====================
# 3. FUNÇÕES AUXILIARES
# ====================

def calculate_entropy(counts):
    """Calcula entropia de Shannon para distribuição de países."""
    total = sum(counts.values())
    if total == 0:
        return 0

    probs = [count/total for count in counts.values()]
    entropy = -sum(p * np.log2(p) for p in probs if p > 0)
    return entropy

def calculate_gini(counts):
    """Calcula coeficiente de Gini para desigualdade de medalhas."""
    values = sorted(counts.values())
    n = len(values)
    if n == 0:
        return 0

    numerator = 2 * sum((i+1) * v for i, v in enumerate(values))
    denominator = n * sum(values)

    if denominator == 0:
        return 0

    return (numerator / denominator) - (n + 1) / n

# ====================
# 4. ANÁLISE POR REDE
# ====================

all_results = []
all_top10_countries = []

for net_config in NETWORKS_CONFIG:
    print(f"\n{'='*80}")
    print(f"🔍 Analisando: {net_config['name']} ({net_config['sport']})")
    print(f"{'='*80}")

    # Filtrar dados para esta rede
    if 'Football' in net_config['event']:
        df_net = df[(df['Sport'] == 'Football') & (df['Sex'] == net_config['gender'])].copy()
    elif 'Basketball' in net_config['event']:
        df_net = df[(df['Sport'] == 'Basketball') & (df['Sex'] == net_config['gender'])].copy()
    elif 'Athletics' in net_config['event']:
        df_net = df[(df['Event'] == net_config['event'])].copy()
    elif 'Swimming' in net_config['event']:
        df_net = df[(df['Event'] == net_config['event'])].copy()
    elif 'Judo' in net_config['event']:
        df_net = df[(df['Event'] == net_config['event'])].copy()
    elif 'Boxing' in net_config['event']:
        df_net = df[(df['Event'] == net_config['event'])].copy()
    else:
        continue

    if len(df_net) == 0:
        print(f"   ⚠️  Sem dados para {net_config['name']}")
        continue

    # Contar medalhas por país (NOC)
    country_counts = Counter(df_net['NOC'].dropna())

    if len(country_counts) == 0:
        print(f"   ⚠️  Sem dados de países para {net_config['name']}")
        continue

    # Métricas geográficas
    total_medals = sum(country_counts.values())
    num_countries = len(country_counts)

    # Top 3 dominância
    top3_medals = sum(c for _, c in country_counts.most_common(3))
    top3_pct = (top3_medals / total_medals * 100) if total_medals > 0 else 0

    # Entropia e Gini
    entropy = calculate_entropy(country_counts)
    gini = calculate_gini(country_counts)

    # Salvar resultado
    result = {
        'network_name': net_config['name'],
        'sport': net_config['sport'],
        'gender': net_config['gender'],
        'total_medals': total_medals,
        'num_countries': num_countries,
        'top3_dominance_pct': top3_pct,
        'entropy': entropy,
        'gini_coefficient': gini,
        'top1_country': country_counts.most_common(1)[0][0],
        'top1_medals': country_counts.most_common(1)[0][1],
        'top1_pct': country_counts.most_common(1)[0][1] / total_medals * 100
    }
    all_results.append(result)

    print(f"   ✓ {num_countries} países | {total_medals} medalhas")
    print(f"   Top 3 dominância: {top3_pct:.1f}%")
    print(f"   Entropia: {entropy:.3f} | Gini: {gini:.3f}")
    print(f"   #1: {result['top1_country']} ({result['top1_pct']:.1f}%)")

    # Salvar top 10 países desta rede
    for rank, (country, medals) in enumerate(country_counts.most_common(10), 1):
        all_top10_countries.append({
            'network_name': net_config['name'],
            'sport': net_config['sport'],
            'gender': net_config['gender'],
            'rank': rank,
            'country': country,
            'medals': medals,
            'pct_of_total': medals / total_medals * 100
        })

# ====================
# 5. CONSOLIDAR RESULTADOS
# ====================

df_results = pd.DataFrame(all_results)
df_top10 = pd.DataFrame(all_top10_countries)

print(f"\n{'='*80}")
print(f"✓ Análise geográfica concluída: {len(df_results)} redes")
print(f"{'='*80}")

# Salvar CSVs
output_summary = '../results_complete_mining/data/geographic_summary_12networks.csv'
df_results.to_csv(output_summary, index=False)
print(f"\n✓ Salvo: {output_summary}")

output_top10 = '../results_complete_mining/data/geographic_top10_12networks.csv'
df_top10.to_csv(output_top10, index=False)
print(f"✓ Salvo: {output_top10}")

# ====================
# 6. VISUALIZAÇÕES
# ====================

print(f"\n{'='*80}")
print("📊 Gerando visualizações...")
print(f"{'='*80}")

# 6.1 Gráfico de barras - Top 5 países por rede
fig, axes = plt.subplots(4, 3, figsize=(20, 16))
fig.suptitle('Top 5 Países por Medalhas - 12 Redes Individuais', fontsize=16, fontweight='bold')

for idx, net_config in enumerate(NETWORKS_CONFIG):
    ax = axes[idx // 3, idx % 3]

    # Filtrar top 5 desta rede
    df_net_top5 = df_top10[
        (df_top10['network_name'] == net_config['name']) &
        (df_top10['rank'] <= 5)
    ].copy()

    if len(df_net_top5) == 0:
        ax.text(0.5, 0.5, 'Sem dados', ha='center', va='center', transform=ax.transAxes)
        ax.set_title(net_config['name'])
        continue

    # Plotar barras
    colors = ['#1f77b4' if net_config['gender'] == 'M' else '#d62728'] * 5
    ax.barh(df_net_top5['country'], df_net_top5['medals'], color=colors, alpha=0.7)

    ax.set_title(f"{net_config['name']}", fontweight='bold')
    ax.set_xlabel('Número de Medalhas')
    ax.invert_yaxis()  # País #1 no topo
    ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
output_fig1 = '../results_complete_mining/figures/geographic_top5_countries.pdf'
plt.savefig(output_fig1, dpi=300, bbox_inches='tight')
print(f"✓ Figura salva: {output_fig1}")
plt.close()

# 6.2 Dominância Top 3 vs Diversidade (entropia)
fig, ax = plt.subplots(figsize=(12, 8))

for _, row in df_results.iterrows():
    color = 'blue' if row['gender'] == 'M' else 'red'
    marker = 'o' if 'team' in row['sport'].lower() or 'ball' in row['sport'].lower() else '^'

    ax.scatter(row['entropy'], row['top3_dominance_pct'],
               s=200, color=color, marker=marker, alpha=0.6, edgecolors='black', linewidth=1.5)
    ax.annotate(row['network_name'], (row['entropy'], row['top3_dominance_pct']),
                xytext=(5, 5), textcoords='offset points', fontsize=9, alpha=0.8)

ax.set_xlabel('Entropia Geográfica (diversidade)', fontsize=12)
ax.set_ylabel('Dominância Top 3 Países (%)', fontsize=12)
ax.set_title('Diversidade Geográfica vs Concentração de Medalhas\n12 Redes Olímpicas Individuais',
             fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

# Legenda
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='blue', alpha=0.6, label='Masculino'),
    Patch(facecolor='red', alpha=0.6, label='Feminino')
]
ax.legend(handles=legend_elements, loc='best')

plt.tight_layout()
output_fig2 = '../results_complete_mining/figures/geographic_diversity_vs_dominance.pdf'
plt.savefig(output_fig2, dpi=300, bbox_inches='tight')
print(f"✓ Figura salva: {output_fig2}")
plt.close()

# 6.3 Coeficiente de Gini por rede
fig, ax = plt.subplots(figsize=(14, 6))

df_sorted = df_results.sort_values('gini_coefficient', ascending=False)
colors = ['blue' if g == 'M' else 'red' for g in df_sorted['gender']]

ax.barh(df_sorted['network_name'], df_sorted['gini_coefficient'], color=colors, alpha=0.7)
ax.set_xlabel('Coeficiente de Gini (desigualdade de medalhas)', fontsize=12)
ax.set_title('Desigualdade na Distribuição de Medalhas entre Países\n12 Redes Individuais',
             fontsize=14, fontweight='bold')
ax.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5, label='Desigualdade moderada')
ax.legend()
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
output_fig3 = '../results_complete_mining/figures/geographic_gini_coefficient.pdf'
plt.savefig(output_fig3, dpi=300, bbox_inches='tight')
print(f"✓ Figura salva: {output_fig3}")
plt.close()

# ====================
# 7. ANÁLISE DE PADRÕES
# ====================

print(f"\n{'='*80}")
print("🔍 Identificando padrões geográficos...")
print(f"{'='*80}")

print("\n📊 Redes com maior dominância (Top 3 > 70%):")
high_dominance = df_results[df_results['top3_dominance_pct'] > 70].sort_values('top3_dominance_pct', ascending=False)
for _, row in high_dominance.head(5).iterrows():
    print(f"   {row['network_name']:25s} | {row['top3_dominance_pct']:5.1f}% | Top 1: {row['top1_country']}")

print("\n📊 Redes com maior diversidade (Entropia > 3.0):")
high_diversity = df_results[df_results['entropy'] > 3.0].sort_values('entropy', ascending=False)
for _, row in high_diversity.head(5).iterrows():
    print(f"   {row['network_name']:25s} | Entropia: {row['entropy']:.3f} | {row['num_countries']} países")

print("\n📊 Redes com maior desigualdade (Gini > 0.7):")
high_inequality = df_results[df_results['gini_coefficient'] > 0.7].sort_values('gini_coefficient', ascending=False)
for _, row in high_inequality.head(5).iterrows():
    print(f"   {row['network_name']:25s} | Gini: {row['gini_coefficient']:.3f}")

print(f"\n{'='*80}")
print("✅ ANÁLISE GEOGRÁFICA CONCLUÍDA")
print(f"{'='*80}")
