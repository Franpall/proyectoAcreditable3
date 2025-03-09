const openButton = document.getElementById("open_all_ctg_button");
openButton.onclick = cambiarEstadoVisible;

const closeButton = document.getElementById("close_all_ctg_button");
closeButton.onclick = cambiarEstadoVisible;

// const header = document.getElementsByTagName('header')[0];
// let headerTop = header.offsetTop;

// window.addEventListener('scroll', () => {
//   if (window.scrollY > headerTop) {
//     ocultarMenu()
//   }
// });

function cambiarEstadoVisible(){
    const ctgWindow = document.getElementById("all_ctg_box");
    if (ctgWindow.className == "hint"){
        ctgWindow.className = "visible"
    } 
    else{
        ctgWindow.className = "hint"
    }
}

function ocultarMenu(){
  const menuUser = document.getElementById("float_menu");
  if (menuUser.className != "hint"){
    menuUser.className = "hint"
  } 
}