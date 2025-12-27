/**
 * UI Module - Gestiona interfaz, modales y navegación
 */

const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';

export class UIManager {
  constructor() {
    this.currentSection = 'dashboard';
  }

  /**
   * Inicializa la interfaz principal
   */
  init() {
    this.setupNavigation();
    this.setupSidebar();
    this.setupModals();
    
    // Asegurar que el botón del carrito esté visible inicialmente y NUNCA tenga hidden
    const cartToggle = document.getElementById('cart-toggle');
    if (cartToggle) {
      cartToggle.classList.remove('hidden');
      cartToggle.style.display = 'block';
      cartToggle.style.visibility = 'visible';
      cartToggle.style.opacity = '1';
    }
    
    this.restoreLastSection();
  }

  /**
   * Configura la navegación del sidebar
   */
  setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const contentSections = document.querySelectorAll('.content-section');

    navLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const section = link.getAttribute('data-section');
        this.showSection(section, navLinks, contentSections);
        localStorage.setItem('activeWaiterSection', section);
      });
    });
  }

  /**
   * Muestra una sección específica
   */
  showSection(section, navLinks = null, contentSections = null) {
    const links = navLinks || document.querySelectorAll('.nav-link');
    const sections = contentSections || document.querySelectorAll('.content-section');

    this.closeAllModals();

    links.forEach(l => {
      l.classList.remove('active', 'text-amber-800', 'bg-amber-100', 'border-r-4', 'border-amber-500');
      l.classList.add('text-gray-600', 'hover:bg-gray-100');
    });

    const activeLink = document.querySelector(`.nav-link[data-section="${section}"]`);
    if (activeLink) {
      activeLink.classList.add('active', 'text-amber-800', 'bg-amber-100', 'border-r-4', 'border-amber-500');
      activeLink.classList.remove('text-gray-600', 'hover:bg-gray-100');
    }

    sections.forEach(s => s.classList.add('hidden'));
    const targetSection = document.getElementById(section);
    if (targetSection) {
      targetSection.classList.remove('hidden');
    }

    // Ocultar carrito en la pestaña de cobros, mostrar en otras
    const cartToggle = document.getElementById('cart-toggle');
    if (cartToggle) {
      if (section === 'cobros') {
        cartToggle.classList.add('hidden');
      } else {
        cartToggle.classList.remove('hidden');
        cartToggle.style.display = 'block';
        cartToggle.style.visibility = 'visible';
        cartToggle.style.opacity = '1';
      }
    }

    this.currentSection = section;
  }

  /**
   * Configura el toggle del sidebar para móvil
   * NOTA: El sidebar se controla desde initUIComponents() en waiter_dashboard.html
   */
  setupSidebar() {
    // Sidebar logic is handled in initUIComponents() template - do nothing here
  }

  /**
   * Configura los listeners básicos de los modales
   */
  setupModals() {
    const paymentCancelBtn = document.getElementById('modal-cancel-btn');
    const serveModalCancelBtn = document.getElementById('serve-modal-cancel-btn');

    paymentCancelBtn?.addEventListener('click', () => this.closePaymentModal());
    serveModalCancelBtn?.addEventListener('click', () => this.closeServeConfirmationModal());
  }

  /**
   * Cierra todos los modales abiertos
   */
  closeAllModals() {
    this.closePaymentModal();
    this.closeServeConfirmationModal();
    this.hideOrderView();
    document.getElementById('modal-charge-to-room-btn')?.classList.add('hidden');
    document.getElementById('mark-served-btn')?.classList.add('hidden');
  }

  /**
   * Cierra el modal de pago
   */
  closePaymentModal() {
    document.getElementById('modal-charge-to-room-btn')?.classList.add('hidden');
    document.getElementById('payment-modal')?.classList.add('hidden');
  }

  /**
   * Cierra el modal de confirmación de entrega
   */
  closeServeConfirmationModal() {
    document.getElementById('serve-confirmation-modal')?.classList.add('hidden');
  }

  /**
   * Abre el modal de pago (llamado desde el monitor)
   */
  async openPaymentModal(orderId, fetchUrl) {
    // Bloquear si el tutorial está activo en pagos
    if (window.tutorialBlockPaymentModal) {
      console.log('Payment modal blocked by tutorial');
      return;
    }

    if (!orderId || orderId === 'undefined') {
      console.error('Invalid orderId:', orderId);
      this.showToast('Error: ID de pedido inválido', 'error');
      return;
    }

    try {
      const response = await fetch(fetchUrl || `/restaurant/api/waiter/orders/${orderId}/`);
      if (!response.ok) throw new Error('Failed to fetch order details');
      const data = await response.json();

      document.getElementById('modal-title').textContent = `Confirmar Cobro - ${data.identifier || ''}`;
      const itemsList = document.getElementById('modal-order-items');
      itemsList.innerHTML = data.items.map(item => `
        <li class="flex justify-between">
          <span>${item.quantity}x ${item.name}</span>
          <span>$${(item.price * item.quantity).toLocaleString('es-CL')}</span>
        </li>
      `).join('');

      const subtotal = data.subtotal;
      this.setupPaymentModal(subtotal, orderId, data.room_number);

      document.getElementById('payment-modal')?.classList.remove('hidden');
    } catch (error) {
      console.error('Error opening payment modal:', error);
      this.showToast('No se pudo cargar el detalle del pedido.', 'error');
    }
  }

  /**
   * Configura la lógica interna del modal de pago
   */
  setupPaymentModal(subtotal, orderId, roomNumber) {
    const includeTipCheckbox = document.getElementById('include-tip-checkbox');
    const customTipInput = document.getElementById('custom-tip-percentage-input');
    const customTipAmountInput = document.getElementById('custom-tip-amount-input');
    const modalOrderSubtotal = document.getElementById('modal-order-subtotal');
    const modalOrderTip = document.getElementById('modal-order-tip');
    const modalOrderTotal = document.getElementById('modal-order-total');
    const splitInput = document.getElementById('split-bill-input');
    const splitResult = document.getElementById('split-bill-result');
    const tipPresetButtonsContainer = document.getElementById('tip-preset-buttons');
    const tipLabel = document.querySelector('label[for="include-tip-checkbox"]');

    let isUpdating = false;

    const calculateAndDisplayTotals = () => {
      modalOrderSubtotal.textContent = subtotal.toLocaleString('es-CL');

      let currentTip = 0;
      if (includeTipCheckbox.checked) {
        document.getElementById('tip-inputs').classList.remove('hidden');
        tipPresetButtonsContainer.classList.remove('hidden');
        tipLabel.classList.remove('bg-amber-200', 'text-amber-900', 'hover:bg-amber-300');
        tipLabel.classList.add('bg-green-100', 'text-green-800', 'hover:bg-green-200');
        includeTipCheckbox.classList.remove('text-amber-700');
        includeTipCheckbox.classList.add('text-green-600');
        currentTip = parseFloat(customTipAmountInput.value) || 0;
      } else {
        document.getElementById('tip-inputs').classList.add('hidden');
        tipPresetButtonsContainer.classList.add('hidden');
        tipLabel.classList.remove('bg-green-100', 'text-green-800', 'hover:bg-green-200');
        tipLabel.classList.add('bg-amber-200', 'text-amber-900', 'hover:bg-amber-300');
        includeTipCheckbox.classList.remove('text-green-600');
        includeTipCheckbox.classList.add('text-amber-700');
        currentTip = 0;
        customTipAmountInput.value = '0';
      }

      const totalWithTip = subtotal + currentTip;
      modalOrderTotal.textContent = totalWithTip.toLocaleString('es-CL');

      const numPeople = parseInt(splitInput.value) || 1;
      if (numPeople > 1) {
        const amountPerPerson = totalWithTip / numPeople;
        splitResult.textContent = ` pagos de $${amountPerPerson.toLocaleString('es-CL', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
      } else {
        splitResult.textContent = '';
      }
    };

    // Inicializar valores
    includeTipCheckbox.checked = false;
    customTipInput.value = "0";
    customTipInput.min = "0";
    customTipAmountInput.min = "0";
    customTipAmountInput.value = "10";
    includeTipCheckbox.classList.add('text-amber-700');

    // Botones de propina preestablecida
    const tipPresetButtons = tipPresetButtonsContainer.querySelectorAll('.tip-preset-btn');
    tipPresetButtons.forEach(button => {
      button.onclick = () => {
        const percentage = button.dataset.percentage;
        customTipInput.value = percentage;
        tipPresetButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        customTipInput.dispatchEvent(new Event('input'));
      };
    });

    includeTipCheckbox.onchange = calculateAndDisplayTotals;

    customTipInput.oninput = () => {
      if (isUpdating) return;
      isUpdating = true;
      const percentage = parseFloat(customTipInput.value) || 0;
      const tipAmount = subtotal * (percentage / 100);
      customTipAmountInput.value = Math.round(tipAmount);
      calculateAndDisplayTotals();
      isUpdating = false;
    };

    customTipAmountInput.oninput = () => {
      if (isUpdating) return;
      isUpdating = true;
      const amount = parseFloat(customTipAmountInput.value) || 0;
      const percentage = subtotal > 0 ? (amount / subtotal) * 100 : 0;
      customTipInput.value = percentage.toFixed(1);
      calculateAndDisplayTotals();
      isUpdating = false;
    };

    splitInput.value = "1";
    splitResult.textContent = '';
    splitInput.oninput = calculateAndDisplayTotals;

    const splitPresetButtons = document.querySelectorAll('.split-preset-btn');
    splitPresetButtons.forEach(button => {
      button.onclick = () => {
        splitInput.value = button.dataset.split;
        splitInput.dispatchEvent(new Event('input'));
      };
    });

    calculateAndDisplayTotals();

    // Payment method selector
    const paymentMethodBtns = document.querySelectorAll('.payment-method-btn');
    const selectedPaymentInput = document.getElementById('selected-payment-method');
    const paymentReferenceContainer = document.getElementById('payment-reference-container');
    
    paymentMethodBtns.forEach(btn => {
      btn.onclick = (e) => {
        e.preventDefault();
        const method = btn.dataset.method;
        selectedPaymentInput.value = method;
        
        // Update button styles - remove selected class from all buttons
        paymentMethodBtns.forEach(b => {
          b.classList.remove('selected');
        });
        
        // Add selected class to clicked button
        btn.classList.add('selected');
        
        // Show/hide reference field based on payment method
        if (method === 'transfer' || method === 'check') {
          paymentReferenceContainer.classList.remove('hidden');
        } else {
          paymentReferenceContainer.classList.add('hidden');
          document.getElementById('payment-reference').value = '';
        }
      };
    });
    
    // Set initial button state to cash
    const cashBtn = document.querySelector('[data-method="cash"]');
    if (cashBtn) {
      cashBtn.click();
    }

    // Botón de confirmación
    const confirmBtn = document.getElementById('modal-confirm-payment-btn');
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    newConfirmBtn.onclick = () => {
      // Get payment method and reference
      const paymentMethod = document.getElementById('selected-payment-method').value || 'cash';
      const paymentReference = document.getElementById('payment-reference')?.value || '';
      
      // Esto será llamado desde orders.js
      window.dispatchEvent(new CustomEvent('payment-confirmed', { 
        detail: { 
          orderId,
          paymentMethod,
          paymentReference
        } 
      }));
      this.closePaymentModal();
    };

    // Botón de cargar a habitación
    const chargeToRoomBtn = document.getElementById('modal-charge-to-room-btn');
    if (roomNumber) {
      chargeToRoomBtn.classList.remove('hidden');
      chargeToRoomBtn.onclick = () => {
        // Get payment method and reference
        const paymentMethod = document.getElementById('selected-payment-method').value || 'cash';
        const paymentReference = document.getElementById('payment-reference')?.value || '';
        
        window.dispatchEvent(new CustomEvent('charge-to-room', { 
          detail: { 
            orderId,
            paymentMethod,
            paymentReference
          } 
        }));
        this.closePaymentModal();
      };
    } else {
      chargeToRoomBtn.classList.add('hidden');
    }
  }

  /**
   * Muestra la vista de pedidos
   */
  showOrderView() {
    document.querySelectorAll('.content-section').forEach(s => s.classList.add('hidden'));
    document.getElementById('order-view')?.classList.remove('hidden');
    
    // Restaurar el carrito a vista normal (no oculto)
    const currentOrderDiv = document.getElementById('current-order');
    if (currentOrderDiv) {
      currentOrderDiv.classList.remove('hidden');
    }
    
    // Restaurar el grid de 2 columnas
    const menuContainer = document.querySelector('#order-view .grid.grid-cols-1');
    if (menuContainer) {
      menuContainer.classList.add('md:grid-cols-2');
      menuContainer.classList.remove('md:grid-cols-1');
    }
    
    const menuLeftDiv = document.querySelector('#order-view .border-r');
    if (menuLeftDiv) {
      // El border-r y pr-6 ya deberían estar en el HTML
    }
    
    // Asegurar que el botón del carrito SIEMPRE sea visible
    const cartToggle = document.getElementById('cart-toggle');
    if (cartToggle) {
      cartToggle.classList.remove('hidden');
      cartToggle.style.display = 'block';
      cartToggle.style.visibility = 'visible';
      cartToggle.style.opacity = '1';
      cartToggle.style.pointerEvents = 'auto';
    }
    
    // NO abrir el carrito automáticamente en móvil - dejar que el usuario lo abra manualmente
    // El usuario puede hacer click en el botón cart-toggle si quiere verlo
  }

  /**
   * Muestra la vista de menú sin abrir el carrito (para editar desde cobros)
   */
  showMenuView() {
    document.querySelectorAll('.content-section').forEach(s => s.classList.add('hidden'));
    document.getElementById('order-view')?.classList.remove('hidden');
    
    // Ocultar el carrito lateral para que solo se vea el menú
    const currentOrderDiv = document.getElementById('current-order');
    if (currentOrderDiv) {
      currentOrderDiv.classList.add('hidden');
    }
    
    // Mostrar el menú a pantalla completa sin la división de columnas
    const menuContainer = document.querySelector('#order-view .grid.grid-cols-1');
    if (menuContainer) {
      menuContainer.classList.remove('md:grid-cols-2');
      menuContainer.classList.add('md:grid-cols-1');
    }
    
    const menuLeftDiv = document.querySelector('#order-view .border-r');
    if (menuLeftDiv) {
      menuLeftDiv.classList.remove('border-r', 'pr-6');
    }
  }

  /**
   * Oculta la vista de pedidos
   */
  hideOrderView() {
    document.getElementById('order-view')?.classList.add('hidden');
  }

  /**
   * Muestra la sección principal anterior
   */
  showMainSectionView() {
    try {
      const activeSectionId = document.querySelector('.nav-link.active')?.dataset.section || 'dashboard';
      document.querySelectorAll('.content-section').forEach(s => s.classList.add('hidden'));
      const targetSection = document.getElementById(activeSectionId);
      if (targetSection) {
        targetSection.classList.remove('hidden');
      }
      this.hideOrderView();
      this.resetCategoryFilters();
    } catch (error) {
      console.error('Error in showMainSectionView:', error);
      document.querySelectorAll('.content-section').forEach(s => s.classList.add('hidden'));
      const dashboardSection = document.getElementById('dashboard');
      if (dashboardSection) dashboardSection.classList.remove('hidden');
      this.hideOrderView();
    }
  }

  /**
   * Reinicia los filtros de categoría (delegado al MenuManager)
   */
  resetCategoryFilters() {
    const filterButtons = document.querySelectorAll('#category-filters .category-filter');
    filterButtons.forEach(button => {
      button.style.display = 'inline-flex';
    });

    const allButton = document.querySelector('.category-filter[data-category="all"]');
    if (allButton) {
      allButton.click();
    }

    const searchInput = document.getElementById('menu-search-input');
    if (searchInput) {
      searchInput.value = '';
    }
  }

  /**
   * Muestra un toast de notificación
   */
  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast`;

    const icons = {
      success: `<svg class="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
      error: `<svg class="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
      info: `<svg class="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`
    };

    const iconHTML = icons[type] || icons['info'];
    const messageSpan = document.createElement('span');
    messageSpan.textContent = message;

    toast.innerHTML = iconHTML;
    toast.appendChild(messageSpan);
    toast.classList.add(type);

    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 500);
    }, 3000);
  }

  /**
   * Restaura la última sección activa
   */
  restoreLastSection() {
    const savedSection = localStorage.getItem('activeWaiterSection') || 'dashboard';
    const savedLink = document.querySelector(`.nav-link[data-section="${savedSection}"]`);
    if (savedLink) {
      savedLink.click();
    } else {
      const dashboardLink = document.querySelector('.nav-link[data-section="dashboard"]');
      if (dashboardLink) dashboardLink.click();
    }
  }
}
