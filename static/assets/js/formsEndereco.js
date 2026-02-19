// formsEndereco.js

(function () {
  const chk = document.getElementById('usarEnderecoCadastro');
  const container = document.getElementById('shippingContainer');

  if (!chk || !container) return;

  // Se quiser inutilizar (recomendado): envolve o conteúdo com um fieldset
  // Você pode colocar manualmente no HTML, mas aqui criamos dinamicamente:
  let fieldset = container.querySelector('fieldset');
  if (!fieldset) {
    fieldset = document.createElement('fieldset');
    // move todos os filhos atuais do container para dentro do fieldset
    while (container.firstChild) {
      fieldset.appendChild(container.firstChild);
    }
    container.appendChild(fieldset);
  }

  function toggle() {
    const usarCadastro = chk.checked;

    // Estratégia A: desabilitar (não envia valores, não valida)
    fieldset.disabled = usarCadastro;

    // Estratégia B (opcional): esconder visualmente
    // container.classList.toggle('is-hidden', usarCadastro);

    // Sincroniza hidden (se você adicionou no template)
    const hidden = document.getElementById('usar_endereco_cadastro_hidden');
    if (hidden) hidden.value = usarCadastro ? '1' : '0';

    // Se estiver escondendo e usando validação nativa, remova/adicione required
    const requireds = fieldset.querySelectorAll('[required]');
    requireds.forEach(el => {
      if (usarCadastro) {
        el.setAttribute('data-was-required', 'true');
        el.removeAttribute('required');
      } else if (el.getAttribute('data-was-required') === 'true') {
        el.setAttribute('required', 'required');
        el.removeAttribute('data-was-required');
      }
    });
  }

  // Estado inicial (caso venha checked do server)
  toggle();
  chk.addEventListener('change', toggle);
})();
