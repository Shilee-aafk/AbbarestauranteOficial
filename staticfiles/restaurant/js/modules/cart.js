/**
 * Cart Module - Gestiona el carrito de pedidos
 */

export class CartManager {
  constructor() {
    this.currentOrder = [];
    this.servedItems = []; // Items ya servidos
    this.currentClientIdentifier = '';
    this.currentRoomNumber = '';
    this.editingOrderId = null;
    this.editingOrderStatus = null;
  }

  /**
   * Agrega un item al carrito
   */
  addToOrder(itemId, name, price) {
    const lineItemId = Date.now() + Math.random();
    this.currentOrder.push({
      lineItemId,
      id: itemId,
      name,
      price,
      quantity: 1,
      note: ''
    });
    this.render();
    return lineItemId;
  }

  /**
   * Incrementa la cantidad de un item
   */
  increaseQuantity(lineItemId) {
    const item = this.currentOrder.find(i => i.lineItemId === lineItemId);
    if (item) {
      item.quantity++;
      this.render();
    }
  }

  /**
   * Decrementa la cantidad de un item
   */
  decreaseQuantity(lineItemId) {
    const item = this.currentOrder.find(i => i.lineItemId === lineItemId);
    if (item) {
      item.quantity--;
      if (item.quantity <= 0) {
        this.removeFromOrder(lineItemId);
      } else {
        this.render();
      }
    }
  }

  /**
   * Elimina un item del carrito
   */
  removeFromOrder(lineItemId) {
    const itemIndex = this.currentOrder.findIndex(item => item.lineItemId === lineItemId);
    if (itemIndex > -1) {
      this.currentOrder.splice(itemIndex, 1);
      this.render();
    }
  }

  /**
   * Actualiza la nota de un item
   */
  updateNote(lineItemId, note) {
    const item = this.currentOrder.find(i => i.lineItemId === lineItemId);
    if (item) {
      item.note = note;
      // Actualizar ambas vistas sin perder el focus
      this.syncNotesAcrossViews(lineItemId, note);
    }
  }

  /**
   * Sincroniza la nota entre cart-note y modal-note sin perder el focus
   */
  syncNotesAcrossViews(lineItemId, note) {
    // Si se cambió en cart-note, actualizar modal-note
    const cartNote = document.querySelector(`.cart-note[data-line-id="${lineItemId}"]`);
    const modalNote = document.querySelector(`.modal-note[data-line-id="${lineItemId}"]`);
    
    if (cartNote && modalNote) {
      if (document.activeElement === cartNote) {
        // Si estamos escribiendo en cart-note, actualizar modal-note
        modalNote.value = note;
      } else if (document.activeElement === modalNote) {
        // Si estamos escribiendo en modal-note, actualizar cart-note
        cartNote.value = note;
      } else {
        // Si no hay focus en ninguno, actualizar ambos (por si acaso)
        cartNote.value = note;
        modalNote.value = note;
      }
    }
  }

  /**
   * Calcula el total del carrito
   */
  getTotal() {
    return this.currentOrder.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  }

  /**
   * Obtiene el count de items
   */
  getItemCount() {
    return this.currentOrder.reduce((sum, item) => sum + item.quantity, 0);
  }

  /**
   * Renderiza la orden tanto en lista como en carrito modal
   */
  render() {
    this.updateOrderList();
    this.updateCartDisplay();
    this.updateCartCount();
  }

  /**
   * Actualiza la lista de pedidos (lado derecho)
   */
  updateOrderList() {
    const orderList = document.getElementById('order-items-list');
    if (!orderList) return;

    orderList.innerHTML = '';

    // Mostrar items ya servidos primero (si hay)
    if (this.servedItems.length > 0) {
      const servedHeader = document.createElement('li');
      servedHeader.className = 'bg-gray-300 p-2 rounded font-bold text-gray-700 mt-2 mb-2 flex items-center';
      servedHeader.innerHTML = `
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        Items Ya Servidos
      `;
      orderList.appendChild(servedHeader);

      this.servedItems.forEach(item => {
        const itemTotal = item.price * item.quantity;
        const li = document.createElement('li');
        li.className = 'flex flex-col bg-gray-200 p-2 rounded opacity-70';
        
        li.innerHTML = `
          <div class="flex justify-between items-start">
            <div>
              <span class="font-medium text-gray-700" style="text-decoration: line-through;">
                ${item.quantity}x ${item.name}
              </span>
              <span class="block text-sm text-gray-600">$${itemTotal.toFixed(0)}</span>
            </div>
          </div>
          ${item.note ? `<div class="text-xs text-gray-600 mt-1">Nota: ${item.note}</div>` : ''}
        `;
        orderList.appendChild(li);
      });
    }

    // Mostrar items nuevos/editables
    if (this.currentOrder.length === 0 && this.servedItems.length === 0) {
      orderList.innerHTML = '<li class="text-gray-500">Aún no hay productos en el pedido.</li>';
      return;
    }

    if (this.currentOrder.length > 0) {
      if (this.servedItems.length > 0) {
        const newHeader = document.createElement('li');
        newHeader.className = 'bg-amber-300 p-2 rounded font-bold text-amber-900 mt-2 mb-2 flex items-center';
        newHeader.innerHTML = `
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Nuevos Items
        `;
        orderList.appendChild(newHeader);
      }

      this.currentOrder.forEach(item => {
        const itemTotal = item.price * item.quantity;
        const li = document.createElement('li');
        li.className = 'flex flex-col bg-amber-100 p-2 rounded';
        
        li.innerHTML = `
          <div class="flex justify-between items-start">
            <div>
              <span class="font-medium text-amber-950">${item.name}</span>
              <span class="block text-sm text-gray-600">$${itemTotal.toFixed(0)}</span>
            </div>
            <div class="flex items-center">
              <button class="text-gray-600 cart-decrease" data-line-id="${item.lineItemId}">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5 10a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1z" clip-rule="evenodd"></path>
                </svg>
              </button>
              <span class="w-8 text-center font-medium cart-qty">${item.quantity}</span>
              <button class="text-gray-600 cart-increase" data-line-id="${item.lineItemId}">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd"></path>
                </svg>
              </button>
            </div>
            <div class="flex items-center">
              <button class="text-red-500 hover:text-red-700 ml-2 cart-remove" data-line-id="${item.lineItemId}">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 012 0v6a1 1 0 11-2 0V8z" clip-rule="evenodd"></path>
                </svg>
              </button>
            </div>
          </div>
          <input type="text" class="mt-2 w-full text-sm border border-gray-200 rounded p-1 cart-note" 
                 placeholder="Agregar nota (ej: sin cebolla...)" 
                 value="${item.note}" 
                 data-line-id="${item.lineItemId}">
        `;
        orderList.appendChild(li);
      });
    }

    // Attachear event listeners
    this.attachOrderListeners();

    // Actualizar el total en el HTML (incluye ambas secciones)
    const orderTotalSpan = document.getElementById('order-total');
    if (orderTotalSpan) {
      const total = this.getTotal() + this.servedItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
      orderTotalSpan.textContent = total.toFixed(0);
    }
  }

  /**
   * Actualiza el display del carrito modal
   */
  updateCartDisplay() {
    const cartItemsDiv = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');

    if (!cartItemsDiv) return;

    if (this.currentOrder.length === 0) {
      cartItemsDiv.innerHTML = '<p class="text-gray-500 text-center">El carrito está vacío</p>';
      if (cartTotal) cartTotal.textContent = '$0.00';
      return;
    }

    cartItemsDiv.innerHTML = this.currentOrder.map(item => {
      const strikeClass = (item.is_prepared || item.is_served) ? 'line-through text-gray-500' : '';
      const isDisabled = (item.is_prepared || item.is_served) ? 'disabled opacity-50 cursor-not-allowed' : '';
      return `
      <div class="flex flex-col p-3 border-b border-gray-100">
        <div class="flex justify-between items-start mb-2">
          <div>
            <p class="font-semibold text-gray-900 ${strikeClass}">${item.name}</p>
            <p class="text-sm text-gray-600 ${strikeClass}">$${item.price.toFixed(2)}</p>
          </div>
          <div class="flex items-center gap-2">
            <button class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-2 py-1 rounded text-sm modal-decrease" data-line-id="${item.lineItemId}" ${isDisabled}>−</button>
            <span class="w-8 text-center font-medium modal-qty">${item.quantity}</span>
            <button class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-2 py-1 rounded text-sm modal-increase" data-line-id="${item.lineItemId}" ${isDisabled}>+</button>
            <button class="text-red-500 hover:text-red-700 text-sm ml-2 modal-remove" data-line-id="${item.lineItemId}" ${isDisabled}>Eliminar</button>
          </div>
        </div>
        <textarea class="text-xs p-2 border border-gray-300 rounded bg-amber-50 resize-none modal-note" data-line-id="${item.lineItemId}" placeholder="Agregar nota especial..." rows="2" maxlength="200" ${isDisabled}>${item.note || ''}</textarea>
      </div>
    `;
    }).join('');

    if (cartTotal) {
      cartTotal.textContent = `$${this.getTotal().toFixed(2)}`;
    }

    this.attachModalListeners();
  }

  /**
   * Actualiza el contador de items en el carrito
   */
  updateCartCount() {
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
      cartCount.textContent = this.getItemCount();
    }
  }

  /**
   * Attachea listeners a los botones de la lista de pedidos
   */
  attachOrderListeners() {
    document.querySelectorAll('.cart-increase').forEach(btn => {
      btn.onclick = () => this.increaseQuantity(parseFloat(btn.dataset.lineId));
    });

    document.querySelectorAll('.cart-decrease').forEach(btn => {
      btn.onclick = () => this.decreaseQuantity(parseFloat(btn.dataset.lineId));
    });

    document.querySelectorAll('.cart-remove').forEach(btn => {
      btn.onclick = () => this.removeFromOrder(parseFloat(btn.dataset.lineId));
    });

    document.querySelectorAll('.cart-note').forEach(input => {
      input.oninput = (e) => this.updateNote(parseFloat(input.dataset.lineId), e.target.value);
    });
  }

  /**
   * Attachea listeners a los botones del modal del carrito
   */
  attachModalListeners() {
    document.querySelectorAll('.modal-increase').forEach(btn => {
      btn.onclick = () => this.increaseQuantity(parseFloat(btn.dataset.lineId));
    });

    document.querySelectorAll('.modal-decrease').forEach(btn => {
      btn.onclick = () => this.decreaseQuantity(parseFloat(btn.dataset.lineId));
    });

    document.querySelectorAll('.modal-remove').forEach(btn => {
      btn.onclick = () => this.removeFromOrder(parseFloat(btn.dataset.lineId));
    });

    document.querySelectorAll('.modal-note').forEach(textarea => {
      textarea.oninput = (e) => this.updateNote(parseFloat(textarea.dataset.lineId), e.target.value);
    });
  }

  /**
   * Limpia el carrito
   */
  clear() {
    this.currentOrder = [];
    this.servedItems = [];
    this.currentClientIdentifier = '';
    this.currentRoomNumber = '';
    this.editingOrderId = null;
    this.editingOrderStatus = null;
    this.render();
  }

  /**
   * Carga un pedido existente para edición
   */
  loadOrder(orderId, data) {
    this.editingOrderId = orderId;
    this.editingOrderStatus = data.status;
    this.currentClientIdentifier = data.client_identifier;
    this.currentRoomNumber = data.room_number;
    
    // Separar items servidos de nuevos
    if (data.status === 'served' || data.is_served) {
      // Si es un pedido servido, todos los items que vienen del servidor fueron servidos
      this.servedItems = data.items.map(item => ({
        ...item,
        lineItemId: Date.now() + Math.random()
      }));
      this.currentOrder = []; // El carrito está vacío para nuevos items
    } else if (data.status === 'ready' || data.is_prepared) {
      // Si es un pedido preparado, separar items ya preparados de nuevos
      const itemsWithLineIds = data.items.map(item => ({
        ...item,
        lineItemId: Date.now() + Math.random()
      }));
      
      this.servedItems = itemsWithLineIds.filter(item => item.is_prepared || item.is_served);
      this.currentOrder = itemsWithLineIds.filter(item => !item.is_prepared && !item.is_served);
    } else {
      // Para otros estados, todos los items son nuevos/editables
      this.servedItems = [];
      this.currentOrder = data.items.map(item => ({
        ...item,
        lineItemId: Date.now() + Math.random()
      }));
    }
    
    // Update form fields with order data
    const clientIdentifierInput = document.getElementById('client-identifier');
    const roomNumberInput = document.getElementById('room-number');
    
    if (clientIdentifierInput) {
      clientIdentifierInput.value = data.client_identifier || '';
    }
    if (roomNumberInput) {
      roomNumberInput.value = data.room_number || '';
    }
    
    this.updateSubmitButton();
    this.render();
  }

  /**
   * Actualiza el texto y comportamiento del botón de submit basado en el status del pedido
   */
  updateSubmitButton() {
    const submitBtn = document.getElementById('cart-submit-btn');
    if (!submitBtn) return;

    if (this.editingOrderId && this.editingOrderStatus === 'ready') {
      submitBtn.textContent = 'Actualizar Pedido';
      submitBtn.classList.add('update-order-btn');
      submitBtn.classList.remove('create-order-btn');
    } else {
      submitBtn.innerHTML = `
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
        Realizar Pedido
      `;
      submitBtn.classList.add('create-order-btn');
      submitBtn.classList.remove('update-order-btn');
    }
  }
}
