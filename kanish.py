import speech_recognition as sr
import pyttsx3
import requests
import json
import threading
import sys

# Global flag to control program execution
exit_flag = False

def get_local_ai_response(prompt):
    url = "http://localhost:11434/api/generate"
    data = {"model": "mistral", "prompt": prompt, "stream": False}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        response_json = response.json()
        return response_json.get("response", "I don't know the answer.").strip()
    return "Error: Could not connect to the local AI model. Make sure Ollama is running."

def speak(text):
    global exit_flag
    if exit_flag:  # Stop speaking if the exit flag is set
        return
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    global exit_flag
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        while not exit_flag:  # Keep listening until the exit flag is set
            try:
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio)
                print("You said:", text)
                if text.lower() == "exit":  # Exit if the user says "exit"
                    print("Goodbye!")
                    speak("Goodbye!")
                    exit_flag = True
                    break
                response = get_local_ai_response(text)
                print("Shadow:", response)
                speak(response)
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
            except sr.RequestError:
                print("Could not request results. Check your internet connection.")

def shadow():
    global exit_flag
    print("Welcome to Shadow, your AI assistant. Speak your message. Say 'exit' to quit.")
    try:
        listen_thread = threading.Thread(target=listen)
        listen_thread.start()
        listen_thread.join()  # Wait for the thread to finish
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        exit_flag = True  # Ensure the program exits gracefully
        sys.exit(0)

if __name__ == "__main__":
    shadow()