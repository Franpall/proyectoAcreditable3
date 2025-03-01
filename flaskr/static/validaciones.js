// Valida que las contraseñas coincidan antes de enviar el formulario de registrarse.

document.getElementById('registro-form').addEventListener('submit', function(event) {
    let password = document.getElementById('password').value;
    let confirm_password = document.getElementById('confirm-password').value;
    let mensajeError = document.getElementById('mensaje-error');

    if (password !== confirm_password) {
        mensajeError.textContent = 'Las contraseñas no coinciden.';
        event.preventDefault(); // Evita el envío del formulario
    }
});