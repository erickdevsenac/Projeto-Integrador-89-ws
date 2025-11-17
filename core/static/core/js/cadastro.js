document.addEventListener('DOMContentLoaded', function() {
  
  // Lógica para alternar campos com base no tipo de usuário
  const tipoSelect = document.getElementById('id_tipo');
  const camposParceiro = document.getElementById('campos-parceiro'); // Presumindo que você tem esses divs no HTML
  const camposCliente = document.getElementById('campos-cliente');   // Presumindo que você tem esses divs no HTML

  function toggleCampos() {
    if (!tipoSelect) return;
    
    const tipo = tipoSelect.value;
    
    if (camposParceiro) camposParceiro.classList.add('d-none');
    if (camposCliente) camposCliente.classList.add('d-none');
    
    if (tipo === 'VENDEDOR' || tipo === 'ONG') {
      if (camposParceiro) camposParceiro.classList.remove('d-none');
    } else if (tipo === 'CLIENTE') {
      if (camposCliente) camposCliente.classList.remove('d-none');
    }
  }

  if (tipoSelect) {
    tipoSelect.addEventListener('change', toggleCampos);
    toggleCampos();
  }

  // --- VALIDAÇÃO DE SENHA ---
  const passwordInput = document.getElementById('id_senha');
  const confirmPasswordInput = document.getElementById('id_confirmar_senha');
  const confirmPasswordFeedback = document.getElementById('confirm-password-feedback');

  // Feedback de força da senha
  const lengthCheck = document.getElementById('length-check');
  const caseCheck = document.getElementById('case-check');
  const numCheck = document.getElementById('num-check');

  if (passwordInput) {
    passwordInput.addEventListener('input', function() {
      const value = this.value;
      
      // Verifica se os elementos de feedback de força existem antes de tentar manipulá-los
      if (lengthCheck) value.length >= 6 ? lengthCheck.classList.add('valid') : lengthCheck.classList.remove('valid');
      if (caseCheck) (/[A-Z]/.test(value) && /[a-z]/.test(value)) ? caseCheck.classList.add('valid') : caseCheck.classList.remove('valid');
      if (numCheck) /\d/.test(value) ? numCheck.classList.add('valid') : numCheck.classList.remove('valid');
    });
  }

  // Validação da confirmação de senha
  function validatePasswordConfirmation() {
    // Só executa se todos os elementos necessários existirem
    if (!passwordInput || !confirmPasswordInput || !confirmPasswordFeedback) {
      return;
    }

    const passwordValue = passwordInput.value;
    const confirmPasswordValue = confirmPasswordInput.value;

    if (confirmPasswordValue === "") {
        confirmPasswordFeedback.textContent = "";
        confirmPasswordFeedback.style.color = ''; // Limpa a cor
        return;
    }

    if (passwordValue === confirmPasswordValue) {
        confirmPasswordFeedback.textContent = "As senhas coincidem!";
        confirmPasswordFeedback.style.color = 'green';
    } else {
        confirmPasswordFeedback.textContent = "As senhas não coincidem.";
        confirmPasswordFeedback.style.color = 'red';
    }
  }

  if (passwordInput && confirmPasswordInput) {
      passwordInput.addEventListener('input', validatePasswordConfirmation);
      confirmPasswordInput.addEventListener('input', validatePasswordConfirmation);
  }

  // --- NOVA LÓGICA: ALTERNAR VISIBILIDADE DA SENHA (ÍCONE DE OLHO) ---
  const passwordToggles = document.querySelectorAll('.password-toggle');

  passwordToggles.forEach(toggle => {
    toggle.addEventListener('click', function() {
      const targetId = this.dataset.target;
      const targetInput = document.getElementById(targetId);

      if (targetInput) {
        if (targetInput.type === 'password') {
          targetInput.type = 'text';
          // this.innerHTML = '&#128064;'; // Ícone de olho aberto
          // this.classList.add('hidden'); // Se estiver usando Font Awesome
        } else {
          targetInput.type = 'password';
          this.innerHTML = '&#128065;'; // Ícone de olho fechado (ou original)
          // this.classList.remove('hidden'); // Se estiver usando Font Awesome
        }
      }
    });
  });

  const cepInput = document.getElementById("id_cep");
  const getCepButton = document.getElementById("getCep");
  const enderecoInput = document.getElementById("id_endereco");
  const cidadeInput = document.getElementById("id_cidade");
  const estadoInput = document.getElementById("id_estado");

  if(getCepButton && cepInput){
    getCep.addEventListener("click", () => {
      const cepValue = cepInput.value;
      if (cepValue) {
        viaCep(cepValue);
      }
    }) 
  }

  if (cepInput) {
    cepInput.addEventListener("blur", () => {
        const cepValue = cepInput.value.replace(/\D/g, '');
        if (cepValue.length === 8) {
            viaCep(cepValue);
        }
    });
  }
  
 async function viaCep(cep) {
    const cepLimpo = cep.replace(/\D/g, '');

    if (!enderecoInput || !cidadeInput || !estadoInput) {
        console.error("Campos de endereço (endereco, cidade, estado) não encontrados no DOM.");
        return;
    }

    try {
      let dados = await fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`);
      let dadosjson = await dados.json();

      if (dadosjson.erro) {
        alert("CEP não encontrado. Verifique o valor digitado.");
        enderecoInput.value = "";
        cidadeInput.value = "";
        estadoInput.value = "";
      } else {
        enderecoInput.value = dadosjson.logradouro;
        cidadeInput.value = dadosjson.localidade;
        estadoInput.value = dadosjson.uf;
        
        enderecoInput.focus();
      }
    } catch (error) {
      console.error("Erro ao buscar CEP:", error);
      alert("Não foi possível buscar o CEP. Tente novamente.");
    }
  }

});