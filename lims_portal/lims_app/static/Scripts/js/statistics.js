// Enhanced Statistics Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const metrics = window.analyticsData || {};

    // Helpers / fallbacks
    const monthlyLabels = metrics.monthlyLabels || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];
    const monthlyData = metrics.monthlyData || [4, 3, 9, 3, 4, 3, 4];

    const weeklyLabels = metrics.weeklyLabels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const weeklyData = metrics.weeklyData || [12, 19, 15, 21, 18, 24, 22];

    const typeLabels = metrics.typeLabels || ['Books', 'Article', 'Thesis', 'Analytics'];
    const typeData = metrics.typeData || [400, 300, 300, 200];

    const languageLabels = metrics.languageLabels || ['English', 'Filipino', 'Spanish', 'Others'];
    const languageData = metrics.languageData || [500, 200, 150, 100];

    // Chart.js default configuration
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
    Chart.defaults.color = '#6b7280';

    // ========== MONTHLY BORROWS CHART (Enhanced Line Chart) ==========
    const revenueCanvas = document.getElementById('revenueChart');
    if (revenueCanvas) {
        const revenueCtx = revenueCanvas.getContext('2d');
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: monthlyLabels,
                datasets: [{
                    label: 'Borrows',
                    data: monthlyData,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointHoverBackgroundColor: '#2563eb',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            precision: 0,
                            padding: 10,
                            font: {
                                size: 12
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            padding: 10,
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        cornerRadius: 8,
                        titleFont: {
                            size: 14,
                            weight: '600'
                        },
                        bodyFont: {
                            size: 13
                        },
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return 'Borrows: ' + context.parsed.y;
                            }
                        }
                    }
                }
            }
        });
    }

    // ========== WEEKLY ACTIVITY CHART (Enhanced Bar Chart) ==========
    const userCanvas = document.getElementById('userChart');
    if (userCanvas) {
        const userCtx = userCanvas.getContext('2d');
        new Chart(userCtx, {
            type: 'bar',
            data: {
                labels: weeklyLabels,
                datasets: [{
                    label: 'Borrows / day',
                    data: weeklyData,
                    backgroundColor: '#8b5cf6',
                    borderRadius: 8,
                    borderSkipped: false,
                    hoverBackgroundColor: '#7c3aed'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            precision: 0,
                            padding: 10,
                            font: {
                                size: 12
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            padding: 10,
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        cornerRadius: 8,
                        titleFont: {
                            size: 14,
                            weight: '600'
                        },
                        bodyFont: {
                            size: 13
                        },
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return 'Borrows: ' + context.parsed.y;
                            }
                        }
                    }
                }
            }
        });
    }

    // ========== BOOKS BY TYPE CHART (Enhanced Doughnut) ==========
    const salesCanvas = document.getElementById('salesChart');
    if (salesCanvas) {
        const salesCtx = salesCanvas.getContext('2d');
        new Chart(salesCtx, {
            type: 'doughnut',
            data: {
                labels: typeLabels,
                datasets: [{
                    data: typeData,
                    backgroundColor: [
                        '#3b82f6',
                        '#8b5cf6',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444',
                        '#06b6d4'
                    ],
                    borderWidth: 0,
                    hoverOffset: 15,
                    hoverBorderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            font: {
                                size: 13,
                                family: "'Inter', sans-serif"
                            },
                            color: '#64748b'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        cornerRadius: 8,
                        titleFont: {
                            size: 14,
                            weight: '600'
                        },
                        bodyFont: {
                            size: 13
                        },
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return label + ': ' + value + ' (' + percentage + '%)';
                            }
                        }
                    }
                }
            }
        });
    }

    // ========== BOOKS BY LANGUAGE CHART (New Doughnut Chart) ==========
    const languageCanvas = document.getElementById('languageChart');
    if (languageCanvas) {
        const languageCtx = languageCanvas.getContext('2d');
        new Chart(languageCtx, {
            type: 'doughnut',
            data: {
                labels: languageLabels,
                datasets: [{
                    data: languageData,
                    backgroundColor: [
                        '#06b6d4',
                        '#14b8a6',
                        '#84cc16',
                        '#eab308',
                        '#f97316'
                    ],
                    borderWidth: 0,
                    hoverOffset: 15,
                    hoverBorderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            font: {
                                size: 13,
                                family: "'Inter', sans-serif"
                            },
                            color: '#64748b'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        cornerRadius: 8,
                        titleFont: {
                            size: 14,
                            weight: '600'
                        },
                        bodyFont: {
                            size: 13
                        },
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return label + ': ' + value + ' (' + percentage + '%)';
                            }
                        }
                    }
                }
            }
        });
    }

    // ========== REFRESH BUTTON FUNCTIONALITY ==========
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.add('fa-spin');
            }
            
            // Reload the page after animation
            setTimeout(() => {
                location.reload();
            }, 1000);
        });
    }

    // ========== PERIOD SELECT FUNCTIONALITY ==========
    const periodSelect = document.getElementById('period-select');
    if (periodSelect) {
        periodSelect.addEventListener('change', function() {
            const selectedPeriod = this.value;
            window.location.href = '?period=' + selectedPeriod;
        });
    }

    // ========== CHART ANIMATIONS ==========
    // Add smooth entrance animations to all charts
    const chartCards = document.querySelectorAll('.chart-card');
    chartCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // ========== KPI CARD ANIMATIONS ==========
    const kpiCards = document.querySelectorAll('.kpi-card');
    kpiCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(10px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50);
    });

    // ========== AUTO-REFRESH (Optional - Commented Out) ==========
    // Uncomment to enable auto-refresh every 5 minutes
    // setInterval(() => {
    //     console.log('Auto-refreshing dashboard...');
    //     location.reload();
    // }, 300000);

    // set progress bar widths from data-percent attributes to avoid inline template CSS
    const progressFills = document.querySelectorAll('.progress-fill[data-percent]');
    progressFills.forEach(el => {
        const p = parseFloat(el.getAttribute('data-percent')) || 0;
        // clamp 0-100
        const pct = Math.max(0, Math.min(100, p));
        el.style.width = pct + '%';
    });

    console.log('📊 Analytics Dashboard Loaded Successfully');
    console.log('📈 Metrics:', metrics);
});