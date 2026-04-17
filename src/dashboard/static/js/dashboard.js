/**
 * Dashboard JavaScript
 * Gráficos interactivos y funcionalidades del dashboard
 */

// Configuración de colores
const colors = {
    primary: '#6366f1',
    secondary: '#8b5cf6',
    success: '#10b981',
    danger: '#ef4444',
    warning: '#f59e0b'
};

// Inicializar dashboard al cargar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Dashboard inicializado');
    initCharts();
});

/**
 * Inicializar todos los gráficos
 */
function initCharts() {
    drawROIChart();
    drawAccuracyChart();
    drawLigasChart();
    drawPlanChart();
}

/**
 * Gráfico de ROI por día (últimos 30 días)
 */
function drawROIChart() {
    const dates = [];
    const roi = [];
    
    // Generar datos de últimos 30 días
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        dates.push(date.toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }));
        roi.push(Math.random() * 25 - 5); // ROI entre -5% y +20%
    }
    
    const trace = {
        x: dates,
        y: roi,
        type: 'scatter',
        mode: 'lines+markers',
        fill: 'tozeroy',
        line: {
            color: colors.primary,
            width: 3
        },
        marker: {
            size: 6,
            color: colors.primary
        },
        fillcolor: 'rgba(99, 102, 241, 0.1)',
        hovertemplate: '<b>%{x}</b><br>ROI: %{y:.1f}%<extra></extra>'
    };
    
    const layout = {
        title: '',
        xaxis: {
            title: 'Fecha',
            gridcolor: '#e5e7eb'
        },
        yaxis: {
            title: 'ROI (%)',
            gridcolor: '#e5e7eb'
        },
        plot_bgcolor: 'rgba(255, 255, 255, 0)',
        paper_bgcolor: 'white',
        hovermode: 'x unified',
        margin: { t: 20, r: 20, b: 40, l: 60 }
    };
    
    Plotly.newPlot('roi-chart', [trace], layout, { responsive: true });
}

/**
 * Gráfico de tasa de acierto por liga
 */
function drawAccuracyChart() {
    const ligas = ['La Liga', 'Premier', 'Serie A', 'ATP', 'NBA'];
    const accuracy = [65, 58, 62, 55, 68];
    
    const trace = {
        x: ligas,
        y: accuracy,
        type: 'bar',
        marker: {
            color: [
                colors.success,
                colors.primary,
                colors.warning,
                colors.secondary,
                colors.success
            ]
        },
        hovertemplate: '<b>%{x}</b><br>Acierto: %{y}%<extra></extra>'
    };
    
    const layout = {
        title: '',
        xaxis: { title: 'Liga' },
        yaxis: { 
            title: 'Tasa de Acierto (%)',
            range: [0, 100]
        },
        plot_bgcolor: 'rgba(255, 255, 255, 0)',
        paper_bgcolor: 'white',
        margin: { t: 20, r: 20, b: 40, l: 60 }
    };
    
    Plotly.newPlot('accuracy-chart', [trace], layout, { responsive: true });
}

/**
 * Gráfico de preferencias de ligas
 */
function drawLigasChart() {
    const labels = ['La Liga', 'Premier', 'Serie A', 'Bundesliga', 'ATP', 'WTA', 'NBA', 'EuroLiga'];
    const values = [45, 52, 38, 21, 23, 18, 34, 12];
    
    const trace = {
        labels: labels,
        values: values,
        type: 'pie',
        marker: {
            colors: [
                colors.primary,
                colors.secondary,
                colors.success,
                colors.warning,
                '#ec4899',
                '#f97316',
                '#6366f1',
                '#8b5cf6'
            ]
        },
        hovertemplate: '<b>%{label}</b><br>%{value} usuarios<extra></extra>'
    };
    
    const layout = {
        title: '',
        paper_bgcolor: 'white',
        margin: { t: 20, r: 20, b: 20, l: 20 }
    };
    
    Plotly.newPlot('ligas-chart', [trace], layout, { responsive: true });
}

/**
 * Gráfico de distribución por plan
 */
function drawPlanChart() {
    const labels = ['Gratis', 'Básico', 'Premium'];
    const values = [45, 78, 33];
    
    const trace = {
        labels: labels,
        values: values,
        type: 'pie',
        marker: {
            colors: [colors.warning, colors.primary, colors.success]
        },
        hovertemplate: '<b>%{label}</b><br>%{value} usuarios<extra></extra>'
    };
    
    const layout = {
        title: '',
        paper_bgcolor: 'white',
        margin: { t: 20, r: 20, b: 20, l: 20 }
    };
    
    Plotly.newPlot('plan-chart', [trace], layout, { responsive: true });
}

/**
 * Filtrar picks por categoría
 */
function filterPicks(category) {
    // Actualizar botones activos
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Filtrar picks (implementar lógica según necesidad)
    console.log(`Filtrando por: ${category}`);
    
    const picks = document.querySelectorAll('.pick-card');
    picks.forEach(pick => {
        if (category === 'all') {
            pick.style.display = 'flex';
        } else if (category === 'valor') {
            // Mostrar solo picks con valor > 0
            pick.style.display = pick.classList.contains('strong') ? 'flex' : 'none';
        } else {
            pick.style.display = 'none'; // Implementar lógica según deporte
        }
    });
}

/**
 * Realizar apuesta (simulado)
 */
function realizarApuesta(pickId) {
    console.log(`Apuesta registrada para pick: ${pickId}`);
    alert('✅ Apuesta registrada exitosamente');
    
    // Aquí iría la lógica para registrar la apuesta via API
    // fetch('/api/bot/registrar-apuesta', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ pick_id: pickId })
    // })
}

/**
 * Cargar datos en tiempo real desde API
 */
async function loadRealtimeData() {
    try {
        // Cargar estadísticas
        const statsResponse = await fetch('/api/dashboard/stats');
        const stats = await statsResponse.json();
        
        console.log('📊 Estadísticas cargadas:', stats);
        
        // Actualizar tarjetas de estadísticas
        updateStatsCards(stats);
        
        // Recargar cada 60 segundos
        setTimeout(loadRealtimeData, 60000);
    } catch (error) {
        console.error('Error cargando datos:', error);
    }
}

/**
 * Actualizar tarjetas de estadísticas
 */
function updateStatsCards(stats) {
    // Implementar actualización dinámica de las tarjetas
    console.log('Actualizando tarjetas con datos:', stats);
}

// Cargar datos en tiempo real
loadRealtimeData();

// Event listeners adicionales
window.addEventListener('load', function() {
    console.log('✅ Dashboard completamente cargado');
});

