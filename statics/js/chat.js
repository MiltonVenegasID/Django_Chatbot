function mostrarFormulario(event, elemento) {
    const liElement = event.target;

    const formularioExistente = liElement.nextElementSibling;
    if (formularioExistente && formularioExistente.classList.contains('form-container')) {
        formularioExistente.classList.remove('show');
        setTimeout(() => formularioExistente.remove(), 300); 
    }

    const formularioAnterior = document.querySelector('.form-container');
    if (formularioAnterior) {
        formularioAnterior.classList.remove('show');
        setTimeout(() => formularioAnterior.remove(), 300);
    }

    const formContainer = document.createElement('div');
    formContainer.classList.add('form-container');

    formContainer.innerHTML = `
        <h3>Actualizar Información</h3>
        e
    `;

    liElement.insertAdjacentElement('afterend', formContainer);

    setTimeout(() => {
        formContainer.classList.add('show');
    }, 10); 
}

function actualizar(elemento) {
    const nuevoNombre = document.getElementById('item-name').value;
    alert('Elemento "' + elemento + '" actualizado a: ' + nuevoNombre);
}

function eliminar(elemento) {
    if (confirm('¿Estás seguro de que deseas eliminar el elemento "' + elemento + '"?')) {
        alert('Elemento "' + elemento + '" eliminado');
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function initializeDynamicElements(parentElement) {
    const buttons = parentElement.querySelectorAll('.select-adapter');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const selectedValue = button.getAttribute('data-value');
            sendMessage(selectedValue);
        });
    });
}

function initializeDynamicElements(container) {
    const forms = container.getElementsByTagName('form');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            if (form.id === 'mirrorAccountForm') {
                SendMirrorAccount(form);
            }
        });
    });

    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    var selected = new Array();

    Array.from(checkboxes).forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            for (var i = 0; i < checkboxes.length; i++) {
                if (checkboxes[i].checked) {
                    selected.push(checkboxes[i].value)
                }
            }
        });
    });

    const buttons = container.getElementsByTagName('button');
    Array.from(buttons).forEach(button => {
        button.addEventListener('click', (e) => {
            if (button.getAttribute('onclick')) {
                const functionName = button.getAttribute('onclick').replace('()', '');
                if (typeof window[functionName] === 'function') {
                    window[functionName]();
                }
            }
        });
    });
}

let recognition;
let isListening = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'es-MX';
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript.trim();
        document.getElementById('newUserInput').value = transcript;
        sendMessage(transcript);
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
    };

    recognition.onend = () => {
        isListening = false;
    };
} else {
    alert('Tu navegador no permite reconocimiento de voz, intenta en otro navegador.');
}

document.getElementById('voiceButton').addEventListener('mousedown', () => {
    if (recognition && !isListening) {
        isListening = true;
        recognition.start();
    }
});

document.getElementById('voiceButton').addEventListener('mouseup', () => {
    if (recognition && isListening) {
        isListening = false;
        recognition.stop();
    }
});


document.querySelector('video').playbackRate = 0.80;
document.addEventListener('DOMContentLoaded', function () {
    document.body.addEventListener('click', function (event) {
        if (event.target.classList.contains('select-adapter')) {
            const selectedValue = event.target.getAttribute('data-value');

            sendMessage(selectedValue);
        }
    });
});

function toggleSpinner(show) {
    const loader = document.getElementById('loader');
    loader.style.display = show ? 'block' : 'none';
}

const makeApiCall = async (url, method = 'GET', body = null) => {
    const headers = {
        'X-CSRFToken': window.CSRF_TOKEN
    };

    if (body) {
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
    }


    try {
        const response = await fetch(url, {
            method,
            headers,
            credentials: 'same-origin',
            body
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
};

async function sendMessage() {
    const userInput = document.getElementById('newUserInput');
    const userMessage = userInput.value.trim();
    const chatLog = document.getElementById('chatLog');

    if (!userMessage) return;
    if (userMessage.length > 100) {
        alert("La peticion es demasiada amplia, por favor reformule su pregunta");
        return;
    }

    const escapeHtml = (unsafe) => {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    };

    chatLog.innerHTML += `<div class="logs" id="user">Tu: ${escapeHtml(userMessage)}</div>`;
    toggleSpinner(true);

    try {
        const data = await makeApiCall(
            window.COMM_URL,
            'POST',
            new URLSearchParams({ 'user_input': userMessage })
        );
        chatLog.innerHTML += `<div class="logs" id="Bot">Iris: ${escapeHtml(data.response)}</div>`;
    } catch (error) {
        chatLog.innerHTML += `<div class="logs error">Error: No se puede emitir una respuesta, por favor reporte la falla</div>`;
    } finally {
        toggleSpinner(false);
        userInput.value = '';
    }
}

var input = document.getElementById("newUserInput");

input.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        document.getElementById("btn").click();
    }
});

