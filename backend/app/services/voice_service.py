import whisper
import torch
import logging
import os

os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

logger = logging.getLogger(__name__)

class SpeechToTextService:
    def __init__(self, model_size="base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading Whisper model ({model_size}) on {self.device}...")
        self.model = whisper.load_model(model_size, device=self.device)
        logger.info("Whisper model loaded successfully.")

    def transcribe(self, audio_path: str) -> str:
        try:
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return ""
            result = self.model.transcribe(audio_path)
            return result["text"].strip()
        except Exception as e:
            logger.error(f"Error in speech-to-text transcription: {str(e)}")
            return ""
