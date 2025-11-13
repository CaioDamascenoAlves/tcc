// Painel de Controle Unificado

let controlPanelState = {
    colorBy: 'Comunidade',
    colorScheme: 'default',
    edgeOpacity: 0.3,
    nodeSizeMin: 5,
    nodeSizeMax: 30,
    showLabels: true,
    physicsEnabled: false,
    gravity: -800,
    springLength: 150,
    springConstant: 0.04
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
    if (typeof setColorBy === 'function') {
        setColorBy(value);
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
    if (typeof setColorScheme === 'function') {
        setColorScheme(scheme);
    }
}

// Função removida - agora usa o color_manager centralizado

// Mudar opacidade das arestas
function changeEdgeOpacity(value) {
    controlPanelState.edgeOpacity = parseFloat(value);
    document.getElementById('edge-opacity-value').textContent = value;

    if (!networkInstance || !edgesDataset) return;

    const allEdges = edgesDataset.get();
    const edgesToUpdate = allEdges.map(edge => ({
        id: edge.id,
        color: {
            color: `rgba(200, 200, 200, ${value})`,
            opacity: parseFloat(value)
        }
    }));

    edgesDataset.update(edgesToUpdate);
}

// Mudar tamanho mínimo dos nós
function changeNodeSizeMin(value) {
    controlPanelState.nodeSizeMin = parseInt(value);
    document.getElementById('node-size-min-value').textContent = value;

    if (!networkInstance) return;

    networkInstance.setOptions({
        nodes: {
            scaling: {
                min: parseInt(value),
                max: controlPanelState.nodeSizeMax
            }
        }
    });
}

// Mudar tamanho máximo dos nós
function changeNodeSizeMax(value) {
    controlPanelState.nodeSizeMax = parseInt(value);
    document.getElementById('node-size-max-value').textContent = value;

    if (!networkInstance) return;

    networkInstance.setOptions({
        nodes: {
            scaling: {
                min: controlPanelState.nodeSizeMin,
                max: parseInt(value)
            }
        }
    });
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
        return {
            id: node.id,
            label: controlPanelState.showLabels ? (original?.label || '') : ''
        };
    });

    nodesDataset.update(nodesToUpdate);
}

// Toggle física do painel
function togglePhysicsFromPanel() {
    controlPanelState.physicsEnabled = !controlPanelState.physicsEnabled;

    const toggle = document.getElementById('physics-toggle');
    toggle.classList.toggle('active');

    if (!networkInstance) return;

    networkInstance.setOptions({
        physics: { enabled: controlPanelState.physicsEnabled }
    });

    // Sincronizar com botão externo
    if (typeof physicsEnabled !== 'undefined') {
        physicsEnabled = controlPanelState.physicsEnabled;
    }

    console.log('Physics:', controlPanelState.physicsEnabled);
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

// Inicializar painel com valores do config
function initControlPanel(config) {
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

    // Toggle switches
    if (controlPanelState.showLabels) {
        document.getElementById('labels-toggle').classList.add('active');
    }
    if (controlPanelState.physicsEnabled) {
        document.getElementById('physics-toggle').classList.add('active');
    }

    console.log('Control panel initialized with config:', controlPanelState);
}

// Abrir primeira seção por padrão
document.addEventListener('DOMContentLoaded', () => {
    const firstSection = document.querySelector('.drawer-section-header');
    if (firstSection) {
        firstSection.click();
    }
});

console.log('Control panel module loaded');
