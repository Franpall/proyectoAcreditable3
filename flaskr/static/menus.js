const menuButton = document.getElementById("user_btn");
menuButton.onclick = cambiarEstadoVisible;

const header = document.getElementsByTagName('header')[0];
let headerTop = header.offsetTop;

window.addEventListener('scroll', () => {
  if (window.scrollY > headerTop) {
    ocultarMenu()
  }
});

function cambiarEstadoVisible(){
    const menuUser = document.getElementById("float_menu");
    if (menuUser.className == "hint"){
        menuUser.className = "visible"
    } 
    else{
        menuUser.className = "hint"
    }
}

function ocultarMenu(){
  const menuUser = document.getElementById("float_menu");
  if (menuUser.className != "hint"){
    menuUser.className = "hint"
  } 
}