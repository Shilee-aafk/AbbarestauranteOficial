/**
 * Cart Module - Gestiona el carrito de pedidos
 */

export class CartManager {
  constructor() {
    this.currentOrder = [];
    this.currentClientIdentifier = '';
    this.currentRoomNumber = '';
    this.editingOrderId = null;
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
      this.updateCartDisplay();
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

    if (this.currentOrder.length === 0) {
      orderList.innerHTML = '<li class="text-gray-500">Aún no hay productos en el pedido.</li>';
      return;
    }

    this.currentOrder.forEach(item => {
      const itemTotal = item.price * item.quantity;
      const li = document.createElement('li');
      li.className = 'flex flex-col bg-gray-100 p-2 rounded';
      li.innerHTML = `
        <div class="flex justify-between items-start">
          <div>
            <span class="font-medium">${item.name}</span>
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

    // Attachear event listeners
    this.attachOrderListeners();
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

    cartItemsDiv.innerHTML = this.currentOrder.map(item => `
      <div class="flex flex-col p-3 border-b border-gray-100">
        <div class="flex justify-between items-start mb-2">
          <div>
            <p class="font-semibold text-gray-900">${item.name}</p>
            <p class="text-sm text-gray-600">$${item.price.toFixed(2)}</p>
          </div>
          <div class="flex items-center gap-2">
            <button class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-2 py-1 rounded text-sm modal-decrease" data-line-id="${item.lineItemId}">−</button>
            <span class="w-8 text-center font-medium modal-qty">${item.quantity}</span>
            <button class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-2 py-1 rounded text-sm modal-increase" data-line-id="${item.lineItemId}">+</button>
            <button class="text-red-500 hover:text-red-700 text-sm ml-2 modal-remove" data-line-id="${item.lineItemId}">Eliminar</button>
          </div>
        </div>
        <textarea class="text-xs p-2 border border-gray-300 rounded bg-white resize-none modal-note" data-line-id="${item.lineItemId}" placeholder="Agregar nota especial..." rows="2" maxlength="200">${item.note || ''}</textarea>
      </div>
    `).join('');

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
    this.currentClientIdentifier = '';
    this.currentRoomNumber = '';
    this.editingOrderId = null;
    this.render();
  }

  /**
   * Carga un pedido existente para edición
   */
  loadOrder(orderId, data) {
    this.editingOrderId = orderId;
    this.currentClientIdentifier = data.identifier;
    this.currentRoomNumber = data.room_number;
    this.currentOrder = data.items.map(item => ({
      ...item,
      lineItemId: Date.now() + Math.random()
    }));
    this.render();
  }
}
