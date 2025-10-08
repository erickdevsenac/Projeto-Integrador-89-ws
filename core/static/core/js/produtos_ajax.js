document.addEventListener('DOMContentLoaded', function () {
    const filtersForm = document.querySelector('#filters-form');
    const productListContainer = document.getElementById('product-list-container');
    let fetchTimeout;

    if (filtersForm && productListContainer) {
    // Função para buscar produtos com os filtros atuais
    function fetchProducts(url) {
       productListContainer.classList.add('loading');
            fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                productListContainer.innerHTML = data.html;
                window.history.pushState({}, '', url);
            })
            .catch(error => console.error('Erro ao buscar produtos:', error))
            .finally(() => {
                productListContainer.classList.remove('loading');
            });
        }
    function applyFilters() {
            const formData = new FormData(filtersForm);
            for (let [key, value] of [...formData.entries()]) {
                if (value === '') formData.delete(key);
            }
            const params = new URLSearchParams(formData).toString();
            const url = `${filtersForm.action}?${params}`;
            fetchProducts(url);
        }
        
        filtersForm.addEventListener('submit', function (e) {
            e.preventDefault();
            applyFilters();
        });

        filtersForm.addEventListener('input', function (e) {
            if (e.target.type === 'text' || e.target.type === 'number') {
                clearTimeout(fetchTimeout);
                fetchTimeout = setTimeout(applyFilters, 500);
            } else {
                applyFilters();
            }
        });

        productListContainer.addEventListener('click', function(e) {
            if (e.target.closest('.pagination a')) {
                e.preventDefault();
                const url = e.target.closest('a').href;
                fetchProducts(url);
            }
        });
    }

    // --- NOVA LÓGICA PARA ABRIR/FECHAR SIDEBAR DE FILTROS NO MOBILE ---
    const toggleButton = document.getElementById('toggle-filters');
    const closeButton = document.getElementById('close-filters-btn');
    const sidebar = document.getElementById('filters-sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    if (toggleButton && sidebar && closeButton && overlay) {
        function openSidebar() {
            sidebar.classList.add('open');
            overlay.classList.add('active');
        }

        function closeSidebar() {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        }

        toggleButton.addEventListener('click', openSidebar);
        closeButton.addEventListener('click', closeSidebar);
        overlay.addEventListener('click', closeSidebar);
    }
});


// Função de Quick View (pode ficar fora do DOMContentLoaded)
function quickView(produtoId) {
    const modalContent = document.getElementById('quickViewContent');
    const modal = new bootstrap.Modal(document.getElementById('quickViewModal'));

    modalContent.innerHTML = '<div class="text-center p-5"><div class="spinner-border text-success" role="status"><span class="visually-hidden">Loading...</span></div></div>';
    modal.show();

    fetch(`/produto/${produtoId}/quick-view/`)
        .then(response => response.json())
        .then(data => {
            modalContent.innerHTML = data.html;
        })
        .catch(error => {
            console.error('Erro no Quick View:', error);
            modalContent.innerHTML = '<p class="text-danger">Não foi possível carregar os detalhes do produto.</p>';
        });
}