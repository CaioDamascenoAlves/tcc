// Timeline de participações olímpicas
function createTimeline(nodesData, margin, canvas) {
    const ctx = canvas.getContext('2d');
    
    // Ajustar tamanho do canvas
    const container = document.getElementById('timeline-container');
    canvas.width = container.clientWidth - 20;
    canvas.height = 100;

    // Extrair anos de todos os nós
    const yearData = {};
    nodesData.forEach(n => {
        if (n.tooltip_data && n.tooltip_data.years_list) {
            n.tooltip_data.years_list.forEach(year => {
                if (!yearData[year]) {
                    yearData[year] = 0;
                }
                yearData[year]++;
            });
        }
    });

    const years = Object.keys(yearData).map(Number).sort((a, b) => a - b);
    if (years.length === 0) {
        ctx.fillStyle = '#666';
        ctx.font = '14px Arial';
        ctx.fillText('Sem dados temporais disponíveis', 20, 50);
        return;
    }

    const counts = years.map(y => yearData[y]);
    const maxCount = Math.max(...counts);
    
    // Dimensões
    const width = canvas.width - margin.left - margin.right;
    const height = canvas.height - margin.top - margin.bottom;

    // Estado de hover e seleção
    let hoveredIndex = -1;
    let selectedYear = null;

    // Função para redesenhar o gráfico
    function draw() {
        // Limpar canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Desenhar título
        ctx.fillStyle = '#333';
        ctx.font = 'bold 12px Arial';
        ctx.fillText('Timeline: Número de Atletas por Ano Olímpico', margin.left, 15);

        // Desenhar barras
        const barWidth = width / years.length;

        years.forEach((year, i) => {
            const count = yearData[year];
            const barHeight = (count / maxCount) * height;
            const x = margin.left + (i * barWidth);
            const y = margin.top + height - barHeight;

            // Cor diferente se hover ou selecionado
            if (i === hoveredIndex) {
                ctx.fillStyle = '#C73948'; // Vermelho mais claro
            } else if (year === selectedYear) {
                ctx.fillStyle = '#FFD700'; // Dourado para selecionado
            } else {
                ctx.fillStyle = '#8B2635'; // Cor padrão UFOP
            }

            ctx.fillRect(x, y, barWidth - 2, barHeight);
            
            ctx.strokeStyle = '#2A2A2A';
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, barWidth - 2, barHeight);
        });

        // Eixo X (Anos)
        ctx.fillStyle = '#333';
        ctx.font = '10px Arial';
        ctx.textAlign = 'center';
        
        // Mostrar apenas alguns anos para não poluir
        const yearStep = Math.ceil(years.length / 10);
        years.forEach((year, i) => {
            if (i % yearStep === 0 || i === years.length - 1) {
                const x = margin.left + (i * barWidth) + barWidth / 2;
                ctx.fillText(year, x, canvas.height - 10);
            }
        });

        // Eixo Y (Contagem)
        ctx.textAlign = 'right';
        const ySteps = 5;
        for (let i = 0; i <= ySteps; i++) {
            const count = Math.round((maxCount / ySteps) * i);
            const y = margin.top + height - (height / ySteps * i);
            ctx.fillText(count, margin.left - 5, y + 4);
            
            // Linha de grade
            ctx.strokeStyle = '#e0e0e0';
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            ctx.moveTo(margin.left, y);
            ctx.lineTo(margin.left + width, y);
            ctx.stroke();
        }

        // Tooltip visual se hover
        if (hoveredIndex >= 0 && hoveredIndex < years.length) {
            const year = years[hoveredIndex];
            const count = yearData[year];
            const barWidth = width / years.length;
            const x = margin.left + (hoveredIndex * barWidth) + barWidth / 2;
            const barHeight = (count / maxCount) * height;
            const y = margin.top + height - barHeight - 5;

            // Fundo do tooltip
            const text = `${year}: ${count} atletas`;
            ctx.font = 'bold 11px Arial';
            const textWidth = ctx.measureText(text).width;
            
            ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
            ctx.fillRect(x - textWidth/2 - 5, y - 20, textWidth + 10, 18);
            
            // Texto do tooltip
            ctx.fillStyle = '#fff';
            ctx.textAlign = 'center';
            ctx.fillText(text, x, y - 7);
        }
    }

    // Desenho inicial
    draw();

    // Interatividade: mostrar detalhes ao passar o mouse
    canvas.onmousemove = function(e) {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        if (x >= margin.left && x <= margin.left + width && 
            y >= margin.top && y <= margin.top + height) {
            const barWidth = width / years.length;
            const index = Math.floor((x - margin.left) / barWidth);
            if (index >= 0 && index < years.length) {
                if (hoveredIndex !== index) {
                    hoveredIndex = index;
                    draw();
                }
                canvas.style.cursor = 'pointer';
                return;
            }
        }
        
        if (hoveredIndex !== -1) {
            hoveredIndex = -1;
            draw();
        }
        canvas.style.cursor = 'default';
    };

    // Sair do canvas
    canvas.onmouseleave = function() {
        if (hoveredIndex !== -1) {
            hoveredIndex = -1;
            draw();
        }
        canvas.style.cursor = 'default';
    };

    // Click para selecionar ano
    canvas.onclick = function(e) {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const barWidth = width / years.length;
        
        if (x >= margin.left && x <= margin.left + width) {
            const index = Math.floor((x - margin.left) / barWidth);
            if (index >= 0 && index < years.length) {
                const year = years[index];
                
                // Alternar seleção
                if (selectedYear === year) {
                    selectedYear = null;
                    console.log('Ano desmarcado:', year);
                } else {
                    selectedYear = year;
                    console.log('Ano selecionado:', year, '- Atletas:', yearData[year]);
                }
                
                draw();
            }
        }
    };
}
