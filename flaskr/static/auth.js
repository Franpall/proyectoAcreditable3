function validarNombreUsuario(nombreUsuario) {
    if (nombreUsuario.length < 3 || nombreUsuario.length > 20) {
      return "La longitud debe estar entre 3 y 20 caracteres.";
    }
  
    const regex = /^[a-zA-Z0-9_]+$/;
    if (!regex.test(nombreUsuario)) {
      return "Solo letras, números y guiones bajos permitidos.";
    }
    nombreUsuarioCorrecto = true
    validarFormulario()
    return ""; 
  }
  
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
  
function validarContrasena(contrasena) {
    if (contrasena.length < 8 || contrasena.length > 100) {
      return "La longitud debe estar entre 8 y 100 caracteres.";
    }
  
    if (!/[a-z]/.test(contrasena)) {
      return "Debe contener al menos una letra minúscula.";
    }
  
    if (!/[0-9]/.test(contrasena)) {
      return "Debe contener al menos un número.";
    }
    contrasenaCorrecto = true
    validarFormulario()
    return "";
}

function validarContrasenaRepeat(contrasena, contrasenaRepeat) {
    if (contrasena != contrasenaRepeat) {
      return "La contraseña repetida no coincide";
    }
    contrasenaRepeatCorrecto = true
    validarFormulario()
    return "";
}
  
function mostrarError(elementoError, mensaje) {
    elementoError.textContent = mensaje;
}

var nombreUsuarioCorrecto = false;
var correoElectronicoCorrecto = false;
var contrasenaCorrecto = false;
var contrasenaRepeatCorrecto = false;  
const enviarFormularioButton = document.getElementById("sendButton")
const nombreUsuarioInput = document.getElementById("username");
const correoElectronicoInput = document.getElementById("email");
const contrasenaInput = document.getElementById("password");
const contrasenaRepeat = document.getElementById("confirm-password");

nombreUsuarioInput.addEventListener("input", () => {
    mostrarError(document.getElementById("nombreUsuarioError"), validarNombreUsuario(nombreUsuarioInput.value));
});
  
correoElectronicoInput.addEventListener("input", () => {
    mostrarError(document.getElementById("correoElectronicoError"), validarCorreoElectronico(correoElectronicoInput.value));
});
  
contrasenaInput.addEventListener("input", () => {
    mostrarError(document.getElementById("contrasenaError"), validarContrasena(contrasenaInput.value));
});

contrasenaRepeat.addEventListener("input", () => {
    mostrarError(document.getElementById("contrasenaRepeatError"), validarContrasenaRepeat(contrasenaInput.value, contrasenaRepeat.value));
});
  
function validarFormulario() {
    if (nombreUsuarioCorrecto && correoElectronicoCorrecto && contrasenaCorrecto && contrasenaRepeatCorrecto) {
        enviarFormularioButton.disabled = 0
    }
}