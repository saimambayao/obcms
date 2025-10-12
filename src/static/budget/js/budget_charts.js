/**
 * Budget Charts - Chart.js Integration
 * OBCMS Budget System
 */

/**
 * Initialize quarterly execution chart
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} data - Chart data with labels and datasets
 */
function initQuarterlyChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return;
    }

    // Destroy existing chart if it exists
    if (window.quarterlyChart) {
        window.quarterlyChart.destroy();
    }

    window.quarterlyChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false, // We're showing custom legend below
                    position: 'bottom',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#1f2937',
                    bodyColor: '#4b5563',
                    borderColor: '#e5e7eb',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += '₱' + context.parsed.y.toLocaleString('en-PH', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });
                            return label;
                        }
                    }
                },
                title: {
                    display: false
                }
            },
            scales: {
                x: {
                    stacked: false,
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 12,
                            weight: 'bold'
                        },
                        color: '#6b7280'
                    }
                },
                y: {
                    stacked: false,
                    beginAtZero: true,
                    grid: {
                        color: '#f3f4f6',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        },
                        color: '#9ca3af',
                        callback: function(value) {
                            return '₱' + (value / 1000000).toFixed(0) + 'M';
                        }
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false,
            }
        }
    });
}

/**
 * Initialize program utilization chart (Doughnut)
 * @param {string} canvasId - ID of the canvas element
 * @param {Array} programs - Array of program objects with name and utilization
 */
function initProgramUtilizationChart(canvasId, programs) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return;
    }

    // Destroy existing chart if it exists
    if (window.programChart) {
        window.programChart.destroy();
    }

    const labels = programs.map(p => p.name);
    const data = programs.map(p => p.utilization);
    const colors = [
        'rgba(37, 99, 235, 0.8)',    // blue-600
        'rgba(5, 150, 105, 0.8)',    // emerald-600
        'rgba(124, 58, 237, 0.8)',   // purple-600
        'rgba(249, 115, 22, 0.8)',   // orange-500
        'rgba(217, 119, 6, 0.8)',    // amber-600
    ];

    window.programChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderColor: '#ffffff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            size: 12
                        },
                        color: '#4b5563',
                        padding: 12,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#1f2937',
                    bodyColor: '#4b5563',
                    borderColor: '#e5e7eb',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.toFixed(0) + '%';
                            return label;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize budget variance chart (Line)
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} data - Variance data with months and variance amounts
 */
function initVarianceChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return;
    }

    // Destroy existing chart if it exists
    if (window.varianceChart) {
        window.varianceChart.destroy();
    }

    window.varianceChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 12
                        },
                        color: '#4b5563',
                        usePointStyle: true
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#1f2937',
                    bodyColor: '#4b5563',
                    borderColor: '#e5e7eb',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += '₱' + context.parsed.y.toLocaleString('en-PH', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });
                            return label;
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
                        font: {
                            size: 11
                        },
                        color: '#6b7280'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#f3f4f6',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        },
                        color: '#9ca3af',
                        callback: function(value) {
                            return '₱' + (value / 1000000).toFixed(1) + 'M';
                        }
                    }
                }
            },
            elements: {
                line: {
                    tension: 0.4,
                    borderWidth: 2
                },
                point: {
                    radius: 4,
                    hoverRadius: 6
                }
            }
        }
    });
}

/**
 * Update chart data dynamically
 * @param {Chart} chart - Chart.js instance
 * @param {Array} newData - New data array
 */
function updateChartData(chart, newData) {
    if (!chart) {
        console.error('Chart instance not provided');
        return;
    }

    chart.data.datasets.forEach((dataset, i) => {
        if (newData[i]) {
            dataset.data = newData[i];
        }
    });

    chart.update();
}

/**
 * Fetch and update chart with real-time data
 * @param {string} chartId - Chart identifier
 * @param {string} apiUrl - API endpoint URL
 */
async function fetchAndUpdateChart(chartId, apiUrl) {
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Update the appropriate chart based on chartId
        switch(chartId) {
            case 'quarterly':
                if (window.quarterlyChart) {
                    updateChartData(window.quarterlyChart, [
                        data.allotted,
                        data.obligated,
                        data.disbursed
                    ]);
                }
                break;
            case 'program':
                if (window.programChart) {
                    window.programChart.data.labels = data.labels;
                    window.programChart.data.datasets[0].data = data.values;
                    window.programChart.update();
                }
                break;
            case 'variance':
                if (window.varianceChart) {
                    updateChartData(window.varianceChart, [
                        data.planned,
                        data.actual
                    ]);
                }
                break;
        }
    } catch (error) {
        console.error('Error fetching chart data:', error);
    }
}

/**
 * Export chart as image
 * @param {string} chartId - Canvas element ID
 * @param {string} filename - Export filename
 */
function exportChartAsImage(chartId, filename = 'chart.png') {
    const canvas = document.getElementById(chartId);
    if (!canvas) {
        console.error(`Canvas with ID '${chartId}' not found`);
        return;
    }

    const url = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.download = filename;
    link.href = url;
    link.click();
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initQuarterlyChart,
        initProgramUtilizationChart,
        initVarianceChart,
        updateChartData,
        fetchAndUpdateChart,
        exportChartAsImage
    };
}
