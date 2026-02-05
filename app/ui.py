"""
Simple Gradio web interface for Encode Therapy System.
"""

import gradio as gr
from dotenv import load_dotenv
import speech_recognition as sr

load_dotenv()

# Use absolute imports
from app.main import create_app
from app.utils.tts import speak

# Create workflow once
workflow = None

def init_workflow():
    global workflow
    if workflow is None:
        workflow = create_app()
        # Get initial greeting
        greeting = workflow.get_greeting()
        greeting_audio = speak(greeting, play=False)
        # Use dictionary format
        return [{"role": "assistant", "content": greeting}], greeting_audio
    return [], None

def transcribe_audio(audio_path):
    """Convert audio file to text"""
    if not audio_path:
        return ""
    
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except:
            return ""

def chat(audio_path, history):
    """Process voice and return response"""
    if not audio_path:
        return history, None, None
    
    global workflow
    
    # Get text from audio
    user_text = transcribe_audio(audio_path)
    if not user_text:
        return history, None, None
    
    # Get response from your agentic workflow
    response = workflow.chat(user_text)
    
    # Convert to speech
    audio_file = speak(response, play=False)
    
    # Update chat with dictionary format
    history = history + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": response}
    ]
    
    return history, audio_file, None

# UI
with gr.Blocks() as demo:
    gr.Markdown("# 🧠 Encode Therapy System")
    
    chatbot = gr.Chatbot(height=400)
    audio_input = gr.Audio(sources=["microphone"], type="filepath")
    audio_output = gr.Audio(autoplay=True)
    
    # Load greeting on start
    demo.load(fn=init_workflow, outputs=[chatbot, audio_output])
    
    # Process voice input - now clears the audio input automatically
    audio_input.stop_recording(
        fn=chat,
        inputs=[audio_input, chatbot],
        outputs=[chatbot, audio_output, audio_input]
    )

if __name__ == "__main__":
    demo.launch()