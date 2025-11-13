"""
Script para verificar métricas hardcoded na monografia
Busca por números específicos que podem estar desatualizados
"""

import os
import re
from pathlib import Path

def extract_numbers_from_file(filepath):
    """Extrai números de um arquivo .tex e seu contexto"""
    findings = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            # Buscar padrões numéricos com contexto
            patterns = [
                (r'(\d+[\.,]?\d*)\s*atletas?', 'atletas'),
                (r'(\d+[\.,]?\d*)\s*comunidades?', 'comunidades'),
                (r'(\d+[\.,]?\d*)\s*arestas?', 'arestas'),
                (r'(\d+[\.,]?\d*)\s*nós?', 'nos'),
                (r'(\d+[\.,]?\d*)\s*medalhistas?', 'medalhistas'),
                (r'(\d+[\.,]?\d*)\s*registros?', 'registros'),
                (r'(\d+[\.,]?\d*)\s*esportes?', 'esportes'),
                (r'(\d+)\s*%', 'percentual'),
            ]

            for pattern, tipo in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    findings.append({
                        'file': filepath.name,
                        'line': line_num,
                        'type': tipo,
                        'number': match.group(1),
                        'context': line.strip()
                    })

    except Exception as e:
        print(f"Erro ao processar {filepath}: {e}")

    return findings

def scan_monografia():
    """Escaneia todos os arquivos .tex da monografia"""

    print("=" * 80)
    print("VERIFICAÇÃO DE MÉTRICAS NA MONOGRAFIA")
    print("=" * 80)

    textuais_dir = Path('textuais')

    if not textuais_dir.exists():
        print("Diretório 'textuais' não encontrado!")
        return

    all_findings = {}

    # Arquivos principais para verificar
    files_to_check = [
        'introducao.tex',
        'desenvolvimento.tex',
        'resultados.tex',
        'conclusao.tex'
    ]

    for filename in files_to_check:
        filepath = textuais_dir / filename
        if filepath.exists():
            print(f"\n{'='*80}")
            print(f"ANALISANDO: {filename}")
            print('='*80)

            findings = extract_numbers_from_file(filepath)

            if findings:
                all_findings[filename] = findings

                # Agrupar por tipo
                by_type = {}
                for f in findings:
                    tipo = f['type']
                    if tipo not in by_type:
                        by_type[tipo] = []
                    by_type[tipo].append(f)

                for tipo, items in sorted(by_type.items()):
                    print(f"\n--- {tipo.upper()} ---")
                    for item in items:
                        print(f"  Linha {item['line']}: {item['number']} {tipo}")
                        print(f"    Contexto: {item['context'][:100]}...")
            else:
                print("  Nenhuma métrica numérica encontrada")

    # Resumo geral
    print("\n" + "=" * 80)
    print("RESUMO GERAL")
    print("=" * 80)

    total_findings = sum(len(f) for f in all_findings.values())
    print(f"\nTotal de métricas encontradas: {total_findings}")

    print("\nPor arquivo:")
    for filename, findings in all_findings.items():
        print(f"  {filename}: {len(findings)} métricas")

    # Valores específicos para verificar
    print("\n" + "=" * 80)
    print("VALORES CRÍTICOS PARA VERIFICAR")
    print("=" * 80)

    critical_values = {
        'Total de atletas': '4.659',
        'Total de comunidades': '17 (Swimming: 17, Basketball: 3, Football: 4)',
        'Total de arestas': '907.976',
        'Duplicatas removidas': '2',
        'Pódios válidos': '662'
    }

    print("\nValores corretos atualizados:")
    for key, value in critical_values.items():
        print(f"  - {key}: {value}")

    print("\n" + "=" * 80)

if __name__ == '__main__':
    scan_monografia()
