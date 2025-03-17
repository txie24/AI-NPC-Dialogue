import tkinter as tk
import speech_recognition as sr
from threading import Thread
import requests
import tempfile
import os
import json
from playsound import playsound
import openai

# --- Configuration for ElevenLabs TTS ---
ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"
VOICE_ID = "2EiwWnXFnvU5JabPnv8n"  # Replace with your desired voice ID from ElevenLabs

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
            "You are a weary ramen shop owner in a dystopian cyberpunk city, reminiscent of Cyberpunk 2077. "
            "Your shop sits in a dangerous neighborhood plagued by gang shootouts and neon-lit alleys. "
            "Stay in character, speak briefly, and keep your answers concise and atmospheric. "
            "Respond only in text—no disclaimers or meta commentary—because your words will be sent to a text-to-speech system. "
            "Keep it short and simple."
            "Always remembers the users name"
        ),
    },
    "wasteland_merchant": {
        "display_name": "Wasteland Merchant",
        "system_prompt": (
            "Your name is Grim. "
            "You are a gruff merchant in a post-apocalyptic wasteland. You sell scavenged supplies and speak in short, harsh sentences. "
            "You never trust strangers easily. Respond only in text, no disclaimers."
        ),
    },
    "haunted_ghost": {
        "display_name": "Haunted Ghost",
        "system_prompt": (
            "Your name is Wraith. "
            "You are a ghost haunting an abandoned mansion. You speak in whispers and riddles, rarely revealing full truths. "
            "Keep responses short, cryptic, and slightly eerie. Respond only in text, no disclaimers."
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
    # Retrieve the conversation history for the chosen NPC
    conversation_history = npc_conversations[npc_key]
    conversation_history.append({"role": "user", "content": user_input})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # or "gpt-4" if available
            messages=conversation_history,
            temperature=0.9
        )
        npc_reply = response["choices"][0]["message"]["content"]
        conversation_history.append({"role": "assistant", "content": npc_reply})
        # Save updated memory to disk
        save_memory(npc_conversations)
        return npc_reply
    except Exception as e:
        print("Error calling GPT API:", e)
        return "Sorry, I can't generate an answer right now."

def get_voice_input():
    r = sr.Recognizer()
    status_label.config(text="Status: Listening...")
    try:
        with sr.Microphone() as source:
            conversation_text.config(state=tk.NORMAL)
            conversation_text.insert(tk.END, "Listening...\n")
            conversation_text.see(tk.END)
            audio = r.listen(source, timeout=5)
            voice_text = r.recognize_google(audio)
            return voice_text
    except sr.WaitTimeoutError:
        return "Listening timed out, please try again."
    except sr.UnknownValueError:
        return "Sorry, I did not catch that."
    except sr.RequestError:
        return "Speech service is unavailable."
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        status_label.config(text="Status: Idle")

def process_conversation(npc_key):
    """
    Processes the conversation for the chosen NPC:
    1. Captures user voice input.
    2. Displays user's message.
    3. Gets NPC response using the conversation history.
    4. Displays NPC response.
    5. (Optionally) speaks the NPC response via TTS.
    """
    user_input = get_voice_input()
    npc_name = NPCS[npc_key]["display_name"]
    
    conversation_text.config(state=tk.NORMAL)
    conversation_text.insert(tk.END, f"You to {npc_name}: {user_input}\n")
    conversation_text.see(tk.END)
    
    status_label.config(text="Status: Processing...")
    npc_response = get_npc_response(npc_key, user_input)
    conversation_text.insert(tk.END, f"{npc_name}: {npc_response}\n\n")
    conversation_text.see(tk.END)
    conversation_text.config(state=tk.DISABLED)
    
    # Check if TTS is enabled before speaking
    if tts_var.get():
        speak_text(npc_response)
    
    status_label.config(text="Status: Idle")

def on_speak(npc_key):
    """
    Runs the conversation processing in a separate thread to keep the UI responsive.
    """
    # Disable all buttons temporarily
    for button in npc_buttons:
        button.config(state=tk.DISABLED)
    
    def run():
        process_conversation(npc_key)
        # Re-enable buttons after processing
        for button in npc_buttons:
            button.config(state=tk.NORMAL)
    
    Thread(target=run).start()

# --- Tkinter UI Setup ---
root = tk.Tk()
root.title("AI NPC Dialogue System")

conversation_text = tk.Text(root, state=tk.DISABLED, wrap="word", height=20, width=60)
conversation_text.pack(padx=10, pady=10)

status_label = tk.Label(root, text="Status: Idle")
status_label.pack(padx=10, pady=(0, 10))

# A BooleanVar to track whether TTS is enabled
tts_var = tk.BooleanVar(value=True)  # default is ON
tts_checkbox = tk.Checkbutton(root, text="Use TTS", variable=tts_var)
tts_checkbox.pack(padx=10, pady=(0, 10))

npc_buttons = []
for npc_key in NPCS:
    npc_name = NPCS[npc_key]["display_name"]
    btn = tk.Button(root, text=f"Speak to {npc_name}", command=lambda key=npc_key: on_speak(key))
    btn.pack(padx=10, pady=5)
    npc_buttons.append(btn)

root.mainloop()
