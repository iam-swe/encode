"""
Simple Gradio web interface for Aura.
"""

import os
import gradio as gr
from dotenv import load_dotenv
import speech_recognition as sr

load_dotenv()

print("=" * 60)
print(f"DEBUG: GOOGLE_API_KEY exists: {'GOOGLE_API_KEY' in os.environ}")
print(f"DEBUG: GOOGLE_API_KEY value: {bool(os.getenv('GOOGLE_API_KEY'))}")
print("=" * 60)

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
    
    # Get text from audio
    user_text = transcribe_audio(audio_path)
    if not user_text:
        return history, None, None
    
    # Get response from workflow
    response = workflow.chat(user_text)
    
    # Convert to speech
    audio_file = speak(response, play=False)
    
    # Update chat
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

# UI
with gr.Blocks() as demo:
    gr.Markdown("# ❤️ Aura")
    
    # State management
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
    
    # Initialize on load
    demo.load(
        fn=init_session,
        outputs=[chatbot, audio_output, workflow]
    )
    
    # Handle recording
    audio_input.stop_recording(
        fn=chat,
        inputs=[audio_input, chatbot, workflow],
        outputs=[chatbot, audio_output, audio_input],
    )

if __name__ == "__main__":
    demo.launch()