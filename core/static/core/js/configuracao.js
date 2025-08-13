document.addEventListener("DOMContentLoaded", function() {
    // Aplique as classes de acordo com as configurações salvas na sessão
    const body = document.body;

    // Tema
    const tema = sessionStorage.getItem('theme');
    if (tema === 'escuro') {
        body.classList.add('tema-escuro');
        body.classList.remove('tema-claro');
    } else {
        body.classList.add('tema-claro');
        body.classList.remove('tema-escuro');
    }

    // Fonte
    const fonte = sessionStorage.getItem('fonte');
    if (fonte === 'grande') {
        body.classList.add('fonte-grande');
        body.classList.remove('fonte-normal', 'fonte-extra-grande');
    } else if (fonte === 'extra_grande') {
        body.classList.add('fonte-extra-grande');
        body.classList.remove('fonte-normal', 'fonte-grande');
    } else {
        body.classList.add('fonte-normal');
        body.classList.remove('fonte-grande', 'fonte-extra-grande');
    }

    // Acessibilidade
    const acessibilidade = sessionStorage.getItem('acessibilidade');
    if (acessibilidade === 'alto_contraste') {
        body.classList.add('alto-contraste');
        body.classList.remove('leitura-facilitada');
    } else if (acessibilidade === 'leitura_facilitada') {
        body.classList.add('leitura-facilitada');
        body.classList.remove('alto-contraste');
    } else {
        body.classList.remove('alto-contraste', 'leitura-facilitada');
    }

    // Notificações
    const notificacoesSelect = document.querySelector('#notificacoes');
    if (notificacoesSelect) {
        notificacoesSelect.addEventListener('change', function() {
            sessionStorage.setItem('notificacoes', this.value);
        });

        // Inicializa a seleção com o valor armazenado
        const notificacoes = sessionStorage.getItem('notificacoes');
        if (notificacoes) {
            notificacoesSelect.value = notificacoes;
        }
    }

    // Modal de exclusão de conta
        const excluirContaBtn = document.querySelector('button[name="excluir_conta"]');
        
        // Pega o formulário principal
        const form = document.querySelector('form');

        if (excluirContaBtn && form) {
            // Adiciona um evento de clique no botão de exclusão
            excluirContaBtn.addEventListener('click', function (event) {
            // Previna a ação padrão do formulário, que é recarregar a página
            event.preventDefault();

            // Você pode adicionar uma lógica adicional aqui, como uma validação
            // ou um aviso final antes de enviar a requisição.

            // Envia o formulário com a ação de exclusão
            // Isso simula o envio do formulário, mas com o botão de exclusão.
            // O backend irá processar o `name="excluir_conta"` para saber o que fazer.
            
            const hiddenInput = document.createElement('input');
            hiddenInput.setAttribute('type', 'hidden');
            hiddenInput.setAttribute('name', 'excluir_conta');
            hiddenInput.setAttribute('value', '1');
            form.appendChild(hiddenInput);
            
            form.submit();
            });
        }
        });