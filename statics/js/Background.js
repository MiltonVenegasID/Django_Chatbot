

const contents = document.querySelectorAll('.Contenido, .Gaviota');
const delay = 2000;

contents.forEach((content, index) => {
    setTimeout(() => {
        content.classList.add('show');
    }, (index + 1) * delay); 
});
