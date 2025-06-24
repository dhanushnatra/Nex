from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from piper_nex import speak
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()

CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
)

@app.get("/speak")
async def speak_text(text: str):
    speak(text, output_file="response.wav")
    return FileResponse("response.wav", media_type="audio/wav")