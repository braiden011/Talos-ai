from flask import Flask, render_template, request, jsonify
import json, os, random
from difflib import get_close_matches

app = Flask(__name__)

# --- TALOS LOGIC (The stuff you already built) ---
class TalosEngine:
    def __init__(self):
        self.filename = "Talos.json"
        self.book_file = "Book.txt"
        self.memory = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                try: return json.load(f)
                except: return {"user_name": "Braiden"}
        return {"user_name": "Braiden"}

    def search_book(self, query):
        if os.path.exists(self.book_file):
            with open(self.book_file, "r") as f:
                for line in f:
                    if query.lower() in line.lower() and len(query) > 3:
                        return line.strip()
        return None

    def get_response(self, user_input):
        user_input = user_input.lower().strip()
        words = user_input.split()

        # Check Memory
        for word in words:
            match = get_close_matches(word, list(self.memory.keys()), n=1, cutoff=0.7)
            if match: return f"I remember: {self.memory[match[0]]}"

        # Check Book
        for word in words:
            fact = self.search_book(word)
            if fact: return f"From my records: {fact}"

        return "I'm not sure about that, Braiden. Can you teach me?"

talos = TalosEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get("message")
    bot_response = talos.get_response(user_message)
    return jsonify({"response": bot_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)