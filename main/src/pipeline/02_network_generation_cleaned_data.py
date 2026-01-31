#!/usr/bin/env python3
"""
Gera redes usando dados LIMPOS e NORMALIZADOS.
UMA REDE para CADA (Sport, Event_Normalized).

AGRUPAMENTO: (Year, Event_Normalized) - competição direta no mesmo pódio
"""

import pandas as pd
import networkx as nx
import numpy as np
import os
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

class CleanedNetworkGenerator:
    """Gera redes a partir dos dados limpos."""

    def __init__(self, data_path: str, output_dir: str = '../../results_per_event_cleaned'):
        self.data_path = data_path
        self.output_dir = output_dir
        self.df = None

        os.makedirs(self.output_dir, exist_ok=True)

    def load_data(self):
        """Carrega dados limpos."""
        print("Carregando dados limpos e normalizados...")
        self.df = pd.read_csv(self.data_path)

        # Filtrar apenas medalhistas
        self.df = self.df[self.df['Medal'].notna()]

        print(f"Total de medalhistas: {len(self.df):,}")
        print(f"Atletas únicos: {self.df['ID'].nunique():,}")
        print(f"Esportes: {', '.join(self.df['Sport'].unique())}")
        print(f"Eventos normalizados únicos: {self.df['Event_Normalized'].nunique()}")

        return self.df

    def create_athlete_network(self, event_data: pd.DataFrame) -> nx.DiGraph:
        """Cria rede direcionada para um evento específico.

        Agrupamento: (Year, Event_Normalized)
        Atletas do mesmo pódio (Year + Event) são conectados.
        """
        G = nx.DiGraph()

        # Agregar informações por atleta
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
                "name": str(row['Name']) if pd.notna(row['Name']) else "Unknown",
                "sex": str(row['Sex']) if pd.notna(row['Sex']) else "U",
                "age": int(row['Age']) if pd.notna(row['Age']) else 0,
                "height": int(row['Height']) if pd.notna(row['Height']) else 0,
                "weight": int(row['Weight']) if pd.notna(row['Weight']) else 0,
                "team": str(row['Team']) if pd.notna(row['Team']) else "Unknown",
                "noc": str(row['NOC']) if pd.notna(row['NOC']) else "UNK",
                "games": str(row['Games']) if pd.notna(row['Games']) else "Unknown",
                "city": str(row['City']) if pd.notna(row['City']) else "Unknown",
                "medal": str(medal_counts['last_medal']) if pd.notna(medal_counts['last_medal']) else "Bronze",
                "gold_medals": int(medal_counts['Gold']),
                "silver_medals": int(medal_counts['Silver']),
                "bronze_medals": int(medal_counts['Bronze']),
                "total_medals": int(medal_counts['Gold'] + medal_counts['Silver'] + medal_counts['Bronze'])
            }
            G.add_node(row['ID'], **athlete_info)

        # Adicionar arestas (agrupamento por Year + Event_Normalized)
        for (year, event_normalized), podium_group in event_data.groupby(['Year', 'Event_Normalized']):
            self._add_competition_edges(G, podium_group)

        # Remover nós isolados
        isolated_nodes = [node for node in G.nodes() if G.degree(node) == 0]
        if isolated_nodes:
            G.remove_nodes_from(isolated_nodes)

        return G

    def _add_competition_edges(self, G: nx.DiGraph, podium_group: pd.DataFrame):
        """Adiciona arestas entre medalhistas do mesmo pódio."""
        unique_athletes = podium_group['ID'].nunique()
        if unique_athletes < 2:
            return

        medalists = podium_group[['ID', 'Medal']].sort_values(
            by='Medal', key=lambda x: x.map({'Gold': 1, 'Silver': 2, 'Bronze': 3})
        ).values

        # Verificar se é evento de equipe (múltiplos atletas na mesma medalha)
        medal_counts = podium_group.groupby('Medal')['ID'].nunique()
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

        # Criar arestas direcionadas: perdedor → vencedor
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

    def run_generation(self):
        """Executa geração de redes para todos os eventos."""
        print("\n" + "="*100)
        print("GERAÇÃO DE REDES POR EVENTO (Dados Limpos)")
        print("="*100)

        self.load_data()

        summary_stats = []

        for sport in sorted(self.df['Sport'].unique()):
            print(f"\n{'='*100}")
            print(f"Processando {sport}...")
            print("="*100)

            sport_df = self.df[self.df['Sport'] == sport]
            sport_dir = os.path.join(self.output_dir, sport.lower())
            os.makedirs(sport_dir, exist_ok=True)

            # Obter eventos normalizados únicos
            unique_events = sorted(sport_df['Event_Normalized'].unique())
            print(f"\n{len(unique_events)} eventos normalizados")

            for event_normalized in unique_events:
                event_data = sport_df[sport_df['Event_Normalized'] == event_normalized]

                # Verificar se tem atletas suficientes
                num_athletes = event_data['ID'].nunique()
                if num_athletes < 2:
                    print(f"  [SKIP] {event_normalized}: apenas {num_athletes} atleta(s)")
                    continue

                # Criar rede
                G = self.create_athlete_network(event_data)

                if G.number_of_nodes() < 2:
                    print(f"  [SKIP] {event_normalized}: rede com < 2 nós")
                    continue

                # Nome do arquivo
                safe_event_name = event_normalized.replace(' ', '_').replace(',', '').replace('/', '_')
                safe_event_name = ''.join(c for c in safe_event_name if c.isalnum() or c in '_-.')

                file_name = f"{sport.lower()}_{safe_event_name}.gexf"
                file_path = os.path.join(sport_dir, file_name)

                # Salvar rede
                nx.write_gexf(G, file_path)

                # Estatísticas
                num_components = nx.number_weakly_connected_components(G)

                stats = {
                    'sport': sport,
                    'event_normalized': event_normalized,
                    'file': file_name,
                    'nodes': G.number_of_nodes(),
                    'edges': G.number_of_edges(),
                    'components': num_components,
                    'connected': num_components == 1,
                    'years_covered': event_data['Year'].nunique(),
                    'first_year': event_data['Year'].min(),
                    'last_year': event_data['Year'].max()
                }
                summary_stats.append(stats)

                status = "✓ CONECTADA" if num_components == 1 else f"⚠️  {num_components} componentes"
                print(f"  {event_normalized[:70]:<70} → {G.number_of_nodes():>4} nós, {G.number_of_edges():>5} arestas [{status}]")

        # Salvar resumo
        df_summary = pd.DataFrame(summary_stats)
        summary_path = os.path.join(self.output_dir, 'networks_summary.csv')
        df_summary.to_csv(summary_path, index=False)

        print(f"\n{'='*100}")
        print(f"RESUMO GERAL")
        print("="*100)
        print(f"Total de redes geradas: {len(summary_stats)}")
        print(f"Redes conectadas: {df_summary['connected'].sum()} ({df_summary['connected'].mean()*100:.1f}%)")
        print(f"Redes fragmentadas: {(~df_summary['connected']).sum()}")
        print(f"\nResumo salvo em: {summary_path}")

        return df_summary


if __name__ == "__main__":
    generator = CleanedNetworkGenerator(
        data_path='../../data/athlete_events_cleaned.csv',
        output_dir='../../results_per_event_cleaned'
    )

    summary = generator.run_generation()

    print("\n" + "="*100)
    print("GERAÇÃO CONCLUÍDA")
    print("="*100)
