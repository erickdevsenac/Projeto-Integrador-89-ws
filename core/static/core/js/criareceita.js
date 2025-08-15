document.addEventListener('DOMContentLoaded', function() {
    function setupFormset(prefix) {
        const addButton = document.getElementById(`add-${prefix}`);
        const formList = document.getElementById(`${prefix}-form-list`);
        const emptyFormTemplate = document.getElementById(`empty-${prefix}-form`).innerHTML;
        const totalFormsInput = document.querySelector(`#id_${prefix}-TOTAL_FORMS`);

        // Adiciona uma verificação para garantir que os elementos foram encontrados
        if (!addButton || !formList || !emptyFormTemplate || !totalFormsInput) {
            console.error(`Erro ao configurar o formset para o prefixo: '${prefix}'. Um ou mais elementos não foram encontrados.`);
            return;
        }

        addButton.addEventListener('click', function() {
            let formNum = parseInt(totalFormsInput.value);
            let newForm = emptyFormTemplate.replace(/__prefix__/g, formNum);
            
            let formElement = document.createElement('div');
            formElement.innerHTML = newForm;
            
            formList.appendChild(formElement);
            
            totalFormsInput.value = formNum + 1;
        });
    }

    // AJUSTE: Chamadas da função agora usam o plural
    setupFormset('ingredientes');
    setupFormset('etapas');
});