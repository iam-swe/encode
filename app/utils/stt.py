"""
Speech-to-Text utility for capturing user voice input.
"""

import speech_recognition as sr


def listen() -> str:
    """Listen for speech input and convert it to text.

    Returns:
        The transcribed text from speech, or an error message if recognition fails.
    """
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=30)
        except sr.WaitTimeoutError:
            return ""

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"Speech service error: {e}")
        return ""