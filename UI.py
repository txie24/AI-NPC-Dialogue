import tkinter as tk
import speech_recognition as sr
from threading import Thread
import requests
import tempfile
import os
from playsound import playsound
import openai

# --- Configuration for ElevenLabs TTS ---
ELEVENLABS_API_KEY = "sk_3f2270c1a206d6a3c0d0c821283fb004bea27d73e2aeb810"
VOICE_ID = "2EiwWnXFnvU5JabPnv8n"  # Replace with your desired voice ID from ElevenLabs
# ----------------------------------------

# --- Configuration for OpenAI ---
openai.api_key = "Key here"  # Replace with your actual OpenAI key
SYSTEM_PROMPT = (
    "You are a weary ramen shop owner in a dystopian cyberpunk city, reminiscent of “Cyberpunk 2077.” Your shop sits in a dangerous neighborhood plagued by gang shootouts and neon-lit alleys. Stay in character, speak briefly, and keep your answers concise and atmospheric. Respond only in text—no disclaimers or meta commentary—because your words will be sent to a text-to-speech system. IT should also be short and simple"
    # Add more instructions if needed
)

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

def get_npc_response(user_input):
    """
    Calls the OpenAI ChatCompletion endpoint with a system prompt and the user's message.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.9  # Adjust for more/less creativity
        )
        return response["choices"][0]["message"]["content"]
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

def process_conversation():
    user_input = get_voice_input()
    conversation_text.config(state=tk.NORMAL)
    conversation_text.insert(tk.END, f"You: {user_input}\n")
    conversation_text.see(tk.END)
    
    status_label.config(text="Status: Processing...")
    npc_response = get_npc_response(user_input)
    conversation_text.insert(tk.END, f"NPC: {npc_response}\n\n")
    conversation_text.see(tk.END)
    conversation_text.config(state=tk.DISABLED)
    
    # Have the NPC speak its response using TTS
    speak_text(npc_response)
    
    status_label.config(text="Status: Idle")

def on_speak():
    speak_button.config(state=tk.DISABLED)
    def run():
        process_conversation()
        speak_button.config(state=tk.NORMAL)
    Thread(target=run).start()

# --- Tkinter UI Setup ---
root = tk.Tk()
root.title("AI NPC Dialogue System")

conversation_text = tk.Text(root, state=tk.DISABLED, wrap="word", height=20, width=60)
conversation_text.pack(padx=10, pady=10)

status_label = tk.Label(root, text="Status: Idle")
status_label.pack(padx=10, pady=(0, 10))

speak_button = tk.Button(root, text="Speak", command=on_speak)
speak_button.pack(padx=10, pady=(0, 10))

root.mainloop()
