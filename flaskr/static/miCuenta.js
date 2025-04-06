const mostrarButton = document.getElementById("mostrarContenidoCuenta");
mostrarButton.onclick = cambiarEstadoVisible;

function cambiarEstadoVisible(){
    const contenido = document.getElementById("editarCuentaDiv");
    if (contenido.className == "hint"){
        contenido.className = "visible"
    } 
    else{
        contenido.className = "hint"
    }
}