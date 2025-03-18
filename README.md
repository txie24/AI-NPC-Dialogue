# AI NPC Dialogue System Demo

This project is a demonstration of an AI-driven NPC dialogue system built in Python. It uses a simple Tkinter UI for interaction, leverages the SpeechRecognition library for capturing voice input, and serves as a basis for integrating advanced AI dialogue systems (e.g., GPT) later on.

## Update Log
Mar 17
- Now has 3 NPCs where has long term memories Where if you restart the program it will still remeber the conversation from the last runtime.
- Now has 3 .py files **Run.py(main run program)** **ai_logic.py(where all the APIs and logics are)** **UI.py(where the UI settings are)**.
- New toggle to turn off TTS to conserve TTS Tokens in the UI menu.
- **npc_memory.json** (dont edit this files unless you want to reset the memory).
- Now has a new **game.py** which is a side scroller game demo to show the different AI NPCs
- New **Assets folder** which has all of the new game assets in there

## TODOs
- Incorporate the game and the Side scroller game demo, so each npc corresponds to the correct AI NPC assistant in **ai_logic.py**
- Fix the Voice latency including both input and output

## Features

- **Voice Input:** Uses the SpeechRecognition library to capture and process spoken user input.
- **Simple UI:** A basic Tkinter interface for interacting with the AI NPC.
- **Modular Design:** Easily integrate with advanced AI models and TTS (text-to-speech) systems in the future.

## Requirements

- Python 3.6+
- [SpeechRecognition]
- [pipwin]
- [PyAudio]
- [elevenlabs]
- [OpenAI]
- [pygame]

## Installation

Install these plugins to set up the project:

- pip install pipwin
- python -m pip install pyaudio
- pip install SpeechRecognition
- pip install SpeechRecognition playsound requests
- pip install elevenlabs
- pip install openai==0.28
- pip install pygame
