#!/usr/bin/env python3
"""
Versão modificada: Gera UMA REDE para CADA EVENTO específico.

MUDANÇA CHAVE:
- Ao invés de agrupar todos os eventos individuais em uma única rede fragmentada,
- Cria redes separadas: "Swimming M 100m Free", "Swimming M 200m Butterfly", etc.

VANTAGEM:
- Cada rede é conectada (sem fragmentação interna)
- Análise de comunidades (Louvain) faz sentido dentro de cada evento
- Métricas de centralidade são interpretáveis

DESVANTAGEM:
- Centenas de redes pequenas ao invés de poucas redes grandes
- Não captura rivalidades cross-event (atletas versáteis)
"""

import pandas as pd
import networkx as nx
import numpy as np
import os
import json
import warnings
from collections import Counter
from pathlib import Path
import sys

# Importar a classe base do script original
sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module

# Configurações
warnings.filterwarnings('ignore')

class SportsNetworkAnalyzerPerEvent:
    """
    Gera uma rede separada para cada evento olímpico.
    """

    def __init__(self, data_path: str, selected_sports: list, base_dir: str = 'results'):
        self.data_path = data_path
        self.selected_sports = selected_sports
        self.base_dir = base_dir
        self.df = None

        os.makedirs(self.base_dir, exist_ok=True)

    def load_and_filter_data(self):
        """Carrega e filtra os dados."""
        print("Carregando dados...")
        self.df = pd.read_csv(self.data_path)

        total_records = len(self.df)
        print(f"Total de registros: {total_records:,}")

        # Filtrar apenas esportes selecionados e medalhistas
        self.df = self.df[
            (self.df['Sport'].isin(self.selected_sports)) &
            self.df['Medal'].notna()
        ]

        print(f"Medalhistas dos esportes selecionados: {len(self.df):,}")

        # Remover duplicatas
        duplicates_before = self.df.duplicated(subset=['Year', 'Sport', 'Event', 'Sex', 'Medal', 'ID']).sum()
        if duplicates_before > 0:
            print(f"[LIMPEZA] Removendo {duplicates_before} registros duplicados...")
            self.df = self.df.drop_duplicates(subset=['Year', 'Sport', 'Event', 'Sex', 'Medal', 'ID'])

        print(f"\n[OK] Dados limpos: {len(self.df):,} registros de {self.df['ID'].nunique():,} atletas")

        return self.df

    def create_athlete_network(self, event_data: pd.DataFrame) -> nx.DiGraph:
        """Cria rede para um evento específico."""
        G = nx.DiGraph()

        # Agregar dados por atleta
        athlete_aggregated = event_data.groupby('ID').agg({
            'Name': 'first',
            'Sex': 'first',
            'Age': lambda x: x.dropna().iloc[-1] if len(x.dropna()) > 0 else 0,
            'Height': lambda x: x.dropna().iloc[-1] if len(x.dropna()) > 0 else 0,
            'Weight': lambda x: x.dropna().iloc[-1] if len(x.dropna()) > 0 else 0,
            'Team': 'first',
            'NOC': 'first',
            'Games': 'last',
            'City': 'last',
            'Medal': lambda x: {
                'Gold': (x == 'Gold').sum(),
                'Silver': (x == 'Silver').sum(),
                'Bronze': (x == 'Bronze').sum(),
                'last_medal': x.iloc[-1]
            }
        }).reset_index()

        # Adicionar nós
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
                "medal": medal_counts['last_medal'],
                "gold_medals": medal_counts['Gold'],
                "silver_medals": medal_counts['Silver'],
                "bronze_medals": medal_counts['Bronze'],
                "total_medals": medal_counts['Gold'] + medal_counts['Silver'] + medal_counts['Bronze']
            }
            G.add_node(row['ID'], **athlete_info)

        # Adicionar arestas (agrupamento por Year + Event já foi feito antes de chamar esta função)
        for (year, event), event_group in event_data.groupby(['Year', 'Event']):
            self._add_competition_edges(G, event_group)

        # Remover nós isolados
        isolated_nodes = [node for node in G.nodes() if G.degree(node) == 0]
        if isolated_nodes:
            G.remove_nodes_from(isolated_nodes)

        return G

    def _add_competition_edges(self, G: nx.DiGraph, event_group: pd.DataFrame):
        """Adiciona arestas entre medalhistas de um pódio."""
        unique_athletes = event_group['ID'].nunique()
        if unique_athletes < 2:
            return

        medalists = event_group[['ID', 'Medal']].sort_values(
            by='Medal', key=lambda x: x.map({'Gold': 1, 'Silver': 2, 'Bronze': 3})
        ).values

        # Verificar se é evento de equipe
        medal_counts = event_group.groupby('Medal')['ID'].nunique()
        is_team_event = any(count > 1 for count in medal_counts.values)

        # Pesos
        if is_team_event:
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

        # Criar arestas
        for i, (loser_id, loser_medal) in enumerate(medalists):
            for winner_id, winner_medal in medalists[:i]:
                if loser_id == winner_id:
                    continue

                if loser_medal != winner_medal:
                    weight = weight_map.get((winner_medal, loser_medal), 1)

                    if G.has_edge(loser_id, winner_id):
                        G[loser_id][winner_id]['weight'] += weight
                    else:
                        G.add_edge(loser_id, winner_id, weight=weight)

    def run_analysis_per_event(self):
        """Executa análise gerando UMA rede por evento."""
        print("\n" + "="*80)
        print("GERAÇÃO DE REDES POR EVENTO")
        print("="*80)

        self.load_and_filter_data()

        summary_stats = []

        for sport in self.selected_sports:
            print(f"\n{'='*80}")
            print(f"Processando {sport}...")
            print("="*80)

            sport_df = self.df[self.df['Sport'] == sport]
            sport_dir = os.path.join(self.base_dir, sport.lower())
            os.makedirs(sport_dir, exist_ok=True)

            for sex in ['M', 'F']:
                sex_data = sport_df[sport_df['Sex'] == sex]

                if len(sex_data) == 0:
                    continue

                # Obter eventos únicos para esse esporte/sexo
                unique_events = sex_data['Event'].unique()
                print(f"\n{sport} {sex}: {len(unique_events)} eventos únicos")

                for event in sorted(unique_events):
                    event_data = sex_data[sex_data['Event'] == event]

                    # Verificar se tem atletas suficientes
                    num_athletes = event_data['ID'].nunique()
                    if num_athletes < 2:
                        print(f"  [SKIP] {event}: apenas {num_athletes} atleta(s)")
                        continue

                    # Criar rede para este evento
                    G = self.create_athlete_network(event_data)

                    if G.number_of_nodes() < 2:
                        print(f"  [SKIP] {event}: rede com < 2 nós")
                        continue

                    # Nome do arquivo (limpar caracteres especiais)
                    safe_event_name = event.replace(' ', '_').replace(',', '').replace('/', '_')
                    safe_event_name = ''.join(c for c in safe_event_name if c.isalnum() or c in '_-.')

                    file_name = f"{sport.lower()}_{sex}_{safe_event_name}.gexf"
                    file_path = os.path.join(sport_dir, file_name)

                    # Salvar rede
                    nx.write_gexf(G, file_path)

                    # Estatísticas
                    num_components = nx.number_weakly_connected_components(G)

                    stats = {
                        'sport': sport,
                        'sex': sex,
                        'event': event,
                        'file': file_name,
                        'nodes': G.number_of_nodes(),
                        'edges': G.number_of_edges(),
                        'components': num_components,
                        'connected': num_components == 1
                    }
                    summary_stats.append(stats)

                    status = "✓ CONECTADA" if num_components == 1 else f"⚠️  {num_components} componentes"
                    print(f"  {event[:60]:<60} → {G.number_of_nodes():>4} nós, {G.number_of_edges():>5} arestas [{status}]")

        # Salvar resumo
        df_summary = pd.DataFrame(summary_stats)
        summary_path = os.path.join(self.base_dir, 'networks_per_event_summary.csv')
        df_summary.to_csv(summary_path, index=False)

        print(f"\n{'='*80}")
        print(f"RESUMO GERAL")
        print("="*80)
        print(f"Total de redes geradas: {len(summary_stats)}")
        print(f"Redes conectadas: {df_summary['connected'].sum()} ({df_summary['connected'].mean()*100:.1f}%)")
        print(f"Redes fragmentadas: {(~df_summary['connected']).sum()}")
        print(f"\nResumo salvo em: {summary_path}")

        return df_summary


if __name__ == "__main__":
    analyzer = SportsNetworkAnalyzerPerEvent(
        data_path='../../data/athlete_events.csv',
        selected_sports=['Swimming', 'Basketball', 'Football', 'Athletics', 'Judo', 'Boxing'],
        base_dir='../../results'
    )

    summary = analyzer.run_analysis_per_event()

    print("\n" + "="*80)
    print("GERAÇÃO CONCLUÍDA")
    print("="*80)
