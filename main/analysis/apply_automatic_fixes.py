#!/usr/bin/env python3
"""
Aplicar Correções Automáticas de Qualidade de Texto

Correções mecânicas aplicadas:
1. Padronizar itálico em termos técnicos
2. Corrigir preposições incorretas
3. Identificar top 10 sentenças longas para correção manual
4. Identificar pontos críticos para adicionar conectores
"""

import re
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("APLICANDO CORREÇÕES AUTOMÁTICAS - OPÇÃO C HÍBRIDA")
print("=" * 80)

TEXTUAIS_DIR = Path("/home/caio/Desktop/tcc/monografia/textuais")
CHAPTERS = ["introducao.tex", "revisao.tex", "desenvolvimento.tex", "resultados.tex", "conclusao.tex"]

# ====================
# 1. CORREÇÕES AUTOMÁTICAS
# ====================

def apply_italic_consistency(content):
    """Padroniza itálico em termos técnicos."""
    changes = []

    # Termos que DEVEM estar em itálico
    technical_terms = [
        'PageRank', 'dataset', 'clustering', 'betweenness', 'closeness',
        'bootstrap', 'threshold', 'scale-free', 'small-world', 'per-event',
        'null models', 'random walks', 'random surfer', 'preferential attachment',
        'degree', 'in-degree', 'out-degree', 'eigenvector', 'hubs'
    ]

    for term in technical_terms:
        # Encontrar ocorrências SEM itálico
        pattern = rf'\b{re.escape(term)}\b(?![}}])'  # Não seguido de }
        matches = list(re.finditer(pattern, content, re.IGNORECASE))

        # Verificar se já está em itálico
        non_italic_matches = []
        for match in matches:
            start = match.start()
            # Verificar contexto anterior
            context_before = content[max(0, start-20):start]
            if '\\textit{' not in context_before:
                non_italic_matches.append(match)

        if non_italic_matches:
            # Substituir por versão italizada
            for match in reversed(non_italic_matches):  # Reverse para não bagunçar índices
                content = content[:match.start()] + f'\\textit{{{match.group()}}}' + content[match.end():]

            changes.append({
                'type': 'Itálico adicionado',
                'term': term,
                'count': len(non_italic_matches)
            })

    return content, changes

def fix_prepositions(content):
    """Corrige preposições incorretas."""
    changes = []

    # Padrões de correção
    fixes = [
        (r'\bconsistente\s+a\b', 'consistente com', 'consistente a → consistente com'),
        (r'\bconsistente\s+aos?\b', 'consistente com os', 'consistente ao(s) → consistente com o(s)'),
        (r'\breferente\s+([aeiouAEIOU])', r'referente à \1', 'referente [vogal] → referente à'),
    ]

    for pattern, replacement, description in fixes:
        matches = list(re.finditer(pattern, content))
        if matches:
            content = re.sub(pattern, replacement, content)
            changes.append({
                'type': 'Preposição corrigida',
                'fix': description,
                'count': len(matches)
            })

    return content, changes

# ====================
# 2. IDENTIFICAR SENTENÇAS LONGAS
# ====================

def identify_long_sentences(content, filename):
    """Identifica sentenças muito longas para correção manual."""
    # Extrair texto sem comandos LaTeX complexos
    text = re.sub(r'\\begin\{[^}]+\}.*?\\end\{[^}]+\}', '', content, flags=re.DOTALL)
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)

    # Dividir em sentenças
    sentences = re.split(r'[.!?]\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 50]

    # Encontrar longas (> 300 chars)
    long_sentences = []
    for i, sent in enumerate(sentences):
        if len(sent) > 300:
            # Encontrar posição aproximada no arquivo original
            snippet = sent[:100].replace('\n', ' ')
            long_sentences.append({
                'file': filename,
                'length': len(sent),
                'preview': snippet + '...',
                'full': sent
            })

    # Ordenar por comprimento
    long_sentences.sort(key=lambda x: x['length'], reverse=True)

    return long_sentences[:5]  # Top 5 por arquivo

# ====================
# 3. IDENTIFICAR PONTOS PARA CONECTORES
# ====================

def identify_connector_points(content, filename):
    """Identifica pontos críticos onde adicionar conectores."""
    # Dividir em parágrafos
    paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]

    # Conectores existentes
    connectors = [
        'portanto', 'entretanto', 'contudo', 'todavia', 'assim',
        'consequentemente', 'ademais', 'além disso', 'por outro lado',
        'em contraste', 'similarmente', 'analogamente', 'posteriormente',
        'primeiramente', 'finalmente'
    ]

    # Identificar parágrafos sem conectores no início
    needs_connector = []
    for i, para in enumerate(paragraphs[1:], 1):  # Pular primeiro parágrafo
        first_50 = para.lower()[:50]

        # Verificar se tem conector
        has_connector = any(c in first_50 for c in connectors)

        # Verificar se não é seção/subsection
        is_section = para.strip().startswith('\\section') or para.strip().startswith('\\subsection')

        if not has_connector and not is_section:
            needs_connector.append({
                'file': filename,
                'para_num': i,
                'preview': para[:100].replace('\n', ' ') + '...'
            })

    return needs_connector[:5]  # Top 5 pontos críticos

# ====================
# 4. PROCESSAR ARQUIVOS
# ====================

all_changes = defaultdict(list)
all_long_sentences = []
all_connector_points = []

for chapter in CHAPTERS:
    filepath = TEXTUAIS_DIR / chapter

    if not filepath.exists():
        print(f"⚠️  Arquivo não encontrado: {chapter}")
        continue

    print(f"\n{'='*80}")
    print(f"📝 Processando: {chapter}")
    print(f"{'='*80}")

    # Ler arquivo
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()

    content = original_content
    chapter_changes = []

    # Aplicar correções automáticas
    print("\n🔧 Aplicando correções automáticas...")

    # 1. Itálico
    content, italic_changes = apply_italic_consistency(content)
    chapter_changes.extend(italic_changes)

    # 2. Preposições
    content, prep_changes = fix_prepositions(content)
    chapter_changes.extend(prep_changes)

    # Mostrar mudanças
    if chapter_changes:
        print(f"✓ {len(chapter_changes)} correções aplicadas:")
        for change in chapter_changes:
            print(f"  - {change['type']}: {change.get('term', change.get('fix', ''))} ({change['count']}x)")
    else:
        print("✓ Nenhuma correção automática necessária")

    # Salvar arquivo corrigido
    if content != original_content:
        output_path = filepath.parent / f"{filepath.stem}_CORRIGIDO.tex"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Salvo: {output_path}")

    # Identificar sentenças longas
    long_sents = identify_long_sentences(content, chapter)
    all_long_sentences.extend(long_sents)

    # Identificar pontos para conectores
    connector_pts = identify_connector_points(content, chapter)
    all_connector_points.extend(connector_pts)

    all_changes[chapter] = chapter_changes

# ====================
# 5. RELATÓRIO FINAL
# ====================

print(f"\n{'='*80}")
print("📊 RESUMO DE CORREÇÕES AUTOMÁTICAS")
print(f"{'='*80}")

total_corrections = sum(len(changes) for changes in all_changes.values())
print(f"\n✓ Total de correções automáticas: {total_corrections}")

for chapter, changes in all_changes.items():
    if changes:
        print(f"\n{chapter}:")
        for change in changes:
            print(f"  - {change['type']}: {change['count']}x")

# ====================
# 6. TOP 10 SENTENÇAS LONGAS
# ====================

print(f"\n{'='*80}")
print("🔍 TOP 10 SENTENÇAS MAIS LONGAS (Correção Manual)")
print(f"{'='*80}")

all_long_sentences.sort(key=lambda x: x['length'], reverse=True)

for i, sent in enumerate(all_long_sentences[:10], 1):
    print(f"\n{i}. {sent['file']} - {sent['length']} caracteres")
    print(f"   Preview: {sent['preview']}")
    print(f"   💡 SUGESTÃO: Quebrar em 2-3 sentenças menores")

# ====================
# 7. PONTOS CRÍTICOS PARA CONECTORES
# ====================

print(f"\n{'='*80}")
print("🔗 TOP 10 PONTOS PARA ADICIONAR CONECTORES (Correção Manual)")
print(f"{'='*80}")

for i, point in enumerate(all_connector_points[:10], 1):
    print(f"\n{i}. {point['file']} - Parágrafo {point['para_num']}")
    print(f"   Preview: {point['preview']}")
    print(f"   💡 SUGESTÃO: Adicionar conector no início")
    print(f"      Opções: Ademais, Entretanto, Consequentemente, Por outro lado")

print(f"\n{'='*80}")
print("✅ FASE 1 CONCLUÍDA - CORREÇÕES AUTOMÁTICAS")
print(f"{'='*80}")

print("\n📝 Próximos passos:")
print("1. Revisar arquivos *_CORRIGIDO.tex")
print("2. Aplicar correções manuais nas sentenças longas")
print("3. Adicionar conectores nos pontos identificados")
print("4. Recompilar PDF e verificar")
