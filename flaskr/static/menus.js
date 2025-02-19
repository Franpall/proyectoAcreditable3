const menuButton = document.getElementById("user_btn");
menuButton.onclick = cambiarEstadoVisible;

function cambiarEstadoVisible(){
    const menuUser = document.getElementById("float_menu");
    if (menuUser.className == "hint"){
        menuUser.className = "visible"
    } 
    else{
        menuUser.className = "hint"
    }
}