function mostrarMensagem(card, nomeProduto) {
    document.querySelectorAll('.card').forEach(c => c.classList.remove('selecionado'));
    card.classList.add('selecionado');

    const msg = document.getElementById('mensagem-produto');
    msg.textContent = `Você selecionou: ${nomeProduto}`;
}