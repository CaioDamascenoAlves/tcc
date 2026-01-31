#!/usr/bin/env python3
"""
Geração de Rede Bipartida para Análise de Rivalidades Olímpicas

MODELAGEM:
- Dois tipos de nós: Atletas e Pódios
- Arestas direcionadas: Atleta → Pódio (ponderadas por medalha)
- Peso: Gold=5, Silver=3, Bronze=2

VANTAGENS:
- Zero fragmentação (rede única e conectada)
- Preserva informação temporal (cada pódio tem timestamp)
- Suporta HITS, PageRank, Louvain, todas centralidades
- Captura dominância através de Authority (HITS)

MÉTRICAS CALCULADAS:
- HITS (Authority para atletas, Hub para pódios)
- PageRank (flui entre atletas e pódios)
- Degree (total e ponderado)
- Betweenness, Closeness
- Entropia de Shannon (diversidade de medalhas)
- Gini (desigualdade de authorities)
"""

import pandas as pd
import networkx as nx
from networkx.algorithms import bipartite
import numpy as np
import os
import json
import warnings
from collections import Counter
from pathlib import Path
import community as community_louvain

warnings.filterwarnings('ignore')


class BipartiteOlympicNetwork:
    """
    Cria e analisa rede bipartida de atletas e pódios olímpicos.
    """

    def __init__(self, data_path: str, selected_sports: list, base_dir: str = 'results_bipartite'):
        self.data_path = data_path
        self.selected_sports = selected_sports
        self.base_dir = base_dir
        self.df = None
        self.G = None  # Rede bipartida

        # Pesos por tipo de medalha
        self.medal_weights = {
            'Gold': 5,
            'Silver': 3,
            'Bronze': 2
        }

        os.makedirs(self.base_dir, exist_ok=True)

    def load_and_filter_data(self):
        """Carrega e filtra os dados."""
        print("="*80)
        print("CARREGANDO DADOS")
        print("="*80)

        self.df = pd.read_csv(self.data_path)
        total_records = len(self.df)
        print(f"Total de registros: {total_records:,}")

        # Filtrar esportes selecionados e medalhistas
        self.df = self.df[
            (self.df['Sport'].isin(self.selected_sports)) &
            self.df['Medal'].notna()
        ]

        print(f"Medalhistas dos esportes selecionados: {len(self.df):,}")

        # Remover duplicatas
        duplicates = self.df.duplicated(subset=['Year', 'Sport', 'Event', 'Sex', 'Medal', 'ID']).sum()
        if duplicates > 0:
            print(f"[LIMPEZA] Removendo {duplicates} registros duplicados...")
            self.df = self.df.drop_duplicates(subset=['Year', 'Sport', 'Event', 'Sex', 'Medal', 'ID'])

        print(f"\n[OK] Dados limpos: {len(self.df):,} registros")
        print(f"[OK] Atletas únicos: {self.df['ID'].nunique():,}")
        print(f"[OK] Pódios únicos: {self._count_unique_podiums()}")

        return self.df

    def _count_unique_podiums(self):
        """Conta pódios únicos (Year, Event, Sex)."""
        podiums = self.df.groupby(['Year', 'Event', 'Sex']).size()
        return len(podiums)

    def create_bipartite_network(self, sport_data, sport_name, sex):
        """Cria a rede bipartida Atletas ↔ Pódios para um esporte/sexo específico."""
        print(f"\nCriando rede bipartida: {sport_name} {sex}")

        G = nx.Graph()  # NÃO-DIRECIONADA para conectividade!

        # Agregar dados de atletas (para atributos dos nós)
        athlete_data = self.df.groupby('ID').agg({
            'Name': 'first',
            'Sex': 'first',
            'Age': lambda x: x.dropna().iloc[-1] if len(x.dropna()) > 0 else 0,
            'Height': lambda x: x.dropna().iloc[-1] if len(x.dropna()) > 0 else 0,
            'Weight': lambda x: x.dropna().iloc[-1] if len(x.dropna()) > 0 else 0,
            'Team': 'first',
            'NOC': 'first',
            'Games': 'last',
            'Sport': lambda x: ', '.join(sorted(x.unique())),  # Pode competir em múltiplos esportes
            'Medal': lambda x: {
                'Gold': (x == 'Gold').sum(),
                'Silver': (x == 'Silver').sum(),
                'Bronze': (x == 'Bronze').sum()
            }
        }).reset_index()

        # Adicionar nós de atletas
        print("\nAdicionando nós de atletas...")
        for _, row in athlete_data.iterrows():
            medal_counts = row['Medal']
            self.G.add_node(
                f"athlete_{row['ID']}",
                bipartite=0,  # Tipo: atleta
                node_type='athlete',
                athlete_id=row['ID'],
                name=row['Name'],
                sex=row['Sex'],
                age=row['Age'] if pd.notna(row['Age']) else 0,
                height=row['Height'] if pd.notna(row['Height']) else 0,
                weight=row['Weight'] if pd.notna(row['Weight']) else 0,
                team=row['Team'],
                noc=row['NOC'],
                sports=row['Sport'],
                gold_medals=medal_counts['Gold'],
                silver_medals=medal_counts['Silver'],
                bronze_medals=medal_counts['Bronze'],
                total_medals=medal_counts['Gold'] + medal_counts['Silver'] + medal_counts['Bronze']
            )

        # Criar identificadores de pódios e adicionar nós
        print("Adicionando nós de pódios...")
        podium_data = self.df.groupby(['Year', 'Sport', 'Event', 'Sex']).agg({
            'City': 'first',
            'Games': 'first',
            'ID': 'nunique'  # Número de atletas únicos no pódio
        }).reset_index()

        for _, row in podium_data.iterrows():
            podium_id = f"podium_{row['Year']}_{row['Sport']}_{row['Event']}_{row['Sex']}"
            # Limpar caracteres especiais do ID
            podium_id = podium_id.replace(' ', '_').replace(',', '').replace('/', '_').replace("'", '')
            podium_id = ''.join(c for c in podium_id if c.isalnum() or c == '_')

            self.G.add_node(
                podium_id,
                bipartite=1,  # Tipo: pódio
                node_type='podium',
                year=row['Year'],
                sport=row['Sport'],
                event=row['Event'],
                sex=row['Sex'],
                city=row['City'],
                games=row['Games'],
                num_athletes=row['ID']
            )

        # Adicionar arestas: Atleta → Pódio
        print("Adicionando arestas Atleta → Pódio...")
        edges_added = 0

        for _, row in self.df.iterrows():
            athlete_node = f"athlete_{row['ID']}"
            podium_id = f"podium_{row['Year']}_{row['Sport']}_{row['Event']}_{row['Sex']}"
            podium_id = podium_id.replace(' ', '_').replace(',', '').replace('/', '_').replace("'", '')
            podium_id = ''.join(c for c in podium_id if c.isalnum() or c == '_')

            medal = row['Medal']
            weight = self.medal_weights.get(medal, 1)

            self.G.add_edge(
                athlete_node,
                podium_id,
                medal=medal,
                weight=weight,
                year=row['Year'],
                sport=row['Sport'],
                event=row['Event']
            )
            edges_added += 1

        print(f"\n[OK] Rede bipartida criada:")
        print(f"  - Nós de atletas: {sum(1 for n, d in self.G.nodes(data=True) if d.get('bipartite') == 0):,}")
        print(f"  - Nós de pódios: {sum(1 for n, d in self.G.nodes(data=True) if d.get('bipartite') == 1):,}")
        print(f"  - Arestas: {self.G.number_of_edges():,}")
        print(f"  - Densidade: {nx.density(self.G):.6f}")
        print(f"  - Componentes conectados: {nx.number_connected_components(self.G)}")
        print(f"  - Rede conectada: {nx.is_connected(self.G)}")

        return self.G

    def calculate_metrics(self):
        """Calcula todas as métricas da rede bipartida."""
        print("\n" + "="*80)
        print("CALCULANDO MÉTRICAS")
        print("="*80)

        metrics = {}

        # 1. HITS (Hubs and Authorities)
        print("\n[1/7] Calculando HITS (Hubs and Authorities)...")
        hubs, authorities = nx.hits(self.G, max_iter=1000, normalized=True)
        metrics['hubs'] = hubs
        metrics['authorities'] = authorities

        # 2. PageRank
        print("[2/7] Calculando PageRank...")
        metrics['pagerank'] = nx.pagerank(self.G, weight='weight', max_iter=1000)

        # 3. Degree (total e ponderado)
        print("[3/7] Calculando Degree (total e ponderado)...")
        metrics['degree'] = dict(self.G.degree())
        metrics['degree_weighted'] = dict(self.G.degree(weight='weight'))

        # 4. Betweenness Centrality
        print("[4/7] Calculando Betweenness Centrality...")
        metrics['betweenness'] = nx.betweenness_centrality(self.G, weight='weight')

        # 5. Closeness Centrality
        print("[5/7] Calculando Closeness Centrality...")
        metrics['closeness'] = nx.closeness_centrality(self.G)

        # 6. Entropia de Shannon (para atletas - diversidade de medalhas)
        print("[6/7] Calculando Entropia de Shannon...")
        metrics['entropy'] = self._calculate_entropy()

        # 7. Gini (desigualdade de authorities)
        print("[7/7] Calculando Coeficiente de Gini...")
        metrics['gini_authorities'] = self._calculate_gini([authorities[n] for n in authorities])

        print(f"\n[OK] Métricas calculadas!")

        return metrics

    def _calculate_entropy(self):
        """Calcula entropia de Shannon para diversidade de medalhas por atleta."""
        entropy = {}

        for node, data in self.G.nodes(data=True):
            if data.get('bipartite') == 0:  # Apenas atletas
                gold = data.get('gold_medals', 0)
                silver = data.get('silver_medals', 0)
                bronze = data.get('bronze_medals', 0)
                total = gold + silver + bronze

                if total > 0:
                    p_gold = gold / total
                    p_silver = silver / total
                    p_bronze = bronze / total

                    # Entropia de Shannon: H = -Σ p(x) × log2(p(x))
                    H = 0
                    for p in [p_gold, p_silver, p_bronze]:
                        if p > 0:
                            H -= p * np.log2(p)

                    entropy[node] = H
                else:
                    entropy[node] = 0

        return entropy

    def _calculate_gini(self, values):
        """Calcula coeficiente de Gini (desigualdade)."""
        values = np.array(sorted(values))
        n = len(values)

        if n == 0 or values.sum() == 0:
            return 0

        index = np.arange(1, n + 1)
        gini = (2 * np.sum(index * values)) / (n * values.sum()) - (n + 1) / n

        return gini

    def export_results(self):
        """Exporta rede e métricas."""
        print("\n" + "="*80)
        print("EXPORTANDO RESULTADOS")
        print("="*80)

        # Calcular métricas
        metrics = self.calculate_metrics()

        # 1. Salvar rede GEXF (limpar valores None primeiro)
        # Converter None em strings vazias para compatibilidade com GEXF
        for node, data in self.G.nodes(data=True):
            for key, value in data.items():
                if value is None:
                    self.G.nodes[node][key] = ''
                elif isinstance(value, (int, float)) and np.isnan(value):
                    self.G.nodes[node][key] = 0

        gexf_path = os.path.join(self.base_dir, 'bipartite_network.gexf')
        nx.write_gexf(self.G, gexf_path)
        print(f"\n[1/4] Rede GEXF salva: {gexf_path}")

        # 2. Exportar métricas de ATLETAS
        athlete_nodes = [n for n, d in self.G.nodes(data=True) if d.get('bipartite') == 0]

        athlete_metrics = []
        for node in athlete_nodes:
            data = self.G.nodes[node]

            row = {
                'athlete_id': data.get('athlete_id'),
                'name': data.get('name'),
                'sex': data.get('sex'),
                'noc': data.get('noc'),
                'sports': data.get('sports'),
                'gold_medals': data.get('gold_medals', 0),
                'silver_medals': data.get('silver_medals', 0),
                'bronze_medals': data.get('bronze_medals', 0),
                'total_medals': data.get('total_medals', 0),
                'authority': metrics['authorities'].get(node, 0),
                'pagerank': metrics['pagerank'].get(node, 0),
                'degree': metrics['degree'].get(node, 0),
                'degree_weighted': metrics['degree_weighted'].get(node, 0),
                'betweenness': metrics['betweenness'].get(node, 0),
                'closeness': metrics['closeness'].get(node, 0),
                'entropy_medals': metrics['entropy'].get(node, 0)
            }
            athlete_metrics.append(row)

        df_athletes = pd.DataFrame(athlete_metrics)

        # Adicionar scores compostos
        df_athletes['dominance_score'] = (
            0.4 * df_athletes['authority'] +
            0.3 * df_athletes['degree_weighted'] / df_athletes['degree_weighted'].max() +
            0.2 * (df_athletes['gold_medals'] / (df_athletes['total_medals'] + 1)) +
            0.1 * (1 - df_athletes['entropy_medals'] / np.log2(3))  # Normalizar entropia
        )

        athletes_path = os.path.join(self.base_dir, 'athlete_metrics.csv')
        df_athletes.to_csv(athletes_path, index=False)
        print(f"[2/4] Métricas de atletas salvas: {athletes_path}")

        # 3. Exportar métricas de PÓDIOS
        podium_nodes = [n for n, d in self.G.nodes(data=True) if d.get('bipartite') == 1]

        podium_metrics = []
        for node in podium_nodes:
            data = self.G.nodes[node]

            row = {
                'podium_id': node,
                'year': data.get('year'),
                'sport': data.get('sport'),
                'event': data.get('event'),
                'sex': data.get('sex'),
                'city': data.get('city'),
                'num_athletes': data.get('num_athletes', 0),
                'hub': metrics['hubs'].get(node, 0),
                'pagerank': metrics['pagerank'].get(node, 0),
                'degree': metrics['degree'].get(node, 0),
                'degree_weighted': metrics['degree_weighted'].get(node, 0),
                'betweenness': metrics['betweenness'].get(node, 0),
                'closeness': metrics['closeness'].get(node, 0)
            }
            podium_metrics.append(row)

        df_podiums = pd.DataFrame(podium_metrics)
        podiums_path = os.path.join(self.base_dir, 'podium_metrics.csv')
        df_podiums.to_csv(podiums_path, index=False)
        print(f"[3/4] Métricas de pódios salvas: {podiums_path}")

        # 4. Salvar estatísticas gerais
        summary = {
            'network_stats': {
                'total_nodes': self.G.number_of_nodes(),
                'athlete_nodes': len(athlete_nodes),
                'podium_nodes': len(podium_nodes),
                'total_edges': self.G.number_of_edges(),
                'density': nx.density(self.G),
                'connected_components': nx.number_connected_components(self.G),
                'is_connected': nx.is_connected(self.G)
            },
            'gini_coefficient': {
                'authorities': metrics['gini_authorities']
            },
            'top_10_athletes_by_authority': df_athletes.nlargest(10, 'authority')[['name', 'authority', 'gold_medals', 'total_medals']].to_dict('records'),
            'top_10_athletes_by_dominance': df_athletes.nlargest(10, 'dominance_score')[['name', 'dominance_score', 'authority', 'gold_medals']].to_dict('records'),
            'top_10_podiums_by_hub': df_podiums.nlargest(10, 'hub')[['event', 'year', 'hub', 'num_athletes']].to_dict('records')
        }

        summary_path = os.path.join(self.base_dir, 'network_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=4, default=str)
        print(f"[4/4] Resumo da rede salvo: {summary_path}")

        print(f"\n{'='*80}")
        print("EXPORTAÇÃO CONCLUÍDA")
        print("="*80)

        return df_athletes, df_podiums, summary

    def print_top_athletes(self, df_athletes, n=20):
        """Imprime top N atletas por diferentes métricas."""
        print("\n" + "="*80)
        print(f"TOP {n} ATLETAS")
        print("="*80)

        print(f"\n--- POR AUTHORITY (HITS) - Dominância Estrutural ---")
        top_authority = df_athletes.nlargest(n, 'authority')[['name', 'authority', 'gold_medals', 'total_medals', 'sports']]
        print(top_authority.to_string(index=False))

        print(f"\n--- POR DOMINANCE SCORE - Score Composto ---")
        top_dominance = df_athletes.nlargest(n, 'dominance_score')[['name', 'dominance_score', 'authority', 'gold_medals', 'sports']]
        print(top_dominance.to_string(index=False))

        print(f"\n--- POR PAGERANK - Influência Global ---")
        top_pagerank = df_athletes.nlargest(n, 'pagerank')[['name', 'pagerank', 'authority', 'total_medals', 'sports']]
        print(top_pagerank.to_string(index=False))


def main():
    """Executa análise completa."""

    analyzer = BipartiteOlympicNetwork(
        data_path='../../data/athlete_events.csv',
        selected_sports=['Swimming', 'Basketball', 'Football', 'Athletics', 'Judo', 'Boxing'],
        base_dir='../../results_bipartite'
    )

    # Pipeline completo
    analyzer.load_and_filter_data()
    analyzer.create_bipartite_network()
    df_athletes, df_podiums, summary = analyzer.export_results()
    analyzer.print_top_athletes(df_athletes, n=20)

    print("\n" + "="*80)
    print("ANÁLISE BIPARTIDA CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print(f"\nResultados salvos em: {analyzer.base_dir}/")
    print("\nArquivos gerados:")
    print("  - bipartite_network.gexf (rede completa)")
    print("  - athlete_metrics.csv (métricas de atletas)")
    print("  - podium_metrics.csv (métricas de pódios)")
    print("  - network_summary.json (estatísticas gerais)")


if __name__ == "__main__":
    main()
