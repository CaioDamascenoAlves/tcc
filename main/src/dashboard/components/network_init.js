// Script principal para inicialização da rede
console.log('[network_init.js] Arquivo carregado!');

function initNetwork(nodesData, linksData, colorPalette, config, keyName) {
    console.log('[initNetwork] FUNÇÃO CHAMADA!');
    // DEBUG: Verificar dados recebidos do Python
    console.log('='.repeat(80));
    console.log('[initNetwork] RECEBEU DO PYTHON:');
    console.log('  - Nodes:', nodesData.length);
    console.log('  - Links:', linksData.length);

    // Procurar McLOUGHLIN nos dados recebidos (buscar por ID)
    const mcloughlinReceived = nodesData.find(n => n.id === '1978278640');
    if (mcloughlinReceived) {
        console.log('  - McLOUGHLIN RECEBIDO:', mcloughlinReceived.id, mcloughlinReceived.label);
    } else {
        console.warn('  - McLOUGHLIN NÃO RECEBIDO do Python!');
    }
    console.log('='.repeat(80));

    // Verificar se vis está disponível
    if (typeof vis === 'undefined') {
        console.error('vis-network library not loaded');
        document.getElementById('loading').textContent = 'Erro ao carregar biblioteca';
        return;
    }

    // Remover loading
    document.getElementById('loading').style.display = 'none';

    try {
        const container = document.getElementById('cosmograph');
        const tooltip = document.getElementById('custom-tooltip');

        // Debug: contar distribuição de grupos E mostrar cores
        const groupCounts = {};
        const groupColors = {};
        nodesData.forEach(n => {
            const g = typeof n.group === 'number' ? n.group : 0;
            groupCounts[g] = (groupCounts[g] || 0) + 1;
            if (!groupColors[g]) {
                groupColors[g] = colorPalette[g % colorPalette.length];
            }
        });
        console.log('Distribuição de grupos/comunidades:', groupCounts);
        console.log('Cores por grupo:');
        Object.keys(groupColors).sort((a,b) => a-b).forEach(g => {
            console.log(`  Grupo ${g}: ${groupColors[g]} (${groupCounts[g]} nós)`);
        });

        // Preparar dados para vis-network
        console.log('[initNetwork] Preparando nodes DataSet...');
        const nodes = new vis.DataSet(
            nodesData.map(n => {
                const groupIndex = typeof n.group === 'number' ? n.group : 0;
                const groupColor = colorPalette[groupIndex % colorPalette.length];

                // Debug: verificar McLOUGHLIN no map
                if (n.label && n.label.toUpperCase().includes('MCLOUGHLIN')) {
                    console.log('McLOUGHLIN dentro do map():');
                    console.log('  - ID:', n.id);
                    console.log('  - Label:', n.label);
                    console.log('  - Size:', n.size);
                    console.log('  - Group:', n.group);
                }

                // Debug: verificar se Michael Phelps tem grupo correto
                if (n.label && n.label.includes('Phelps')) {
                    console.log('Michael Phelps - DADOS ORIGINAIS do Python:');
                    console.log('  - ID:', n.id);
                    console.log('  - Grupo (n.group):', n.group);
                    console.log('  - Size:', n.size);
                    console.log('  - Todos os dados:', JSON.stringify(n, null, 2));
                }

                // Preserva todas as propriedades calculadas previamente (x, y, physics, etc.)
                const node = { ...n };
                node.label = config.showLabels ? (n.label || '') : '';
                // IMPORTANTE: vis-network usa 'value' para scaling, não 'size'
                node.value = n.size !== undefined ? n.size : 10;
                node.group = groupIndex;
                node.color = {
                    background: groupColor,
                    border: '#000000',
                    highlight: {
                        background: '#8B2635',
                        border: '#FF0000'
                    }
                };
                node.borderWidth = 2;
                node.tooltipHTML = window.createRichTooltip(n);

                // Debug: verificar McLOUGHLIN após processamento
                if (n.label && n.label.toUpperCase().includes('MCLOUGHLIN')) {
                    console.log('McLOUGHLIN DEPOIS de processar:');
                    console.log('  - node.id:', node.id);
                    console.log('  - node.label:', node.label);
                    console.log('  - node retornado:', node);
                }

                // Debug: verificar nó APÓS aplicar configurações
                if (n.label && n.label.includes('Phelps')) {
                    console.log('Michael Phelps - DEPOIS de aplicar configurações:');
                    console.log('  - node.color.background:', node.color.background);
                    console.log('  - node.color.border:', node.color.border);
                    console.log('  - node.group:', node.group);
                    console.log('  - node.size:', node.size);
                }

                return node;
            })
        );

        console.log('[initNetwork] DataSet criado com', nodes.length, 'nodes');

        // Verificar se McLOUGHLIN está no DataSet (buscar por ID direto)
        const mcloughlinById = nodes.get('1978278640');
        if (mcloughlinById) {
            console.log('[initNetwork] McLOUGHLIN no DataSet (por ID):', mcloughlinById.id, mcloughlinById.label);
        } else {
            console.error('[initNetwork] McLOUGHLIN NÃO está no DataSet (busca por ID)!');

            // Buscar por substring no label
            const allNodes = nodes.get();
            const mcloughlinByLabel = allNodes.find(n =>
                n.label && n.label.toUpperCase().includes('MCLOUGHLIN')
            );

            if (mcloughlinByLabel) {
                console.log('[initNetwork] Mas McLOUGHLIN encontrado por label:', mcloughlinByLabel.id, mcloughlinByLabel.label);
            } else {
                console.error('[initNetwork] McLOUGHLIN REALMENTE não está no DataSet!');

                // Debug: procurar IDs próximos
                const nearbyIds = allNodes
                    .filter(n => Math.abs(parseInt(n.id) - 1978278640) < 1000)
                    .slice(0, 5);
                console.log('IDs próximos de 1978278640:', nearbyIds.map(n => ({ id: n.id, label: n.label })));
            }
        }

        const edges = new vis.DataSet(
            linksData.map(l => {
                const edge = { ...l };
                edge.from = l.from ?? l.source;
                edge.to = l.to ?? l.target;
                edge.value = l.value !== undefined ? l.value : 1;
                edge.color = { color: config.edgeColor, opacity: config.edgeOpacity };
                edge.smooth = l.smooth ? { ...l.smooth } : { type: 'continuous' };
                return edge;
            })
        );

        // Debug: mostrar vizinhos do Michael Phelps
        const phelpsNode = nodesData.find(n => n.label && n.label.includes('Phelps'));
        if (phelpsNode) {
            const phelpsId = phelpsNode.id;
            const neighbors = linksData
                .filter(l => (l.source === phelpsId || l.from === phelpsId) || (l.target === phelpsId || l.to === phelpsId))
                .map(l => {
                    const neighborId = (l.source === phelpsId || l.from === phelpsId) ? (l.target || l.to) : (l.source || l.from);
                    const neighborNode = nodesData.find(n => n.id === neighborId);
                    return neighborNode ? { id: neighborId, name: neighborNode.label, group: neighborNode.group } : null;
                })
                .filter(n => n !== null)
                .slice(0, 10); // Primeiros 10 vizinhos

            console.log('Vizinhos de Michael Phelps (primeiros 10):');
            neighbors.forEach(n => console.log(`  - ${n.name} (grupo ${n.group})`));
        }

        // Configurações do layout
        const options = {
            nodes: {
                shape: 'dot',
                scaling: {
                    min: config.nodeScaleMin,
                    max: config.nodeScaleMax
                },
                font: {
                    size: 12,
                    color: '#2A2A2A'
                }
            },
            edges: {
                width: 1,
                smooth: {
                    enabled: true,
                    type: 'continuous'
                },
                arrows: {
                    to: {
                        enabled: config.showArrows !== undefined ? config.showArrows : false,
                        scaleFactor: 0.5,
                        type: 'arrow'
                    }
                }
            },
            physics: {
                enabled: config.physicsEnabled,
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {
                    gravitationalConstant: config.gravitationalConstant,
                    centralGravity: 0.005,  // Reduzido de 0.01
                    springLength: config.springLength,
                    springConstant: config.springConstant,
                    damping: 0.98,  // Aumentado de 0.95 (converge mais rápido)
                    avoidOverlap: 0
                },
                maxVelocity: 20,  // Reduzido de 1000 (menos caótico)
                minVelocity: 1.5,  // Aumentado de 0.75 (para mais cedo)
                timestep: 0.5,  // Aumentado de 0.2 (passos maiores)
                stabilization: {
                    enabled: true,
                    iterations: 200,  // Reduzido de 1000 (5x mais rápido!)
                    updateInterval: 25,  // Reduzido de 50 (updates mais frequentes)
                    onlyDynamicEdges: false,
                    fit: true
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 100,
                zoomView: true,
                dragView: true
            }
        };

        // Criar rede
        const network = new vis.Network(container, { nodes, edges }, options);

        // Tornar networkInstance global para os gerenciadores
        window.networkInstance = network;
        window.nodesDataset = nodes;
        window.edgesDataset = edges;
        window.allNodesData = nodesData;

        // Inicializar gerenciadores centralizados
        window.initPhysicsManager(config.physicsEnabled);
        window.initColorManager(config.colorBy, 'default'); // Sempre começa com 'default' do Python

        // Passar referência da rede para o sistema de toast
        window.setNetworkReference(network, nodes, edges, nodesData, linksData);

        // Inicializar índice de busca
        window.initSearchIndex(nodesData);

        // Inicializar legenda de comunidades
        window.initCommunityLegend(nodesData, colorPalette);

        // Inicializar painel de controle
        window.initControlPanel(config);

        // Monitorar estabilização de física
        network.on('stabilizationProgress', window.onStabilizationProgress);
        network.on('stabilizationIterationsDone', window.onStabilizationComplete);

        // Tooltip customizado ao hover
        network.on('hoverNode', function(params) {
            const nodeId = params.node;
            const node = nodes.get(nodeId);
            
            if (node && node.tooltipHTML) {
                tooltip.innerHTML = node.tooltipHTML;
                tooltip.style.display = 'block';
            }
        });

        // Atualizar posição do tooltip ao mover o mouse
        network.on('hoverNode', function(params) {
            const canvasPos = network.canvasToDOM({ x: params.pointer.canvas.x, y: params.pointer.canvas.y });
            tooltip.style.left = (canvasPos.x + 15) + 'px';
            tooltip.style.top = (canvasPos.y + 15) + 'px';
        });

        // Esconder tooltip ao sair do nó
        network.on('blurNode', function() {
            tooltip.style.display = 'none';
        });

        // Esconder tooltip ao mover o mouse fora da rede
        container.addEventListener('mouseleave', function() {
            tooltip.style.display = 'none';
        });

        // Event handlers
        network.on('click', function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                console.log('Clicked node:', nodeId, node);

                // Mostrar toast com detalhes do atleta
                window.showAthleteToast(nodeId, node);

                // Enviar dados do nó para o Streamlit (mantido para compatibilidade)
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    key: keyName,
                    value: {
                        nodeId: nodeId,
                        nodeData: node
                    }
                }, '*');
            } else {
                // Click no background - fechar toast se estiver aberta
                const toast = document.getElementById('athlete-toast');
                if (toast && toast.classList.contains('visible')) {
                    window.closeAthleteToast();
                }
            }
        });

        // Inicializar botão de física com o estado inicial da config
        window.initPhysicsButton(config.physicsEnabled);

        // Função para inicializar mini-mapa
        function initMinimapAfterRender() {
            setTimeout(() => {
                if (typeof window.initMinimap === 'function') {
                    console.log('Initializing minimap...');
                    window.initMinimap();
                } else {
                    console.error('initMinimap function not found');
                }
            }, 1000);
        }

        // Se física está ativada, inicializar após estabilização
        if (config.physicsEnabled) {
            network.once('stabilizationIterationsDone', function() {
                network.fit();

                // DESATIVAR FÍSICA após estabilizar para parar movimento
                network.setOptions({ physics: { enabled: false } });

                // Atualizar botão para refletir que física foi desativada
                window.initPhysicsButton(false);

                console.log('Rede estabilizada - física desativada');

                // Inicializar mini-mapa
                initMinimapAfterRender();
            });
        } else {
            // Se física está desativada, inicializar após render inicial
            console.log('Physics disabled - initializing minimap after initial render');
            setTimeout(() => {
                network.fit();
                initMinimapAfterRender();
            }, 500);
        }

    } catch (error) {
        console.error('Error initializing network:', error);
        document.getElementById('loading').textContent = 'Erro ao inicializar: ' + error.message;
        document.getElementById('loading').style.display = 'block';
    }
}
