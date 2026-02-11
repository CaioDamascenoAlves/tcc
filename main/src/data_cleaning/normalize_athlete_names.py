#!/usr/bin/env python3
"""
NORMALIZAÇÃO DE NOMES DE ATLETAS

Problema: Dados de Tokyo 2020 (2021) estão no formato "LASTNAME FirstName"
enquanto dados históricos (1896-2016) estão no formato "FirstName LastName".

Solução: Normalizar TODOS os nomes para o formato "FirstName LastName".

Estratégia:
1. Detectar padrão LASTNAME_First (nomes que começam com 2+ letras maiúsculas)
2. Inverter para FirstName LASTNAME
3. Preservar apelidos e caracteres especiais entre parênteses
4. Gerar CSV limpo e normalizado

Autor: Pipeline de Limpeza
Data: 2026-02-10
"""

import pandas as pd
import re
from pathlib import Path
import shutil
from datetime import datetime


class AthleteNameNormalizer:
    """Normaliza nomes de atletas para formato consistente."""

    def __init__(self, input_csv: str, output_csv: str, backup: bool = True):
        """
        Inicializa o normalizador.

        Args:
            input_csv: Caminho do CSV original
            output_csv: Caminho do CSV normalizado
            backup: Se True, cria backup do original
        """
        self.input_csv = Path(input_csv)
        self.output_csv = Path(output_csv)
        self.backup = backup

        self.stats = {
            'total_records': 0,
            'names_normalized': 0,
            'patterns_detected': {},
            'errors': []
        }

    def detect_pattern(self, name: str) -> str:
        """
        Detecta o padrão do nome.

        Returns:
            'LASTNAME_First': Padrão SOBRENOME Nome (ex: TAKATO Naohisa)
            'Normal': Padrão Nome Sobrenome (ex: Naohisa Takato)
            'null': Nome vazio/nulo
        """
        if pd.isna(name) or not isinstance(name, str):
            return 'null'

        name = name.strip()

        # Padrão: SOBRENOME Nome
        # Detecta se começa com 2+ letras maiúsculas seguidas de espaço e letra maiúscula
        if re.match(r'^[A-Z]{2,}[\s\-][A-Z]', name):
            return 'LASTNAME_First'

        return 'Normal'

    def normalize_name(self, name: str) -> str:
        """
        Normaliza um nome para o formato padrão.

        Args:
            name: Nome original

        Returns:
            Nome normalizado no formato "FirstName LastName"
        """
        if pd.isna(name) or not isinstance(name, str):
            return name

        name = name.strip()
        pattern = self.detect_pattern(name)

        # Já está no formato correto
        if pattern == 'Normal':
            return name

        # Padrão LASTNAME_First: inverter
        if pattern == 'LASTNAME_First':
            # Separar em partes
            parts = name.split()

            if len(parts) < 2:
                return name  # Não consegue inverter

            # Primeiro elemento é o SOBRENOME (todo maiúsculo)
            lastname = parts[0]

            # Resto é o primeiro nome (pode ter múltiplas partes)
            firstname_parts = parts[1:]

            # Converter sobrenome para Title Case (apenas primeira letra maiúscula)
            lastname_normalized = lastname.title()

            # Manter primeiro nome como está (já tem capitalização correta)
            firstname = ' '.join(firstname_parts)

            # Retornar no formato: FirstName LASTNAME
            return f"{firstname} {lastname_normalized}"

        return name

    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processa o DataFrame normalizando todos os nomes.

        Args:
            df: DataFrame original

        Returns:
            DataFrame com nomes normalizados
        """
        print("Processando nomes...")

        df_clean = df.copy()

        # Aplicar normalização
        original_names = df_clean['Name'].copy()
        df_clean['Name'] = df_clean['Name'].apply(self.normalize_name)

        # Estatísticas
        self.stats['total_records'] = len(df)
        self.stats['names_normalized'] = (original_names != df_clean['Name']).sum()

        # Contar padrões detectados
        patterns = original_names.apply(self.detect_pattern)
        self.stats['patterns_detected'] = patterns.value_counts().to_dict()

        return df_clean

    def create_backup(self):
        """Cria backup do arquivo original."""
        if not self.backup:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.input_csv.parent / f"{self.input_csv.stem}_BACKUP_{timestamp}.csv"

        print(f"Criando backup: {backup_path}")
        shutil.copy2(self.input_csv, backup_path)

        return backup_path

    def run(self):
        """Executa a normalização completa."""
        print("="*80)
        print("NORMALIZAÇÃO DE NOMES DE ATLETAS")
        print("="*80)

        # 1. Criar backup
        if self.backup:
            backup_path = self.create_backup()
            print(f"✅ Backup criado: {backup_path}\n")

        # 2. Carregar dados
        print(f"Carregando dados de: {self.input_csv}")
        df = pd.read_csv(self.input_csv)
        print(f"  Total de registros: {len(df):,}\n")

        # 3. Processar
        df_clean = self.process_dataframe(df)

        # 4. Salvar
        print(f"\nSalvando dados normalizados em: {self.output_csv}")
        df_clean.to_csv(self.output_csv, index=False)

        # 5. Relatório
        self.print_report()

        return df_clean

    def print_report(self):
        """Imprime relatório de normalização."""
        print("\n" + "="*80)
        print("RELATÓRIO DE NORMALIZAÇÃO")
        print("="*80)

        print(f"\n📊 Estatísticas:")
        print(f"  Total de registros processados: {self.stats['total_records']:,}")
        print(f"  Nomes normalizados: {self.stats['names_normalized']:,}")
        print(f"  Taxa de normalização: {100 * self.stats['names_normalized'] / self.stats['total_records']:.2f}%")

        print(f"\n📊 Padrões detectados:")
        for pattern, count in sorted(self.stats['patterns_detected'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern:20s}: {count:,} nomes")

        if self.stats['errors']:
            print(f"\n⚠️  Erros encontrados: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:10]:
                print(f"  - {error}")

        print("\n" + "="*80)
        print("✅ NORMALIZAÇÃO CONCLUÍDA!")
        print("="*80)


def main():
    """Função principal."""
    # Caminhos
    project_root = Path(__file__).parent.parent.parent
    input_csv = project_root / 'data' / 'athlete_events.csv'
    output_csv = project_root / 'data' / 'athlete_events_normalized.csv'

    # Criar normalizador
    normalizer = AthleteNameNormalizer(
        input_csv=input_csv,
        output_csv=output_csv,
        backup=True
    )

    # Executar
    df_clean = normalizer.run()

    # Validação: Mostrar exemplos de antes/depois
    print("\n" + "="*80)
    print("EXEMPLOS DE NORMALIZAÇÃO (2021):")
    print("="*80)

    df_original = pd.read_csv(input_csv)

    # Filtrar 2021
    mask_2021 = df_original['Year'] == 2021
    df_orig_2021 = df_original[mask_2021].copy()
    df_clean_2021 = df_clean[mask_2021].copy()

    # Pegar apenas os que mudaram
    changed_mask = df_orig_2021['Name'] != df_clean_2021['Name']

    if changed_mask.sum() > 0:
        print("\nPrimeiros 20 exemplos:")
        for i, (idx, row_orig) in enumerate(df_orig_2021[changed_mask].head(20).iterrows(), 1):
            row_clean = df_clean_2021.loc[idx]
            print(f"{i:2d}. ANTES: {row_orig['Name']:40s} → DEPOIS: {row_clean['Name']}")

    print(f"\n✅ Arquivo normalizado salvo em: {output_csv}")


if __name__ == "__main__":
    main()
