#!/usr/bin/env python3
"""
MINERAÇÃO UNIVERSAL DE TODAS AS REDES OLÍMPICAS

Processa TODOS os arquivos GEXF disponíveis e gera dados consolidados
para alimentar o dashboard com a modelagem per-event completa.

Critérios de rede válida:
- Mínimo 10 atletas
- Mínimo 10 arestas
- Arquivo GEXF bem formado

Outputs:
- consolidated_all_networks.csv (dados de atletas de todas as redes)
- network_metadata.csv (metadata de cada rede)
- communities_all_networks.csv (dados de comunidades)
- consolidated_all_edges.csv (arestas de todas as redes)
- mining_log.txt (log de processamento)

Autor: Pipeline automatizado
Data: 2026-02-05
"""

import sys
from pathlib import Path
import pandas as pd
import networkx as nx
import community as community_louvain
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Adicionar src ao path
SCRIPT_DIR = Path(__file__).parent
SRC_ROOT = SCRIPT_DIR.parent
MAIN_ROOT = SRC_ROOT.parent
sys.path.insert(0, str(SRC_ROOT))

from core.config.paths import PATHS


class UniversalNetworkMiner:
    """Minera TODAS as redes GEXF disponíveis."""

    def __init__(self,
                 gexf_dir: Path,
                 output_dir: Path,
                 min_athletes: int = 10,
                 min_edges: int = 10):
        """
        Inicializa minerador universal.

        Args:
            gexf_dir: Diretório contendo subdiretorios de esportes com GEXFs
            output_dir: Diretório para salvar resultados
            min_athletes: Mínimo de nós para rede válida
            min_edges: Mínimo de arestas para rede válida
        """
        self.gexf_dir = Path(gexf_dir)
        self.output_dir = Path(output_dir)
        self.min_athletes = min_athletes
        self.min_edges = min_edges

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Logs
        self.log_file = self.output_dir / 'mining_log.txt'
        self.errors = []
        self.processed = []

        self.log(f"Inicializado UniversalNetworkMiner")
        self.log(f"  GEXF dir: {self.gexf_dir}")
        self.log(f"  Output dir: {self.output_dir}")
        self.log(f"  Critérios: >= {min_athletes} atletas, >= {min_edges} arestas")

    def log(self, message: str):
        """Adiciona mensagem ao log e imprime."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')

    def discover_networks(self):
        """
        Varre pasta results/ e identifica todas as redes válidas.

        Returns:
            List of dicts com metadata de cada GEXF encontrado
        """
        self.log("\n" + "="*80)
        self.log("FASE 1: DESCOBRINDO REDES DISPONÍVEIS")
        self.log("="*80)

        # Padrão: results/{sport}/{sport}_{gender}_{event_name}.gexf
        gexf_files = list(self.gexf_dir.rglob("*.gexf"))

        self.log(f"\nEncontrados {len(gexf_files)} arquivos GEXF")

        networks = []

        for gexf_path in sorted(gexf_files):
            # Extrair informações do caminho
            # Ex: results/swimming/swimming_M_Swimming_Mens_100m_Freestyle.gexf

            sport_dir = gexf_path.parent.name  # swimming
            filename = gexf_path.stem  # swimming_M_Swimming_Mens_100m_Freestyle

            # Parse do nome do arquivo
            parts = filename.split('_', 2)  # Divide em no máximo 3 partes

            if len(parts) < 3:
                self.log(f"⚠️  SKIP: Formato inválido: {filename}")
                continue

            sport = parts[0]  # swimming
            gender = parts[1]  # M
            event_name = parts[2]  # Swimming_Mens_100m_Freestyle

            networks.append({
                'file_path': gexf_path,
                'sport': sport,
                'gender': gender,
                'event_name': event_name,
                'filename': filename
            })

        self.log(f"\n✅ {len(networks)} redes identificadas")

        # Resumo por esporte
        sports_count = {}
        for net in networks:
            sport = net['sport']
            sports_count[sport] = sports_count.get(sport, 0) + 1

        self.log("\nDistribuição por esporte:")
        for sport, count in sorted(sports_count.items()):
            self.log(f"  {sport}: {count} redes")

        return networks

    def validate_network(self, G: nx.Graph, net_info: dict) -> tuple:
        """
        Valida se rede atende critérios mínimos.

        Returns:
            (is_valid, reason)
        """
        n_nodes = G.number_of_nodes()
        n_edges = G.number_of_edges()

        if n_nodes < self.min_athletes:
            return False, f"Poucos nós ({n_nodes} < {self.min_athletes})"

        if n_edges < self.min_edges:
            return False, f"Poucas arestas ({n_edges} < {self.min_edges})"

        return True, "OK"

    def mine_network(self, net_info: dict, network_id: int):
        """
        Minera UMA rede: calcula todas as métricas.

        Args:
            net_info: Dict com informações da rede
            network_id: ID único da rede

        Returns:
            Dict com:
                - athletes: DataFrame com métricas de atletas
                - metadata: Dict com metadata da rede
                - communities: DataFrame com dados de comunidades
        """
        gexf_path = net_info['file_path']

        try:
            # Carregar GEXF
            G = nx.read_gexf(str(gexf_path))

            # Validar
            is_valid, reason = self.validate_network(G, net_info)
            if not is_valid:
                self.log(f"  ⏭️  SKIP: {reason}")
                return None

            # Converter para grafo não direcionado para algumas métricas
            G_undirected = G.to_undirected()

            # === MÉTRICAS DE REDE ===

            # PageRank
            try:
                pagerank = nx.pagerank(G, alpha=0.85, max_iter=100)
            except:
                pagerank = {node: 0.0 for node in G.nodes()}

            # Betweenness
            try:
                betweenness = nx.betweenness_centrality(G_undirected)
            except:
                betweenness = {node: 0.0 for node in G.nodes()}

            # Degree
            degree = dict(G_undirected.degree())

            # Comunidades (Louvain em rede não direcionada)
            try:
                communities = community_louvain.best_partition(G_undirected)
            except:
                # Se falhar, comunidade única
                communities = {node: 0 for node in G.nodes()}

            # === CONSTRUIR DATAFRAME DE ATLETAS ===

            athletes_data = []

            for node in G.nodes():
                node_data = G.nodes[node]

                athletes_data.append({
                    'network_id': network_id,
                    'sport': net_info['sport'],
                    'gender': net_info['gender'],
                    'event_name': net_info['event_name'],
                    'athlete_name': node_data.get('label', node),
                    'noc': node_data.get('noc', 'UNK'),
                    'year': node_data.get('year', 0),
                    'pagerank': pagerank.get(node, 0.0),
                    'betweenness': betweenness.get(node, 0.0),
                    'degree': degree.get(node, 0),
                    'community': communities.get(node, 0),
                    'gold': int(node_data.get('gold', 0)),
                    'silver': int(node_data.get('silver', 0)),
                    'bronze': int(node_data.get('bronze', 0)),
                    'total_medals': int(node_data.get('total', 0))
                })

            df_athletes = pd.DataFrame(athletes_data)

            # === EXTRAIR ARESTAS ===

            edges_data = []
            for source, target, data in G.edges(data=True):
                source_node = G.nodes[source]
                target_node = G.nodes[target]

                edges_data.append({
                    'network_id': network_id,
                    'sport': net_info['sport'],
                    'gender': net_info['gender'],
                    'event_name': net_info['event_name'],
                    'source_name': source_node.get('label', source),
                    'target_name': target_node.get('label', target),
                    'source_noc': source_node.get('noc', 'UNK'),
                    'target_noc': target_node.get('noc', 'UNK'),
                    'weight': data.get('weight', 1.0)
                })

            df_edges = pd.DataFrame(edges_data)

            # === METADATA DA REDE ===

            n_communities = df_athletes['community'].nunique()

            # Densidade
            n_nodes = G.number_of_nodes()
            n_edges = G.number_of_edges()
            max_edges = n_nodes * (n_nodes - 1)
            density = (2 * n_edges / max_edges) if max_edges > 0 else 0.0

            # Modularidade
            try:
                modularity = community_louvain.modularity(communities, G_undirected)
            except:
                modularity = 0.0

            metadata = {
                'network_id': network_id,
                'sport': net_info['sport'],
                'gender': net_info['gender'],
                'event_name': net_info['event_name'],
                'filename': net_info['filename'],
                'n_athletes': n_nodes,
                'n_edges': n_edges,
                'density': density,
                'n_communities': n_communities,
                'modularity': modularity,
                'min_year': int(df_athletes['year'].min()) if df_athletes['year'].max() > 0 else 0,
                'max_year': int(df_athletes['year'].max()) if df_athletes['year'].max() > 0 else 0,
                'total_medals': int(df_athletes['total_medals'].sum())
            }

            # === DADOS DE COMUNIDADES ===

            community_stats = df_athletes.groupby('community').agg({
                'athlete_name': 'count',
                'pagerank': 'mean',
                'total_medals': 'sum',
                'noc': lambda x: x.nunique()
            }).reset_index()

            community_stats.columns = ['community', 'size', 'avg_pagerank', 'total_medals', 'n_nocs']
            community_stats['network_id'] = network_id

            self.log(f"  ✅ OK: {n_nodes} atletas, {n_edges} arestas, {n_communities} comunidades")

            return {
                'athletes': df_athletes,
                'metadata': metadata,
                'communities': community_stats,
                'edges': df_edges
            }

        except Exception as e:
            error_msg = f"Erro ao processar {gexf_path.name}: {str(e)}"
            self.log(f"  ❌ ERRO: {error_msg}")
            self.errors.append(error_msg)
            return None

    def mine_all(self):
        """
        Loop principal: minera todas as redes descobertas.

        Gera arquivos CSV consolidados.
        """
        self.log("\n" + "="*80)
        self.log("FASE 2: MINERANDO TODAS AS REDES")
        self.log("="*80)

        # Descobrir redes
        networks = self.discover_networks()

        if not networks:
            self.log("\n❌ Nenhuma rede encontrada!")
            return

        # Listas para acumular resultados
        all_athletes = []
        all_metadata = []
        all_communities = []
        all_edges = []

        network_id = 1
        valid_count = 0

        self.log(f"\nProcessando {len(networks)} redes...")
        self.log("-" * 80)

        for i, net_info in enumerate(networks, 1):
            self.log(f"\n[{i}/{len(networks)}] {net_info['sport']} - {net_info['gender']} - {net_info['event_name']}")

            result = self.mine_network(net_info, network_id)

            if result:
                all_athletes.append(result['athletes'])
                all_metadata.append(result['metadata'])
                all_communities.append(result['communities'])
                all_edges.append(result['edges'])

                self.processed.append(net_info['filename'])
                valid_count += 1
                network_id += 1

        self.log("\n" + "="*80)
        self.log("FASE 3: CONSOLIDANDO RESULTADOS")
        self.log("="*80)

        if not all_athletes:
            self.log("\n❌ Nenhuma rede válida processada!")
            return

        # Consolidar DataFrames
        self.log(f"\nConsolidando {valid_count} redes válidas...")

        df_athletes_all = pd.concat(all_athletes, ignore_index=True)
        df_metadata_all = pd.DataFrame(all_metadata)
        df_communities_all = pd.concat(all_communities, ignore_index=True)
        df_edges_all = pd.concat(all_edges, ignore_index=True)

        # Salvar CSVs
        athletes_path = self.output_dir / 'consolidated_all_networks.csv'
        metadata_path = self.output_dir / 'network_metadata.csv'
        communities_path = self.output_dir / 'communities_all_networks.csv'
        edges_path = self.output_dir / 'consolidated_all_edges.csv'

        self.log("\nSalvando arquivos...")

        df_athletes_all.to_csv(athletes_path, index=False)
        self.log(f"  ✅ {athletes_path.name}: {len(df_athletes_all)} atletas")

        df_metadata_all.to_csv(metadata_path, index=False)
        self.log(f"  ✅ {metadata_path.name}: {len(df_metadata_all)} redes")

        df_communities_all.to_csv(communities_path, index=False)
        self.log(f"  ✅ {communities_path.name}: {len(df_communities_all)} comunidades")

        df_edges_all.to_csv(edges_path, index=False)
        self.log(f"  ✅ {edges_path.name}: {len(df_edges_all)} arestas")

        # === ESTATÍSTICAS FINAIS ===

        self.log("\n" + "="*80)
        self.log("ESTATÍSTICAS FINAIS")
        self.log("="*80)

        self.log(f"\n📊 Processamento:")
        self.log(f"  Total de GEXFs encontrados: {len(networks)}")
        self.log(f"  Redes válidas processadas: {valid_count}")
        self.log(f"  Redes rejeitadas: {len(networks) - valid_count}")
        self.log(f"  Erros: {len(self.errors)}")

        self.log(f"\n📊 Dados gerados:")
        self.log(f"  Total de atletas: {len(df_athletes_all)}")
        self.log(f"  Total de redes: {df_metadata_all['network_id'].nunique()}")
        self.log(f"  Total de comunidades: {len(df_communities_all)}")

        self.log(f"\n📊 Por esporte:")
        sport_summary = df_metadata_all.groupby('sport').agg({
            'network_id': 'count',
            'n_athletes': 'sum'
        }).reset_index()
        sport_summary.columns = ['sport', 'n_networks', 'total_athletes']

        for _, row in sport_summary.iterrows():
            self.log(f"  {row['sport']}: {row['n_networks']} redes, {row['total_athletes']} atletas")

        self.log(f"\n📊 Por gênero:")
        gender_summary = df_metadata_all.groupby('gender').agg({
            'network_id': 'count',
            'n_athletes': 'sum'
        }).reset_index()
        gender_summary.columns = ['gender', 'n_networks', 'total_athletes']

        for _, row in gender_summary.iterrows():
            self.log(f"  {row['gender']}: {row['n_networks']} redes, {row['total_athletes']} atletas")

        if self.errors:
            self.log(f"\n⚠️  Erros encontrados ({len(self.errors)}):")
            for error in self.errors[:10]:  # Mostrar até 10 erros
                self.log(f"  - {error}")
            if len(self.errors) > 10:
                self.log(f"  ... e mais {len(self.errors) - 10} erros (ver log completo)")

        self.log("\n" + "="*80)
        self.log("✅ MINERAÇÃO COMPLETA!")
        self.log("="*80)
        self.log(f"\nArquivos gerados em: {self.output_dir}")
        self.log(f"Log completo em: {self.log_file}")


def main():
    """Executa mineração completa."""
    print("\n" + "="*80)
    print("MINERAÇÃO UNIVERSAL DE REDES OLÍMPICAS")
    print("="*80)

    # Configuração
    GEXF_DIR = MAIN_ROOT / 'results'
    OUTPUT_DIR = MAIN_ROOT / 'results_all_mining'

    print(f"\nDiretório de entrada: {GEXF_DIR}")
    print(f"Diretório de saída: {OUTPUT_DIR}")

    if not GEXF_DIR.exists():
        print(f"\n❌ ERRO: Diretório {GEXF_DIR} não existe!")
        return

    # Criar minerador
    miner = UniversalNetworkMiner(
        gexf_dir=GEXF_DIR,
        output_dir=OUTPUT_DIR,
        min_athletes=10,
        min_edges=10
    )

    # Executar mineração
    miner.mine_all()

    print("\n✅ Processo finalizado!")
    print(f"Veja os resultados em: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
