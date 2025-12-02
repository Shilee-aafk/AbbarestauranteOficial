console.log('📝 Sidebar init script cargado');

function initSidebar() {
    console.log('🚀 initSidebar() ejecutándose...');
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (!sidebar || !sidebarToggle || !sidebarOverlay) {
        console.error('❌ Elementos del sidebar no encontrados');
        console.error('sidebar:', sidebar);
        console.error('sidebarToggle:', sidebarToggle);
        console.error('sidebarOverlay:', sidebarOverlay);
        return;
    }
    
    console.log('✅ Sidebar elements found, initializing...');
    
    const toggleSidebar = () => {
        console.log('🔄 Toggle sidebar clicked');
        sidebar.classList.toggle('-translate-x-full');
        const isClosed = sidebar.classList.contains('-translate-x-full');
        
        // Aplicar transform inline como respaldo
        if (isClosed) {
            sidebar.style.transform = 'translateX(-100%)';
            console.log('Aplicando transform: translateX(-100%)');
        } else {
            sidebar.style.transform = 'translateX(0)';
            console.log('Aplicando transform: translateX(0)');
        }
        
        sidebarOverlay.style.opacity = isClosed ? '0' : '1';
        sidebarOverlay.style.pointerEvents = isClosed ? 'none' : 'auto';
        sidebarToggle.style.pointerEvents = 'auto';
        
        console.log(isClosed ? '✅ Sidebar cerrado' : '✅ Sidebar abierto');
    };
    
    // Botón hamburguesa
    console.log('🔔 Registrando listener para el botón hamburguesa...');
    sidebarToggle.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('🔘 Hamburguesa clickeada!');
        toggleSidebar();
    });
    console.log('✅ Click listener agregado al botón hamburguesa');
    
    // Overlay para cerrar
    sidebarOverlay.addEventListener('click', toggleSidebar);
    
    // Swipe para cerrar/abrir el sidebar - SIGUE EL DEDO
    let touchStart = null;
    let isDragging = false;
    
    document.addEventListener('touchstart', (e) => {
        const sidebarWidth = sidebar.offsetWidth;
        const isClosed = sidebar.classList.contains('-translate-x-full');
        const isOpeningSide = e.changedTouches[0].clientX < 20;
        
        if (!isClosed || isOpeningSide) {
            touchStart = e.changedTouches[0].clientX;
            isDragging = true;
            sidebar.style.transition = 'none';
        }
    }, false);
    
    document.addEventListener('touchmove', (e) => {
        if (!isDragging || !touchStart) return;
        
        const sidebarWidth = sidebar.offsetWidth;
        const currentX = e.changedTouches[0].clientX;
        const diff = touchStart - currentX;
        const isClosed = sidebar.classList.contains('-translate-x-full');
        
        if (!isClosed) {
            const newTranslate = Math.max(-sidebarWidth, -diff);
            sidebar.style.transform = `translateX(${newTranslate}px)`;
        } else if (touchStart < 20) {
            const newTranslate = Math.min(0, currentX - touchStart - sidebarWidth);
            sidebar.style.transform = `translateX(${newTranslate}px)`;
        }
    }, false);
    
    document.addEventListener('touchend', (e) => {
        if (!isDragging || !touchStart) {
            isDragging = false;
            touchStart = null;
            return;
        }
        
        const touchEnd = e.changedTouches[0].clientX;
        const diff = touchStart - touchEnd;
        isDragging = false;
        
        sidebar.style.transition = 'transform 0.3s ease-in-out';
        
        const isClosed = sidebar.classList.contains('-translate-x-full');
        
        if (!isClosed && diff > 50) {
            console.log('👆 Swipe hacia izquierda detectado, cerrando sidebar');
            sidebar.classList.add('-translate-x-full');
            sidebar.style.transform = 'translateX(-100%)';
            sidebarOverlay.style.opacity = '0';
            sidebarOverlay.style.pointerEvents = 'none';
        }
        else if (isClosed && touchStart < 20 && (touchEnd - touchStart) > 50) {
            console.log('👆 Swipe desde borde izquierdo detectado, abriendo sidebar');
            sidebar.classList.remove('-translate-x-full');
            sidebar.style.transform = 'translateX(0)';
            sidebarOverlay.style.opacity = '1';
            sidebarOverlay.style.pointerEvents = 'auto';
        }
        else {
            sidebar.style.transform = isClosed ? 'translateX(-100%)' : 'translateX(0)';
        }
        
        touchStart = null;
    }, false);
}

// Ejecutar apenas el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSidebar);
} else {
    initSidebar();
}
