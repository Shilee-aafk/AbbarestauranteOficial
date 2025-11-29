/**
 * Waiter Dashboard App - Integración de todos los módulos
 * Importar y usar: import { initApp } from '/static/restaurant/js/modules/app.js'
 */

import { CartManager } from '/static/restaurant/js/modules/cart.js';
import { OrdersManager } from '/static/restaurant/js/modules/orders.js';
import { MenuManager } from '/static/restaurant/js/modules/menu.js';
import { UIManager } from '/static/restaurant/js/modules/ui.js';

let cartManager;
let ordersManager;
let menuManager;
let uiManager;

/**
 * Inicializa toda la aplicación
 */
export function initApp(initialOrders = []) {
  try {
    // Crear instancias de los managers
    console.log('Creating manager instances...');
    cartManager = new CartManager();
    uiManager = new UIManager();
    ordersManager = new OrdersManager(cartManager, uiManager);
    menuManager = new MenuManager();

    // Exportar a window para acceso global
    window.cartManager = cartManager;
    window.ordersManager = ordersManager;
    window.menuManager = menuManager;
    window.uiManager = uiManager;

    // Inicializar módulos
    console.log('Initializing UI...');
    uiManager.init();
    
    console.log('Initializing Menu...');
    menuManager.init();
    
    console.log('Initializing Orders monitor...');
    ordersManager.initializeMonitor(initialOrders);

    // Configurar event listeners globales
    console.log('Setting up global listeners...');
    setupGlobalListeners();
    setupMenuItemListeners();
    setupPusherListeners();
    
    console.log('✅ App initialized successfully');
    console.log('Managers:', { cartManager, ordersManager, menuManager, uiManager });
  } catch (error) {
    console.error('❌ Error initializing app:', error);
    console.error('Stack:', error.stack);
  }
}

/**
 * Configura los listeners globales de la aplicación
 */
function setupGlobalListeners() {
  console.log('setupGlobalListeners starting...');
  
  // Botón de volver a vista principal
  const backToMainBtn = document.getElementById('back-to-main-view-btn');
  if (backToMainBtn) {
    backToMainBtn.addEventListener('click', () => {
      cartManager.clear();
      // Clear form fields
      const clientIdentifierInput = document.getElementById('client-identifier');
      const roomNumberInput = document.getElementById('room-number');
      if (clientIdentifierInput) clientIdentifierInput.value = '';
      if (roomNumberInput) roomNumberInput.value = '';
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
      cartManager.editingOrderStatus = null;
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
      cartManager.editingOrderStatus = null;
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
    ordersManager.removeServedOrder(orderId);
  });

  window.addEventListener('charge-to-room', (e) => {
    const { orderId } = e.detail;
    ordersManager.updateOrderStatus(orderId, 'charged_to_room', 'Cargado a Habitación');
    ordersManager.removeServedOrder(orderId);
  });

  // Botón para limpiar el carrito
  const clearOrderBtn = document.getElementById('clear-order-btn');
  if (clearOrderBtn) {
    clearOrderBtn.addEventListener('click', () => {
      if (cartManager.currentOrder.length === 0) {
        uiManager.showToast('El carrito ya está vacío', 'info');
        return;
      }

      // Confirmación antes de limpiar
      if (confirm('¿Estás seguro de que deseas limpiar el carrito? Esto eliminará todos los items.')) {
        cartManager.clear();
        console.log('✅ Carrito limpiado exitosamente');
      }
    });
  }

  // Listeners para el carrito modal
  const cartToggle = document.getElementById('cart-toggle');
  const cartModal = document.getElementById('cart-modal');
  const closeCartBtn = document.getElementById('close-cart');

  console.log('cartToggle element:', cartToggle);
  console.log('cartModal element:', cartModal);
  console.log('closeCartBtn element:', closeCartBtn);

  if (cartToggle && cartModal) {
    cartToggle.addEventListener('click', () => {
      console.log('Toggle carrito');
      cartModal.classList.toggle('hidden');
      // Actualizar el botón cuando se abre el modal
      if (!cartModal.classList.contains('hidden')) {
        cartManager.updateSubmitButton();
      }
    });
  } else {
    console.error('cartToggle or cartModal not found');
  }

  if (closeCartBtn && cartModal) {
    closeCartBtn.addEventListener('click', () => {
      console.log('Cerrar carrito');
      cartModal.classList.add('hidden');
    });
  }

  // Botón para abrir el carrito desde la vista de edición
  const orderViewCartBtn = document.getElementById('order-view-cart-btn');
  if (orderViewCartBtn && cartModal) {
    orderViewCartBtn.addEventListener('click', () => {
      console.log('Abrir carrito desde vista de pedido');
      cartModal.classList.remove('hidden');
    });
  }

  // Cerrar carrito al hacer click fuera
  if (cartModal) {
    cartModal.addEventListener('click', (e) => {
      if (e.target === cartModal) {
        cartModal.classList.add('hidden');
      }
    });
  }

  // Botón para enviar pedido desde el carrito modal
  const cartSubmitBtn = document.getElementById('cart-submit-btn');
  if (cartSubmitBtn) {
    cartSubmitBtn.addEventListener('click', async () => {
      console.log('Enviar pedido desde carrito');
      if (cartManager.currentOrder.length === 0) {
        uiManager.showToast('El carrito está vacío', 'error');
        return;
      }

      // Obtener valores de los campos de entrada
      const clientIdentifier = document.getElementById('client-identifier')?.value || '';
      const roomNumber = document.getElementById('room-number')?.value || '';

      if (!clientIdentifier) {
        uiManager.showToast('Por favor, ingresa un identificador del cliente', 'error');
        return;
      }

      const orderData = {
        items: cartManager.currentOrder.map(item => ({
          id: item.id,
          quantity: item.quantity,
          note: item.note || ''
        })),
        client_identifier: clientIdentifier,
        room_number: roomNumber,
        tip_amount: 0
      };

      // Determinar si es creación o actualización
      let endpoint = '/restaurant/save_order/';
      let method = 'POST';

      if (cartManager.editingOrderId && cartManager.editingOrderStatus === 'ready') {
        endpoint = `/restaurant/api/waiter/orders/${cartManager.editingOrderId}/`;
        method = 'PUT';
      }

      try {
        console.log('Enviando pedido desde carrito:', orderData);
        const response = await fetch(endpoint, {
          method: method,
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
          },
          body: JSON.stringify(orderData)
        });

        console.log('Response status:', response.status, response.statusText);
        
        const responseText = await response.text();
        console.log('Response text:', responseText.substring(0, 500));

        if (response.ok) {
          const data = JSON.parse(responseText);
          console.log('✅ Respuesta completa:', data);
          console.log('Order data:', data.order);
          
          // Determinar si es creación o actualización
          const isUpdate = cartManager.editingOrderId && cartManager.editingOrderStatus === 'ready';
          const message = isUpdate 
            ? `Pedido #${data.order_id} actualizado exitosamente.`
            : `Pedido #${data.order_id} creado exitosamente.`;
          
          uiManager.showToast(message, 'success');
          cartManager.clear();
          
          // Actualizar el monitor de pedidos localmente de inmediato
          // (sin esperar a que llegue el evento de Pusher)
          if (data.order && ordersManager) {
            console.log('✅ Actualizando monitor con nuevo pedido:', data.order);
            try {
              ordersManager.handleOrderUpdate(data.order);
              console.log('✅ Monitor actualizado correctamente');
            } catch (updateError) {
              console.error('❌ Error al actualizar monitor:', updateError);
            }
          } else {
            console.warn('⚠️ No hay data.order o ordersManager disponible');
          }
          
          // Cerrar el carrito modal
          if (cartModal) {
            cartModal.classList.add('hidden');
          }

          // Limpiar campos de formulario
          const clientInput = document.getElementById('client-identifier');
          const roomInput = document.getElementById('room-number');
          if (clientInput) clientInput.value = '';
          if (roomInput) roomInput.value = '';

          uiManager.showMainSectionView();
        } else {
          console.error('❌ Error response:', response.status, response.statusText);
          try {
            const error = JSON.parse(responseText);
            console.error('Error details:', error);
            uiManager.showToast(
              error.detail || 'Error al crear el pedido.',
              'error'
            );
          } catch (parseError) {
            console.error('Could not parse error JSON. Raw response:', responseText.substring(0, 200));
            uiManager.showToast('Error del servidor al procesar el pedido.', 'error');
          }
        }
      } catch (error) {
        console.error('❌ Catch error:', error);
        uiManager.showToast('Error al procesar el pedido.', 'error');
      }
    });
  }
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
 * Configura los listeners para eventos de Pusher (actualizaciones en tiempo real)
 */
function setupPusherListeners() {
  // Set para rastrear qué órdenes ya han sido notificadas como "ready"
  const notifiedOrders = new Set();
  
  // Event: Nuevo pedido creado
  window.addEventListener('newOrder', (e) => {
    console.log('newOrder event recibido:', e.detail);
    if (e.detail && e.detail.order) {
      ordersManager.handleOrderUpdate(e.detail.order);
    }
  });

  // Event: Pedido actualizado
  window.addEventListener('orderUpdated', (e) => {
    console.log('orderUpdated event recibido:', e.detail);
    if (e.detail && e.detail.order) {
      ordersManager.handleOrderUpdate(e.detail.order);
    }
  });

  // Event: Pedido listo (evitar duplicados con orderUpdated)
  window.addEventListener('orderReady', (e) => {
    console.log('orderReady event recibido:', e.detail);
    if (e.detail && e.detail.order) {
      const orderId = e.detail.order.id;
      
      // Solo procesar si no hemos notificado sobre este pedido recientemente
      if (!notifiedOrders.has(orderId)) {
        notifiedOrders.add(orderId);
        ordersManager.handleOrderUpdate(e.detail.order);
        
        // Limpiar el set después de 5 segundos para evitar duplicados
        setTimeout(() => {
          notifiedOrders.delete(orderId);
        }, 5000);
      } else {
        console.log('⚠️ Notificación duplicada evitada para orden:', orderId);
      }
    }
  });
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
