/**
 * Tutorial Interactivo para el Dashboard
 * Guía al usuario a través de los elementos principales
 */

class DashboardTutorial {
    constructor() {
        // Inicializar variable global para bloquear modal de pagos
        window.tutorialBlockPaymentModal = false;
        
        // Función helper para crear SVGs
        this.getSVG = (name) => {
            const svgs = {
                menu: '<svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>',
                user: '<svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>',
                home: '<svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9m-9 11l4-4m0 0l4 4m-4-4V3"></path></svg>',
                check: '<svg class="w-5 h-5 inline-block mr-2" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>',
                plate: '<svg class="w-5 h-5 inline-block mr-2" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"></path></svg>',
                cart: '<svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>',
                send: '<svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>',
                drink: '<svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3v-3"></path></svg>',
                list: '<svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>',
                card: '<svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>'
            };
            return svgs[name] || '';
        };

        this.tutorials = {
            'dashboard': [
                {
                    element: '#client-identifier',
                    title: this.getSVG('user') + 'Identificador del Cliente',
                    text: 'Ingresa el nombre del cliente, número de mesa o identificador. Ejemplos: "Mesa 5", "Juan García", "Barra 1", "Habitación 203".',
                },
                {
                    element: '#room-number',
                    title: this.getSVG('home') + 'Número de Habitación',
                    text: 'Si el cliente es huésped del hotel, ingresa su número de habitación aquí. Esto permite cargar el pedido a su cuenta. Si no aplica, déjalo vacío.',
                },
                {
                    element: '#start-table-order-btn',
                    title: this.getSVG('check') + 'Iniciar Pedido',
                    text: 'Haz click para crear un nuevo pedido. Asegúrate de haber completado la información del cliente antes de iniciar. 🔸 Este es el final de la primera parte del tutorial.',
                }
            ],
            'dashboard_orders': [
                {
                    element: '.add-to-order-btn',
                    title: this.getSVG('plate') + 'Agregar Productos al Pedido',
                    text: 'Haz click en "Agregar" para añadir un plato o bebida al pedido actual. Puedes agregar múltiples productos. El precio se actualiza automáticamente.',
                },
                {
                    element: '#current-order',
                    title: this.getSVG('list') + 'Detalles del Pedido Actual',
                    text: 'Aquí ves un resumen completo del pedido actual: cliente, productos, cantidades y totales. Puedes revisar todos los detalles antes de enviar a cocina.',
                },
                {
                    element: '#cart-toggle',
                    title: this.getSVG('cart') + 'Ver Carrito de Compras',
                    text: 'Haz click para abrir el carrito y revisar todos los productos agregados. Aquí puedes ver el subtotal, impuestos y el total del pedido.',
                },
                {
                    element: '#cart-submit-btn',
                    title: this.getSVG('send') + 'Enviar Pedido a la Cocina',
                    text: 'Cuando hayas terminado de agregar productos, haz click aquí para enviar el pedido a la cocina. El pedido aparecerá en el Monitor de Cocina. ✓ ¡Tutorial completado!',
                }
            ],
            'bar': [
                {
                    element: '#bar-client-identifier',
                    title: this.getSVG('user') + 'Identificador del Cliente',
                    text: 'Ingresa el nombre o identificador del cliente de la barra. Ejemplos: "Barra 1", "Cliente de la esquina", "Juan Pérez".',
                },
                {
                    element: '#bar-room-number',
                    title: this.getSVG('home') + 'Número de Habitación (Opcional)',
                    text: 'Si el cliente es huésped del hotel, ingresa su número de habitación. Esto permite cargar el pedido a su cuenta. Si no aplica, déjalo vacío.',
                },
                {
                    element: '#start-bar-order-btn',
                    title: this.getSVG('check') + 'Iniciar Pedido de Barra',
                    text: 'Haz click para crear un nuevo pedido de barra. Esto abrirá el menú completo para agregar bebidas y productos.',
                },
                {
                    element: '#menu-items-container',
                    title: this.getSVG('drink') + 'Menú de Bebidas y Productos',
                    text: 'Este es el catálogo completo disponible. Busca por nombre o filtra por categoría. Haz click en "Agregar" para incluir un producto al pedido.',
                },
                {
                    element: '#current-order',
                    title: this.getSVG('list') + 'Resumen del Pedido Actual',
                    text: 'Aquí ves todos los productos agregados al pedido, cantidades y el total. Puedes eliminar items si es necesario.',
                }
            ],
            'monitor': [
                {
                    element: '#in-progress-orders-list-monitor',
                    title: this.getSVG('list') + 'Pedidos en Curso',
                    text: 'Esta es la lista de pedidos que están siendo preparados en la cocina. Muestra el cliente, productos solicitados y el tiempo que llevan en preparación.',
                },
                {
                    element: '.status-changer',
                    title: this.getSVG('send') + 'Cambiar Estado del Pedido',
                    text: 'Utiliza este selector para cambiar el estado del pedido. Puedes seleccionar entre: Pendiente, En Preparación o Listo. Esto actualiza el progreso de la preparación.',
                },
                {
                    element: '#ready-orders-list-monitor',
                    title: this.getSVG('check') + 'Pedidos Listos para Servir',
                    text: 'Aquí aparecen todos los pedidos que ya han sido preparados en la cocina y están listos para servir a los clientes. Haz click en "Servir" para entregar el pedido al cliente.',
                },
                {
                    element: '.view-details-btn',
                    title: this.getSVG('list') + 'Ver Detalles del Pedido',
                    text: 'Haz click en este botón para ver los detalles completos del pedido, incluyendo todos los productos, cantidades y notas especiales.',
                },
                {
                    element: '.mark-served-monitor-btn',
                    title: this.getSVG('check') + 'Cambiar Estado - Marcar Servido',
                    text: 'Haz click aquí para marcar el pedido como servido. El pedido se moverá a la sección de "Pedidos Servidos (para Cobrar)" y aparecerá en el panel de cobros.',
                }
            ],
            'payments': [
                {
                    element: '#served-orders-list-monitor',
                    title: this.getSVG('send') + 'Sección de Cobros - Pedidos Servidos',
                    text: 'Esta sección muestra TODOS los pedidos que ya han sido servidos y están listos para cobrar.\n\n' +
                          '🔸 Aquí verás una lista de todos los pedidos pendientes de cobro\n' +
                          '🔸 Cada pedido muestra el identificador del cliente y el total a cobrar\n' +
                          '🔸 Haz click en el botón "Cobrar" para abrir el modal de pago',
                },
                {
                    element: '.charge-btn',
                    title: this.getSVG('card') + 'Botón Cobrar - Procesar Pago',
                    text: 'El botón "Cobrar" abre el modal de pago para este pedido.\n\n' +
                          '🔸 El modal mostrará todos los productos del pedido\n' +
                          '🔸 Verás el subtotal y el total a cobrar\n' +
                          '🔸 Luego seleccionarás el método de pago\n\n' +
                          '💡 Tip: Asegúrate de que el cliente esté presente antes de procesar el pago',
                },
                {
                    element: '#payment-modal #modal-order-subtotal',
                    title: this.getSVG('list') + 'Resumen de Productos - Modal de Pago',
                    text: 'En el modal de pago verás una lista completa de todos los productos del pedido.\n\n' +
                          '🔸 Verifica que todos los productos están aquí\n' +
                          '🔸 Confirma la cantidad de cada producto\n' +
                          '🔸 Revisa el subtotal que se muestra aquí\n' +
                          '🔸 Confirma que el cliente no quiera agregar o quitar nada\n\n' +
                          '💡 Si hay un error, cancela y regresa a editar el pedido',
                },
                {
                    element: '#payment-modal .payment-method-btn:nth-child(3)',
                    title: this.getSVG('send') + 'Seleccionar Método de Pago',
                    text: 'Ahora selecciona cómo va a pagar el cliente. Los 5 métodos disponibles son:\n\n' +
                          '💵 Efectivo - Pago en efectivo al contado\n' +
                          '💳 Tarjeta - Tarjeta de crédito o débito\n' +
                          '🏦 Transferencia - Transferencia bancaria\n' +
                          '📋 Cheque - Pago con cheque\n' +
                          '🔀 Mixto - Combinación de dos o más métodos\n\n' +
                          '🔸 El botón del método seleccionado se pondrá de color ámbar\n' +
                          '🔸 Si seleccionas Transferencia o Cheque, aparecerá un campo para el comprobante',
                },
                {
                    element: '#payment-reference-container',
                    title: this.getSVG('list') + 'Campo de Referencia - Para Cheques y Transferencias',
                    text: 'Este campo aparece SOLO si seleccionaste Cheque o Transferencia.\n\n' +
                          '🔸 Ingresa el número de cheque o comprobante de transferencia\n' +
                          '🔸 Esto es importante para el registro y conciliación\n' +
                          '🔸 Ejemplo: "12345678" para un cheque o "Ref-2025-001" para transferencia\n\n' +
                          '💡 Tip: Ten el comprobante a mano antes de procesar el pago',
                },
                {
                    element: '#include-tip-checkbox',
                    title: this.getSVG('list') + 'Incluir Propina - Opcional',
                    text: 'El cliente puede dejar propina al pagar. Esto es OPCIONAL.\n\n' +
                          '🔸 Marca el checkbox "Incluir Propina" si el cliente quiere dejar propina\n' +
                          '🔸 Si NO marca, la propina será $0\n' +
                          '🔸 En el siguiente paso verás cómo calcular el monto de propina',
                },
                {
                    element: '#tip-preset-buttons .tip-preset-btn:first-child',
                    title: this.getSVG('check') + 'Propinas Rápidas - Porcentajes Predefinidos',
                    text: 'Si el cliente quiere dejar propina, puedes usar los botones rápidos:\n\n' +
                          '🔸 10% - Calcula automáticamente el 10% del subtotal\n' +
                          '🔸 15% - Calcula automáticamente el 15% del subtotal\n' +
                          '🔸 20% - Calcula automáticamente el 20% del subtotal\n\n' +
                          '💡 O puedes ingresar un monto personalizado manualmente\n' +
                          '💡 El total se actualiza automáticamente',
                },
                {
                    element: '#modal-order-total',
                    title: this.getSVG('send') + 'Total Final - Monto a Cobrar',
                    text: 'Este es el monto FINAL que el cliente debe pagar.\n\n' +
                          '🔸 Se calcula como: Subtotal + Propina (si la hay)\n' +
                          '🔸 Verifica que sea el monto correcto\n' +
                          '🔸 Comunica este monto al cliente antes de procesar\n\n' +
                          '💡 El cliente debe tener este monto en la forma de pago seleccionada',
                },
                {
                    element: '#modal-charge-to-room-btn',
                    title: this.getSVG('home') + 'Cargar a Habitación',
                    text: 'Aparece si ingresaste número de habitación.\n\n' +
                          '🔸 Carga el pedido a la cuenta de la habitación\n' +
                          '🔸 El cliente pagará en recepción',
                },
                {
                    element: '#modal-confirm-payment-btn',
                    title: this.getSVG('check') + 'Confirmar Pago',
                    text: 'Elige uno de estos botones:\n\n' +
                          '🔸 "Confirmar Pago" - Pago inmediato\n' +
                          '🔸 "Cargar a Habitación" - Para huéspedes\n\n' +
                          '✓ El pedido se marcará como PAGADO',
                }
            ]
        };

        this.currentSection = 'dashboard';
        this.currentStep = 0;
        this.tutorialActive = false;
        this.openedCartModal = false;
        this.paymentModalWasHidden = false;
        this.actionListeners = {}; // Para rastrear listeners de acciones
        this.completedActions = {}; // Para rastrear acciones completadas por paso

        // HTML del modal
        this.modalHtml = `
            <div id="tutorial-overlay" class="fixed inset-0 z-50 hidden"></div>
            <div id="tutorial-modal" class="fixed bg-white rounded-xl shadow-2xl max-w-sm p-6 z-50 hidden" style="width: 360px; top: 50%; left: 50%; transform: translate(-50%, -50%); max-height: 90vh; overflow-y: auto;">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex-1">
                        <h3 id="tutorial-title" class="text-lg font-bold text-amber-900 mb-2"></h3>
                        <p id="tutorial-text" class="text-gray-700 text-sm mb-4 leading-relaxed"></p>
                    </div>
                    <button id="tutorial-close" class="text-gray-400 hover:text-gray-600 ml-2 flex-shrink-0">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <div id="tutorial-progress" class="flex gap-1 mb-4"></div>

                <div class="flex gap-2">
                    <button id="tutorial-prev" class="flex-1 px-2 py-2 border border-amber-900 text-amber-900 rounded-lg hover:bg-amber-50 transition-colors text-xs font-medium">
                        ← Anterior
                    </button>
                    <button id="tutorial-next" class="flex-1 px-2 py-2 bg-amber-900 text-white rounded-lg hover:bg-amber-800 transition-colors text-xs font-medium">
                        Siguiente →
                    </button>
                </div>
            </div>

            <style>
                #tutorial-overlay {
                    background: transparent;
                    pointer-events: none;
                }
                #tutorial-overlay.show {
                    display: block !important;
                }
                #tutorial-modal {
                    animation: slideUp 0.3s ease-out;
                    transition: all 0.3s ease-out;
                    pointer-events: auto;
                    z-index: 9999 !important;
                    display: none !important;
                }
                #tutorial-modal.show {
                    display: block !important;
                }
                .tutorial-action-badge {
                    display: inline-block;
                    background-color: #dcfce7;
                    color: #166534;
                    padding: 0.25rem 0.75rem;
                    border-radius: 9999px;
                    font-size: 0.75rem;
                    font-weight: 500;
                    border-left: 2px solid #22c55e;
                }
                .tutorial-progress-dot.active {
                    background-color: #92400e;
                }
                .tutorial-progress-dot {
                    height: 4px;
                    flex: 1;
                    background-color: #d1d5db;
                    border-radius: 2px;
                }
                @keyframes slideUp {
                    from {
                        opacity: 0;
                        transform: translate(-50%, calc(-50% + 10px));
                    }
                    to {
                        opacity: 1;
                        transform: translate(-50%, -50%);
                    }
                }
                #tutorial-highlight {
                    animation: pulse 2s infinite, border-pulse 1.5s infinite;
                    pointer-events: none;
                    z-index: 1000;
                }
                @keyframes pulse {
                    0%, 100% {
                        box-shadow: 0 0 0 0 rgba(146, 64, 14, 0.7);
                    }
                    50% {
                        box-shadow: 0 0 0 15px rgba(146, 64, 14, 0);
                    }
                }
                @keyframes border-pulse {
                    0%, 100% {
                        border-color: rgba(146, 64, 14, 0.9);
                    }
                    50% {
                        border-color: rgba(251, 146, 60, 0.9);
                    }
                }
            </style>
        `;
    }

    hasTutorialBeenCompleted() {
        return localStorage.getItem('tutorialCompleted') === 'true';
    }

    markTutorialAsCompleted() {
        localStorage.setItem('tutorialCompleted', 'true');
    }

    setupActionListeners() {
        // Limpiar listeners anteriores
        this.removeActionListeners();

        const step = this.tutorials[this.currentSection][this.currentStep];
        if (!step) return;

        // Obtener todos los elementos que coinciden (puede ser una clase o ID)
        const elements = document.querySelectorAll(step.element);
        
        // Si no hay elementos, avanzar automáticamente después de 0.4 segundos
        if (elements.length === 0) {
            console.warn(`No elements found for selector: ${step.element}. Skipping step...`);
            setTimeout(() => this.nextStep(), 400);
            return;
        }

        const stepKey = `${this.currentSection}-${this.currentStep}`;

        elements.forEach((element, index) => {
            // Crear ID único para este listener
            const listenerId = `tutorial-step-${this.currentSection}-${this.currentStep}-${index}`;
            this.actionListeners[listenerId] = null;

            // Detectar diferentes tipos de acciones según el elemento
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                // Para inputs, detectar cuando tienen valor
                const checkInput = () => {
                    if (element.value.trim() !== '') {
                        // Registrar acción
                        this.recordAction(stepKey, 'Datos ingresados correctamente');
                        setTimeout(() => this.nextStep(), 100);
                    }
                };
                element.addEventListener('change', checkInput);
                this.actionListeners[listenerId] = { element, event: 'change', handler: checkInput };
            } else if (element.tagName === 'BUTTON' || 
                       element.classList.contains('add-to-order-btn') || 
                       element.classList.contains('add-drink-btn') || 
                       element.classList.contains('order-ready-btn') ||
                       element.classList.contains('charge-btn') ||
                       element.id.includes('btn') ||
                       element.id.includes('button')) {
                // Para botones, detectar click
                const checkClick = (e) => {
                    // Si es el botón de cobro y el tutorial está bloqueando, detener todo
                    if (element.classList.contains('charge-btn') && window.tutorialBlockPaymentModal) {
                        e.preventDefault();
                        e.stopPropagation();
                        e.stopImmediatePropagation();
                    }
                    // Registrar acción con el nombre del botón o elemento
                    let actionText = element.textContent?.trim() || element.getAttribute('title') || 'Acción realizada';
                    if (actionText.length > 30) actionText = actionText.substring(0, 27) + '...';
                    this.recordAction(stepKey, actionText);
                    setTimeout(() => this.nextStep(), 100);
                };
                element.addEventListener('click', checkClick, true); // Capture phase para ejecutarse primero
                this.actionListeners[listenerId] = { element, event: 'click', handler: checkClick, useCapture: true };
            } else {
                // Para elementos que no son inputs ni botones, detectar click genérico
                const checkClick = () => {
                    let actionText = element.textContent?.trim() || element.getAttribute('title') || 'Elemento interactuado';
                    if (actionText.length > 30) actionText = actionText.substring(0, 27) + '...';
                    this.recordAction(stepKey, actionText);
                    setTimeout(() => this.nextStep(), 600);
                };
                element.addEventListener('click', checkClick);
                this.actionListeners[listenerId] = { element, event: 'click', handler: checkClick };
            }
        });
    }

    recordAction(stepKey, actionText) {
        if (!this.completedActions[stepKey]) {
            this.completedActions[stepKey] = [];
        }
        this.completedActions[stepKey].push({
            text: actionText,
            timestamp: new Date().toLocaleTimeString()
        });
    }

    removeActionListeners() {
        Object.values(this.actionListeners).forEach(listener => {
            if (listener) {
                if (listener.observer) {
                    listener.observer.disconnect();
                } else if (listener.element && listener.handler && listener.event) {
                    listener.element.removeEventListener(listener.event, listener.handler, listener.useCapture || false);
                }
            }
        });
        this.actionListeners = {};
    }

    init() {
        // Crear el modal HTML
        document.body.insertAdjacentHTML('beforeend', this.modalHtml);
        
        // Crear botón para iniciar tutorial
        const tutorialBtn = document.createElement('button');
        tutorialBtn.id = 'tutorial-btn';
        tutorialBtn.className = 'fixed bottom-4 right-4 z-40 p-3 bg-amber-900 text-white rounded-full shadow-lg hover:bg-amber-800 transition-colors';
        tutorialBtn.title = 'Inicia el tutorial interactivo';
        tutorialBtn.innerHTML = `
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
        `;
        
        document.body.appendChild(tutorialBtn);

        // Event listeners
        tutorialBtn.addEventListener('click', () => this.start());
        document.getElementById('tutorial-close').addEventListener('click', () => this.end());
        document.getElementById('tutorial-next').addEventListener('click', () => this.nextStep());
        document.getElementById('tutorial-prev').addEventListener('click', () => this.prevStep());
        document.getElementById('tutorial-overlay').addEventListener('click', () => this.end());

        // Bloqueador de clics para la sección monitor
        document.addEventListener('click', (e) => {
            if (this.tutorialActive && this.currentSection === 'monitor') {
                // Permitir clics SOLO en status-changer
                if (!e.target.closest('.status-changer')) {
                    // Bloquear cualquier otro clic
                    const monitor = document.querySelector('#in-progress-orders-list-monitor, #ready-orders-list-monitor');
                    if (monitor && monitor.contains(e.target)) {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                }
            }
        }, true); // Usar capture phase para interceptar primero

        // Detectar cambios de sección
        document.addEventListener('click', (e) => {
            const navLink = e.target.closest('[data-section]');
            if (navLink) {
                const section = navLink.dataset.section;
                if (section && this.tutorials[section]) {
                    this.currentSection = section;
                    this.currentStep = 0;
                    
                    // Bloquear modal de pagos si estamos en tutorial y la sección es pagos
                    if (this.tutorialActive && section === 'payments') {
                        window.tutorialBlockPaymentModal = true;
                    } else {
                        window.tutorialBlockPaymentModal = false;
                    }
                    
                    if (this.tutorialActive) {
                        this.showStep();
                    }
                }
            }
        });

        // Cerrar tutorial con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.tutorialActive) {
                this.end();
            }
        });

        // Detectar cuando se inicia un pedido en la sección dashboard
        const observer = new MutationObserver(() => {
            if (this.tutorialActive && this.currentSection === 'dashboard') {
                // Verificar si aparecieron los elementos del pedido (esto indica que se inició un pedido)
                const orderStarted = document.querySelector('.add-to-order-btn') && document.querySelector('#current-order');
                const startBtn = document.querySelector('#start-table-order-btn');
                
                // Si el botón de iniciar ya no existe o está oculto, y aparecen los elementos del pedido
                if (orderStarted && (!startBtn || startBtn.offsetParent === null)) {
                    console.log('Pedido iniciado detectado, cambiando a sección dashboard_orders');
                    this.currentSection = 'dashboard_orders';
                    this.currentStep = 0;
                    this.showStep();
                    this.setupActionListeners();
                }
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class', 'style']
        });

        // NO auto-lanzar tutorial automáticamente
        // El usuario debe hacer click en el botón de ayuda manualmente
    }

    start() {
        this.tutorialActive = true;
        this.currentStep = 0;
        document.getElementById('tutorial-overlay').classList.add('show');
        document.getElementById('tutorial-modal').classList.add('show');
        
        // Detectar sección actual del visible content
        const activeSection = document.querySelector('[data-section].active') || 
                              document.querySelector('.content-section:not(.hidden)');
        
        if (activeSection && activeSection.id) {
            this.currentSection = activeSection.id;
        }
        
        console.log('Tutorial started in section:', this.currentSection);
        
        // Bloquear modal de pagos si iniciamos en sección de pagos
        if (this.currentSection === 'payments') {
            window.tutorialBlockPaymentModal = true;
        } else {
            window.tutorialBlockPaymentModal = false;
        }
        console.log('Payment modal blocking:', window.tutorialBlockPaymentModal);
        
        this.updateProgressDots();
        this.showStep();
        this.setupActionListeners();
    }

    end() {
        this.tutorialActive = false;
        document.getElementById('tutorial-overlay').classList.remove('show');
        document.getElementById('tutorial-modal').classList.remove('show');
        
        // Desbloquear el evento openPaymentModal
        window.tutorialBlockPaymentModal = false;
        this.removeHighlight();
        this.removeActionListeners();
        
        // Asegurar que se remuevan todos los highlights
        const highlights = document.querySelectorAll('#tutorial-highlight');
        highlights.forEach(highlight => highlight.remove());
        // Limpiar listener de reposicionamiento
        if (this.repositionListener) {
            window.removeEventListener('scroll', this.repositionListener, true);
            window.removeEventListener('resize', this.repositionListener);
        }
        this.markTutorialAsCompleted();
    }

    nextStep() {
        const steps = this.tutorials[this.currentSection];
        if (this.currentStep < steps.length - 1) {
            this.currentStep++;
            
            // Añadir delay extra cuando se transiciona a "Pedidos Listos para Servir" en la sección monitor
            const currentStep = steps[this.currentStep];
            const delay = (this.currentSection === 'monitor' && currentStep.element === '#ready-orders-list-monitor') ? 1000 : 0;
            
            if (delay > 0) {
                setTimeout(() => this.showStep(), delay);
            } else {
                this.showStep();
            }
        } else {
            this.end();
        }
    }

    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.showStep();
        }
    }

    updateProgressDots() {
        const progressContainer = document.getElementById('tutorial-progress');
        const steps = this.tutorials[this.currentSection];
        progressContainer.innerHTML = steps.map((_, i) => 
            `<div class="tutorial-progress-dot ${i === this.currentStep ? 'active' : ''}"></div>`
        ).join('');
    }

    showStep() {
        const steps = this.tutorials[this.currentSection];
        const step = steps[this.currentStep];
        
        if (!step) return;

        // Actualizar contenido
        document.getElementById('tutorial-title').innerHTML = step.title;
        document.getElementById('tutorial-text').textContent = step.text;

        // Actualizar progreso
        this.updateProgressDots();

        // Mostrar/ocultar botones
        document.getElementById('tutorial-prev').style.display = this.currentStep === 0 ? 'none' : 'block';
        const nextBtn = document.getElementById('tutorial-next');
        if (this.currentStep === steps.length - 1) {
            nextBtn.innerHTML = this.getSVG('check') + 'Finalizar';
        } else {
            nextBtn.textContent = 'Siguiente →';
        }

        // Desbloquear modal de pago cuando llegamos al paso del botón "Cobrar"
        // Esto permite que se abra el modal real en lugar de crear uno nuevo
        if (step.element === '.charge-btn' || 
            step.element.includes('#payment-modal') || 
            step.element.includes('#modal-')) {
            window.tutorialBlockPaymentModal = false;
        } else {
            window.tutorialBlockPaymentModal = true;
        }

        // Resaltar elemento y posicionar modal
        this.highlightElement(step.element);
        this.positionModal(step.element);
        
        // Agregar listener para reposicionar el modal cuando hay scroll o resize
        this.addRepositionListener(step.element);

        // Configurar listeners para auto-avance
        this.setupActionListeners();
    }

    addRepositionListener(selector) {
        // Limpiar listener anterior si existe
        if (this.repositionListener) {
            window.removeEventListener('scroll', this.repositionListener, true);
            window.removeEventListener('resize', this.repositionListener);
        }

        // Crear función que reposiciona el modal
        this.repositionListener = () => {
            if (this.tutorialActive) {
                this.positionModal(selector);
            }
        };

        // Agregar listeners
        window.addEventListener('scroll', this.repositionListener, true);
        window.addEventListener('resize', this.repositionListener);
    }

    positionModal(selector) {
        const modal = document.getElementById('tutorial-modal');
        let element = document.querySelector(selector);
        
        if (!modal) return;

        // Si el elemento no existe o no está visible, centrar el modal
        if (!element || element.offsetParent === null) {
            modal.style.left = (window.innerWidth / 2) + 'px';
            modal.style.top = window.innerHeight / 2 + window.scrollY + 'px';
            modal.style.transform = 'translate(-50%, -50%)';
            return;
        }

        const elementRect = element.getBoundingClientRect();
        const modalWidth = 360;
        const modalHeight = 280;
        const gap = 20;
        const padding = 15;

        // Intentar posiciones: derecha, izquierda, abajo, arriba
        let positioned = false;
        let top, left, transform;

        // 1. Intentar a la DERECHA
        if (elementRect.right + gap + modalWidth + padding <= window.innerWidth) {
            left = elementRect.right + gap + window.scrollX;
            top = elementRect.top + window.scrollY + (elementRect.height / 2);
            transform = 'translateY(-50%)';
            positioned = true;
        }
        // 2. Intentar a la IZQUIERDA
        else if (elementRect.left - gap - modalWidth >= padding) {
            left = elementRect.left - gap - modalWidth + window.scrollX;
            top = elementRect.top + window.scrollY + (elementRect.height / 2);
            transform = 'translateY(-50%)';
            positioned = true;
        }
        // 3. Intentar ABAJO
        else if (elementRect.bottom + gap + modalHeight <= window.innerHeight + window.scrollY) {
            left = elementRect.left + window.scrollX + (elementRect.width / 2);
            top = elementRect.bottom + gap + window.scrollY;
            transform = 'translate(-50%, 0)';
            positioned = true;
        }
        // 4. Intentar ARRIBA
        else if (elementRect.top - gap - modalHeight >= padding + window.scrollY) {
            left = elementRect.left + window.scrollX + (elementRect.width / 2);
            top = elementRect.top + window.scrollY - gap - modalHeight;
            transform = 'translate(-50%, 0)';
            positioned = true;
        }

        // Si no hay espacio en ningún lado, centrar en pantalla
        if (!positioned) {
            left = window.innerWidth / 2;
            top = window.innerHeight / 2 + window.scrollY;
            transform = 'translate(-50%, -50%)';
        }

        // Aplicar límites para mantener el modal visible
        left = Math.max(padding, Math.min(left, window.innerWidth - padding));
        
        modal.style.left = left + 'px';
        modal.style.top = top + 'px';
        modal.style.transform = transform;
    }

    highlightElement(selector) {
        this.removeHighlight();
        
        // Obtener el primer elemento que coincida
        const element = document.querySelector(selector);
        if (!element) return;

        // Si es el botón de realizar pedido, abrir el modal del carrito
        if (selector === '#cart-submit-btn') {
            const cartModal = document.getElementById('cart-modal');
            if (cartModal && cartModal.classList.contains('hidden')) {
                cartModal.classList.remove('hidden');
                // Guardar que abrimos el modal para cerrarlo después
                this.openedCartModal = true;
            }
        }

        // Si el elemento está dentro del modal de pago, mostrarlo temporalmente
        const paymentModal = document.getElementById('payment-modal');
        let paymentModalWasHidden = false;
        if (paymentModal && paymentModal.classList.contains('hidden') && element.closest('#payment-modal')) {
            paymentModal.classList.remove('hidden');
            paymentModalWasHidden = true;
        }

        // Pequeño delay para permitir que el navegador renderice el elemento
        setTimeout(() => {
            const rect = element.getBoundingClientRect();
            
            // Crear highlight con borde titilante
            const highlight = document.createElement('div');
            highlight.id = 'tutorial-highlight';
            highlight.className = 'absolute z-50 border-4 border-amber-600 rounded-lg pointer-events-none';
            
            highlight.style.top = (rect.top + window.scrollY - 8) + 'px';
            highlight.style.left = (rect.left + window.scrollX - 8) + 'px';
            highlight.style.width = (rect.width + 16) + 'px';
            highlight.style.height = (rect.height + 16) + 'px';
            
            document.body.appendChild(highlight);

            // Si tuvimos que mostrar el modal temporalmente, guardamos esa información
            if (paymentModalWasHidden) {
                this.paymentModalWasHidden = true;
            }
        }, 50);
    }

    removeHighlight() {
        // Remover TODOS los highlights (en caso de que haya múltiples)
        const highlights = document.querySelectorAll('#tutorial-highlight');
        highlights.forEach(highlight => highlight.remove());

        // Si abrimos el modal del carrito, cerrarlo de nuevo
        if (this.openedCartModal) {
            const cartModal = document.getElementById('cart-modal');
            if (cartModal) {
                cartModal.classList.add('hidden');
            }
            this.openedCartModal = false;
        }

        // Cerrar modales de detalles si están abiertos
        const detailsModal = document.getElementById('order-details-modal');
        if (detailsModal && !detailsModal.classList.contains('hidden')) {
            detailsModal.classList.add('hidden');
        }

        // Cerrar modales de confirmación de entrega
        const confirmModal = document.querySelector('[id*="confirm-modal"]');
        if (confirmModal && !confirmModal.classList.contains('hidden')) {
            confirmModal.classList.add('hidden');
        }

        // Restaurar visibilidad del modal de pago si fue mostrado temporalmente
        if (this.paymentModalWasHidden) {
            const paymentModal = document.getElementById('payment-modal');
            if (paymentModal) {
                paymentModal.classList.add('hidden');
            }
            this.paymentModalWasHidden = false;
        }

        // Si abrimos el modal de pago temporalmente, mantenerlo abierto para que el usuario interactúe
        // (No lo cerramos aquí porque el usuario necesita ver los elementos del modal)
    }
}

// Inicializar cuando el DOM está listo
document.addEventListener('DOMContentLoaded', () => {
    const tutorial = new DashboardTutorial();
    tutorial.init();
});
