"""
Gerador de Narrativas Automáticas para Comunidades - Componente 2

Este script transforma métricas numéricas em histórias interpretativas,
contextualizando os dados com significado histórico-esportivo.

Entrada:
- community_typology_classification.csv (Componente 1)
- community_profiles_enriched.csv
- community_members_detailed.csv

Saída:
- community_narratives.json
- community_narratives_summary.txt
"""

import pandas as pd
import numpy as np
import json
import os
from collections import Counter

# ==============================================================================
# BASE DE CONHECIMENTO HISTÓRICO
# ==============================================================================

HISTORICAL_CONTEXT = {
    "Era Pioneira (1896-1919)": {
        "context": "Início dos Jogos Olímpicos modernos com participação limitada a países europeus e norte-americanos. Amadorismo estrito, infraestrutura precária, técnicas rudimentares.",
        "Swimming": "Eventos em águas abertas, técnicas primitivas. Crawl ainda não padronizado. Dominância inicial britânica e nórdica.",
        "Basketball": "Esporte ainda não inventado (criado em 1891, incluído em 1936).",
        "Football": "Participação limitada, dominância europeia inicial."
    },

    "Entre Guerras (1920-1949)": {
        "context": "Período marcado por duas guerras mundiais com interrupção dos jogos (1916, 1940, 1944). Emergência dos EUA como potência esportiva.",
        "Swimming": "Era Johnny Weissmuller - revoluciona técnica de crawl. Programas universitários americanos (NCAA) começam dominância. Primeiras piscinas olímpicas de 50m.",
        "Basketball": "Inclusão oficial em Berlim 1936. Dominância americana absoluta desde o início.",
        "Football": "Consolidação do torneio, rivalidades europeias intensas."
    },

    "Guerra Fria (1950-1979)": {
        "context": "Competição ideológica EUA-URSS transformou esporte em campo de batalha política. Investimento massivo em programas estatais, profissionalização disfarçada, doping sistemático no bloco soviético.",
        "Swimming": "Auge da hegemonia americana. Mark Spitz conquista 7 ouros históricos em Munique 1972. Confronto EUA vs GDR (doping sistemático). Análise biomecânica, treino científico emergem.",
        "Basketball": "Hegemonia absoluta americana quebrada apenas em Munique 1972 (polêmica URSS). Confronto de sistemas: capitalista vs socialista.",
        "Football": "Disputas entre blocos: amadores do leste europeu vs profissionais disfarçados. Hungria (1952-1968) e URSS dominam."
    },

    "Pós-Guerra Fria (1980-1999)": {
        "context": "Colapso da URSS, fim das restrições de profissionalismo (1992 Barcelona - Dream Team). Globalização acelerada, comercialização do esporte olímpico.",
        "Swimming": "Transição para era moderna. Matt Biondi domina anos 1980s. Emergência de potências secundárias (AUS, CHN). Polêmicas de doping continuam (GDR legacy).",
        "Basketball": "Dream Team 1992 - profissionais da NBA dominam. Globalização do basquete com emergência europeia (ESP, LTU) e argentina.",
        "Football": "Restrições etárias (sub-23) mudam natureza do torneio a partir de 1992. Descentralização da competitividade."
    },

    "Era Moderna (2000-2016)": {
        "context": "Profissionalização completa, tecnologia wearable, análise de vídeo avançada, globalização da participação. Escândalos de doping (RUSADA) e pressões por fair play.",
        "Swimming": "Era Michael Phelps - 8 ouros Beijing 2008 supera Spitz. Polêmica dos maiôs tecnológicos (2008-2009). China emerge como potência. Globalização: múltiplos centros de excelência.",
        "Basketball": "Consolidação da hegemonia americana com estrelas NBA. Competitividade europeia aumenta (ESP campeã 2008). Argentina medalha 2004/2008.",
        "Football": "Torneio sub-23 consolidado. Brasil busca ouro inédito (conquista 2016). Distribuição global de medalhas aumenta."
    }
}

# ==============================================================================
# FUNÇÕES DE INTERPRETAÇÃO
# ==============================================================================

def interpret_temporal_diversity(temporal_entropy, num_eras):
    """Interpreta entropia temporal e número de eras"""
    if temporal_entropy > 2.5:
        return "alta diversidade temporal, abrangendo múltiplas gerações de atletas"
    elif temporal_entropy > 1.8:
        return "moderada diversidade temporal, com presença em múltiplas eras"
    else:
        return "concentração temporal, caracterizando período específico"

def interpret_geographic_concentration(hhi, dominant_country, dominance_pct):
    """Interpreta concentração geográfica"""
    if hhi > 0.25:
        return f"alta concentração geográfica com hegemonia de {dominant_country} ({dominance_pct:.1f}%), refletindo investimento institucional histórico ou domínio técnico específico"
    elif hhi > 0.15:
        return f"concentração geográfica moderada com dominância de {dominant_country} ({dominance_pct:.1f}%), indicando centro de excelência estabelecido mas com competição secundária"
    else:
        return f"diversidade geográfica significativa sem hegemonia clara (líder {dominant_country} com apenas {dominance_pct:.1f}%), caracterizando competição globalizada"

def interpret_performance_heterogeneity(gini_pr, cv_pr):
    """Interpreta heterogeneidade de performance via Gini e CV"""
    if gini_pr > 0.40:
        return "alta heterogeneidade de importância estrutural, com superstars claramente destacados concentrando centralidade desproporcional"
    elif gini_pr > 0.30:
        return "moderada heterogeneidade de importância, com líderes identificáveis mas sem dominância extrema"
    else:
        return "baixa heterogeneidade de importância, indicando distribuição equilibrada característica de dinâmica coletiva ou competição nivelada"

def interpret_concentration_profile(quadrant, profile_label, hhi, gini_pr):
    """Interpreta perfil bidimensional de concentração"""
    interpretations = {
        "Q1": f"Padrão de HEGEMONIA COM SUPERSTARS: concentração geográfica (HHI={hhi:.3f}) combinada com concentração estrutural (Gini={gini_pr:.3f}) caracteriza dinâmica onde investimento institucional nacional cria condições para emergência de talentos geracionais excepcionais. Típico de esportes individuais com programas nacionais consolidados.",

        "Q2": f"Padrão de ELITE GLOBAL: diversidade geográfica (HHI={hhi:.3f}) mas persistência de superstars (Gini={gini_pr:.3f}) indica globalização do esporte sem perda da dinâmica individual-superstar. Talentos excepcionais emergem de múltiplos centros de excelência distribuídos globalmente.",

        "Q3": f"Padrão de EQUILÍBRIO GLOBAL: diversidade geográfica (HHI={hhi:.3f}) combinada com distribuição equilibrada de importância (Gini={gini_pr:.3f}) caracteriza competição madura globalizada. Típico de esportes coletivos onde múltiplos sistemas nacionais competem sem dominância individual clara.",

        "Q4": f"Padrão de HEGEMONIA SISTÊMICA: concentração geográfica (HHI={hhi:.3f}) mas distribuição equilibrada de importância (Gini={gini_pr:.3f}) revela hegemonia por SISTEMA ao invés de talentos isolados. País domina através de pipeline contínuo de atletas competitivos gerados por infraestrutura institucional robusta."
    }
    return interpretations.get(quadrant, "Padrão estrutural específico desta comunidade.")

def interpret_bridge_athletes(num_bridges, total_size):
    """Interpreta atletas-ponte"""
    pct = (num_bridges / total_size) * 100
    if pct > 12:
        return f"{num_bridges} atletas-ponte ({pct:.1f}%) - proporção elevada indica estrutura modular com conectores críticos entre sub-grupos especializados ou eras distintas"
    elif pct > 7:
        return f"{num_bridges} atletas-ponte ({pct:.1f}%) - presença moderada de conectores estruturais, típico de comunidades com divisões internas sutis"
    else:
        return f"{num_bridges} atletas-ponte ({pct:.1f}%) - baixa necessidade de pontes indica comunidade coesa ou altamente densa sem fragmentação significativa"

def get_historical_context(era, sport):
    """Retorna contexto histórico relevante"""
    if era in HISTORICAL_CONTEXT:
        era_data = HISTORICAL_CONTEXT[era]
        sport_context = era_data.get(sport, "")
        general_context = era_data.get("context", "")

        if sport_context:
            return f"{sport_context} Contexto geral: {general_context}"
        else:
            return general_context
    return "Período histórico específico com características competitivas particulares."

# ==============================================================================
# GERADOR DE NARRATIVAS
# ==============================================================================

def generate_community_narrative(community_row, members_df, typology_row):
    """
    Gera narrativa estruturada completa para uma comunidade.

    Args:
        community_row: Linha do community_profiles_enriched.csv
        members_df: DataFrame de membros da comunidade
        typology_row: Linha do community_typology_classification.csv

    Returns:
        dict: Narrativa estruturada em seções
    """
    # Extrair dados básicos
    sport = community_row['sport']
    sex = community_row['sex']
    comm_id = community_row['community_id']
    size = community_row['size']

    # Dados temporais
    year_start = community_row['year_start']
    year_end = community_row['year_end']
    span_years = year_end - year_start
    dominant_era = community_row['dominant_era']
    era_concentration = community_row['era_concentration']
    temporal_entropy = community_row['temporal_entropy']

    # Dados geográficos
    hhi = community_row['geographic_hhi']
    dominant_country = community_row['dominant_country']
    country_dominance = community_row['country_dominance']
    num_countries = community_row['num_countries']
    top_countries = community_row['top_countries']

    # Dados de performance
    pagerank_mean = community_row['pagerank_mean']
    pagerank_cv = community_row['pagerank_cv']

    # Dados de tipologia
    performance_class = typology_row['performance_class']
    geographic_class = typology_row['geographic_class']
    temporal_class = typology_row['temporal_class']
    typology_label = typology_row['typology_label']

    gini_pr = typology_row['gini_pagerank']
    concentration_profile = typology_row['concentration_profile']
    concentration_quadrant = typology_row['concentration_quadrant']

    # Top superstars
    top3_superstars = members_df.nlargest(3, 'pagerank')[['name', 'noc', 'year', 'pagerank', 'medal']]

    # Atletas ponte (estimativa - usamos betweenness como proxy)
    if 'betweenness' in members_df.columns:
        bridge_threshold = members_df['betweenness'].quantile(0.9)
        num_bridges = len(members_df[members_df['betweenness'] > bridge_threshold])
    else:
        num_bridges = int(size * 0.10)  # Estimativa 10%

    # Contagem de eras únicas
    years = members_df['year'].unique()
    eras_list = []
    for year in years:
        if year < 1920:
            eras_list.append("Pioneira")
        elif year < 1950:
            eras_list.append("Entre-Guerras")
        elif year < 1980:
            eras_list.append("Guerra-Fria")
        elif year < 2000:
            eras_list.append("Pós-Guerra-Fria")
        else:
            eras_list.append("Moderna")
    num_eras = len(set(eras_list))

    # ==============================================================================
    # CONSTRUIR NARRATIVA ESTRUTURADA
    # ==============================================================================

    # §1 - IDENTIFICAÇÃO E CONTEXTO
    identification = (
        f"Comunidade {comm_id} ({sport}-{sex}): {typology_label}\n\n"
        f"Agrupa {size} atletas medalhistas distribuídos ao longo de {span_years:.0f} anos "
        f"({year_start:.0f}-{year_end:.0f}), representando {num_countries} países em "
        f"{num_eras} eras olímpicas distintas."
    )

    # §2 - CARACTERIZAÇÃO TEMPORAL
    temporal_interp = interpret_temporal_diversity(temporal_entropy, num_eras)
    historical_ctx = get_historical_context(dominant_era, sport)

    temporal = (
        f"A comunidade concentra-se na {dominant_era} ({era_concentration*100:.1f}% dos atletas), "
        f"apresentando {temporal_interp} (entropia de Shannon = {temporal_entropy:.2f}). "
        f"\n\n{historical_ctx}"
    )

    # §3 - PERFIL GEOGRÁFICO
    geo_interp = interpret_geographic_concentration(hhi, dominant_country, country_dominance*100)

    geographic = (
        f"Geograficamente, apresenta classificação {geographic_class} com {geo_interp}. "
        f"\n\nTop 3 países: {top_countries}. "
        f"Esta distribuição revela padrões de investimento histórico, tradições esportivas "
        f"consolidadas e/ou hegemonias competitivas características da modalidade."
    )

    # §4 - ANÁLISE DE PERFORMANCE E ESTRUTURA (INTEGRA GINI!)
    perf_interp = interpret_performance_heterogeneity(gini_pr, pagerank_cv)
    conc_interp = interpret_concentration_profile(concentration_quadrant, concentration_profile, hhi, gini_pr)

    # Formatar superstars
    superstars_text = ""
    for i, (idx, athlete) in enumerate(top3_superstars.iterrows(), 1):
        superstars_text += f"{i}. {athlete['name']} ({athlete['noc']}, {athlete['year']:.0f}): PageRank={athlete['pagerank']:.6f} ({athlete['medal']})"
        if i < len(top3_superstars):
            superstars_text += "; "

    performance = (
        f"Em termos de performance, classificada como {performance_class} com PageRank médio de "
        f"{pagerank_mean:.6f}. \n\nSuperstars destacados: {superstars_text}. "
        f"\n\nA análise estrutural revela {perf_interp} (Gini PageRank = {gini_pr:.3f}, "
        f"CV = {pagerank_cv:.2f}). "
        f"\n\n{conc_interp}"
    )

    # §5 - SIGNIFICADO ESTRUTURAL
    bridge_interp = interpret_bridge_athletes(num_bridges, size)

    # Calcular razão max/mediana como evidência de superstars
    pr_max = members_df['pagerank'].max()
    pr_median = members_df['pagerank'].median()
    max_median_ratio = pr_max / pr_median if pr_median > 0 else 1

    if max_median_ratio > 7:
        dominance_note = f"A razão máximo/mediana de PageRank ({max_median_ratio:.1f}x) evidencia padrão 'winner-takes-all' com superstars concentrando reconhecimento desproporcional."
    elif max_median_ratio > 4:
        dominance_note = f"A razão máximo/mediana de PageRank ({max_median_ratio:.1f}x) indica presença de líderes destacados sem dominância extrema."
    else:
        dominance_note = f"A razão máximo/mediana de PageRank ({max_median_ratio:.1f}x) confirma distribuição equilibrada sem superstars individuais claramente dominantes."

    structural = (
        f"Estruturalmente, a comunidade apresenta {bridge_interp}. "
        f"{dominance_note} "
        f"\n\nA combinação de perfil temporal ({temporal_class}), geográfico ({geographic_class}) "
        f"e de concentração ({concentration_profile}) caracteriza dinâmica competitiva específica "
        f"desta comunidade no contexto da modalidade {sport}."
    )

    # ==============================================================================
    # IDENTIFICAR INSIGHTS-CHAVE
    # ==============================================================================

    key_insights = []

    # Insight 1: Tipologia principal
    key_insights.append(f"Tipologia {typology_label}: {typology_row['typology_description']}")

    # Insight 2: Perfil de concentração
    if concentration_quadrant == "Q1":
        key_insights.append(f"Hegemonia com superstars: {dominant_country} domina institucionalmente E produz talentos excepcionais")
    elif concentration_quadrant == "Q2":
        key_insights.append(f"Elite global: Superstars emergem de múltiplos centros de excelência distribuídos mundialmente")
    elif concentration_quadrant == "Q3":
        key_insights.append(f"Equilíbrio global: Competição madura globalizada sem hegemonias nacionais ou superstars individuais")
    elif concentration_quadrant == "Q4":
        key_insights.append(f"Hegemonia sistêmica: {dominant_country} domina por sistema institucional, não talentos isolados")

    # Insight 3: Temporal
    if num_eras >= 4:
        key_insights.append(f"Persistência histórica: {num_eras} eras olímpicas indicam fatores estruturais duradouros")
    elif num_eras == 1:
        key_insights.append(f"Especificidade temporal: Concentração em 1 era sugere fenômeno conjuntural")

    # Insight 4: Performance
    if gini_pr > 0.40:
        key_insights.append(f"Alta desigualdade estrutural (Gini={gini_pr:.2f}): Superstars concentram importância desproporcional")

    # Insight 5: Tamanho
    if size > 500:
        key_insights.append(f"Comunidade massiva ({size} atletas): Representa núcleo central da modalidade")
    elif size < 20:
        key_insights.append(f"Comunidade especializada ({size} atletas): Nicho específico ou período histórico limitado")

    # ==============================================================================
    # RETORNAR NARRATIVA COMPLETA
    # ==============================================================================

    narrative = {
        "community_id": int(comm_id),
        "sport": sport,
        "sex": sex,
        "size": int(size),
        "typology": typology_label,
        "concentration_profile": concentration_profile,

        "narrative_paragraphs": {
            "identification": identification,
            "temporal": temporal,
            "geographic": geographic,
            "performance": performance,
            "structural": structural
        },

        "key_insights": key_insights,

        "metrics_summary": {
            "years": f"{year_start:.0f}-{year_end:.0f}",
            "dominant_era": dominant_era,
            "num_countries": int(num_countries),
            "dominant_country": dominant_country,
            "hhi": float(hhi),
            "gini_pagerank": float(gini_pr),
            "pagerank_mean": float(pagerank_mean),
            "top_superstar": top3_superstars.iloc[0]['name'] if len(top3_superstars) > 0 else None,
            "max_median_ratio": float(max_median_ratio)
        }
    }

    return narrative

# ==============================================================================
# PROCESSAMENTO PRINCIPAL
# ==============================================================================

def generate_all_narratives(base_dir='../../results'):
    """Gera narrativas para todas as comunidades"""

    print("=" * 80)
    print("GERADOR DE NARRATIVAS AUTOMÁTICAS - COMPONENTE 2")
    print("=" * 80)

    # Carregar dados
    print("\n[1/4] Carregando dados...")

    profiles_df = pd.read_csv(os.path.join(base_dir, 'community_profiles_enriched.csv'))
    members_df = pd.read_csv(os.path.join(base_dir, 'community_members_detailed.csv'))
    typology_df = pd.read_csv(os.path.join(base_dir, 'community_typology_classification.csv'))

    print(f"   Carregados: {len(profiles_df)} comunidades, {len(members_df)} atletas")

    # Gerar narrativas
    print("\n[2/4] Gerando narrativas...")

    all_narratives = {}

    for idx, profile_row in profiles_df.iterrows():
        comm_id = profile_row['community_id']
        sport = profile_row['sport']
        sex = profile_row['sex']

        # Obter dados correspondentes
        community_members = members_df[
            (members_df['community_id'] == comm_id) &
            (members_df['sport'] == sport) &
            (members_df['sex'] == sex)
        ]

        typology_row = typology_df[
            (typology_df['community_id'] == comm_id) &
            (typology_df['sport'] == sport) &
            (typology_df['sex'] == sex)
        ].iloc[0]

        # Gerar narrativa
        narrative = generate_community_narrative(profile_row, community_members, typology_row)

        # Usar chave única
        key = f"{sport}-{sex}-{comm_id}"
        all_narratives[key] = narrative

        print(f"   [OK] {key}: {narrative['typology']}")

    # Exportar JSON
    print("\n[3/4] Exportando narrativas...")

    json_path = os.path.join(base_dir, 'community_narratives.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_narratives, f, indent=2, ensure_ascii=False)
    print(f"   [OK] {json_path}")

    # Exportar TXT formatado
    txt_path = os.path.join(base_dir, 'community_narratives_summary.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("NARRATIVAS DAS COMUNIDADES - ANALISE OLIMPICA\n")
        f.write("=" * 80 + "\n\n")

        # Agrupar por esporte
        for sport in ['Swimming', 'Basketball', 'Football']:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"{sport.upper()}\n")
            f.write(f"{'=' * 80}\n\n")

            sport_narratives = {k: v for k, v in all_narratives.items() if v['sport'] == sport}

            for key in sorted(sport_narratives.keys()):
                narrative = sport_narratives[key]

                f.write(f"Comunidade {narrative['community_id']} - {narrative['sport']} {narrative['sex']}\n")
                f.write(f"{'-' * 80}\n")
                f.write(f"Tipologia: {narrative['typology']}\n")
                f.write(f"Perfil de Concentracao: {narrative['concentration_profile']}\n")
                f.write(f"Tamanho: {narrative['size']} atletas\n\n")

                for section_name, section_text in narrative['narrative_paragraphs'].items():
                    f.write(f"[{section_name.upper()}]\n")
                    f.write(f"{section_text}\n\n")

                f.write(f"INSIGHTS-CHAVE:\n")
                for i, insight in enumerate(narrative['key_insights'], 1):
                    f.write(f"  {i}. {insight}\n")

                f.write(f"\n{'=' * 80}\n\n")

    print(f"   [OK] {txt_path}")

    # Estatísticas finais
    print("\n[4/4] Resumo da Geracao")
    print("=" * 80)
    print(f"\nTotal de narrativas geradas: {len(all_narratives)}")
    print(f"\nDistribuicao por esporte:")
    for sport in ['Swimming', 'Basketball', 'Football']:
        count = sum(1 for v in all_narratives.values() if v['sport'] == sport)
        print(f"  {sport}: {count} comunidades")

    print("\n" + "=" * 80)
    print("NARRATIVAS GERADAS COM SUCESSO!")
    print("=" * 80 + "\n")

    return all_narratives

# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================

if __name__ == "__main__":
    narratives = generate_all_narratives(base_dir='../../results')

    print("\nArquivos gerados em: ../../results/")
    print("  - community_narratives.json")
    print("  - community_narratives_summary.txt")
    print("\n" + "=" * 80)
