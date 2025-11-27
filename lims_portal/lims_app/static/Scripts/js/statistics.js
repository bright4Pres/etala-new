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
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
    Chart.defaults.color = '#6b7280';

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
                    borderColor: '#3b82f6',              // Blue line color
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',  // Light blue fill under line
                    borderWidth: 3,
                    fill: true,                          // Fill area under line
                    tension: 0.4,                        // Curve the line (0 = straight, 1 = very curved)
                    
                    // Point styling for data markers
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    
                    // Hover state styling
                    pointHoverBackgroundColor: '#2563eb',
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
                    backgroundColor: '#8b5cf6',          // Purple bar color
                    borderRadius: 8,                     // Rounded corners on bars
                    borderSkipped: false,                // Round all corners, not just top
                    hoverBackgroundColor: '#7c3aed'      // Darker purple on hover
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
            '#06b6d4', '#14b8a6', '#84cc16', '#eab308', '#f97316',
            '#ef4444', '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b',
            '#a21caf', '#6366f1', '#0ea5e9', '#f43f5e', '#22d3ee',
            '#e11d48', '#facc15', '#16a34a', '#7c3aed', '#f472b6'
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
    if (periodSelect) {
        periodSelect.addEventListener('change', function() {
            const selectedPeriod = this.value;
            // Redirect to same page with new period parameter
            window.location.href = '?period=' + selectedPeriod;
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

    /* ==========================================
       CALENDAR HEATMAP RENDERER
       GitHub-style activity heatmap showing daily borrow counts
       ========================================== */
    (function renderCalendarHeatmap() {
        // Get heatmap data from metrics object
        const heatmap = metrics.heatmapData || null;
        const container = document.getElementById('calendar-heatmap');
        
        // Exit early if no data or container
        if (!heatmap || !container || !Array.isArray(heatmap) || heatmap.length === 0) return;

        // Data format: [{ date: 'YYYY-MM-DD', count: N }, ...]
        // Already sorted oldest->newest by Django backend
        const data = heatmap.slice();
        
        // Calculate grid dimensions
        const firstDate = new Date(data[0].date + 'T00:00:00');
        const startDow = firstDate.getDay();  // Day of week (0=Sunday, 6=Saturday)
        const days = data.length;
        const weeks = Math.ceil((startDow + days) / 7);  // Number of week columns needed

        /* ------------------------------------------
           RESPONSIVE CELL SIZING
           Adjust cell size based on date range
           ------------------------------------------ */
        let cellSize = 14;  // Default size
        if (days <= 14) cellSize = 32;        // Large cells for week view
        else if (days <= 31) cellSize = 22;   // Medium cells for month view
        else if (days <= 62) cellSize = 16;   // Smaller for 2 months
        else if (days <= 366) cellSize = 20;  // Comfortable for year view

        // Center grid if not filling full width
        let gridJustify = 'center';

        /* ------------------------------------------
           COLOR SCALING CALCULATION
           Find max count for relative intensity scaling
           ------------------------------------------ */
        const maxCount = data.reduce((m, d) => Math.max(m, d.count || 0), 0);

        // Color palette: 5 intensity levels (0=none, 4=most activity)
        const colors = ['#a8a8a8ff', '#c6e48b', '#7bc96f', '#239a3b', '#196127'];

        /**
         * Determine color intensity level based on count
         * @param {number} count - Number of borrows on this day
         * @returns {number} Level from 0-4
         */
        function getLevel(count) {
            if (!count || maxCount === 0) return 0;
            const ratio = count / maxCount;
            if (ratio <= 0.2) return 1;
            if (ratio <= 0.4) return 2;
            if (ratio <= 0.7) return 3;
            return 4;
        }

        /* ------------------------------------------
           BUILD GRID CONTAINER
           ------------------------------------------ */
        container.innerHTML = '';  // Clear any existing content
        container.style.display = 'grid';
        container.style.gridTemplateRows = `repeat(7, ${cellSize}px)`;      // 7 rows (days of week)
        container.style.gridTemplateColumns = `repeat(${weeks}, ${cellSize}px)`;  // N columns (weeks)
        container.style.gap = `${Math.max(2, Math.round(cellSize / 7))}px`;  // Proportional gap
        container.style.alignItems = 'center';
        container.style.justifyItems = 'center';
        container.style.justifyContent = gridJustify;
        container.style.padding = '12px 0';

        /* ------------------------------------------
           CREATE DAY CELLS
           Fill grid week by week, row by row
           ------------------------------------------ */
        for (let w = 0; w < weeks; w++) {           // For each week column
            for (let d = 0; d < 7; d++) {           // For each day row (0-6)
                // Calculate which day in our data array this represents
                const globalIndex = w * 7 + d - startDow;
                
                // Create cell element
                const cell = document.createElement('div');
                cell.className = 'heatday';
                cell.style.width = `${cellSize}px`;
                cell.style.height = `${cellSize}px`;
                cell.style.borderRadius = `${Math.round(cellSize/4)}px`;
                cell.style.boxSizing = 'border-box';
                cell.style.background = colors[0];  // Default to gray (no data)
                cell.style.cursor = 'default';
                cell.style.transition = 'transform 120ms ease';

                // If this cell represents a valid data day
                if (globalIndex >= 0 && globalIndex < days) {
                    const item = data[globalIndex];
                    const cnt = item.count || 0;
                    const lvl = getLevel(cnt);
                    
                    // Apply color based on activity level
                    cell.style.background = colors[lvl];
                    cell.title = `${item.date}: ${cnt} borrows`;
                    cell.setAttribute('data-count', cnt);
                    cell.setAttribute('data-date', item.date);
                    
                    // Hover effect - slight scale up
                    cell.addEventListener('mouseenter', () => { 
                        cell.style.transform = 'scale(1.15)'; 
                    });
                    cell.addEventListener('mouseleave', () => { 
                        cell.style.transform = 'scale(1)'; 
                    });
                } else {
                    // Empty cell (before first date or after last date)
                    cell.title = '';
                    cell.setAttribute('aria-hidden', 'true');
                    cell.style.opacity = '0.3';
                }

                container.appendChild(cell);
            }
        }

        /* ------------------------------------------
           SYNCHRONIZE LEGEND COLORS
           Update legend boxes to match actual colors used
           ------------------------------------------ */
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

        /* ------------------------------------------
           ADD CAPTION WITH DATE RANGE INFO
           Shows date range and max activity
           ------------------------------------------ */
        const caption = document.createElement('div');
        caption.style.fontSize = '12px';
        caption.style.color = '#6b7280';
        caption.style.marginTop = '8px';
        const startLabel = data[0].date;
        const endLabel = data[data.length - 1].date;
        caption.textContent = `Showing ${startLabel} → ${endLabel} — max ${maxCount} borrows/day`;
        container.parentNode.appendChild(caption);
    })();

    /* ==========================================
       INITIALIZATION COMPLETE
       Log success message to console
       ========================================== */
    console.log('📊 Analytics Dashboard Loaded Successfully');
    console.log('📈 Metrics:', metrics);
});