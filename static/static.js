const sessionId = Math.random().toString(36).substring(2);

        async function loadHistory() {
            try {
                let response = await fetch(`/history?session_id=${sessionId}`);
                if (!response.ok) throw new Error('Failed to load history');
                let data = await response.json();
                let chatbox = document.getElementById('chatbox');
                chatbox.innerHTML = '';
                data.history.forEach(msg => {
                    chatbox.innerHTML += `<div class="${msg.role}"><b>${msg.role}:</b> ${msg.content}</div>`;
                });
                chatbox.scrollTop = chatbox.scrollHeight;
            } catch (error) {
                console.error(error);
            }
        }

        async function sendMessage() {
    try {
        let input = document.getElementById('user_input').value;
        if (!input) return;
        let chatbox = document.getElementById('chatbox');
        chatbox.innerHTML += `<div class="user"><b>You:</b> ${input}</div>`;
        document.getElementById('user_input').value = '';

        let response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `user_input=${encodeURIComponent(input)}&session_id=${sessionId}`
        });
        if (!response.ok) throw new Error('Failed to send message');
        let data = await response.json();

        // Check if the response contains an error
        if (data.error) {
            chatbox.innerHTML += `<div class="bot"><b>Bot:</b> Error: ${data.error}</div>`;
        } else {
            chatbox.innerHTML += `<div class="bot"><b>Bot:</b> ${data.response}</div>`;
            if (data.audio) {
                let audio = new Audio(data.audio);
                audio.play();
            }
        }
        chatbox.scrollTop = chatbox.scrollHeight;
    } catch (error) {
        console.error(error);
        let chatbox = document.getElementById('chatbox');
        chatbox.innerHTML += `<div class="bot"><b>Bot:</b> Error: Failed to process your request.</div>`;
    }
}

        async function uploadFile() {
            try {
                let fileInput = document.getElementById('file_input');
                if (!fileInput.files.length) return;
                let formData = new FormData();
                formData.append('file', fileInput.files[0]);
                formData.append('session_id', sessionId);

                let response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                if (!response.ok) throw new Error('Failed to upload file');
                let data = await response.json();
                let chatbox = document.getElementById('chatbox');
                chatbox.innerHTML += `<div class="bot"><b>Bot:</b> ${data.response}</div>`;
                if (data.audio) {
                    let audio = new Audio(data.audio);
                    audio.play();
                }
                chatbox.scrollTop = chatbox.scrollHeight;
                fileInput.value = '';
            } catch (error) {
                console.error(error);
            }
        }

        async function uploadImage() {
            try {
                let imageInput = document.getElementById('image_input');
                if (!imageInput.files.length) return;
                let formData = new FormData();
                formData.append('image', imageInput.files[0]);
                formData.append('session_id', sessionId);

                let response = await fetch('/upload_image', {
                    method: 'POST',
                    body: formData
                });
                if (!response.ok) throw new Error('Failed to upload image');
                let data = await response.json();
                let chatbox = document.getElementById('chatbox');
                chatbox.innerHTML += `<div class="bot"><b>Bot:</b> ${data.response}</div>`;
                if (data.audio) {
                    let audio = new Audio(data.audio);
                    audio.play();
                }
                chatbox.scrollTop = chatbox.scrollHeight;
                imageInput.value = '';
            } catch (error) {
                console.error(error.q);
            }
        }

        document.getElementById('user_input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });

        window.onload = loadHistory;





function startSpeech() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Sorry, your browser doesn't support speech recognition.");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('user_input').value = transcript;
        sendMessage();
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        alert("Speech recognition failed. Try again.");
    };

    recognition.onend = function() {
        console.log('Speech recognition ended.');
    };

    recognition.start();
    
}