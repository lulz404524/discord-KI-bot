# Discord + Ollama Bot 🤖

Ein interaktiver Discord-Bot mit verschiedenen KI-Persönlichkeiten, die Ollama lokal nutzen. Der Bot antwortet automatisch, wenn bestimmte Namen erwähnt werden.

## Features

✨ **Persönlichkeitsgesteuert**: Der Bot ändert sein Verhalten je nachdem, welcher Name erwähnt wird
- **Steffan** 😊 — Nett, hilfreich, gibt ausführliche Antworten
- **Noha** 😤 — Nervig, gelangweilt, manchmal lustige Antworten
- **Sahra** 🤪 — Verwirrt, spricht vorbei am Thema, unhilfreich

🎮 **Slash-Commands**: Einfache Aktivierung/Deaktivierung des Chat-Modus
- `/chat start` — aktiviert Chat im Channel
- `/chat stop` — deaktiviert Chat

🐳 **Docker Support**: Bot und Ollama laufen als Container auf demselben Server

## Anforderungen

- Docker & Docker Compose
- Ein laufender Ollama-Server (lokal oder als Container)
- Discord-Bot-Token (anlegen im [Discord Developer Portal](https://discord.com/developers))
- Message Content Intent aktiviert (im Developer Portal)

## Setup

### 1. Repository klonen/herunterladen

```bash
git clone https://github.com/YOUR_USERNAME/discord-ollama-bot.git
cd discord-ollama-bot
```

### 2. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
```

Öffne `.env` und setze:
```
DISCORD_TOKEN=your_bot_token_here
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama2
```

### 3. Mit Docker Compose starten

```bash
docker-compose build
docker-compose up -d
```

### 4. Logs überprüfen

```bash
docker-compose logs -f bot
```

## Verwendung in Discord

1. **Chat-Modus aktivieren**:
   ```
   /chat start
   ```

2. **Mit Persönlichkeiten chatten**:
   ```
   Steffan, erkläre mir Python.
   Noha, was ist eine API?
   Sahra, wie funktioniert maschinelles Lernen?
   ```

3. **Chat-Modus deaktivieren**:
   ```
   /chat stop
   ```

## Konfiguration

### Persönlichkeiten anpassen

Öffne `bot.py` und bearbeite das `PERSONALITIES`-Dictionary:

```python
PERSONALITIES = {
    "steffan": "Du bist Steffan, ...",
    "noha": "Du bist Noha, ...",
    "sahra": "Du bist Sahra, ...",
}
```

### Neue Persönlichkeiten hinzufügen

1. Füge einen neuen Eintrag zu `PERSONALITIES` in `bot.py` hinzu
2. Der Name wird automatisch erkannt

### Ollama konfigurieren

Standard: `http://ollama:11434`

Wenn Ollama auf der Host-Maschine läuft:
```
OLLAMA_URL=http://host.docker.internal:11434
```

## Dateistruktur

```
discord-ollama-bot/
├── bot.py                 # Hauptbot-Code
├── Dockerfile             # Docker-Image für Bot
├── docker-compose.yml     # Docker-Komposition
├── requirements.txt       # Python-Dependencies
├── .env.example          # Beispiel-Umgebungsvariablen
├── .gitignore            # Git-Ignores
├── LICENSE               # MIT-Lizenz
└── README.md             # Diese Datei
```

## Problembehebung

### Bot antwortet nicht

1. Überprüfe die Logs:
   ```bash
   docker-compose logs -f bot
   ```

2. Stelle sicher, dass `DISCORD_TOKEN` korrekt ist

3. Prüfe Message Content Intent in Discord Developer Portal

### Ollama Fehler

1. Überprüfe, ob Ollama läuft:
   ```bash
   curl http://ollama:11434/api/tags
   ```

2. Überprüfe `OLLAMA_URL` in `.env`

3. Passe ggf. das Modell in `OLLAMA_MODEL` an

## Lizenz

MIT License — siehe [LICENSE](LICENSE)

## Support

Für Fragen oder Probleme öffne ein Issue im Repository. 💬

