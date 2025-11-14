// Painel de Controle Unificado

let controlPanelState = {
    colorBy: 'Comunidade',
    colorScheme: 'default',
    edgeOpacity: 0.3,
    edgeColorMode: 'solid',
    edgeWidthMin: 1,
    edgeWidthMax: 5,
    nodeSizeMin: 5,
    nodeSizeMax: 50,
    nodeSizeMetric: 'pagerank',
    showLabels: true,
    physicsEnabled: false,
    gravity: -800,
    springLength: 150,
    springConstant: 0.04,
    topN: 10000,
    minEdgeWeight: 1
};

// Paletas de cores
const colorSchemes = {
    'default': ['#8B2635', '#2E5A88', '#2A7F62', '#D4A017', '#8B4513', '#4B0082', '#008B8B', '#B8860B',
               '#CD5C5C', '#4682B4', '#9ACD32', '#FF8C00', '#8A2BE2', '#20B2AA', '#CD853F', '#9370DB'],
    'pastel': ['#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#E0BBE4', '#FFDFD3', '#C9E4DE',
              '#FFC8DD', '#BDE0FE', '#A2D2FF', '#CDB4DB', '#FEC89A', '#F1FAEE', '#A8DADC', '#E5989B'],
    'vibrant': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
               '#F8B195', '#F67280', '#C06C84', '#6C5B7B', '#355C7D', '#99B898', '#FECEAB', '#FF847C'],
    'cool': ['#1A535C', '#4ECDC4', '#F7FFF7', '#FF6B6B', '#FFE66D', '#2E86AB', '#A23B72', '#F18F01',
            '#C73E1D', '#6A994E', '#BC4749', '#F2CC8F', '#81B29A', '#3D405B', '#E07A5F', '#F4F1DE']
};

// Toggle do painel
function toggleControlPanel() {
    const drawer = document.getElementById('control-panel-drawer');
    const overlay = document.getElementById('control-panel-overlay');
    const toggle = document.getElementById('control-panel-toggle');

    drawer.classList.toggle('open');
    overlay.classList.toggle('visible');
    toggle.classList.toggle('active');
}

// Toggle de seção (accordion)
function toggleSection(header) {
    const body = header.nextElementSibling;
    const allHeaders = document.querySelectorAll('.drawer-section-header');
    const allBodies = document.querySelectorAll('.drawer-section-body');

    // Fechar outras seções
    allHeaders.forEach(h => {
        if (h !== header) {
            h.classList.remove('active');
        }
    });
    allBodies.forEach(b => {
        if (b !== body) {
            b.classList.remove('expanded');
        }
    });

    // Toggle seção atual
    header.classList.toggle('active');
    body.classList.toggle('expanded');
}

// Mudar esquema de coloração
function changeColorBy(value) {
    controlPanelState.colorBy = value;

    // Usar o color manager para sincronização total
    if (typeof window.setColorBy === 'function') {
        window.setColorBy(value);
    }
}

// Mudar paleta de cores
function changeColorScheme(scheme) {
    controlPanelState.colorScheme = scheme;

    // Atualizar UI
    document.querySelectorAll('.color-palette-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.scheme === scheme) {
            item.classList.add('active');
        }
    });

    // Usar o color manager para sincronização total
    if (typeof window.setColorScheme === 'function') {
        window.setColorScheme(scheme);
    }
}

// Função removida - agora usa o color_manager centralizado

// Mudar opacidade das arestas
function changeEdgeOpacity(value) {
    controlPanelState.edgeOpacity = parseFloat(value);
    document.getElementById('edge-opacity-value').textContent = value;

    // Reaplicar cores das arestas com nova opacidade
    applyEdgeColors();
}

// Mudar modo de cor das arestas
function changeEdgeColorMode(mode) {
    controlPanelState.edgeColorMode = mode;
    console.log('Edge color mode changed to:', mode);

    // Reaplicar cores
    applyEdgeColors();
}

// Mudar espessura mínima das arestas
function changeEdgeWidthMin(value) {
    controlPanelState.edgeWidthMin = parseFloat(value);
    document.getElementById('edge-width-min-value').textContent = value;

    applyEdgeWidths();
}

// Mudar espessura máxima das arestas
function changeEdgeWidthMax(value) {
    controlPanelState.edgeWidthMax = parseFloat(value);
    document.getElementById('edge-width-max-value').textContent = value;

    applyEdgeWidths();
}

// Aplicar cores nas arestas
function applyEdgeColors() {
    if (!networkInstance || !edgesDataset || !nodesDataset) return;

    const allEdges = edgesDataset.get();
    const allNodes = nodesDataset.get();
    const edgesToUpdate = [];

    const opacity = controlPanelState.edgeOpacity;
    const mode = controlPanelState.edgeColorMode;

    allEdges.forEach(edge => {
        let color;

        if (mode === 'solid') {
            // Cor sólida cinza
            color = {
                color: `rgba(200, 200, 200, ${opacity})`,
                opacity: opacity
            };
        } else if (mode === 'from') {
            // Cor do nó de origem
            const fromNode = allNodes.find(n => n.id === edge.from);
            if (fromNode && fromNode.color && fromNode.color.background) {
                const rgb = hexToRgb(fromNode.color.background);
                color = {
                    color: `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${opacity})`,
                    opacity: opacity
                };
            } else {
                color = { color: `rgba(200, 200, 200, ${opacity})`, opacity };
            }
        } else if (mode === 'to') {
            // Cor do nó de destino
            const toNode = allNodes.find(n => n.id === edge.to);
            if (toNode && toNode.color && toNode.color.background) {
                const rgb = hexToRgb(toNode.color.background);
                color = {
                    color: `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${opacity})`,
                    opacity: opacity
                };
            } else {
                color = { color: `rgba(200, 200, 200, ${opacity})`, opacity };
            }
        } else if (mode === 'gradient') {
            // Gradiente de origem para destino
            const fromNode = allNodes.find(n => n.id === edge.from);
            const toNode = allNodes.find(n => n.id === edge.to);

            if (fromNode && toNode && fromNode.color && toNode.color) {
                const fromRgb = hexToRgb(fromNode.color.background);
                const toRgb = hexToRgb(toNode.color.background);

                color = {
                    color: `rgba(${fromRgb.r}, ${fromRgb.g}, ${fromRgb.b}, ${opacity})`,
                    highlight: `rgba(${toRgb.r}, ${toRgb.g}, ${toRgb.b}, ${opacity})`,
                    opacity: opacity,
                    inherit: false
                };
            } else {
                color = { color: `rgba(200, 200, 200, ${opacity})`, opacity };
            }
        }

        edgesToUpdate.push({
            id: edge.id,
            color: color,
            width: edge.width // Preservar largura
        });
    });

    edgesDataset.update(edgesToUpdate);

    // Forçar re-render completo
    networkInstance.redraw();

    console.log('Edge colors updated:', edgesToUpdate.length, 'edges');
}

// Aplicar espessuras nas arestas baseado no peso
function applyEdgeWidths() {
    if (!networkInstance || !edgesDataset) return;

    const allEdges = edgesDataset.get();
    const edgesToUpdate = [];

    // Encontrar peso min/max para normalização
    let minWeight = Infinity;
    let maxWeight = -Infinity;

    allEdges.forEach(edge => {
        const weight = edge.weight || edge.value || 1;
        if (weight < minWeight) minWeight = weight;
        if (weight > maxWeight) maxWeight = weight;
    });

    const widthRange = controlPanelState.edgeWidthMax - controlPanelState.edgeWidthMin;

    allEdges.forEach(edge => {
        const weight = edge.weight || edge.value || 1;

        // Normalizar peso para range de espessura
        let width;
        if (maxWeight === minWeight) {
            width = controlPanelState.edgeWidthMin;
        } else {
            const normalized = (weight - minWeight) / (maxWeight - minWeight);
            width = controlPanelState.edgeWidthMin + (normalized * widthRange);
        }

        edgesToUpdate.push({
            id: edge.id,
            width: width,
            color: edge.color, // Preservar cor
            // Adicionar scaling para forçar vis-network a recalcular
            scaling: {
                min: controlPanelState.edgeWidthMin,
                max: controlPanelState.edgeWidthMax
            }
        });
    });

    edgesDataset.update(edgesToUpdate);

    // Forçar re-render completo
    networkInstance.redraw();

    console.log('Edge widths updated:', edgesToUpdate.length, 'edges');
}

// Helper: Converter hex para RGB
function hexToRgb(hex) {
    // Remove # se existir
    hex = hex.replace('#', '');

    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);

    return { r, g, b };
}

// Mudar tamanho mínimo dos nós
function changeNodeSizeMin(value) {
    controlPanelState.nodeSizeMin = parseInt(value);
    document.getElementById('node-size-min-value').textContent = value;

    if (!networkInstance || !nodesDataset) return;

    networkInstance.setOptions({
        nodes: {
            scaling: {
                min: parseInt(value),
                max: controlPanelState.nodeSizeMax
            }
        }
    });

    // Forçar atualização COMPLETA: tocar nos nós para re-render
    const allNodes = nodesDataset.get();
    const nodesToUpdate = allNodes.map(n => ({
        id: n.id,
        value: n.value, // Re-aplicar value para forçar recálculo
        color: n.color
    }));
    nodesDataset.update(nodesToUpdate);
}

// Mudar tamanho máximo dos nós
function changeNodeSizeMax(value) {
    controlPanelState.nodeSizeMax = parseInt(value);
    document.getElementById('node-size-max-value').textContent = value;

    if (!networkInstance || !nodesDataset) return;

    networkInstance.setOptions({
        nodes: {
            scaling: {
                min: controlPanelState.nodeSizeMin,
                max: parseInt(value)
            }
        }
    });

    // Forçar atualização COMPLETA: tocar nos nós para re-render
    const allNodes = nodesDataset.get();
    const nodesToUpdate = allNodes.map(n => ({
        id: n.id,
        value: n.value, // Re-aplicar value para forçar recálculo
        color: n.color
    }));
    nodesDataset.update(nodesToUpdate);
}

// Mudar métrica de tamanho dos nós
function changeNodeSizeMetric(metric) {
    controlPanelState.nodeSizeMetric = metric;

    if (!networkInstance || !nodesDataset || !allNodesData) return;

    console.log('Changing node size metric to:', metric);

    // Recalcular valores para todos os nós
    const allNodes = nodesDataset.get();
    const nodesToUpdate = [];

    allNodes.forEach(node => {
        const originalNode = allNodesData.find(n => n.id === node.id);
        if (!originalNode) return;

        let value = 10; // Padrão

        if (metric === 'pagerank') {
            value = parseFloat(originalNode.tooltip_data?.pagerank || 0.001) * 1000;
        } else if (metric === 'betweenness') {
            value = parseFloat(originalNode.tooltip_data?.betweenness || 0.001) * 1000;
        } else if (metric === 'degree') {
            value = originalNode.tooltip_data?.degree_total || 1;
        } else if (metric === 'degree_in') {
            value = originalNode.tooltip_data?.degree_in || 1;
        } else if (metric === 'degree_out') {
            value = originalNode.tooltip_data?.degree_out || 1;
        } else if (metric === 'medals') {
            value = originalNode.tooltip_data?.medal_total || 1;
        } else if (metric === 'uniform') {
            value = 10;
        }

        nodesToUpdate.push({
            id: node.id,
            value: value,
            color: node.color // Preservar cor
        });
    });

    nodesDataset.update(nodesToUpdate);
    networkInstance.redraw();

    console.log('Node sizes updated:', nodesToUpdate.length, 'nodes');
}

// Toggle labels
function toggleLabels() {
    controlPanelState.showLabels = !controlPanelState.showLabels;

    const toggle = document.getElementById('labels-toggle');
    toggle.classList.toggle('active');

    if (!networkInstance || !nodesDataset) return;

    const allNodes = nodesDataset.get();
    const originalNodes = allNodesData;
    const nodesToUpdate = allNodes.map(node => {
        const original = originalNodes.find(n => n.id === node.id);

        // CRÍTICO: Preservar TODAS as propriedades, especialmente color
        return {
            id: node.id,
            label: controlPanelState.showLabels ? (original?.label || '') : '',
            // Preservar cor atual
            color: node.color
        };
    });

    nodesDataset.update(nodesToUpdate);
}

// Toggle física do painel
function togglePhysicsFromPanel() {
    // Delegar ao physics_manager (sincroniza com toolbar)
    if (typeof window.togglePhysics === 'function') {
        window.togglePhysics();
    }
}

// Mudar gravidade
function changeGravity(value) {
    controlPanelState.gravity = parseInt(value);
    document.getElementById('gravity-value').textContent = value;

    if (!networkInstance) return;

    networkInstance.setOptions({
        physics: {
            forceAtlas2Based: {
                gravitationalConstant: parseInt(value)
            }
        }
    });
}

// Mudar comprimento das molas
function changeSpringLength(value) {
    controlPanelState.springLength = parseInt(value);
    document.getElementById('spring-length-value').textContent = value;

    if (!networkInstance) return;

    networkInstance.setOptions({
        physics: {
            forceAtlas2Based: {
                springLength: parseInt(value)
            }
        }
    });
}

// Mudar constante das molas
function changeSpringConstant(value) {
    controlPanelState.springConstant = parseFloat(value);
    document.getElementById('spring-constant-value').textContent = value;

    if (!networkInstance) return;

    networkInstance.setOptions({
        physics: {
            forceAtlas2Based: {
                springConstant: parseFloat(value)
            }
        }
    });
}

// Mudar central gravity
function changeCentralGravity(value) {
    const numValue = parseFloat(value);
    document.getElementById('central-gravity-value').textContent = value;

    if (!networkInstance) return;

    networkInstance.setOptions({
        physics: {
            forceAtlas2Based: {
                centralGravity: numValue
            }
        }
    });
}

// Mudar damping
function changeDamping(value) {
    const numValue = parseFloat(value);
    document.getElementById('damping-value').textContent = value;

    if (!networkInstance) return;

    networkInstance.setOptions({
        physics: {
            forceAtlas2Based: {
                damping: numValue
            }
        }
    });
}

// Mudar max velocity
function changeMaxVelocity(value) {
    const numValue = parseInt(value);
    document.getElementById('max-velocity-value').textContent = value;

    if (!networkInstance) return;

    networkInstance.setOptions({
        physics: {
            maxVelocity: numValue
        }
    });
}

// Mudar min velocity
function changeMinVelocity(value) {
    const numValue = parseFloat(value);
    document.getElementById('min-velocity-value').textContent = value;

    if (!networkInstance) return;

    networkInstance.setOptions({
        physics: {
            minVelocity: numValue
        }
    });
}

// Mudar timestep
function changeTimestep(value) {
    const numValue = parseFloat(value);
    document.getElementById('timestep-value').textContent = value;

    if (!networkInstance) return;

    networkInstance.setOptions({
        physics: {
            timestep: numValue
        }
    });
}

// Resetar física para valores padrão
function resetPhysicsDefaults() {
    const defaults = {
        gravitationalConstant: -800,
        centralGravity: 0.005,
        springLength: 150,
        springConstant: 0.04,
        damping: 0.98,
        maxVelocity: 20,
        minVelocity: 1.5,
        timestep: 0.5
    };

    // Atualizar UI
    document.getElementById('gravity-slider').value = defaults.gravitationalConstant;
    document.getElementById('gravity-value').textContent = defaults.gravitationalConstant;

    document.getElementById('central-gravity-slider').value = defaults.centralGravity;
    document.getElementById('central-gravity-value').textContent = defaults.centralGravity;

    document.getElementById('spring-length-slider').value = defaults.springLength;
    document.getElementById('spring-length-value').textContent = defaults.springLength;

    document.getElementById('spring-constant-slider').value = defaults.springConstant;
    document.getElementById('spring-constant-value').textContent = defaults.springConstant;

    document.getElementById('damping-slider').value = defaults.damping;
    document.getElementById('damping-value').textContent = defaults.damping;

    document.getElementById('max-velocity-slider').value = defaults.maxVelocity;
    document.getElementById('max-velocity-value').textContent = defaults.maxVelocity;

    document.getElementById('min-velocity-slider').value = defaults.minVelocity;
    document.getElementById('min-velocity-value').textContent = defaults.minVelocity;

    document.getElementById('timestep-slider').value = defaults.timestep;
    document.getElementById('timestep-value').textContent = defaults.timestep;

    // Aplicar configurações
    if (!networkInstance) return;

    networkInstance.setOptions({
        physics: {
            forceAtlas2Based: {
                gravitationalConstant: defaults.gravitationalConstant,
                centralGravity: defaults.centralGravity,
                springLength: defaults.springLength,
                springConstant: defaults.springConstant,
                damping: defaults.damping
            },
            maxVelocity: defaults.maxVelocity,
            minVelocity: defaults.minVelocity,
            timestep: defaults.timestep
        }
    });

    console.log('Physics reset to defaults');
}

// Funções de exportação (placeholders)
function exportPNG() {
    if (typeof takeScreenshot === 'function') {
        takeScreenshot();
    } else {
        alert('Exportar PNG');
    }
}

function exportSVG() {
    alert('Exportação SVG será implementada');
}

function exportGEXF() {
    alert('Exportação GEXF será implementada');
}

function exportCSV() {
    alert('Exportação CSV será implementada');
}

// Inicializar painel com valores do config (exposta globalmente)
window.initControlPanel = function(config) {
    if (!config) return;

    // Atualizar estado interno
    if (config.colorBy) controlPanelState.colorBy = config.colorBy;
    if (config.edgeOpacity !== undefined) controlPanelState.edgeOpacity = config.edgeOpacity;
    if (config.nodeScaleMin !== undefined) controlPanelState.nodeSizeMin = config.nodeScaleMin;
    if (config.nodeScaleMax !== undefined) controlPanelState.nodeSizeMax = config.nodeScaleMax;
    if (config.showLabels !== undefined) controlPanelState.showLabels = config.showLabels;
    if (config.physicsEnabled !== undefined) controlPanelState.physicsEnabled = config.physicsEnabled;
    if (config.gravitationalConstant !== undefined) controlPanelState.gravity = config.gravitationalConstant;
    if (config.springLength !== undefined) controlPanelState.springLength = config.springLength;
    if (config.springConstant !== undefined) controlPanelState.springConstant = config.springConstant;

    // Atualizar UI
    document.getElementById('color-by-select').value = controlPanelState.colorBy;
    document.getElementById('edge-opacity-slider').value = controlPanelState.edgeOpacity;
    document.getElementById('edge-opacity-value').textContent = controlPanelState.edgeOpacity;
    document.getElementById('node-size-min-slider').value = controlPanelState.nodeSizeMin;
    document.getElementById('node-size-min-value').textContent = controlPanelState.nodeSizeMin;
    document.getElementById('node-size-max-slider').value = controlPanelState.nodeSizeMax;
    document.getElementById('node-size-max-value').textContent = controlPanelState.nodeSizeMax;
    document.getElementById('gravity-slider').value = controlPanelState.gravity;
    document.getElementById('gravity-value').textContent = controlPanelState.gravity;
    document.getElementById('spring-length-slider').value = controlPanelState.springLength;
    document.getElementById('spring-length-value').textContent = controlPanelState.springLength;
    document.getElementById('spring-constant-slider').value = controlPanelState.springConstant;
    document.getElementById('spring-constant-value').textContent = controlPanelState.springConstant;

    // Inicializar novos controles de física (valores padrão do network_init.js)
    if (document.getElementById('central-gravity-slider')) {
        document.getElementById('central-gravity-slider').value = 0.005;
        document.getElementById('central-gravity-value').textContent = '0.005';
    }
    if (document.getElementById('damping-slider')) {
        document.getElementById('damping-slider').value = 0.98;
        document.getElementById('damping-value').textContent = '0.98';
    }
    if (document.getElementById('max-velocity-slider')) {
        document.getElementById('max-velocity-slider').value = 20;
        document.getElementById('max-velocity-value').textContent = '20';
    }
    if (document.getElementById('min-velocity-slider')) {
        document.getElementById('min-velocity-slider').value = 1.5;
        document.getElementById('min-velocity-value').textContent = '1.5';
    }
    if (document.getElementById('timestep-slider')) {
        document.getElementById('timestep-slider').value = 0.5;
        document.getElementById('timestep-value').textContent = '0.5';
    }

    // Toggle switches
    if (controlPanelState.showLabels) {
        document.getElementById('labels-toggle').classList.add('active');
    }

    // Registrar callback para mudanças de física
    if (typeof onPhysicsChange === 'function') {
        onPhysicsChange(updatePanelPhysicsToggle);
    }

    // Atualizar toggle com estado inicial
    updatePanelPhysicsToggle(config.physicsEnabled);

    // Aplicar configurações iniciais de arestas
    setTimeout(() => {
        if (typeof applyEdgeWidths === 'function') {
            applyEdgeWidths();
        }
        if (typeof applyEdgeColors === 'function') {
            applyEdgeColors();
        }
    }, 500);

    console.log('Control panel initialized with config:', controlPanelState);
};

// Abrir primeira seção por padrão
document.addEventListener('DOMContentLoaded', () => {
    const firstSection = document.querySelector('.drawer-section-header');
    if (firstSection) {
        firstSection.click();
    }
});

console.log('Control panel module loaded');

// ==============================================================================
// FILTROS DE REDE
// ==============================================================================

// Filtrar número de nós (Top N por PageRank)
function changeTopN(value) {
    controlPanelState.topN = parseInt(value);
    
    // Atualizar display
    document.getElementById('top-n-value').textContent = 
        value >= 1000 ? 'TODOS' : value;
    
    if (!networkInstance || !nodesDataset) return;
    
    // Pegar todos os nós e ordenar por PageRank
    const allNodes = nodesDataset.get();
    allNodes.sort((a, b) => (b.pagerank || 0) - (a.pagerank || 0));
    
    // Top N nós
    const topNodeIds = new Set(allNodes.slice(0, parseInt(value)).map(n => n.id));
    
    // Atualizar visibilidade
    const nodesToUpdate = allNodes.map(node => ({
        id: node.id,
        hidden: !topNodeIds.has(node.id),
        // CRÍTICO: Preservar cor atual
        color: node.color
    }));
    
    nodesDataset.update(nodesToUpdate);
    
    // Filtrar arestas conectadas aos nós visíveis
    filterEdgesByVisibleNodes(topNodeIds);
    
    // Atualizar status
    updateFilterStatus();
    
    console.log(`Filtro Top N: ${value} nós visíveis`);
}

// Filtrar arestas por peso mínimo
function changeMinEdgeWeight(value) {
    controlPanelState.minEdgeWeight = parseInt(value);
    
    // Atualizar display
    document.getElementById('min-weight-value').textContent = value;
    
    if (!networkInstance || !edgesDataset) return;
    
    // Pegar nós visíveis
    const allNodes = nodesDataset.get();
    const visibleNodeIds = new Set(allNodes.filter(n => !n.hidden).map(n => n.id));
    
    // Atualizar arestas
    const allEdges = edgesDataset.get();
    const edgesToUpdate = allEdges.map(edge => ({
        id: edge.id,
        hidden: edge.weight < parseInt(value) || 
                !visibleNodeIds.has(edge.from) || 
                !visibleNodeIds.has(edge.to)
    }));
    
    edgesDataset.update(edgesToUpdate);
    
    // Atualizar status
    updateFilterStatus();
    
    console.log(`Filtro Peso Mínimo: ${value}`);
}

// Filtrar arestas baseado em nós visíveis
function filterEdgesByVisibleNodes(visibleNodeIds) {
    if (!edgesDataset) return;
    
    const allEdges = edgesDataset.get();
    const minWeight = controlPanelState.minEdgeWeight;
    
    const edgesToUpdate = allEdges.map(edge => ({
        id: edge.id,
        hidden: !visibleNodeIds.has(edge.from) || 
                !visibleNodeIds.has(edge.to) ||
                edge.weight < minWeight
    }));
    
    edgesDataset.update(edgesToUpdate);
}

// Resetar todos os filtros
function resetAllFilters() {
    // Resetar sliders
    document.getElementById('top-n-slider').value = 1000;
    document.getElementById('top-n-value').textContent = 'TODOS';
    document.getElementById('min-weight-slider').value = 1;
    document.getElementById('min-weight-value').textContent = '1';
    
    // Resetar state
    controlPanelState.topN = 10000;
    controlPanelState.minEdgeWeight = 1;
    
    if (!networkInstance || !nodesDataset || !edgesDataset) return;
    
    // Mostrar TODOS os nós e arestas
    const allNodes = nodesDataset.get();
    const allEdges = edgesDataset.get();

    nodesDataset.update(allNodes.map(n => ({
        id: n.id,
        hidden: false,
        // CRÍTICO: Preservar cor atual
        color: n.color
    })));
    edgesDataset.update(allEdges.map(e => ({ id: e.id, hidden: false })));
    
    // Atualizar status
    updateFilterStatus();
    
    console.log('Filtros resetados - exibindo TUDO');
}

// Atualizar status visual dos filtros
function updateFilterStatus() {
    if (!nodesDataset || !edgesDataset) return;
    
    const allNodes = nodesDataset.get();
    const allEdges = edgesDataset.get();
    
    const visibleNodes = allNodes.filter(n => !n.hidden).length;
    const visibleEdges = allEdges.filter(e => !e.hidden).length;
    
    // Atualizar contadores
    document.getElementById('visible-nodes-count').textContent = visibleNodes;
    document.getElementById('visible-edges-count').textContent = visibleEdges;
    
    // Mostrar/esconder status
    const statusDiv = document.getElementById('filter-status');
    if (visibleNodes < allNodes.length || visibleEdges < allEdges.length) {
        statusDiv.style.display = 'block';
    } else {
        statusDiv.style.display = 'none';
    }
}
