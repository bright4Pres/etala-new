/* ==========================================
   LIBRARY ANALYTICS DASHBOARD - STATISTICS.JS
   Enhanced statistics visualization using Chart.js
   ========================================== */

// Wait for DOM to be fully loaded before initializing
document.addEventListener('DOMContentLoaded', function() {
    
    /* ==========================================
       DATA INITIALIZATION
       Load analytics data from window object (injected from Django)
       ========================================== */
    const metrics = window.analyticsData || {};

    // Monthly borrows data with fallback defaults
    const monthlyLabels = metrics.monthlyLabels || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];
    const monthlyData = metrics.monthlyData || [4, 3, 9, 3, 4, 3, 4];

    // Weekly activity data with fallback defaults
    const weeklyLabels = metrics.weeklyLabels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const weeklyData = metrics.weeklyData || [12, 19, 15, 21, 18, 24, 22];

    // Book type distribution data with fallback defaults
    const typeLabels = metrics.typeLabels || ['Books', 'Article', 'Thesis', 'Analytics'];
    const typeData = metrics.typeData || [400, 300, 300, 200];

    // Language distribution data with fallback defaults
    const languageLabels = metrics.languageLabels || ['English', 'Filipino', 'Spanish', 'Others'];
    const languageData = metrics.languageData || [500, 200, 150, 100];

     /* ==========================================
         CHART.JS GLOBAL CONFIGURATION
         Set default styling for all charts
         ========================================== */
     const rootStyles = getComputedStyle(document.documentElement);
     const colorToken = (name, fallback) => rootStyles.getPropertyValue(name).trim() || fallback;
     const themeColors = {
          accent: colorToken('--accent', '#2f3a40'),
          accentStrong: colorToken('--accent-strong', '#252f34'),
          accentSoft: colorToken('--accent-soft', '#e3e6e1'),
          info: colorToken('--info', '#2f5b6b'),
          success: colorToken('--success', '#2f6f5f'),
          warning: colorToken('--warning', '#8a6b2e'),
          danger: colorToken('--danger', '#8c3a3a'),
          textMuted: colorToken('--secondary-color', '#6b7280')
     };

     Chart.defaults.font.family = '"DM Sans", sans-serif';
     Chart.defaults.color = themeColors.textMuted;

    /* ==========================================
       MONTHLY BORROWS CHART
       Line chart showing borrowing trends over months
       ========================================== */
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
                    borderColor: themeColors.accent,
                    backgroundColor: themeColors.accentSoft,
                    borderWidth: 3,
                    fill: true,                          // Fill area under line
                    tension: 0.4,                        // Curve the line (0 = straight, 1 = very curved)
                    
                    // Point styling for data markers
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: themeColors.accent,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    
                    // Hover state styling
                    pointHoverBackgroundColor: themeColors.accentStrong,
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,                        // Auto-resize with container
                maintainAspectRatio: false,              // Allow custom height
                interaction: {
                    mode: 'index',                       // Show tooltip for all datasets at x-position
                    intersect: false                     // Show tooltip even when not directly over point
                },
                scales: {
                    y: {
                        beginAtZero: true,               // Start y-axis at 0
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            precision: 0,                // No decimal places (whole numbers only)
                            padding: 10,
                            font: { size: 12 }
                        }
                    },
                    x: {
                        grid: {
                            display: false,              // Hide vertical grid lines
                            drawBorder: false
                        },
                        ticks: {
                            padding: 10,
                            font: { size: 12 }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false                   // Hide legend (only one dataset)
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
                        displayColors: false,            // Hide color box in tooltip
                        callbacks: {
                            // Custom tooltip text format
                            label: function(context) {
                                return 'Borrows: ' + context.parsed.y;
                            }
                        }
                    }
                }
            }
        });
    }

    /* ==========================================
       WEEKLY ACTIVITY CHART
       Bar chart showing daily borrows for the last 7 days
       ========================================== */
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
                    backgroundColor: themeColors.info,
                    borderRadius: 8,                     // Rounded corners on bars
                    borderSkipped: false,                // Round all corners, not just top
                    hoverBackgroundColor: themeColors.accentStrong
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
                            precision: 0,                // Whole numbers only
                            padding: 10,
                            font: { size: 12 }
                        }
                    },
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            padding: 10,
                            font: { size: 12 }
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

    /* ==========================================
       COLOR GENERATOR HELPER FUNCTION
       Generates unique colors for charts with many segments
       ========================================== */
    function generateColors(n) {
        // Predefined color palette (20 colors)
        const baseColors = [
            themeColors.accent,
            themeColors.info,
            themeColors.success,
            themeColors.warning,
            themeColors.danger,
            themeColors.accentStrong,
            themeColors.textMuted,
        ];
        
        // If we need fewer colors than we have, just slice the array
        if (n <= baseColors.length) return baseColors.slice(0, n);
        
        // If we need more colors, generate additional HSL colors
        const colors = baseColors.slice();
        for (let i = colors.length; i < n; i++) {
            const hue = Math.round((360 / n) * i);      // Distribute hues evenly around color wheel
            colors.push(`hsl(${hue}, 70%, 55%)`);
        }
        return colors;
    }

    /* ==========================================
       BOOKS BY TYPE CHART
       Doughnut chart showing distribution of book types
       ========================================== */
    const salesCanvas = document.getElementById('salesChart');
    if (salesCanvas) {
        const salesCtx = salesCanvas.getContext('2d');
        const typeColors = generateColors(typeLabels.length);
        
        new Chart(salesCtx, {
            type: 'doughnut',
            data: {
                labels: typeLabels,
                datasets: [{
                    data: typeData,
                    backgroundColor: typeColors,
                    borderWidth: 0,                      // No borders between segments
                    hoverOffset: 15,                     // Pull segment out on hover
                    hoverBorderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',                           // Size of donut hole (65% = large hole)
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,         // Use circles instead of rectangles
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
                            // Show count and percentage in tooltip
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

    /* ==========================================
       BOOKS BY LANGUAGE CHART
       Doughnut chart showing distribution by language
       ========================================== */
    const languageCanvas = document.getElementById('languageChart');
    if (languageCanvas) {
        const languageCtx = languageCanvas.getContext('2d');
        const langColors = generateColors(languageLabels.length);
        
        new Chart(languageCtx, {
            type: 'doughnut',
            data: {
                labels: languageLabels,
                datasets: [{
                    data: languageData,
                    backgroundColor: langColors,
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

    /* ==========================================
       REFRESH BUTTON FUNCTIONALITY
       Adds spinning animation and reloads page
       ========================================== */
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon) {
                // Add spinning animation to refresh icon
                icon.classList.add('fa-spin');
            }
            
            // Reload page after 1 second (allows user to see animation)
            setTimeout(() => {
                location.reload();
            }, 1000);
        });
    }

    /* ==========================================
       PERIOD SELECT FUNCTIONALITY
       Changes URL parameter when user selects different time period
       ========================================== */
    const periodSelect = document.getElementById('period-select');
    const periodForm = document.getElementById('period-form');
    const rangeFields = document.getElementById('period-range-fields');

    function toggleRangeFields(isRange) {
        if (!rangeFields) return;
        rangeFields.style.display = isRange ? 'flex' : 'none';
    }

    if (periodSelect) {
        toggleRangeFields(periodSelect.value === 'range');
        periodSelect.addEventListener('change', function() {
            const isRange = this.value === 'range';
            toggleRangeFields(isRange);
            if (!isRange && periodForm) {
                periodForm.submit();
            }
        });
    }

    /* ==========================================
       HEATMAP RANGE SELECT AUTO-SUBMIT
       Submits form when user changes heatmap time range
       ========================================== */
    const heatmapRangeSelect = document.getElementById('heatmap-range-select');
    if (heatmapRangeSelect) {
        heatmapRangeSelect.addEventListener('change', function() {
            // Automatically submit the form to refresh heatmap
            this.form.submit();
        });
    }

    /* ==========================================
       CHART CARD ENTRANCE ANIMATIONS
       Staggered fade-in animation for chart containers
       ========================================== */
    const chartCards = document.querySelectorAll('.chart-card');
    chartCards.forEach((card, index) => {
        // Start hidden and slightly below final position
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        // Animate in with staggered delay (100ms between each card)
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    /* ==========================================
       KPI CARD ENTRANCE ANIMATIONS
       Faster staggered animation for KPI cards
       ========================================== */
    const kpiCards = document.querySelectorAll('.kpi-card');
    kpiCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(10px)';
        
        // Faster animation with 50ms stagger
        setTimeout(() => {
            card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50);
    });

    /* ==========================================
       AUTO-REFRESH (OPTIONAL)
       Uncomment to enable automatic dashboard refresh
       ========================================== */
    // setInterval(() => {
    //     console.log('Auto-refreshing dashboard...');
    //     location.reload();
    // }, 300000);  // Refresh every 5 minutes (300000ms)

    /* ==========================================
       PROGRESS BAR ANIMATION
       Animates progress bars using data-percent attributes
       Avoids inline template CSS for cleaner code
       ========================================== */
    const progressFills = document.querySelectorAll('.progress-fill[data-percent]');
    progressFills.forEach(el => {
        const p = parseFloat(el.getAttribute('data-percent')) || 0;
        // Clamp percentage between 0 and 100
        const pct = Math.max(0, Math.min(100, p));
        el.style.width = pct + '%';
    });
    console.log('📊 Analytics Dashboard Loaded Successfully');
    console.log('📈 Metrics:', metrics);
});