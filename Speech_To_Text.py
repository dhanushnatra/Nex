import os
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog

import whisper

# Supported Whisper models
WHISPER_MODELS = ["tiny", "small", "base", "medium", "large"]

# Video file extensions we’ll treat as “needs audio extraction”
VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm"]


def is_video_file(path):
    extension = os.path.splitext(path)[1].lower()
    return extension in VIDEO_EXTENSIONS


def find_ffmpeg():
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    print("Error: FFmpeg not found. Please install FFmpeg and add it to your PATH.", file=sys.stderr)
    sys.exit(1)


def extract_audio(video_path, ffmpeg_path):
    # Create a temporary WAV filename
    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wav_path = temp_wav.name
    temp_wav.close()

    command = [
        ffmpeg_path,
        "-i",
        video_path,
        "-vn",               # drop the video stream
        "-acodec",
        "pcm_s16le",         # 16-bit PCM WAV
        "-ar",
        "16000",             # 16 kHz sample rate
        "-ac",
        "1",                 # mono
        wav_path,
        "-y",                # overwrite if exists
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        # Clean up the temp WAV if something goes wrong
        if os.path.exists(wav_path):
            os.unlink(wav_path)
        print("Error: FFmpeg failed to extract audio.", file=sys.stderr)
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)

    return wav_path


def seconds_to_srt_timestamp(seconds):
    milliseconds = int(seconds * 1000)
    hours = milliseconds // 3_600_000
    minutes = (milliseconds % 3_600_000) // 60_000
    secs = (milliseconds % 60_000) // 1000
    millis = milliseconds % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def seconds_to_vtt_timestamp(seconds):
    milliseconds = int(seconds * 1000)
    hours = milliseconds // 3_600_000
    minutes = (milliseconds % 3_600_000) // 60_000
    secs = (milliseconds % 60_000) // 1000
    millis = milliseconds % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def save_txt(file_stem, text):
    out_path = f"{file_stem}_transcript.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    return out_path


def save_srt(file_stem, segments):
    out_path = f"{file_stem}_transcript.srt"
    with open(out_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start_ts = seconds_to_srt_timestamp(seg["start"])
            end_ts = seconds_to_srt_timestamp(seg["end"])
            text = seg["text"].strip()
            f.write(f"{i}\n")
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{text}\n\n")
    return out_path


def save_vtt(file_stem, segments):
    out_path = f"{file_stem}_transcript.vtt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for seg in segments:
            start_ts = seconds_to_vtt_timestamp(seg["start"])
            end_ts = seconds_to_vtt_timestamp(seg["end"])
            text = seg["text"].strip()
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{text}\n\n")
    return out_path


def choose_whisper_model(default="base"):
    models_str = ", ".join(WHISPER_MODELS)
    choice = input(f"Choose Whisper model ({models_str}) [default: {default}]: ").strip().lower()
    if choice in WHISPER_MODELS:
        return choice
    print(f"No valid model chosen. Using '{default}'.")
    return default


def select_file_with_dialog():
    root = tk.Tk()
    root.withdraw()  
    filetypes = [
        ("Audio or Video", "*.wav *.mp3 *.m4a *.mp4 *.mov *.avi *.mkv *.flv *.wmv *.webm"),
        ("All files", "*.*"),
    ]
    selected = filedialog.askopenfilename(title="Select an audio or video file", filetypes=filetypes)
    root.destroy()

    if not selected:
        print("No file was selected. Exiting.", file=sys.stderr)
        sys.exit(1)

    return selected


def main():
    # 1) Let the user pick a file using a dialog box
    file_path = select_file_with_dialog()
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)

    # 2) If it’s a video, use FFmpeg to extract a WAV first
    needs_cleanup = False
    if is_video_file(file_path):
        print("Video detected. Locating ffmpeg…")
        ffmpeg_path = find_ffmpeg()
        print(f"Using ffmpeg at: {ffmpeg_path}")
        print("Extracting audio to temporary WAV…")
        audio_path = extract_audio(file_path, ffmpeg_path)
        needs_cleanup = True
    else:
        # Otherwise, it’s already an audio file
        audio_path = file_path

    # 3) Let the user pick which Whisper model to load
    model_name = choose_whisper_model(default="base")

    # 4) Load Whisper and transcribe. We ask for full "segments" to build subtitles.
    print(f"\nLoading Whisper model '{model_name}'…")
    model = whisper.load_model(model_name)

    print(f"Transcribing '{audio_path}'… (this may take a while)")
    result = model.transcribe(audio_path)
    transcript_text = result.get("text", "").strip()
    segments = result.get("segments", [])

    print("\n" + "=" * 60)
    print("🎙️  Transcript  (plain text)  🎙️")
    print(transcript_text)
    print("=" * 60 + "\n")

    # 5) Clean up the temporary WAV if we created one
    if needs_cleanup and os.path.exists(audio_path):
        os.unlink(audio_path)

    # 6) Save outputs: .txt, .srt, and .vtt
    directory = os.path.dirname(file_path)
    stem = os.path.splitext(os.path.basename(file_path))[0]
    os.chdir(directory)  # save files alongside the original

    # Save plain .txt
    txt_path = save_txt(stem, transcript_text)
    print(f"Saved plain text to: {txt_path}")

    # If Whisper provided segments, save .srt and .vtt
    if segments:
        srt_path = save_srt(stem, segments)
        print(f"Saved SRT subtitles to: {srt_path}")

        vtt_path = save_vtt(stem, segments)
        print(f"Saved VTT subtitles to: {vtt_path}")
    else:
        print("No segment timestamps available; skipping .srt/.vtt.")

    print("\nDone.")


if __name__ == "__main__":
    main()
