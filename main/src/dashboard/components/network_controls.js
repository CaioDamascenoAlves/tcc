// Controles de Visualização da Rede

let physicsEnabled = null; // Será inicializado com o valor da config
let isFullscreen = false;

function resetZoom() {
    if (!networkInstance) {
        console.error('Network instance not available');
        return;
    }

    console.log('Reset zoom triggered');

    // Restaurar highlight se estiver ativo
    if (isHighlighted) {
        restoreNetwork();
    } else {
        // Apenas dar fit na rede
        networkInstance.fit({
            animation: {
                duration: 1000,
                easingFunction: 'easeInOutQuad'
            }
        });
    }

    // Remover seleção
    networkInstance.unselectAll();
    lastFocusedRivalId = null;

    console.log('Zoom reset complete');
}

function togglePhysics() {
    if (!networkInstance) {
        console.error('Network instance not available');
        return;
    }

    physicsEnabled = !physicsEnabled;

    console.log('Toggling physics to:', physicsEnabled);

    const btn = document.getElementById('btn-toggle-physics');
    const btnSvg = btn.querySelector('svg');

    if (physicsEnabled) {
        // Ativar física
        networkInstance.setOptions({ physics: { enabled: true } });
        btn.classList.add('active');
        btn.setAttribute('data-tooltip', 'Pausar Física');

        // Mudar ícone para "pause" (duas barras verticais)
        btnSvg.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>';

        console.log('Physics enabled - icon set to PAUSE');
    } else {
        // Desativar física
        networkInstance.setOptions({ physics: { enabled: false } });
        btn.classList.remove('active');
        btn.setAttribute('data-tooltip', 'Ativar Física');

        // Mudar ícone para "play" (triângulo)
        btnSvg.innerHTML = '<path d="M8 5v14l11-7z"/>';

        console.log('Physics disabled - icon set to PLAY');
    }
}

// Inicializar estado do botão de física baseado na config
function initPhysicsButton(initialPhysicsState) {
    physicsEnabled = initialPhysicsState;

    const btn = document.getElementById('btn-toggle-physics');
    const btnSvg = btn.querySelector('svg');

    console.log('Initializing physics button with state:', physicsEnabled);

    if (physicsEnabled) {
        btn.classList.add('active');
        btn.setAttribute('data-tooltip', 'Pausar Física');
        btnSvg.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>'; // PAUSE
    } else {
        btn.classList.remove('active');
        btn.setAttribute('data-tooltip', 'Ativar Física');
        btnSvg.innerHTML = '<path d="M8 5v14l11-7z"/>'; // PLAY
    }
}

function takeScreenshot() {
    if (!networkInstance) {
        console.error('Network instance not available');
        return;
    }

    console.log('Taking screenshot...');

    try {
        // Pegar o canvas da rede
        const canvas = document.querySelector('#cosmograph canvas');

        if (!canvas) {
            console.error('Canvas not found');
            alert('Erro: Canvas da rede não encontrado');
            return;
        }

        // Converter para blob e fazer download
        canvas.toBlob(function(blob) {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');

            // Gerar nome do arquivo com timestamp
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            link.download = `rede-olimpica-${timestamp}.png`;

            link.href = url;
            link.click();

            // Limpar URL
            setTimeout(() => URL.revokeObjectURL(url), 100);

            console.log('Screenshot saved successfully');

            // Feedback visual
            flashControl('btn-screenshot');
        }, 'image/png');

    } catch (error) {
        console.error('Error taking screenshot:', error);
        alert('Erro ao capturar screenshot: ' + error.message);
    }
}

function toggleFullscreen() {
    const container = document.getElementById('cosmograph').parentElement;

    if (!document.fullscreenElement) {
        // Entrar em fullscreen
        if (container.requestFullscreen) {
            container.requestFullscreen();
        } else if (container.webkitRequestFullscreen) {
            container.webkitRequestFullscreen();
        } else if (container.msRequestFullscreen) {
            container.msRequestFullscreen();
        }

        isFullscreen = true;
        updateFullscreenButton(true);
        console.log('Entered fullscreen');

    } else {
        // Sair de fullscreen
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }

        isFullscreen = false;
        updateFullscreenButton(false);
        console.log('Exited fullscreen');
    }
}

function updateFullscreenButton(isFullscreen) {
    const btn = document.getElementById('btn-fullscreen');
    const btnSvg = btn.querySelector('svg');

    if (isFullscreen) {
        btn.classList.add('active');
        btn.setAttribute('data-tooltip', 'Sair de Tela Cheia');
        // Ícone de "exit fullscreen"
        btnSvg.innerHTML = '<path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>';
    } else {
        btn.classList.remove('active');
        btn.setAttribute('data-tooltip', 'Tela Cheia');
        // Ícone de "enter fullscreen"
        btnSvg.innerHTML = '<path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>';
    }
}

// Listener para detectar saída de fullscreen via ESC
document.addEventListener('fullscreenchange', function() {
    if (!document.fullscreenElement) {
        isFullscreen = false;
        updateFullscreenButton(false);
    }
});

document.addEventListener('webkitfullscreenchange', function() {
    if (!document.webkitFullscreenElement) {
        isFullscreen = false;
        updateFullscreenButton(false);
    }
});

// Feedback visual para botões
function flashControl(buttonId) {
    const btn = document.getElementById(buttonId);
    btn.classList.add('active');
    setTimeout(() => btn.classList.remove('active'), 300);
}

// Atalhos de teclado
document.addEventListener('keydown', function(e) {
    // ESC - Reset zoom
    if (e.key === 'Escape' && !document.getElementById('athlete-toast').classList.contains('visible')) {
        resetZoom();
    }

    // F - Fullscreen
    if (e.key === 'f' || e.key === 'F') {
        if (!e.target.matches('input, textarea')) {
            e.preventDefault();
            toggleFullscreen();
        }
    }

    // P - Physics toggle
    if (e.key === 'p' || e.key === 'P') {
        if (!e.target.matches('input, textarea')) {
            e.preventDefault();
            togglePhysics();
        }
    }

    // S - Screenshot
    if (e.key === 's' || e.key === 'S') {
        if (!e.target.matches('input, textarea') && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            takeScreenshot();
        }
    }
});

console.log('Network controls initialized');
console.log('Keyboard shortcuts:');
console.log('  - ESC: Reset zoom');
console.log('  - F: Toggle fullscreen');
console.log('  - P: Toggle physics');
console.log('  - Ctrl+S: Screenshot');
