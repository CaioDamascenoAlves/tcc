// Gerenciador Central de Cores - Sincronização Total

let currentColorBy = 'Comunidade';
let currentColorScheme = 'default';
let currentPalette = [];

// Paletas de cores (mesmas do control_panel.js)
const COLOR_SCHEMES = {
    'default': ['#8B2635', '#2E5A88', '#2A7F62', '#D4A017', '#8B4513', '#4B0082', '#008B8B', '#B8860B',
               '#CD5C5C', '#4682B4', '#9ACD32', '#FF8C00', '#8A2BE2', '#20B2AA', '#CD853F', '#9370DB'],
    'pastel': ['#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#E0BBE4', '#FFDFD3', '#C9E4DE',
              '#FFC8DD', '#BDE0FE', '#A2D2FF', '#CDB4DB', '#FEC89A', '#F1FAEE', '#A8DADC', '#E5989B'],
    'vibrant': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
               '#F8B195', '#F67280', '#C06C84', '#6C5B7B', '#355C7D', '#99B898', '#FECEAB', '#FF847C'],
    'cool': ['#1A535C', '#4ECDC4', '#F7FFF7', '#FF6B6B', '#FFE66D', '#2E86AB', '#A23B72', '#F18F01',
            '#C73E1D', '#6A994E', '#BC4749', '#F2CC8F', '#81B29A', '#3D405B', '#E07A5F', '#F4F1DE']
};

// Inicializar gerenciador de cores (exposta globalmente)
window.initColorManager = function(colorBy, colorScheme) {
    currentColorBy = colorBy || 'Comunidade';
    currentColorScheme = colorScheme || 'default';
    currentPalette = COLOR_SCHEMES[currentColorScheme];

    console.log('Color Manager initialized:', { colorBy: currentColorBy, colorScheme: currentColorScheme });
};

// Obter cor para um nó específico
window.getNodeColor = function(node) {
    const palette = currentPalette;
    let color;

    if (currentColorBy === 'Comunidade') {
        const community = node.group || 0;
        color = palette[community % palette.length];
    } else if (currentColorBy === 'País (NOC)') {
        const noc = node.tooltip_data?.noc || 'Unknown';
        const hashCode = noc.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
        color = palette[hashCode % palette.length];
    } else if (currentColorBy === 'Década') {
        const years = node.tooltip_data?.years_list || [];
        const decade = years.length > 0 ? Math.floor(years[0] / 10) * 10 : 2000;
        color = palette[Math.floor(decade / 10) % palette.length];
    } else if (currentColorBy === 'Tipo de Medalha') {
        const gold = node.tooltip_data?.medal_gold || 0;
        const silver = node.tooltip_data?.medal_silver || 0;
        const bronze = node.tooltip_data?.medal_bronze || 0;

        let medalType = 'Bronze';
        if (gold >= silver && gold >= bronze) medalType = 'Gold';
        else if (silver >= gold && silver >= bronze) medalType = 'Silver';

        color = medalType === 'Gold' ? palette[0] : medalType === 'Silver' ? palette[1] : palette[2];
    }

    return color;
};

// Obter chave de agrupamento para um nó (para legenda)
window.getNodeGroupKey = function(node) {
    if (currentColorBy === 'Comunidade') {
        return String(node.group || 0);
    } else if (currentColorBy === 'País (NOC)') {
        return node.tooltip_data?.noc || 'Unknown';
    } else if (currentColorBy === 'Década') {
        const years = node.tooltip_data?.years_list || [];
        return String(years.length > 0 ? Math.floor(years[0] / 10) * 10 : 2000);
    } else if (currentColorBy === 'Tipo de Medalha') {
        const gold = node.tooltip_data?.medal_gold || 0;
        const silver = node.tooltip_data?.medal_silver || 0;
        const bronze = node.tooltip_data?.medal_bronze || 0;

        if (gold >= silver && gold >= bronze) return 'Gold';
        if (silver >= gold && silver >= bronze) return 'Silver';
        return 'Bronze';
    }
};

// Obter label para chave de grupo
window.getGroupLabel = function(groupKey) {
    if (currentColorBy === 'Comunidade') {
        return `Comunidade ${groupKey}`;
    } else if (currentColorBy === 'País (NOC)') {
        return groupKey;
    } else if (currentColorBy === 'Década') {
        return `${groupKey}s`;
    } else if (currentColorBy === 'Tipo de Medalha') {
        return groupKey === 'Gold' ? '🥇 Ouro' : groupKey === 'Silver' ? '🥈 Prata' : '🥉 Bronze';
    }
};

// Mudar esquema de cores (ÚNICO ponto de mudança)
window.setColorScheme = function(scheme) {
    if (!COLOR_SCHEMES[scheme]) {
        console.error('Invalid color scheme:', scheme);
        return;
    }

    currentColorScheme = scheme;
    currentPalette = COLOR_SCHEMES[scheme];

    console.log('Color scheme changed to:', scheme);

    // Aplicar em todos os componentes
    applyColorsToNetwork();
    updateLegendColors();
};

// Mudar tipo de coloração (ÚNICO ponto de mudança)
window.setColorBy = function(colorBy) {
    const validOptions = ['Comunidade', 'País (NOC)', 'Década', 'Tipo de Medalha'];
    if (!validOptions.includes(colorBy)) {
        console.error('Invalid color by:', colorBy);
        return;
    }

    currentColorBy = colorBy;

    console.log('Color by changed to:', colorBy);

    // Aplicar em todos os componentes
    applyColorsToNetwork();
    rebuildLegend();
};

// Aplicar cores na rede
function applyColorsToNetwork() {
    if (!networkInstance || !nodesDataset || !allNodesData) {
        console.warn('Network not ready for color application');
        return;
    }

    const allNodes = nodesDataset.get();
    const nodesToUpdate = [];

    allNodes.forEach(node => {
        const originalNode = allNodesData.find(n => n.id === node.id);
        if (!originalNode) return;

        const color = getNodeColor(originalNode);

        nodesToUpdate.push({
            id: node.id,
            color: {
                background: color,
                border: '#000000',
                highlight: {
                    background: '#8B2635',
                    border: '#FF0000'
                }
            }
        });
    });

    nodesDataset.update(nodesToUpdate);
    console.log('Network colors updated:', nodesToUpdate.length, 'nodes');
}

// Atualizar cores na legenda existente
function updateLegendColors() {
    if (typeof window.initCommunityLegend === 'function' && allNodesData) {
        window.initCommunityLegend(allNodesData, currentPalette);
    }
}

// Reconstruir legenda (quando muda o tipo de coloração)
function rebuildLegend() {
    if (typeof window.initCommunityLegend === 'function' && allNodesData) {
        window.initCommunityLegend(allNodesData, currentPalette);
    }
}

// Obter estado atual
window.getColorState = function() {
    return {
        colorBy: currentColorBy,
        colorScheme: currentColorScheme,
        palette: currentPalette
    };
};

console.log('Color Manager module loaded');
