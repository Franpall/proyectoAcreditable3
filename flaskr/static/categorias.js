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

// Animación para la sección de categorías
document.addEventListener('DOMContentLoaded', function() {
  // Configuración del Intersection Observer
    const observerOptions = {
      threshold: 0.10 // Se activa cuando el 10% del elemento es visible
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Animación para la versión mobile
                if (window.innerWidth <= 695) {
                    const categorias = entry.target.querySelectorAll('.categoria');
                    categorias.forEach((categoria, index) => {
                        // Delays diferentes a cada categoría
                        categoria.style.transitionDelay = `${0.1 + (index * 0.2)}s`;
                        categoria.style.opacity = '1';
                        categoria.style.transform = 'translateX(0)';
                    });
                } else {
                    // Animación para la versión desktop
                    entry.target.classList.add('visible');
                }
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observa el elemento de categorías
    const categoriasSection = document.querySelector('#categorias');
    if (categoriasSection) {
        observer.observe(categoriasSection);
        }
    });