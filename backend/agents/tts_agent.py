import logging
from pathlib import Path
import os

# For MVP: Use gTTS (free, no auth needed)
try:
    from gtts import gTTS
    USE_GTTS = True
except ImportError:
    USE_GTTS = False
    import torch
    from transformers import AutoTokenizer, AutoModel

logger = logging.getLogger(__name__)

class TTSAgent:
    def __init__(self):
        logger.info("🎤 TTS Agent initialized")
        self.use_gtts = USE_GTTS
        
        if not USE_GTTS:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading Transformers TTS on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-parler-tts")
            self.model = AutoModel.from_pretrained("ai4bharat/indic-parler-tts")

        self.voices = ["male_adult", "female_adult", "male_young", "female_young"]
        self.emotions = ["neutral", "happy", "sad", "excited"]

    def generate_speech(self, text: str, voice: str = "male_adult", emotion: str = "neutral", output_path: str = None) -> str:
        try:
            if output_path is None:
                output_path = f"./backend/outputs/audio_{hash(text)}.wav"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"🎵 Generating speech (gTTS)...")
            logger.info(f"   Text: {text[:50]}...")
            logger.info(f"   Language: Hindi")

            # Use gTTS for Hindi
            tts = gTTS(text=text, lang='hi', slow=False)
            tts.save(output_path)

            logger.info(f"✅ Audio saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"❌ TTS generation failed: {e}")
            raise

    def get_available_voices(self):
        return self.voices

    def get_available_emotions(self):
        return self.emotions


_tts_agent = None

def get_tts_agent():
    global _tts_agent
    if _tts_agent is None:
        _tts_agent = TTSAgent()
    return _tts_agent
