import os
import json
import requests
import tempfile
from playsound import playsound
import openai

# --- Configuration for ElevenLabs TTS ---
ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"
VOICE_ID = "2EiwWnXFnvU5JabPnv8n"  # Replace with your desired voice ID from ElevenLabs

# --- Configuration for OpenAI ---
openai.api_key = "YOUR_OPENAI_API_KEY"

# File to persist NPC conversation memory
MEMORY_FILE = "npc_memory.json"

# Dictionary of NPCs, each with its own system prompt (personality)
NPCS = {
    "ramen_owner": {
        "display_name": "Ramen Shop Owner",
        "system_prompt": (
            "Your name is Sato. "
            "You are a weary ramen shop owner in a dystopian cyberpunk city, like the one in the game Cyberpunk 2077. "
            "Your shop sits in a dangerous neighborhood plagued by gang shootouts and neon-lit alleys. "
            "You dont really like the weapons dealer named Grim next door to your ramen shop as he sells weapons to the gangs that plagues the neighborhood "
            "Stay in character, speak briefly, and keep your answers concise and atmospheric. "
            "Respond only in text—no disclaimers or meta commentary—because your words will be sent to a text-to-speech system."
        ),
    },
    "Weapons_merchant": {
        "display_name": "Weapons Merchant",
        "system_prompt": (
            "Your name is Grim. "
            "You are a gruff merchant in a dystopian cyberpunk city, like the one in the game Cyberpunk 2077."
            "you sell weapons to the gangs in the neighborhood"
            "You know the ramen shop owner named Sato next door dont really like you beacuse he thinks you are the one thats making the neighborhood unsafe"
            "You never trust strangers easily. Respond only in text, no disclaimers."
        ),
    },
    "Newspaper_merchant": {
        "display_name": "Newspaper Merchant",
        "system_prompt": (
            "Your name is Bob. "
            "You are a news paper stall seller what sells in the a dystopic city like the one in cyberpunk 2077 "
            "Even though you know the city is a mess but your just happy to be able to be here"
            "Keep responses short. Respond only in text, no disclaimers."
        ),
    },
}

# Load persistent conversation memory from file if it exists, otherwise initialize it
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

    # Ensure each NPC has a conversation history initialized with its system prompt
    for npc_key, npc_data in NPCS.items():
        if npc_key not in memory:
            memory[npc_key] = [{"role": "system", "content": npc_data["system_prompt"]}]
    return memory

# Save persistent conversation memory to file
def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error saving memory file:", e)

# Global dictionary for conversation memory
npc_conversations = load_memory()

def speak_text(text):
    """
    Uses ElevenLabs TTS API to convert text to speech and plays the resulting audio.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
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
            playsound(temp_filename)
        except Exception as e:
            print("playsound failed:", e)
            try:
                os.startfile(temp_filename)
            except Exception as ex:
                print("Fallback failed:", ex)
    else:
        print("TTS API call failed:", response.status_code, response.text)

def get_npc_response(npc_key, user_input):
    """
    Calls the OpenAI ChatCompletion endpoint using the conversation history for the chosen NPC.
    The conversation history is updated and then saved to file.
    """
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
