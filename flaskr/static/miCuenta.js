const mostrarButton = document.getElementById("mostrarContenidoCuenta");
mostrarButton.onclick = cambiarEstadoVisible;

function cambiarEstadoVisible(){
    const contenido = document.getElementById("editarCuentaDiv");
    if (contenido.classList.contains("hint")){
        contenido.classList.remove("hint");
    } 
    else{
        contenido.classList.add("hint");
    }
}