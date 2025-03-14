import tkinter as tk
import speech_recognition as sr
from threading import Thread

# Placeholder for your AI response function.
def get_npc_response(user_input):
    # For demonstration, simply echo the input with a message.
    return f"I heard you say: '{user_input}'"

# Function to capture voice input using speech_recognition
def get_voice_input():
    r = sr.Recognizer()
    # Update status label to indicate that listening has started.
    status_label.config(text="Status: Listening...")
    try:
        with sr.Microphone() as source:
            conversation_text.config(state=tk.NORMAL)
            conversation_text.insert(tk.END, "Listening...\n")
            conversation_text.see(tk.END)
            # Listen for voice input (5-second timeout)
            audio = r.listen(source, timeout=5)
            # Recognize using Google's speech recognition (requires internet)
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
        # Reset status after listening attempt is complete.
        status_label.config(text="Status: Idle")

# Function to process the conversation
def process_conversation():
    # Capture the user's voice input
    user_input = get_voice_input()
    
    conversation_text.config(state=tk.NORMAL)
    conversation_text.insert(tk.END, f"You: {user_input}\n")
    conversation_text.see(tk.END)
    
    # Update status label to show that the system is processing
    status_label.config(text="Status: Processing...")
    
    # Get the NPC's response (replace with your AI code)
    npc_response = get_npc_response(user_input)
    
    # Display the NPC's response
    conversation_text.insert(tk.END, f"NPC: {npc_response}\n\n")
    conversation_text.see(tk.END)
    conversation_text.config(state=tk.DISABLED)
    
    # Reset status to idle after processing is complete
    status_label.config(text="Status: Idle")

# Function to run conversation processing in a separate thread (to avoid UI freezing)
def on_speak():
    # Optionally disable the button while processing to prevent duplicate clicks
    speak_button.config(state=tk.DISABLED)
    def run():
        process_conversation()
        speak_button.config(state=tk.NORMAL)
    Thread(target=run).start()

# Set up the main Tkinter window
root = tk.Tk()
root.title("AI NPC Dialogue System")

# Create a text widget to display conversation
conversation_text = tk.Text(root, state=tk.DISABLED, wrap="word", height=20, width=60)
conversation_text.pack(padx=10, pady=10)

# Create a label to display the current status
status_label = tk.Label(root, text="Status: Idle")
status_label.pack(padx=10, pady=(0, 10))

# Create a button to trigger voice input
speak_button = tk.Button(root, text="Speak", command=on_speak)
speak_button.pack(padx=10, pady=(0, 10))

# Start the Tkinter event loop
root.mainloop()
