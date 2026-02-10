#!/usr/bin/env python3
"""
Análise de Qualidade de Texto Acadêmico

Avalia sistematicamente a qualidade do texto da monografia:
1. Citações (formato, uso de aspas, citeonline vs cite)
2. Estrutura de sentenças (comprimento, voz passiva)
3. Conectores e transições
4. Preposições e artigos
5. Legibilidade (complexidade, jargões)
6. Consistência terminológica
"""

import re
import os
from collections import Counter, defaultdict
from pathlib import Path

print("=" * 80)
print("ANÁLISE DE QUALIDADE DE TEXTO ACADÊMICO")
print("=" * 80)

# ====================
# 1. CONFIGURAÇÃO
# ====================

TEXTUAIS_DIR = Path("/home/caio/Desktop/tcc/monografia/textuais")
CHAPTERS = [
    "introducao.tex",
    "revisao.tex",
    "desenvolvimento.tex",
    "resultados.tex",
    "conclusao.tex"
]

# ====================
# 2. FUNÇÕES DE ANÁLISE
# ====================

def read_tex_file(filepath):
    """Lê arquivo .tex removendo comentários."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remover comentários LaTeX (linhas começando com %)
    lines = []
    for line in content.split('\n'):
        if not line.strip().startswith('%'):
            lines.append(line)

    return '\n'.join(lines)

def extract_text_content(tex_content):
    """Extrai apenas texto, removendo comandos LaTeX."""
    # Remover comandos LaTeX complexos
    text = re.sub(r'\\begin\{[^}]+\}.*?\\end\{[^}]+\}', '', tex_content, flags=re.DOTALL)
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    text = re.sub(r'\{[^}]*\}', '', text)

    # Remover caracteres especiais LaTeX
    text = text.replace('~', ' ')
    text = text.replace('\\', '')

    return text

def analyze_citations(tex_content):
    """Analisa uso de citações."""
    issues = []

    # 1. Citações diretas sem aspas (palavras entre "aspas" sem \cite próximo)
    direct_quotes = re.findall(r'["""]([^"""]{20,})["""]', tex_content)
    citations_nearby = re.findall(r'["""][^"""]+["""].{0,50}\\cite', tex_content)

    if len(direct_quotes) > len(citations_nearby):
        issues.append({
            'type': 'Citações diretas sem referência',
            'severity': 'ALTA',
            'count': len(direct_quotes) - len(citations_nearby),
            'detail': 'Possíveis citações diretas sem \\cite próximo'
        })

    # 2. Uso de \cite quando deveria ser \citeonline
    cite_inline = re.findall(r'[A-Z][a-z]+\s+\\cite\{', tex_content)
    if cite_inline:
        issues.append({
            'type': 'Uso incorreto de \\cite',
            'severity': 'MÉDIA',
            'count': len(cite_inline),
            'detail': 'Usar \\citeonline quando autor faz parte da sentença',
            'examples': cite_inline[:3]
        })

    # 3. Múltiplas citações consecutivas sem integração textual
    multiple_cites = re.findall(r'\\cite\{[^}]+\}\s*\\cite\{[^}]+\}', tex_content)
    if multiple_cites:
        issues.append({
            'type': 'Citações consecutivas não integradas',
            'severity': 'BAIXA',
            'count': len(multiple_cites),
            'detail': 'Considerar integrar em texto corrido'
        })

    # 4. Apud não utilizado
    apud_count = len(re.findall(r'\\apud', tex_content))
    cite_count = len(re.findall(r'\\cite', tex_content))

    if apud_count == 0 and cite_count > 50:
        issues.append({
            'type': 'Ausência de citações secundárias (apud)',
            'severity': 'BAIXA',
            'count': 0,
            'detail': 'Verificar se todas as fontes são primárias'
        })

    return issues

def analyze_sentence_structure(text_content):
    """Analisa estrutura das sentenças."""
    issues = []

    # Dividir em sentenças (aproximado)
    sentences = re.split(r'[.!?]\s+', text_content)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    # 1. Sentenças muito longas (> 300 caracteres)
    long_sentences = [s for s in sentences if len(s) > 300]
    if long_sentences:
        issues.append({
            'type': 'Sentenças muito longas',
            'severity': 'ALTA',
            'count': len(long_sentences),
            'detail': f'Média: {int(sum(len(s) for s in long_sentences)/len(long_sentences))} chars',
            'examples': [s[:100] + '...' for s in long_sentences[:2]]
        })

    # 2. Voz passiva excessiva
    passive_markers = ['foi', 'foram', 'é', 'são', 'ser', 'sendo', 'sido']
    passive_count = sum(text_content.lower().count(f' {marker} ') for marker in passive_markers)
    word_count = len(text_content.split())
    passive_ratio = passive_count / word_count if word_count > 0 else 0

    if passive_ratio > 0.03:  # Mais de 3% de marcadores passivos
        issues.append({
            'type': 'Excesso de voz passiva',
            'severity': 'MÉDIA',
            'count': passive_count,
            'detail': f'Ratio: {passive_ratio*100:.1f}% (ideal < 3%)'
        })

    # 3. Sentenças iniciando com números/dados sem contexto
    number_starts = [s for s in sentences if re.match(r'^\d+', s.strip())]
    if len(number_starts) > 5:
        issues.append({
            'type': 'Sentenças iniciando com números',
            'severity': 'BAIXA',
            'count': len(number_starts),
            'detail': 'Considerar contextualizar dados antes de apresentá-los'
        })

    return issues

def analyze_connectors(text_content):
    """Analisa uso de conectores e transições."""
    issues = []

    # Parágrafo aproximado (linhas duplas)
    paragraphs = [p.strip() for p in text_content.split('\n\n') if len(p.strip()) > 50]

    # Conectores comuns
    connectors = [
        'portanto', 'entretanto', 'contudo', 'todavia', 'assim',
        'consequentemente', 'ademais', 'além disso', 'por outro lado',
        'em contraste', 'similarmente', 'analogamente', 'posteriormente',
        'anteriormente', 'primeiramente', 'em primeiro lugar', 'finalmente'
    ]

    # Contar conectores
    connector_count = sum(text_content.lower().count(c) for c in connectors)
    para_count = len(paragraphs)
    connector_ratio = connector_count / para_count if para_count > 0 else 0

    if connector_ratio < 0.3:  # Menos de 0.3 conectores por parágrafo
        issues.append({
            'type': 'Poucos conectores textuais',
            'severity': 'MÉDIA',
            'count': connector_count,
            'detail': f'Ratio: {connector_ratio:.2f} por parágrafo (ideal > 0.5)',
            'suggestion': 'Adicionar mais transições entre parágrafos'
        })

    # Parágrafos sem conectores no início
    para_without_connector = 0
    for para in paragraphs[1:]:  # Pular primeiro parágrafo
        first_words = para.lower()[:50]
        if not any(c in first_words for c in connectors):
            para_without_connector += 1

    if para_without_connector > len(paragraphs) * 0.5:
        issues.append({
            'type': 'Parágrafos sem transição',
            'severity': 'ALTA',
            'count': para_without_connector,
            'detail': f'{para_without_connector}/{len(paragraphs)} parágrafos sem conector inicial'
        })

    return issues

def analyze_prepositions(text_content):
    """Analisa uso de preposições e artigos."""
    issues = []

    # Padrões comuns de preposições faltantes
    patterns = [
        (r'\b(em|no|na|nos|nas)\s+que\b', 'Considerar "em que" vs "que"'),
        (r'\b(para|pra)\s+que\b', 'Verificar "para que" vs "que"'),
        (r'\b(de|do|da|dos|das)\s+acordo\s+com\b', 'OK: "de acordo com"'),
        (r'\b(a|o)\s+qual\b', 'Verificar "o qual" vs "que"'),
    ]

    # Detectar problemas comuns
    missing_prep_patterns = [
        (r'\breferente\s+[aeiou]', 'Falta preposição após "referente"'),
        (r'\bconsistente\s+[aeiou]', 'Verificar "consistente com"'),
        (r'\bdiferente\s+[aeiou]', 'Verificar "diferente de"'),
    ]

    for pattern, msg in missing_prep_patterns:
        matches = re.findall(pattern, text_content, re.IGNORECASE)
        if matches:
            issues.append({
                'type': 'Possível preposição faltante',
                'severity': 'MÉDIA',
                'count': len(matches),
                'detail': msg,
                'examples': matches[:3]
            })

    return issues

def analyze_readability(text_content):
    """Analisa legibilidade do texto."""
    issues = []

    # 1. Palavras muito longas (> 20 caracteres)
    words = re.findall(r'\b\w+\b', text_content)
    long_words = [w for w in words if len(w) > 20]

    if len(long_words) > len(words) * 0.01:  # Mais de 1% de palavras longas
        issues.append({
            'type': 'Palavras muito longas',
            'severity': 'BAIXA',
            'count': len(long_words),
            'detail': f'Ratio: {len(long_words)/len(words)*100:.1f}% (ideal < 1%)',
            'examples': list(set(long_words))[:5]
        })

    # 2. Jargões técnicos sem definição (aproximado)
    technical_terms = [
        'modularidade', 'centralidade', 'betweenness', 'clustering',
        'entropia', 'bootstrapping', 'z-score', 'p-valor'
    ]

    first_occurrences = {}
    for term in technical_terms:
        match = re.search(rf'\b{term}\b', text_content, re.IGNORECASE)
        if match:
            # Verificar se há definição próxima (parênteses, dois pontos, etc)
            context = text_content[max(0, match.start()-100):match.end()+100]
            if '(' not in context and ':' not in context and 'é' not in context:
                first_occurrences[term] = context[:80]

    if first_occurrences:
        issues.append({
            'type': 'Termos técnicos possivelmente não definidos',
            'severity': 'MÉDIA',
            'count': len(first_occurrences),
            'detail': 'Verificar se termos são definidos na primeira ocorrência',
            'examples': list(first_occurrences.keys())[:5]
        })

    return issues

def analyze_consistency(tex_content):
    """Analisa consistência terminológica."""
    issues = []

    # 1. Variações de termos que deveriam ser padronizados
    variations = {
        'PageRank': [r'\bPageRank\b', r'\bpagerank\b', r'\bpage rank\b'],
        'dataset': [r'\bdataset\b', r'\bdata set\b', r'\bdata-set\b'],
        'per-event': [r'\bper-event\b', r'\bper event\b', r'\bperevent\b'],
    }

    for term, patterns in variations.items():
        counts = {}
        for pattern in patterns:
            matches = re.findall(pattern, tex_content)
            if matches:
                counts[pattern] = len(matches)

        if len(counts) > 1:
            issues.append({
                'type': 'Inconsistência terminológica',
                'severity': 'ALTA',
                'count': sum(counts.values()),
                'detail': f'Termo "{term}" com variações: {counts}'
            })

    # 2. Formatação inconsistente de itálico
    italic_terms = re.findall(r'\\textit\{([^}]+)\}', tex_content)
    non_italic_same = []
    for term in set(italic_terms):
        # Verificar se aparece sem itálico também
        if re.search(rf'\b{re.escape(term)}\b(?!}})', tex_content):
            non_italic_same.append(term)

    if non_italic_same:
        issues.append({
            'type': 'Itálico inconsistente',
            'severity': 'MÉDIA',
            'count': len(non_italic_same),
            'detail': 'Termos que aparecem com e sem itálico',
            'examples': non_italic_same[:5]
        })

    return issues

# ====================
# 3. ANÁLISE PRINCIPAL
# ====================

all_issues = defaultdict(list)

for chapter in CHAPTERS:
    filepath = TEXTUAIS_DIR / chapter

    if not filepath.exists():
        print(f"⚠️  Arquivo não encontrado: {chapter}")
        continue

    print(f"\n{'='*80}")
    print(f"📖 Analisando: {chapter}")
    print(f"{'='*80}")

    # Ler arquivo
    tex_content = read_tex_file(filepath)
    text_content = extract_text_content(tex_content)

    print(f"Caracteres: {len(tex_content):,} | Palavras: {len(text_content.split()):,}")

    # Executar análises
    chapter_issues = {
        'Citações': analyze_citations(tex_content),
        'Estrutura de sentenças': analyze_sentence_structure(text_content),
        'Conectores e transições': analyze_connectors(text_content),
        'Preposições e artigos': analyze_prepositions(text_content),
        'Legibilidade': analyze_readability(text_content),
        'Consistência terminológica': analyze_consistency(tex_content)
    }

    # Consolidar
    for category, issues in chapter_issues.items():
        if issues:
            all_issues[chapter].extend([{**issue, 'category': category} for issue in issues])

    # Mostrar resumo
    total_issues = sum(len(issues) for issues in chapter_issues.values())
    if total_issues > 0:
        print(f"\n🔍 Problemas encontrados: {total_issues}")
        for category, issues in chapter_issues.items():
            if issues:
                print(f"   {category}: {len(issues)} problemas")
    else:
        print("\n✓ Nenhum problema detectado")

# ====================
# 4. RELATÓRIO CONSOLIDADO
# ====================

print(f"\n{'='*80}")
print("📊 RELATÓRIO CONSOLIDADO - QUALIDADE DO TEXTO")
print(f"{'='*80}")

# Agrupar por severidade
by_severity = {'ALTA': [], 'MÉDIA': [], 'BAIXA': []}
for chapter, issues in all_issues.items():
    for issue in issues:
        by_severity[issue['severity']].append({**issue, 'chapter': chapter})

# Apresentar por severidade
for severity in ['ALTA', 'MÉDIA', 'BAIXA']:
    issues = by_severity[severity]
    if not issues:
        continue

    print(f"\n{'='*80}")
    print(f"🔴 PRIORIDADE {severity}: {len(issues)} problemas")
    print(f"{'='*80}")

    # Agrupar por tipo
    by_type = defaultdict(list)
    for issue in issues:
        by_type[issue['type']].append(issue)

    for issue_type, issue_list in sorted(by_type.items()):
        print(f"\n📌 {issue_type} ({len(issue_list)} ocorrências)")

        # Mostrar detalhes dos primeiros
        for issue in issue_list[:2]:
            print(f"   Arquivo: {issue['chapter']}")
            print(f"   Categoria: {issue['category']}")
            print(f"   Detalhes: {issue['detail']}")
            if 'examples' in issue:
                print(f"   Exemplos: {issue['examples']}")
            print()

# ====================
# 5. RECOMENDAÇÕES
# ====================

print(f"\n{'='*80}")
print("💡 RECOMENDAÇÕES PARA MELHORIA")
print(f"{'='*80}")

recommendations = [
    {
        'priority': 'ALTA',
        'title': 'Quebrar sentenças longas',
        'detail': 'Sentenças > 300 caracteres dificultam leitura. Quebrar em 2-3 sentenças menores.'
    },
    {
        'priority': 'ALTA',
        'title': 'Adicionar conectores entre parágrafos',
        'detail': 'Usar transições explícitas (Portanto, Entretanto, Ademais, etc.) para guiar leitor.'
    },
    {
        'priority': 'MÉDIA',
        'title': 'Reduzir voz passiva',
        'detail': 'Converter construções passivas em ativas quando possível para mais dinamismo.'
    },
    {
        'priority': 'MÉDIA',
        'title': 'Verificar uso de \\cite vs \\citeonline',
        'detail': 'Usar \\citeonline quando autor faz parte da sentença.'
    },
    {
        'priority': 'BAIXA',
        'title': 'Definir termos técnicos na primeira ocorrência',
        'detail': 'Adicionar breves definições ou explicações de jargões técnicos.'
    }
]

for rec in recommendations:
    print(f"\n[{rec['priority']}] {rec['title']}")
    print(f"    {rec['detail']}")

print(f"\n{'='*80}")
print("✅ ANÁLISE CONCLUÍDA")
print(f"{'='*80}")

print("\n📝 Próximos passos sugeridos:")
print("1. Revisar problemas de ALTA prioridade")
print("2. Corrigir inconsistências terminológicas")
print("3. Adicionar conectores onde faltam")
print("4. Quebrar sentenças muito longas")
print("5. Validar formatação de citações")
