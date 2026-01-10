import torch
import soundfile as sf
from transformers import AutoTokenizer, AutoModel
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TTSAgent:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🎤 Loading TTS model on {self.device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-parler-tts")
            self.model = AutoModel.from_pretrained("ai4bharat/indic-parler-tts")
            self.model.to(self.device)
            self.model.eval()
            logger.info("✅ TTS Model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load TTS model: {e}")
            raise

        self.voices = {
            "male_young": "A male speaker with youthful voice",
            "male_adult": "A male speaker with mature voice",
            "female_young": "A female speaker with youthful voice",
            "female_adult": "A female speaker with mature voice",
            "male_kids": "A male speaker speaking to children",
        }

        self.emotions = {
            "neutral": "speaking in a neutral tone",
            "happy": "speaking in a happy, cheerful tone",
            "sad": "speaking in a sad, melancholic tone",
            "excited": "speaking with excitement and enthusiasm",
            "angry": "speaking in an angry tone",
            "scared": "speaking in a frightened tone",
        }

    def generate_speech(self, text: str, voice: str = "male_adult", emotion: str = "neutral", output_path: str = None) -> str:
        try:
            voice_desc = self.voices.get(voice, self.voices["male_adult"])
            emotion_desc = self.emotions.get(emotion, self.emotions["neutral"])
            description = f"{voice_desc}, {emotion_desc}"

            logger.info(f"🎵 Generating speech: {text[:50]}...")

            inputs = self.tokenizer(description, text, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                audio = self.model.generate(**inputs)

            audio_numpy = audio.cpu().numpy().squeeze()

            if output_path is None:
                output_path = f"./backend/outputs/audio_{hash(text)}.wav"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            sf.write(output_path, audio_numpy, 24000)

            logger.info(f"✅ Audio saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"❌ TTS generation failed: {e}")
            raise

    def get_available_voices(self):
        return list(self.voices.keys())

    def get_available_emotions(self):
        return list(self.emotions.keys())


_tts_agent = None

def get_tts_agent():
    global _tts_agent
    if _tts_agent is None:
        _tts_agent = TTSAgent()
    return _tts_agent
