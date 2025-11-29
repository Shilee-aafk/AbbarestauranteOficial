/**
 * Menu Module - Gestiona filtros, búsqueda y categorías del menú
 */

export class MenuManager {
  constructor() {
    this.selectedCategory = 'all';
    this.searchTerm = '';
  }

  /**
   * Inicializa los listeners del menú
   */
  init() {
    this.setupCategoryFilters();
    this.setupSearch();
  }

  /**
   * Configura los listeners para los botones de filtrado de categorías
   */
  setupCategoryFilters() {
    const filterButtons = document.querySelectorAll('#category-filters .category-filter');

    filterButtons.forEach(button => {
      button.addEventListener('click', () => {
        filterButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        this.selectedCategory = button.getAttribute('data-category') || 'all';
        this.applyFilters();
      });
    });
  }

  /**
   * Configura los listeners para la búsqueda
   */
  setupSearch() {
    const searchInput = document.getElementById('menu-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchTerm = e.target.value.toLowerCase();
        this.applyFilters();
      });
    }
  }

  /**
   * Aplica los filtros de categoría y búsqueda
   */
  applyFilters() {
    const menuItems = document.querySelectorAll('.menu-item');

    menuItems.forEach(item => {
      const itemName = item.querySelector('h3').textContent.toLowerCase();
      const itemCategory = item.getAttribute('data-category');
      
      const categoryMatch = (this.selectedCategory === 'all' || itemCategory === this.selectedCategory);
      const searchMatch = itemName.includes(this.searchTerm);

      item.style.display = (categoryMatch && searchMatch) ? 'flex' : 'none';
    });
  }

  /**
   * Filtra categorías específicas de la barra
   */
  filterBarCategories(autoSelectCocktails = false) {
    const barCategories = ['cocteles', 'vinos-y-cervezas', 'bebestibles'];
    const filterButtons = document.querySelectorAll('#category-filters .category-filter');
    
    filterButtons.forEach(button => {
      const category = button.dataset.category;
      button.style.display = (barCategories.includes(category) || category === 'all') ? 'inline-flex' : 'none';
    });

    if (autoSelectCocktails) {
      const cocktailsButton = document.querySelector('.category-filter[data-category="cocteles"]');
      if (cocktailsButton) {
        cocktailsButton.click();
      }
    }
  }

  /**
   * Reinicia los filtros de categoría (restaura visibilidad de todos)
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

    this.selectedCategory = 'all';
    this.searchTerm = '';
    
    const searchInput = document.getElementById('menu-search-input');
    if (searchInput) {
      searchInput.value = '';
    }
  }

  /**
   * Obtiene la categoría actualmente seleccionada
   */
  getSelectedCategory() {
    return this.selectedCategory;
  }

  /**
   * Obtiene el término de búsqueda
   */
  getSearchTerm() {
    return this.searchTerm;
  }
}
