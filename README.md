# Discord + Ollama Dockerized Bot

Kurzanleitung (Deutsch): Ein einfacher Discord-Bot, der Anfragen an eine lokale Ollama-Instanz weiterleitet.

Dateien:
- `bot.py` - Python-Discord-Bot mit Ollama-HTTP-Client
- `Dockerfile` - baut das Bot-Image
- `docker-compose.yml` - startet den Bot; optionaler Ollama-Block als Platzhalter
- `.env.example` - Umgebungsvariablenbeispiel

Vorraussetzungen:
- Docker und Docker Compose installiert
- Ein laufender Ollama-Server auf dem Host (Standard `http://localhost:11434`) oder als Container
- Ein Discord-Bot-Token (im Discord Developer Portal anlegen) und die Intent `MESSAGE CONTENT INTENT` aktivieren

Schnellstart (PowerShell):

1. Kopiere `.env.example` zu `.env` und fülle `DISCORD_TOKEN` aus.

```powershell
cp .env.example .env
# Öffne .env und setze DISCORD_TOKEN und ggf. OLLAMA_URL
```

2. Build & run mit Docker Compose:

```powershell
docker-compose build
docker-compose up -d
```

3. In Discord: Nutze im Server den Befehl mit dem Präfix (Standard `!ask `):

```text
!ask Erzähle mir etwas über Python.
```

Hinweise & Anpassungen:
- Wenn dein Ollama-Container anders heißt oder auf einem anderen Port läuft, passe `OLLAMA_URL` in `.env` an (z.B. `http://ollama:11434`).
- Das Beispiel nutzt ein einfaches Präfix (`!ask `). Du kannst `bot.py` erweitern auf Slash-Commands oder Mentions.
- Die Ollama-API-Pfade/Antwortstruktur können sich unterscheiden; wenn Antworten leer sind, prüfe die genaue API-Antwort und passe `query_ollama` in `bot.py` an.

Probleme?
- Schick mir die Fehlermeldung aus den Container-Logs und ich helfe beim Debuggen:

```powershell
docker-compose logs -f bot
```
