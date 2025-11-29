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

  // Listeners para el carrito modal
  const cartToggle = document.getElementById('cart-toggle');
  const cartModal = document.getElementById('cart-modal');
  const closeCartBtn = document.getElementById('close-cart');

  if (cartToggle && cartModal) {
    cartToggle.addEventListener('click', () => {
      console.log('Toggle carrito');
      cartModal.classList.toggle('hidden');
    });
  }

  if (closeCartBtn && cartModal) {
    closeCartBtn.addEventListener('click', () => {
      console.log('Cerrar carrito');
      cartModal.classList.add('hidden');
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

      const endpoint = '/restaurant/save_order/';

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

      try {
        console.log('Enviando pedido desde carrito:', orderData);
        const response = await fetch(endpoint, {
          method: 'POST',
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
          console.log('✅ Pedido guardado:', data);
          uiManager.showToast(
            `Pedido #${data.order_id} creado exitosamente.`,
            'success'
          );
          cartManager.clear();
          
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
