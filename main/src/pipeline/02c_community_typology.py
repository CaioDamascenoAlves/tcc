"""
Sistema de Tipologia de Comunidades - Componente 1

Este script classifica comunidades detectadas pelo algoritmo de Louvain em tipologias
interpretativas baseadas em múltiplas dimensões:

1. Performance (via CDF de PageRank): Elite vs Massa
2. Geografia (via HHI): Concentrada vs Intermediária vs Diversa
3. Temporalidade (via contagem de eras): Dinastia vs Transição vs Multi-Era
4. Concentração Bidimensional (HHI x Gini): 4 perfis de concentração

Entrada:
- community_profiles_enriched.csv
- community_members_detailed.csv

Saída:
- community_typology_classification.csv
- community_typology_summary.json
- community_cdf_analysis.csv
- community_concentration_profiles.csv
"""

import pandas as pd
import numpy as np
import json
from scipy import stats
from collections import Counter
import os

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def calculate_gini(values):
    """
    Calcula o índice de Gini para medir desigualdade.

    O índice de Gini varia de 0 (igualdade perfeita) a 1 (desigualdade máxima).
    Originalmente desenvolvido para medir desigualdade de renda, aqui aplicado
    a valores de PageRank para quantificar concentração de importância estrutural.

    Args:
        values (array-like): Valores numéricos (ex: PageRank)

    Returns:
        float: Índice de Gini (0-1)

    Referência:
        Cowell, F. A. (2011). Measuring Inequality. Oxford University Press.
    """
    if len(values) == 0:
        return 0.0

    # Remover zeros e ordenar
    values = np.array([v for v in values if v > 0])
    if len(values) == 0:
        return 0.0

    sorted_values = np.sort(values)
    n = len(sorted_values)

    # Fórmula do Gini
    cumsum = np.cumsum(sorted_values)
    gini = (2 * np.sum((np.arange(1, n+1)) * sorted_values)) / (n * np.sum(sorted_values)) - (n + 1) / n

    return gini


def calculate_cdf_inflection_point(values):
    """
    Identifica ponto de inflexão na CDF empírica para separar Elite/Massa.

    Usa a segunda derivada da CDF para detectar onde a distribuição
    muda de comportamento, indicando transição natural entre grupos.

    Args:
        values (array-like): Valores de PageRank da comunidade

    Returns:
        tuple: (threshold, percentile, inflection_detected)
    """
    if len(values) < 10:
        # Comunidade muito pequena, usar mediana
        return np.median(values), 50, False

    # Ordenar valores
    sorted_values = np.sort(values)
    n = len(sorted_values)

    # Calcular CDF empírica
    cdf = np.arange(1, n+1) / n

    # Calcular segunda derivada (diferenças de diferenças)
    # Smooth first para evitar ruído
    window_size = max(3, n // 20)  # 5% da amostra ou mínimo 3

    if n < window_size * 2:
        # Não há dados suficientes para smooth
        return np.percentile(values, 75), 75, False

    # Moving average para smooth
    def moving_average(x, w):
        return np.convolve(x, np.ones(w), 'valid') / w

    cdf_smooth = moving_average(cdf, window_size)
    values_smooth = moving_average(sorted_values, window_size)

    # Primeira derivada (taxa de mudança da CDF)
    first_deriv = np.diff(cdf_smooth)

    # Segunda derivada (aceleração da mudança)
    second_deriv = np.diff(first_deriv)

    if len(second_deriv) == 0:
        return np.percentile(values, 75), 75, False

    # Ponto de inflexão = onde segunda derivada é máxima (maior aceleração)
    inflection_idx = np.argmax(np.abs(second_deriv))

    # Ajustar índice para valores originais
    inflection_idx_adjusted = inflection_idx + window_size

    if inflection_idx_adjusted >= len(sorted_values):
        inflection_idx_adjusted = len(sorted_values) - 1

    threshold = sorted_values[inflection_idx_adjusted]
    percentile = (inflection_idx_adjusted / n) * 100

    # Considerar inflexão detectada se estiver entre 60-95 percentil
    # (fora disso, provavelmente é distribuição uniforme ou extremamente desigual)
    inflection_detected = 60 <= percentile <= 95

    if not inflection_detected:
        # Fallback: usar 75 percentil
        threshold = np.percentile(values, 75)
        percentile = 75

    return threshold, percentile, inflection_detected


def classify_performance_cdf(pagerank_values):
    """
    Classifica comunidade em ELITE ou MASSA usando análise de CDF.

    Args:
        pagerank_values (array-like): Valores de PageRank da comunidade

    Returns:
        tuple: (class, threshold, percentile, method)
    """
    threshold, percentile, inflection_detected = calculate_cdf_inflection_point(pagerank_values)

    method = "CDF_inflection" if inflection_detected else "percentile_75_fallback"

    # Elite = acima do threshold
    num_elite = np.sum(pagerank_values >= threshold)
    num_total = len(pagerank_values)

    elite_percentage = (num_elite / num_total) * 100

    # Classificação da comunidade como um todo
    # Se tem elite significativa (>15%) e inflexão detectada, é ELITE
    # Senão, é MASSA
    if elite_percentage >= 15 and inflection_detected:
        classification = "ELITE"
    else:
        classification = "MASSA"

    return classification, threshold, percentile, method


def classify_geography_hhi(hhi):
    """
    Classifica concentração geográfica baseado no índice HHI.

    Thresholds baseados em padrões antitruste:
    - HHI > 0.25: equivalente a ~4 países dominantes
    - HHI < 0.10: equivalente a ~10+ países equilibrados

    Args:
        hhi (float): Índice de Herfindahl-Hirschman

    Returns:
        str: CONCENTRADA, INTERMEDIÁRIA ou DIVERSA
    """
    if hhi > 0.25:
        return "CONCENTRADA"
    elif hhi >= 0.10:
        return "INTERMEDIÁRIA"
    else:
        return "DIVERSA"


def classify_temporality(num_eras, temporal_entropy):
    """
    Classifica extensão temporal da comunidade.

    Args:
        num_eras (int): Número de eras olímpicas distintas
        temporal_entropy (float): Entropia de Shannon da distribuição temporal

    Returns:
        str: DINASTIA, TRANSIÇÃO ou MULTI-ERA
    """
    if num_eras <= 2:
        return "DINASTIA"
    elif num_eras <= 4:
        return "TRANSIÇÃO"
    else:
        return "MULTI-ERA"


def classify_concentration_profile(hhi, gini_pr):
    """
    Classifica perfil bidimensional de concentração.

    Dimensão 1: Concentração Geográfica (HHI)
    Dimensão 2: Concentração Estrutural (Gini de PageRank)

    Thresholds calibrados empiricamente:
    - HHI: 0.15 (mediana do dataset, separa 50/50)
    - Gini PR: 0.35 (75º percentil, separa top 26% mais heterogêneos)

    Args:
        hhi (float): Índice HHI geográfico
        gini_pr (float): Gini de PageRank

    Returns:
        tuple: (quadrant, profile_label, interpretation)
    """
    # Thresholds calibrados
    hhi_threshold = 0.15
    gini_threshold = 0.35

    # Classificação
    hhi_high = hhi >= hhi_threshold
    gini_high = gini_pr >= gini_threshold

    if hhi_high and gini_high:
        return "Q1", "Hegemonia-Superstars", "Dominância nacional com emergência de superstars individuais"
    elif (not hhi_high) and gini_high:
        return "Q2", "Elite-Global", "Diversidade geográfica com poucos talentos excepcionais"
    elif (not hhi_high) and (not gini_high):
        return "Q3", "Equilíbrio-Global", "Diversidade geográfica com importância distribuída"
    else:  # hhi_high and not gini_high
        return "Q4", "Hegemonia-Sistêmica", "Dominância nacional com importância distribuída (sistema forte)"


def generate_typology_label(perf_class, geo_class, temp_class):
    """
    Gera label interpretativo combinando as 3 dimensões.

    Args:
        perf_class (str): ELITE ou MASSA
        geo_class (str): CONCENTRADA, INTERMEDIÁRIA ou DIVERSA
        temp_class (str): DINASTIA, TRANSIÇÃO ou MULTI-ERA

    Returns:
        str: Label combinado (ex: "Elite-Concentrada-Multi-Era")
    """
    return f"{perf_class.title()}-{geo_class.title()}-{temp_class.title()}"


def generate_typology_description(perf_class, geo_class, temp_class, conc_profile_label):
    """
    Gera descrição interpretativa da tipologia.

    Args:
        perf_class (str): Classificação de performance
        geo_class (str): Classificação geográfica
        temp_class (str): Classificação temporal
        conc_profile_label (str): Label do perfil de concentração

    Returns:
        str: Descrição interpretativa
    """
    descriptions = {
        ("ELITE", "CONCENTRADA", "DINASTIA"): "Elite concentrada geograficamente em período específico",
        ("ELITE", "CONCENTRADA", "MULTI-ERA"): "Hegemonia nacional sustentada ao longo de múltiplas eras",
        ("ELITE", "DIVERSA", "MULTI-ERA"): "Elite global persistente com diversidade geográfica",
        ("MASSA", "DIVERSA", "MULTI-ERA"): "Competição global equilibrada sem hegemonias claras",
        ("MASSA", "CONCENTRADA", "DINASTIA"): "Dominância regional em período específico",
    }

    # Buscar descrição específica ou gerar genérica
    key = (perf_class, geo_class, temp_class)
    if key in descriptions:
        return descriptions[key]
    else:
        return f"{perf_class.title()} performance, {geo_class.lower()} geograficamente, {temp_class.lower()}"


# ==============================================================================
# PROCESSAMENTO PRINCIPAL
# ==============================================================================

def analyze_community_typology(base_dir='../../results'):
    """
    Executa análise completa de tipologia de comunidades.

    Args:
        base_dir (str): Diretório com os arquivos de entrada

    Returns:
        tuple: (typology_df, summary_dict)
    """
    print("=" * 80)
    print("ANÁLISE DE TIPOLOGIA DE COMUNIDADES")
    print("=" * 80)

    # Carregar dados
    print("\n[1/5] Carregando dados...")
    profiles_path = os.path.join(base_dir, 'community_profiles_enriched.csv')
    members_path = os.path.join(base_dir, 'community_members_detailed.csv')

    if not os.path.exists(profiles_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {profiles_path}")
    if not os.path.exists(members_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {members_path}")

    profiles_df = pd.read_csv(profiles_path)
    members_df = pd.read_csv(members_path)

    print(f"   Carregados: {len(profiles_df)} comunidades, {len(members_df)} atletas")

    # Análise de tipologia
    print("\n[2/5] Calculando tipologias...")

    typology_results = []
    cdf_analysis = []

    for idx, row in profiles_df.iterrows():
        community_id = row['community_id']
        sport = row['sport']
        sex = row['sex']

        # Obter membros da comunidade
        community_members = members_df[
            (members_df['community_id'] == community_id) &
            (members_df['sport'] == sport) &
            (members_df['sex'] == sex)
        ]

        if len(community_members) == 0:
            print(f"   [AVISO] Comunidade {community_id} ({sport}-{sex}) sem membros!")
            continue

        pagerank_values = community_members['pagerank'].values

        # 1. Classificação de Performance (CDF)
        perf_class, perf_threshold, perf_percentile, perf_method = classify_performance_cdf(pagerank_values)

        # 2. Calcular Gini de PageRank
        gini_pr = calculate_gini(pagerank_values)

        # 3. Classificação Geográfica (HHI já calculado)
        geo_class = classify_geography_hhi(row['geographic_hhi'])

        # 4. Classificação Temporal
        temp_class = classify_temporality(
            row['year_end'] - row['year_start'],  # Aproximação de número de eras
            row['temporal_entropy']
        )

        # Calcular número de eras mais precisamente
        years = community_members['year'].unique()
        eras = set()
        for year in years:
            if year < 1920:
                eras.add("Pioneira")
            elif year < 1950:
                eras.add("Entre-Guerras")
            elif year < 1980:
                eras.add("Guerra-Fria")
            elif year < 2000:
                eras.add("Pós-Guerra-Fria")
            else:
                eras.add("Moderna")
        num_eras = len(eras)

        # Re-classificar temporalidade com contagem precisa
        temp_class = classify_temporality(num_eras, row['temporal_entropy'])

        # 5. Perfil de Concentração Bidimensional
        quadrant, conc_profile_label, conc_interpretation = classify_concentration_profile(
            row['geographic_hhi'],
            gini_pr
        )

        # 6. Gerar labels
        typology_label = generate_typology_label(perf_class, geo_class, temp_class)
        typology_description = generate_typology_description(
            perf_class, geo_class, temp_class, conc_profile_label
        )

        # Armazenar resultados
        typology_results.append({
            'sport': sport,
            'sex': sex,
            'community_id': community_id,
            'size': row['size'],

            # Performance
            'performance_class': perf_class,
            'performance_threshold': perf_threshold,
            'performance_percentile': perf_percentile,
            'performance_method': perf_method,

            # Geografia
            'geographic_class': geo_class,
            'hhi': row['geographic_hhi'],

            # Estrutural (Gini PageRank)
            'gini_pagerank': gini_pr,

            # Temporal
            'temporal_class': temp_class,
            'num_eras': num_eras,
            'temporal_entropy': row['temporal_entropy'],

            # Tipologias
            'typology_label': typology_label,
            'concentration_profile': conc_profile_label,
            'concentration_quadrant': quadrant,
            'concentration_interpretation': conc_interpretation,
            'typology_description': typology_description,

            # Métricas adicionais
            'pagerank_mean': row['pagerank_mean'],
            'pagerank_cv': row['pagerank_cv'],
            'dominant_country': row['dominant_country'],
            'country_dominance': row['country_dominance'],
            'dominant_era': row['dominant_era']
        })

        # Armazenar análise CDF
        pr_sorted = np.sort(pagerank_values)
        cdf_analysis.append({
            'community_id': community_id,
            'sport': sport,
            'sex': sex,
            'pagerank_min': pr_sorted[0],
            'pagerank_25': np.percentile(pr_sorted, 25),
            'pagerank_50': np.percentile(pr_sorted, 50),
            'pagerank_75': np.percentile(pr_sorted, 75),
            'pagerank_max': pr_sorted[-1],
            'cdf_inflection_point': perf_threshold,
            'cdf_inflection_percentile': perf_percentile,
            'gini_coefficient': gini_pr
        })

    typology_df = pd.DataFrame(typology_results)
    cdf_df = pd.DataFrame(cdf_analysis)

    print(f"   Processadas {len(typology_df)} comunidades")

    # Gerar resumo estatístico
    print("\n[3/5] Gerando resumos estatísticos...")

    summary = {
        'total_communities': len(typology_df),
        'total_athletes': len(members_df),
        'sports': list(typology_df['sport'].unique()),

        'distribution': {
            'by_performance': typology_df['performance_class'].value_counts().to_dict(),
            'by_geography': typology_df['geographic_class'].value_counts().to_dict(),
            'by_temporality': typology_df['temporal_class'].value_counts().to_dict(),
            'by_concentration_profile': typology_df['concentration_profile'].value_counts().to_dict()
        },

        'typologies_found': [],

        'concentration_profiles': {
            'Q1_Hegemonia_Superstars': {
                'count': len(typology_df[typology_df['concentration_quadrant'] == 'Q1']),
                'examples': typology_df[typology_df['concentration_quadrant'] == 'Q1'][
                    ['sport', 'sex', 'community_id', 'hhi', 'gini_pagerank']
                ].head(3).to_dict('records')
            },
            'Q2_Elite_Global': {
                'count': len(typology_df[typology_df['concentration_quadrant'] == 'Q2']),
                'examples': typology_df[typology_df['concentration_quadrant'] == 'Q2'][
                    ['sport', 'sex', 'community_id', 'hhi', 'gini_pagerank']
                ].head(3).to_dict('records')
            },
            'Q3_Equilibrio_Global': {
                'count': len(typology_df[typology_df['concentration_quadrant'] == 'Q3']),
                'examples': typology_df[typology_df['concentration_quadrant'] == 'Q3'][
                    ['sport', 'sex', 'community_id', 'hhi', 'gini_pagerank']
                ].head(3).to_dict('records')
            },
            'Q4_Hegemonia_Sistemica': {
                'count': len(typology_df[typology_df['concentration_quadrant'] == 'Q4']),
                'examples': typology_df[typology_df['concentration_quadrant'] == 'Q4'][
                    ['sport', 'sex', 'community_id', 'hhi', 'gini_pagerank']
                ].head(3).to_dict('records')
            }
        },

        'metrics': {
            'gini_pagerank': {
                'mean': float(typology_df['gini_pagerank'].mean()),
                'std': float(typology_df['gini_pagerank'].std()),
                'min': float(typology_df['gini_pagerank'].min()),
                'max': float(typology_df['gini_pagerank'].max())
            },
            'hhi_geographic': {
                'mean': float(typology_df['hhi'].mean()),
                'std': float(typology_df['hhi'].std()),
                'min': float(typology_df['hhi'].min()),
                'max': float(typology_df['hhi'].max())
            }
        }
    }

    # Tipologias mais comuns
    typology_counts = typology_df['typology_label'].value_counts()
    for typology, count in typology_counts.head(10).items():
        examples = typology_df[typology_df['typology_label'] == typology][
            ['sport', 'sex', 'community_id', 'size']
        ].head(3).to_dict('records')

        summary['typologies_found'].append({
            'label': typology,
            'count': int(count),
            'percentage': float(count / len(typology_df) * 100),
            'examples': examples
        })

    # Exportar resultados
    print("\n[4/5] Exportando resultados...")

    # CSV principal
    output_path = os.path.join(base_dir, 'community_typology_classification.csv')
    typology_df.to_csv(output_path, index=False)
    print(f"   [OK] {output_path}")

    # Análise CDF
    cdf_path = os.path.join(base_dir, 'community_cdf_analysis.csv')
    cdf_df.to_csv(cdf_path, index=False)
    print(f"   [OK] {cdf_path}")

    # Perfis de concentração
    conc_profiles = typology_df[[
        'sport', 'sex', 'community_id', 'hhi', 'gini_pagerank',
        'concentration_quadrant', 'concentration_profile', 'concentration_interpretation'
    ]].copy()
    conc_path = os.path.join(base_dir, 'community_concentration_profiles.csv')
    conc_profiles.to_csv(conc_path, index=False)
    print(f"   [OK] {conc_path}")

    # JSON resumo
    summary_path = os.path.join(base_dir, 'community_typology_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"   [OK] {summary_path}")

    # Estatísticas finais
    print("\n[5/5] Resumo da Análise")
    print("=" * 80)
    print(f"\nTotal de Comunidades Classificadas: {len(typology_df)}")
    print(f"\nDistribuição de Performance:")
    for perf_class, count in summary['distribution']['by_performance'].items():
        pct = count / len(typology_df) * 100
        print(f"  • {perf_class}: {count} ({pct:.1f}%)")

    print(f"\nDistribuição Geográfica:")
    for geo_class, count in summary['distribution']['by_geography'].items():
        pct = count / len(typology_df) * 100
        print(f"  • {geo_class}: {count} ({pct:.1f}%)")

    print(f"\nDistribuição Temporal:")
    for temp_class, count in summary['distribution']['by_temporality'].items():
        pct = count / len(typology_df) * 100
        print(f"  • {temp_class}: {count} ({pct:.1f}%)")

    print(f"\nPerfis de Concentração Bidimensional:")
    for profile, count in summary['distribution']['by_concentration_profile'].items():
        pct = count / len(typology_df) * 100
        print(f"  • {profile}: {count} ({pct:.1f}%)")

    print(f"\nMétricas de Concentração:")
    print(f"  • Gini PageRank médio: {summary['metrics']['gini_pagerank']['mean']:.3f}")
    print(f"  • HHI Geográfico médio: {summary['metrics']['hhi_geographic']['mean']:.3f}")

    print("\n" + "=" * 80)
    print("ANÁLISE CONCLUÍDA COM SUCESSO!")
    print("=" * 80 + "\n")

    return typology_df, summary


# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================

if __name__ == "__main__":
    # Executar análise
    typology_df, summary = analyze_community_typology(base_dir='../../results')

    # Exibir top 10 tipologias
    print("\nTop 10 Tipologias Mais Comuns:")
    print("-" * 80)
    for i, item in enumerate(summary['typologies_found'][:10], 1):
        print(f"{i}. {item['label']}: {item['count']} comunidades ({item['percentage']:.1f}%)")
        for ex in item['examples']:
            print(f"   -> {ex['sport']}-{ex['sex']}, Comunidade {ex['community_id']} ({ex['size']} atletas)")

    print("\n" + "=" * 80)
    print("Arquivos gerados em: ../../results/")
    print("  - community_typology_classification.csv")
    print("  - community_cdf_analysis.csv")
    print("  - community_concentration_profiles.csv")
    print("  - community_typology_summary.json")
    print("=" * 80)
