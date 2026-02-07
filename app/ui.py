"""
Simple Gradio web interface for Aura.
"""

import os
import gradio as gr
from dotenv import load_dotenv
import speech_recognition as sr

load_dotenv()

from app.main import create_app
from app.utils.tts import speak

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

def chat(audio_path, history, workflow):
    """Process voice and return response"""
    if not audio_path:
        return history, None, None
    
    user_text = transcribe_audio(audio_path)
    if not user_text:
        return history, None, None
    
    response = workflow.chat(user_text)
    
    audio_file = speak(response, play=False)
    
    history = history + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": response}
    ]
    
    return history, audio_file, None

def init_session():
    """Initialize new session with greeting"""
    workflow = create_app()
    greeting = workflow.get_greeting()
    greeting_audio = speak(greeting, play=False)
    initial_history = [{"role": "assistant", "content": greeting}]
    return initial_history, greeting_audio, workflow

with gr.Blocks() as demo:
    gr.Markdown("# ❤️ Aura")
    
    workflow = gr.State()
    
    chatbot = gr.Chatbot(height=400)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🎤 Your Voice")
            audio_input = gr.Audio(
                sources=["microphone"], 
                type="filepath",
                label="Record your message",
                container=True
            )
        
        with gr.Column():
            gr.Markdown("### ❤️ Aura")
            audio_output = gr.Audio(
                autoplay=True,
                label="Listen to response",
                container=True
            )
    
    demo.load(
        fn=init_session,
        outputs=[chatbot, audio_output, workflow]
    )
    
    audio_input.stop_recording(
        fn=chat,
        inputs=[audio_input, chatbot, workflow],
        outputs=[chatbot, audio_output, audio_input],
    )

if __name__ == "__main__":
    demo.launch()