import tkinter as tk
import speech_recognition as sr
from threading import Thread
import requests
import tempfile
import os
from playsound import playsound
import openai

# --- Configuration for ElevenLabs TTS ---
ELEVENLABS_API_KEY = "sk_3f2270c1a206d6a3c0d0c821283fb004bea27d73e2aeb810"  # Your API key
VOICE_ID = "2EiwWnXFnvU5JabPnv8n"  # Replace with your desired voice ID from ElevenLabs
# ----------------------------------------
    
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
        # Save the audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(response.content)
            temp_filename = f.name
        try:
            # Attempt to play using playsound
            playsound(temp_filename)
        except Exception as e:
            print("playsound failed:", e)
            # Fallback: use os.startfile (Windows only)
            try:
                os.startfile(temp_filename)
            except Exception as ex:
                print("Fallback failed:", ex)
    else:
        print("TTS API call failed:", response.status_code, response.text)

def get_npc_response(user_input):
    # 设置你的 OpenAI API 密钥
    openai.api_key = "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"
    try:
        response = openai.ChatCompletion.create(
            model="o3-mini",  # 或者其他你选择的模型
            messages=[
                {"role": "system", "content": "You're a helpful AI assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        # 提取 GPT 的回复文本
        answer = response["choices"][0]["message"]["content"]
        return answer
    except Exception as e:
        print("Error calling GPT API.", e)
        return "Sorry, I can't generate an answer right now."

def get_voice_input():
    """
    Captures voice input using speech_recognition.
    """
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
    """
    Processes the conversation: captures input, displays it, echoes the input,
    and then uses TTS to speak the echoed response.
    """
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
    """
    Runs the conversation processing in a separate thread to keep the UI responsive.
    """
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
