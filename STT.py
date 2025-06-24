import whisper

model = whisper.load_model("base.en")


def get_text(audio_file: str) -> str:
    result =  model.transcribe(audio_file)
    return result["text"]

