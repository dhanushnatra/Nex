from requests import get, post
from typing import Union
import re
from music_player import playPause,stop

messages=[]

def ask_ai(q) -> str:
    url = "http://localhost:11434/api/generate"
    response = post(url, json={"model":"Optimus","prompt":q, "stream": False })
    if response.status_code == 200:
        data = response.json()
        return data["response"]
    return "Sorry Boss . Ollama backend is not working Shall i start it"

def start_ollama():
    from os import system
    system("ollama serve")

def think(question: str) -> str:
    question=question.lower()
    if re.search(r'\b(music|song)\b', question):
        if re.search(r'\b(play|pause)\b', question):
            return playPause()
        elif re.search(r'\b(stop)\b',question):
            return stop()
    elif re.search(r'\b(weather|forecast)\b', question):
        return "Fetching weather information..."
    # Fallback for unrecognized tasks
    return ask_ai(question)