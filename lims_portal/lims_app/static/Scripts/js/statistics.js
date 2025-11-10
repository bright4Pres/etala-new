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
        function generateColors(n) {
            const baseColors = [
                '#06b6d4', '#14b8a6', '#84cc16', '#eab308', '#f97316',
                '#ef4444', '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b',
                '#a21caf', '#6366f1', '#0ea5e9', '#f43f5e', '#22d3ee',
                '#e11d48', '#facc15', '#16a34a', '#7c3aed', '#f472b6'
            ];
            if (n <= baseColors.length) return baseColors.slice(0, n);
            // If more needed, generate HSL colors
            const colors = baseColors.slice();
            for (let i = colors.length; i < n; i++) {
                const hue = Math.round((360 / n) * i);
                colors.push(`hsl(${hue}, 70%, 55%)`);
            }
            return colors;
        }
        const langColors = generateColors(languageLabels.length);
        new Chart(salesCtx, {
            type: 'doughnut',
            data: {
                labels: typeLabels,
                datasets: [{
                    data: typeData,
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

    // ========== BOOKS BY LANGUAGE CHART (New Doughnut Chart) ==========
    const languageCanvas = document.getElementById('languageChart');
    if (languageCanvas) {
        const languageCtx = languageCanvas.getContext('2d');
        // Generate enough unique colors for all languages
        function generateColors(n) {
            const baseColors = [
                '#06b6d4', '#14b8a6', '#84cc16', '#eab308', '#f97316',
                '#ef4444', '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b',
                '#a21caf', '#6366f1', '#0ea5e9', '#f43f5e', '#22d3ee',
                '#e11d48', '#facc15', '#16a34a', '#7c3aed', '#f472b6'
            ];
            if (n <= baseColors.length) return baseColors.slice(0, n);
            // If more needed, generate HSL colors
            const colors = baseColors.slice();
            for (let i = colors.length; i < n; i++) {
                const hue = Math.round((360 / n) * i);
                colors.push(`hsl(${hue}, 70%, 55%)`);
            }
            return colors;
        }
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

    // ========== HEATMAP RANGE SELECT AUTO-SUBMIT ==========
    const heatmapRangeSelect = document.getElementById('heatmap-range-select');
    if (heatmapRangeSelect) {
        heatmapRangeSelect.addEventListener('change', function() {
            this.form.submit();
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

    // ========== CALENDAR HEATMAP RENDERER ==========
    (function renderCalendarHeatmap() {
        const heatmap = metrics.heatmapData || null;
        const container = document.getElementById('calendar-heatmap');
        if (!heatmap || !container || !Array.isArray(heatmap) || heatmap.length === 0) return;

        // Prepare chronological array (views.py already reverses to oldest->newest)
        const data = heatmap.slice(); // { date: 'YYYY-MM-DD', count: N }
        const firstDate = new Date(data[0].date + 'T00:00:00');
        const startDow = firstDate.getDay(); // 0 (Sun) - 6 (Sat)

        const days = data.length;
        const weeks = Math.ceil((startDow + days) / 7);

        // Responsive cell size: bigger if fewer days, smaller if more days
        let cellSize = 14;
        if (days <= 14) cellSize = 32;
        else if (days <= 31) cellSize = 22;
        else if (days <= 62) cellSize = 16;
        else if (days <= 366) cellSize = 20;

        // Center the grid horizontally if not full weeks
        let gridJustify = 'center';
        if (weeks * 7 - days - startDow > 0) gridJustify = 'center';

        // compute max for scaling
        const maxCount = data.reduce((m, d) => Math.max(m, d.count || 0), 0);

        // color palette: 5 levels (0..4)
        const colors = ['#a8a8a8ff', '#c6e48b', '#7bc96f', '#239a3b', '#196127'];

        // helper: compute level 0..4
        function getLevel(count) {
            if (!count || maxCount === 0) return 0;
            const ratio = count / maxCount;
            if (ratio <= 0.2) return 1;
            if (ratio <= 0.4) return 2;
            if (ratio <= 0.7) return 3;
            return 4;
        }

        // clear and setup container grid
        container.innerHTML = '';
        container.style.display = 'grid';
        container.style.gridTemplateRows = `repeat(7, ${cellSize}px)`;
        container.style.gridTemplateColumns = `repeat(${weeks}, ${cellSize}px)`;
        container.style.gap = `${Math.max(2, Math.round(cellSize / 7))}px`;
        container.style.alignItems = 'center';
        container.style.justifyItems = 'center';
        container.style.justifyContent = gridJustify;
        container.style.padding = '12px 0';

        // build day cells into grid by week/weekday
        // globalIndex = week*7 + weekday - startDow
        for (let w = 0; w < weeks; w++) {
            for (let d = 0; d < 7; d++) {
                const globalIndex = w * 7 + d - startDow;
                const cell = document.createElement('div');
                cell.className = 'heatday';
                cell.style.width = `${cellSize}px`;
                cell.style.height = `${cellSize}px`;
                cell.style.borderRadius = `${Math.round(cellSize/4)}px`;
                cell.style.boxSizing = 'border-box';
                cell.style.background = colors[0];
                cell.style.cursor = 'default';
                cell.style.transition = 'transform 120ms ease';

                if (globalIndex >= 0 && globalIndex < days) {
                    const item = data[globalIndex];
                    const cnt = item.count || 0;
                    const lvl = getLevel(cnt);
                    cell.style.background = colors[lvl];
                    cell.title = `${item.date}: ${cnt} borrows`;
                    cell.setAttribute('data-count', cnt);
                    cell.setAttribute('data-date', item.date);
                    // hover effect
                    cell.addEventListener('mouseenter', () => { cell.style.transform = 'scale(1.15)'; });
                    cell.addEventListener('mouseleave', () => { cell.style.transform = 'scale(1)'; });
                } else {
                    // empty day (out of range)
                    cell.title = '';
                    cell.setAttribute('aria-hidden', 'true');
                    cell.style.opacity = '0.3';
                }

                container.appendChild(cell);
            }
        }

        // synchronize legend boxes in template (if present)
        const legendBoxes = document.querySelectorAll('.heatmap-legend-box');
        if (legendBoxes && legendBoxes.length >= 5) {
            for (let i = 0; i < 5 && i < legendBoxes.length; i++) {
                legendBoxes[i].style.background = colors[i];
                legendBoxes[i].style.width = `${Math.max(18, cellSize)}px`;
                legendBoxes[i].style.height = `${Math.max(12, Math.round(cellSize * 0.7))}px`;
                legendBoxes[i].style.borderRadius = `${Math.round(cellSize/4)}px`;
                legendBoxes[i].style.display = 'inline-block';
            }
        }

        // optional: add small responsive caption showing date range and max count
        const caption = document.createElement('div');
        caption.style.fontSize = '12px';
        caption.style.color = '#6b7280';
        caption.style.marginTop = '8px';
        const startLabel = data[0].date;
        const endLabel = data[data.length - 1].date;
        caption.textContent = `Showing ${startLabel} → ${endLabel} — max ${maxCount} borrows/day`;
        // append below container
        container.parentNode.appendChild(caption);
    })();

    console.log('📊 Analytics Dashboard Loaded Successfully');
    console.log('📈 Metrics:', metrics);
});