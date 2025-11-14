"""
Componente de visualização de redes usando vis-network.

Renderiza redes interativas com tooltips ricos e timeline temporal.
"""

import json
from pathlib import Path
import streamlit.components.v1 as components
import sys


def render_cosmograph(nodes: list, links: list, height: int = 800,
                     physics_enabled: bool = True,
                     show_labels: bool = True,
                     color_scheme: str = 'default',
                     edge_opacity: float = 0.3,
                     node_scale_min: int = 5,
                     node_scale_max: int = 50,
                     gravitational_constant: int = -800,
                     spring_length: int = 150,
                     spring_constant: float = 0.04,
                     color_by: str = 'Comunidade',
                     key: str = None):
    """
    Renderiza uma rede interativa usando vis-network.

    # DEBUG
    print(f"[render_cosmograph] CHAMADA! Nodes: {len(nodes)}, Links: {len(links)}", flush=True)

    Parameters
    ----------
    nodes: list of dict
        Lista de nós com estrutura: [{'id': 'node1', 'label': 'Node 1', 'size': 10, 'group': 0}, ...]
    links: list of dict
        Lista de arestas com estrutura: [{'source': 'node1', 'target': 'node2', 'value': 1}, ...]
    height: int
        Altura do componente em pixels
    physics_enabled: bool
        Se True, nós se movem com física; se False, layout estático
    show_labels: bool
        Se True, mostra labels dos nós
    color_scheme: str
        Esquema de cores: 'default', 'pastel', 'vibrant', 'cool', 'warm'
    edge_opacity: float
        Opacidade das arestas (0.0 a 1.0)
    node_scale_min: int
        Tamanho mínimo dos nós
    node_scale_max: int
        Tamanho máximo dos nós
    """

    # Carregar arquivos externos
    component_dir = Path(__file__).parent

    with open(component_dir / 'cosmograph_styles.css', 'r', encoding='utf-8') as f:
        css_content = f.read()

    with open(component_dir / 'control_panel.css', 'r', encoding='utf-8') as f:
        control_panel_css = f.read()

    with open(component_dir / 'control_panel_html.txt', 'r', encoding='utf-8') as f:
        control_panel_html = f.read()
    
    with open(component_dir / 'tooltip_utils.js', 'r', encoding='utf-8') as f:
        tooltip_js = f.read()

    with open(component_dir / 'athlete_toast.js', 'r', encoding='utf-8') as f:
        athlete_toast_js = f.read()

    with open(component_dir / 'athlete_search.js', 'r', encoding='utf-8') as f:
        athlete_search_js = f.read()

    with open(component_dir / 'physics_manager.js', 'r', encoding='utf-8') as f:
        physics_manager_js = f.read()

    with open(component_dir / 'color_manager.js', 'r', encoding='utf-8') as f:
        color_manager_js = f.read()

    with open(component_dir / 'community_legend.js', 'r', encoding='utf-8') as f:
        community_legend_js = f.read()

    with open(component_dir / 'control_panel.js', 'r', encoding='utf-8') as f:
        control_panel_js = f.read()

    with open(component_dir / 'network_controls.js', 'r', encoding='utf-8') as f:
        network_controls_js = f.read()

    with open(component_dir / 'minimap.js', 'r', encoding='utf-8') as f:
        minimap_js = f.read()

    with open(component_dir / 'network_init.js', 'r', encoding='utf-8') as f:
        network_init_js = f.read()

    with open(component_dir / 'debug_hidden.js', 'r', encoding='utf-8') as f:
        debug_hidden_js = f.read()


    # Verificar McLOUGHLIN

    # Converter dados para JSON
    nodes_json = json.dumps(nodes)
    links_json = json.dumps(links)

    # Verificar tamanho do JSON

    # Teste: carregar de volta para garantir que não há perda

    # Paletas de cores expandidas
    color_schemes = {
        'default': ['#8B2635', '#2E5A88', '#2A7F62', '#D4A017', '#8B4513', '#4B0082', '#008B8B', '#B8860B',
                   '#CD5C5C', '#4682B4', '#9ACD32', '#FF8C00', '#8A2BE2', '#20B2AA', '#CD853F', '#9370DB'],
        'pastel': ['#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#E0BBE4', '#FFDFD3', '#C9E4DE',
                  '#FFC8DD', '#BDE0FE', '#A2D2FF', '#CDB4DB', '#FEC89A', '#F1FAEE', '#A8DADC', '#E5989B'],
        'vibrant': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
                   '#F8B195', '#F67280', '#C06C84', '#6C5B7B', '#355C7D', '#99B898', '#FECEAB', '#FF847C'],
        'cool': ['#1A535C', '#4ECDC4', '#F7FFF7', '#FF6B6B', '#FFE66D', '#2E86AB', '#A23B72', '#F18F01',
                '#C73E1D', '#6A994E', '#BC4749', '#F2CC8F', '#81B29A', '#3D405B', '#E07A5F', '#F4F1DE'],
        'warm': ['#D62828', '#F77F00', '#FCBF49', '#EAE2B7', '#003049', '#D9376E', '#FF8C42', '#FFC857',
                '#E5323B', '#F25F5C', '#FFE066', '#50514F', '#247BA0', '#70C1B3', '#B2DBBF', '#F3FFBD']
    }

    selected_colors = color_schemes.get(color_scheme, color_schemes['default'])
    selected_colors_json = json.dumps(selected_colors)
    edge_color = f'rgba(200, 200, 200, {edge_opacity})'
    
    # Configurações para o JavaScript
    config = {
        'physicsEnabled': physics_enabled,
        'showLabels': show_labels,
        'edgeColor': edge_color,
        'edgeOpacity': edge_opacity,
        'nodeScaleMin': node_scale_min,
        'nodeScaleMax': node_scale_max,
        'gravitationalConstant': gravitational_constant,
        'springLength': spring_length,
        'springConstant': spring_constant,
        'colorBy': color_by
    }
    config_json = json.dumps(config)
    
    if key is None:
        key = "network_viz"

    # HTML limpo com imports
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            {css_content}
            {control_panel_css}
            #cosmograph {{
                height: {height}px;
            }}
        </style>
    </head>
    <body>
        <div id="loading" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 24px; color: #8B2635; font-weight: bold; z-index: 9999;">
            Carregando visualização...
        </div>
        <div id="cosmograph"></div>
        <div id="custom-tooltip"></div>

        <!-- Painel de Controle -->
        {control_panel_html}

        <!-- Legenda de Comunidades -->
        <div id="community-legend">
            <div class="legend-header">
                <div class="legend-title">
                    <span>Comunidades</span>
                </div>
                <button class="legend-toggle-btn" onclick="toggleLegend()">−</button>
            </div>
            <div class="legend-content" id="legend-items"></div>
            <div class="legend-actions">
                <button class="legend-action-btn" onclick="showAllCommunities()">Mostrar Todas</button>
                <button class="legend-action-btn" onclick="resetCommunityFilter()">Limpar Filtro</button>
            </div>
        </div>

        <!-- Busca de Atleta -->
        <div id="athlete-search-container">
            <div id="athlete-search-box">
                <span class="search-icon">🔍</span>
                <input
                    type="text"
                    id="athlete-search-input"
                    placeholder="Buscar atleta por nome..."
                    autocomplete="off"
                    spellcheck="false"
                />
                <button id="clear-search" onclick="clearSearch()">✕</button>
                <div id="search-suggestions"></div>
            </div>
        </div>

        <!-- Mini-mapa -->
        <div id="minimap-container">
            <canvas id="minimap-canvas"></canvas>
            <div id="minimap-viewport"></div>
            <button id="minimap-toggle" onclick="toggleMinimap()">−</button>
        </div>

        <!-- Controles de Visualização -->
        <div id="network-controls">
            <button class="control-btn" id="btn-reset-zoom" data-tooltip="Reset Zoom" onclick="resetZoom()">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
                </svg>
            </button>
            <button class="control-btn" id="btn-toggle-physics" data-tooltip="Pausar Física" onclick="togglePhysics()">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                </svg>
            </button>
            <button class="control-btn" id="btn-screenshot" data-tooltip="Capturar Screenshot" onclick="takeScreenshot()">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="3.2"/>
                    <path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
                </svg>
            </button>
            <button class="control-btn" id="btn-fullscreen" data-tooltip="Tela Cheia" onclick="toggleFullscreen()">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
                </svg>
            </button>
        </div>

        <!-- Toast Flutuante para Detalhes do Atleta -->
        <div id="athlete-toast">
            <div class="toast-header">
                <h3 id="toast-athlete-name">Atleta</h3>
                <button class="toast-close-btn" onclick="closeAthleteToast()">✕</button>
            </div>
            <div class="toast-content">
                <div class="toast-section">
                    <div class="toast-section-title">Informações Básicas</div>
                    <div class="toast-info-grid">
                        <div class="toast-info-item">
                            <div class="toast-info-label">País (NOC)</div>
                            <div class="toast-info-value" id="toast-noc">-</div>
                        </div>
                        <div class="toast-info-item">
                            <div class="toast-info-label">Time</div>
                            <div class="toast-info-value" id="toast-team">-</div>
                        </div>
                        <div class="toast-info-item">
                            <div class="toast-info-label">Anos de Participação</div>
                            <div class="toast-info-value" id="toast-years">-</div>
                        </div>
                        <div class="toast-info-item">
                            <div class="toast-info-label">Idade</div>
                            <div class="toast-info-value" id="toast-age">-</div>
                        </div>
                    </div>
                </div>

                <div class="toast-section">
                    <div class="toast-section-title">Medalhas Conquistadas</div>
                    <div class="toast-medals">
                        <div class="toast-medal-item">
                            <span class="toast-medal-icon">🥇</span>
                            <span class="toast-medal-count" id="toast-gold">0</span>
                        </div>
                        <div class="toast-medal-item">
                            <span class="toast-medal-icon">🥈</span>
                            <span class="toast-medal-count" id="toast-silver">0</span>
                        </div>
                        <div class="toast-medal-item">
                            <span class="toast-medal-icon">🥉</span>
                            <span class="toast-medal-count" id="toast-bronze">0</span>
                        </div>
                    </div>
                </div>

                <div class="toast-section">
                    <div class="toast-section-title">Métricas de Rede</div>
                    <div class="toast-metrics">
                        <div class="toast-metric-row">
                            <span class="toast-metric-label">PageRank</span>
                            <span class="toast-metric-value" id="toast-pagerank">-</span>
                        </div>
                        <div class="toast-metric-row">
                            <span class="toast-metric-label">Percentil PageRank</span>
                            <span class="toast-metric-value" id="toast-pagerank-percentile">-</span>
                        </div>
                        <div class="toast-metric-row">
                            <span class="toast-metric-label">Betweenness</span>
                            <span class="toast-metric-value" id="toast-betweenness">-</span>
                        </div>
                        <div class="toast-metric-row">
                            <span class="toast-metric-label">Grau de Entrada</span>
                            <span class="toast-metric-value" id="toast-degree-in">-</span>
                        </div>
                        <div class="toast-metric-row">
                            <span class="toast-metric-label">Grau de Saída</span>
                            <span class="toast-metric-value" id="toast-degree-out">-</span>
                        </div>
                        <div class="toast-metric-row">
                            <span class="toast-metric-label">Comunidade <span id="toast-bridge-badge"></span></span>
                            <span class="toast-metric-value" id="toast-community">-</span>
                        </div>
                    </div>
                </div>

                <div class="toast-section" id="toast-rivals-section" style="display: none;">
                    <div class="toast-section-title">Conexões Diretas (<span id="toast-rivals-count">0</span>)</div>
                    <div class="toast-rivals-list" id="toast-rivals-list"></div>
                </div>
            </div>
            <div class="toast-actions">
                <button class="toast-action-btn toast-action-btn-primary" onclick="highlightRivals()">
                    👥 Ver Rivais Diretos
                </button>
                <button class="toast-action-btn toast-action-btn-secondary" onclick="isolateSubnetwork()">
                    🔍 Isolar Subrede
                </button>
                <button class="toast-action-btn toast-action-btn-secondary" onclick="focusOnNode()">
                    🎯 Centralizar na Rede
                </button>
            </div>
        </div>

        <!-- Carregar vis-network via CDN -->
        <script src="https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js"></script>

        <!-- Utilitários -->
        <script>{tooltip_js}</script>
        <script>{athlete_toast_js}</script>
        <script>{athlete_search_js}</script>

        <!-- Gerenciadores Centralizados (ORDEM IMPORT: devem carregar primeiro) -->
        <script>{physics_manager_js}</script>
        <script>{color_manager_js}</script>

        <!-- Componentes UI -->
        <script>{community_legend_js}</script>
        <script>{control_panel_js}</script>
        <script>{network_controls_js}</script>
        <script>{minimap_js}</script>
        <script>{debug_hidden_js}</script>

        <!-- Inicialização (ÚLTIMO - depende de todos os outros) -->
        <script>{network_init_js}</script>

        <!-- Inicializar -->
        <script>
            const nodesData = {nodes_json};
            const linksData = {links_json};
            const colorPalette = {selected_colors_json};
            const config = {config_json};
            const keyName = '{key}';

            // Tornar config disponível globalmente
            window.config = config;

            // DEBUG: Log inicial
            console.log('='.repeat(80));
            console.log('SCRIPT DE INICIALIZAÇÃO CARREGADO');
            console.log('Document readyState:', document.readyState);
            console.log('Nodes:', nodesData ? nodesData.length : 'undefined');
            console.log('Links:', linksData ? linksData.length : 'undefined');
            console.log('='.repeat(80));

            // Inicializar diretamente (SEM retry por enquanto para debug)
            function startNetwork() {{
                console.log('>>> startNetwork() chamada');

                // Verificar se vis-network está disponível
                if (typeof vis === 'undefined') {{
                    console.error('ERRO: vis-network não carregou!');
                    alert('ERRO: Biblioteca vis-network não foi carregada.');
                    return;
                }}
                console.log('✓ vis-network disponível');

                // Verificar se initNetwork existe
                if (typeof initNetwork === 'undefined') {{
                    console.error('ERRO: initNetwork não está definida!');
                    alert('ERRO: Função initNetwork não foi carregada.');
                    return;
                }}
                console.log('✓ initNetwork disponível');

                console.log('>>> Chamando initNetwork...');
                try {{
                    initNetwork(nodesData, linksData, colorPalette, config, keyName);
                    console.log('✓ initNetwork executada com sucesso');
                }} catch (error) {{
                    console.error('ERRO ao executar initNetwork:', error);
                    console.error('Stack:', error.stack);
                    alert('ERRO ao inicializar rede: ' + error.message);
                }}
            }}

            // Aguardar DOM carregar
            if (document.readyState === 'loading') {{
                console.log('Document loading... aguardando DOMContentLoaded');
                document.addEventListener('DOMContentLoaded', () => {{
                    console.log('DOMContentLoaded fired');
                    setTimeout(startNetwork, 200);
                }});
            }} else {{
                console.log('Document já carregado, inicializando imediatamente');
                setTimeout(startNetwork, 200);
            }}
        </script>
    </body>
    </html>
    """

    # Renderizar no Streamlit
    return components.html(html_code, height=height, width=None, scrolling=False)
