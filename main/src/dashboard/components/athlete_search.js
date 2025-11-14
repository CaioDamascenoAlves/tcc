// Sistema de Busca de Atletas

let searchIndex = []; // Lista de todos os atletas para busca
let selectedSuggestionIndex = -1;
let currentSuggestions = [];

// Inicializar índice de busca (exposta globalmente)
window.initSearchIndex = function(nodesData) {
    searchIndex = nodesData.map(node => ({
        id: node.id,
        name: node.tooltip_data?.name || node.label || `Atleta ${node.id}`,
        noc: node.tooltip_data?.noc || 'N/A',
        medals: node.tooltip_data?.medal_total || 0,
        pagerank: node.tooltip_data?.pagerank || '0'
    }));

    console.log('Search index initialized with', searchIndex.length, 'athletes');
};

// Buscar atletas
function searchAthletes(query) {
    if (!query || query.length < 2) {
        return [];
    }

    const lowerQuery = query.toLowerCase();

    // Buscar por nome (case insensitive)
    const results = searchIndex.filter(athlete =>
        athlete.name.toLowerCase().includes(lowerQuery)
    );

    // Ordenar por relevância (quanto mais cedo aparece a query, melhor)
    results.sort((a, b) => {
        const aIndex = a.name.toLowerCase().indexOf(lowerQuery);
        const bIndex = b.name.toLowerCase().indexOf(lowerQuery);

        if (aIndex !== bIndex) {
            return aIndex - bIndex;
        }

        // Se empatar, ordenar por número de medalhas
        return b.medals - a.medals;
    });

    return results.slice(0, 10); // Limitar a 10 resultados
}

// Renderizar sugestões
function renderSuggestions(suggestions) {
    const container = document.getElementById('search-suggestions');

    if (suggestions.length === 0) {
        container.innerHTML = '<div class="no-results">Nenhum atleta encontrado</div>';
        container.classList.add('visible');
        currentSuggestions = [];
        return;
    }

    currentSuggestions = suggestions;
    selectedSuggestionIndex = -1;

    container.innerHTML = suggestions.map((athlete, index) => `
        <div class="suggestion-item" data-index="${index}" data-athlete-id="${athlete.id}">
            <div class="suggestion-name">${highlightMatch(athlete.name, document.getElementById('athlete-search-input').value)}</div>
            <div class="suggestion-info">
                <span>${athlete.noc}</span>
                <span>🏅 ${athlete.medals}</span>
            </div>
        </div>
    `).join('');

    container.classList.add('visible');

    // Adicionar event listeners
    container.querySelectorAll('.suggestion-item').forEach(item => {
        item.addEventListener('click', function() {
            selectAthlete(this.dataset.athleteId);
        });

        item.addEventListener('mouseenter', function() {
            selectedSuggestionIndex = parseInt(this.dataset.index);
            updateSelectedSuggestion();
        });
    });
}

// Destacar texto que corresponde à busca
function highlightMatch(text, query) {
    if (!query) return text;

    const index = text.toLowerCase().indexOf(query.toLowerCase());
    if (index === -1) return text;

    const before = text.substring(0, index);
    const match = text.substring(index, index + query.length);
    const after = text.substring(index + query.length);

    return `${before}<strong>${match}</strong>${after}`;
}

// Selecionar atleta
function selectAthlete(athleteId) {
    console.log('Athlete selected:', athleteId);

    // Fechar dropdown
    hideSuggestions();

    // Limpar input
    document.getElementById('athlete-search-input').value = '';
    document.getElementById('clear-search').classList.remove('visible');

    // Buscar nó
    const node = nodesDataset.get(athleteId);

    if (!node) {
        console.error('Node not found:', athleteId);
        return;
    }

    // Mostrar toast
    showAthleteToast(athleteId, node);

    // Focar e dar zoom
    if (networkInstance) {
        networkInstance.focus(athleteId, {
            scale: 2.0,
            animation: { duration: 1000, easingFunction: 'easeInOutQuad' }
        });
        networkInstance.selectNodes([athleteId]);
    }
}

// Esconder sugestões
function hideSuggestions() {
    document.getElementById('search-suggestions').classList.remove('visible');
    currentSuggestions = [];
    selectedSuggestionIndex = -1;
}

// Atualizar sugestão selecionada (navegação por teclado)
function updateSelectedSuggestion() {
    const items = document.querySelectorAll('.suggestion-item');
    items.forEach((item, index) => {
        if (index === selectedSuggestionIndex) {
            item.classList.add('active');
            item.scrollIntoView({ block: 'nearest' });
        } else {
            item.classList.remove('active');
        }
    });
}

// Limpar busca
function clearSearch() {
    const input = document.getElementById('athlete-search-input');
    input.value = '';
    input.focus();
    hideSuggestions();
    document.getElementById('clear-search').classList.remove('visible');
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('athlete-search-input');
    const clearBtn = document.getElementById('clear-search');

    // Input change
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.trim();

        // Mostrar/esconder botão limpar
        if (query.length > 0) {
            clearBtn.classList.add('visible');
        } else {
            clearBtn.classList.remove('visible');
        }

        // Buscar
        if (query.length >= 2) {
            const results = searchAthletes(query);
            renderSuggestions(results);
        } else {
            hideSuggestions();
        }
    });

    // Navegação por teclado
    searchInput.addEventListener('keydown', function(e) {
        const suggestionsVisible = document.getElementById('search-suggestions').classList.contains('visible');

        if (!suggestionsVisible || currentSuggestions.length === 0) {
            if (e.key === 'Escape') {
                clearSearch();
            }
            return;
        }

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, currentSuggestions.length - 1);
                updateSelectedSuggestion();
                break;

            case 'ArrowUp':
                e.preventDefault();
                selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, 0);
                updateSelectedSuggestion();
                break;

            case 'Enter':
                e.preventDefault();
                if (selectedSuggestionIndex >= 0 && selectedSuggestionIndex < currentSuggestions.length) {
                    selectAthlete(currentSuggestions[selectedSuggestionIndex].id);
                }
                break;

            case 'Escape':
                e.preventDefault();
                hideSuggestions();
                break;
        }
    });

    // Fechar ao clicar fora
    document.addEventListener('click', function(e) {
        const container = document.getElementById('athlete-search-container');
        if (!container.contains(e.target)) {
            hideSuggestions();
        }
    });

    console.log('Athlete search initialized');
});

// Atalho de teclado: Ctrl+K ou Cmd+K para focar na busca
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('athlete-search-input').focus();
    }
});

console.log('Athlete search ready');
console.log('Keyboard shortcut: Ctrl+K or Cmd+K to focus search');
