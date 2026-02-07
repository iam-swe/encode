"""
Text-to-Speech utility for converting agent responses to audio.
"""

import os
import tempfile
from gtts import gTTS


def speak(text: str, filename: str | None = None, play: bool = True) -> str:
    """Convert text to speech and optionally play it.

    Args:
        text: The text to convert to speech
        filename: Optional filename for the audio file. If not provided,
                  a temporary file will be created.
        play: Whether to play the audio immediately (default: True)

    Returns:
        The path to the saved audio file
    """
    if not text or not text.strip():
        return ""

    if filename is None:
        temp_dir = tempfile.gettempdir()
        filename = os.path.join(temp_dir, "encode_response.mp3")

    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(filename)

    if play:
        os.system(f'afplay "{filename}"')

    return filename
