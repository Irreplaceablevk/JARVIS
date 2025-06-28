import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wolframalpha
import wikipedia
import cv2
import numpy as np
import requests

# Initialize AI Voice
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Change index for different voices

def speak(text):
    """Speaks the given text."""
    engine.say(text)
    engine.runAndWait()

def take_command():
    """Listens to microphone input and returns text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            command = r.recognize_google(audio, language='en-in')
            print(f"Command: {command}\n")
        except:
            command = ""
        return command.lower()

def open_camera():
    """Opens webcam with face detection."""
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
        
        cv2.imshow('JARVIS Surveillance', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

def main():
    speak("Initializing JARVIS. How can I help you today?")
    
    while True:
        command = take_command()
        
        if 'hello' in command:
            speak("Hello, Sir. How can I assist you?")
        
        elif 'time' in command:
            now = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"Current time is {now}")
        
        elif 'open youtube' in command:
            webbrowser.open("https://youtube.com")
            speak("Opening YouTube")
        
        elif 'open camera' in command:
            speak("Activating surveillance mode")
            open_camera()
        
        elif 'calculate' in command or 'what is' in command:
            client = wolframalpha.Client("YOUR_WOLFRAM_API_KEY")
            try:
                res = client.query(command)
                speak(next(res.results).text)
            except:
                speak("I couldn't compute that")
        
        elif 'search wikipedia' in command:
            speak("Searching Wikipedia...")
            query = command.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak(f"According to Wikipedia: {results}")
        
        elif 'exit' in command:
            speak("Shutting down. Goodbye, Sir.")
            break

main()
