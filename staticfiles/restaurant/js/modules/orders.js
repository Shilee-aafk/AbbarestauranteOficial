/**
 * Orders Module - Gestiona la vista monitor y estado de pedidos
 */

const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';

export class OrdersManager {
  constructor(cartManager, uiManager) {
    this.cartManager = cartManager;
    this.uiManager = uiManager;
    this.playedSoundForOrders = new Set();
    
    // Set up event delegation for dynamic elements
    this.setupEventDelegation();
  }

  /**
   * Configura event delegation para elementos dinámicos
   */
  setupEventDelegation() {
    document.addEventListener('click', (e) => {
      const editBtn = e.target.closest('.edit-btn');
      const cancelBtn = e.target.closest('.cancel-btn');
      const markServedBtn = e.target.closest('.mark-served-monitor-btn');
      const chargeBtn = e.target.closest('.charge-btn');

      if (editBtn) {
        const orderId = editBtn.dataset.orderId;
        this.editOrderFromMonitor(orderId);
      }

      if (cancelBtn) {
        const orderId = cancelBtn.dataset.orderId;
        if (confirm('¿Estás seguro de que quieres cancelar este pedido? Esta acción no se puede deshacer.')) {
          this.updateOrderStatus(orderId, 'cancelled');
        }
      }

      if (markServedBtn) {
        const orderId = markServedBtn.dataset.orderId;
        this.openServeConfirmationModal(orderId);
      }

      if (chargeBtn) {
        const orderId = chargeBtn.dataset.orderId;
        // Dispatchear evento para que otro handler lo maneje
        window.dispatchEvent(new CustomEvent('openPaymentModal', { detail: { orderId } }));
      }
    });

    // Event delegation para cambios de status
    document.addEventListener('change', (e) => {
      if (e.target.classList.contains('status-changer')) {
        const orderId = e.target.dataset.orderId;
        const newStatus = e.target.value;
        this.updateOrderStatus(orderId, newStatus);
      }
    });
  }

  /**
   * Inicializa el monitor con pedidos iniciales
   */
  initializeMonitor(initialOrders) {
    initialOrders.forEach(order => {
      if (['paid', 'cancelled', 'charged_to_room'].includes(order.status)) {
        return;
      }

      if (order.status === 'served') {
        this.addOrUpdateServedOrder(order);
      } else if (order.status === 'ready') {
        this.addOrUpdateReadyOrder(order);
      } else {
        this.addOrUpdateInProgressOrder(order);
      }
    });
  }

  /**
   * Maneja las actualizaciones de pedidos en tiempo real
   */
  handleOrderUpdate(order) {
    if (['paid', 'cancelled', 'charged_to_room'].includes(order.status)) {
      this.removeInProgressOrder(order.id);
      this.removeReadyOrder(order.id);
      this.removeServedOrder(order.id);
      this.playedSoundForOrders.delete(order.id);
      return;
    }

    if (order.status === 'served') {
      this.removeInProgressOrder(order.id);
      this.removeReadyOrder(order.id);
      this.addOrUpdateServedOrder(order);
    } else if (order.status === 'ready') {
      this.removeInProgressOrder(order.id);
      this.removeServedOrder(order.id);
      this.addOrUpdateReadyOrder(order);

      if (!this.playedSoundForOrders.has(order.id)) {
        this.uiManager.showToast(
          `¡El pedido para ${order.identifier} está listo!`,
          'info'
        );
        const notificationSound = new Audio("/static/restaurant/sounds/notification.mp3");
        notificationSound.play().catch(e => 
          console.warn("La interacción del usuario es necesaria para reproducir audio.")
        );
        this.playedSoundForOrders.add(order.id);
      }
    } else {
      this.removeReadyOrder(order.id);
      this.removeServedOrder(order.id);
      this.addOrUpdateInProgressOrder(order);
    }
  }

  /**
   * Agrega o actualiza un pedido en la sección de "En Preparación"
   */
  addOrUpdateInProgressOrder(order) {
    const inProgressList = document.getElementById('in-progress-orders-list-monitor');
    let orderLi = document.getElementById(`inprogress-order-${order.id}`);

    const itemsHTML = (order.items && Array.isArray(order.items))
      ? order.items.map(item => {
          const strikeClass = item.is_prepared ? 'line-through text-gray-500' : '';
          return `<li class="${strikeClass}">${item.quantity}x ${item.name}</li>`;
        }).join('')
      : '<li>Items no disponibles</li>';

    const statusOptions = `
      <option value="pending" ${order.status === 'pending' ? 'selected' : ''}>Pendiente</option>
      <option value="preparing" ${order.status === 'preparing' ? 'selected' : ''}>En Preparación</option>
      <option value="ready" ${order.status === 'ready' ? 'selected' : ''}>Listo</option>
    `;

    const orderHTML = `
      <div class="flex justify-between items-center">
        <div>
          <p class="font-semibold">Pedido #${order.id} (${order.identifier})</p>
          <span class="px-2 py-1 text-xs font-medium rounded-full ${order.status_class}">${order.status_display}</span>
        </div>
      </div>
      <div class="text-sm text-gray-600 mt-1">
        <p>Total: $${order.total.toLocaleString('es-CL')}</p>
        <ul class="list-disc list-inside pl-1">${itemsHTML}</ul>
      </div>
      <div class="mt-2 text-right">
        <div class="flex items-center justify-end space-x-2">
          <select class="status-changer text-xs border-gray-300 rounded-md shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50" data-order-id="${order.id}">
            ${statusOptions}
          </select>
          <button class="edit-btn flex items-center justify-center bg-amber-200 text-amber-900 px-3 py-1 rounded-md text-xs font-medium hover:bg-amber-300" data-order-id="${order.id}">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L16.732 3.732z"></path></svg>
          </button>
          <button class="cancel-btn flex items-center justify-center bg-amber-800 text-white px-3 py-1 rounded-md text-xs font-medium hover:bg-amber-900" data-order-id="${order.id}">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
      </div>
    `;

    if (orderLi) {
      orderLi.innerHTML = orderHTML;
      const newOrderLi = orderLi.cloneNode(true);
      orderLi.parentNode.replaceChild(newOrderLi, orderLi);
      orderLi = newOrderLi;
    } else {
      orderLi = document.createElement('li');
      orderLi.id = `inprogress-order-${order.id}`;
      orderLi.dataset.updatedAt = order.updated_at;
      orderLi.className = 'bg-gray-50 p-3 rounded-lg border';
      orderLi.innerHTML = orderHTML;
      inProgressList.appendChild(orderLi);
    }

    document.getElementById('no-in-progress-orders')?.remove();
  }

  /**
   * Elimina un pedido de la sección "En Preparación"
   */
  removeInProgressOrder(orderId) {
    const orderLi = document.getElementById(`inprogress-order-${orderId}`);
    if (orderLi) {
      orderLi.remove();
    }
    const list = document.getElementById('in-progress-orders-list-monitor');
    if (list.children.length === 0) {
      list.innerHTML = '<li id="no-in-progress-orders" class="text-gray-500">No hay pedidos en curso.</li>';
    }
  }

  /**
   * Agrega o actualiza un pedido en la sección "Listos"
   */
  addOrUpdateReadyOrder(order) {
    const readyList = document.getElementById('ready-orders-list-monitor');
    let orderLi = document.getElementById(`ready-order-${order.id}`);

    const itemsHTML = (order.items && Array.isArray(order.items))
      ? order.items.map(item => {
          const strikeClass = item.is_prepared ? 'line-through text-gray-500' : '';
          return `<li class="${strikeClass}">${item.quantity}x ${item.name}</li>`;
        }).join('')
      : '<li>Items no disponibles</li>';

    const orderHTML = `
      <div class="flex justify-between items-center">
        <div>
          <p class="font-semibold">Pedido #${order.id} (${order.identifier})</p>
          <span class="px-2 py-1 text-xs font-medium rounded-full ${order.status_class}">${order.status_display}</span>
        </div>
      </div>
      <div class="text-sm text-gray-600 mt-1">
        <ul class="list-disc list-inside pl-1">${itemsHTML}</ul>
      </div>
      <div class="mt-3 flex items-center space-x-2">
        <button class="edit-btn flex-shrink-0 flex items-center justify-center bg-amber-200 text-amber-900 px-3 py-2 rounded-lg text-sm font-medium hover:bg-amber-300" data-order-id="${order.id}">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L16.732 3.732z"></path></svg>
        </button>
        <button class="mark-served-monitor-btn w-full flex items-center justify-center bg-amber-100 text-amber-900 px-4 py-2 rounded-lg text-sm font-bold hover:bg-amber-200" data-order-id="${order.id}">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
          Marcar Servido
        </button>
      </div>
    `;

    if (orderLi) {
      orderLi.innerHTML = orderHTML;
      const newOrderLi = orderLi.cloneNode(true);
      orderLi.parentNode.replaceChild(newOrderLi, orderLi);
      orderLi = newOrderLi;
    } else {
      orderLi = document.createElement('li');
      orderLi.id = `ready-order-${order.id}`;
      orderLi.dataset.updatedAt = order.updated_at;
      orderLi.className = 'bg-amber-50 p-3 rounded-lg border border-amber-200';
      orderLi.innerHTML = orderHTML;
      readyList.appendChild(orderLi);
    }
    document.getElementById('no-ready-orders')?.remove();
  }

  /**
   * Elimina un pedido de la sección "Listos"
   */
  removeReadyOrder(orderId) {
    const orderLi = document.getElementById(`ready-order-${orderId}`);
    if (orderLi) {
      orderLi.classList.add('fade-out');
      setTimeout(() => {
        orderLi.remove();
        const list = document.getElementById('ready-orders-list-monitor');
        if (list.children.length === 0) {
          list.innerHTML = '<li id="no-ready-orders" class="text-gray-500">No hay pedidos listos.</li>';
        }
      }, 500);
    }
  }

  /**
   * Agrega o actualiza un pedido en la sección "Servidos"
   */
  addOrUpdateServedOrder(order) {
    const servedOrdersList = document.getElementById('served-orders-list-monitor');
    let orderLi = document.getElementById(`served-order-monitor-${order.id}`);

    const orderHTML = `
      <div class="flex-grow">
        <div class="flex justify-between items-center">
          <p class="font-semibold">${order.identifier} - Pedido #${order.id}</p>
        </div>
        <p class="text-sm text-gray-700 mt-1">Total: $${order.total.toLocaleString('es-CL')}</p>
      </div>
      <div class="flex items-center space-x-2 ml-4">
        <button class="edit-btn flex items-center justify-center bg-gray-500 text-white px-3 py-2 rounded-lg text-sm font-medium hover:bg-gray-600" data-order-id="${order.id}">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L16.732 3.732z"></path></svg>
        </button>
        <button class="charge-btn flex items-center justify-center bg-amber-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-amber-900" data-order-id="${order.id}">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H4a3 3 0 00-3 3v8a3 3 0 003 3z"></path></svg>
          <span>Cobrar</span>
        </button>
      </div>
    `;

    if (orderLi) {
      orderLi.innerHTML = orderHTML;
      const newOrderLi = orderLi.cloneNode(true);
      orderLi.parentNode.replaceChild(newOrderLi, orderLi);
      orderLi = newOrderLi;
    } else {
      orderLi = document.createElement('li');
      orderLi.id = `served-order-monitor-${order.id}`;
      orderLi.dataset.updatedAt = order.updated_at;
      orderLi.className = 'flex justify-between items-center bg-blue-50 p-3 rounded-lg';
      orderLi.innerHTML = orderHTML;
      servedOrdersList.append(orderLi);
    }

    document.getElementById('no-served-orders')?.remove();
  }

  /**
   * Elimina un pedido de la sección "Servidos"
   */
  removeServedOrder(orderId) {
    const orderLi = document.getElementById(`served-order-monitor-${orderId}`);
    if (orderLi) {
      orderLi.remove();
    }
    const list = document.getElementById('served-orders-list-monitor');
    if (list.children.length === 0) {
      list.innerHTML = '<li id="no-served-orders" class="text-gray-500">No hay pedidos servidos pendientes de cobro.</li>';
    }
  }

  /**
   * Actualiza el estado de un pedido
   */
  async updateOrderStatus(orderId, newStatus, statusText = null) {
    if (!orderId || orderId === 'undefined') {
      console.error('Invalid orderId:', orderId);
      this.uiManager.showToast('Error: ID de pedido inválido', 'error');
      return;
    }

    const body = { status: newStatus };

    if (newStatus === 'paid' || newStatus === 'charged_to_room') {
      const includeTipCheckbox = document.getElementById('include-tip-checkbox');
      if (includeTipCheckbox?.checked) {
        body.tip_amount = parseFloat(document.getElementById('custom-tip-amount-input').value).toFixed(2) || '0.00';
      } else {
        body.tip_amount = '0.00';
      }
    }

    try {
      const response = await fetch(`/restaurant/api/orders/${orderId}/status/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify(body)
      });
      if (response.ok) {
        const text = statusText || this.getStatusInSpanish(newStatus);
        this.uiManager.showToast(`Pedido #${orderId} marcado como ${text}.`, 'success');
      } else {
        this.uiManager.showToast('Error al actualizar el estado del pedido.', 'error');
      }
    } catch (error) {
      console.error('Error:', error);
      this.uiManager.showToast('Error al actualizar el estado.', 'error');
    }
  }

  /**
   * Abre el modal de confirmación de entrega
   */
  async openServeConfirmationModal(orderId) {
    if (!orderId || orderId === 'undefined') {
      console.error('Invalid orderId:', orderId);
      this.uiManager.showToast('Error: ID de pedido inválido', 'error');
      return;
    }

    try {
      const response = await fetch(`/restaurant/api/waiter/orders/${orderId}/`);
      if (!response.ok) throw new Error('Failed to fetch order details');
      const data = await response.json();

      document.getElementById('serve-modal-title').textContent = `Confirmar Entrega - ${data.identifier || ''}`;
      const itemsList = document.getElementById('serve-modal-order-items');
      itemsList.innerHTML = data.items.map(item => {
        const strikeClass = item.is_prepared ? 'line-through text-gray-500' : '';
        return `
          <li class="flex justify-between ${strikeClass}">
            <span>${item.quantity}x ${item.name}</span>
          </li>
        `;
      }).join('');

      const confirmBtn = document.getElementById('serve-modal-confirm-btn');
      const newConfirmBtn = confirmBtn.cloneNode(true);
      confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

      newConfirmBtn.onclick = () => {
        this.updateOrderStatus(orderId, 'served');
        this.uiManager.closeServeConfirmationModal();
      };

      document.getElementById('serve-confirmation-modal').classList.remove('hidden');
    } catch (error) {
      console.error('Error opening serve confirmation modal:', error);
      this.uiManager.showToast('No se pudo cargar el detalle del pedido para confirmar.', 'error');
    }
  }

  /**
   * Edita un pedido desde el monitor
   */
  async editOrderFromMonitor(orderId) {
    if (!orderId || orderId === 'undefined') {
      console.error('Invalid orderId:', orderId);
      this.uiManager.showToast('Error: ID de pedido inválido', 'error');
      return;
    }

    try {
      const response = await fetch(`/restaurant/api/waiter/orders/${orderId}/`);
      if (!response.ok) {
        this.uiManager.showToast('No se pudo cargar el pedido para editar.', 'error');
        return;
      }
      const data = await response.json();

      // Show the order view first so elements are visible
      this.uiManager.showOrderView();

      // Wait a tick to ensure DOM is updated
      await new Promise(resolve => setTimeout(resolve, 0));

      const identifierElement = document.getElementById('order-identifier-display');
      if (identifierElement) {
        identifierElement.textContent = data.identifier;
      } else {
        console.error('Element order-identifier-display not found');
      }

      this.cartManager.loadOrder(orderId, data);

      const submitBtn = document.getElementById('submit-order-btn');
      if (submitBtn) {
        submitBtn.textContent = 'Actualizar Pedido';
      }

      const servedBtn = document.getElementById('mark-served-btn');
      if (servedBtn) {
        servedBtn.classList.remove('hidden');
      }

      this.uiManager.resetCategoryFilters();
    } catch (error) {
      console.error('Error editing order:', error);
      this.uiManager.showToast('Error al cargar el pedido.', 'error');
    }
  }

  /**
   * Obtiene el status en español
   */
  getStatusInSpanish(status) {
    const statuses = {
      'pending': 'Pendiente',
      'preparing': 'En Preparación',
      'ready': 'Listo',
      'served': 'Servido',
      'paid': 'Pagado',
      'charged_to_room': 'Cargado a Habitación',
      'cancelled': 'Cancelado'
    };
    return statuses[status] || status;
  }
}
