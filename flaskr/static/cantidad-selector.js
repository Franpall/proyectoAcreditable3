// Obtener los elementos 
const cantidadInput = document.getElementById('cantidad');
const incrementoButton = document.getElementById('incremento');
const decrementoButton = document.getElementById('decremento');

// Incrementar la cantidad 
incrementoButton.addEventListener('click', () => {
    let currentValue = parseInt(cantidadInput.value);
    cantidadInput.value = currentValue + 1;
});

// Decrementar la cantidad
decrementoButton.addEventListener('click', () => {
    let currentValue = parseInt(cantidadInput.value);
    if (currentValue > 1) { // Evitar que el valor sea menor que 1
        cantidadInput.value = currentValue - 1;
    }
});