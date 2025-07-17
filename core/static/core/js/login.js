document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('login-form');
    const usernameField = document.getElementById('id_username');
    const passwordField = document.getElementById('id_password');
    const errorMessage = document.getElementById('error-message');

    form.addEventListener('submit', function (event) {
        event.preventDefault(); 

        const username = usernameField.value.trim();
        const password = passwordField.value.trim();


        if (username !== "admin" || password !== "1234") {
            errorMessage.textContent = "Usuário ou senha incorretos!";
            errorMessage.style.display = "block";
        } else {
            errorMessage.style.display = "none";
            alert("Login realizado com sucesso!");
        }
    });
});