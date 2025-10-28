#Step1: Setup Audio recorder (ffmpeg & portaudio)
# ffmpeg, portaudio, pyaudio
# voice_of_the_patient.py

from dotenv import load_dotenv
load_dotenv()

import logging
import os
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from groq import Groq

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- FFmpeg paths ---
AudioSegment.ffmpeg = r"ffmpeg.exe"
AudioSegment.ffprobe = r"ffprobe.exe"

# --- Step 1: Record Audio ---
def record_audio(file_path, timeout=10, phrase_time_limit=10):
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Start speaking now...")

            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete.")

            wav_data = audio_data.get_wav_data()
            logging.info(f"Captured audio data size: {len(wav_data)} bytes")

            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")

            if os.path.exists(file_path):
                logging.info(f" Audio successfully saved to: {os.path.abspath(file_path)}")
            else:
                logging.error(" Export failed — file not created.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

# --- Define audio file path ---
audio_filepath = r"Ai chatbot\patient_voice_test_for_patient.mp3"

# --- Record user voice ---
record_audio(file_path=audio_filepath)

# --- Step 2: Speech-to-Text using Groq Whisper model ---
def transcribe_with_groq(stt_model, audio_filepath, api_key):
    try:
        client = Groq(api_key=api_key)

        with open(audio_filepath, "rb") as audio_file:
            logging.info("Transcribing audio with Groq Whisper model...")
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en"
            )

        logging.info(" Transcription complete.")
        return transcription.text

    except Exception as e:
        logging.error(f"Transcription failed: {e}")
        return None

# --- Provide your API key ---
GROQ_API_KEY = "My API_KEY"  # Replace with your actual API key
stt_model = "whisper-large-v3"

# --- Transcribe the recorded file ---
if os.path.exists(audio_filepath):
    result_text = transcribe_with_groq(stt_model, audio_filepath, GROQ_API_KEY)
    if result_text:
        print("\nTranscribed Text:\n")
        print(result_text)
    else:
        print("\n No text transcribed. Check logs for details.")
else:
    print(" Audio file not found — recording step might have failed.")
