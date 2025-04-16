from transformers import T5Tokenizer, T5ForConditionalGeneration, BlipProcessor, BlipForConditionalGeneration
import requests
import PyPDF2
import sqlite3
from PIL import Image
import io
from gtts import gTTS
import os
import uuid

class Chatbot:
    def __init__(self):
        print("[INFO] Initializing Chatbot...")
        # Text model
        self.text_model_name = "google/flan-t5-base"
        self.text_tokenizer = T5Tokenizer.from_pretrained(self.text_model_name)
        self.text_model = T5ForConditionalGeneration.from_pretrained(self.text_model_name)

        # Image model
        self.image_model_name = "Salesforce/blip-image-captioning-base"
        self.image_processor = BlipProcessor.from_pretrained(self.image_model_name)
        self.image_model = BlipForConditionalGeneration.from_pretrained(self.image_model_name)

        # Search API
        self.search_api_key = "sk-9e8318fb40194736b4ff6bfe2129642f"  # DeepSeek AI API key

        # System prompt
        self.system_prompt = (
            "You are Grok-Lite, a helpful, witty AI inspired by sci-fi assistants. "
            "Provide clear, detailed answers with a touch of humor."
        )

        # Audio output
        self.audio_dir = "static/audio"
        os.makedirs(self.audio_dir, exist_ok=True)

        print("[INFO] Chatbot ready to go!")

    def generate_audio(self, text):
        try:
            audio_file = f"{uuid.uuid4()}.mp3"
            audio_path = os.path.join(self.audio_dir, audio_file)
            tts = gTTS(text=text, lang='en')
            tts.save(audio_path)
            return f"/audio/{audio_file}"
        except Exception as e:
            print(f"[ERROR] Audio generation failed: {e}")
            return None

    def get_response(self, user_input, session_id):
        try:
            # Fetch context
            conn = sqlite3.connect('chat_history.db')
            c = conn.cursor()
            c.execute("SELECT role, content FROM history WHERE session_id = ? ORDER BY id DESC LIMIT 5", (session_id,))
            context = c.fetchall()
            conn.close()

            context_str = "".join([f"{row[0]}: {row[1]}\n" for row in context[::-1]])
            prompt =(
    f"{self.system_prompt}\n"
    f"{context_str}"
    f"User asked: \"{user_input}\"\n"
    f"Please reply with a helpful, detailed response in 2-4 sentences:\n"
    f"Assistant:"
)


            if user_input.lower().startswith("search ") or "research" in user_input.lower():
                query = user_input.replace("search ", "").strip()
                search_results = self.deep_research(query)
                prompt += f"Web research: {search_results}\nSynthesize a detailed answer: "

            inputs = self.text_tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            outputs = self.text_model.generate(
                inputs.input_ids,
    max_length=512,            # allow more output
    min_length=50,             # force longer responses
    num_beams=5,
    no_repeat_ngram_size=2,
    early_stopping=True
            )
            response = self.text_tokenizer.decode(outputs[0], skip_special_tokens=True)
            audio_path = self.generate_audio(response)
            return response, audio_path

        except Exception as e:
            return f"Something went wrong: {e}", None

    def deep_research(self, query):
        try:
            # Use DeepSeek AI's endpoint
            url = f"https://api.deepseek.ai/search?q={query}&api_key={self.search_api_key}"
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for HTTP issues
            data = response.json()

            # Parse the response based on DeepSeek AI's structure
            results = data.get("results", [])
            snippets = [result.get("snippet", "") for result in results[:5] if result.get("snippet")]
            summary = " ".join(snippets)

            return summary[:2000] if summary else "No relevant results found."
        except Exception as e:
            print(f"[ERROR] DeepSeek AI search failed: {e}")
            return "Sorry, I couldn't fetch web results. Try again later!"

    def analyze_file(self, file):
        try:
            if file.filename.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(file)
                text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
            elif file.filename.endswith('.txt'):
                text = file.read().decode('utf-8')
            else:
                return "Unsupported file type. Use PDF or TXT.", None

            prompt = f"{self.system_prompt}\nSummarize this text in 100 words or less:\n{text[:2000]}\nassistant: "
            inputs = self.text_tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            outputs = self.text_model.generate(inputs.input_ids, max_length=100, num_beams=5)
            summary = self.text_tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = f"File summary: {summary}"
            audio_path = self.generate_audio(response)
            return response, audio_path

        except Exception as e:
            return f"Error reading file: {e}", None

    def analyze_image(self, image_file):
        try:
            image = Image.open(image_file).convert("RGB")
            inputs = self.image_processor(images=image, return_tensors="pt")
            outputs = self.image_model.generate(**inputs)
            caption = self.image_processor.decode(outputs[0], skip_special_tokens=True)

            prompt = f"{self.system_prompt}\nDescribe this image in 50 words or less based on: '{caption}'\nassistant: "
            text_inputs = self.text_tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            text_outputs = self.text_model.generate(text_inputs.input_ids, max_length=50, num_beams=5)
            summary = self.text_tokenizer.decode(text_outputs[0], skip_special_tokens=True)
            response = f"Image summary: {summary}"
            audio_path = self.generate_audio(response)
            return response, audio_path

        except Exception as e:
            return f"Error processing image: {e}", None
