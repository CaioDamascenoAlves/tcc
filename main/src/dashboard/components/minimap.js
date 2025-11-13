// Mini-mapa da Rede

let minimapEnabled = true;
let minimapCanvas = null;
let minimapCtx = null;
let minimapViewport = null;
let networkBounds = null;
let minimapUpdateInterval = null;

// Inicializar mini-mapa
function initMinimap() {
    if (!networkInstance) {
        console.error('Network instance not available for minimap');
        return;
    }

    minimapCanvas = document.getElementById('minimap-canvas');
    minimapCtx = minimapCanvas.getContext('2d');
    minimapViewport = document.getElementById('minimap-viewport');

    // Ajustar tamanho do canvas
    const container = document.getElementById('minimap-container');
    minimapCanvas.width = container.clientWidth;
    minimapCanvas.height = container.clientHeight;

    console.log('Minimap initialized:', minimapCanvas.width, 'x', minimapCanvas.height);

    // Click no minimap para navegar
    minimapCanvas.addEventListener('click', handleMinimapClick);

    // Renderizar completamente a cada 2 segundos (para atualizar posições quando física está ativa)
    minimapUpdateInterval = setInterval(renderMinimap, 2000);

    // Atualizar viewport a cada 100ms (suave)
    setInterval(updateMinimapViewport, 100);

    // Primeira renderização
    renderMinimap();
}

// Renderizar mini-mapa
function renderMinimap() {
    if (!networkInstance || !minimapCtx || !minimapEnabled) {
        return;
    }

    try {
        const positions = networkInstance.getPositions();
        const nodeIds = nodesDataset ? nodesDataset.getIds() : Object.keys(positions);

        if (nodeIds.length === 0) {
            return;
        }

        // Calcular bounds da rede
        let minX = Infinity, maxX = -Infinity;
        let minY = Infinity, maxY = -Infinity;
        let validNodes = 0;

        nodeIds.forEach(id => {
            const pos = positions[id];
            if (pos && typeof pos.x === 'number' && typeof pos.y === 'number') {
                minX = Math.min(minX, pos.x);
                maxX = Math.max(maxX, pos.x);
                minY = Math.min(minY, pos.y);
                maxY = Math.max(maxY, pos.y);
                validNodes++;
            }
        });

        if (validNodes === 0 || !isFinite(minX) || !isFinite(maxX)) {
            return;
        }

        // Adicionar margem aos bounds para melhor visualização
        const marginX = (maxX - minX) * 0.1;
        const marginY = (maxY - minY) * 0.1;
        minX -= marginX;
        maxX += marginX;
        minY -= marginY;
        maxY += marginY;

        networkBounds = { minX, maxX, minY, maxY };

        const networkWidth = maxX - minX;
        const networkHeight = maxY - minY;

        // Limpar canvas
        minimapCtx.clearRect(0, 0, minimapCanvas.width, minimapCanvas.height);

        // Desenhar background
        minimapCtx.fillStyle = '#f8f9fa';
        minimapCtx.fillRect(0, 0, minimapCanvas.width, minimapCanvas.height);

        // Calcular escala
        const padding = 10;
        const scaleX = (minimapCanvas.width - 2 * padding) / networkWidth;
        const scaleY = (minimapCanvas.height - 2 * padding) / networkHeight;
        const scale = Math.min(scaleX, scaleY);

        // Função para converter coordenadas da rede para minimap
        function toMinimapCoords(x, y) {
            return {
                x: padding + (x - minX) * scale,
                y: padding + (y - minY) * scale
            };
        }

        // Desenhar arestas (simplificado - só algumas)
        if (edgesDataset) {
            minimapCtx.strokeStyle = 'rgba(200, 200, 200, 0.3)';
            minimapCtx.lineWidth = 0.5;

            try {
                const edges = edgesDataset.get();
                // Desenhar apenas 1 a cada 5 arestas para performance
                edges.filter((_, i) => i % 5 === 0).forEach(edge => {
                    const fromPos = positions[edge.from];
                    const toPos = positions[edge.to];

                    if (fromPos && toPos) {
                        const from = toMinimapCoords(fromPos.x, fromPos.y);
                        const to = toMinimapCoords(toPos.x, toPos.y);

                        minimapCtx.beginPath();
                        minimapCtx.moveTo(from.x, from.y);
                        minimapCtx.lineTo(to.x, to.y);
                        minimapCtx.stroke();
                    }
                });
            } catch (e) {
                console.warn('Could not draw minimap edges:', e);
            }
        }

        // Desenhar nós
        minimapCtx.fillStyle = '#8B2635';
        nodeIds.forEach(id => {
            const pos = positions[id];
            if (pos && typeof pos.x === 'number' && typeof pos.y === 'number') {
                const miniPos = toMinimapCoords(pos.x, pos.y);

                minimapCtx.beginPath();
                minimapCtx.arc(miniPos.x, miniPos.y, 1.5, 0, 2 * Math.PI);
                minimapCtx.fill();
            }
        });

        // Desenhar viewport atual
        updateMinimapViewport();

    } catch (error) {
        console.error('Error rendering minimap:', error);
    }
}

// Atualizar posição do viewport no minimap
function updateMinimapViewport() {
    if (!networkInstance || !minimapViewport || !networkBounds || !minimapEnabled) {
        return;
    }

    try {
        const viewPosition = networkInstance.getViewPosition();
        const scale = networkInstance.getScale();

        const { minX, maxX, minY, maxY } = networkBounds;
        const networkWidth = maxX - minX;
        const networkHeight = maxY - minY;

        // Obter tamanho do container da rede
        const container = document.getElementById('cosmograph');
        if (!container) return;

        const canvasWidth = container.clientWidth;
        const canvasHeight = container.clientHeight;

        // Tamanho da área visível no espaço da rede
        // Ajustar baseado no scale real da vis-network (que é invertido)
        const visibleWidth = (canvasWidth / scale) * 0.5;
        const visibleHeight = (canvasHeight / scale) * 0.5;

        // Posição do centro da visualização
        const centerX = viewPosition.x;
        const centerY = viewPosition.y;

        // Bounds da área visível
        const viewMinX = centerX - visibleWidth / 2;
        const viewMaxX = centerX + visibleWidth / 2;
        const viewMinY = centerY - visibleHeight / 2;
        const viewMaxY = centerY + visibleHeight / 2;

        // Converter para coordenadas do minimap
        const padding = 10;
        const minimapScaleX = (minimapCanvas.width - 2 * padding) / networkWidth;
        const minimapScaleY = (minimapCanvas.height - 2 * padding) / networkHeight;
        const minimapScale = Math.min(minimapScaleX, minimapScaleY);

        const vpLeft = padding + (viewMinX - minX) * minimapScale;
        const vpTop = padding + (viewMinY - minY) * minimapScale;
        const vpWidth = visibleWidth * minimapScale;
        const vpHeight = visibleHeight * minimapScale;

        // Atualizar elemento do viewport
        minimapViewport.style.left = Math.max(0, vpLeft) + 'px';
        minimapViewport.style.top = Math.max(0, vpTop) + 'px';
        minimapViewport.style.width = Math.min(vpWidth, minimapCanvas.width) + 'px';
        minimapViewport.style.height = Math.min(vpHeight, minimapCanvas.height) + 'px';

    } catch (error) {
        console.error('Error updating minimap viewport:', error);
    }
}

// Atualizar minimap periodicamente
function updateMinimap() {
    if (minimapEnabled) {
        updateMinimapViewport();
    }
}

// Click no minimap para navegar
function handleMinimapClick(e) {
    if (!networkInstance || !networkBounds) {
        return;
    }

    const rect = minimapCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Converter coordenadas do minimap para coordenadas da rede
    const { minX, maxX, minY, maxY } = networkBounds;
    const networkWidth = maxX - minX;
    const networkHeight = maxY - minY;

    const padding = 10;
    const minimapScaleX = (minimapCanvas.width - 2 * padding) / networkWidth;
    const minimapScaleY = (minimapCanvas.height - 2 * padding) / networkHeight;
    const minimapScale = Math.min(minimapScaleX, minimapScaleY);

    const networkX = minX + (x - padding) / minimapScale;
    const networkY = minY + (y - padding) / minimapScale;

    // Mover visualização para essa posição
    networkInstance.moveTo({
        position: { x: networkX, y: networkY },
        animation: {
            duration: 500,
            easingFunction: 'easeInOutQuad'
        }
    });

    console.log('Minimap clicked - moving to:', networkX, networkY);
}

// Toggle minimap (minimizar/maximizar)
function toggleMinimap() {
    const container = document.getElementById('minimap-container');
    const btn = document.getElementById('minimap-toggle');

    if (container.classList.contains('minimized')) {
        // Expandir
        container.classList.remove('minimized');
        btn.textContent = '−';
        minimapEnabled = true;

        // Reajustar canvas
        setTimeout(() => {
            minimapCanvas.width = container.clientWidth;
            minimapCanvas.height = container.clientHeight;
            renderMinimap();
        }, 100);

        console.log('Minimap expanded');
    } else {
        // Minimizar
        container.classList.add('minimized');
        btn.textContent = '🗺️';
        minimapEnabled = false;

        console.log('Minimap minimized');
    }
}

console.log('Minimap module loaded');
