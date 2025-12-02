console.log('📝 Sidebar init script cargado');

function initSidebar() {
    console.log('🚀 initSidebar() ejecutándose...');
    
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (!sidebar || !toggleBtn || !overlay) {
        console.error('❌ Elementos del sidebar no encontrados');
        return;
    }
    
    console.log('✅ Todos los elementos encontrados, inicializando...');
    
    // Estado del sidebar
    let isOpen = false;
    let touchStartX = null;
    let isDragging = false;
    
    // Función para abrir/cerrar
    function toggleSidebar() {
        isOpen = !isOpen;
        console.log(isOpen ? '📂 Abriendo sidebar...' : '📁 Cerrando sidebar...');
        
        if (isOpen) {
            // ABIERTO
            sidebar.classList.remove('-translate-x-full');
            sidebar.style.transform = 'translateX(0)';
            overlay.style.opacity = '0.5';
            overlay.style.visibility = 'visible';
            toggleBtn.style.pointerEvents = 'auto';
        } else {
            // CERRADO
            sidebar.classList.add('-translate-x-full');
            sidebar.style.transform = 'translateX(-100%)';
            overlay.style.opacity = '0';
            overlay.style.visibility = 'hidden';
            toggleBtn.style.pointerEvents = 'auto';
        }
        
        console.log(isOpen ? '✅ Sidebar abierto' : '✅ Sidebar cerrado');
    }
    
    // ========== CLICK EN BOTÓN HAMBURGUESA ==========
    toggleBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('🔘 Hamburguesa clickeada');
        toggleSidebar();
    });
    
    // ========== CLICK EN OVERLAY PARA CERRAR ==========
    overlay.addEventListener('click', function(e) {
        if (isOpen && e.target === overlay) {
            console.log('👆 Overlay clickeado, cerrando');
            toggleSidebar();
        }
    });
    
    // ========== PERMITIR CLICKS EN ELEMENTOS DENTRO DEL SIDEBAR ==========
    sidebar.addEventListener('click', function(e) {
        // Los clicks dentro del sidebar no cierran el sidebar
        console.log('🖱️ Click dentro del sidebar - permitido');
    });
    
    // ========== SWIPE/DRAG DETECTION ==========
    document.addEventListener('touchstart', function(e) {
        // Solo detectar si:
        // 1. El sidebar está abierto (para cerrar con swipe)
        // 2. O el toque es en el borde izquierdo < 20px (para abrir)
        const touchX = e.touches[0].clientX;
        
        if (isOpen || touchX < 20) {
            touchStartX = touchX;
            isDragging = true;
            sidebar.style.transition = 'none';
            console.log(`👆 Toque detectado en X: ${touchX}`);
        }
    }, { passive: true });
    
    document.addEventListener('touchmove', function(e) {
        if (!isDragging || touchStartX === null) return;
        
        const currentX = e.touches[0].clientX;
        const diff = touchStartX - currentX;
        const sidebarWidth = sidebar.offsetWidth;
        
        // Solo responder a movimientos hacia la IZQUIERDA (para cerrar)
        if (isOpen && diff > 0) {
            // Sidebar está abierto, usuario está deslizando hacia la izquierda
            const translateValue = Math.max(-sidebarWidth, -diff);
            sidebar.style.transform = `translateX(${translateValue}px)`;
            overlay.style.opacity = Math.max(0, 0.5 - (diff / sidebarWidth * 0.5));
        } else if (!isOpen && touchStartX < 20 && diff < 0) {
            // Sidebar está cerrado, usuario está deslizando desde borde izquierdo hacia la derecha
            const distanceFromEdge = Math.abs(diff);
            const translateValue = Math.min(0, -sidebarWidth + distanceFromEdge);
            sidebar.style.transform = `translateX(${translateValue}px)`;
            overlay.style.opacity = Math.min(0.5, (distanceFromEdge / sidebarWidth * 0.5));
        }
    }, { passive: true });
    
    document.addEventListener('touchend', function(e) {
        if (!isDragging || touchStartX === null) {
            isDragging = false;
            touchStartX = null;
            return;
        }
        
        const touchEndX = e.changedTouches[0].clientX;
        const diff = touchStartX - touchEndX;
        isDragging = false;
        
        // Restaurar transición
        sidebar.style.transition = 'transform 0.3s ease-in-out';
        
        // CERRAR: swipe hacia izquierda > 50px
        if (isOpen && diff > 50) {
            console.log('🎯 Swipe izquierda detectado, cerrando');
            isOpen = true; // Toggle lo cambiará a false
            toggleSidebar();
        }
        // ABRIR: swipe desde borde izquierdo hacia derecha > 50px
        else if (!isOpen && touchStartX < 20 && (touchEndX - touchStartX) > 50) {
            console.log('🎯 Swipe derecha desde borde detectado, abriendo');
            isOpen = false; // Toggle lo cambiará a true
            toggleSidebar();
        }
        // REVERTIR: swipe no fue suficiente, volver a posición anterior
        else {
            sidebar.style.transition = 'transform 0.3s ease-in-out';
            if (isOpen) {
                sidebar.style.transform = 'translateX(0)';
                overlay.style.opacity = '0.5';
            } else {
                sidebar.style.transform = 'translateX(-100%)';
                overlay.style.opacity = '0';
            }
            console.log('↩️ Swipe insuficiente, revertiendo');
        }
        
        touchStartX = null;
    }, { passive: true });
    
    console.log('✅ Sidebar inicializado correctamente');
}

// Ejecutar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSidebar);
} else {
    initSidebar();
}

