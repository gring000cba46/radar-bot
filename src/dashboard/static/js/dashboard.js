/**
 * Dashboard - Radar Maestro
 * Carga datos y actualiza gráficos
 */

// URLs de la API
const API_BASE = '/api';

// Cargar datos al iniciar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Inicializando Dashboard...');
    cargarEstadisticas();
    cargarPicks();
    cargarGraficos();
    
    // Actualizar cada 30 segundos
    setInterval(cargarEstadisticas, 30000);
});

/**
 * Carga estadísticas generales
 */
async function cargarEstadisticas() {
    try {
        const response = await fetch(`${API_BASE}/dashboard/stats`);
        const data = await response.json();
        
        // Actualizar tarjetas
        document.getElementById('total_suscriptores').textContent = data.suscriptores_total;
        document.getElementById('picks_hoy').textContent = data.picks_generados_hoy;
        document.getElementById('picks_valor').textContent = data.picks_con_valor;
        document.getElementById('roi_promedio').textContent = data.roi_promedio.toFixed(2) + '%';
        
        console.log('✅ Estadísticas cargadas');
    } catch (error) {
        console.error('❌ Error cargando estadísticas:', error);
    }
}

/**
 * Carga picks disponibles
 */
async function cargarPicks() {
    try {
        const response = await fetch(`${API_BASE}/bot/picks`);
        const data = await response.json();
        
        const tbody = document.getElementById('picks-table');
        tbody.innerHTML = '';
        
        data.picks.forEach(pick => {
            const row = document.createElement('tr');
            
            // Determinar color del valor
            const valor = parseFloat(pick.valor);
            let valorClass = 'text-success';
            if (valor >= 3) valorClass = 'text-success';
            else if (valor >= 1.5) valorClass = 'text-warning';
            else valorClass = 'text-info';
            
            row.innerHTML = `
                <td><strong>${pick.partido}</strong></td>
                <td>${pick.mercado}</td>
                <td><strong>${pick.cuota.toFixed(2)}</strong></td>
                <td class="${valorClass}"><strong>${pick.valor}</strong></td>
                <td>${pick.expected_value.toFixed(3)}</td>
                <td>
                    <span class="badge ${pick.confianza >= 0.8 ? 'bg-success' : 'bg-warning'}">
                        ${(pick.confianza * 100).toFixed(0)}%
                    </span>
                </td>
            `;
            
            tbody.appendChild(row);
        });
        
        console.log('✅ Picks cargados:', data.picks.length);
    } catch (error) {
        console.error('❌ Error cargando picks:', error);
    }
}

/**
 * Carga y renderiza gráficos
 */
async function cargarGraficos() {
    try {
        // Gráfico de ROI
        const roiData = [{
            x: ['Día 1', 'Día 2', 'Día 3', 'Día 4', 'Día 5', 'Día 6', 'Día 7'],
            y: [5.2, 7.1, 6.8, 9.3, 12.1, 14.5, 15.5],
            type: 'scatter',
            mode: 'lines+markers',
            line: {color: '#0d6efd', width: 3},
            marker: {size: 8, color: '#0d6efd'}
        }];
        
        const roiLayout = {
            title: '',
            xaxis: {title: 'Días'},
            yaxis: {title: 'ROI (%)'},
            hovermode: 'closest',
            margin: {t: 20},
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: '#fff'
        };
        
        Plotly.newPlot('chart-roi', roiData, roiLayout, {responsive: true});
        
        // Gráfico de ligas
        const ligasData = [{
            labels: ['La Liga', 'Premier', 'Serie A', 'Bundesliga', 'Ligue 1'],
            values: [45, 52, 38, 21, 18],
            type: 'bar',
            marker: {color: ['#0d6efd', '#28a745', '#ffc107', '#dc3545', '#17a2b8']}
        }];
        
        const ligasLayout = {
            title: '',
            xaxis: {title: 'Liga'},
            yaxis: {title: 'Aciertos'},
            margin: {t: 20},
            plot_bgcolor: '#f8f9fa',
            paper_bgcolor: '#fff'
        };
        
        Plotly.newPlot('chart-ligas', ligasData, ligasLayout, {responsive: true});
        
        console.log('✅ Gráficos cargados');
    } catch (error) {
        console.error('❌ Error cargando gráficos:', error);
    }
}

