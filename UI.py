# UI.py
import tkinter as tk
import speech_recognition as sr
from threading import Thread
from ai_logic import get_npc_response, speak_text, NPCS
import threading
import game  # 导入 game, 以便调用 add_chat_message

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

###################################################
# 新增：用来标记当前对话是否被“Esc”或其他操作取消
conversation_cancelled = False

def cancel_current_conversation():
    """
    当游戏里按下Esc (或UI里某个按钮) 时，会调用此函数。
    标记当前对话取消, 并在UI与Pygame显示系统消息。
    """
    global conversation_cancelled
    conversation_cancelled = True
    status_label.config(text="Status: Conversation Cancelled")
    # 在Tkinter对话框里显示提示
    conversation_text.config(state=tk.NORMAL)
    conversation_text.insert(tk.END, "[SYSTEM]: Conversation cancelled by user.\n\n")
    conversation_text.see(tk.END)
    conversation_text.config(state=tk.DISABLED)
    # 在Pygame对话日志显示提示
    game.add_chat_message("[SYSTEM]: Conversation cancelled.")

###################################################

def get_voice_input():
    global conversation_cancelled
    conversation_cancelled = False  # 每次对话开始前重置

    r = sr.Recognizer()
    status_label.config(text="Status: Listening...")
    try:
        with sr.Microphone() as source:
            conversation_text.config(state=tk.NORMAL)
            conversation_text.insert(tk.END, "Listening...\n")
            conversation_text.see(tk.END)
            conversation_text.config(state=tk.DISABLED)

            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            if conversation_cancelled:
                # 如果用户在录音过程中按下Esc，就不解析了
                return "[CANCELLED]"
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
        # 如果录音结束后发现对话取消，也可以这里检查
        if conversation_cancelled:
            status_label.config(text="Status: Conversation Cancelled")
        else:
            status_label.config(text="Status: Idle")

def speak_text_async(text):
    # 如果对话被取消，就不再播TTS
    if conversation_cancelled:
        return
    threading.Thread(target=speak_text, args=(text,)).start()

def process_conversation(npc_key):
    global conversation_cancelled
    conversation_cancelled = False  # 对话开始，先重置标记

    user_input = get_voice_input()
    npc_name = NPCS[npc_key]["display_name"]

    # 如果在录音阶段就被取消了，会返回 "[CANCELLED]"
    if user_input == "[CANCELLED]":
        return

    error_messages = [
        "Listening timed out, please try again.",
        "Sorry, I did not catch that.",
        "Speech service is unavailable."
    ]
    if user_input in error_messages or user_input.startswith("Error:"):
        # 显示错误
        conversation_text.config(state=tk.NORMAL)
        conversation_text.insert(tk.END, f"[SYSTEM]: {user_input}\n\n")
        conversation_text.see(tk.END)
        conversation_text.config(state=tk.DISABLED)
        game.add_chat_message(f"[SYSTEM]: {user_input}")
        return

    # 如果此时用户按 Esc，也不要再处理
    if conversation_cancelled:
        return

    # 显示用户输入
    conversation_text.config(state=tk.NORMAL)
    conversation_text.insert(tk.END, f"You to {npc_name}: {user_input}\n")
    conversation_text.see(tk.END)
    conversation_text.config(state=tk.DISABLED)
    game.add_chat_message(f"You to {npc_name}: {user_input}")

    status_label.config(text="Status: Processing...")

    # 调用 GPT
    if conversation_cancelled:
        return
    npc_response = get_npc_response(npc_key, user_input)

    if conversation_cancelled:
        return

    # 显示 GPT 回复
    conversation_text.config(state=tk.NORMAL)
    conversation_text.insert(tk.END, f"{npc_name}: {npc_response}\n\n")
    conversation_text.see(tk.END)
    conversation_text.config(state=tk.DISABLED)
    game.add_chat_message(f"{npc_name}: {npc_response}")

    if tts_var.get():
        # 如果对话被取消，就不再播TTS
        if not conversation_cancelled:
            speak_text_async(npc_response)
    
    status_label.config(text="Status: Idle")

def on_speak(npc_key):
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
    def safe_call():
        process_conversation(npc_key)
    root.after(0, safe_call)
