document.addEventListener('DOMContentLoaded', function() {
  const tipoSelect = document.getElementById('id_tipo');
  const camposParceiro = document.getElementById('campos-parceiro');
  const camposCliente = document.getElementById('campos-cliente');
  const labelNome = document.querySelector('label[for="id_nome_negocio"]');

  function toggleCampos() {
    const tipo = tipoSelect.value;
    
    if (tipo === 'VENDEDOR' || tipo === 'ONG') {
      camposParceiro.classList.remove('d-none');
      camposCliente.classList.add('d-none');
      if(labelNome) labelNome.textContent = 'Nome do Negócio/ONG';
    } else if (tipo === 'CLIENTE') {
      camposParceiro.classList.add('d-none');
      camposCliente.classList.remove('d-none');
      if(labelNome) labelNome.textContent = 'Nome Completo';
    } else {
      camposParceiro.classList.add('d-none');
      camposCliente.classList.add('d-none');
    }
  }

  tipoSelect.addEventListener('change', toggleCampos);
  toggleCampos(); // Executa ao carregar a página
});