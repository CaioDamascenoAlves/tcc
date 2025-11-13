// Sistema de Toast para Detalhes do Atleta
let currentAthleteId = null;
let currentAthleteData = null;
let networkInstance = null;
let nodesDataset = null;
let edgesDataset = null;
let allNodesData = [];

// Estado de highlight
let isHighlighted = false;
let originalColors = {}; // {nodeId: colorObj}
let originalEdgeColors = {}; // {edgeId: colorObj}
let lastFocusedRivalId = null; // Rastrear último rival focado para toggle

function setNetworkReference(network, nodes, edges, nodesData, edgesData) {
    networkInstance = network;
    nodesDataset = nodes;
    edgesDataset = edges;
    allNodesData = nodesData;

    console.log('Network reference set:', {
        nodes: nodes.length,
        edges: edges.length,
        dataNodes: nodesData.length
    });
}

function showAthleteToast(nodeId, nodeData) {
    currentAthleteId = nodeId;
    currentAthleteData = nodeData;

    const toast = document.getElementById('athlete-toast');
    const tooltipData = nodeData.tooltip_data || {};

    console.log('Showing toast for node:', nodeId, tooltipData);

    // Preencher informações básicas
    document.getElementById('toast-athlete-name').textContent = tooltipData.name || 'Atleta';
    document.getElementById('toast-noc').textContent = tooltipData.noc || 'N/A';
    document.getElementById('toast-team').textContent = tooltipData.team || 'N/A';
    document.getElementById('toast-years').textContent = tooltipData.years || 'N/A';
    document.getElementById('toast-age').textContent = tooltipData.age !== 'N/A' ? tooltipData.age : 'N/A';

    // Medalhas
    document.getElementById('toast-gold').textContent = tooltipData.medal_gold || 0;
    document.getElementById('toast-silver').textContent = tooltipData.medal_silver || 0;
    document.getElementById('toast-bronze').textContent = tooltipData.medal_bronze || 0;

    // Métricas
    document.getElementById('toast-pagerank').textContent = tooltipData.pagerank || '-';
    document.getElementById('toast-pagerank-percentile').textContent =
        tooltipData.pagerank_percentile ? `Top ${(100 - parseFloat(tooltipData.pagerank_percentile)).toFixed(1)}%` : '-';
    document.getElementById('toast-betweenness').textContent = tooltipData.betweenness || '-';
    document.getElementById('toast-degree-in').textContent = tooltipData.degree_in || 0;
    document.getElementById('toast-degree-out').textContent = tooltipData.degree_out || 0;
    document.getElementById('toast-community').textContent = tooltipData.community || 0;

    // Badge de atleta-ponte
    const bridgeBadge = document.getElementById('toast-bridge-badge');
    if (tooltipData.is_bridge) {
        bridgeBadge.innerHTML = '<span class="toast-badge">PONTE</span>';
    } else {
        bridgeBadge.innerHTML = '';
    }

    // Carregar lista de rivais
    loadRivalsList(nodeId);

    // Mostrar toast
    toast.classList.add('visible');

    // Tornar draggable
    makeToastDraggable();
}

function loadRivalsList(nodeId) {
    if (!edgesDataset || !nodesDataset) {
        console.warn('Datasets not ready');
        return;
    }

    console.log('Loading rivals for node:', nodeId);

    // Buscar arestas conectadas
    const allEdges = edgesDataset.get();
    const connectedEdges = allEdges.filter(edge =>
        edge.from === nodeId || edge.to === nodeId
    );

    console.log('Connected edges:', connectedEdges.length);

    if (connectedEdges.length === 0) {
        document.getElementById('toast-rivals-section').style.display = 'none';
        return;
    }

    // Buscar vizinhos
    const neighborIds = new Set();
    connectedEdges.forEach(edge => {
        neighborIds.add(edge.from === nodeId ? edge.to : edge.from);
    });

    console.log('Neighbors:', neighborIds.size);

    // Montar lista de rivais
    const rivals = [];
    neighborIds.forEach(id => {
        const node = nodesDataset.get(id);
        const edge = connectedEdges.find(e =>
            (e.from === nodeId && e.to === id) || (e.to === nodeId && e.from === id)
        );

        // CORREÇÃO: Buscar nome no tooltip_data dos dados originais
        const originalNode = allNodesData.find(n => n.id === id);
        const name = originalNode?.tooltip_data?.name || originalNode?.label || `Atleta ${id}`;

        rivals.push({
            id: id,
            name: name,
            weight: edge?.value || 1
        });
    });

    rivals.sort((a, b) => b.weight - a.weight);

    console.log('Rivals prepared:', rivals.length, rivals.slice(0, 3));

    // Renderizar
    const rivalsList = document.getElementById('toast-rivals-list');
    rivalsList.innerHTML = '';

    rivals.slice(0, 20).forEach(rival => {
        const item = document.createElement('div');
        item.className = 'toast-rival-item';
        item.innerHTML = `
            <span class="toast-rival-name">${rival.name}</span>
            <span class="toast-rival-weight">Peso: ${rival.weight}</span>
        `;
        item.style.cursor = 'pointer';
        item.onclick = () => focusOnNodeById(rival.id);
        rivalsList.appendChild(item);
    });

    document.getElementById('toast-rivals-count').textContent = neighborIds.size;
    document.getElementById('toast-rivals-section').style.display = 'block';
}

function closeAthleteToast() {
    const toast = document.getElementById('athlete-toast');
    toast.classList.remove('visible');

    if (isHighlighted) {
        restoreNetwork();
    }

    // Resetar estado de foco ao fechar toast
    lastFocusedRivalId = null;

    currentAthleteId = null;
    currentAthleteData = null;
}

function highlightRivals() {
    if (!currentAthleteId || !networkInstance || !nodesDataset || !edgesDataset) {
        console.error('Missing components');
        return;
    }

    console.log('highlightRivals called, current state:', isHighlighted);

    // Toggle: se já está destacado, restaura
    if (isHighlighted) {
        restoreNetwork();
        return;
    }

    // Encontrar vizinhos
    const allEdges = edgesDataset.get();
    const neighborIds = new Set([currentAthleteId]);

    allEdges.forEach(edge => {
        if (edge.from === currentAthleteId) {
            neighborIds.add(edge.to);
        } else if (edge.to === currentAthleteId) {
            neighborIds.add(edge.from);
        }
    });

    console.log('Highlighting', neighborIds.size, 'nodes');

    // CORREÇÃO: Usar batch update ao invés de updates individuais
    const allNodes = nodesDataset.get();
    const nodesToUpdate = [];

    allNodes.forEach(node => {
        // Guardar cor original
        if (!originalColors[node.id]) {
            originalColors[node.id] = node.color;
        }

        // Se NÃO é vizinho, esmaecer
        if (!neighborIds.has(node.id)) {
            nodesToUpdate.push({
                id: node.id,
                color: {
                    background: '#e0e0e0',
                    border: '#999999'
                }
            });
        }
    });

    // Batch update de nós
    if (nodesToUpdate.length > 0) {
        console.log('Updating', nodesToUpdate.length, 'nodes in batch');
        nodesDataset.update(nodesToUpdate);
    }

    // CORREÇÃO: Batch update de arestas
    const edgesToUpdate = [];

    allEdges.forEach(edge => {
        // Guardar cor original
        if (!originalEdgeColors[edge.id]) {
            originalEdgeColors[edge.id] = edge.color;
        }

        if (neighborIds.has(edge.from) && neighborIds.has(edge.to)) {
            // Destacar arestas entre vizinhos
            edgesToUpdate.push({
                id: edge.id,
                color: { color: '#8B2635' },
                width: 3
            });
        } else {
            // Esmaecer outras arestas
            edgesToUpdate.push({
                id: edge.id,
                color: { color: '#e0e0e0' },
                width: 1
            });
        }
    });

    // Batch update de arestas
    if (edgesToUpdate.length > 0) {
        console.log('Updating', edgesToUpdate.length, 'edges in batch');
        edgesDataset.update(edgesToUpdate);
    }

    isHighlighted = true;

    // Focar
    networkInstance.fit({
        nodes: Array.from(neighborIds),
        animation: { duration: 800 }
    });

    console.log('Highlight applied successfully');
}

function isolateSubnetwork() {
    if (!currentAthleteId || !networkInstance || !nodesDataset || !edgesDataset) {
        console.error('Missing components');
        return;
    }

    console.log('isolateSubnetwork called, current state:', isHighlighted);

    // Toggle
    if (isHighlighted) {
        restoreNetwork();
        return;
    }

    // Encontrar vizinhos
    const allEdges = edgesDataset.get();
    const neighborIds = new Set([currentAthleteId]);

    allEdges.forEach(edge => {
        if (edge.from === currentAthleteId) {
            neighborIds.add(edge.to);
        } else if (edge.to === currentAthleteId) {
            neighborIds.add(edge.from);
        }
    });

    console.log('Isolating', neighborIds.size, 'nodes');

    // CORREÇÃO: Batch update para esconder não-vizinhos
    const allNodes = nodesDataset.get();
    const nodesToHide = [];

    allNodes.forEach(node => {
        if (!neighborIds.has(node.id)) {
            nodesToHide.push({ id: node.id, hidden: true });
        }
    });

    if (nodesToHide.length > 0) {
        console.log('Hiding', nodesToHide.length, 'nodes in batch');
        nodesDataset.update(nodesToHide);
    }

    // CORREÇÃO: Batch update para esconder arestas não conectadas
    const edgesToHide = [];

    allEdges.forEach(edge => {
        const isConnected = neighborIds.has(edge.from) && neighborIds.has(edge.to);
        if (!isConnected) {
            edgesToHide.push({ id: edge.id, hidden: true });
        }
    });

    if (edgesToHide.length > 0) {
        console.log('Hiding', edgesToHide.length, 'edges in batch');
        edgesDataset.update(edgesToHide);
    }

    isHighlighted = true;

    networkInstance.fit({
        nodes: Array.from(neighborIds),
        animation: { duration: 800 }
    });

    console.log('Isolation applied successfully');
}

function focusOnNode() {
    if (!currentAthleteId || !networkInstance) {
        return;
    }

    // Resetar foco de rival ao usar botão centralizar
    lastFocusedRivalId = null;

    networkInstance.focus(currentAthleteId, {
        scale: 2.0,
        animation: { duration: 800 }
    });
    networkInstance.selectNodes([currentAthleteId]);
}

function focusOnNodeById(nodeId) {
    if (!networkInstance) return;

    console.log('focusOnNodeById called for:', nodeId, 'last focused:', lastFocusedRivalId);

    // Toggle: se clicar no mesmo rival novamente, restaurar zoom
    if (lastFocusedRivalId === nodeId) {
        console.log('Same rival clicked - restoring network view');
        networkInstance.fit({ animation: { duration: 800 } });
        networkInstance.unselectAll();
        lastFocusedRivalId = null;
    } else {
        // Focar em novo rival
        console.log('Focusing on new rival:', nodeId);
        networkInstance.focus(nodeId, {
            scale: 1.5,
            animation: { duration: 800 }
        });
        networkInstance.selectNodes([nodeId]);
        lastFocusedRivalId = nodeId;
    }
}

function restoreNetwork() {
    if (!nodesDataset || !edgesDataset) {
        return;
    }

    console.log('Restoring network...');

    // CORREÇÃO: Batch update para restaurar nós
    const allNodes = nodesDataset.get();
    const nodesToRestore = [];

    allNodes.forEach(node => {
        const updates = { id: node.id, hidden: false };

        if (originalColors[node.id]) {
            updates.color = originalColors[node.id];
        }

        nodesToRestore.push(updates);
    });

    if (nodesToRestore.length > 0) {
        console.log('Restoring', nodesToRestore.length, 'nodes in batch');
        nodesDataset.update(nodesToRestore);
    }

    // CORREÇÃO: Batch update para restaurar arestas
    const allEdges = edgesDataset.get();
    const edgesToRestore = [];

    allEdges.forEach(edge => {
        const updates = { id: edge.id, hidden: false, width: 1 };

        if (originalEdgeColors[edge.id]) {
            updates.color = originalEdgeColors[edge.id];
        } else {
            updates.color = { color: 'rgba(200, 200, 200, 0.3)' };
        }

        edgesToRestore.push(updates);
    });

    if (edgesToRestore.length > 0) {
        console.log('Restoring', edgesToRestore.length, 'edges in batch');
        edgesDataset.update(edgesToRestore);
    }

    originalColors = {};
    originalEdgeColors = {};
    isHighlighted = false;
    lastFocusedRivalId = null; // Resetar foco ao restaurar rede

    networkInstance.fit({ animation: { duration: 800 } });

    console.log('Network restored successfully');
}

// Draggable
let isDragging = false;
let dragOffsetX = 0;
let dragOffsetY = 0;

function makeToastDraggable() {
    const toast = document.getElementById('athlete-toast');
    const header = toast.querySelector('.toast-header');

    header.onmousedown = (e) => {
        if (e.target.classList.contains('toast-close-btn')) return;

        isDragging = true;
        const rect = toast.getBoundingClientRect();
        dragOffsetX = e.clientX - rect.left;
        dragOffsetY = e.clientY - rect.top;
        header.style.cursor = 'grabbing';
    };

    document.onmousemove = (e) => {
        if (!isDragging) return;

        const x = e.clientX - dragOffsetX;
        const y = e.clientY - dragOffsetY;

        toast.style.left = x + 'px';
        toast.style.top = y + 'px';
        toast.style.right = 'auto';
    };

    document.onmouseup = () => {
        if (isDragging) {
            isDragging = false;
            header.style.cursor = 'move';
        }
    };
}
