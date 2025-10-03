// Charts and Data Visualization for NASA Weather Risk Detection
class ChartManager {
  constructor() {
    this.charts = {};
    this.initializeCharts();
  }

  initializeCharts() {
    // Wait for Chart.js to be loaded
    if (typeof Chart === 'undefined') {
      setTimeout(() => this.initializeCharts(), 100);
      return;
    }

    Chart.defaults.font.family = 'Inter, sans-serif';
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#64748b';
    Chart.defaults.borderColor = '#e2e8f0';
    Chart.defaults.backgroundColor = 'rgba(79, 141, 216, 0.1)';
  }

  // Create risk probability chart
  createRiskChart(categories) {
    // Remove existing chart if any
    if (this.charts.riskChart) {
      this.charts.riskChart.destroy();
    }

    // Get the charts container
    const chartsContainer = document.getElementById('charts-container');
    if (!chartsContainer) {
      console.warn('Charts container not found');
      return;
    }

    // Clear existing content
    chartsContainer.innerHTML = '';

    // Create canvas element
    const canvas = document.createElement('canvas');
    canvas.id = 'risk-chart';
    canvas.width = 400;
    canvas.height = 200;

    // Create chart wrapper
    const chartWrapper = document.createElement('div');
    chartWrapper.className = 'chart-wrapper';
    chartWrapper.style.cssText = `
      margin-bottom: var(--spacing-lg);
      text-align: center;
    `;

    const chartTitle = document.createElement('h4');
    chartTitle.textContent = 'Risk Probability Overview';
    chartTitle.style.cssText = `
      margin-bottom: var(--spacing-md);
      color: var(--text-primary);
      font-weight: 600;
      font-size: 1rem;
    `;

    chartWrapper.appendChild(chartTitle);
    chartWrapper.appendChild(canvas);
    chartsContainer.appendChild(chartWrapper);

    // Prepare chart data
    const labels = categories.map(cat => this.getShortCategoryName(cat.category));
    const data = categories.map(cat => cat.probability);
    const colors = categories.map(cat => this.getRiskColor(cat.probability));

    // Create chart
    const ctx = canvas.getContext('2d');
    this.charts.riskChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Risk Probability (%)',
          data: data,
          backgroundColor: colors.map(color => color + '20'), // Add transparency
          borderColor: colors,
          borderWidth: 2,
          borderRadius: 6,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'var(--surface)',
            titleColor: 'var(--text-primary)',
            bodyColor: 'var(--text-secondary)',
            borderColor: 'var(--border)',
            borderWidth: 1,
            cornerRadius: 8,
            callbacks: {
              title: function(context) {
                const index = context[0].dataIndex;
                return categories[index].description;
              },
              label: function(context) {
                return `Risk Probability: ${context.parsed.y}%`;
              },
              afterLabel: function(context) {
                const index = context.dataIndex;
                return `Confidence: ${categories[index].confidence}%`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            ticks: {
              maxRotation: 45,
              minRotation: 0
            }
          },
          y: {
            beginAtZero: true,
            max: 100,
            grid: {
              color: 'var(--border)'
            },
            ticks: {
              callback: function(value) {
                return value + '%';
              }
            }
          }
        },
        animation: {
          duration: 1000,
          easing: 'easeInOutQuart'
        }
      }
    });
  }

  // Create historical trend chart (placeholder for future enhancement)
  createTrendChart(historicalData) {
    // This could be implemented to show historical trends
    // For now, we'll focus on the main risk chart
    console.log('Trend chart data:', historicalData);
  }

  // Create risk gauge chart
  createRiskGauge(overallRisk) {
    // Remove existing gauge if any
    if (this.charts.gaugeChart) {
      this.charts.gaugeChart.destroy();
    }

    // Get the charts container
    const chartsContainer = document.getElementById('charts-container');
    if (!chartsContainer) {
      console.warn('Charts container not found');
      return;
    }

    // Create canvas element for gauge
    const canvas = document.createElement('canvas');
    canvas.id = 'risk-gauge';
    canvas.width = 200;
    canvas.height = 200;

    // Create gauge wrapper
    const gaugeWrapper = document.createElement('div');
    gaugeWrapper.className = 'gauge-wrapper';
    gaugeWrapper.style.cssText = `
      text-align: center;
      margin-bottom: var(--spacing-lg);
    `;

    const gaugeTitle = document.createElement('h4');
    gaugeTitle.textContent = 'Overall Risk Gauge';
    gaugeTitle.style.cssText = `
      margin-bottom: var(--spacing-md);
      color: var(--text-primary);
      font-weight: 600;
      font-size: 1rem;
    `;

    const gaugeContainer = document.createElement('div');
    gaugeContainer.className = 'gauge-container';
    gaugeContainer.style.cssText = `
      display: flex;
      justify-content: center;
      align-items: center;
    `;

    gaugeContainer.appendChild(canvas);
    gaugeWrapper.appendChild(gaugeTitle);
    gaugeWrapper.appendChild(gaugeContainer);
    chartsContainer.appendChild(gaugeWrapper);

    // Create gauge chart
    const ctx = canvas.getContext('2d');
    this.charts.gaugeChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Risk', 'Safe'],
        datasets: [{
          data: [overallRisk, 100 - overallRisk],
          backgroundColor: [
            this.getRiskColor(overallRisk),
            '#e2e8f0'
          ],
          borderWidth: 0,
          cutout: '70%'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            enabled: false
          }
        },
        animation: {
          animateRotate: true,
          duration: 1500
        }
      }
    });
  }

  // Get short category name for chart labels
  getShortCategoryName(category) {
    const names = {
      'very_hot': 'Hot',
      'very_cold': 'Cold',
      'very_windy': 'Windy',
      'very_wet': 'Wet',
      'very_uncomfortable': 'Uncomfortable'
    };
    return names[category] || category;
  }

  // Get color based on risk level
  getRiskColor(probability) {
    if (probability >= 30) return '#dc2626'; // very-high
    if (probability >= 20) return '#ef4444'; // high
    if (probability >= 10) return '#f59e0b'; // moderate
    return '#10b981'; // low
  }

  // Clear all charts
  clearCharts() {
    Object.values(this.charts).forEach(chart => {
      if (chart && chart.destroy) {
        chart.destroy();
      }
    });
    this.charts = {};

    // Clear charts container
    const chartsContainer = document.getElementById('charts-container');
    if (chartsContainer) {
      chartsContainer.innerHTML = '';
    }
  }

  // Update charts with new data
  updateCharts(results) {
    this.clearCharts();
    
    if (results.risk_categories && results.risk_categories.length > 0) {
      this.createRiskChart(results.risk_categories);
    }
    
    if (results.overall_risk_score !== undefined) {
      this.createRiskGauge(results.overall_risk_score);
    }
  }
}

// Create global chart manager instance
window.chartManager = new ChartManager();