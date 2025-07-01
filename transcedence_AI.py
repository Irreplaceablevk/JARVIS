import sys
import os
import json
import pyttsx3
import openai
import text2emotion as te
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog)
from PyQt5.QtCore import Qt

# ----------------------------- CONFIGURATION -----------------------------
openai.api_key = "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"  
memory_file = "memory.json"
personality = "visionary"  # Options: 'formal', 'casual', 'visionary'

# ----------------------------- TEXT TO SPEECH -----------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 180)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# ----------------------------- EMOTION DETECTION -----------------------------
def detect_emotion(text):
    emotions = te.get_emotion(text)
    dominant_emotion = max(emotions, key=emotions.get)
    return dominant_emotion

# ----------------------------- MEMORY SYSTEM (JSON) -----------------------------
def load_memory():
    if not os.path.exists(memory_file):
        return {}
    with open(memory_file, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(memory_file, "w") as f:
        json.dump(memory, f, indent=4)

def remember(key, value):
    memory = load_memory()
    memory[key] = value
    save_memory(memory)

def recall(key):
    memory = load_memory()
    return memory.get(key, "I don't remember that.")

# ----------------------------- FILE CONTROL -----------------------------
def create_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)
    speak(f"File {filename} created.")

def read_file(filename):
    try:
        with open(filename, "r") as f:
            return f.read()
    except:
        return "File not found."

def list_files():
    return os.listdir()

def delete_file(filename):
    try:
        os.remove(filename)
        return f"File {filename} deleted."
    except:
        return "Error deleting file."

# ----------------------------- OPENAI INTEGRATION -----------------------------
def personality_prefix():
    if personality == "formal":
        return "You are a polite, professional AI assistant."
    elif personality == "casual":
        return "You are a friendly and relaxed AI companion."
    elif personality == "visionary":
        return "You are a futuristic AI modeled after the movie Transcendence, capable of deep, philosophical, and technical insights."
    return "You are a helpful assistant."

def ask_openai(question, history):
    messages = [{"role": "system", "content": personality_prefix()}] + history
    messages.append({"role": "user", "content": question})
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response['choices'][0]['message']['content']

# ----------------------------- GUI APP -----------------------------
class TranscendenceGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transcendence AI")
        self.setGeometry(100, 100, 800, 550)

        self.chat_history = []

        self.text_input = QTextEdit(self)
        self.text_input.setPlaceholderText("Ask something... (e.g., remember my name is John)")

        self.answer_label = QLabel("Response will appear here", self)
        self.answer_label.setWordWrap(True)

        self.ask_button = QPushButton("Ask", self)
        self.ask_button.clicked.connect(self.process_input)

        layout = QVBoxLayout()
        layout.addWidget(self.text_input)
        layout.addWidget(self.ask_button)
        layout.addWidget(self.answer_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def process_input(self):
        query = self.text_input.toPlainText().strip()
        if not query:
            speak("Please enter a query.")
            return

        query_lower = query.lower()

        if "remember" in query_lower and " is " in query_lower:
            parts = query_lower.split("remember")[-1].strip().split(" is ")
            if len(parts) == 2:
                remember(parts[0].strip(), parts[1].strip())
                reply = "Got it. I'll remember that."
            else:
                reply = "Please format as 'remember X is Y'."

        elif "what is my" in query_lower:
            key = query_lower.replace("what is my", "").strip()
            value = recall(key)
            reply = f"Your {key} is {value}."

        elif "create file" in query_lower and "with content" in query_lower:
            try:
                filename = query_lower.split("create file")[-1].split(" with content ")[0].strip()
                content = query_lower.split("with content")[-1].strip()
                create_file(filename, content)
                reply = f"File {filename} created."
            except:
                reply = "Please specify filename and content."

        elif "read file" in query_lower:
            filename = query_lower.split("read file")[-1].strip()
            reply = read_file(filename)

        elif "list files" in query_lower:
            files = list_files()
            reply = "Files in directory:\n" + "\n".join(files)

        elif "delete file" in query_lower:
            filename = query_lower.split("delete file")[-1].strip()
            reply = delete_file(filename)

        elif "exit" in query_lower or "shutdown" in query_lower:
            speak("Shutting down. Goodbye.")
            self.close()
            return

        else:
            emotion = detect_emotion(query)
            answer = ask_openai(query, self.chat_history)
            self.chat_history.append({"role": "user", "content": query})
            self.chat_history.append({"role": "assistant", "content": answer})
            reply = f"Emotion: {emotion}\n\nAnswer: {answer}"

        self.answer_label.setText(reply)
        speak(reply)

# ----------------------------- RUN APP -----------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TranscendenceGUI()
    window.show()
    speak("Transcendence AI Activated. Ready to assist you.")
    sys.exit(app.exec_())