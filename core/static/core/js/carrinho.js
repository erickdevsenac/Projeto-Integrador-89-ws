function atualizarTotal() {
      let total = 0;
      const produtos = document.querySelectorAll('.produto-item');
 
      produtos.forEach(produto => {
        const checkbox = produto.querySelector('input[type="checkbox"]');
        const quantidade = produto.querySelector('input[type="number"]').value;
        const precoTexto = produto.querySelector('span').textContent;
        const preco = parseFloat(precoTexto.replace('R$', '').replace(',', '.'));
 
        if (checkbox.checked) {
          total += preco * quantidade;
        }
      });
 
      document.getElementById('total').textContent = `Total: R$${total.toFixed(2).replace('.', ',')}`;
    }
 
    document.querySelectorAll('input[type="checkbox"], input[type="number"]').forEach(input => {
      input.addEventListener('change', atualizarTotal);
    });
 
    atualizarTotal();