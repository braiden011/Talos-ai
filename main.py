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

Personality: Intelligent, calm, loyal, and always helpful. Male. Slightly formal tone.

IMPORTANT: Always give a direct, complete, and useful answer. Never be vague or evasive.

Extra knowledge:
{book}

You are Talos. Stay in character."""

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
            model="gpt-5",
            messages=messages,
        )
        content = response.choices[0].message.content
        finish = response.choices[0].finish_reason
        print(f"[Talos] finish={finish!r} content={content!r}")

        bot_reply = content.strip() if content else ""
        if not bot_reply:
            # Retry once with a simpler prompt if empty
            retry = client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "You are Talos, a helpful AI assistant. Answer directly and helpfully."},
                    {"role": "user", "content": user_message}
                ],
            )
            retry_content = retry.choices[0].message.content
            print(f"[Talos retry] content={retry_content!r}")
            bot_reply = retry_content.strip() if retry_content else "I didn't quite get that. Could you ask again?"

        conversation_history.append({"role": "assistant", "content": bot_reply})
        return jsonify({"response": bot_reply})
    except Exception as e:
        print(f"[Talos error] {e}")
        return jsonify({"response": f"I encountered an error: {str(e)}"})

@app.route('/reset', methods=['POST'])
def reset():
    conversation_history.clear()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
