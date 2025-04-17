import whisper
import sys
import os

# Load Whisper model (specifically medium.en)
model = whisper.load_model("medium.en")
def transcribe_audio():

    # Get audio file path from command line argument
    audio_path = 'server/downloaded_audio.wav'

    # Transcribe
    result = model.transcribe(audio_path)

    # Print just the transcription text
    return result['text']
