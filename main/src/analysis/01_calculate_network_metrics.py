#!/usr/bin/env python3
"""
Calcula métricas de rede para os 12 casos de estudo selecionados.

Métricas calculadas:
- PageRank (influência)
- HITS (Authority & Hub)
- Louvain (detecção de comunidades)
- Centralidades: Degree, Betweenness, Closeness
- Métricas globais: densidade, diâmetro, clustering, componentes
"""

import networkx as nx
import pandas as pd
import numpy as np
from pathlib import Path
import json
import warnings
from collections import Counter

warnings.filterwarnings('ignore')

# Importar community detection (python-louvain)
try:
    import community as community_louvain
except ImportError:
    print("AVISO: python-louvain não instalado. Instale com: pip install python-louvain")
    community_louvain = None


class NetworkMetricsAnalyzer:
    """Calcula métricas de rede para análise de rivalidades olímpicas."""

    def __init__(self, networks_dir: str, output_dir: str):
        self.networks_dir = Path(networks_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Definir os 12 casos de estudo
        self.case_studies = [
            # Par 1: Futebol
            {'id': 1, 'sport': 'football', 'file': 'football_M_Football_Mens_Football.gexf', 'name': 'M Football', 'gender': 'M'},
            {'id': 2, 'sport': 'football', 'file': 'football_F_Football_Womens_Football.gexf', 'name': 'F Football', 'gender': 'F'},

            # Par 2: Basquete
            {'id': 3, 'sport': 'basketball', 'file': 'basketball_M_Basketball_Mens_Basketball.gexf', 'name': 'M Basketball', 'gender': 'M'},
            {'id': 4, 'sport': 'basketball', 'file': 'basketball_F_Basketball_Womens_Basketball.gexf', 'name': 'F Basketball', 'gender': 'F'},

            # Par 3: Atletismo 100m
            {'id': 5, 'sport': 'athletics', 'file': 'athletics_M_100m.gexf', 'name': 'M 100m', 'gender': 'M'},
            {'id': 6, 'sport': 'athletics', 'file': 'athletics_F_100m.gexf', 'name': 'F 100m', 'gender': 'F'},

            # Par 4: Natação 100m Livre
            {'id': 7, 'sport': 'swimming', 'file': 'swimming_M_100m_Freestyle.gexf', 'name': 'M 100m Freestyle', 'gender': 'M'},
            {'id': 8, 'sport': 'swimming', 'file': 'swimming_F_100m_Freestyle.gexf', 'name': 'F 100m Freestyle', 'gender': 'F'},

            # Par 5: Judô Peso Médio
            {'id': 9, 'sport': 'judo', 'file': 'judo_M_-90kg.gexf', 'name': 'M -90kg', 'gender': 'M'},
            {'id': 10, 'sport': 'judo', 'file': 'judo_F_-70kg.gexf', 'name': 'F -70kg', 'gender': 'F'},

            # Par 6: Boxe Peso Médio/Welter
            {'id': 11, 'sport': 'boxing', 'file': 'boxing_M_Welter_63-69kg.gexf', 'name': 'M Welter', 'gender': 'M'},
            {'id': 12, 'sport': 'boxing', 'file': 'boxing_F_Middle_69-75kg.gexf', 'name': 'F Middle', 'gender': 'F'}
        ]

    def load_network(self, case_study: dict) -> nx.DiGraph:
        """Carrega rede GEXF."""
        file_path = self.networks_dir / case_study['sport'] / case_study['file']

        if not file_path.exists():
            print(f"❌ ERRO: Arquivo não encontrado: {file_path}")
            return None

        try:
            G = nx.read_gexf(file_path)
            print(f"✓ Carregado: {case_study['name']} ({G.number_of_nodes()} nós, {G.number_of_edges()} arestas)")
            return G
        except Exception as e:
            print(f"❌ ERRO ao carregar {case_study['name']}: {e}")
            return None

    def calculate_pagerank(self, G: nx.DiGraph, weight='weight') -> dict:
        """Calcula PageRank."""
        try:
            return nx.pagerank(G, weight=weight, max_iter=100)
        except:
            return nx.pagerank(G, max_iter=100)

    def calculate_hits(self, G: nx.DiGraph) -> tuple:
        """Calcula HITS (hubs e authorities)."""
        try:
            hubs, authorities = nx.hits(G, max_iter=100)
            return hubs, authorities
        except:
            # HITS pode falhar em grafos desconectados
            return {}, {}

    def calculate_communities(self, G: nx.DiGraph) -> dict:
        """Detecta comunidades usando Louvain."""
        if community_louvain is None:
            return {}

        try:
            # Converter para grafo não-direcionado
            G_undirected = G.to_undirected()

            # Louvain
            partition = community_louvain.best_partition(G_undirected, weight='weight')
            return partition
        except Exception as e:
            print(f"  ⚠️  Erro na detecção de comunidades: {e}")
            return {}

    def calculate_centralities(self, G: nx.DiGraph) -> dict:
        """Calcula centralidades."""
        centralities = {}

        # Degree centrality (in e out)
        centralities['in_degree'] = dict(G.in_degree(weight='weight'))
        centralities['out_degree'] = dict(G.out_degree(weight='weight'))

        # Betweenness centrality (pode ser lento para redes grandes)
        try:
            if G.number_of_nodes() < 500:
                centralities['betweenness'] = nx.betweenness_centrality(G, weight='weight')
            else:
                # Para redes grandes, usar amostragem
                centralities['betweenness'] = nx.betweenness_centrality(G, k=min(100, G.number_of_nodes()), weight='weight')
        except:
            centralities['betweenness'] = {}

        # Closeness centrality (apenas para componente maior)
        try:
            if nx.is_weakly_connected(G):
                centralities['closeness'] = nx.closeness_centrality(G, distance='weight')
            else:
                # Calcular só para o maior componente
                largest_cc = max(nx.weakly_connected_components(G), key=len)
                G_largest = G.subgraph(largest_cc)
                closeness_largest = nx.closeness_centrality(G_largest, distance='weight')
                centralities['closeness'] = {node: closeness_largest.get(node, 0) for node in G.nodes()}
        except:
            centralities['closeness'] = {}

        return centralities

    def calculate_global_metrics(self, G: nx.DiGraph) -> dict:
        """Calcula métricas globais da rede."""
        metrics = {}

        # Básicas
        metrics['nodes'] = G.number_of_nodes()
        metrics['edges'] = G.number_of_edges()
        metrics['density'] = nx.density(G)

        # Componentes
        metrics['num_components'] = nx.number_weakly_connected_components(G)
        metrics['is_connected'] = nx.is_weakly_connected(G)

        # Componente maior
        largest_cc = max(nx.weakly_connected_components(G), key=len)
        metrics['largest_component_size'] = len(largest_cc)
        metrics['largest_component_fraction'] = len(largest_cc) / G.number_of_nodes()

        # Diâmetro (só para redes conectadas ou componente maior)
        try:
            if nx.is_weakly_connected(G):
                metrics['diameter'] = nx.diameter(G.to_undirected())
            else:
                G_largest = G.subgraph(largest_cc)
                metrics['diameter'] = nx.diameter(G_largest.to_undirected())
        except:
            metrics['diameter'] = None

        # Clustering coefficient
        try:
            G_undirected = G.to_undirected()
            metrics['avg_clustering'] = nx.average_clustering(G_undirected, weight='weight')
        except:
            metrics['avg_clustering'] = None

        return metrics

    def analyze_network(self, case_study: dict) -> dict:
        """Análise completa de uma rede."""
        print(f"\n{'='*80}")
        print(f"Analisando: {case_study['name']} ({case_study['sport'].upper()})")
        print("="*80)

        # Carregar rede
        G = self.load_network(case_study)
        if G is None:
            return None

        results = {
            'id': case_study['id'],
            'sport': case_study['sport'],
            'name': case_study['name'],
            'gender': case_study['gender'],
            'file': case_study['file']
        }

        # Métricas globais
        print("  Calculando métricas globais...")
        results['global_metrics'] = self.calculate_global_metrics(G)

        # PageRank
        print("  Calculando PageRank...")
        pagerank = self.calculate_pagerank(G)
        results['pagerank'] = pagerank

        # HITS
        print("  Calculando HITS...")
        hubs, authorities = self.calculate_hits(G)
        results['hubs'] = hubs
        results['authorities'] = authorities

        # Comunidades
        print("  Detectando comunidades (Louvain)...")
        communities = self.calculate_communities(G)
        results['communities'] = communities

        if communities:
            num_communities = len(set(communities.values()))
            print(f"    → {num_communities} comunidades detectadas")
            results['global_metrics']['num_communities'] = num_communities

        # Centralidades
        print("  Calculando centralidades...")
        centralities = self.calculate_centralities(G)
        results['centralities'] = centralities

        # Top 10 atletas por métrica
        print("  Gerando rankings...")
        results['top_pagerank'] = self._get_top_athletes(G, pagerank, 10)
        results['top_authorities'] = self._get_top_athletes(G, authorities, 10) if authorities else []
        results['top_betweenness'] = self._get_top_athletes(G, centralities['betweenness'], 10) if centralities['betweenness'] else []

        return results

    def _get_top_athletes(self, G: nx.DiGraph, metric_dict: dict, top_n: int = 10) -> list:
        """Retorna top N atletas com informações."""
        if not metric_dict:
            return []

        # Ordenar por valor
        sorted_athletes = sorted(metric_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]

        # Adicionar informações dos nós
        top_list = []
        for athlete_id, score in sorted_athletes:
            athlete_data = G.nodes[athlete_id]
            top_list.append({
                'rank': len(top_list) + 1,
                'id': athlete_id,
                'name': athlete_data.get('name', 'Unknown'),
                'noc': athlete_data.get('noc', 'UNK'),
                'score': float(score),
                'gold_medals': int(athlete_data.get('gold_medals', 0)),
                'total_medals': int(athlete_data.get('total_medals', 0))
            })

        return top_list

    def run_analysis(self):
        """Executa análise completa dos 12 casos de estudo."""
        print("\n" + "="*80)
        print("ANÁLISE DE MÉTRICAS DE REDE - 12 CASOS DE ESTUDO")
        print("="*80)

        all_results = []

        for case_study in self.case_studies:
            results = self.analyze_network(case_study)
            if results:
                all_results.append(results)

        # Salvar resultados
        self._save_results(all_results)

        # Gerar relatório
        self._generate_report(all_results)

        print(f"\n{'='*80}")
        print("ANÁLISE CONCLUÍDA!")
        print("="*80)
        print(f"Resultados salvos em: {self.output_dir}")

    def _save_results(self, all_results: list):
        """Salva resultados em múltiplos formatos."""
        print(f"\n{'='*80}")
        print("SALVANDO RESULTADOS")
        print("="*80)

        # 1. Métricas globais (CSV)
        global_metrics_list = []
        for result in all_results:
            row = {
                'id': result['id'],
                'sport': result['sport'],
                'name': result['name'],
                'gender': result['gender']
            }
            row.update(result['global_metrics'])
            global_metrics_list.append(row)

        df_global = pd.DataFrame(global_metrics_list)
        global_csv = self.output_dir / 'global_metrics.csv'
        df_global.to_csv(global_csv, index=False)
        print(f"✓ Métricas globais: {global_csv}")

        # 2. Top 10 PageRank por rede (CSV)
        pagerank_list = []
        for result in all_results:
            for athlete in result['top_pagerank']:
                pagerank_list.append({
                    'network_id': result['id'],
                    'network_name': result['name'],
                    'sport': result['sport'],
                    'gender': result['gender'],
                    **athlete
                })

        df_pagerank = pd.DataFrame(pagerank_list)
        pagerank_csv = self.output_dir / 'top_pagerank.csv'
        df_pagerank.to_csv(pagerank_csv, index=False)
        print(f"✓ Top PageRank: {pagerank_csv}")

        # 3. Top 10 Authorities (CSV)
        authorities_list = []
        for result in all_results:
            for athlete in result['top_authorities']:
                authorities_list.append({
                    'network_id': result['id'],
                    'network_name': result['name'],
                    'sport': result['sport'],
                    'gender': result['gender'],
                    **athlete
                })

        if authorities_list:
            df_authorities = pd.DataFrame(authorities_list)
            authorities_csv = self.output_dir / 'top_authorities.csv'
            df_authorities.to_csv(authorities_csv, index=False)
            print(f"✓ Top Authorities: {authorities_csv}")

        # 4. JSON completo (para uso posterior)
        json_output = self.output_dir / 'all_metrics.json'
        with open(json_output, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"✓ JSON completo: {json_output}")

    def _generate_report(self, all_results: list):
        """Gera relatório em Markdown."""
        report_path = self.output_dir / 'metrics_report.md'

        with open(report_path, 'w') as f:
            f.write("# Relatório de Métricas de Rede\n\n")
            f.write("**Data:** " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
            f.write("---\n\n")

            # Resumo geral
            f.write("## Resumo Geral\n\n")
            f.write(f"**Total de redes analisadas:** {len(all_results)}\n\n")

            # Tabela de métricas globais
            f.write("### Métricas Globais\n\n")
            f.write("| # | Evento | Nós | Arestas | Densidade | Componentes | Comunidades |\n")
            f.write("|---|--------|-----|---------|-----------|-------------|-------------|\n")

            for result in all_results:
                gm = result['global_metrics']
                f.write(f"| {result['id']} | {result['name']} | {gm['nodes']} | {gm['edges']} | "
                       f"{gm['density']:.4f} | {gm['num_components']} | "
                       f"{gm.get('num_communities', 'N/A')} |\n")

            f.write("\n---\n\n")

            # Top PageRank de cada rede
            f.write("## Top 5 Atletas por PageRank\n\n")

            for result in all_results:
                f.write(f"### {result['name']} ({result['sport'].upper()})\n\n")
                f.write("| Rank | Nome | País | PageRank | Ouros | Total |\n")
                f.write("|------|------|------|----------|-------|-------|\n")

                for athlete in result['top_pagerank'][:5]:
                    f.write(f"| {athlete['rank']} | {athlete['name']} | {athlete['noc']} | "
                           f"{athlete['score']:.6f} | {athlete['gold_medals']} | {athlete['total_medals']} |\n")

                f.write("\n")

        print(f"✓ Relatório: {report_path}")


if __name__ == "__main__":
    analyzer = NetworkMetricsAnalyzer(
        networks_dir='../../results_per_event_cleaned',
        output_dir='../../results_metrics'
    )

    analyzer.run_analysis()
