"""
TTS Agent - Indic-Parler TTS Integration
Converts Hindi/English text to natural speech
"""

import torch
import soundfile as sf
from transformers import AutoTokenizer, AutoModel
from pathlib import Path
import logging
from config import TTS_MODEL_NAME

logger = logging.getLogger(__name__)

class TTSAgent:
    def __init__(self):
        """Initialize TTS model"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🎤 Loading TTS model on {self.device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(TTS_MODEL_NAME)
            self.model = AutoModel.from_pretrained(TTS_MODEL_NAME)
            self.model.to(self.device)
            self.model.eval()
            logger.info("✅ TTS Model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load TTS model: {e}")
            raise

        # Voice presets
        self.voices = {
            "male_young": "A male speaker with youthful voice",
            "male_adult": "A male speaker with mature voice",
            "female_young": "A female speaker with youthful voice",
            "female_adult": "A female speaker with mature voice",
            "male_kids": "A male speaker speaking to children",
        }

        # Emotion descriptions
        self.emotions = {
            "neutral": "speaking in a neutral tone",
            "happy": "speaking in a happy, cheerful tone",
            "sad": "speaking in a sad, melancholic tone",
            "excited": "speaking with excitement and enthusiasm",
            "angry": "speaking in an angry tone",
            "scared": "speaking in a frightened tone",
        }

    def generate_speech(
        self, 
        text: str, 
        voice: str = "male_adult", 
        emotion: str = "neutral",
        output_path: str = None
    ) -> str:
        """
        Generate speech from text
        
        Args:
            text: Input text (Hindi/English)
            voice: Voice preset
            emotion: Emotion modifier
            output_path: Where to save audio
            
        Returns:
            Path to generated audio file
        """
        try:
            # Build description
            voice_desc = self.voices.get(voice, self.voices["male_adult"])
            emotion_desc = self.emotions.get(emotion, self.emotions["neutral"])
            description = f"{voice_desc}, {emotion_desc}"

            logger.info(f"🎵 Generating speech: {text[:50]}...")
            logger.info(f"   Voice: {voice}, Emotion: {emotion}")

            # Tokenize
            inputs = self.tokenizer(description, text, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate audio
            with torch.no_grad():
                audio = self.model.generate(**inputs)

            # Extract audio tensor
            audio_numpy = audio.cpu().numpy().squeeze()

            # Save audio
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
        """Return available voice options"""
        return list(self.voices.keys())

    def get_available_emotions(self):
        """Return available emotion options"""
        return list(self.emotions.keys())


# Singleton instance
_tts_agent = None

def get_tts_agent():
    """Get or create TTS agent instance"""
    global _tts_agent
    if _tts_agent is None:
        _tts_agent = TTSAgent()
    return _tts_agent
