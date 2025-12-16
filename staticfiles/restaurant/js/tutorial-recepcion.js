/**
 * Tutorial Interactivo para el Dashboard de Recepción
 * Guía al recepcionista a través de los elementos principales
 */

class ReceptionTutorial {
    constructor() {
        // Función helper para crear SVGs
        this.getSVG = (name) => {
            const svgs = {
                card: '<svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>',
                send: '<svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>',
                home: '<svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9m-9 11l4-4m0 0l4 4m-4-4V3"></path></svg>',
                list: '<svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>',
                check: '<svg class="w-5 h-5 inline-block mr-2" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>',
            };
            return svgs[name] || '';
        };

        this.tutorials = {
            'dashboard': [
                {
                    element: '.dashboard-section',
                    title: this.getSVG('card') + 'Sección de Cobros',
                    text: 'Bienvenido a la sección de Caja y Cobranza.\n\n' +
                          '🔸 Aquí gestiones todos los pagos\n' +
                          '🔸 Visualizas pedidos listos para cobrar\n' +
                          '🔸 Procesas cobros y propinas\n' +
                          '🔸 Registras múltiples métodos de pago',
                },
                {
                    element: '#total-sales-today',
                    title: this.getSVG('card') + 'Total de Ventas Hoy',
                    text: 'Este es el monto acumulado de todas las ventas completadas durante el día.\n\n' +
                          '✓ Se actualiza automáticamente\n' +
                          '✓ Incluye efectivo y tarjetas\n' +
                          '✓ Refleja solo pagos procesados\n' +
                          '✓ Útil para cierre de caja',
                },
                {
                    element: '#served-orders-list',
                    title: this.getSVG('send') + 'Lista de Pedidos por Cobrar',
                    text: 'Aquí aparecen todos los pedidos listos para cobrar:\n\n' +
                          '🔸 Pedidos servidos en mesas\n' +
                          '🔸 Pedidos de mostrador/bar\n' +
                          '🔸 Pedidos cargados a habitaciones\n' +
                          '→ Haz scroll para ver más pedidos',
                },
                {
                    element: '.charge-btn',
                    title: this.getSVG('card') + 'Botón Cobrar',
                    text: 'Este botón abre el modal de pago para cada pedido.\n\n' +
                          '➊ Haz click en "Cobrar"\n' +
                          '➋ Selecciona el método de pago\n' +
                          '➌ Registra la propina (opcional)\n' +
                          '➍ Confirma el pago',
                }
            ],
            'room_charges': [
                {
                    element: '.room-charges-section',
                    title: this.getSVG('home') + 'Gestión de Cargos por Habitación',
                    text: 'En esta sección administras cargos agrupados por habitaciones.\n\n' +
                          '✓ Consolidar múltiples pedidos por room\n' +
                          '✓ Generar facturas completas\n' +
                          '✓ Facilitar el cobro al checkout\n' +
                          '✓ Trazabilidad de cargos',
                },
                {
                    element: '.room-bill-tab',
                    title: this.getSVG('card') + 'Pestañas de Gestión',
                    text: 'Aquí tienes tres opciones:\n\n' +
                          '📋 Seleccionar Pedidos - Agrupar pedidos por room\n' +
                          '📄 Mis Facturas - Ver facturas generadas\n' +
                          '⏰ Historial - Registro de cargos pasados',
                },
                {
                    element: '#room-search-input',
                    title: this.getSVG('card') + 'Búsqueda Rápida',
                    text: 'Busca rápidamente pedidos por:\n\n' +
                          '🔍 Número de habitación\n' +
                          '🔍 Nombre del huésped\n' +
                          '→ Escribe para filtrar en tiempo real',
                }
            ],
            'reports': [
                {
                    element: '.reports-section',
                    title: this.getSVG('list') + 'Dashboard de Reportes',
                    text: 'Aquí accedes a análisis y estadísticas completas.\n\n' +
                          '📊 Métricas de ventas diarias\n' +
                          '📊 Desglose por método de pago\n' +
                          '📊 Comparativas y tendencias\n' +
                          '📊 Datos para auditoría',
                },
                {
                    element: '.report-tab',
                    title: this.getSVG('list') + 'Pestañas de Reportes',
                    text: 'Elige entre dos vistas principales:\n\n' +
                          '📋 Reporte de Pedidos - Detalle de cada transacción\n' +
                          '💳 Métodos de Pago - Desglose y análisis de pagos\n' +
                          '→ Filtra datos y exporta a Excel',
                },
                {
                    element: '#search-input',
                    title: this.getSVG('card') + 'Búsqueda de Pedidos',
                    text: 'Busca pedidos específicos rápidamente:\n\n' +
                          '🔍 Número de pedido\n' +
                          '🔍 Nombre del cliente\n' +
                          '🔍 Número de habitación\n' +
                          '→ Presiona "Buscar" para filtrar',
                },
                {
                    element: '#export-excel-btn',
                    title: this.getSVG('send') + 'Exportar a Excel',
                    text: 'Descarga los datos en formato Excel:\n\n' +
                          '📊 Incluye todos los filtros aplicados\n' +
                          '📊 Listo para análisis en hojas de cálculo\n' +
                          '→ Útil para auditoría y gestión',
                }
            ]
        };

        this.currentSection = 'dashboard';
        this.currentStep = 0;
        this.tutorialActive = false;
        this.actionListeners = {};
        this.completedActions = {};

        // HTML del modal
        this.modalHtml = `
            <div id="tutorial-overlay-recepcion" class="fixed inset-0 z-50 hidden"></div>
            <div id="tutorial-modal-recepcion" class="fixed bg-white rounded-xl shadow-2xl max-w-sm p-6 z-50 hidden" style="width: 360px; top: 50%; left: 50%; transform: translate(-50%, -50%); max-height: 90vh; overflow-y: auto;">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex-1">
                        <h3 id="tutorial-title-recepcion" class="text-lg font-bold text-amber-900 mb-2"></h3>
                        <p id="tutorial-text-recepcion" class="text-gray-700 text-sm mb-4 leading-relaxed"></p>
                    </div>
                    <button id="tutorial-close-recepcion" class="text-gray-400 hover:text-gray-600 ml-2 flex-shrink-0">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <div id="tutorial-progress-recepcion" class="flex gap-1 mb-4"></div>

                <div class="flex gap-2">
                    <button id="tutorial-prev-recepcion" class="flex-1 px-2 py-2 border border-amber-900 text-amber-900 rounded-lg hover:bg-amber-50 transition-colors text-xs font-medium">
                        ← Anterior
                    </button>
                    <button id="tutorial-next-recepcion" class="flex-1 px-2 py-2 bg-amber-900 text-white rounded-lg hover:bg-amber-800 transition-colors text-xs font-medium">
                        Siguiente →
                    </button>
                </div>
            </div>

            <style>
                #tutorial-overlay-recepcion {
                    background: transparent;
                    pointer-events: none;
                }
                #tutorial-overlay-recepcion.show {
                    display: block !important;
                }
                #tutorial-modal-recepcion {
                    animation: slideUp 0.3s ease-out;
                    transition: all 0.3s ease-out;
                    pointer-events: auto;
                    z-index: 9999 !important;
                    display: none !important;
                }
                #tutorial-modal-recepcion.show {
                    display: block !important;
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
                #tutorial-highlight-recepcion {
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

    init() {
        // Crear el modal HTML
        document.body.insertAdjacentHTML('beforeend', this.modalHtml);
        
        // Crear botón para iniciar tutorial
        const tutorialBtn = document.createElement('button');
        tutorialBtn.id = 'tutorial-btn-recepcion';
        tutorialBtn.className = 'fixed p-3 bg-amber-900 text-white rounded-full shadow-lg hover:bg-amber-800 transition-colors';
        tutorialBtn.style.cssText = 'bottom: 1rem; right: 1rem; z-index: 9999; padding: 0.75rem; font-size: 1rem; cursor: pointer;';
        tutorialBtn.title = 'Inicia el tutorial interactivo';
        tutorialBtn.innerHTML = `
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
        `;
        
        document.body.appendChild(tutorialBtn);

        // Event listeners
        tutorialBtn.addEventListener('click', () => this.start());
        document.getElementById('tutorial-close-recepcion').addEventListener('click', () => this.end());
        document.getElementById('tutorial-next-recepcion').addEventListener('click', () => this.nextStep());
        document.getElementById('tutorial-prev-recepcion').addEventListener('click', () => this.prevStep());
        document.getElementById('tutorial-overlay-recepcion').addEventListener('click', () => this.end());

        // Cerrar tutorial con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.tutorialActive) {
                this.end();
            }
        });
    }

    start() {
        this.tutorialActive = true;
        this.currentStep = 0;
        document.getElementById('tutorial-overlay-recepcion').classList.add('show');
        document.getElementById('tutorial-modal-recepcion').classList.add('show');
        
        console.log('Tutorial de Recepción iniciado');
        
        this.updateProgressDots();
        this.showStep();
    }

    end() {
        this.tutorialActive = false;
        document.getElementById('tutorial-overlay-recepcion').classList.remove('show');
        document.getElementById('tutorial-modal-recepcion').classList.remove('show');
        this.removeHighlight();
        // Limpiar listener de reposicionamiento
        if (this.repositionListener) {
            window.removeEventListener('scroll', this.repositionListener, true);
            window.removeEventListener('resize', this.repositionListener);
        }
    }

    nextStep() {
        const steps = this.tutorials[this.currentSection];
        if (this.currentStep < steps.length - 1) {
            this.currentStep++;
            this.showStep();
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
        const progressContainer = document.getElementById('tutorial-progress-recepcion');
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
        document.getElementById('tutorial-title-recepcion').innerHTML = step.title;
        document.getElementById('tutorial-text-recepcion').textContent = step.text;

        // Actualizar progreso
        this.updateProgressDots();

        // Mostrar/ocultar botones
        document.getElementById('tutorial-prev-recepcion').style.display = this.currentStep === 0 ? 'none' : 'block';
        const nextBtn = document.getElementById('tutorial-next-recepcion');
        if (this.currentStep === steps.length - 1) {
            nextBtn.innerHTML = this.getSVG('check') + 'Finalizar';
        } else {
            nextBtn.textContent = 'Siguiente →';
        }

        // Resaltar elemento y posicionar modal
        this.highlightElement(step.element);
        this.positionModal(step.element);
        
        // Agregar listener para reposicionar el modal cuando hay scroll o resize
        this.addRepositionListener(step.element);
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
        const modal = document.getElementById('tutorial-modal-recepcion');
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

        // Pequeño delay para permitir que el navegador renderice el elemento
        setTimeout(() => {
            const rect = element.getBoundingClientRect();
            
            // Crear highlight con borde titilante
            const highlight = document.createElement('div');
            highlight.id = 'tutorial-highlight-recepcion';
            highlight.className = 'absolute z-50 border-4 border-amber-600 rounded-lg pointer-events-none';
            
            highlight.style.top = (rect.top + window.scrollY - 8) + 'px';
            highlight.style.left = (rect.left + window.scrollX - 8) + 'px';
            highlight.style.width = (rect.width + 16) + 'px';
            highlight.style.height = (rect.height + 16) + 'px';
            
            document.body.appendChild(highlight);
        }, 50);
    }

    removeHighlight() {
        // Remover TODOS los highlights
        const highlights = document.querySelectorAll('#tutorial-highlight-recepcion');
        highlights.forEach(highlight => highlight.remove());
    }
}
