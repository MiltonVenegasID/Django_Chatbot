function DisplayAddForm() {
    document.getElementById('formRegister').style.display = 'block';
    document.getElementById('formEdit').style.display = 'none';
}

function DisplayEditForm() {
    document.getElementById('formRegister').style.display = 'none';
    document.getElementById('formEdit').style.display = 'block';
}

document.querySelector('#ListaCuentasEspejo').addEventListener('click', function(event){
    const element = event.target;

    const ActiveForm = element.nextElementSibling;
    if(ActiveForm && ActiveForm.classList.contains('form-container')) {
        ActiveForm.classList.remove('show');
        setTimeout(() => ActiveForm.remove(), 300);
        return;
    } 
    
    const prevForm = document.querySelector('.form-container');
    if(prevForm){
        prevForm.classList.remove('show');
        setTimeout(() => prevForm.remove(), 300);
    }

    const  formContainer = document.createElement('div');
    formContainer.classList.add('form-container');
    formContainer.innerHTML = `
        <h3>Cuenta Espejo</h3>
    `

    element.insertAdjacentElement('afterend', formContainer);

    setTimeout(() =>{
        formContainer.classList.add('show');
    })
})