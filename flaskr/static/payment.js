function validarCorreoElectronico(correoElectronico) {
    if (correoElectronico.length < 5 || correoElectronico.length > 254) {
        return "La longitud debe estar entre 5 y 254 caracteres.";
    }

    const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!regex.test(correoElectronico)) {
        return "Formato de correo electrónico inválido.";
    }
    correoElectronicoCorrecto = true
    validarFormulario()
    return "";
}

function mostrarError(elementoError, mensaje) {
    elementoError.textContent = mensaje;
}

var correoElectronicoCorrecto = false
const correoElectronicoInput = document.getElementById("paypal-email");
const enviarFormularioButton = document.getElementById("paypalPayBtn")

correoElectronicoInput.addEventListener("input", () => {
    mostrarError(document.getElementById("correoElectronicoError"), validarCorreoElectronico(correoElectronicoInput.value));
});

function validarFormulario() {
    if (correoElectronicoCorrecto) {
        enviarFormularioButton.disabled = 0
    }
}