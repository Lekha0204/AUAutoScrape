/**
 * Charts and Data Visualization Module
 * Handles Chart.js initialization and data visualization
 */

class ChartsManager {
    constructor() {
        this.charts = {};
        this.defaultColors = {
            primary: '#667eea',
            success: '#38ef7d',
            info: '#17a2b8',
            warning: '#ffc107',
            danger: '#e74c3c',
            secondary: '#6c757d'
        };
        this.chartOptions = this.getDefaultChartOptions();
    }

    getDefaultChartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    padding: 12
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            }
        };
    }

    initializeGradeDistributionChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data) return null;

        const chartData = {
            labels: data.grades || ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F'],
            datasets: [{
                label: 'Number of Students',
                data: data.counts || [0, 0, 0, 0, 0, 0, 0, 0],
                backgroundColor: [
                    '#28a745',
                    '#20c997',
                    '#17a2b8',
                    '#007bff',
                    '#6f42c1',
                    '#e83e8c',
                    '#fd7e14',
                    '#dc3545'
                ],
                borderColor: [
                    '#1e7e34',
                    '#1a9e7e',
                    '#138496',
                    '#0056b3',
                    '#5a2a87',
                    '#c22965',
                    '#dc6510',
                    '#bd2130'
                ],
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        };

        const config = {
            type: 'bar',
            data: chartData,
            options: {
                ...this.chartOptions,
                plugins: {
                    ...this.chartOptions.plugins,
                    title: {
                        display: true,
                        text: 'Grade Distribution',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    }
                },
                scales: {
                    ...this.chartOptions.scales,
                    y: {
                        ...this.chartOptions.scales.y,
                        title: {
                            display: true,
                            text: 'Number of Students'
                        }
                    },
                    x: {
                        ...this.chartOptions.scales.x,
                        title: {
                            display: true,
                            text: 'Grades'
                        }
                    }
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    initializePerformanceTrendChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data) return null;

        const chartData = {
            labels: data.semesters || ['Semester 1', 'Semester 2', 'Semester 3'],
            datasets: [{
                label: 'Average CGPA',
                data: data.cgpa_trends || [0, 0, 0],
                borderColor: this.defaultColors.primary,
                backgroundColor: this.defaultColors.primary + '20',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: this.defaultColors.primary,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }, {
                label: 'Pass Rate (%)',
                data: data.pass_rates || [0, 0, 0],
                borderColor: this.defaultColors.success,
                backgroundColor: this.defaultColors.success + '20',
                tension: 0.4,
                fill: false,
                pointBackgroundColor: this.defaultColors.success,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8,
                yAxisID: 'y1'
            }]
        };

        const config = {
            type: 'line',
            data: chartData,
            options: {
                ...this.chartOptions,
                plugins: {
                    ...this.chartOptions.plugins,
                    title: {
                        display: true,
                        text: 'Performance Trends',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    }
                },
                scales: {
                    ...this.chartOptions.scales,
                    y: {
                        ...this.chartOptions.scales.y,
                        title: {
                            display: true,
                            text: 'CGPA'
                        },
                        max: 10
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Pass Rate (%)'
                        },
                        max: 100,
                        grid: {
                            drawOnChartArea: false,
                        },
                    },
                    x: {
                        ...this.chartOptions.scales.x,
                        title: {
                            display: true,
                            text: 'Semesters'
                        }
                    }
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    initializeBranchComparisonChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data) return null;

        const chartData = {
            labels: data.branches || ['CSE', 'ECE', 'AIML', 'AI'],
            datasets: [{
                label: 'Average CGPA',
                data: data.avg_cgpa || [0, 0, 0, 0],
                backgroundColor: [
                    this.defaultColors.primary,
                    this.defaultColors.success,
                    this.defaultColors.info,
                    this.defaultColors.warning
                ],
                borderColor: [
                    this.defaultColors.primary,
                    this.defaultColors.success,
                    this.defaultColors.info,
                    this.defaultColors.warning
                ],
                borderWidth: 2,
                borderRadius: 8
            }]
        };

        const config = {
            type: 'doughnut',
            data: chartData,
            options: {
                ...this.chartOptions,
                plugins: {
                    ...this.chartOptions.plugins,
                    title: {
                        display: true,
                        text: 'Branch-wise Average Performance',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    }
                },
                cutout: '60%'
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    initializeSubjectPerformanceChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data) return null;

        const chartData = {
            labels: data.subjects || [],
            datasets: [{
                label: 'Average Grade Points',
                data: data.grade_points || [],
                backgroundColor: this.generateColorArray(data.subjects?.length || 0),
                borderColor: this.generateColorArray(data.subjects?.length || 0, true),
                borderWidth: 2,
                borderRadius: 4
            }]
        };

        const config = {
            type: 'horizontalBar',
            data: chartData,
            options: {
                ...this.chartOptions,
                indexAxis: 'y',
                plugins: {
                    ...this.chartOptions.plugins,
                    title: {
                        display: true,
                        text: 'Subject-wise Performance',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 10,
                        title: {
                            display: true,
                            text: 'Grade Points'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Subjects'
                        }
                    }
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    generateColorArray(count, darker = false) {
        const colors = Object.values(this.defaultColors);
        const result = [];
        
        for (let i = 0; i < count; i++) {
            let color = colors[i % colors.length];
            if (darker) {
                color = this.darkenColor(color, 20);
            }
            result.push(color);
        }
        
        return result;
    }

    darkenColor(color, percent) {
        const num = parseInt(color.replace("#", ""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }

    updateChart(chartId, newData) {
        if (this.charts[chartId]) {
            this.charts[chartId].data = newData;
            this.charts[chartId].update('active');
        }
    }

    destroyChart(chartId) {
        if (this.charts[chartId]) {
            this.charts[chartId].destroy();
            delete this.charts[chartId];
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(chartId => {
            this.destroyChart(chartId);
        });
    }

    initializeAllCharts(analysisData) {
        if (!analysisData) return;

        // Initialize grade distribution chart
        if (analysisData.grade_distribution) {
            this.initializeGradeDistributionChart('gradeChart', analysisData.grade_distribution);
        }

        // Initialize performance trend chart
        if (analysisData.performance_trends) {
            this.initializePerformanceTrendChart('trendChart', analysisData.performance_trends);
        }

        // Initialize branch comparison chart
        if (analysisData.branch_comparison) {
            this.initializeBranchComparisonChart('branchChart', analysisData.branch_comparison);
        }

        // Initialize subject performance chart if container exists
        const subjectChartCanvas = document.getElementById('subjectChart');
        if (subjectChartCanvas && analysisData.subject_performance) {
            this.initializeSubjectPerformanceChart('subjectChart', analysisData.subject_performance);
        }
    }

    // Method to create a simple statistics card chart
    createStatCard(containerId, value, label, icon, color = 'primary') {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="text-center">
                <i class="fas fa-${icon} fa-2x text-${color} mb-2"></i>
                <h3 class="text-${color}">${value}</h3>
                <p class="text-muted">${label}</p>
            </div>
        `;
    }

    // Method to create animated counters
    animateCounter(elementId, targetValue, duration = 2000) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startValue = 0;
        const increment = targetValue / (duration / 16);
        let currentValue = startValue;

        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            
            // Format value based on type
            let displayValue = Math.floor(currentValue);
            if (targetValue % 1 !== 0) {
                displayValue = currentValue.toFixed(2);
            }
            
            element.textContent = displayValue;
        }, 16);
    }

    // Export chart as image
    exportChart(chartId, filename = 'chart.png') {
        if (this.charts[chartId]) {
            const url = this.charts[chartId].toBase64Image();
            const link = document.createElement('a');
            link.download = filename;
            link.href = url;
            link.click();
        }
    }

    // Resize all charts (useful for responsive behavior)
    resizeAllCharts() {
        Object.values(this.charts).forEach(chart => {
            chart.resize();
        });
    }
}

// Initialize charts manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.chartsManager = new ChartsManager();
    
    // Global function to initialize charts with data
    window.initializeCharts = function(data) {
        window.chartsManager.initializeAllCharts(data);
    };
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.chartsManager) {
            window.chartsManager.resizeAllCharts();
        }
    });
    
    console.log('Charts Manager initialized successfully');
});

// Export for use in other modules
window.ChartsManager = ChartsManager;
