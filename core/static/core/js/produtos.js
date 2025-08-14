document.addEventListener('DOMContentLoaded', function() {
    const quantidadeInputs = document.querySelectorAll('input[name="quantidade"]');

    quantidadeInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            if (input.value < 1) {
                input.value = 1;
            }
        });
    });
});