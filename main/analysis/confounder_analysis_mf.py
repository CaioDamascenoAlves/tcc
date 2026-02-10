#!/usr/bin/env python3
"""
Análise de Confounders M/F

Implementa regressão linear múltipla para controlar variáveis confundidoras
na comparação de densidade entre redes masculinas e femininas.

Variáveis:
- Variável dependente: densidade
- Variável independente principal: gênero (M=0, F=1)
- Confounders:
  * anos_atividade: quantos anos o evento esteve ativo nas olimpíadas
  * tamanho_campo: número de nós na rede (log-transformado)
  * tipo_esporte: individual vs team
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ====================
# 1. CARREGAR DADOS
# ====================

print("=" * 80)
print("ANÁLISE DE CONFOUNDERS M/F - DENSIDADE")
print("=" * 80)

# Carregar dados de métricas globais
df_metrics = pd.read_csv('../results_complete_mining/data/global_metrics.csv')

# Carregar dataset original para calcular anos de atividade
df_athletes = pd.read_csv('../data/athlete_events_cleaned.csv')

print(f"\n✓ Dados carregados: {len(df_metrics)} redes")
print(f"✓ Dataset original: {len(df_athletes)} registros")

# ====================
# 2. CALCULAR ANOS DE ATIVIDADE
# ====================

print("\n" + "=" * 80)
print("CALCULANDO ANOS DE ATIVIDADE POR EVENTO")
print("=" * 80)

# Filtrar apenas medalhistas
df_medalists = df_athletes[df_athletes['Medal'].notna()].copy()

# Agrupar por (Sport, Event_Normalized) e calcular anos
temporal_info = df_medalists.groupby('Event_Normalized')['Year'].agg([
    ('min_year', 'min'),
    ('max_year', 'max'),
    ('num_editions', 'nunique')
]).reset_index()

# Calcular anos de atividade
temporal_info['anos_atividade'] = temporal_info['max_year'] - temporal_info['min_year'] + 4

# Extrair gênero do Event_Normalized (primeiro caractere)
temporal_info['gender'] = temporal_info['Event_Normalized'].str[0]

print("\nAnos de atividade por evento:")
print(temporal_info[['Event_Normalized', 'min_year', 'max_year', 'anos_atividade']].to_string(index=False))

# ====================
# 3. PREPARAR DATASET PARA REGRESSÃO
# ====================

print("\n" + "=" * 80)
print("PREPARANDO DATASET PARA REGRESSÃO")
print("=" * 80)

# Criar mapeamento manual entre nomes das redes e Event_Normalized
name_mapping = {
    'M Football': 'M Football Men\'s Football',
    'F Football': 'F Football Women\'s Football',
    'M Basketball': 'M Basketball Men\'s Basketball',
    'F Basketball': 'F Basketball Women\'s Basketball',
    'M 100m': 'M 100m',
    'F 100m': 'F 100m',
    'M 100m Freestyle': 'M 100m Freestyle',
    'F 100m Freestyle': 'F 100m Freestyle',
    'M -90kg': 'M -90kg',
    'F -70kg': 'F -70kg',
    'M Welter': 'M Welter (63-69kg)',
    'F Middle': 'F Middle (69-75kg)'
}

# Merge dados
df_analysis = df_metrics.copy()
df_analysis['Event_Normalized'] = df_analysis['name'].map(name_mapping)

# Adicionar informações temporais
df_analysis = df_analysis.merge(
    temporal_info[['Event_Normalized', 'anos_atividade', 'num_editions']],
    on='Event_Normalized',
    how='left'
)

# Verificar se há valores faltantes
missing = df_analysis['anos_atividade'].isna().sum()
if missing > 0:
    print(f"\n⚠️  {missing} redes sem informação temporal - preenchendo com média do esporte")
    # Preencher com média do esporte
    for sport in df_analysis['sport'].unique():
        mask = (df_analysis['sport'] == sport) & (df_analysis['anos_atividade'].isna())
        mean_years = df_analysis[df_analysis['sport'] == sport]['anos_atividade'].mean()
        df_analysis.loc[mask, 'anos_atividade'] = mean_years

# Criar variáveis dummy
df_analysis['gender_numeric'] = (df_analysis['gender'] == 'F').astype(int)  # F=1, M=0
df_analysis['type_numeric'] = (df_analysis['type'] == 'team').astype(int)   # team=1, individual=0

# Log-transformar tamanho do campo (evitar log(0))
df_analysis['log_nodes'] = np.log(df_analysis['nodes'] + 1)
df_analysis['log_anos'] = np.log(df_analysis['anos_atividade'] + 1)

# Dataset completo para análise
df_reg = df_analysis[[
    'name', 'sport', 'gender', 'type',
    'density', 'nodes', 'anos_atividade',
    'gender_numeric', 'type_numeric', 'log_nodes', 'log_anos'
]].dropna()

print(f"\n✓ Dataset final: {len(df_reg)} redes")
print(f"  - Masculinas: {(df_reg['gender'] == 'M').sum()}")
print(f"  - Femininas: {(df_reg['gender'] == 'F').sum()}")
print(f"  - Individuais: {(df_reg['type'] == 'individual').sum()}")
print(f"  - Coletivas: {(df_reg['type'] == 'team').sum()}")

# ====================
# 4. ANÁLISE DESCRITIVA
# ====================

print("\n" + "=" * 80)
print("ESTATÍSTICAS DESCRITIVAS POR GÊNERO")
print("=" * 80)

desc_stats = df_reg.groupby('gender').agg({
    'density': ['mean', 'std', 'median'],
    'nodes': ['mean', 'std'],
    'anos_atividade': ['mean', 'std']
}).round(4)

print("\n", desc_stats)

# Teste t simples (sem controles)
density_M = df_reg[df_reg['gender'] == 'M']['density']
density_F = df_reg[df_reg['gender'] == 'F']['density']

t_stat, p_value = stats.ttest_ind(density_M, density_F)

print("\n" + "-" * 80)
print("TESTE T INDEPENDENTE (SEM CONTROLES)")
print("-" * 80)
print(f"Densidade média M: {density_M.mean():.4f}")
print(f"Densidade média F: {density_F.mean():.4f}")
print(f"t-statistic: {t_stat:.3f}")
print(f"p-value: {p_value:.4f}")
print(f"Significativo? {'SIM' if p_value < 0.05 else 'NÃO'} (α=0.05)")

# ====================
# 5. REGRESSÃO LINEAR MÚLTIPLA
# ====================

print("\n" + "=" * 80)
print("MODELO DE REGRESSÃO LINEAR MÚLTIPLA")
print("=" * 80)
print("\nModelo: densidade ~ gênero + log(nodes) + log(anos_atividade) + tipo_esporte")

# Preparar variáveis
X = df_reg[['gender_numeric', 'log_nodes', 'log_anos', 'type_numeric']].values
y = df_reg['density'].values

# Padronizar para melhorar interpretação
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Ajustar modelo
model = LinearRegression()
model.fit(X_scaled, y)

# Coeficientes
coefs = pd.DataFrame({
    'Variável': ['Gênero (F)', 'log(Nodes)', 'log(Anos)', 'Tipo (Team)'],
    'Coeficiente': model.coef_,
    'Coef_abs': np.abs(model.coef_)
}).sort_values('Coef_abs', ascending=False)

print(f"\nIntercepto: {model.intercept_:.6f}")
print("\nCoeficientes (padronizados):")
print(coefs[['Variável', 'Coeficiente']].to_string(index=False))

# R² do modelo
r2 = model.score(X_scaled, y)
print(f"\nR² do modelo: {r2:.4f}")

# ====================
# 6. CÁLCULO DE P-VALORES (Bootstrap)
# ====================

print("\n" + "=" * 80)
print("TESTE DE SIGNIFICÂNCIA DOS COEFICIENTES (Bootstrap)")
print("=" * 80)

n_bootstrap = 1000
np.random.seed(42)

# Bootstrap para calcular p-valores
bootstrap_coefs = []

for i in range(n_bootstrap):
    # Amostra com reposição
    indices = np.random.choice(len(X_scaled), size=len(X_scaled), replace=True)
    X_boot = X_scaled[indices]
    y_boot = y[indices]

    # Ajustar modelo
    model_boot = LinearRegression()
    model_boot.fit(X_boot, y_boot)
    bootstrap_coefs.append(model_boot.coef_)

bootstrap_coefs = np.array(bootstrap_coefs)

# Calcular p-valores (teste bicaudal)
p_values = []
for i in range(len(model.coef_)):
    # Proporção de bootstraps onde coef tem sinal oposto
    p_val = 2 * min(
        (bootstrap_coefs[:, i] <= 0).mean(),
        (bootstrap_coefs[:, i] >= 0).mean()
    )
    p_values.append(p_val)

# Tabela de resultados
results_table = pd.DataFrame({
    'Variável': ['Gênero (F=1)', 'log(Nodes)', 'log(Anos)', 'Tipo (Team=1)'],
    'Coeficiente': model.coef_,
    'p-valor': p_values,
    'Significativo': ['***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.10 else 'NS' for p in p_values]
})

print("\nResultados:")
print(results_table.to_string(index=False))
print("\nLegenda: *** p<0.01  ** p<0.05  * p<0.10  NS não significativo")

# ====================
# 7. INTERPRETAÇÃO
# ====================

print("\n" + "=" * 80)
print("INTERPRETAÇÃO")
print("=" * 80)

gender_coef = model.coef_[0]
gender_pval = p_values[0]

if gender_pval < 0.05:
    print(f"\n✓ EFEITO DE GÊNERO É SIGNIFICATIVO (p={gender_pval:.4f})")
    print(f"  Coeficiente: {gender_coef:.4f}")

    if gender_coef > 0:
        print(f"\n  → Redes femininas têm densidade MAIOR que masculinas,")
        print(f"    MESMO após controlar para:")
        print(f"    - Tamanho da rede (log nodes)")
        print(f"    - Anos de atividade (log anos)")
        print(f"    - Tipo de esporte (individual vs coletivo)")
        print(f"\n  → Este é um EFEITO REAL DE GÊNERO, não um artefato de confounders.")
    else:
        print(f"\n  → Redes femininas têm densidade MENOR que masculinas,")
        print(f"    mesmo após controlar para confounders.")
else:
    print(f"\n✗ EFEITO DE GÊNERO NÃO É SIGNIFICATIVO (p={gender_pval:.4f})")
    print(f"\n  → A diferença observada na densidade M/F pode ser explicada por:")
    print(f"    - Diferenças no tamanho das redes")
    print(f"    - Diferenças nos anos de atividade")
    print(f"    - Diferenças na tipologia (individual vs coletivo)")
    print(f"\n  → NÃO há evidência de efeito independente do gênero.")

# ====================
# 8. SALVAR RESULTADOS
# ====================

print("\n" + "=" * 80)
print("SALVANDO RESULTADOS")
print("=" * 80)

# Salvar dataset completo
output_file = '../results_complete_mining/data/confounder_analysis_data.csv'
df_reg.to_csv(output_file, index=False)
print(f"\n✓ Dataset salvo: {output_file}")

# Salvar tabela de resultados
results_file = '../results_complete_mining/data/confounder_regression_results.csv'
results_table.to_csv(results_file, index=False)
print(f"✓ Resultados salvos: {results_file}")

# ====================
# 9. GERAR TABELA LATEX
# ====================

print("\n" + "=" * 80)
print("GERANDO TABELA LATEX")
print("=" * 80)

latex_table = r"""\begin{table}[h]
\centering
\caption{Análise de regressão: efeito do gênero na densidade da rede controlando para confounders}
\label{tab:confounder_regression}
\begin{tabular}{lrrr}
\hline
\textbf{Variável} & \textbf{Coeficiente} & \textbf{p-valor} & \textbf{Sig.} \\
\hline
"""

for _, row in results_table.iterrows():
    latex_table += f"{row['Variável']} & {row['Coeficiente']:.4f} & {row['p-valor']:.4f} & {row['Significativo']} \\\\\n"

latex_table += r"""\hline
\end{tabular}
\begin{tablenotes}
\small
\item Modelo: $\text{densidade} \sim \beta_0 + \beta_1 \cdot \text{gênero} + \beta_2 \cdot \log(\text{nodes}) + \beta_3 \cdot \log(\text{anos}) + \beta_4 \cdot \text{tipo}$
\item $R^2 = """ + f"{r2:.4f}" + r"""$
\item Gênero: F=1, M=0; Tipo: Team=1, Individual=0
\item p-valores calculados via bootstrap ($n=1000$)
\item *** $p<0.01$, ** $p<0.05$, * $p<0.10$, NS não significativo
\end{tablenotes}
\end{table}
"""

latex_file = '../results_complete_mining/tables/tab_confounder_regression.tex'
with open(latex_file, 'w', encoding='utf-8') as f:
    f.write(latex_table)

print(f"\n✓ Tabela LaTeX salva: {latex_file}")

# ====================
# 10. SUMÁRIO FINAL
# ====================

print("\n" + "=" * 80)
print("SUMÁRIO EXECUTIVO")
print("=" * 80)

print(f"""
COMPARAÇÃO DENSIDADE M/F:
- Densidade média M: {density_M.mean():.4f}
- Densidade média F: {density_F.mean():.4f}
- Razão F/M: {density_F.mean() / density_M.mean():.2f}x
- Teste t simples: t={t_stat:.3f}, p={p_value:.4f}

REGRESSÃO COM CONTROLES:
- R² do modelo: {r2:.4f}
- Coeficiente gênero: {gender_coef:.4f}
- p-valor gênero: {gender_pval:.4f}
- Efeito significativo? {'SIM' if gender_pval < 0.05 else 'NÃO'}

CONCLUSÃO:
""")

if gender_pval < 0.05 and gender_coef > 0:
    print("A maior densidade em redes femininas é um EFEITO REAL de gênero,")
    print("não explicado por diferenças em tamanho de rede, anos de atividade,")
    print("ou tipologia esportiva.")
elif gender_pval < 0.05 and gender_coef < 0:
    print("Redes masculinas têm densidade maior após controlar para confounders.")
else:
    print("A diferença de densidade M/F é ESPÚRIA, explicada por confounders.")

print("\n" + "=" * 80)
print("ANÁLISE CONCLUÍDA")
print("=" * 80)
