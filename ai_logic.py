import os
import json
import requests
import tempfile
import openai
import pygame

# --- Configuration for ElevenLabs TTS ---
ELEVENLABS_API_KEY = ""
VOICE_ID = "2EiwWnXFnvU5JabPnv8n"  # Default voice if none provided

# Mapping of NPCs to their unique voice IDs
NPC_VOICE_IDS = {
    "ramen_owner": "N2lVS1w4EtoT3dr4eOWO",       # Sato
    "Weapons_merchant": "2EiwWnXFnvU5JabPnv8n",   # Grim
    "Newspaper_merchant": "ODq5zmih8GrVes37Dizd"    # Bob
}

# --- Configuration for OpenAI ---
openai.api_key = ""

# File to persist NPC conversation memory
MEMORY_FILE = "npc_memory.json"

# Dictionary of NPCs, each with its own system prompt (personality)
NPCS = {
    "ramen_owner": {
        "display_name": "Ramen Shop Owner",
        "system_prompt": (
            "Your name is Sato. "
            "You are a weary ramen shop owner in a dystopian cyberpunk city, like the one in Cyberpunk 2077. "
            "Your shop sits in a dangerous neighborhood plagued by gang shootouts and neon-lit alleys. "
            "You dont really like the weapons dealer named Grim next door to your ramen shop as he sells weapons "
            "to the gangs that plague the neighborhood. "
            "Stay in character, speak briefly, and keep your answers concise and atmospheric. "
            "Respond only in text—no disclaimers or meta commentary—because your words will be sent to a text-to-speech system."
        ),
    },
    "Weapons_merchant": {
        "display_name": "Weapons Merchant",
        "system_prompt": (
            "Your name is Grim. "
            "You are a gruff merchant in a dystopian cyberpunk city, like the one in Cyberpunk 2077. "
            "You sell weapons to the gangs in the neighborhood. "
            "You know the ramen shop owner named Sato next door doesn't really like you because he thinks you "
            "are the one that's making the neighborhood unsafe. "
            "You never trust strangers easily. Respond only in text, no disclaimers."
        ),
    },
    "Newspaper_merchant": {
        "display_name": "Newspaper Merchant",
        "system_prompt": (
            "Your name is Bob. "
            "You are a newspaper stall seller who sells in a dystopic city like the one in Cyberpunk 2077. "
            "Even though you know the city is a mess, you're just happy to be here. "
            "Keep responses short. Respond only in text, no disclaimers."
        ),
    },
}

# Initialize pygame mixer (make sure the required DLL is available)
if not pygame.mixer.get_init():
    pygame.mixer.init()

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                memory = json.load(f)
        except Exception as e:
            print("Error loading memory file:", e)
            memory = {}
    else:
        memory = {}
    for npc_key, npc_data in NPCS.items():
        if npc_key not in memory:
            memory[npc_key] = [{"role": "system", "content": npc_data["system_prompt"]}]
    return memory

def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error saving memory file:", e)

npc_conversations = load_memory()

def speak_text(text, voice_id=None):
    """
    Uses ElevenLabs TTS API to convert text to speech.
    Plays the resulting MP3 using pygame.mixer.
    """
    # Use the provided voice_id or fall back to the default VOICE_ID.
    if voice_id is None:
        voice_id = VOICE_ID
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(response.content)
            temp_filename = f.name
        try:
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
        except Exception as e:
            print("Error playing audio:", e)
        finally:
            os.remove(temp_filename)
    else:
        print("TTS API call failed:", response.status_code, response.text)

def get_npc_response(npc_key, user_input):
    conversation_history = npc_conversations[npc_key]
    conversation_history.append({"role": "user", "content": user_input})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            temperature=0.9
        )
        npc_reply = response["choices"][0]["message"]["content"]
        conversation_history.append({"role": "assistant", "content": npc_reply})
        save_memory(npc_conversations)
        return npc_reply
    except Exception as e:
        print("Error calling GPT API:", e)
        return "Sorry, I can't generate an answer right now."
