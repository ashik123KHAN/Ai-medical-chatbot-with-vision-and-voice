# gradio_app.py
# VoiceBot UI with Gradio
# ------------------------------------------------------

import os
import gradio as gr
from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import save_tts, play_audio



GROQ_API_KEY = "your_api_key_here"  # Replace with your actual API key

SYSTEM_PROMPT = (
    "You have to act as a professional doctor, I know you are not but this is for learning purposes. "
    "What's in this image? Do you find anything wrong with it medically? "
    "If you make a differential, suggest some remedies for them. "
    "Do not add any numbers or special characters in your response. "
    "Your response should be in one long paragraph. Always answer as if you are talking to a real person. "
    "Do not say 'In the image I see' but say 'With what I see, I think you have ...'. "
    "Do not respond as an AI model or in markdown. Your answer should mimic that of an actual doctor, "
    "not an AI bot. Keep your answer concise (max 2 sentences). No preamble, start your answer right away."
)



def process_inputs(audio_filepath, image_filepath):
    

    if not audio_filepath:
        return "No voice input received.", "Please provide voice input.", None

    try:
        # 1. Speech-to-Text (Patient)
        speech_to_text_output = transcribe_with_groq(
            stt_model="whisper-large-v3",
            audio_filepath=audio_filepath,
            api_key=GROQ_API_KEY
        )

        # 2. Image Analysis (Doctor)
        if image_filepath:
            encoded_image = encode_image(image_filepath)
            doctor_response = analyze_image_with_query(
                query=f"{SYSTEM_PROMPT} {speech_to_text_output}",
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                encoded_image=encoded_image
            )
        else:
            doctor_response = "No image provided for analysis."

        # 3. Text-to-Speech (Doctor’s Voice)
        output_audio_path = "final_doctor_voice.mp3"
        save_tts(doctor_response, output_audio_path)

        # Optional autoplay (disabled in Gradio)
        # play_audio(output_audio_path)

        return speech_to_text_output, doctor_response, output_audio_path

    except Exception as e:
        return "Error processing input.", str(e), None



iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath", label="Patient's Voice Input"),
        gr.Image(type="filepath", label="Upload Face Image (Optional)")
    ],
    outputs=[
        gr.Textbox(label="Transcribed Text (Patient says)"),
        gr.Textbox(label="Doctor's Diagnosis / Response"),
        gr.Audio(label="Doctor's Voice Response")
    ],
    title="AI Doctor with Vision and Voice",
    description="Speak your symptoms and optionally upload your face image. The AI doctor will respond with a diagnosis and voice message."
)



if __name__ == "__main__":
    iface.launch(debug=True)
