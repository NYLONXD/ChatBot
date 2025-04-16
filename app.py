from flask import Flask, request, render_template, jsonify, send_file
from chatbot import Chatbot
from db import ChatHistory
import os

app = Flask(__name__)
chatbot = Chatbot()
history = ChatHistory()

@app.route('/')
def home():
    return render_template('templates.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.form['user_input']
        session_id = request.form.get('session_id', 'default')
        response, audio_path = chatbot.get_response(user_input, session_id)
        history.save_message(session_id, 'user', user_input)
        history.save_message(session_id, 'bot', response)
        return jsonify({'response': response, 'audio': audio_path})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    file = request.files['file']
    session_id = request.form.get('session_id', 'default')
    result, audio_path = chatbot.analyze_file(file)
    history.save_message(session_id, 'bot', result)
    return jsonify({'response': result, 'audio': audio_path})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'})
    image = request.files['image']
    session_id = request.form.get('session_id', 'default')
    result, audio_path = chatbot.analyze_image(image)
    history.save_message(session_id, 'bot', result)
    return jsonify({'response': result, 'audio': audio_path})

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_file(os.path.join('static', 'audio', filename), mimetype='audio/mpeg')

@app.route('/history', methods=['GET'])
def get_history():
    session_id = request.args.get('session_id', 'default')
    messages = history.get_history(session_id)
    return jsonify({'history': messages})

if __name__ == '__main__':
    os.makedirs('static/audio', exist_ok=True)
    app.run(debug=True)