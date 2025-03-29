// Area de paypal

function validarCorreoElectronico(correoElectronico) {

    correoElectronicoCorrecto = false

    if (correoElectronico.length < 5 || correoElectronico.length > 254) {
        validarFormularioP();
        return "La longitud debe estar entre 5 y 254 caracteres.";
    }

    const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{3,}$/;
    if (!regex.test(correoElectronico)) {
        validarFormularioP();
        return "Formato de correo electrónico inválido.";
    }
    correoElectronicoCorrecto = true
    validarFormularioP()
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

function validarFormularioP() {
    if (correoElectronicoCorrecto) {
      enviarFormularioButton.disabled = 0
    } else {
        enviarFormularioButton.disabled = 1
    }
  }

// Area de tarjeta de credito
function validarNumeroTarjeta(numeroTarjeta) {
    if (numeroTarjeta.length < 13 || numeroTarjeta.length > 19) {
      return "El número de tarjeta debe tener entre 13 y 19 dígitos.";
    }
  
    const regex = /^[0-9]{13,19}$/;
    if (!regex.test(numeroTarjeta)) {
      return "Formato de número de tarjeta inválido.";
    }
    numeroTarjetaCorrecto = true;
    validarFormulario();
    return "";
  }
  
  function validarCVV(cvv) {
    if (cvv.length < 3 || cvv.length > 4) {
      return "El CVV debe tener 3 o 4 dígitos.";
    }
  
    const regex = /^[0-9]{3,4}$/;
    if (!regex.test(cvv)) {
      return "Formato de CVV inválido.";
    }
    cvvCorrecto = true;
    validarFormulario();
    return "";
  }
  
  function validarFechaVencimiento(fechaVencimiento) {
    const regex = /^(0[1-9]|1[0-2])\/?([0-9]{2})$/;
    if (!regex.test(fechaVencimiento)) {
      return "Formato de fecha de vencimiento inválido (MM/AA).";
    }
  
    const [mes, año] = fechaVencimiento.split('/');
    const fechaActual = new Date();
    const mesActual = fechaActual.getMonth() + 1;
    const añoActual = fechaActual.getFullYear() % 100; // Obtener los últimos 2 dígitos del año
  
    if (año < añoActual || (año == añoActual && mes < mesActual)) {
      return "Tarjeta vencida.";
    }
  
    fechaVencimientoCorrecta = true;
    validarFormulario();
    return "";
  }
  
  var numeroTarjetaCorrecto = false;
  var cvvCorrecto = false;
  var fechaVencimientoCorrecta = false;
  
  const numeroTarjetaInput = document.getElementById("tarjeta-numero");
  const cvvInput = document.getElementById("tarjeta-cvv");
  const fechaVencimientoInput = document.getElementById("tarjeta-fecha");
  const enviarFormularioButton2 = document.getElementById("creditCardBtn");
  
  numeroTarjetaInput.addEventListener("input", () => {
    mostrarError(document.getElementById("consolaErrorCreditCard"), validarNumeroTarjeta(numeroTarjetaInput.value));
  });
  
  cvvInput.addEventListener("input", () => {
    mostrarError(document.getElementById("consolaErrorCreditCard"), validarCVV(cvvInput.value));
  });
  
  fechaVencimientoInput.addEventListener("input", () => {
    mostrarError(document.getElementById("consolaErrorCreditCard"), validarFechaVencimiento(fechaVencimientoInput.value));
  });
  
  function validarFormulario() {
    if (numeroTarjetaCorrecto && cvvCorrecto && fechaVencimientoCorrecta) {
      enviarFormularioButton2.disabled = false;
    } else {
      enviarFormularioButton2.disabled = true;
    }
  }