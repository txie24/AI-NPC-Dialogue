# UI.py
import tkinter as tk
import speech_recognition as sr
from threading import Thread
from ai_logic import get_npc_response, speak_text, NPCS
import threading
import game  # 用于同步对话到Pygame对话日志

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

def get_voice_input():
    """
    一次性录音 5~8 秒，阻塞等待结果，结束后再进行 GPT。
    """
    r = sr.Recognizer()
    status_label.config(text="Status: Listening...")
    try:
        with sr.Microphone() as source:
            conversation_text.config(state=tk.NORMAL)
            conversation_text.insert(tk.END, "Listening...\n")
            conversation_text.see(tk.END)
            conversation_text.config(state=tk.DISABLED)

            audio = r.listen(source, timeout=5, phrase_time_limit=8)
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

def speak_text_async(text):
    threading.Thread(target=speak_text, args=(text,)).start()

def process_conversation(npc_key):
    """
    单轮对话: 录音 -> GPT -> (可选)TTS -> 结束
    """
    user_input = get_voice_input()
    npc_name = NPCS[npc_key]["display_name"]

    # 如果识别失败，就不调用GPT
    error_messages = [
        "Listening timed out, please try again.",
        "Sorry, I did not catch that.",
        "Speech service is unavailable."
    ]
    if user_input in error_messages or user_input.startswith("Error:"):
        conversation_text.config(state=tk.NORMAL)
        conversation_text.insert(tk.END, f"[SYSTEM]: {user_input}\n\n")
        conversation_text.see(tk.END)
        conversation_text.config(state=tk.DISABLED)
        game.add_chat_message(f"[SYSTEM]: {user_input}")
        game.on_dialog_end()
        return

    # 显示用户输入
    conversation_text.config(state=tk.NORMAL)
    conversation_text.insert(tk.END, f"You to {npc_name}: {user_input}\n")
    conversation_text.see(tk.END)
    conversation_text.config(state=tk.DISABLED)
    game.add_chat_message(f"You to {npc_name}: {user_input}")

    status_label.config(text="Status: Processing...")
    npc_response = get_npc_response(npc_key, user_input)

    # 显示 GPT 回复
    conversation_text.config(state=tk.NORMAL)
    conversation_text.insert(tk.END, f"{npc_name}: {npc_response}\n\n")
    conversation_text.see(tk.END)
    conversation_text.config(state=tk.DISABLED)
    game.add_chat_message(f"{npc_name}: {npc_response}")

    # 可选TTS
    if tts_var.get():
        speak_text_async(npc_response)
    
    status_label.config(text="Status: Idle")
    
    game.on_dialog_end()

def on_speak(npc_key):
    """
    UI上点击“Speak to XXX”按钮时的回调: 只做一次对话
    """
    # 暂时禁用按钮，避免用户重复点击
    for button in npc_buttons:
        button.config(state=tk.DISABLED)
    
    def run():
        process_conversation(npc_key)
        for button in npc_buttons:
            button.config(state=tk.NORMAL)
    Thread(target=run).start()

# 生成UI按钮: “Speak to Ramen Shop Owner”等
for key in NPCS:
    btn = tk.Button(root, text=f"Speak to {NPCS[key]['display_name']}",
                    command=lambda npc_key=key: on_speak(npc_key))
    btn.pack(padx=10, pady=5)
    npc_buttons.append(btn)

def trigger_conversation_from_game(npc_key):
    """
    给 game.py 调用的函数:
    当 Pygame 检测到碰撞并按下 SPACE 时，会调用这个函数。
    """
    def safe_call():
        process_conversation(npc_key)
    root.after(0, safe_call)
