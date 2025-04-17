from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from summarizer import summarize_text
from typing import Optional
from deepseek import refine_summary_with_ollama
from transcribe import transcribe_audio

# import os
# from vosk import Model, KaldiRecognizer
# import wave
# import json

app = FastAPI()

# class TextInput(BaseModel):
#     text: str

# @app.post("/summarize")
# async def summarize(input_data: TextInput):

#     if not input_data.text.strip():
#         raise HTTPException(status_code=400, detail="Text input cannot be empty.")
#     summary = summarize_text(input_data.text)
#     return {summary}

class SummaryRequest(BaseModel):
    text: str
    purpose: Optional[str] = "default"

@app.post("/summarize")
async def summarize(req: SummaryRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")
    
    summary = summarize_text(req.text)
    if (req.purpose != "default"):
        refined = refine_summary_with_ollama(summary, req.purpose)
        return { refined }
    else:
        return { summary }

# model = Model("vosk-model-en-us-0.42-gigaspeech")

# @app.post("/transcribe")
# async def transcribe_audio(audio: UploadFile = File(...)):
#     print(audio.filename)
#     if audio.content_type != "audio/wav":
#         raise HTTPException(status_code=400, detail="Invalid file type. Please upload a WAV file.")

#     # Save the uploaded file temporarily
#     temp_file_path = f"temp_{audio.filename}"
#     with open(temp_file_path, "wb") as buffer:
#         buffer.write(await audio.read())

#     # Open the WAV file
#     wf = wave.open(temp_file_path, "rb")
#     if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
#         os.remove(temp_file_path)
#         raise HTTPException(status_code=400, detail="Audio file must be WAV format mono PCM with a sample rate of 16000.")

#     # Initialize the recognizer
#     rec = KaldiRecognizer(model, wf.getframerate())

#     # Process the audio and collect the transcription
#     results = []
#     while True:
#         data = wf.readframes(4000)
#         if len(data) == 0:
#             break
#         if rec.AcceptWaveform(data):
#             result = json.loads(rec.Result())
#             results.append(result.get("text", ""))

#     # Get the final result
#     final_result = json.loads(rec.FinalResult())
#     results.append(final_result.get("text", ""))

#     # Clean up the temporary file
#     wf.close()
#     os.remove(temp_file_path)

#     # Combine all parts of the transcription
#     transcription = ' '.join(results).strip()
#     return {"transcription": transcription}

from youtube_transcript_api import YouTubeTranscriptApi

class VideoIdInput(BaseModel):
    videoId: str
    purpose: Optional[str] = "default"

@app.post("/get-transcript")
async def get_transcript(videoId: VideoIdInput):
    try:
        fetched_transcript = YouTubeTranscriptApi.get_transcript(videoId.videoId)
        text = ' '.join([snippet['text'] for snippet in fetched_transcript])
        
        summary = summarize_text(text)
        if (videoId.purpose != "default"):
            refined = refine_summary_with_ollama(summary, videoId.purpose)
            return { refined }
        else:
            return { summary }
    
    except Exception as e:
        return {"error": str(e)}

@app.get("/audio-transcribe")
async def audio_transcribe():
    try:
        transcribed_text = transcribe_audio()
        return {"transcription": transcribed_text}
    except Exception as e:
        return {"error": str(e)}


        

# audio_file = "downloaded_file.wav"

# @app.get("/transcribe")
# async def transcribe_audio():
#     # Open the audio file
#     wf = wave.open(audio_file, "rb")

#     # Check audio file parameters
#     # if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
#     #     print("Audio file must be WAV format mono PCM with a sample rate of 16000 Hz.")
#     #     wf.close()
#     #     exit(1)

#     print("Starting transcription...")
#     # Initialize the recognizer
#     rec = KaldiRecognizer(model, wf.getframerate())

#     # Process the audio file
#     results = []
#     while True:
#         data = wf.readframes(4000)
#         if len(data) == 0:
#             break
#         if rec.AcceptWaveform(data):
#             result = json.loads(rec.Result())
#             results.append(result.get("text", ""))

#     # Get the final result
#     final_result = json.loads(rec.FinalResult())
#     results.append(final_result.get("text", ""))

#     # Close the audio file
#     wf.close()

#     # Combine and print the transcription
#     transcription = ' '.join(results).strip()
#     print("Transcription:")
#     print(transcription)