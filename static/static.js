function startSpeech() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Sorry, your browser doesn't support speech recognition.");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('user_input').value = transcript;
        sendMessage();
    };

    recognition.onerror = function (event) {
        console.error('Speech recognition error:', event.error);
        alert("Speech recognition failed. Please try again.");
    };

    recognition.start();
}

const sessionId = Math.random().toString(36).substring(2);

async function loadHistory() {
    try {
        const res = await fetch(`/history?session_id=${sessionId}`);
        if (!res.ok) throw new Error('Could not fetch history');
        const data = await res.json();
        const chatbox = document.getElementById('chatbox');
        chatbox.innerHTML = '';

        data.history.forEach(msg => {
            chatbox.innerHTML += `<div class="${msg.role}"><b>${msg.role === 'user' ? 'You' : 'Bot'}:</b> ${msg.content}</div>`;
        });
        chatbox.scrollTop = chatbox.scrollHeight;
    } catch (error) {
        console.error('History error:', error);
    }
}

async function sendMessage() {
    try {
        const input = document.getElementById('user_input').value.trim();
        if (!input) return;

        const chatbox = document.getElementById('chatbox');
        chatbox.innerHTML += `<div class="user"><b>You:</b> ${input}</div>`;
        document.getElementById('user_input').value = '';

        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `user_input=${encodeURIComponent(input)}&session_id=${sessionId}`
        });

        const data = await res.json();

        if (data.error) {
            chatbox.innerHTML += `<div class="bot"><b>Bot:</b> ❌ Error: ${data.error}</div>`;
        } else {
            chatbox.innerHTML += `<div class="bot"><b>Bot:</b> ${data.response}</div>`;
            if (data.audio) {
                const audio = new Audio(data.audio);
                audio.play();
            }
        }

        chatbox.scrollTop = chatbox.scrollHeight;
    } catch (error) {
        console.error('Send error:', error);
        document.getElementById('chatbox').innerHTML += `<div class="bot"><b>Bot:</b> ⚠️ Could not process your message.</div>`;
    }
}

async function uploadFile() {
    const fileInput = document.getElementById('file_input');
    if (!fileInput.files.length) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('session_id', sessionId);

    try {
        const res = await fetch('/upload', { method: 'POST', body: formData });
        const data = await res.json();

        document.getElementById('chatbox').innerHTML += `<div class="bot"><b>Bot:</b> ${data.response}</div>`;
        if (data.audio) {
            const audio = new Audio(data.audio);
            audio.play();
        }

        fileInput.value = '';
    } catch (error) {
        console.error('File upload error:', error);
    }
}

async function uploadImage() {
    const imageInput = document.getElementById('image_input');
    if (!imageInput.files.length) return;

    const formData = new FormData();
    formData.append('image', imageInput.files[0]);
    formData.append('session_id', sessionId);

    try {
        const res = await fetch('/upload_image', { method: 'POST', body: formData });
        const data = await res.json();

        document.getElementById('chatbox').innerHTML += `<div class="bot"><b>Bot:</b> ${data.response}</div>`;
        if (data.audio) {
            const audio = new Audio(data.audio);
            audio.play();
        }

        imageInput.value = '';
    } catch (error) {
        console.error('Image upload error:', error);
    }
}

document.getElementById('user_input').addEventListener('keypress', e => {
    if (e.key === 'Enter') sendMessage();
});

window.onload = loadHistory;
