import tkinter as tk
import speech_recognition as sr
from threading import Thread
from ai_logic import get_npc_response, speak_text, NPCS  # Import AI functions

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
    
    if tts_var.get():
        speak_text(npc_response)
    
    status_label.config(text="Status: Idle")

def on_speak(npc_key):
    for button in npc_buttons:
        button.config(state=tk.DISABLED)
    
    def run():
        process_conversation(npc_key)
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

tts_var = tk.BooleanVar(value=True)
tts_checkbox = tk.Checkbutton(root, text="Use TTS", variable=tts_var)
tts_checkbox.pack(padx=10, pady=(0, 10))

npc_buttons = []
for npc_key in NPCS:
    btn = tk.Button(root, text=f"Speak to {NPCS[npc_key]['display_name']}", command=lambda key=npc_key: on_speak(key))
    btn.pack(padx=10, pady=5)
    npc_buttons.append(btn)

root.mainloop()
