function initSidebar() {
    // Evitar que se ejecute dos veces
    if (window.__sidebarInitialized) {
        return;
    }
    window.__sidebarInitialized = true;
    
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    
    console.log('🔍 Sidebar init check:', {
        sidebar: !!sidebar,
        toggleBtn: !!toggleBtn
    });
    
    if (!sidebar || !toggleBtn) {
        console.error('❌ Elementos del sidebar no encontrados', {
            sidebar: !!sidebar,
            toggleBtn: !!toggleBtn
        });
        return;
    }
    
    // Estado del sidebar
    let isOpen = false;
    let touchStartX = 0;
    let touchStartY = 0;
    
    // Función para abrir/cerrar
    function toggleSidebar() {
        isOpen = !isOpen;
        console.log('🔄 Toggle sidebar, isOpen:', isOpen);
        
        if (isOpen) {
            // ABIERTO
            sidebar.classList.remove('-translate-x-full');
            sidebar.style.transform = 'translateX(0)';
            toggleBtn.style.pointerEvents = 'auto';
            
            // Crear overlay para cerrar al hacer click fuera
            if (!document.getElementById('sidebar-overlay')) {
                const overlay = document.createElement('div');
                overlay.id = 'sidebar-overlay';
                overlay.className = 'fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden';
                document.body.appendChild(overlay);
                
                overlay.addEventListener('click', function() {
                    console.log('✋ Cerrando por click en overlay');
                    toggleSidebar();
                });
            } else {
                document.getElementById('sidebar-overlay').style.display = 'block';
            }
            
            console.log('✅ Sidebar abierto');
        } else {
            // CERRADO
            sidebar.classList.add('-translate-x-full');
            sidebar.style.transform = 'translateX(-100%)';
            toggleBtn.style.pointerEvents = 'auto';
            
            // Ocultar overlay
            const overlay = document.getElementById('sidebar-overlay');
            if (overlay) {
                overlay.style.display = 'none';
            }
            
            console.log('✅ Sidebar cerrado');
        }
    }
    
    // ========== CLICK EN BOTÓN HAMBURGUESA ==========
    toggleBtn.addEventListener('click', function(e) {
        console.log('🔘 Click en hamburguesa');
        e.preventDefault();
        e.stopPropagation();
        toggleSidebar();
    });
    
    // ========== CLICK EN ITEMS DEL SIDEBAR PARA CERRAR ==========
    const navLinks = sidebar.querySelectorAll('nav a');
    console.log('📍 Encontrados', navLinks.length, 'enlaces en el sidebar');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            console.log('🔗 Click en enlace del sidebar, isOpen:', isOpen);
            // Cerrar el sidebar cuando se haga click en cualquier enlace del menú
            if (isOpen) {
                console.log('✋ Cerrando por click en enlace');
                toggleSidebar();
            }
        });
    });
    
    // ========== SWIPE HACIA LA IZQUIERDA PARA CERRAR ==========
    sidebar.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].clientX;
        touchStartY = e.changedTouches[0].clientY;
    }, false);
    
    sidebar.addEventListener('touchend', function(e) {
        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;
        
        // Calcular diferencia
        const diffX = touchStartX - touchEndX;
        const diffY = touchStartY - touchEndY;
        
        // Swipe hacia la izquierda (más de 50px horizontalmente y menos movimiento vertical)
        if (diffX > 50 && Math.abs(diffY) < 50 && isOpen) {
            console.log('👈 Swipe izquierda detectado');
            toggleSidebar();
        }
    }, false);
}

// Ejecutar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSidebar);
} else {
    // El DOM ya está listo (el script se cargó tarde)
    initSidebar();
}

// Ejecutar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSidebar);
} else {
    initSidebar();
}

