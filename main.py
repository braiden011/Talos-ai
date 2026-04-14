import os
import json
import base64
import asyncio
import logging
from flask import Flask, render_template, request, jsonify, Response, session, redirect, url_for
from flask_login import current_user
from openai import OpenAI
from werkzeug.middleware.proxy_fix import ProxyFix
import edge_tts

from models import db, User, OAuth
from replit_auth import init_auth, require_login

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

db.init_app(app)

with app.app_context():
    db.create_all()

init_auth(app, db, User, OAuth)

client = OpenAI(
    api_key=os.environ["AI_INTEGRATIONS_OPENAI_API_KEY"],
    base_url=os.environ["AI_INTEGRATIONS_OPENAI_BASE_URL"],
)

JOURNAL_FILE = "Journal.txt"
JOURNAL_PIN_FILE = "journal_pin.txt"


def get_journal_pin():
    try:
        with open(JOURNAL_PIN_FILE, "r") as f:
            return f.read().strip()
    except:
        return None


def set_journal_pin(pin):
    with open(JOURNAL_PIN_FILE, "w") as f:
        f.write(pin.strip())


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


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('landing.html')
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
@require_login
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
        response = client.chat.completions.create(model="gpt-5", messages=messages)
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
        logging.error(f"[Talos error] {e}")
        return jsonify({"response": f"I encountered an error: {str(e)}"})


@app.route('/reset', methods=['POST'])
@require_login
def reset():
    conversation_history.clear()
    return jsonify({"status": "ok"})


@app.route('/tts', methods=['POST'])
@require_login
def tts():
    text = request.json.get('text', '').strip()
    if not text:
        return '', 400
    try:
        async def generate_audio():
            communicate = edge_tts.Communicate(
                text,
                voice="en-US-ChristopherNeural",
                rate="-8%",
                pitch="-12Hz",
                volume="+0%",
            )
            chunks = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    chunks.append(chunk["data"])
            return b"".join(chunks)

        audio_data = asyncio.run(generate_audio())
        return Response(audio_data, mimetype='audio/mpeg')
    except Exception as e:
        logging.error(f"[TTS error] {e}")
        return '', 500


# ── Journal Routes ──

@app.route('/journal/has_pin', methods=['GET'])
@require_login
def journal_has_pin():
    return jsonify({"has_pin": get_journal_pin() is not None})


@app.route('/journal/setup', methods=['POST'])
@require_login
def journal_setup():
    if get_journal_pin() is not None:
        return jsonify({"error": "PIN already set."})
    pin = request.json.get("pin", "").strip()
    if not pin.isdigit() or len(pin) < 4:
        return jsonify({"error": "PIN must be at least 4 digits."})
    set_journal_pin(pin)
    return jsonify({"status": "ok"})


@app.route('/journal/unlock', methods=['POST'])
@require_login
def journal_unlock():
    passcode = request.json.get("passcode", "")
    if passcode != get_journal_pin():
        return jsonify({"error": "Wrong PIN. Try again."})
    entries = []
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, "r") as f:
            entries = [line.strip() for line in f.readlines() if line.strip()]
    return jsonify({"entries": entries})


@app.route('/journal/write', methods=['POST'])
@require_login
def journal_write():
    data = request.json
    if data.get("passcode") != get_journal_pin():
        return jsonify({"error": "Wrong PIN."})
    entry = data.get("entry", "").strip()
    if entry:
        with open(JOURNAL_FILE, "a") as f:
            f.write(f"- {entry}\n")
    return jsonify({"status": "ok"})


@app.route('/journal/delete', methods=['POST'])
@require_login
def journal_delete():
    data = request.json
    if data.get("passcode") != get_journal_pin():
        return jsonify({"error": "Wrong PIN."})
    open(JOURNAL_FILE, "w").close()
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
