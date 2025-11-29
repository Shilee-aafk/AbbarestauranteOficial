/**
 * Waiter Dashboard App - Integración de todos los módulos
 * Importar y usar: import { initApp } from '/static/restaurant/js/modules/app.js'
 */

import { CartManager } from './cart.js';
import { OrdersManager } from './orders.js';
import { MenuManager } from './menu.js';
import { UIManager } from './ui.js';

let cartManager;
let ordersManager;
let menuManager;
let uiManager;

/**
 * Inicializa toda la aplicación
 */
export function initApp(initialOrders = []) {
  // Crear instancias de los managers
  cartManager = new CartManager();
  uiManager = new UIManager();
  ordersManager = new OrdersManager(cartManager, uiManager);
  menuManager = new MenuManager();

  // Inicializar módulos
  uiManager.init();
  menuManager.init();
  ordersManager.initializeMonitor(initialOrders);

  // Configurar event listeners globales
  setupGlobalListeners();
  setupMenuItemListeners();
  setupOrderFormListeners();
}

/**
 * Configura los listeners globales de la aplicación
 */
function setupGlobalListeners() {
  // Botón de volver a vista principal
  const backToMainBtn = document.getElementById('back-to-main-view-btn');
  if (backToMainBtn) {
    backToMainBtn.addEventListener('click', () => {
      cartManager.clear();
      uiManager.showMainSectionView();
    });
  }

  // Botón de crear pedido de mesa
  const startTableOrderBtn = document.getElementById('start-table-order-btn');
  if (startTableOrderBtn) {
    startTableOrderBtn.addEventListener('click', () => {
      const clientIdentifier = document.getElementById('client-identifier').value.trim();
      const roomNumber = document.getElementById('room-number').value.trim();

      if (!clientIdentifier && !roomNumber) {
        uiManager.showToast(
          'Debe ingresar un identificador de cliente o un número de habitación.',
          'error'
        );
        return;
      }

      cartManager.currentClientIdentifier = clientIdentifier;
      cartManager.currentRoomNumber = roomNumber;
      document.getElementById('order-identifier-display').textContent = 
        roomNumber || clientIdentifier;

      cartManager.currentOrder = [];
      cartManager.editingOrderId = null;
      cartManager.render();
      uiManager.showOrderView();
    });
  }

  // Botón de crear pedido de barra
  const startBarOrderBtn = document.getElementById('start-bar-order-btn');
  if (startBarOrderBtn) {
    startBarOrderBtn.addEventListener('click', () => {
      const clientIdentifier = document.getElementById('bar-client-identifier').value.trim();
      const roomNumber = document.getElementById('bar-room-number').value.trim();

      if (!clientIdentifier && !roomNumber) {
        uiManager.showToast(
          'Debe ingresar un identificador o un número de habitación.',
          'error'
        );
        return;
      }

      cartManager.currentClientIdentifier = clientIdentifier || 'Barra';
      cartManager.currentRoomNumber = roomNumber;
      document.getElementById('order-identifier-display').textContent = 
        roomNumber || cartManager.currentClientIdentifier;

      cartManager.currentOrder = [];
      cartManager.editingOrderId = null;
      cartManager.render();

      document.getElementById('bar-client-identifier').value = '';
      document.getElementById('bar-room-number').value = '';

      menuManager.filterBarCategories(true);
      uiManager.showOrderView();
    });
  }

  // Event listeners para el monitor de pedidos
  const servedOrdersList = document.getElementById('served-orders-list-monitor');
  if (servedOrdersList) {
    servedOrdersList.addEventListener('click', (e) => {
      const chargeButton = e.target.closest('.charge-btn');
      if (chargeButton) {
        const orderId = chargeButton.dataset.orderId;
        if (orderId && orderId !== 'undefined') {
          uiManager.openPaymentModal(orderId);
        }
      }

      const editButton = e.target.closest('.edit-btn');
      if (editButton) {
        const orderId = editButton.dataset.orderId;
        if (orderId && orderId !== 'undefined') {
          ordersManager.editOrderFromMonitor(orderId);
        }
      }
    });
  }

  // Events para confirmación de pago
  window.addEventListener('payment-confirmed', (e) => {
    const { orderId } = e.detail;
    ordersManager.updateOrderStatus(orderId, 'paid', 'Pagado');
  });

  window.addEventListener('charge-to-room', (e) => {
    const { orderId } = e.detail;
    ordersManager.updateOrderStatus(orderId, 'charged_to_room', 'Cargado a Habitación');
  });
}

/**
 * Configura los listeners para los items del menú
 */
function setupMenuItemListeners() {
  // Delegar click en botones "Agregar al pedido"
  document.addEventListener('click', (e) => {
    const addBtn = e.target.closest('.add-to-order-btn');
    if (addBtn) {
      const itemId = addBtn.dataset.itemId;
      const name = addBtn.dataset.name;
      const price = parseFloat(addBtn.dataset.price);

      if (itemId && name && price) {
        const lineItemId = cartManager.addToOrder(itemId, name, price);
        
        // Efecto visual de animación
        addBtn.classList.add('pulse');
        setTimeout(() => {
          addBtn.classList.remove('pulse');
        }, 400);
      }
    }
  });
}

/**
 * Configura los listeners del formulario de pedido
 */
function setupOrderFormListeners() {
  const submitOrderBtn = document.getElementById('submit-order-btn');
  if (submitOrderBtn) {
    submitOrderBtn.addEventListener('click', async () => {
      if (cartManager.currentOrder.length === 0) {
        uiManager.showToast(
          'El carrito está vacío. Agrega productos antes de enviar.',
          'error'
        );
        return;
      }

      const orderId = cartManager.editingOrderId;
      const endpoint = orderId 
        ? `/restaurant/api/orders/${orderId}/` 
        : '/restaurant/api/orders/create/';
      
      const method = orderId ? 'PUT' : 'POST';

      const orderData = {
        items: cartManager.currentOrder.map(item => ({
          menu_item: item.id,
          quantity: item.quantity,
          notes: item.note
        })),
        identifier: cartManager.currentClientIdentifier,
        room_number: cartManager.currentRoomNumber || ''
      };

      try {
        const response = await fetch(endpoint, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
          },
          body: JSON.stringify(orderData)
        });

        if (response.ok) {
          const data = await response.json();
          const action = orderId ? 'actualizado' : 'creado';
          uiManager.showToast(
            `Pedido #${data.id} ${action} exitosamente.`,
            'success'
          );
          cartManager.clear();
          uiManager.showMainSectionView();
        } else {
          const error = await response.json();
          uiManager.showToast(
            error.detail || `Error al ${orderId ? 'actualizar' : 'crear'} el pedido.`,
            'error'
          );
        }
      } catch (error) {
        console.error('Error:', error);
        uiManager.showToast('Error al procesar el pedido.', 'error');
      }
    });
  }

  const markServedBtn = document.getElementById('mark-served-btn');
  if (markServedBtn) {
    markServedBtn.addEventListener('click', async () => {
      const orderId = cartManager.editingOrderId;
      if (orderId) {
        ordersManager.updateOrderStatus(orderId, 'served');
        cartManager.clear();
        uiManager.showMainSectionView();
      }
    });
  }
}

/**
 * Obtiene el token CSRF del DOM
 */
function getCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]')?.content || '';
}

/**
 * Función global para que el HTML pueda llamar addToOrder
 */
window.addToOrder = function(evt, itemId, name, price) {
  const lineItemId = cartManager.addToOrder(itemId, name, price);
  const button = evt.target.closest('.add-to-order-btn');
  if (button) {
    button.classList.add('pulse');
    setTimeout(() => {
      button.classList.remove('pulse');
    }, 400);
  }
};

/**
 * Funciones globales para el carrito
 */
window.increaseQuantity = function(lineItemId) {
  cartManager.increaseQuantity(lineItemId);
};

window.decreaseQuantity = function(lineItemId) {
  cartManager.decreaseQuantity(lineItemId);
};

window.removeFromOrder = function(lineItemId) {
  cartManager.removeFromOrder(lineItemId);
};

window.updateNote = function(lineItemId, note) {
  cartManager.updateNote(lineItemId, note);
};

/**
 * Exportar managers para debugging o extensiones futuras
 */
export { cartManager, ordersManager, menuManager, uiManager };
