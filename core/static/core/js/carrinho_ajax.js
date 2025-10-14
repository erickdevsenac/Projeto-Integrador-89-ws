document.addEventListener('DOMContentLoaded', function () {
    const cartTable = document.querySelector('.table tbody');
    const cartTotalEl = document.getElementById('cart-total');
    const cartItemCountEl = document.getElementById('cart-item-count'); // Isso pode ser null
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const alertsContainer = document.getElementById('cart-alerts-container');

    let debounceTimeout;

    if (!cartTable) return;

    cartTable.addEventListener('input', function(e) {
        if (e.target.classList.contains('quantity-input')) {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                updateQuantity(e.target);
            }, 500);
        }
    });

    cartTable.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-item-btn')) {
            e.preventDefault();
            removeItem(e.target);
        }
    });

    function showAlert(message, type = 'danger') {
        if (!alertsContainer) return;
        const wrapper = document.createElement('div');
        wrapper.innerHTML = [
            `<div class="alert alert-${type} alert-dismissible fade show" role="alert">`,
            `   <div>${message}</div>`,
            '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
            '</div>'
        ].join('');
        alertsContainer.append(wrapper);
    }

    function updateQuantity(inputElement) {
        const itemKey = inputElement.dataset.itemKey;
        const quantidade = parseInt(inputElement.value, 10);
        const row = inputElement.closest('tr');

        row.classList.add('updating');

        fetch(`/carrinho/atualizar/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify({ item_key: itemKey, quantidade: quantidade })
        })
        .then(response => {
            if (!response.ok) { return response.json().then(err => { throw new Error(err.message || 'Erro do servidor'); }); }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const subtotalEl = document.getElementById(`subtotal-${itemKey}`);
                if (data.removed) {
                    row.classList.add('removing');
                    setTimeout(() => {
                        row.remove();
                        if (data.total_itens === 0) { window.location.reload(); }
                    }, 400);
                } else {
                    subtotalEl.textContent = data.subtotal;
                    subtotalEl.classList.add('flash-success');
                    cartTotalEl.classList.add('flash-success');
                    setTimeout(() => {
                        subtotalEl.classList.remove('flash-success');
                        cartTotalEl.classList.remove('flash-success');
                    }, 700);
                }
                
                cartTotalEl.textContent = data.total_carrinho;

                if (cartItemCountEl) {
                    cartItemCountEl.textContent = data.total_itens;
                }
            }
        })
        .catch(error => { showAlert(error.message); })
        .finally(() => { row.classList.remove('updating'); });
    }

    function removeItem(buttonElement) {
        const itemKey = buttonElement.dataset.itemKey;
        const row = buttonElement.closest('tr');

         fetch(`/carrinho/remover/`, {
             method: 'POST',
             headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
             body: JSON.stringify({ item_key: itemKey })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                row.classList.add('removing');
                setTimeout(() => {
                    row.remove();
                    if (data.total_itens === 0) { window.location.reload(); }
                }, 400);

                cartTotalEl.textContent = data.total_carrinho;

                // CORREÇÃO PRINCIPAL: Verificar se o elemento existe antes de usá-lo
                if (cartItemCountEl) {
                    cartItemCountEl.textContent = data.total_itens;
                }
            } else {
                showAlert(data.message, 'danger');
            }
        });
    }
});