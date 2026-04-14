# Talos AI

A personal AI chatbot with a professional dark web interface, created by Braiden Bryer.

## Tech Stack
- **Backend**: Python + Flask (port 5000)
- **AI**: OpenAI `gpt-5` via Replit AI Integrations — no API key needed
- **Frontend**: Vanilla HTML/CSS/JS in `templates/index.html`
- **TTS**: Browser Web Speech API (toggleable, deep English male voice)
- **Voice Input**: Web Speech API (SpeechRecognition)

## Key Files
- `main.py` — Flask server, OpenAI chat endpoint (`/ask` with image support), journal routes, system prompt
- `templates/index.html` — Chat UI with voice input, image upload, TTS toggle, journal modal
- `Talos.json` — Memory store (creator name, etc.)
- `Book.txt` — Knowledge base injected into system prompt
- `Journal.txt` — Secure journal file (passcode protected)
- `static/logo.png` — Spartan helmet logo with transparent background

## Features
- **Chat**: Full conversation with gpt-5, context-aware, dark gold UI
- **Image understanding**: Attach an image via 🖼️ button; Talos analyzes it using vision
- **Voice input**: Click 🎤 — speak — message is auto-sent; response is read aloud
- **TTS**: Deep English male voice via Web Speech API, toggleable with 🔊 button
- **Tutor mode**: For homework/academic questions, Talos explains and guides rather than giving direct answers
- **Secure journal**: Click 📓 in header, enter passcode `0907`, read/write/delete entries stored in `Journal.txt`

## API Notes
- Do NOT pass `max_tokens` or `max_completion_tokens` to gpt-5 — causes empty responses
- Image is sent as base64 in the `image` field of the `/ask` JSON payload
- ElevenLabs TTS was dismissed by the user; Web Speech API only
