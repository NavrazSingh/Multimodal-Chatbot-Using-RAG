from gtts import gTTS
import os
import uuid
import logging

logger = logging.getLogger(__name__)

class TTSService:
    @staticmethod
    def text_to_speech(text: str, output_dir: str = "uploads") -> str:
        try:
            filename = f"response_{uuid.uuid4()}.mp3"
            filepath = os.path.join(output_dir, filename)
            tts = gTTS(text=text, lang='en')
            tts.save(filepath)
            return filepath
        except Exception as e:
            logger.error(f"TTS Error: {str(e)}")
            return ""
