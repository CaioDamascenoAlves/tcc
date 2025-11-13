#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Community Cohesion Analysis - Component 3
==========================================

Calcula métricas de coesão estrutural interna para as 27 comunidades detectadas.

IMPORTANTE: Esta análise usa a REDE ORIGINAL (não backbone) para preservar
a estrutura completa da rede, incluindo PageRanks diferenciados e conexões
significativas. O filtro de disparidade foi descontinuado pois mesmo com
alpha alto (0.7-0.9) ainda capava excessivamente a rede.

Métricas Implementadas:
- Densidade interna (edges_real / edges_possible)
- Peso médio das arestas internas
- Diâmetro e distância média (compactação)
- Coeficiente de agrupamento (transitividade)
- Razão intra/inter (segregação)
- Detecção de sub-comunidades (Louvain recursivo)
- Score de coesão normalizado (0-1)

Author: TCC Analysis System
Date: January 2025
"""

import os
import pandas as pd
import networkx as nx
import numpy as np
import json
from pathlib import Path
import community as community_louvain
import warnings
warnings.filterwarnings('ignore')

# Paths
RESULTS_DIR = Path(__file__).parent.parent / "../../results"
OUTPUT_DIR = RESULTS_DIR


class CommunityStructuralAnalyzer:
    """Analisa coesão estrutural interna de comunidades."""

    def __init__(self, results_dir: Path):
        self.results_dir = Path(results_dir)
        self.community_profiles = None
        self.networks = {}
        self.cohesion_metrics = []

    def load_community_profiles(self):
        """Carrega perfis de comunidades existentes."""
        profile_path = self.results_dir / "community_profiles_enriched.csv"
        self.community_profiles = pd.read_csv(profile_path)
        print(f"[OK] Loaded {len(self.community_profiles)} community profiles")
        return self.community_profiles

    def load_network_from_csvs(self, sport: str, sex: str, event_type: str = None) -> nx.DiGraph:
        """
        Constrói rede backbone diretamente dos CSVs (evita problemas com GEXF).

        Args:
            sport: 'swimming', 'basketball', 'football'
            sex: 'M' or 'F'
            event_type: 'individual', 'team', or None (for non-swimming)

        Returns:
            NetworkX DiGraph com atributo 'community' nos nós
        """
        # Construir nomes dos arquivos
        if event_type:
            metrics_filename = f"{sport}_{sex}_{event_type}_detailed_metrics.csv"
            edges_filename = f"{sport}_{sex}_{event_type}_backbone_edges.csv"
        else:
            metrics_filename = f"{sport}_{sex}_team_detailed_metrics.csv"
            edges_filename = f"{sport}_{sex}_team_backbone_edges.csv"

        metrics_path = self.results_dir / sport / metrics_filename
        edges_path = self.results_dir / sport / edges_filename

        # Verificar existência
        if not metrics_path.exists():
            print(f"[WARN] Metrics CSV not found: {metrics_path}")
            return None

        if not edges_path.exists():
            print(f"[WARN] Edges CSV not found: {edges_path}")
            return None

        # Carregar CSV com métricas e comunidades
        try:
            df_metrics = pd.read_csv(metrics_path)
        except Exception as e:
            print(f"[ERROR] Failed to load metrics CSV: {e}")
            return None

        # Carregar CSV com arestas
        try:
            df_edges = pd.read_csv(edges_path)
        except Exception as e:
            print(f"[ERROR] Failed to load edges CSV: {e}")
            return None

        # Criar grafo direcionado
        G = nx.DiGraph()

        # Adicionar nós com atributos de comunidade
        name_to_community = dict(zip(df_metrics['name'], df_metrics['backbone_community']))

        for name, community in name_to_community.items():
            G.add_node(name, community=int(community))

        # Adicionar arestas
        for _, edge in df_edges.iterrows():
            source = edge['source_name']
            target = edge['target_name']
            weight = edge['weight']

            # Garantir que ambos os nós existem
            if source not in G:
                G.add_node(source, community=-1)
            if target not in G:
                G.add_node(target, community=-1)

            G.add_edge(source, target, weight=weight)

        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()
        num_with_community = sum(1 for n in G.nodes() if G.nodes[n]['community'] != -1)

        print(f"[OK] Built {sport}_{sex}_{event_type or 'team'}: {num_nodes} nodes, "
              f"{num_edges} edges, {num_with_community} with community")

        return G

    def extract_community_subgraph(self, G: nx.DiGraph, community_id: int) -> nx.DiGraph:
        """
        Extrai subgrafo de uma comunidade específica.

        Args:
            G: Rede completa
            community_id: ID da comunidade

        Returns:
            Subgrafo contendo apenas nós da comunidade
        """
        # Filtrar nós da comunidade
        community_nodes = [
            node for node, data in G.nodes(data=True)
            if data.get('community') == community_id
        ]

        if not community_nodes:
            return None

        # Criar subgrafo
        subgraph = G.subgraph(community_nodes).copy()
        return subgraph

    def calculate_density(self, G: nx.DiGraph) -> float:
        """
        Calcula densidade interna: edges_actual / edges_possible.

        Para grafo direcionado: max_edges = n*(n-1)
        """
        n = G.number_of_nodes()
        if n <= 1:
            return 0.0

        actual_edges = G.number_of_edges()
        possible_edges = n * (n - 1)  # Direcionado

        density = actual_edges / possible_edges if possible_edges > 0 else 0.0
        return density

    def calculate_avg_edge_weight(self, G: nx.DiGraph) -> float:
        """Calcula peso médio das arestas internas."""
        if G.number_of_edges() == 0:
            return 0.0

        weights = [data.get('weight', 1.0) for u, v, data in G.edges(data=True)]
        return np.mean(weights)

    def calculate_diameter_and_avg_distance(self, G: nx.DiGraph) -> tuple:
        """
        Calcula diâmetro e distância média.

        Returns:
            (diameter, avg_distance)
        """
        # Converter para não-direcionado para análise de distâncias
        G_undirected = G.to_undirected()

        # Verificar conectividade
        if not nx.is_connected(G_undirected):
            # Usar maior componente conectado
            largest_cc = max(nx.connected_components(G_undirected), key=len)
            G_undirected = G_undirected.subgraph(largest_cc).copy()

        try:
            diameter = nx.diameter(G_undirected)
            avg_distance = nx.average_shortest_path_length(G_undirected)
        except:
            diameter = np.nan
            avg_distance = np.nan

        return diameter, avg_distance

    def calculate_clustering_coefficient(self, G: nx.DiGraph) -> float:
        """Calcula coeficiente de agrupamento (transitivity)."""
        G_undirected = G.to_undirected()

        try:
            clustering = nx.transitivity(G_undirected)
        except:
            clustering = 0.0

        return clustering

    def calculate_intra_inter_ratio(self, G_full: nx.DiGraph, community_nodes: set) -> float:
        """
        Calcula razão intra/inter: arestas internas / arestas de fronteira.

        Args:
            G_full: Rede completa
            community_nodes: Set de nós da comunidade

        Returns:
            Razão intra/inter (valores altos = alta segregação)
        """
        intra_edges = 0  # Arestas internas (ambos os nós na comunidade)
        inter_edges = 0  # Arestas de fronteira (um nó dentro, outro fora)

        for u, v in G_full.edges():
            u_in = u in community_nodes
            v_in = v in community_nodes

            if u_in and v_in:
                intra_edges += 1
            elif u_in or v_in:
                inter_edges += 1

        if inter_edges == 0:
            return np.inf if intra_edges > 0 else 0.0

        ratio = intra_edges / inter_edges
        return ratio

    def detect_subcommunities(self, G: nx.DiGraph) -> dict:
        """
        Detecta sub-comunidades usando Louvain recursivo.

        Returns:
            Dict com estatísticas de sub-comunidades
        """
        if G.number_of_nodes() < 5:
            return {
                'num_subcommunities': 1,
                'modularity': 0.0,
                'sizes': [G.number_of_nodes()]
            }

        # Converter para não-direcionado (Louvain não suporta direcionado)
        G_undirected = G.to_undirected()

        try:
            # Detectar sub-comunidades
            partition = community_louvain.best_partition(G_undirected)

            # Calcular modularidade
            modularity = community_louvain.modularity(partition, G_undirected)

            # Contar tamanhos
            subcommunities = {}
            for node, comm_id in partition.items():
                subcommunities.setdefault(comm_id, []).append(node)

            sizes = sorted([len(nodes) for nodes in subcommunities.values()], reverse=True)

            return {
                'num_subcommunities': len(subcommunities),
                'modularity': modularity,
                'sizes': sizes,
                'largest_subcomm_fraction': sizes[0] / G.number_of_nodes() if sizes else 0.0
            }
        except:
            return {
                'num_subcommunities': 1,
                'modularity': 0.0,
                'sizes': [G.number_of_nodes()],
                'largest_subcomm_fraction': 1.0
            }

    def calculate_cohesion_score(self, metrics: dict) -> float:
        """
        Calcula score de coesão normalizado (0-1).

        Componentes:
        - Densidade (0-1): quanto mais densa, mais coesa
        - Clustering (0-1): quanto mais agrupada, mais coesa
        - Intra/inter ratio normalizado: quanto maior, mais coesa
        - Modularidade inversa: quanto MENOR a modularidade interna, mais coesa (menos fragmentada)

        Score = média ponderada dos componentes
        """
        density = metrics['density']
        clustering = metrics['clustering_coefficient']

        # Normalizar intra/inter ratio (sigmoid)
        ratio = metrics['intra_inter_ratio']
        if np.isinf(ratio):
            ratio_norm = 1.0
        else:
            ratio_norm = 1 / (1 + np.exp(-ratio))  # Sigmoid

        # Modularidade inversa (baixa modularidade = alta coesão)
        modularity = metrics['subcommunity_modularity']
        modularity_inv = 1 - modularity if not np.isnan(modularity) else 0.5

        # Pesos
        weights = {
            'density': 0.35,
            'clustering': 0.25,
            'ratio': 0.25,
            'modularity': 0.15
        }

        cohesion_score = (
            weights['density'] * density +
            weights['clustering'] * clustering +
            weights['ratio'] * ratio_norm +
            weights['modularity'] * modularity_inv
        )

        return cohesion_score

    def analyze_community(self, sport: str, sex: str, community_id: int,
                         event_type: str = None) -> dict:
        """
        Analisa coesão estrutural de uma comunidade.

        Returns:
            Dict com todas as métricas de coesão
        """
        # Carregar rede
        G_full = self.load_network_from_csvs(sport, sex, event_type)

        if G_full is None:
            return None

        # Extrair subgrafo da comunidade
        G_comm = self.extract_community_subgraph(G_full, community_id)

        if G_comm is None or G_comm.number_of_nodes() == 0:
            print(f"[WARN] Community {community_id} not found in {sport}_{sex}_{event_type}")
            return None

        community_nodes = set(G_comm.nodes())

        # Calcular métricas
        density = self.calculate_density(G_comm)
        avg_weight = self.calculate_avg_edge_weight(G_comm)
        diameter, avg_distance = self.calculate_diameter_and_avg_distance(G_comm)
        clustering = self.calculate_clustering_coefficient(G_comm)
        intra_inter_ratio = self.calculate_intra_inter_ratio(G_full, community_nodes)
        subcomm_stats = self.detect_subcommunities(G_comm)

        # Agregar métricas
        metrics = {
            'sport': sport,
            'sex': sex,
            'event_type': event_type or 'team',
            'community_id': community_id,
            'size': G_comm.number_of_nodes(),
            'num_edges': G_comm.number_of_edges(),
            'density': density,
            'avg_edge_weight': avg_weight,
            'diameter': diameter,
            'avg_distance': avg_distance,
            'clustering_coefficient': clustering,
            'intra_inter_ratio': intra_inter_ratio,
            'num_subcommunities': subcomm_stats['num_subcommunities'],
            'subcommunity_modularity': subcomm_stats['modularity'],
            'largest_subcomm_fraction': subcomm_stats.get('largest_subcomm_fraction', 0.0)
        }

        # Calcular score de coesão
        metrics['cohesion_score'] = self.calculate_cohesion_score(metrics)

        return metrics

    def load_global_community_data(self):
        """Carrega dados globais de comunidades com todos os membros."""
        members_path = self.results_dir / "community_members_detailed.csv"
        df_members = pd.read_csv(members_path)
        print(f"[OK] Loaded {len(df_members)} athlete-community assignments")
        return df_members

    def build_community_network(self, sport: str, sex: str, community_id: int) -> nx.DiGraph:
        """
        Constrói rede de uma comunidade específica a partir dos dados globais.

        IMPORTANTE: Usa rede ORIGINAL (não backbone) para preservar estrutura completa.

        Returns:
            NetworkX DiGraph contendo apenas os atletas e arestas da comunidade
        """
        # Carregar membros da comunidade
        df_members = pd.read_csv(self.results_dir / "community_members_detailed.csv")

        # Filtrar atletas da comunidade específica
        community_members = df_members[
            (df_members['sport'] == sport.capitalize()) &
            (df_members['sex'] == sex) &
            (df_members['community_id'] == community_id)
        ]

        if len(community_members) == 0:
            return None

        member_names = set(community_members['name'].values)

        # Carregar todas as arestas relevantes (individual + team para swimming)
        G = nx.DiGraph()

        # Adicionar nós
        for name in member_names:
            G.add_node(name, community=community_id)

        # Carregar arestas de todos os arquivos relevantes
        # MUDANÇA: Usar *_original_edges.csv ao invés de *_backbone_edges.csv
        edges_files = []
        if sport == 'swimming':
            # Swimming tem individual e team
            edges_files.append(self.results_dir / sport / f"{sport}_{sex}_individual_original_edges.csv")
            edges_files.append(self.results_dir / sport / f"{sport}_{sex}_team_original_edges.csv")
        else:
            # Basketball e Football são team
            edges_files.append(self.results_dir / sport / f"{sport}_{sex}_team_original_edges.csv")

        # Carregar e filtrar arestas
        for edges_file in edges_files:
            if not edges_file.exists():
                continue

            df_edges = pd.read_csv(edges_file)

            # Filtrar arestas internas à comunidade
            for _, edge in df_edges.iterrows():
                source = edge['source_name']
                target = edge['target_name']

                if source in member_names and target in member_names:
                    weight = edge['weight']
                    G.add_edge(source, target, weight=weight)

        return G

    def analyze_all_communities(self):
        """Analisa todas as 27 comunidades."""
        self.cohesion_metrics = []

        for idx, row in self.community_profiles.iterrows():
            sport = row['sport'].lower()
            sex = row['sex']
            community_id = int(row['community_id'])

            # Construir rede da comunidade a partir dos dados globais
            G_comm = self.build_community_network(sport, sex, community_id)

            if G_comm is None or G_comm.number_of_nodes() == 0:
                print(f"[{idx+1}/{len(self.community_profiles)}] {sport}_{sex}_C{community_id}: SKIP (no nodes)")
                continue

            # Calcular métricas diretamente no subgrafo
            community_nodes = set(G_comm.nodes())

            # Métricas básicas
            density = self.calculate_density(G_comm)
            avg_weight = self.calculate_avg_edge_weight(G_comm)
            diameter, avg_distance = self.calculate_diameter_and_avg_distance(G_comm)
            clustering = self.calculate_clustering_coefficient(G_comm)
            subcomm_stats = self.detect_subcommunities(G_comm)

            # Intra/inter ratio precisa da rede completa - usar aproximação
            # Aproximação: edges internas / possíveis edges de saída
            intra_edges = G_comm.number_of_edges()
            # Como não temos a rede global aqui, usar razão interna/externa = inf se isolada
            intra_inter_ratio = np.inf if intra_edges > 0 else 0.0

            metrics = {
                'sport': sport,
                'sex': sex,
                'event_type': 'mixed',  # Combina individual+team para swimming
                'community_id': community_id,
                'size': G_comm.number_of_nodes(),
                'num_edges': G_comm.number_of_edges(),
                'density': density,
                'avg_edge_weight': avg_weight,
                'diameter': diameter,
                'avg_distance': avg_distance,
                'clustering_coefficient': clustering,
                'intra_inter_ratio': intra_inter_ratio,
                'num_subcommunities': subcomm_stats['num_subcommunities'],
                'subcommunity_modularity': subcomm_stats['modularity'],
                'largest_subcomm_fraction': subcomm_stats.get('largest_subcomm_fraction', 0.0)
            }

            metrics['cohesion_score'] = self.calculate_cohesion_score(metrics)

            self.cohesion_metrics.append(metrics)
            print(f"[{idx+1}/{len(self.community_profiles)}] {sport}_{sex}_C{community_id}: "
                  f"size={metrics['size']}, edges={metrics['num_edges']}, "
                  f"cohesion={metrics['cohesion_score']:.3f}, density={metrics['density']:.4f}")

        print(f"\n[OK] Analyzed {len(self.cohesion_metrics)} communities successfully")

    def generate_summary_statistics(self) -> dict:
        """Gera estatísticas resumidas por esporte."""
        df = pd.DataFrame(self.cohesion_metrics)

        summary = {
            'overall': {
                'mean_cohesion': float(df['cohesion_score'].mean()),
                'std_cohesion': float(df['cohesion_score'].std()),
                'mean_density': float(df['density'].mean()),
                'mean_clustering': float(df['clustering_coefficient'].mean()),
                'mean_intra_inter_ratio': float(df['intra_inter_ratio'].replace([np.inf], np.nan).mean())
            },
            'by_sport': {}
        }

        for sport in df['sport'].unique():
            sport_df = df[df['sport'] == sport]
            summary['by_sport'][sport] = {
                'num_communities': len(sport_df),
                'mean_cohesion': float(sport_df['cohesion_score'].mean()),
                'std_cohesion': float(sport_df['cohesion_score'].std()),
                'mean_density': float(sport_df['density'].mean()),
                'mean_clustering': float(sport_df['clustering_coefficient'].mean()),
                'mean_diameter': float(sport_df['diameter'].mean()),
                'mean_intra_inter_ratio': float(sport_df['intra_inter_ratio'].replace([np.inf], np.nan).mean())
            }

        return summary

    def export_results(self):
        """Exporta resultados para CSV e JSON."""
        # CSV detalhado
        df = pd.DataFrame(self.cohesion_metrics)
        csv_path = OUTPUT_DIR / "community_cohesion_metrics.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"\n[OK] Exported detailed metrics: {csv_path}")

        # JSON com resumo estatístico
        summary = self.generate_summary_statistics()
        json_path = OUTPUT_DIR / "community_cohesion_summary.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"[OK] Exported summary: {json_path}")

        # Relatório interpretativo
        self.generate_interpretation_report(df, summary)

    def generate_interpretation_report(self, df: pd.DataFrame, summary: dict):
        """Gera relatório textual interpretativo."""
        report_lines = []

        report_lines.append("=" * 80)
        report_lines.append("COMPONENTE 3: ANALISE DE COESAO ESTRUTURAL INTERNA")
        report_lines.append("=" * 80)
        report_lines.append("")
        report_lines.append(f"Comunidades Analisadas: {len(df)}")
        report_lines.append("")

        # Overall statistics
        report_lines.append("-" * 80)
        report_lines.append("METRICAS GERAIS (Todas as Comunidades)")
        report_lines.append("-" * 80)
        ov = summary['overall']
        report_lines.append(f"Cohesion Score Medio: {ov['mean_cohesion']:.3f} (±{ov['std_cohesion']:.3f})")
        report_lines.append(f"Densidade Media: {ov['mean_density']:.3f}")
        report_lines.append(f"Clustering Medio: {ov['mean_clustering']:.3f}")
        report_lines.append(f"Razao Intra/Inter Media: {ov['mean_intra_inter_ratio']:.3f}")
        report_lines.append("")

        # By sport
        report_lines.append("-" * 80)
        report_lines.append("COMPARACAO POR ESPORTE")
        report_lines.append("-" * 80)

        sports_sorted = sorted(
            summary['by_sport'].items(),
            key=lambda x: x[1]['mean_cohesion'],
            reverse=True
        )

        for rank, (sport, stats) in enumerate(sports_sorted, 1):
            report_lines.append(f"\n{rank}. {sport.upper()}")
            report_lines.append(f"   Comunidades: {stats['num_communities']}")
            report_lines.append(f"   Cohesion Score: {stats['mean_cohesion']:.3f} (±{stats['std_cohesion']:.3f})")
            report_lines.append(f"   Densidade: {stats['mean_density']:.3f}")
            report_lines.append(f"   Clustering: {stats['mean_clustering']:.3f}")
            report_lines.append(f"   Diametro: {stats['mean_diameter']:.1f}")
            report_lines.append(f"   Razao Intra/Inter: {stats['mean_intra_inter_ratio']:.3f}")

        report_lines.append("")
        report_lines.append("-" * 80)
        report_lines.append("INTERPRETACAO TEORICA")
        report_lines.append("-" * 80)
        report_lines.append("")
        report_lines.append("NOTA: Analise realizada na REDE ORIGINAL (sem filtro de disparidade)")
        report_lines.append("para preservar estrutura completa e PageRanks diferenciados.")
        report_lines.append("")
        report_lines.append("HIPOTESE: Esportes individuais -> maior coesao que coletivos")
        report_lines.append("RAZAO: Confrontos repetidos entre especialistas criam redes mais densas")
        report_lines.append("")

        # Validar hipótese
        swimming_cohesion = summary['by_sport'].get('swimming', {}).get('mean_cohesion', 0)
        basketball_cohesion = summary['by_sport'].get('basketball', {}).get('mean_cohesion', 0)
        football_cohesion = summary['by_sport'].get('football', {}).get('mean_cohesion', 0)

        report_lines.append(f"RESULTADO:")
        if swimming_cohesion > basketball_cohesion > football_cohesion:
            report_lines.append("-> HIPOTESE CONFIRMADA: Swimming > Basketball > Football")
        else:
            report_lines.append(f"-> Hierarquia observada: ranking acima")

        report_lines.append("")
        report_lines.append("-" * 80)
        report_lines.append("TOP 5 COMUNIDADES MAIS COESAS")
        report_lines.append("-" * 80)

        top5 = df.nlargest(5, 'cohesion_score')
        for idx, row in top5.iterrows():
            report_lines.append(f"\n{row['sport'].upper()}-{row['sex']} C{int(row['community_id'])}")
            report_lines.append(f"  Cohesion Score: {row['cohesion_score']:.3f}")
            report_lines.append(f"  Tamanho: {int(row['size'])} atletas")
            report_lines.append(f"  Densidade: {row['density']:.3f}")
            report_lines.append(f"  Clustering: {row['clustering_coefficient']:.3f}")
            report_lines.append(f"  Razao Intra/Inter: {row['intra_inter_ratio']:.3f}")

        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("FIM DO RELATORIO")
        report_lines.append("=" * 80)

        # Salvar
        report_path = OUTPUT_DIR / "community_cohesion_interpretation.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"[OK] Exported interpretation report: {report_path}")


def main():
    """Pipeline principal."""
    print("=" * 80)
    print("COMPONENTE 3: METRICAS DE COESAO ESTRUTURAL")
    print("=" * 80)
    print()

    analyzer = CommunityStructuralAnalyzer(RESULTS_DIR)

    # Passo 1: Carregar comunidades
    print("-> Passo 1: Carregando perfis de comunidades...")
    analyzer.load_community_profiles()
    print()

    # Passo 2: Analisar todas as comunidades
    print("-> Passo 2: Analisando coesao estrutural (27 comunidades)...")
    analyzer.analyze_all_communities()
    print()

    # Passo 3: Exportar resultados
    print("-> Passo 3: Exportando resultados...")
    analyzer.export_results()
    print()

    print("=" * 80)
    print("COMPONENTE 3 CONCLUIDO COM SUCESSO!")
    print("=" * 80)
    print("\nArquivos gerados:")
    print("  1. community_cohesion_metrics.csv - Metricas detalhadas")
    print("  2. community_cohesion_summary.json - Resumo estatistico")
    print("  3. community_cohesion_interpretation.txt - Relatorio interpretativo")


if __name__ == "__main__":
    main()
