# Talos AI

A personal AI chatbot with a web interface, created by Braiden Bryer.

## Tech Stack
- **Backend**: Python + Flask (port 5000)
- **AI Brain**: OpenAI via Replit AI Integrations (`gpt-5-mini`) — no API key needed, billed to Replit credits
- **Frontend**: Vanilla HTML/CSS/JS in `templates/index.html`
- **TTS**: Browser Web Speech API (optional, toggleable)
- **Voice Input**: Web Speech API (SpeechRecognition)

## Key Files
- `main.py` — Flask server, OpenAI chat endpoint (`/ask`), conversation history, reset endpoint (`/reset`)
- `templates/index.html` — Chat UI with voice input, TTS toggle, typing indicator
- `Talos.json` — Memory store (creator name, etc.)
- `Book.txt` — Knowledge base injected into Talos's system prompt
- `Journal.txt` — Secure journal (passcode protected in original version)

## Notes
- ElevenLabs TTS integration was proposed but dismissed by the user. If higher quality voice output is needed in the future, reconnect ElevenLabs via the integrations panel or provide an API key to store as a secret.
- Conversation history is stored in memory (resets when server restarts). For persistence, consider a database.
