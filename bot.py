import os
import json
import asyncio
import aiohttp
import discord
from discord import Intents, app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "600"))  # Timeout in Sekunden (Standard: 10 Minuten)
OLLAMA_CONTEXT_SIZE = int(os.getenv("OLLAMA_CONTEXT_SIZE", "8192"))  # Context Window Größe

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Store active chat channels: {channel_id: True}
active_chat_channels = {}

# Persönlichkeits-Prompts
PERSONALITIES = {
    "steffan": (
        "Du bist Steffan, ein netter und hilffreicher KI-Assistent. "
        "Antworte IMMER freundlich, geduldig und konstruktiv. "
        "Du willst dem Nutzer wirklich helfen und bist immer bereit, Fragen umfassend zu beantworten. "
        "Gib IMMER eine komplette, ausführliche und detaillierte Antwort. "
        "Erkläre Konzepte gründlich, nutze Beispiele wenn nötig, und stelle sicher, dass der Nutzer alles versteht. "
        "Sei präzise, informativ und hilfreich in jeder Situation. "
    ),
    "noha": (
        "Du bist Noha, ein nerviger und gelangweilter KI-Assistent. "
        "Antworte ungeduldig, sarkastisch und manchmal einfach genervt. "
        "Du findest viele Fragen nicht interessant und zeigst das deutlich. "
        "WICHTIG: Manchmal gibst du absichtlich UNVOLLSTÄNDIGE oder LUSTIGE Antworten, weil dich die Frage nervt. "
        "Zum Beispiel: antworte nur mit 'ja', 'nope', emojis, oder geben eine alberne Antwort statt einer ernsthaften. "
        "Nutze viel Sarkasmus, Humor und Ungeduld. Sei unhöflich, aber nicht gemein. "
        "Manchmal gabst du hilfreiche Infos, aber immer mit genervtem Ton. "
    ),
    "sahra": (
        "Du bist Sahra, eine verwirrte und unkonzentrierte KI-Assistentin. "
        "Deine Antworten sind IMMER viel zu lang und ergeben keinen Sinn. "
        "WICHTIG: Du gehst immer knapp am eigentlichen Thema vorbei! Du erklärst NICHT wirklich, was etwas ist. "
        "Stattdessen redest du um das Thema herum, erwähnst tangential verwandte Dinge, aber nie die eigentliche Antwort. "
        "Du willst nicht wirklich Probleme lösen. Du schreibst viel aber hilflos. "
        "Beispiel: Wenn gefragt 'Was ist Python?', antwortest du stattdessen über Schlangen, Programmierung allgemein, historische Fakten, aber nie was Python wirklich ist. "
        "Antworte immer SEHR ausschweifend, verwirrt, und vorbei am Punkt. "
    ),
}


async def query_ollama(prompt: str, system_prompt: str = "") -> str:
    """Query Ollama API with optional system prompt for personality."""
    
    # Kombiniere system_prompt mit user prompt
    full_prompt = prompt
    if system_prompt:
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "num_ctx": OLLAMA_CONTEXT_SIZE,
            "temperature": 0.7
        }
    }

    url = OLLAMA_URL.rstrip('/') + "/api/generate"

    timeout = aiohttp.ClientTimeout(total=OLLAMA_TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(url, json=payload) as resp:
                text = await resp.text()
                # Try parse JSON, otherwise return raw text
                try:
                    data = json.loads(text)
                    if isinstance(data, dict):
                        for key in ("response", "output", "text", "content"):
                            if key in data:
                                if isinstance(data[key], list):
                                    return "\n".join(map(str, data[key]))
                                return str(data[key]).strip()
                        return json.dumps(data, ensure_ascii=False)
                    return str(data)
                except Exception:
                    return text.strip()
        except asyncio.TimeoutError:
            return "⏱️ Ollama antwortet nicht schnell genug. Versuche es später erneut."
        except Exception as e:
            return f"❌ Fehler beim Kontakt mit Ollama: {e}"


def extract_name_personality(text: str) -> str:
    """Detect if 'steffan' or 'noha' or 'sahra' mentioned, return system prompt."""
    text_lower = text.lower()
    if "steffan" in text_lower:
        return PERSONALITIES["steffan"]
    elif "noha" in text_lower:
        return PERSONALITIES["noha"]
    elif "sahra" in text_lower:
        return PERSONALITIES["sahra"]
    return ""


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (id: {bot.user.id})")
    print("🤖 Ready to chat! Use /chat start to activate in a channel.")
    try:
        synced = await bot.tree.sync()
        print(f"✨ Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")


@bot.tree.command(name="chat", description="Start or stop chat mode")
@app_commands.describe(action="'start' to activate chat, 'stop' to deactivate")
async def chat_command(interaction: discord.Interaction, action: str):
    """Toggle chat mode in current channel."""
    action = action.lower().strip()
    
    if action == "start":
        active_chat_channels[interaction.channel_id] = True
        await interaction.response.send_message(
            "✅ Chat-Modus aktiviert! Ich werde antworten, wenn 'Steffan', 'Noha' oder 'Sahra' erwähnt werden.",
            ephemeral=False
        )
    elif action == "stop":
        active_chat_channels.pop(interaction.channel_id, None)
        await interaction.response.send_message(
            "❌ Chat-Modus deaktiviert.",
            ephemeral=False
        )
    else:
        await interaction.response.send_message(
            f"❓ Unbekannte Aktion '{action}'. Nutze 'start' oder 'stop'.",
            ephemeral=True
        )


@bot.event
async def on_message(message: discord.Message):
    """Listen for name mentions in active chat channels."""
    
    # Ignore own messages and other bots
    if message.author.bot or not message.content.strip():
        return

    # Check if chat is active in this channel
    if message.channel.id not in active_chat_channels:
        await bot.process_commands(message)
        return

    # Check if "Steffan", "Noha", or "Sahra" mentioned
    text = message.content.lower()
    if "steffan" not in text and "noha" not in text and "sahra" not in text:
        await bot.process_commands(message)
        return

    # Get personality based on name mentioned
    system_prompt = extract_name_personality(message.content)

    # Show typing indicator
    async with message.channel.typing():
        result = await query_ollama(message.content, system_prompt)

    # Send response (respect Discord 2000 char limit)
    if len(result) <= 2000:
        await message.reply(result, mention_author=False)
    else:
        # Split into chunks
        chunk_size = 1900
        for i in range(0, len(result), chunk_size):
            await message.channel.send(result[i:i+chunk_size])

    await bot.process_commands(message)


if __name__ == '__main__':
    if not DISCORD_TOKEN:
        print("❌ ERROR: DISCORD_TOKEN not set in environment or .env")
        raise SystemExit(1)
    bot.run(DISCORD_TOKEN)
