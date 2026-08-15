document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadKPIs();
    loadQ1Chart();
    loadQ2Chart();
    loadQ3Chart();
    loadQ4Map();
});

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetTab = document.getElementById(btn.dataset.tab);
            if (targetTab) {
                targetTab.classList.add('active');
            }
        });
    });
}

function loadKPIs() {
    fetch('/api/kpis')
        .then(res => res.json())
        .then(data => {
            document.getElementById('kpiRevenue').innerText = `£${(data.total_revenue).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('kpiOrders').innerText = (data.total_orders).toLocaleString();
            document.getElementById('kpiCustomers').innerText = (data.total_customers).toLocaleString();
            document.getElementById('kpiAOV').innerText = `£${(data.aov).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('kpiUnits').innerText = (data.total_units).toLocaleString();
        })
        .catch(err => console.error('Error loading KPIs:', err));
}

let q1Chart, q2Chart, q3Chart;

function loadQ1Chart() {
    fetch('/api/q1-monthly-trend')
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById('q1Canvas').getContext('2d');
            
            q1Chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.months,
                    datasets: [{
                        label: '2011 Revenue (£)',
                        data: data.revenue,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.15)',
                        borderWidth: 3,
                        pointRadius: 6,
                        pointBackgroundColor: '#60a5fa',
                        fill: true,
                        tension: 0.35
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return ` Revenue: £${context.raw.toLocaleString()}`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(255,255,255,0.05)' },
                            ticks: { color: '#94a3b8' }
                        },
                        y: {
                            grid: { color: 'rgba(255,255,255,0.08)' },
                            ticks: { 
                                color: '#94a3b8',
                                callback: value => `£${(value/1e3).toFixed(0)}k`
                            }
                        }
                    }
                }
            });

            // Populate table
            const tbody = document.getElementById('q1TableBody');
            tbody.innerHTML = '';
            data.months.forEach((m, idx) => {
                const rev = data.revenue[idx];
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${m} 2011</strong></td>
                    <td style="color: #60a5fa; font-weight: 700;">£${rev.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                `;
                tbody.appendChild(tr);
            });
        });
}

function loadQ2Chart() {
    fetch('/api/q2-top10-countries')
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById('q2Canvas').getContext('2d');
            
            q2Chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.countries,
                    datasets: [
                        {
                            label: 'Revenue (£)',
                            data: data.revenue,
                            backgroundColor: '#2563eb',
                            borderRadius: 6,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Quantity Sold (Units)',
                            data: data.quantity,
                            backgroundColor: '#10b981',
                            borderRadius: 6,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#f8fafc', font: { weight: '600' } } }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(255,255,255,0.05)' },
                            ticks: { color: '#94a3b8' }
                        },
                        y: {
                            type: 'linear',
                            position: 'left',
                            title: { display: true, text: 'Revenue (£)', color: '#60a5fa' },
                            grid: { color: 'rgba(255,255,255,0.08)' },
                            ticks: { 
                                color: '#94a3b8',
                                callback: value => `£${(value/1e3).toFixed(0)}k`
                            }
                        },
                        y1: {
                            type: 'linear',
                            position: 'right',
                            title: { display: true, text: 'Quantity Sold (Units)', color: '#34d399' },
                            grid: { drawOnChartArea: false },
                            ticks: { 
                                color: '#94a3b8',
                                callback: value => `${(value/1e3).toFixed(0)}k`
                            }
                        }
                    }
                }
            });

            // Populate table
            const tbody = document.getElementById('q2TableBody');
            tbody.innerHTML = '';
            data.countries.forEach((c, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>#${idx+1} ${c}</strong></td>
                    <td style="color: #60a5fa; font-weight: 700;">£${data.revenue[idx].toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td style="color: #34d399; font-weight: 700;">${data.quantity[idx].toLocaleString()} units</td>
                `;
                tbody.appendChild(tr);
            });
        });
}

function loadQ3Chart() {
    fetch('/api/q3-top10-customers')
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById('q3Canvas').getContext('2d');
            
            q3Chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.customer_ids.map(id => `Customer ${id}`),
                    datasets: [{
                        label: 'Total Spend (£)',
                        data: data.revenue,
                        backgroundColor: '#8b5cf6',
                        borderRadius: 8,
                        hoverBackgroundColor: '#a78bfa'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const idx = context.dataIndex;
                                    return [
                                        ` Total Spend: £${context.raw.toLocaleString()}`,
                                        ` Orders Placed: ${data.orders[idx]} orders`,
                                        ` Units Bought: ${data.quantity[idx].toLocaleString()} items`
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(255,255,255,0.05)' },
                            ticks: { color: '#94a3b8' }
                        },
                        y: {
                            grid: { color: 'rgba(255,255,255,0.08)' },
                            ticks: { 
                                color: '#94a3b8',
                                callback: value => `£${(value/1e3).toFixed(0)}k`
                            }
                        }
                    }
                }
            });

            // Populate table
            const tbody = document.getElementById('q3TableBody');
            tbody.innerHTML = '';
            data.customer_ids.forEach((cid, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><span class="badge badge-rank">#${idx+1}</span></td>
                    <td><strong>Customer ${cid}</strong></td>
                    <td style="color: #c084fc; font-weight: 700;">£${data.revenue[idx].toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td>${data.orders[idx]} orders</td>
                    <td>${data.quantity[idx].toLocaleString()} items</td>
                `;
                tbody.appendChild(tr);
            });
        });
}

function loadQ4Map() {
    fetch('/api/q4-global-map')
        .then(res => res.json())
        .then(data => {
            // Render Plotly choropleth or bubble world map
            const mapData = [{
                type: 'choropleth',
                locationmode: 'country names',
                locations: data.countries,
                z: data.quantity,
                text: data.countries.map((c, i) => `${c}<br>Demand: ${data.quantity[i].toLocaleString()} units<br>Revenue: £${data.revenue[i].toLocaleString()}`),
                colorscale: [
                    [0, '#06b6d4'],
                    [0.2, '#0284c7'],
                    [0.5, '#2563eb'],
                    [0.8, '#7c3aed'],
                    [1, '#d946ef']
                ],
                autocolorscale: false,
                reversescale: false,
                colorbar: {
                    title: 'Units Sold',
                    tickfont: { color: '#ffffff' },
                    titlefont: { color: '#ffffff' }
                }
            }];

            const layout = {
                geo: {
                    showframe: false,
                    showcoastlines: true,
                    projection: { type: 'mercator' },
                    bgcolor: '#0f172a',
                    lakecolor: '#1e293b',
                    landcolor: '#1e293b',
                    subunitcolor: '#334155',
                    countrycolor: '#475569'
                },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                margin: { l: 0, r: 0, t: 0, b: 0 }
            };

            Plotly.newPlot('mapContainer', mapData, layout, {responsive: true, displayModeBar: false});

            // Populate table
            const tbody = document.getElementById('q4TableBody');
            tbody.innerHTML = '';
            data.countries.forEach((c, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>#${idx+1} ${c}</strong></td>
                    <td style="color: #22d3ee; font-weight: 700;">${data.quantity[idx].toLocaleString()} units</td>
                    <td style="color: #60a5fa; font-weight: 700;">£${data.revenue[idx].toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td>${data.orders[idx]} orders</td>
                `;
                tbody.appendChild(tr);
            });
        });
}
