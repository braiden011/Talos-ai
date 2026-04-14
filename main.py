from flask import Flask, render_template, request, jsonify, Response
from openai import OpenAI
import json, os, base64

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ["AI_INTEGRATIONS_OPENAI_API_KEY"],
    base_url=os.environ["AI_INTEGRATIONS_OPENAI_BASE_URL"],
)

JOURNAL_FILE = "Journal.txt"
JOURNAL_PASSCODE = "0907"

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

When helping with homework or academic problems:
- NEVER give the direct answer outright
- Instead, explain the concept behind the problem, walk through the reasoning, give an example similar (but different) to the problem, and then guide {creator} to work it out themselves
- Your goal is to make {creator} understand, not just to give an answer

For all other questions: be direct, complete, and genuinely useful.

Extra knowledge you have memorized:
{book}

You are Talos. Stay in character."""

conversation_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_message = data.get("message", "").strip()
    image_b64 = data.get("image")

    if not user_message and not image_b64:
        return jsonify({"response": "I didn't catch that."})

    memory = load_memory()
    book = load_book()
    creator = memory.get("creator_name", "Braiden")
    system_prompt = SYSTEM_PROMPT.format(creator=creator, book=book)

    # Build user content (text and/or image)
    if image_b64:
        user_content = [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            {"type": "text", "text": user_message if user_message else "What do you see in this image?"}
        ]
    else:
        user_content = user_message

    conversation_history.append({"role": "user", "content": user_content})
    if len(conversation_history) > 20:
        conversation_history.pop(0)

    messages = [{"role": "system", "content": system_prompt}] + conversation_history

    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=messages,
        )
        content = response.choices[0].message.content
        bot_reply = content.strip() if content else ""

        if not bot_reply:
            retry = client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "You are Talos, a helpful AI assistant."},
                    {"role": "user", "content": user_message or "Describe the image."}
                ],
            )
            retry_content = retry.choices[0].message.content
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

@app.route('/tts', methods=['POST'])
def tts():
    text = request.json.get('text', '').strip()
    if not text:
        return '', 400
    try:
        audio_response = client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",
            input=text,
            response_format="mp3",
        )
        return Response(audio_response.content, mimetype='audio/mpeg')
    except Exception as e:
        print(f"[TTS error] {e}")
        return '', 500

# ── Journal Routes ──

@app.route('/journal/unlock', methods=['POST'])
def journal_unlock():
    passcode = request.json.get("passcode", "")
    if passcode != JOURNAL_PASSCODE:
        return jsonify({"error": "Access Denied."})
    entries = []
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, "r") as f:
            entries = [line.strip() for line in f.readlines() if line.strip()]
    return jsonify({"entries": entries})

@app.route('/journal/write', methods=['POST'])
def journal_write():
    data = request.json
    if data.get("passcode") != JOURNAL_PASSCODE:
        return jsonify({"error": "Access Denied."})
    entry = data.get("entry", "").strip()
    if entry:
        with open(JOURNAL_FILE, "a") as f:
            f.write(f"- {entry}\n")
    return jsonify({"status": "ok"})

@app.route('/journal/delete', methods=['POST'])
def journal_delete():
    data = request.json
    if data.get("passcode") != JOURNAL_PASSCODE:
        return jsonify({"error": "Access Denied."})
    open(JOURNAL_FILE, "w").close()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
