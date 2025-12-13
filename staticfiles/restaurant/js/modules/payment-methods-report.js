/**
 * Payment Methods Report Module
 * Handles reporting and visualization of payment method statistics
 * with monthly, daily, and weekly breakdowns
 */

const paymentMethodsReport = (() => {
    let charts = {
        monthly: null,
        daily: null,
        weekly: null
    };
    let isInitialized = false;
    let currentTab = 'monthly';

    const init = () => {
        if (isInitialized) return;
        isInitialized = true;
        console.log('✅ Payment Methods Report Module loaded');
        setupEventListeners();
    };

    const setupEventListeners = () => {
        console.log('📋 Setting up event listeners, DOM state:', document.readyState);
        
        if (document.readyState === 'loading') {
            console.log('⏳ DOM still loading, deferring setup');
            document.addEventListener('DOMContentLoaded', setupEventListeners);
            return;
        }

        // Tab switching
        const tabs = document.querySelectorAll('[data-payment-tab]');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                currentTab = e.target.dataset.paymentTab;
                console.log(`📊 Switching to tab: ${currentTab}`);
                switchTab(currentTab);
            });
        });

        console.log('📊 Cargando reporte inicial de métodos de pago');
        loadPaymentReport();
    };

    const switchTab = (tabName) => {
        // Update active tab button
        const tabs = document.querySelectorAll('[data-payment-tab]');
        tabs.forEach(t => {
            t.classList.remove('active', 'text-amber-900', 'border-b-2', 'border-amber-900');
            t.classList.add('text-gray-700');
        });
        
        const activeTab = document.querySelector(`[data-payment-tab="${tabName}"]`);
        if (activeTab) {
            activeTab.classList.add('active', 'text-amber-900', 'border-b-2', 'border-amber-900');
            activeTab.classList.remove('text-gray-700');
        }

        // Show/hide content
        const contents = document.querySelectorAll('[data-payment-content]');
        contents.forEach(c => c.classList.add('hidden'));
        
        const content = document.querySelector(`[data-payment-content="${tabName}"]`);
        if (content) {
            content.classList.remove('hidden');
            // Trigger chart resize on tab change
            setTimeout(() => {
                if (charts[tabName]) charts[tabName].resize();
            }, 100);
        }
    };

    const loadPaymentReport = async () => {
        try {
            console.log('🌐 Solicitando reporte de métodos de pago');
            const response = await fetch('/restaurant/api/payment-methods-report/');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const reportData = await response.json();
            console.log('✅ Datos recibidos:', reportData);
            renderPaymentReport(reportData);
        } catch (error) {
            console.error('❌ Error loading payment report:', error);
            if (typeof showToast !== 'undefined') {
                showToast('Error al cargar reporte de métodos de pago', 'error');
            } else {
                alert('Error: ' + error.message);
            }
        }
    };

    const renderPaymentReport = (data) => {
        // Render tables and charts
        renderMonthlyData(data.monthly, data.summary);
        renderDailyData(data.daily, data.summary);
        renderWeeklyData(data.weekly, data.summary);
        
        // Render summary at the end
        renderSummary(data.summary, data.month);
        
        // Switch to initial tab
        switchTab('monthly');
    };

    const renderSummary = (summary, month) => {
        const container = document.getElementById('payment-methods-summary');
        if (!container) return;

        const html = `
            <div class="mb-6">
                <h2 class="text-2xl font-bold text-amber-900 mb-4">${month}</h2>
                <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
                    <div class="bg-blue-50 p-4 rounded-lg text-center">
                        <p class="text-gray-600 text-sm font-medium">Total Órdenes</p>
                        <p class="text-2xl font-bold text-blue-600">${summary.total_orders}</p>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg text-center">
                        <p class="text-gray-600 text-sm font-medium">Ventas Totales</p>
                        <p class="text-2xl font-bold text-green-600">$${summary.grand_total.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</p>
                    </div>
                    <div class="bg-purple-50 p-4 rounded-lg text-center">
                        <p class="text-gray-600 text-sm font-medium">Propinas</p>
                        <p class="text-2xl font-bold text-purple-600">$${summary.grand_tips.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</p>
                    </div>
                    <div class="bg-orange-50 p-4 rounded-lg text-center">
                        <p class="text-gray-600 text-sm font-medium">Ticket Promedio</p>
                        <p class="text-2xl font-bold text-orange-600">$${summary.average_order.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</p>
                    </div>
                    <div class="bg-indigo-50 p-4 rounded-lg text-center">
                        <p class="text-gray-600 text-sm font-medium">Propina Promedio</p>
                        <p class="text-2xl font-bold text-indigo-600">$${summary.average_tip.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</p>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
    };

    const renderMonthlyData = (monthlyStats, summary) => {
        const container = document.getElementById('payment-methods-monthly-content');
        if (!container) return;

        let html = `
            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-lg font-bold text-amber-900 mb-4">Métodos de Pago</h3>
                
                <!-- Chart -->
                <div id="payment-methods-chart-monthly" class="mb-6 h-72 flex justify-center">
                    <canvas id="chart-monthly"></canvas>
                </div>

                <!-- Table -->
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-gray-100 border-b-2 border-gray-300">
                            <tr>
                                <th class="px-4 py-3 text-left font-semibold text-gray-700">Método</th>
                                <th class="px-4 py-3 text-center font-semibold text-gray-700">Órdenes</th>
                                <th class="px-4 py-3 text-right font-semibold text-gray-700">Total</th>
                                <th class="px-4 py-3 text-right font-semibold text-gray-700">Propinas</th>
                                <th class="px-4 py-3 text-right font-semibold text-gray-700">Promedio</th>
                                <th class="px-4 py-3 text-center font-semibold text-gray-700">Porcentaje</th>
                            </tr>
                        </thead>
                        <tbody>
        `;

        if (monthlyStats.length === 0) {
            html += `<tr><td colspan="6" class="px-4 py-8 text-center text-gray-500">No hay datos</td></tr>`;
        } else {
            const methodSVGs = {
                'cash': '<svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
                'card': '<svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>',
                'transfer': '<svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path></svg>',
                'check': '<svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
                'mixed': '<svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>'
            };

            monthlyStats.forEach(stat => {
                const svg = methodSVGs[stat.method] || '<svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
                html += `
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                        <td class="px-4 py-3 font-medium">${svg} ${stat.method_display}</td>
                        <td class="px-4 py-3 text-center">${stat.count}</td>
                        <td class="px-4 py-3 text-right font-semibold">$${stat.total.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</td>
                        <td class="px-4 py-3 text-right text-purple-600">$${stat.total_tips.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</td>
                        <td class="px-4 py-3 text-right">$${stat.average.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</td>
                        <td class="px-4 py-3 text-center"><span class="font-semibold">${stat.percentage}%</span></td>
                    </tr>
                `;
            });
        }

        html += `
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        container.innerHTML = html;
        renderMonthlyChart(monthlyStats);
    };

    const renderMonthlyChart = (monthlyStats) => {
        const ctx = document.getElementById('chart-monthly')?.getContext('2d');
        if (!ctx || monthlyStats.length === 0) return;

        const labels = monthlyStats.map(s => s.method_display);
        const data = monthlyStats.map(s => s.total);
        const colors = [
            'rgba(34, 197, 94, 0.8)',
            'rgba(59, 130, 246, 0.8)',
            'rgba(168, 85, 247, 0.8)',
            'rgba(249, 115, 22, 0.8)',
            'rgba(239, 68, 68, 0.8)'
        ];

        if (charts.monthly) charts.monthly.destroy();

        charts.monthly = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors.slice(0, labels.length),
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 10,
                            font: { size: 11, weight: '500' },
                            usePointStyle: true,
                            boxWidth: 12
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = ((value / total) * 100).toFixed(1);
                                return `$${value.toLocaleString('es-CL', { maximumFractionDigits: 0 })} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    };

    const renderDailyData = (dailyStats, summary) => {
        const container = document.getElementById('payment-methods-daily-content');
        if (!container) return;

        let html = `
            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-lg font-bold text-amber-900 mb-4">Ventas por Día</h3>
                
                <!-- Chart -->
                <div id="payment-methods-chart-daily" class="mb-6 h-64">
                    <canvas id="chart-daily"></canvas>
                </div>

                <!-- Table -->
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-gray-100 border-b-2 border-gray-300">
                            <tr>
                                <th class="px-4 py-3 text-left font-semibold text-gray-700">Fecha</th>
                                <th class="px-4 py-3 text-center font-semibold text-gray-700">Órdenes</th>
                                <th class="px-4 py-3 text-right font-semibold text-gray-700">Total</th>
                                <th class="px-4 py-3 text-right font-semibold text-gray-700">Propinas</th>
                                <th class="px-4 py-3 text-right font-semibold text-gray-700">Promedio</th>
                            </tr>
                        </thead>
                        <tbody>
        `;

        if (dailyStats.length === 0) {
            html += `<tr><td colspan="5" class="px-4 py-8 text-center text-gray-500">No hay datos</td></tr>`;
        } else {
            dailyStats.forEach(stat => {
                html += `
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                        <td class="px-4 py-3 font-medium">${stat.date}</td>
                        <td class="px-4 py-3 text-center">${stat.count}</td>
                        <td class="px-4 py-3 text-right font-semibold">$${stat.total.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</td>
                        <td class="px-4 py-3 text-right text-purple-600">$${stat.total_tips.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</td>
                        <td class="px-4 py-3 text-right">$${stat.average.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</td>
                    </tr>
                `;
            });
        }

        html += `
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        container.innerHTML = html;
        renderDailyChart(dailyStats);
    };

    const renderDailyChart = (dailyStats) => {
        const ctx = document.getElementById('chart-daily')?.getContext('2d');
        if (!ctx || dailyStats.length === 0) return;

        const labels = dailyStats.map(s => s.date);
        const data = dailyStats.map(s => s.total);

        if (charts.daily) charts.daily.destroy();

        charts.daily = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Ventas Diarias',
                    data: data,
                    backgroundColor: 'rgba(251, 146, 60, 0.8)',
                    borderColor: 'rgba(251, 146, 60, 1)',
                    borderWidth: 1
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
                        callbacks: {
                            label: function(context) {
                                return `$${context.raw.toLocaleString('es-CL', { maximumFractionDigits: 0 })}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString('es-CL', { maximumFractionDigits: 0 });
                            }
                        }
                    }
                }
            }
        });
    };

    const renderWeeklyData = (weeklyStats, summary) => {
        const container = document.getElementById('payment-methods-weekly-content');
        if (!container) return;

        let html = `
            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-lg font-bold text-amber-900 mb-4">Ventas por Semana</h3>
                
                <!-- Chart -->
                <div id="payment-methods-chart-weekly" class="mb-6 h-64">
                    <canvas id="chart-weekly"></canvas>
                </div>

                <!-- Table -->
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-gray-100 border-b-2 border-gray-300">
                            <tr>
                                <th class="px-4 py-3 text-left font-semibold text-gray-700">Semana</th>
                                <th class="px-4 py-3 text-center font-semibold text-gray-700">Órdenes</th>
                                <th class="px-4 py-3 text-right font-semibold text-gray-700">Total</th>
                                <th class="px-4 py-3 text-right font-semibold text-gray-700">Propinas</th>
                                <th class="px-4 py-3 text-right font-semibold text-gray-700">Promedio</th>
                            </tr>
                        </thead>
                        <tbody>
        `;

        if (weeklyStats.length === 0) {
            html += `<tr><td colspan="5" class="px-4 py-8 text-center text-gray-500">No hay datos</td></tr>`;
        } else {
            weeklyStats.forEach(stat => {
                html += `
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                        <td class="px-4 py-3 font-medium">${stat.week}</td>
                        <td class="px-4 py-3 text-center">${stat.count}</td>
                        <td class="px-4 py-3 text-right font-semibold">$${stat.total.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</td>
                        <td class="px-4 py-3 text-right text-purple-600">$${stat.total_tips.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</td>
                        <td class="px-4 py-3 text-right">$${stat.average.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</td>
                    </tr>
                `;
            });
        }

        html += `
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        container.innerHTML = html;
        renderWeeklyChart(weeklyStats);
    };

    const renderWeeklyChart = (weeklyStats) => {
        const ctx = document.getElementById('chart-weekly')?.getContext('2d');
        if (!ctx || weeklyStats.length === 0) return;

        const labels = weeklyStats.map(s => s.week);
        const data = weeklyStats.map(s => s.total);

        if (charts.weekly) charts.weekly.destroy();

        charts.weekly = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Ventas Semanales',
                    data: data,
                    borderColor: 'rgba(59, 130, 246, 1)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
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
                        callbacks: {
                            label: function(context) {
                                return `$${context.raw.toLocaleString('es-CL', { maximumFractionDigits: 0 })}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString('es-CL', { maximumFractionDigits: 0 });
                            }
                        }
                    }
                }
            }
        });
    };


    return {
        init: init,
        loadReport: loadPaymentReport
    };
})();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('📍 DOMContentLoaded event fired');
        paymentMethodsReport.init();
    });
} else {
    console.log('📍 DOM already loaded, initializing immediately');
    paymentMethodsReport.init();
}
