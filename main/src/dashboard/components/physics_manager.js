// Physics Manager - Gerenciador Centralizado de Física
// Sincroniza estado entre toolbar e painel de controle

let physicsState = {
    enabled: false,
    stabilizing: false,
    progress: 0
};

let physicsCallbacks = [];

// Inicializar gerenciador de física (exposta globalmente)
window.initPhysicsManager = function(initialState) {
    physicsState.enabled = initialState;
    console.log('Physics Manager initialized:', physicsState);
};

// Registrar callback para mudanças de estado
function onPhysicsChange(callback) {
    physicsCallbacks.push(callback);
}

// Obter estado atual
function getPhysicsState() {
    return { ...physicsState };
}

// Alterar estado da física (ÚNICO ponto de mudança)
function setPhysicsEnabled(enabled) {
    if (physicsState.enabled === enabled) {
        console.log('Physics state unchanged:', enabled);
        return;
    }

    physicsState.enabled = enabled;
    console.log('Physics state changed to:', enabled);

    // Aplicar na rede
    if (networkInstance) {
        networkInstance.setOptions({ physics: { enabled } });
    }

    // Notificar todos os componentes
    notifyPhysicsChange();
}

// Toggle da física (ÚNICA função global)
window.togglePhysics = function() {
    setPhysicsEnabled(!physicsState.enabled);
};

// Notificar todos os componentes registrados
function notifyPhysicsChange() {
    physicsCallbacks.forEach(callback => {
        try {
            callback(physicsState.enabled);
        } catch (error) {
            console.error('Error in physics callback:', error);
        }
    });
}

// Atualizar UI do botão da toolbar
function updateToolbarPhysicsButton(enabled) {
    const btn = document.getElementById('btn-toggle-physics');
    if (!btn) return;

    const btnSvg = btn.querySelector('svg');

    if (enabled) {
        btn.classList.add('active');
        btn.setAttribute('data-tooltip', 'Pausar Física');
        btnSvg.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>'; // PAUSE
    } else {
        btn.classList.remove('active');
        btn.setAttribute('data-tooltip', 'Ativar Física');
        btnSvg.innerHTML = '<path d="M8 5v14l11-7z"/>'; // PLAY
    }
}

// Atualizar UI do toggle do painel
function updatePanelPhysicsToggle(enabled) {
    const toggle = document.getElementById('physics-toggle');
    if (!toggle) return;

    if (enabled) {
        toggle.classList.add('active');
    } else {
        toggle.classList.remove('active');
    }
}

// Monitorar progresso de estabilização (exposta globalmente)
window.onStabilizationProgress = function(params) {
    if (!params) return;

    physicsState.stabilizing = true;
    physicsState.progress = Math.round((params.iterations / params.total) * 100);

    // Atualizar UI (se houver)
    updateStabilizationUI(physicsState.progress);
}

window.onStabilizationComplete = function() {
    physicsState.stabilizing = false;
    physicsState.progress = 100;

    console.log('Stabilization complete');

    // Esconder UI de progresso
    hideStabilizationUI();
};

// UI de progresso (placeholder)
function updateStabilizationUI(progress) {
    // TODO: Implementar barra de progresso visual
    if (progress % 10 === 0) {
        console.log(`Stabilization progress: ${progress}%`);
    }
}

function hideStabilizationUI() {
    // TODO: Esconder barra de progresso
}

console.log('Physics Manager module loaded');
