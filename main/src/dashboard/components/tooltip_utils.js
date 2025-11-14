// Utilitários para criar tooltips ricos
window.createRichTooltip = function(data) {
    if (!data.tooltip_data) {
        return data.label || 'Atleta';
    }

    const d = data.tooltip_data;

    let tooltip = `<div style="font-family: Arial, sans-serif; padding: 8px; max-width: 300px;">`;

    // Cabeçalho com nome
    tooltip += `<div style="font-weight: bold; font-size: 14px; margin-bottom: 8px; border-bottom: 2px solid #8B2635; padding-bottom: 4px;">${d.name}</div>`;

    // Informações gerais
    tooltip += `<div style="font-size: 11px; margin-bottom: 6px;">`;
    tooltip += `<div>🌍 ${d.team} (${d.noc})</div>`;

    // Mostrar anos apenas se não for N/A
    if (d.years !== 'N/A') {
        tooltip += `<div>📅 ${d.years}</div>`;
    }

    // Dados bioantropométricos (se disponíveis)
    if (d.age !== 'N/A' || d.height !== 'N/A' || d.weight !== 'N/A') {
        let bioData = [];
        if (d.age !== 'N/A') bioData.push(`${d.age} anos`);
        if (d.height !== 'N/A') bioData.push(`${d.height}cm`);
        if (d.weight !== 'N/A') bioData.push(`${d.weight}kg`);
        tooltip += `<div>👤 ${bioData.join(' | ')}</div>`;
    }
    tooltip += `</div>`;

    // Performance (mostrar contagem de medalhas)
    tooltip += `<div style="background-color: #f5f5f5; padding: 6px; margin: 4px 0; border-radius: 3px; font-size: 11px;">`;
    tooltip += `<div style="font-weight: bold; margin-bottom: 3px;">🏅 Medalhas</div>`;

    let medalParts = [];
    if (d.medal_gold > 0) medalParts.push(`🥇 ${d.medal_gold}`);
    if (d.medal_silver > 0) medalParts.push(`🥈 ${d.medal_silver}`);
    if (d.medal_bronze > 0) medalParts.push(`🥉 ${d.medal_bronze}`);

    if (medalParts.length > 0) {
        tooltip += `<div>${medalParts.join(' · ')}</div>`;
        tooltip += `<div style="margin-top: 2px; color: #666;">Total: ${d.medal_total} ${d.medal_total === 1 ? 'medalha' : 'medalhas'}</div>`;
    } else {
        tooltip += `<div>Sem medalhas</div>`;
    }
    tooltip += `</div>`;

    // Métricas de rede
    tooltip += `<div style="background-color: #f0f8ff; padding: 4px; margin: 4px 0; border-radius: 3px; font-size: 10px;">`;
    tooltip += `<div style="font-weight: bold; margin-bottom: 2px;">📊 Métricas de Rede</div>`;
    tooltip += `<div>PageRank: ${d.pagerank} (Top ${d.pagerank_percentile}%)</div>`;
    tooltip += `<div>Betweenness: ${d.betweenness} ${d.is_bridge ? '⭐ Ponte' : ''}</div>`;
    tooltip += `<div>Grau: ${d.degree_total} (in: ${d.degree_in}, out: ${d.degree_out})</div>`;
    tooltip += `<div>Comunidade: ${d.community}</div>`;
    tooltip += `</div>`;

    tooltip += `</div>`;
    return tooltip;
};
