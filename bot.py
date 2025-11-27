import os
import asyncio
import json
import aiohttp
import discord
from discord import Intents
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
PREFIX = os.getenv("PREFIX", "!ask ")

intents = Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


async def query_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "max_tokens": 512
    }

    url = OLLAMA_URL.rstrip('/') + "/api/generate"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, timeout=60) as resp:
                text = await resp.text()
                # Try parse JSON, otherwise return raw text
                try:
                    data = json.loads(text)
                    # Attempt to extract sensible fields used by various Ollama API responses
                    if isinstance(data, dict):
                        # common keys might be 'output', 'text', or 'content'
                        for key in ("output", "text", "content", "response"):
                            if key in data:
                                if isinstance(data[key], list):
                                    return "\n".join(map(str, data[key]))
                                return str(data[key])
                        # fallback to full JSON repr
                        return json.dumps(data, ensure_ascii=False)
                    return str(data)
                except Exception:
                    return text
        except Exception as e:
            return f"Error contacting Ollama API: {e}"


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (id: {client.user.id})")
    print("Ready to relay prompts to Ollama.")


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.strip()

    # Use prefix-based queries. Example: !ask Was ist der Sinn des Lebens?
    if content.lower().startswith(PREFIX.lower()):
        prompt = content[len(PREFIX):].strip()
        if not prompt:
            await message.channel.send("Bitte gib eine Frage nach dem Präfix ein, z.B. `!ask Was ist Python?`")
            return

        # Indicate typing
        async with message.channel.typing():
            # Query Ollama
            result = await query_ollama(prompt)

        # Respect Discord message length limits; split if needed
        if len(result) <= 2000:
            await message.channel.send(result)
        else:
            # Split into chunks
            chunk_size = 1900
            for i in range(0, len(result), chunk_size):
                await message.channel.send(result[i:i+chunk_size])


if __name__ == '__main__':
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_TOKEN not set in environment or .env")
        raise SystemExit(1)
    client.run(DISCORD_TOKEN)
