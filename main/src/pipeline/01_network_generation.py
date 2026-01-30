import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import warnings
from collections import Counter
from typing import Dict, List, Tuple, Optional
import community as community_louvain
from pathlib import Path

# Configurações globais
warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class SportsNetworkAnalyzer:
    """
    Classe principal para análise de redes esportivas.

    Funcionalidades:
    - Criação de redes direcionadas ponderadas
    - Cálculo de métricas de centralidade
    - Detecção de comunidades
    - Análise de distribuição de pesos
    """
    
    def __init__(self, data_path: str, selected_sports: List[str] = None, base_dir: str = 'resultados_esportes'):
        """
        Inicializa o analisador.
        
        Args:
            data_path: Caminho para o arquivo CSV dos dados
            selected_sports: Lista dos esportes selecionados
            base_dir: Diretório base para salvar resultados
        """
        self.data_path = data_path
        self.selected_sports = selected_sports or ['Swimming', 'Basketball', 'Football', 'Athletics', 'Judo', 'Boxing']
        self.base_dir = base_dir
        self.df = None
        self.results = {}
        self.sport_types = None
        
        # Criar diretório base
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Carregar classificação de esportes
        self.load_sport_classification()
        
    def load_sport_classification(self):
        """Gera classificação simples baseada nos esportes selecionados."""
        print("Usando classificação simples direta...")

        self.sport_types = {
            'Swimming': {
                'type': 'mixed',
                'individual_events': [],  # Será preenchido dinamicamente
                'team_events': []         # Será preenchido dinamicamente
            },
            'Basketball': {
                'type': 'team_only',
                'individual_events': [],
                'team_events': []  # Todos os eventos
            },
            'Football': {
                'type': 'team_only',
                'individual_events': [],
                'team_events': []  # Todos os eventos
            },
            'Athletics': {
                'type': 'mixed',
                'individual_events': [],
                'team_events': []
            },
            'Judo': {
                'type': 'individual_only',
                'individual_events': [],  # Todos os eventos
                'team_events': []
            },
            'Boxing': {
                'type': 'individual_only',
                'individual_events': [],  # Todos os eventos
                'team_events': []
            }
        }
        
    def load_and_filter_data(self) -> pd.DataFrame:
        """Carrega e filtra os dados."""
        print("Carregando dados...")
        self.df = pd.read_csv(self.data_path)

        # Estatísticas iniciais
        total_records = len(self.df)
        print(f"Total de registros: {total_records:,}")

        # Filtrar apenas esportes selecionados e medalhistas
        self.df = self.df[
            (self.df['Sport'].isin(self.selected_sports)) &
            self.df['Medal'].notna()
        ]

        print(f"Medalhistas dos esportes selecionados: {len(self.df):,}")

        # LIMPEZA 1: Remover duplicatas
        duplicates_before = self.df.duplicated(subset=['Year', 'Sport', 'Event', 'Sex', 'Medal', 'ID']).sum()
        if duplicates_before > 0:
            print(f"[LIMPEZA] Removendo {duplicates_before} registros duplicados...")
            self.df = self.df.drop_duplicates(subset=['Year', 'Sport', 'Event', 'Sex', 'Medal', 'ID'])

        # LIMPEZA 2: Remover pódios com menos de 2 atletas
        print("[LIMPEZA] Analisando podios...")
        self.df['podium_key'] = (
            self.df['Year'].astype(str) + '_' +
            self.df['Sport'] + '_' +
            self.df['Event'] + '_' +
            self.df['Sex']
        )

        # Contar atletas únicos por pódio
        podium_athlete_counts = self.df.groupby('podium_key')['ID'].nunique()

        # Filtrar apenas pódios com 2+ atletas (necessário para criar arestas)
        valid_podiums = podium_athlete_counts[podium_athlete_counts >= 2].index

        removed_solo_podiums = (podium_athlete_counts == 1).sum()
        removed_athletes = self.df[~self.df['podium_key'].isin(valid_podiums)]['ID'].nunique()

        if removed_solo_podiums > 0:
            print(f"[LIMPEZA] Removendo {removed_solo_podiums} podios solo (1 atleta apenas)")
            print(f"[LIMPEZA] Atletas removidos: {removed_athletes}")
            self.df = self.df[self.df['podium_key'].isin(valid_podiums)]

        # Remover coluna temporária
        self.df = self.df.drop(columns=['podium_key'])

        print(f"\n[OK] Dados limpos: {len(self.df):,} registros de {self.df['ID'].nunique():,} atletas")
        print(f"[OK] Podios validos: {len(valid_podiums):,}")

        # Preencher eventos dinamicamente baseado nos dados
        self._classify_events_dynamically()

        return self.df
    
    def _classify_events_dynamically(self):
        """Classifica eventos dinamicamente baseado nos dados reais."""

        def is_team_event(event_name, sport):
            """Determina se um evento é coletivo ou individual com base no esporte."""
            if sport == 'Swimming':
                return ('Relay' in event_name) or ('Team Swimming' in event_name)
            if sport == 'Athletics':
                return ('Relay' in event_name) or (', Team' in event_name) # '4 x' pattern is also very common for relays
            return False

        for sport in self.selected_sports:
            sport_data = self.df[self.df['Sport'] == sport]
            eventos_unicos = sport_data['Event'].unique()
            sport_info = self.sport_types[sport]
            sport_type = sport_info['type']

            if sport_type == 'mixed':
                individual_events = [e for e in eventos_unicos if not is_team_event(e, sport)]
                team_events = [e for e in eventos_unicos if is_team_event(e, sport)]
                sport_info['individual_events'] = individual_events
                sport_info['team_events'] = team_events
                print(f"{sport} (Misto): {len(individual_events)} eventos individuais, {len(team_events)} eventos de equipe")

            elif sport_type == 'team_only':
                sport_info['team_events'] = list(eventos_unicos)
                sport_info['individual_events'] = [] # Clear individual events as it's team_only
                print(f"{sport} (Coletivo): {len(eventos_unicos)} eventos de equipe")
            
            elif sport_type == 'individual_only':
                sport_info['individual_events'] = list(eventos_unicos)
                sport_info['team_events'] = [] # Clear team events as it's individual_only
                print(f"{sport} (Individual): {len(eventos_unicos)} eventos individuais")
    
    def create_athlete_network(self, sport_data: pd.DataFrame, event_filter: List[str] = None) -> nx.DiGraph:
        """
        Cria uma rede direcionada ponderada de atletas.
        
        Args:
            sport_data: DataFrame com dados do esporte específico
            event_filter: Lista de eventos para filtrar (opcional)
            
        Returns:
            nx.DiGraph: Rede direcionada ponderada
        """
        
        # Filtrar por eventos específicos se fornecido
        if event_filter is not None:
            sport_data = sport_data[sport_data['Event'].isin(event_filter)]
        G = nx.DiGraph()

        # CORREÇÃO: Agregar dados por atleta ANTES de adicionar nós
        # Cada atleta tem múltiplas linhas (uma por evento/medalha)
        athlete_aggregated = sport_data.groupby('ID').agg({
            'Name': 'first',  # Nome é sempre o mesmo
            'Sex': 'first',
            'Age': lambda x: x.dropna().iloc[-1] if len(x.dropna()) > 0 else 0,  # Última idade conhecida
            'Height': lambda x: x.dropna().iloc[-1] if len(x.dropna()) > 0 else 0,
            'Weight': lambda x: x.dropna().iloc[-1] if len(x.dropna()) > 0 else 0,
            'Team': 'first',  # Pode variar, usar primeiro
            'NOC': 'first',
            'Games': 'last',  # Última olimpíada que participou
            'City': 'last',
            'Medal': lambda x: {  # Contar medalhas por tipo
                'Gold': (x == 'Gold').sum(),
                'Silver': (x == 'Silver').sum(),
                'Bronze': (x == 'Bronze').sum(),
                'last_medal': x.iloc[-1]  # Última medalha ganha (para compatibilidade)
            }
        }).reset_index()

        # Adicionar nós (atletas) com dados agregados
        for _, row in athlete_aggregated.iterrows():
            medal_counts = row['Medal']
            athlete_info = {
                "name": row['Name'],
                "sex": row['Sex'],
                "age": row['Age'] if pd.notna(row['Age']) else 0,
                "height": row['Height'] if pd.notna(row['Height']) else 0,
                "weight": row['Weight'] if pd.notna(row['Weight']) else 0,
                "team": row['Team'],
                "noc": row['NOC'],
                "games": row['Games'],
                "city": row['City'],
                "medal": medal_counts['last_medal'],  # Última medalha (compatibilidade)
                "gold_medals": medal_counts['Gold'],
                "silver_medals": medal_counts['Silver'],
                "bronze_medals": medal_counts['Bronze'],
                "total_medals": medal_counts['Gold'] + medal_counts['Silver'] + medal_counts['Bronze']
            }
            G.add_node(row['ID'], **athlete_info)
        
        # Adicionar arestas ponderadas entre medalhistas do mesmo evento
        # CRÍTICO: Agrupar por Year + Event para evitar misturar olimpíadas diferentes
        # Cada pódio é único: só atletas que REALMENTE competiram juntos naquele ano
        # Previne auto-loops (atleta competindo contra si mesmo em anos diferentes)
        # Previne arestas fantasmas (atletas de anos diferentes que nunca se enfrentaram)
        for (year, event), event_group in sport_data.groupby(['Year', 'Event']):
            self._add_competition_edges(G, event_group)

        # CRÍTICO: Remover nós isolados (sem conexões diretas)
        isolated_nodes = [node for node in G.nodes() if G.degree(node) == 0]
        if isolated_nodes:
            print(f"[LIMPEZA] Removendo {len(isolated_nodes)} nós isolados (atletas sem competidores diretos)")
            G.remove_nodes_from(isolated_nodes)

        return G
    
    def _add_competition_edges(self, G: nx.DiGraph, event_group: pd.DataFrame):
        """Adiciona arestas ponderadas entre medalhistas de um evento (histórico acumulado)."""

        # VALIDAÇÃO: Verificar se há pelo menos 2 atletas únicos
        unique_athletes = event_group['ID'].nunique()
        if unique_athletes < 2:
            return

        medalists = event_group[['ID', 'Medal']].sort_values(
            by='Medal', key=lambda x: x.map({'Gold': 1, 'Silver': 2, 'Bronze': 3})
        ).values

        # Verificar se é evento de equipe (múltiplos atletas com mesma medalha)
        medal_counts = event_group.groupby('Medal')['ID'].nunique()
        is_team_event = any(count > 1 for count in medal_counts.values)

        # Mapear pesos das conexões (ajustar para eventos de equipe)
        if is_team_event:
            # Para eventos de equipe, reduzir ligeiramente os pesos
            weight_map = {
                ('Gold', 'Bronze'): 4,
                ('Gold', 'Silver'): 2.5,
                ('Silver', 'Bronze'): 1.5
            }
        else:
            weight_map = {
                ('Gold', 'Bronze'): 5,
                ('Gold', 'Silver'): 3,
                ('Silver', 'Bronze'): 2
            }

        # Criar arestas direcionadas: do perdedor para o ganhador
        for i, (loser_id, loser_medal) in enumerate(medalists):
            for winner_id, winner_medal in medalists[:i]:
                # CRÍTICO: Prevenir auto-loops (mesmo atleta em anos diferentes)
                if loser_id == winner_id:
                    continue

                if loser_medal != winner_medal:
                    weight = weight_map.get((winner_medal, loser_medal), 1)

                    if G.has_edge(loser_id, winner_id):
                        G[loser_id][winner_id]['weight'] += weight
                    else:
                        G.add_edge(loser_id, winner_id, weight=weight)
    
    # Função apply_disparity_filter removida (backbone descontinuado)

    def calculate_network_metrics(self, G: nx.DiGraph) -> Dict:
        """
        Calcula métricas abrangentes da rede.
        
        Args:
            G: Grafo para análise
            
        Returns:
            Dict: Dicionário com todas as métricas
        """
        print("Calculando métricas da rede...")
        
        metrics = {
            'basic_metrics': self._calculate_basic_metrics(G),
            'centrality_metrics': self._calculate_centrality_metrics(G),
            'community_metrics': self._calculate_community_metrics(G),
            'node_metrics': self._calculate_node_metrics(G)
        }
        
        return metrics
    
    def _calculate_basic_metrics(self, G: nx.DiGraph) -> Dict:
        """Calcula métricas básicas da rede."""
        return {
            'num_nodes': G.number_of_nodes(),
            'num_edges': G.number_of_edges(),
            'density': nx.density(G),
            'is_strongly_connected': nx.is_strongly_connected(G),
            'is_weakly_connected': nx.is_weakly_connected(G),
            'num_strongly_connected_components': nx.number_strongly_connected_components(G),
            'num_weakly_connected_components': nx.number_weakly_connected_components(G)
        }

    def diagnose_network_integrity(self, G: nx.DiGraph, network_name: str = "Rede"):
        """
        Diagnostica integridade da rede e reporta nos isolados.

        Args:
            G: Grafo para diagnosticar
            network_name: Nome da rede para o relatório
        """
        print(f"\n[DIAGNOSTICO] {network_name}")
        print("=" * 60)

        # Verificar nós isolados (grau 0)
        isolated_nodes = [node for node in G.nodes() if G.degree(node) == 0]

        if len(isolated_nodes) == 0:
            print("[OK] Nenhum no isolado encontrado!")
        else:
            print(f"[ALERTA] {len(isolated_nodes)} nos isolados encontrados:")
            # Mostrar os primeiros 10
            for node in isolated_nodes[:10]:
                node_data = G.nodes[node]
                print(f"  - ID {node}: {node_data.get('name', 'Unknown')}")

            if len(isolated_nodes) > 10:
                print(f"  ... e mais {len(isolated_nodes) - 10} nos isolados")

        # Estatísticas de grau
        degrees = [G.degree(node) for node in G.nodes()]
        if degrees:
            print(f"\nEstatisticas de grau:")
            print(f"  - Grau medio: {np.mean(degrees):.2f}")
            print(f"  - Grau minimo: {min(degrees)}")
            print(f"  - Grau maximo: {max(degrees)}")

        print("=" * 60)

    def _calculate_centrality_metrics(self, G: nx.DiGraph) -> Dict:
        """Calcula métricas de centralidade."""
        # PageRank com pesos
        pagerank = nx.pagerank(G, weight='weight')
        
        # Centralidades
        in_degree_cent = nx.in_degree_centrality(G)
        out_degree_cent = nx.out_degree_centrality(G)
        betweenness_cent = nx.betweenness_centrality(G, weight='weight')
        closeness_cent = nx.closeness_centrality(G)
        eigenvector_cent = {}
        
        # Eigenvector centrality pode falhar em grafos direcionados
        try:
            eigenvector_cent = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
        except:
            eigenvector_cent = {node: 0 for node in G.nodes()}
        
        return {
            'pagerank': pagerank,
            'in_degree_centrality': in_degree_cent,
            'out_degree_centrality': out_degree_cent,
            'betweenness_centrality': betweenness_cent,
            'closeness_centrality': closeness_cent,
            'eigenvector_centrality': eigenvector_cent
        }
    
    def _calculate_community_metrics(self, G: nx.DiGraph) -> Dict:
        """Calcula métricas de comunidades usando Louvain."""
        # Converter para grafo não direcionado para detecção de comunidades
        G_undirected = G.to_undirected()
        
        # Aplicar algoritmo de Louvain
        communities = community_louvain.best_partition(G_undirected, weight='weight')
        modularity = community_louvain.modularity(communities, G_undirected, weight='weight')
        
        # Estatísticas das comunidades
        community_sizes = Counter(communities.values())
        num_communities = len(community_sizes)
        
        return {
            'communities': communities,
            'modularity': modularity,
            'num_communities': num_communities,
            'community_sizes': dict(community_sizes),
            'largest_community_size': max(community_sizes.values()),
            'smallest_community_size': min(community_sizes.values()),
            'avg_community_size': np.mean(list(community_sizes.values()))
        }
    
    def _calculate_node_metrics(self, G: nx.DiGraph) -> Dict:
        """Calcula métricas individuais dos nós."""
        node_metrics = {}
        
        for node in G.nodes():
            node_data = G.nodes[node]
            
            node_metrics[node] = {
                'in_degree': G.in_degree(node),
                'out_degree': G.out_degree(node),
                'weighted_in_degree': G.in_degree(node, weight='weight'),
                'weighted_out_degree': G.out_degree(node, weight='weight'),
                'total_degree': G.degree(node),
                'name': node_data.get('name', f'Athlete_{node}'),
                'sex': node_data.get('sex', 'Unknown'),
                'medal': node_data.get('medal', 'Unknown'),
                'team': node_data.get('team', 'Unknown'),
                'noc': node_data.get('noc', 'Unknown')
            }
        
        return node_metrics
    
    def analyze_edge_distribution(self, G: nx.DiGraph, network_name: str, output_dir: str) -> Dict:
        """Analisa a distribuição dos pesos das arestas."""
        weights = [data['weight'] for _, _, data in G.edges(data=True)]
        
        if not weights:
            return {'edge_count': 0, 'mean': 0, 'median': 0, 'max': 0, 'min': 0, 'std': 0}
        
        # Criar diretório para gráficos
        graphs_dir = os.path.join(output_dir, 'graphs')
        os.makedirs(graphs_dir, exist_ok=True)
        
        # Estatísticas básicas
        stats = {
            'edge_count': len(weights),
            'mean': np.mean(weights),
            'median': np.median(weights),
            'max': max(weights),
            'min': min(weights),
            'std': np.std(weights),
            'unique_weights': len(set(weights))
        }
        
        # Gerar visualizações
        self._plot_edge_distributions(weights, network_name, graphs_dir)
        
        return stats
    
    def _plot_edge_distributions(self, weights: List[float], network_name: str, output_dir: str):
        """Plota distribuições CDF e CCDF."""
        weight_counts = Counter(weights)
        unique_weights = sorted(weight_counts.keys())
        counts = [weight_counts[w] for w in unique_weights]
        
        # CDF e CCDF
        total = sum(counts)
        cdf = np.cumsum(counts) / total
        ccdf = 1 - cdf
        
        # Plot CDF
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        plt.plot(unique_weights, cdf, marker='o', linestyle='-', markersize=4)
        plt.title(f'CDF - {network_name}')
        plt.xlabel('Peso da Aresta')
        plt.ylabel('Probabilidade Acumulada')
        plt.grid(True, alpha=0.3)
        
        # Plot CCDF
        plt.subplot(1, 2, 2)
        plt.loglog(unique_weights, ccdf, marker='o', linestyle='-', markersize=4)
        plt.title(f'CCDF - {network_name}')
        plt.xlabel('Peso da Aresta')
        plt.ylabel('1 - Probabilidade Acumulada')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{network_name.lower().replace(" ", "_")}_distributions.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def export_edge_data(self, G: nx.DiGraph, network_type: str, sport: str, sex: str, output_dir: str, event_type_suffix: str = ''):
        """Exporta dados das arestas para análise CDF/CCDF."""
        edge_data = []
        
        for u, v, data in G.edges(data=True):
            edge_info = {
                'sport': sport,
                'sex': sex,
                'network_type': network_type,
                'source_id': u,
                'target_id': v,
                'weight': data['weight'],
                'source_name': G.nodes[u].get('name', f'Athlete_{u}'),
                'target_name': G.nodes[v].get('name', f'Athlete_{v}'),
                'source_medal': G.nodes[u].get('medal', 'Unknown'),
                'target_medal': G.nodes[v].get('medal', 'Unknown'),
                'source_team': G.nodes[u].get('team', 'Unknown'),
                'target_team': G.nodes[v].get('team', 'Unknown')
            }
            edge_data.append(edge_info)
        
        if edge_data:
            df_edges = pd.DataFrame(edge_data)
            suffix = f'{event_type_suffix}_' if event_type_suffix else ''
            edge_file = os.path.join(output_dir, f'{sport.lower()}_{sex}_{suffix}{network_type}_edges.csv')
            df_edges.to_csv(edge_file, index=False)
            return df_edges
        
        return pd.DataFrame()

    def export_detailed_results(self, sport: str, sex: str, G_original: nx.DiGraph,
                              output_dir: str, event_type_suffix: str = ''):
        """Exporta resultados detalhados para CSV."""
        suffix_info = f" ({event_type_suffix})" if event_type_suffix else ""
        print(f"Exportando resultados detalhados para {sport} {sex}{suffix_info}...")

        # Exportar dados das arestas
        original_edges = self.export_edge_data(G_original, 'original', sport, sex, output_dir, event_type_suffix)

        # Calcular métricas da rede
        original_metrics = self.calculate_network_metrics(G_original)
        
        # Criar DataFrame com métricas dos nós
        node_data = []
        
        for node in G_original.nodes():
            row = {
                'athlete_id': node,
                'sport': sport,
                'sex': sex,
            }
            
            # Dados básicos do atleta
            node_attrs = G_original.nodes[node]
            row.update({
                'name': node_attrs.get('name', f'Athlete_{node}'),
                'age': node_attrs.get('age', 0),
                'height': node_attrs.get('height', 0),
                'weight_kg': node_attrs.get('weight', 0),
                'team': node_attrs.get('team', ''),
                'noc': node_attrs.get('noc', ''),
                'medal': node_attrs.get('medal', ''),
                'games': node_attrs.get('games', ''),
                'city': node_attrs.get('city', ''),
                # Contagem de medalhas agregadas
                'gold_medals': node_attrs.get('gold_medals', 0),
                'silver_medals': node_attrs.get('silver_medals', 0),
                'bronze_medals': node_attrs.get('bronze_medals', 0),
                'total_medals': node_attrs.get('total_medals', 0)
            })
            
            # Métricas da rede original
            orig_node_metrics = original_metrics['node_metrics'][node]
            row.update({
                'original_in_degree': orig_node_metrics['in_degree'],
                'original_out_degree': orig_node_metrics['out_degree'],
                'original_weighted_in_degree': orig_node_metrics['weighted_in_degree'],
                'original_weighted_out_degree': orig_node_metrics['weighted_out_degree'],
                'original_total_degree': orig_node_metrics['total_degree']
            })
            
            # Métricas de centralidade - rede original
            row.update({
                'original_pagerank': original_metrics['centrality_metrics']['pagerank'].get(node, 0),
                'original_in_degree_centrality': original_metrics['centrality_metrics']['in_degree_centrality'].get(node, 0),
                'original_out_degree_centrality': original_metrics['centrality_metrics']['out_degree_centrality'].get(node, 0),
                'original_betweenness_centrality': original_metrics['centrality_metrics']['betweenness_centrality'].get(node, 0),
                'original_closeness_centrality': original_metrics['centrality_metrics']['closeness_centrality'].get(node, 0),
                'original_eigenvector_centrality': original_metrics['centrality_metrics']['eigenvector_centrality'].get(node, 0)
            })
            
            # Comunidade - rede original
            row['original_community'] = original_metrics['community_metrics']['communities'].get(node, -1)

            node_data.append(row)
        
        # Salvar DataFrame
        df_results = pd.DataFrame(node_data)
        suffix = f'{event_type_suffix}_' if event_type_suffix else ''
        csv_path = os.path.join(output_dir, f'{sport.lower()}_{sex}_{suffix}detailed_metrics.csv')
        df_results.to_csv(csv_path, index=False)
        
        # Salvar métricas da rede
        network_summary = {
            'sport': sport,
            'sex': sex,
            'original_network': original_metrics['basic_metrics'],
            'original_community': {
                'modularity': original_metrics['community_metrics']['modularity'],
                'num_communities': original_metrics['community_metrics']['num_communities'],
                'avg_community_size': original_metrics['community_metrics']['avg_community_size']
            }
        }
        
        # Salvar resumo da rede
        suffix = f'{event_type_suffix}_' if event_type_suffix else ''
        with open(os.path.join(output_dir, f'{sport.lower()}_{sex}_{suffix}network_summary.json'), 'w') as f:
            json.dump(network_summary, f, indent=4, default=str)
        
        return df_results, network_summary
    
    def run_complete_analysis(self):
        """Executa a análise completa."""
        print("Iniciando análise completa das redes esportivas...")
        
        # Carregar dados
        self.load_and_filter_data()
        
        all_results = []
        all_summaries = []
        
        for sport in self.selected_sports:
            print(f"\nAnalisando {sport}...")
            sport_df = self.df[self.df['Sport'] == sport]
            sport_dir = os.path.join(self.base_dir, sport.lower())
            os.makedirs(sport_dir, exist_ok=True)
            
            # Verificar tipo do esporte
            sport_type = 'mixed'  # default
            individual_events = []
            team_events = []
            
            if self.sport_types and sport in self.sport_types:
                sport_info = self.sport_types[sport]
                sport_type = sport_info['type']
                individual_events = sport_info.get('individual_events', [])
                team_events = sport_info.get('team_events', [])
                print(f"  Tipo do esporte: {sport_type}")
                
                if sport_type == 'mixed':
                    print(f"    Eventos individuais: {len(individual_events)}")
                    print(f"    Eventos coletivos: {len(team_events)}")
            
            for sex in ['M', 'F']:
                sex_data = sport_df[sport_df['Sex'] == sex]
                
                if len(sex_data) == 0:
                    print(f"Sem dados para {sport} {sex}")
                    continue
                
                print(f"  Processando {sport} {sex} - {len(sex_data)} registros")
                
                # Processar baseado no tipo do esporte
                if sport_type == 'individual_only':
                    # Apenas eventos individuais
                    networks_to_process = [('individual', sex_data, individual_events)]
                elif sport_type == 'team_only':
                    # Apenas eventos coletivos
                    networks_to_process = [('team', sex_data, team_events)]
                elif sport_type == 'mixed':
                    # Criar duas redes: uma para eventos individuais, outra para coletivos
                    individual_data = sex_data[sex_data['Event'].isin(individual_events)] if individual_events else pd.DataFrame()
                    team_data = sex_data[sex_data['Event'].isin(team_events)] if team_events else pd.DataFrame()
                    
                    networks_to_process = []
                    if len(individual_data) > 0:
                        networks_to_process.append(('individual', individual_data, individual_events))
                    if len(team_data) > 0:
                        networks_to_process.append(('team', team_data, team_events))
                else:
                    # Fallback para análise padrão
                    networks_to_process = [('combined', sex_data, None)]
                
                # Processar cada rede
                for network_type, data, event_filter in networks_to_process:
                    if len(data) == 0:
                        continue
                    
                    suffix = f"_{network_type}" if network_type in ['individual', 'team'] else ""
                    print(f"    Criando rede {network_type}: {len(data)} registros")
                
                    # Criar rede original
                    G_original = self.create_athlete_network(data, event_filter)

                    # DIAGNOSTICO: Verificar integridade da rede
                    self.diagnose_network_integrity(G_original, f"{sport} {sex} {network_type}")

                    # Salvar rede original
                    original_file = os.path.join(sport_dir, f'{sport.lower()}_original_{sex}{suffix}.gexf')
                    nx.write_gexf(G_original, original_file)
                    
                    # Analisar distribuição de arestas da rede original
                    original_edge_stats = self.analyze_edge_distribution(
                        G_original, f'{sport} Original {sex} {network_type}', sport_dir
                    )

                    # Exportar resultados detalhados
                    event_suffix = network_type if network_type in ['individual', 'team'] else ''
                    df_results, network_summary = self.export_detailed_results(
                        sport, sex, G_original, sport_dir, event_suffix
                    )
                    
                    # Adicionar informações sobre tipo de evento aos resultados
                    if not df_results.empty:
                        df_results['event_type'] = network_type
                        df_results['sport_classification'] = sport_type
                    
                    all_results.append(df_results)
                    network_summary['event_type'] = network_type
                    network_summary['sport_classification'] = sport_type
                    all_summaries.append(network_summary)
        
        # Consolidar todos os resultados
        if all_results:
            consolidated_results = pd.concat(all_results, ignore_index=True)
            consolidated_results.to_csv(
                os.path.join(self.base_dir, 'consolidated_sports_network_analysis.csv'), 
                index=False
            )
            
            print(f"\nAnálise concluída! Resultados consolidados salvos em:")
            print(f"  - {os.path.join(self.base_dir, 'consolidated_sports_network_analysis.csv')}")
        
        # Consolidar dados das arestas
        edge_files = []
        for sport in self.selected_sports:
            sport_dir = os.path.join(self.base_dir, sport.lower())
            for file in os.listdir(sport_dir):
                if file.endswith('_edges.csv'):
                    edge_files.append(os.path.join(sport_dir, file))
        
        if edge_files:
            all_edges = []
            for file_path in edge_files:
                if os.path.exists(file_path):
                    edge_df = pd.read_csv(file_path)
                    all_edges.append(edge_df)
            
            if all_edges:
                consolidated_edges = pd.concat(all_edges, ignore_index=True)
                consolidated_edges.to_csv(
                    os.path.join(self.base_dir, 'consolidated_edges_data.csv'),
                    index=False
                )
                print(f"  - {os.path.join(self.base_dir, 'consolidated_edges_data.csv')}")
        
        # Salvar resumos consolidados
        with open(os.path.join(self.base_dir, 'all_network_summaries.json'), 'w') as f:
            json.dump(all_summaries, f, indent=4, default=str)
        
        print(f"  - {os.path.join(self.base_dir, 'all_network_summaries.json')}")

        # Gerar rede híbrida para Swimming (agregar individual + team)
        self._create_hybrid_swimming_network()

        print(f"\nTodos os arquivos foram salvos no diretório: {self.base_dir}")

        return consolidated_results, all_summaries

    def _create_hybrid_swimming_network(self):
        """Cria rede híbrida para Swimming agregando individual + team por atleta."""
        print("\nGerando rede híbrida para Swimming...")

        # Usar dados originais RAW, não os resultados processados
        if self.df is None:
            print("Erro: dados não carregados")
            return

        # Filtrar apenas dados de Swimming do dataset original
        swimming_data = self.df[self.df['Sport'] == 'Swimming'].copy()
        swimming_data = swimming_data[swimming_data['Medal'].notna()].copy()  # Apenas medalhistas

        if len(swimming_data) == 0:
            return

        print(f"Dados Swimming encontrados: {len(swimming_data)} registros")

        # Separar eventos individuais vs team
        def is_team_event(event_name):
            return ('Relay' in event_name) or ('Team Swimming' in event_name)

        # Classificar eventos
        swimming_data['event_type'] = swimming_data['Event'].apply(
            lambda x: 'team' if is_team_event(x) else 'individual'
        )

        # Criar uma rede unificada com TODOS os atletas (individual + team)
        G_hybrid = self.create_athlete_network(swimming_data, event_filter=None)

        print(f"Rede híbrida criada: {G_hybrid.number_of_nodes()} nós, {G_hybrid.number_of_edges()} arestas")

        # Calcular métricas da rede híbrida
        metrics_original = self.calculate_network_metrics(G_hybrid)

        # Criar DataFrame final com estrutura idêntica ao consolidated
        athlete_data = []

        for name in G_hybrid.nodes():
            node_data = G_hybrid.nodes[name]

            # Determinar athlete_id (usar primeiro registro encontrado)
            athlete_records = swimming_data[swimming_data['Name'] == name]
            if len(athlete_records) > 0:
                first_record = athlete_records.iloc[0]
                athlete_id = first_record['ID']
            else:
                athlete_id = 0

            # Dados básicos seguindo exatamente a estrutura do consolidated
            athlete_record = {
                'athlete_id': athlete_id,
                'sport': 'Swimming',
                'sex': node_data.get('sex', ''),
                'name': name,
                'age': node_data.get('age', ''),
                'height': node_data.get('height', ''),
                'weight_kg': node_data.get('weight', ''),
                'team': node_data.get('team', ''),
                'noc': node_data.get('noc', ''),
                'medal': node_data.get('medal', ''),
                'games': node_data.get('games', ''),
                'city': node_data.get('city', '')
            }

            # Métricas originais (seguindo ordem exata do consolidated)
            athlete_record['original_in_degree'] = metrics_original.get('in_degree', {}).get(name, 0)
            athlete_record['original_out_degree'] = metrics_original.get('out_degree', {}).get(name, 0)
            athlete_record['original_weighted_in_degree'] = metrics_original.get('weighted_in_degree', {}).get(name, 0)
            athlete_record['original_weighted_out_degree'] = metrics_original.get('weighted_out_degree', {}).get(name, 0)
            athlete_record['original_total_degree'] = metrics_original.get('total_degree', {}).get(name, 0)
            athlete_record['original_pagerank'] = metrics_original.get('pagerank', {}).get(name, 0)
            athlete_record['original_in_degree_centrality'] = metrics_original.get('in_degree_centrality', {}).get(name, 0)
            athlete_record['original_out_degree_centrality'] = metrics_original.get('out_degree_centrality', {}).get(name, 0)
            athlete_record['original_betweenness_centrality'] = metrics_original.get('betweenness_centrality', {}).get(name, 0)
            athlete_record['original_closeness_centrality'] = metrics_original.get('closeness_centrality', {}).get(name, 0)
            athlete_record['original_eigenvector_centrality'] = metrics_original.get('eigenvector_centrality', {}).get(name, 0)
            athlete_record['original_community'] = metrics_original.get('community', {}).get(name, 0)

            # Determinar tipos de evento que o atleta participou
            athlete_events = swimming_data[swimming_data['Name'] == name]['Event'].unique()
            event_types = [('team' if is_team_event(e) else 'individual') for e in athlete_events]
            athlete_record['event_type'] = '+'.join(sorted(set(event_types)))
            athlete_record['sport_classification'] = 'mixed'

            athlete_data.append(athlete_record)

        hybrid_swimming = pd.DataFrame(athlete_data)

        # Salvar rede híbrida
        hybrid_file = os.path.join(self.base_dir, 'swimming_hybrid_network.csv')
        hybrid_swimming.to_csv(hybrid_file, index=False)

        print(f"Rede híbrida Swimming salva: {os.path.basename(hybrid_file)}")


# Exemplo de uso
if __name__ == "__main__":
    # Configurar análise
    analyzer = SportsNetworkAnalyzer(
        data_path='../../data/athlete_events.csv',
        selected_sports=['Swimming', 'Basketball', 'Football', 'Athletics', 'Judo', 'Boxing'],
        base_dir='../../results'
    )
    
    # Executar análise completa
    results_df, summaries = analyzer.run_complete_analysis()
    
    # Exibir estatísticas básicas
    print("\n" + "="*60)
    print("RESUMO DA ANÁLISE")
    print("="*60)
    print(f"Total de atletas analisados: {len(results_df)}")
    print(f"Esportes: {results_df['sport'].unique()}")
    print(f"Distribuição por sexo: {results_df['sex'].value_counts().to_dict()}")
    print("\nTop 10 atletas por PageRank (rede original):")
    top_pagerank = results_df.nlargest(10, 'original_pagerank')[['name', 'sport', 'sex', 'medal', 'original_pagerank']]
    print(top_pagerank.to_string(index=False))