#!/usr/bin/env python3
"""
Calcula intervalos de confiança (IC95%) via bootstrap para métricas agregadas.

Métricas:
- PageRank médio por rede
- Coeficiente de Gini por rede
- Modularidade média (Louvain vs Infomap)
- NMI e ARI médios
"""

import pandas as pd
import numpy as np
from scipy import stats

np.random.seed(42)

print("=" * 80)
print("CÁLCULO DE INTERVALOS DE CONFIANÇA (IC95%) - BOOTSTRAP")
print("=" * 80)

# ====================
# 1. CARREGAR DADOS
# ====================

# Carregar métricas globais
df_global = pd.read_csv('../results_complete_mining/data/global_metrics.csv')

# Carregar validação Louvain vs Infomap
try:
    df_louvain = pd.read_csv('../analysis/louvain_vs_infomap_metrics.csv')
except:
    df_louvain = None
    print("\n⚠️  Arquivo louvain_vs_infomap_metrics.csv não encontrado")

print(f"\n✓ Dados carregados: {len(df_global)} redes")

# ====================
# 2. FUNÇÃO BOOTSTRAP
# ====================

def bootstrap_ci(data, func=np.mean, n_boot=10000, alpha=0.05):
    """
    Calcula intervalo de confiança via bootstrap.

    Args:
        data: array de dados
        func: função para calcular estatística (default: média)
        n_boot: número de amostras bootstrap
        alpha: nível de significância (default: 0.05 para IC95%)

    Returns:
        (mean, lower, upper)
    """
    boot_samples = []

    for _ in range(n_boot):
        sample = np.random.choice(data, size=len(data), replace=True)
        boot_samples.append(func(sample))

    boot_samples = np.array(boot_samples)

    mean_val = func(data)
    lower = np.percentile(boot_samples, alpha/2 * 100)
    upper = np.percentile(boot_samples, (1 - alpha/2) * 100)

    return mean_val, lower, upper

# ====================
# 3. MÉTRICAS AGREGADAS POR GÊNERO
# ====================

print("\n" + "=" * 80)
print("IC95% PARA MÉTRICAS AGREGADAS POR GÊNERO")
print("=" * 80)

metrics_to_analyze = ['density', 'avg_clustering']

results_by_gender = []

for metric in metrics_to_analyze:
    if metric in df_global.columns:
        for gender in ['M', 'F']:
            data = df_global[df_global['gender'] == gender][metric].values

            if len(data) > 0:
                mean, lower, upper = bootstrap_ci(data)

                results_by_gender.append({
                    'Metric': metric,
                    'Gender': gender,
                    'Mean': mean,
                    'IC95_lower': lower,
                    'IC95_upper': upper,
                    'N': len(data)
                })

                print(f"\n{metric} ({gender}):")
                print(f"  Média: {mean:.6f}")
                print(f"  IC95%: [{lower:.6f}, {upper:.6f}]")

df_results_gender = pd.DataFrame(results_by_gender)

# ====================
# 4. VALIDAÇÃO LOUVAIN VS INFOMAP
# ====================

if df_louvain is not None:
    print("\n" + "=" * 80)
    print("IC95% PARA MÉTRICAS DE VALIDAÇÃO")
    print("=" * 80)

    validation_metrics = ['NMI', 'ARI', 'modularity_louvain', 'modularity_infomap']

    for metric in validation_metrics:
        if metric in df_louvain.columns:
            data = df_louvain[metric].dropna().values

            if len(data) > 0:
                mean, lower, upper = bootstrap_ci(data)

                print(f"\n{metric}:")
                print(f"  Média: {mean:.4f}")
                print(f"  IC95%: [{lower:.4f}, {upper:.4f}]")

# ====================
# 5. COMPARAÇÃO M/F COM IC95%
# ====================

print("\n" + "=" * 80)
print("COMPARAÇÃO M/F COM IC95%")
print("=" * 80)

comparison_results = []

for metric in ['density', 'avg_clustering']:
    if metric in df_global.columns:
        data_m = df_global[df_global['gender'] == 'M'][metric].values
        data_f = df_global[df_global['gender'] == 'F'][metric].values

        if len(data_m) > 0 and len(data_f) > 0:
            mean_m, lower_m, upper_m = bootstrap_ci(data_m)
            mean_f, lower_f, upper_f = bootstrap_ci(data_f)

            ratio = mean_f / mean_m if mean_m > 0 else 0

            comparison_results.append({
                'Metric': metric,
                'Mean_M': f"{mean_m:.6f}",
                'IC95_M': f"[{lower_m:.6f}, {upper_m:.6f}]",
                'Mean_F': f"{mean_f:.6f}",
                'IC95_F': f"[{lower_f:.6f}, {upper_f:.6f}]",
                'Ratio_F/M': f"{ratio:.2f}×"
            })

            print(f"\n{metric}:")
            print(f"  M: {mean_m:.6f} IC95% [{lower_m:.6f}, {upper_m:.6f}]")
            print(f"  F: {mean_f:.6f} IC95% [{lower_f:.6f}, {upper_f:.6f}]")
            print(f"  Razão F/M: {ratio:.2f}×")

df_comparison = pd.DataFrame(comparison_results)

# ====================
# 6. SALVAR RESULTADOS
# ====================

print("\n" + "=" * 80)
print("SALVANDO RESULTADOS")
print("=" * 80)

# Salvar CSVs
output_gender = '../results_complete_mining/data/confidence_intervals_by_gender.csv'
df_results_gender.to_csv(output_gender, index=False)
print(f"\n✓ Salvo: {output_gender}")

output_comparison = '../results_complete_mining/data/confidence_intervals_comparison_mf.csv'
df_comparison.to_csv(output_comparison, index=False)
print(f"✓ Salvo: {output_comparison}")

# Gerar tabela LaTeX
latex_table = r"""\begin{table}[H]
\centering
\small
\caption{Métricas agregadas com intervalos de confiança (IC95\%) via bootstrap}
\label{tab:confidence_intervals}
\begin{tabular}{lcccc}
\hline
\textbf{Métrica} & \textbf{M (Média)} & \textbf{IC95\% M} & \textbf{F (Média)} & \textbf{IC95\% F} \\
\hline
"""

for _, row in df_comparison.iterrows():
    metric_name = row['Metric'].replace('_', ' ').title()
    latex_table += f"{metric_name} & {row['Mean_M']} & {row['IC95_M']} & {row['Mean_F']} & {row['IC95_F']} \\\\\n"

latex_table += r"""\hline
\multicolumn{5}{l}{\footnotesize IC95\% calculado via bootstrap ($n=10.000$ amostras)} \\
\multicolumn{5}{l}{\footnotesize M: masculino ($n=6$ redes), F: feminino ($n=6$ redes)} \\
\end{tabular}
\end{table}
"""

latex_file = '../results_complete_mining/tables/tab_confidence_intervals.tex'
with open(latex_file, 'w', encoding='utf-8') as f:
    f.write(latex_table)

print(f"✓ Tabela LaTeX: {latex_file}")

print("\n" + "=" * 80)
print("CONCLUÍDO")
print("=" * 80)
