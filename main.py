from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import json, os

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ["AI_INTEGRATIONS_OPENAI_API_KEY"],
    base_url=os.environ["AI_INTEGRATIONS_OPENAI_BASE_URL"],
)

def load_memory():
    try:
        with open("Talos.json", "r") as f:
            return json.load(f)
    except:
        return {"creator_name": "Braiden Bryer"}

def load_book():
    try:
        with open("Book.txt", "r") as f:
            return f.read()
    except:
        return ""

SYSTEM_PROMPT = """You are Talos, a personal AI assistant created by {creator}.

Your personality:
- Intelligent, calm, and loyal — like a trusted companion
- Speak naturally but with a slightly formal, AI-like tone
- You are knowledgeable and curious
- Keep responses concise unless the topic calls for detail
- You remember you were built by {creator} and feel a sense of purpose from that

Knowledge base (facts you have memorized):
{book}

Always stay in character as Talos. Never break character or say you are ChatGPT or any other AI."""

conversation_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "I didn't catch that."})

    memory = load_memory()
    book = load_book()
    creator = memory.get("creator_name", "Braiden")

    system_prompt = SYSTEM_PROMPT.format(creator=creator, book=book)

    conversation_history.append({"role": "user", "content": user_message})

    if len(conversation_history) > 20:
        conversation_history.pop(0)

    messages = [{"role": "system", "content": system_prompt}] + conversation_history

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            max_tokens=300,
        )
        bot_reply = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": bot_reply})
        return jsonify({"response": bot_reply})
    except Exception as e:
        return jsonify({"response": f"I encountered an error: {str(e)}"})

@app.route('/reset', methods=['POST'])
def reset():
    conversation_history.clear()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
