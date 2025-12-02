function initSidebar() {
    // Evitar que se ejecute dos veces
    if (window.__sidebarInitialized) {
        return;
    }
    window.__sidebarInitialized = true;
    
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const overlay = document.getElementById('sidebar-overlay');
    
    console.log('🔍 Sidebar init check:', {
        sidebar: !!sidebar,
        toggleBtn: !!toggleBtn,
        overlay: !!overlay
    });
    
    if (!sidebar || !toggleBtn || !overlay) {
        console.error('❌ Elementos del sidebar no encontrados', {
            sidebar: !!sidebar,
            toggleBtn: !!toggleBtn,
            overlay: !!overlay
        });
        return;
    }
    
    // Estado del sidebar
    let isOpen = false;
    
    // Función para abrir/cerrar
    function toggleSidebar() {
        isOpen = !isOpen;
        console.log('🔄 Toggle sidebar, isOpen:', isOpen);
        
        if (isOpen) {
            // ABIERTO
            sidebar.classList.remove('-translate-x-full');
            sidebar.style.transform = 'translateX(0)';
            overlay.style.opacity = '0.5';
            overlay.style.pointerEvents = 'auto';
            toggleBtn.style.pointerEvents = 'auto';
            console.log('✅ Sidebar abierto');
        } else {
            // CERRADO
            sidebar.classList.add('-translate-x-full');
            sidebar.style.transform = 'translateX(-100%)';
            overlay.style.opacity = '0';
            overlay.style.pointerEvents = 'none';
            toggleBtn.style.pointerEvents = 'auto';
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
    
    // ========== CLICK EN OVERLAY PARA CERRAR ==========
    overlay.addEventListener('click', function(e) {
        console.log('🖱️ Click en overlay, isOpen:', isOpen);
        if (isOpen && e.target === overlay) {
            console.log('✋ Cerrando por click en overlay');
            toggleSidebar();
        }
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

