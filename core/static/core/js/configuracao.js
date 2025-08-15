document.addEventListener("DOMContentLoaded", function() {
    // Pega o formulário principal da página
    const form = document.querySelector('form');
    
    // Pega o botão de exclusão que está DENTRO do modal de confirmação
    const botaoConfirmarExclusao = document.querySelector('.modal-footer .btn-danger');

    // Se o botão de confirmação e o formulário existirem na página,
    // adiciona um "escutador" de eventos de clique.
    if (botaoConfirmarExclusao && form) {
        botaoConfirmarExclusao.addEventListener('click', function(event) {
            // Cria um campo de formulário invisível
            const hiddenInput = document.createElement('input');
            hiddenInput.setAttribute('type', 'hidden');
            hiddenInput.setAttribute('name', 'excluir_conta');
            hiddenInput.setAttribute('value', '1');
            
            // Adiciona este campo ao formulário para que o Django o reconheça
            form.appendChild(hiddenInput);

            // Envia o formulário completo para a sua view no Django
            form.submit();
        });
    }
});