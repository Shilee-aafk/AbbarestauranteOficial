/**
 * RoomBill Manager - Gestiona la creación y pago de facturas de habitación
 */

class RoomBillManager {
    constructor() {
        this.selectedOrders = {};
        this.selectedBillStatuses = new Set(['draft']); // Estados seleccionados por defecto
        this.billDateFrom = null;
        this.billDateTo = null;
        this.csrfToken = this.getCsrfToken();
        this.init();
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('input[name="csrfmiddlewaretoken"]')?.value ||
               document.body.getAttribute('data-csrf-token') || '';
    }

    init() {
        this.setupTabListeners();
        this.setupFilterListeners();
        this.setupExportListener();
        this.loadInitialData();
    }

    setupTabListeners() {
        document.querySelectorAll('.room-bill-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(tab.dataset.tab);
            });
        });
    }

    setupFilterListeners() {
        // Filtro de búsqueda de habitaciones
        const searchInput = document.getElementById('room-search-input');
        const clearBtn = document.getElementById('clear-search-btn');
        const dateFromInput = document.getElementById('date-from');
        const dateToInput = document.getElementById('date-to');
        const clearDateBtn = document.getElementById('clear-date-filter-btn');
        
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                this.filterRoomsBySearch(searchInput.value);
            });
        }
        
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                searchInput.value = '';
                this.loadUnpaidOrders();
            });
        }

        // Filtro por fecha
        if (dateFromInput) {
            dateFromInput.addEventListener('change', () => {
                this.filterRoomsByDateRange();
            });
        }

        if (dateToInput) {
            dateToInput.addEventListener('change', () => {
                this.filterRoomsByDateRange();
            });
        }

        if (clearDateBtn) {
            clearDateBtn.addEventListener('click', () => {
                dateFromInput.value = '';
                dateToInput.value = '';
                this.loadUnpaidOrders();
            });
        }

        // Filtro de estado de facturas - permite seleccionar múltiples
        document.querySelectorAll('.bill-status-filter').forEach(btn => {
            btn.addEventListener('click', () => {
                const status = btn.dataset.status;
                
                if (status === 'all') {
                    // Si se hace clic en "Todas", mostrar todas
                    this.selectedBillStatuses = new Set(['draft', 'confirmed', 'paid', 'cancelled']);
                    this.filterBillsBySelectedStatuses();
                    this.updateMultipleFilterButtons();
                } else {
                    // Toggle del estado seleccionado
                    if (this.selectedBillStatuses.has(status)) {
                        this.selectedBillStatuses.delete(status);
                    } else {
                        this.selectedBillStatuses.add(status);
                    }
                    
                    // Si no hay ninguno seleccionado, seleccionar el actual
                    if (this.selectedBillStatuses.size === 0) {
                        this.selectedBillStatuses.add(status);
                    }
                    
                    this.filterBillsBySelectedStatuses();
                    this.updateMultipleFilterButtons();
                }
            });
        });

        // Filtros de fecha para las facturas
        const billsDateFromInput = document.getElementById('bills-date-from');
        const billsDateToInput = document.getElementById('bills-date-to');
        const clearBillsDateBtn = document.getElementById('clear-bills-date-btn');

        if (billsDateFromInput) {
            billsDateFromInput.addEventListener('change', () => {
                this.billDateFrom = billsDateFromInput.value;
                this.filterBillsBySelectedStatuses();
            });
        }

        if (billsDateToInput) {
            billsDateToInput.addEventListener('change', () => {
                this.billDateTo = billsDateToInput.value;
                this.filterBillsBySelectedStatuses();
            });
        }

        if (clearBillsDateBtn) {
            clearBillsDateBtn.addEventListener('click', () => {
                billsDateFromInput.value = '';
                billsDateToInput.value = '';
                this.billDateFrom = null;
                this.billDateTo = null;
                this.filterBillsBySelectedStatuses();
            });
        }
    }

    updateMultipleFilterButtons() {
        document.querySelectorAll('.bill-status-filter').forEach(b => {
            const status = b.dataset.status;
            
            if (status === 'all') {
                if (this.selectedBillStatuses.size === 4) {
                    b.classList.add('active', 'bg-amber-100', 'text-amber-900');
                    b.classList.remove('text-gray-700');
                } else {
                    b.classList.remove('active', 'bg-amber-100', 'text-amber-900');
                    b.classList.add('text-gray-700');
                }
            } else {
                if (this.selectedBillStatuses.has(status)) {
                    b.classList.add('active', 'bg-amber-100', 'text-amber-900');
                    b.classList.remove('text-gray-700');
                } else {
                    b.classList.remove('active', 'bg-amber-100', 'text-amber-900');
                    b.classList.add('text-gray-700');
                }
            }
        });
    }

    updateActiveFilterButton(activeBtn) {
        document.querySelectorAll('.bill-status-filter').forEach(b => {
            b.classList.remove('active', 'bg-amber-100', 'text-amber-900');
            b.classList.add('text-gray-700');
        });
        activeBtn.classList.add('active', 'bg-amber-100', 'text-amber-900');
    }

    setupExportListener() {
        const exportBtn = document.getElementById('export-bills-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportBillsWithFilters());
        }
    }

    exportBillsWithFilters() {
        // Construir URL con parámetros de filtro
        const params = new URLSearchParams();

        // Agregar estados seleccionados
        if (this.selectedBillStatuses.size > 0 && this.selectedBillStatuses.size < 4) {
            // Si no están todos seleccionados, agregar los seleccionados
            const statusesArray = Array.from(this.selectedBillStatuses);
            params.append('status', statusesArray.join(','));
        }

        // Agregar filtros de fecha
        if (this.billDateFrom) {
            params.append('date_from', this.billDateFrom);
        }
        if (this.billDateTo) {
            params.append('date_to', this.billDateTo);
        }

        // Crear URL de descarga
        const url = `/restaurant/export/roombills-excel/?${params.toString()}`;
        window.location.href = url;
    }

    loadInitialData() {
        this.loadUnpaidOrders();
        this.loadBills();
        this.loadHistory();
    }

    switchTab(tabName) {
        document.querySelectorAll('.room-bill-tab').forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active', 'text-amber-900', 'border-b-2', 'border-amber-900');
                tab.classList.remove('text-gray-700');
            } else {
                tab.classList.remove('active', 'text-amber-900', 'border-b-2', 'border-amber-900');
                tab.classList.add('text-gray-700');
            }
        });

        document.querySelectorAll('.room-bill-tab-content').forEach(content => {
            content.classList.add('hidden');
        });

        const activeContent = document.getElementById(`${tabName}-tab`);
        if (activeContent) {
            activeContent.classList.remove('hidden');

            if (tabName === 'select-orders') {
                this.loadUnpaidOrders();
            } else if (tabName === 'bills') {
                this.loadBills();
            } else if (tabName === 'history') {
                this.loadHistory();
            }
        }
    }

    async loadUnpaidOrders() {
        try {
            const response = await fetch('/restaurant/api/roombills/unpaid-orders/', {
                method: 'GET',
                headers: { 'X-CSRFToken': this.csrfToken }
            });

            if (!response.ok) throw new Error('No se pudieron cargar los pedidos');

            const data = await response.json();
            this.allRooms = data.rooms; // Guardar para el filtro
            this.renderRooms(data.rooms);
        } catch (error) {
            console.error('Error:', error);
            this.showToast('Error al cargar pedidos', 'error');
        }
    }

    applyAllFilters() {
        if (!this.allRooms) return;

        const searchInput = document.getElementById('room-search-input');
        const dateFromInput = document.getElementById('date-from');
        const dateToInput = document.getElementById('date-to');

        const searchQuery = searchInput.value.toLowerCase().trim();
        const dateFrom = dateFromInput.value ? new Date(dateFromInput.value + 'T00:00:00') : null;
        const dateTo = dateToInput.value ? new Date(dateToInput.value + 'T23:59:59') : null;

        let filtered = this.allRooms.map(room => {
            let matchesSearch = true; // Por defecto, incluir la habitación
            let isExactRoomMatch = false;
            
            if (searchQuery) {
                // Buscar por número de habitación exacto
                if (room.room_number.toLowerCase() === searchQuery) {
                    matchesSearch = true;
                    isExactRoomMatch = true;
                } else {
                    // Buscar por nombre de cliente dentro de la habitación (parcial)
                    matchesSearch = room.clients.some(client => 
                        client.name.toLowerCase().includes(searchQuery)
                    );
                }
            }

            if (!matchesSearch) return null;

            // Filtrar clientes y pedidos por fecha dentro de la habitación
            let filteredClients = room.clients.map(client => {
                // Si se busca por nombre, solo incluir clientes que coincidan
                if (searchQuery && !isExactRoomMatch) {
                    if (!client.name.toLowerCase().includes(searchQuery)) {
                        return null;
                    }
                }

                const filteredOrders = client.orders.filter(order => {
                    const orderDate = new Date(order.created_at);
                    
                    let isInRange = true;
                    if (dateFrom) isInRange = isInRange && orderDate >= dateFrom;
                    if (dateTo) isInRange = isInRange && orderDate <= dateTo;
                    
                    return isInRange;
                });

                if (filteredOrders.length === 0) return null;

                return {
                    ...client,
                    orders: filteredOrders,
                    total: filteredOrders.reduce((sum, order) => sum + order.total, 0)
                };
            }).filter(c => c !== null);

            if (filteredClients.length === 0) return null;

            return {
                ...room,
                clients: filteredClients,
                total: filteredClients.reduce((sum, client) => sum + client.total, 0)
            };
        }).filter(room => room !== null);

        // Mensaje combinado
        let filterMsg = '';
        if (searchQuery) filterMsg += `búsqueda: "${searchQuery}"`;
        if (dateFrom || dateTo) {
            if (filterMsg) filterMsg += ' + ';
            filterMsg += `${dateFrom ? dateFrom.toLocaleDateString('es-CL') : 'inicio'} - ${dateTo ? dateTo.toLocaleDateString('es-CL') : 'hoy'}`;
        }

        this.renderRooms(filtered, filterMsg);
    }

    filterRoomsBySearch(query) {
        this.applyAllFilters();
    }

    filterRoomsByDateRange() {
        this.applyAllFilters();
    }

    renderRooms(rooms, searchQuery = '') {
        const container = document.getElementById('rooms-container');
        
        if (rooms.length === 0) {
            const message = searchQuery 
                ? `No hay resultados para "${searchQuery}"`
                : 'No hay pedidos pendientes en las habitaciones.';
            container.innerHTML = `<div class="text-center py-12 text-gray-500">${message}</div>`;
            return;
        }

        container.innerHTML = rooms.map(room => `
            <div class="rounded-lg p-6 bg-amber-50" style="border: 2px solid #6F4E37;">
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-lg font-bold text-amber-900">Habitación ${room.room_number}</h3>
                    <span class="text-2xl font-bold text-amber-900">$${room.total.toFixed(2)}</span>
                </div>

                <!-- Sub-grupos por cliente -->
                <div class="space-y-4">
                    ${room.clients.map(client => `
                        <div class="bg-white rounded-lg border border-gray-200 p-4">
                            <div class="flex justify-between items-center mb-3 pb-2 border-b border-gray-100">
                                <h4 class="font-semibold text-gray-900">${client.name}</h4>
                                <button type="button" class="select-all-client-btn text-xs px-3 py-1 rounded text-white hover:opacity-90 transition font-medium" 
                                        style="background-color: #6F4E37;"
                                        data-room="${room.room_number}" 
                                        data-client="${client.name}">
                                    Seleccionar todo
                                </button>
                            </div>
                            
                            <!-- Pedidos del cliente -->
                            <div class="space-y-2 mb-4 max-h-40 overflow-y-auto">
                                ${client.orders.map(order => `
                                    <label class="flex items-start p-3 bg-gray-50 rounded cursor-pointer hover:bg-amber-50" style="border: 1px solid #6F4E37;">
                                        <input type="checkbox" class="mt-1 mr-3 order-checkbox" 
                                               data-room="${room.room_number}" 
                                               data-client="${client.name}"
                                               data-order-id="${order.id}"
                                               data-total="${order.total}">
                                        <div class="flex-1 text-sm">
                                            <div class="flex justify-between items-start">
                                                <div class="font-semibold text-gray-900">Pedido #${order.id}</div>
                                                <span class="text-xs font-bold bg-amber-100 text-amber-900 px-2 py-1 rounded">${new Date(order.created_at).toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' })}</span>
                                            </div>
                                            <div class="text-gray-700 mt-2">
                                                ${order.items.map(item => `${item.quantity}x ${item.name}`).join(', ')}
                                            </div>
                                            <div class="text-right text-amber-900 font-semibold mt-1">$${order.total.toFixed(2)}</div>
                                        </div>
                                    </label>
                                `).join('')}
                            </div>
                            
                            <!-- Subtotal del cliente -->
                            <div class="text-right text-sm font-semibold text-gray-700 pb-3 border-b border-gray-100">
                                Subtotal: $${client.total.toFixed(2)}
                            </div>
                        </div>
                    `).join('')}
                </div>

                <!-- Propina para toda la habitación -->
                <div class="mt-4 space-y-4">
                    <div>
                        <label class="block font-semibold text-amber-900 mb-2">Propina (opcional)</label>
                        
                        <!-- Botones de porcentaje -->
                        <div class="flex gap-2 mb-3">
                            <button class="tip-percentage-btn flex-1 px-3 py-2 border border-amber-300 rounded-lg text-sm font-medium text-amber-900 hover:bg-amber-100 transition" 
                                    data-room="${room.room_number}" 
                                    data-percentage="10">
                                10%
                            </button>
                            <button class="tip-percentage-btn flex-1 px-3 py-2 border border-amber-300 rounded-lg text-sm font-medium text-amber-900 hover:bg-amber-100 transition" 
                                    data-room="${room.room_number}" 
                                    data-percentage="15">
                                15%
                            </button>
                            <button class="tip-percentage-btn flex-1 px-3 py-2 border border-amber-300 rounded-lg text-sm font-medium text-amber-900 hover:bg-amber-100 transition" 
                                    data-room="${room.room_number}" 
                                    data-percentage="20">
                                20%
                            </button>
                        </div>

                        <!-- Input de propina directa -->
                        <div class="flex gap-2">
                            <input type="number" 
                                   step="0.01" 
                                   min="0" 
                                   placeholder="Monto directo" 
                                   class="room-tip flex-1 px-3 py-2 border border-amber-300 rounded-lg text-right text-amber-900 placeholder-amber-600"
                                   data-room="${room.room_number}">
                        </div>
                    </div>

                    <button class="w-full text-white px-4 py-2 rounded-lg font-semibold create-bill-btn" 
                            style="background-color: #6F4E37;" 
                            data-room="${room.room_number}">
                        Crear Factura
                    </button>
                </div>
            </div>
        `).join('');

        this.attachRoomEventListeners();
    }

    attachRoomEventListeners() {
        document.querySelectorAll('.create-bill-btn').forEach(btn => {
            btn.addEventListener('click', () => this.createBill(btn.dataset.room));
        });

        // Botones de seleccionar todo por cliente
        document.querySelectorAll('.select-all-client-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const room = btn.dataset.room;
                const clientName = btn.dataset.client;
                
                // Seleccionar todos los checkboxes del cliente
                document.querySelectorAll(
                    `.order-checkbox[data-room="${room}"][data-client="${clientName}"]`
                ).forEach(checkbox => {
                    if (!checkbox.checked) {
                        checkbox.checked = true;
                        // Disparar evento change para actualizar selectedOrders
                        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });
            });
        });

        // Botones de porcentaje de propina
        document.querySelectorAll('.tip-percentage-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const room = btn.dataset.room;
                const percentage = parseInt(btn.dataset.percentage);
                this.calculateTipPercentage(room, percentage);
            });
        });

        document.querySelectorAll('.order-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                const room = checkbox.dataset.room;
                if (checkbox.checked) {
                    if (!this.selectedOrders[room]) this.selectedOrders[room] = [];
                    if (!this.selectedOrders[room].includes(parseInt(checkbox.dataset.orderId))) {
                        this.selectedOrders[room].push(parseInt(checkbox.dataset.orderId));
                    }
                } else if (this.selectedOrders[room]) {
                    this.selectedOrders[room] = this.selectedOrders[room].filter(
                        id => id !== parseInt(checkbox.dataset.orderId)
                    );
                }
            });
        });
    }

    calculateTipPercentage(room, percentage) {
        // Obtener el total de la habitación
        const selectedCheckboxes = document.querySelectorAll(
            `.order-checkbox[data-room="${room}"]:checked`
        );

        if (selectedCheckboxes.length === 0) {
            this.showToast('Selecciona al menos un pedido para calcular la propina', 'info');
            return;
        }

        let total = 0;
        selectedCheckboxes.forEach(checkbox => {
            total += parseFloat(checkbox.dataset.total);
        });

        const tipAmount = (total * percentage) / 100;
        const tipInput = document.querySelector(`.room-tip[data-room="${room}"]`);
        if (tipInput) {
            tipInput.value = tipAmount.toFixed(2);
        }
    }

    async createBill(roomNumber) {
        const selectedCheckboxes = document.querySelectorAll(
            `.order-checkbox[data-room="${roomNumber}"]:checked`
        );

        if (selectedCheckboxes.length === 0) {
            this.showToast('Debes seleccionar al menos un pedido', 'error');
            return;
        }

        const orderIds = Array.from(selectedCheckboxes).map(cb => parseInt(cb.dataset.orderId));
        const tipInput = document.querySelector(`.room-tip[data-room="${roomNumber}"]`);
        const tipAmount = parseFloat(tipInput.value) || 0;

        try {
            const response = await fetch('/restaurant/api/roombills/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    room_number: roomNumber,
                    guest_name: '',
                    order_ids: orderIds,
                    tip_amount: tipAmount
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Error al crear factura');
            }

            this.showToast(`Factura #${data.bill_id} creada correctamente`, 'success');
            selectedCheckboxes.forEach(cb => cb.checked = false);
            tipInput.value = '0';
            
            this.loadUnpaidOrders();
            this.loadBills();
        } catch (error) {
            console.error('Error:', error);
            this.showToast(error.message || 'Error al crear factura', 'error');
        }
    }

    async loadBills() {
        try {
            const response = await fetch('/restaurant/api/roombills/?status=all', {
                method: 'GET',
                headers: { 'X-CSRFToken': this.csrfToken }
            });

            if (!response.ok) throw new Error('Error al cargar facturas');

            const data = await response.json();
            const draftBills = data.bills.filter(b => b.status === 'draft' || b.status === 'confirmed');
            this.renderBills(draftBills);
        } catch (error) {
            console.error('Error:', error);
            this.showToast('Error al cargar facturas', 'error');
        }
    }

    filterBillsByStatus(status) {
        fetch('/restaurant/api/roombills/?status=all', {
            method: 'GET',
            headers: { 'X-CSRFToken': this.csrfToken }
        })
        .then(r => r.json())
        .then(data => {
            const filtered = status === 'all' 
                ? data.bills.filter(b => b.status === 'draft' || b.status === 'confirmed')
                : data.bills.filter(b => b.status === status);
            this.renderBills(filtered);
        })
        .catch(error => {
            console.error('Error:', error);
            this.showToast('Error al filtrar facturas', 'error');
        });
    }

    filterBillsBySelectedStatuses() {
        fetch('/restaurant/api/roombills/?status=all', {
            method: 'GET',
            headers: { 'X-CSRFToken': this.csrfToken }
        })
        .then(r => r.json())
        .then(data => {
            let filtered = data.bills.filter(b => this.selectedBillStatuses.has(b.status));
            
            // Aplicar filtro de fecha
            if (this.billDateFrom || this.billDateTo) {
                filtered = filtered.filter(bill => {
                    const billDate = new Date(bill.created_at);
                    
                    let isInRange = true;
                    if (this.billDateFrom) {
                        const dateFrom = new Date(this.billDateFrom + 'T00:00:00');
                        isInRange = isInRange && billDate >= dateFrom;
                    }
                    if (this.billDateTo) {
                        const dateTo = new Date(this.billDateTo + 'T23:59:59');
                        isInRange = isInRange && billDate <= dateTo;
                    }
                    
                    return isInRange;
                });
            }
            
            this.renderBills(filtered);
        })
        .catch(error => {
            console.error('Error:', error);
            this.showToast('Error al filtrar facturas', 'error');
        });
    }

    renderBills(bills) {
        const tbody = document.getElementById('bills-tbody');

        if (bills.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center py-12 text-gray-500">No hay facturas en este estado.</td></tr>';
            return;
        }

        tbody.innerHTML = bills.map(bill => `
            <tr class="border-b border-gray-100 hover:bg-gray-50">
                <td class="py-4 font-semibold text-gray-900">Habitación ${bill.room_number}</td>
                <td class="py-4">
                    <span class="px-3 py-1 rounded-full text-sm font-semibold ${bill.status_class}">
                        ${bill.status_display}
                    </span>
                </td>
                <td class="py-4">${bill.order_count} pedidos</td>
                <td class="py-4 font-semibold">$${bill.total.toFixed(2)}</td>
                <td class="py-4 text-sm text-gray-600">${new Date(bill.created_at).toLocaleDateString()}</td>
                <td class="py-4 space-x-2 flex">
                    <button class="text-blue-600 hover:text-blue-800 font-medium view-bill-btn" data-bill-id="${bill.id}">Ver</button>
                    ${bill.status === 'draft' ? `
                        <button class="text-green-600 hover:text-green-800 font-medium confirm-bill-btn" data-bill-id="${bill.id}">Confirmar</button>
                        <button class="text-red-600 hover:text-red-800 font-medium delete-bill-btn" data-bill-id="${bill.id}">Cancelar</button>
                    ` : bill.status === 'confirmed' ? `
                        <button class="text-green-600 hover:text-green-800 font-medium pay-bill-quick-btn" data-bill-id="${bill.id}">Pagar</button>
                        <button class="text-red-600 hover:text-red-800 font-medium delete-bill-btn" data-bill-id="${bill.id}">Cancelar</button>
                    ` : ''}
                </td>
            </tr>
        `).join('');

        this.attachBillEventListeners();
    }

    attachBillEventListeners() {
        document.querySelectorAll('.view-bill-btn').forEach(btn => {
            btn.addEventListener('click', () => this.viewBillDetail(btn.dataset.billId));
        });

        document.querySelectorAll('.confirm-bill-btn').forEach(btn => {
            btn.addEventListener('click', () => this.confirmBill(btn.dataset.billId));
        });

        document.querySelectorAll('.pay-bill-quick-btn').forEach(btn => {
            btn.addEventListener('click', () => this.viewBillDetail(btn.dataset.billId, true));
        });

        document.querySelectorAll('.delete-bill-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (confirm('¿Cancelar esta factura?')) {
                    this.cancelBill(btn.dataset.billId);
                }
            });
        });
    }

    async viewBillDetail(billId, quickPay = false) {
        try {
            const response = await fetch(`/restaurant/api/roombills/${billId}/`, {
                method: 'GET',
                headers: { 'X-CSRFToken': this.csrfToken }
            });

            const bill = await response.json();
            this.showBillModal(bill, quickPay);
        } catch (error) {
            console.error('Error:', error);
            this.showToast('Error al cargar detalle de factura', 'error');
        }
    }

    showBillModal(bill, quickPay = false) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="modal-container bg-amber-50 rounded-lg shadow-xl w-full max-w-md max-h-[90vh] flex flex-col">
                <!-- Modal Header -->
                <div class="p-6 border-b border-amber-300 bg-amber-50">
                    <div class="flex justify-between items-start">
                        <div>
                            <h2 class="text-2xl font-bold text-gray-900">Factura #${bill.id}</h2>
                            <p class="text-sm text-amber-900">Habitación ${bill.room_number}</p>
                        </div>
                        <button class="close-modal text-amber-900 hover:text-amber-800">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                </div>

                <!-- Modal Body -->
                <div class="overflow-y-auto flex-1 p-6 space-y-4">
                    <!-- Estado -->
                    <div class="bg-amber-100 p-4 rounded-lg border border-amber-300">
                        <div class="flex justify-between items-center">
                            <span class="font-semibold text-amber-900">Estado:</span>
                            <span class="px-3 py-1 rounded-full text-sm font-semibold ${bill.status_class}">
                                ${bill.status_display}
                            </span>
                        </div>
                    </div>

                    <!-- Resumen de Pedidos -->
                    <div>
                        <h3 class="font-bold text-amber-900 mb-3">Pedidos incluidos</h3>
                        <div class="space-y-2 max-h-48 overflow-y-auto">
                            ${bill.orders.map(order => `
                                <div class="border border-amber-200 rounded-lg p-3 bg-white">
                                    <div class="flex justify-between mb-2">
                                        <span class="font-semibold text-gray-900">Pedido #${order.id}</span>
                                        <span class="font-semibold text-amber-900">$${order.total.toFixed(2)}</span>
                                    </div>
                                    <div class="text-xs text-gray-600 space-y-1">
                                        ${order.items.map(item => `<div>${item.quantity}x ${item.name} - $${item.subtotal.toFixed(2)}</div>`).join('')}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <!-- Totales -->
                    <div class="bg-amber-100 p-4 rounded-lg border border-amber-300">
                        <div class="space-y-2">
                            <div class="flex justify-between">
                                <span class="text-amber-900">Subtotal:</span>
                                <span class="font-semibold text-amber-900">$${(bill.total - bill.tip).toFixed(2)}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-amber-900">Propina:</span>
                                <span class="font-semibold text-amber-900">$${bill.tip.toFixed(2)}</span>
                            </div>
                            <div class="flex justify-between text-lg font-bold text-amber-900 border-t border-amber-300 pt-2">
                                <span>Total:</span>
                                <span>$${bill.total.toFixed(2)}</span>
                            </div>
                        </div>
                    </div>

                    ${bill.status === 'confirmed' ? `
                        <div class="space-y-2 py-3 border-t border-amber-300">
                            <label class="block text-sm font-medium text-amber-900">Método de Pago</label>
                            <select id="payment-method-select" class="w-full px-4 py-2 border border-amber-300 rounded-lg bg-white text-amber-900 font-medium focus:ring-2 focus:ring-amber-500">
                                <option value="cash">Efectivo</option>
                                <option value="card">Tarjeta</option>
                                <option value="transfer">Transferencia</option>
                                <option value="check">Cheque</option>
                                <option value="mixed">Mixto</option>
                            </select>
                        </div>
                    ` : ''}
                </div>

                <!-- Modal Footer -->
                <div class="modal-footer p-6 border-t border-amber-300 bg-amber-50 sticky bottom-0 space-y-2">
                    ${bill.status === 'confirmed' ? `
                        <button class="pay-bill-btn px-4 py-2 bg-amber-900 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-amber-800 focus:outline-none focus:ring-2 focus:ring-amber-500 flex items-center justify-center gap-2" data-bill-id="${bill.id}">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            Procesar Pago
                        </button>
                    ` : bill.status === 'draft' ? `
                        <button class="confirm-bill-btn px-4 py-2 bg-amber-900 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-amber-800 focus:outline-none focus:ring-2 focus:ring-amber-500 flex items-center justify-center gap-2" data-bill-id="${bill.id}">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            Confirmar Factura
                        </button>
                    ` : ''}
                    <button class="close-modal px-4 py-2 bg-gray-200 text-gray-800 text-base font-medium rounded-md w-full shadow-sm hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-400 flex items-center justify-center gap-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                        Cerrar
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        modal.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', () => modal.remove());
        });

        const payBtn = modal.querySelector('.pay-bill-btn');
        if (payBtn) {
            payBtn.addEventListener('click', () => {
                const method = modal.querySelector('#payment-method-select')?.value || 'cash';
                this.payBill(bill.id, method);
                modal.remove();
            });
        }

        const confirmBtn = modal.querySelector('.confirm-bill-btn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                this.confirmBill(bill.id);
                modal.remove();
            });
        }

        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }

    async confirmBill(billId) {
        try {
            const response = await fetch(`/restaurant/api/roombills/${billId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({ status: 'confirmed' })
            });

            if (!response.ok) throw new Error('Error al confirmar factura');

            this.showToast('Factura confirmada', 'success');
            this.loadBills();
        } catch (error) {
            console.error('Error:', error);
            this.showToast(error.message || 'Error al confirmar factura', 'error');
        }
    }

    async payBill(billId, paymentMethod) {
        try {
            const response = await fetch(`/restaurant/api/roombills/${billId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    status: 'paid',
                    payment_method: paymentMethod
                })
            });

            if (!response.ok) throw new Error('Error al procesar pago');

            this.showToast('¡Pago procesado correctamente!', 'success');
            this.loadBills();
            this.loadHistory();
        } catch (error) {
            console.error('Error:', error);
            this.showToast(error.message || 'Error al procesar pago', 'error');
        }
    }

    async cancelBill(billId) {
        try {
            const response = await fetch(`/restaurant/api/roombills/${billId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({ status: 'cancelled' })
            });

            if (!response.ok) throw new Error('Error al cancelar factura');

            this.showToast('Factura cancelada', 'success');
            this.loadBills();
        } catch (error) {
            console.error('Error:', error);
            this.showToast(error.message || 'Error al cancelar factura', 'error');
        }
    }

    async loadHistory() {
        try {
            const response = await fetch('/restaurant/api/roombills/?status=all', {
                method: 'GET',
                headers: { 'X-CSRFToken': this.csrfToken }
            });

            if (!response.ok) throw new Error('Error al cargar historial');

            const data = await response.json();
            const historyBills = data.bills.filter(b => b.status === 'paid' || b.status === 'cancelled');
            this.renderHistory(historyBills);
        } catch (error) {
            console.error('Error:', error);
            this.showToast('Error al cargar historial', 'error');
            const tbody = document.getElementById('history-tbody');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center py-12 text-gray-500">Error al cargar el historial.</td></tr>';
            }
        }
    }

    renderHistory(bills) {
        const tbody = document.getElementById('history-tbody');

        if (!tbody) {
            console.warn('history-tbody no encontrado');
            return;
        }

        if (bills.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-12 text-gray-500">No hay facturas en el historial aún.</td></tr>';
            return;
        }

        tbody.innerHTML = bills.map(bill => `
            <tr class="border-b border-gray-100 hover:bg-gray-50">
                <td class="py-4 font-semibold text-gray-900">Habitación ${bill.room_number}</td>
                <td class="py-4">
                    <span class="px-3 py-1 rounded-full text-sm font-semibold ${bill.status_class}">
                        ${bill.status_display}
                    </span>
                </td>
                <td class="py-4 font-semibold">$${bill.total.toFixed(2)}</td>
                <td class="py-4 text-sm text-gray-600">${bill.paid_at ? new Date(bill.paid_at).toLocaleString() : '-'}</td>
                <td class="py-4 text-sm">${bill.payment_method_display || '-'}</td>
            </tr>
        `).join('');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icons = {
            success: `<svg class="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
            error: `<svg class="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
            info: `<svg class="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
        };

        toast.innerHTML = icons[type] || icons['info'];
        const messageSpan = document.createElement('span');
        messageSpan.textContent = message;
        toast.appendChild(messageSpan);

        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    window.roomBillManager = new RoomBillManager();
});
