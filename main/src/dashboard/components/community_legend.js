// Sistema de Legenda Dinâmica (Comunidades, NOC, Década, Medalha)

let legendData = [];
let activeLegendItems = new Set();
let legendInitialized = false;
let currentColorBy = 'Comunidade';

// Inicializar legenda com dados
function initCommunityLegend(nodesData, colorPalette) {
    // Obter estado atual do color manager
    const colorState = typeof getColorState === 'function' ? getColorState() : null;
    if (colorState) {
        currentColorBy = colorState.colorBy;
        colorPalette = colorState.palette;
    } else {
        currentColorBy = window.config?.colorBy || 'Comunidade';
    }

    // Agregar dados baseado no esquema de cores usando color_manager
    const itemMap = {};

    nodesData.forEach(node => {
        // Usar color_manager para obter chave, label e cor
        const itemKey = typeof getNodeGroupKey === 'function' ? getNodeGroupKey(node) : String(node.group || 0);
        const itemLabel = typeof getGroupLabel === 'function' ? getGroupLabel(itemKey) : `Item ${itemKey}`;
        const itemColor = typeof getNodeColor === 'function' ? getNodeColor(node) : colorPalette[0];

        if (!itemMap[itemKey]) {
            itemMap[itemKey] = {
                id: String(itemKey),
                label: itemLabel,
                color: itemColor,
                count: 0,
                nodes: []
            };
        }
        itemMap[itemKey].count++;
        itemMap[itemKey].nodes.push(node.id);
    });

    // Converter para array e ordenar
    legendData = Object.values(itemMap).sort((a, b) => b.count - a.count);

    // Limitar a 20 items para NOC (são muitos países)
    if (currentColorBy === 'País (NOC)' && legendData.length > 20) {
        legendData = legendData.slice(0, 20);
    }

    // Renderizar legenda
    renderLegend();

    legendInitialized = true;
    console.log('Legend initialized:', currentColorBy, legendData.length, 'items');
}

// Renderizar items da legenda
function renderLegend() {
    const container = document.getElementById('legend-items');
    const legendTitle = document.querySelector('.legend-title span');

    // Atualizar título
    if (legendTitle) {
        legendTitle.textContent = currentColorBy === 'País (NOC)' ? 'Países (NOC)' : currentColorBy === 'Década' ? 'Décadas' : currentColorBy === 'Tipo de Medalha' ? 'Medalhas' : 'Comunidades';
    }

    container.innerHTML = legendData.map((item, index) => {
        // Escapar aspas no ID para uso seguro no onclick
        const itemIdEscaped = String(item.id).replace(/'/g, "\\'");
        return `
            <div class="legend-item" data-item-id="${item.id}" onclick="toggleLegendItem(\`${itemIdEscaped}\`)">
                <div class="legend-color-box" style="background-color: ${item.color}; border-color: ${item.color};"></div>
                <div class="legend-info">
                    <div class="legend-community-name">${item.label}</div>
                    <div class="legend-community-count">${item.count} atletas</div>
                </div>
            </div>
        `;
    }).join('');
}

// Toggle visibilidade de um item
function toggleLegendItem(itemId) {
    if (!networkInstance || !nodesDataset) return;

    // Converter para string para comparação consistente
    itemId = String(itemId);

    const legendItem = document.querySelector(`.legend-item[data-item-id="${itemId}"]`);

    if (!legendItem) {
        console.error('Legend item not found:', itemId);
        return;
    }

    // Se o item já está ativo, desativar
    if (activeLegendItems.has(itemId)) {
        activeLegendItems.delete(itemId);
        legendItem.classList.remove('active');

        // Se não há items ativos, mostrar todas
        if (activeLegendItems.size === 0) {
            resetLegendFilter();
        } else {
            updateNetworkVisibilityByLegend();
        }
    } else {
        // Ativar item
        activeLegendItems.add(itemId);
        legendItem.classList.add('active');
        updateNetworkVisibilityByLegend();
    }

    console.log('Active items:', Array.from(activeLegendItems));
}

// Atualizar visibilidade da rede baseado em items ativos
function updateNetworkVisibilityByLegend() {
    if (!networkInstance || !nodesDataset || !edgesDataset) return;

    const allNodes = nodesDataset.get();
    const allEdges = edgesDataset.get();

    // Se nenhum item está ativo, mostrar todas
    if (activeLegendItems.size === 0) {
        resetLegendFilter();
        return;
    }

    // Coletar IDs dos nós dos items ativos
    const activeNodeIds = new Set();
    legendData.forEach(item => {
        if (activeLegendItems.has(item.id)) {
            item.nodes.forEach(nodeId => activeNodeIds.add(nodeId));
        }
    });

    // Batch update para performance
    const nodesToUpdate = [];
    const edgesToUpdate = [];

    // Atualizar nós
    allNodes.forEach(node => {
        const isActive = activeNodeIds.has(node.id);
        nodesToUpdate.push({
            id: node.id,
            hidden: !isActive
        });
    });

    // Atualizar arestas (esconder se ambos os nós não estão ativos)
    allEdges.forEach(edge => {
        const bothActive = activeNodeIds.has(edge.from) && activeNodeIds.has(edge.to);
        edgesToUpdate.push({
            id: edge.id,
            hidden: !bothActive
        });
    });

    // Aplicar updates em batch
    nodesDataset.update(nodesToUpdate);
    edgesDataset.update(edgesToUpdate);

    // Atualizar estado visual dos items da legenda
    updateLegendItemsVisibility();

    // Fit na visualização
    setTimeout(() => {
        networkInstance.fit({
            animation: { duration: 500, easingFunction: 'easeInOutQuad' }
        });
    }, 100);
}

// Atualizar estado visual dos items da legenda
function updateLegendItemsVisibility() {
    document.querySelectorAll('.legend-item').forEach(item => {
        const itemId = item.dataset.itemId;

        if (activeLegendItems.size === 0) {
            item.classList.remove('dimmed');
        } else if (activeLegendItems.has(itemId)) {
            item.classList.remove('dimmed');
        } else {
            item.classList.add('dimmed');
        }
    });
}

// Mostrar todos os items
function showAllCommunities() {
    // Ativar todos
    activeLegendItems.clear();
    legendData.forEach(item => activeLegendItems.add(item.id));

    // Atualizar UI
    document.querySelectorAll('.legend-item').forEach(item => {
        item.classList.add('active');
        item.classList.remove('dimmed');
    });

    // Mostrar todos os nós
    resetLegendFilter();

    console.log('Showing all items');
}

// Limpar filtro (com dois nomes para compatibilidade)
function resetCommunityFilter() {
    if (!networkInstance || !nodesDataset || !edgesDataset) return;

    // Limpar items ativos
    activeLegendItems.clear();

    // Mostrar todos os nós e arestas
    const allNodes = nodesDataset.get();
    const allEdges = edgesDataset.get();

    const nodesToUpdate = allNodes.map(node => ({ id: node.id, hidden: false }));
    const edgesToUpdate = allEdges.map(edge => ({ id: edge.id, hidden: false }));

    nodesDataset.update(nodesToUpdate);
    edgesDataset.update(edgesToUpdate);

    // Limpar estado visual
    document.querySelectorAll('.legend-item').forEach(item => {
        item.classList.remove('active');
        item.classList.remove('dimmed');
    });

    // Fit na visualização
    setTimeout(() => {
        networkInstance.fit({
            animation: { duration: 500, easingFunction: 'easeInOutQuad' }
        });
    }, 100);

    console.log('Legend filter reset');
}

// Alias
const resetLegendFilter = resetCommunityFilter;

// Toggle minimizar/maximizar legenda
function toggleLegend() {
    const legend = document.getElementById('community-legend');
    const btn = document.querySelector('.legend-toggle-btn');

    if (legend.classList.contains('minimized')) {
        // Expandir
        legend.classList.remove('minimized');
        btn.textContent = '−';
        console.log('Legend expanded');
    } else {
        // Minimizar
        legend.classList.add('minimized');
        btn.innerHTML = '🏷️';
        console.log('Legend minimized');
    }
}

console.log('Community legend module loaded');
