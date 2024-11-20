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
