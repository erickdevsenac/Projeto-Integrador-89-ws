document.addEventListener('DOMContentLoaded', function () {
    const cartTable = document.querySelector('.table tbody');
    const cartTotalEl = document.getElementById('cart-total');
    const cartItemCountEl = document.getElementById('cart-item-count');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;


    let debounceTimeout;

    cartTable.addEventListener('input', function(e) {
        if (e.target.classList.contains('quantity-input')) {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                updateQuantity(e.target);
            }, 500); // Espera 500ms após o usuário parar de digitar
        }
    });

    cartTable.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-item-btn')) {
            removeItem(e.target);
        }
    });

    function updateQuantity(inputElement) {
        const produtoId = inputElement.dataset.produtoId;
        const quantidade = parseInt(inputElement.value, 10);

        fetch(`/carrinho/atualizar/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ produto_id: produtoId, quantidade: quantidade })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.removed) {
                    document.querySelector(`tr[data-produto-id='${produtoId}']`).remove();
                } else {
                    document.getElementById(`subtotal-${produtoId}`).textContent = data.subtotal;
                }
                cartTotalEl.textContent = data.total_carrinho;
                cartItemCountEl.textContent = data.total_itens;
            } else {
                alert(data.message); 
            }
        });
    }

    function removeItem(buttonElement) {
        console.log('excluir')

        const produtoId = buttonElement.dataset.produtoId;

        fetch(`/carrinho/remover/${produtoId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector(`tr[data-produto-id='${produtoId}']`).remove();
                cartTotalEl.textContent = data.total_carrinho;
                cartItemCountEl.textContent = data.total_itens;

                // Se o carrinho ficar vazio, mostrar mensagem
                if (data.total_itens === 0) {
                }
            } else {
                alert(data.message);
            }
        });
    }
});