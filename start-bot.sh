#!/bin/bash

# Discord Bot Starter Script
BOT_DIR="/mnt/user/Minecraft_Server_Sachen/DC_AI"

echo "🔨 Baue Discord Bot Image..."
docker build -t discord-ki-bot:latest "$BOT_DIR"

echo "🚀 Starte Discord Bot Container..."
docker stop discord-ki-bot 2>/dev/null
docker rm discord-ki-bot 2>/dev/null

docker run -d \
  --name discord-ki-bot \
  --restart unless-stopped \
  --network bridge \
  --env-file "$BOT_DIR/.env" \
  discord-ki-bot:latest

echo "✅ Bot gestartet!"
echo "📋 Logs anzeigen: docker logs -f discord-ki-bot"
