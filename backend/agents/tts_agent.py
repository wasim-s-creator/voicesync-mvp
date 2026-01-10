import logging
from pathlib import Path
import asyncio
from edge_tts import communicate

logger = logging.getLogger(__name__)

class TTSAgent:
    def __init__(self):
        logger.info("🎤 TTS Agent initialized (Microsoft Edge TTS)")
        
        # Male and Female voices for Hindi and English
        self.voices = {
            # Male voices - Hindi
            "male_deep_hi": {"voice": "hi-IN-MadhurNeural", "desc": "🎤 Deep Male (Hindi)"},
            "male_natural_hi": {"voice": "hi-IN-MadhurNeural", "desc": "🎤 Natural Male (Hindi)"},
            
            # Female voices - Hindi
            "female_natural_hi": {"voice": "hi-IN-SwaraNeural", "desc": "👩 Natural Female (Hindi)"},
            
            # Male voices - English (India)
            "male_english_in": {"voice": "en-IN-PrabhatNeural", "desc": "🎤 Male English (India)"},
            
            # Female voices - English (India)
            "female_english_in": {"voice": "en-IN-NeerjaNeural", "desc": "👩 Female English (India)"},
            
            # Hinglish options (using Hindi voice for mixed content)
            "male_hinglish": {"voice": "hi-IN-MadhurNeural", "desc": "🎙️ Male Hinglish"},
            "female_hinglish": {"voice": "hi-IN-SwaraNeural", "desc": "🎙️ Female Hinglish"},
        }

        self.emotions = ["neutral", "happy", "sad", "excited", "enthusiastic", "calm"]

    async def generate_speech_async(
        self, 
        text: str, 
        voice: str = "male_natural_hi", 
        emotion: str = "neutral", 
        output_path: str = None
    ) -> str:
        try:
            if output_path is None:
                output_path = f"./backend/outputs/audio_{hash(text)}.wav"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            voice_config = self.voices.get(voice, self.voices["male_natural_hi"])
            voice_id = voice_config["voice"]

            logger.info(f"🎵 Generating speech with Microsoft Edge TTS...")
            logger.info(f"   Text: {text[:50]}...")
            logger.info(f"   Voice: {voice} ({voice_config['desc']})")
            logger.info(f"   Voice ID: {voice_id}")

            # Generate speech with edge-tts
            communicate_instance = communicate.Communicate(text, voice_id, rate="+0%")
            await communicate_instance.save(output_path)

            logger.info(f"✅ Audio saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"❌ TTS generation failed: {e}")
            raise

    async def generate_speech(
        self,
        text: str,
        voice: str = "male_natural_hi",
        emotion: str = "neutral",
        output_path: str = None,
    ) -> str:
        """Async helper that forwards to the core async TTS method."""
        try:
            return await self.generate_speech_async(text, voice, emotion, output_path)
        except Exception as e:
            logger.error(f"❌ TTS generation failed: {e}")
            raise

    def get_available_voices(self):
        """Return voice options"""
        return [
            {
                "id": key,
                "name": value["desc"]
            }
            for key, value in self.voices.items()
        ]

    def get_available_emotions(self):
        return self.emotions


_tts_agent = None

def get_tts_agent():
    global _tts_agent
    if _tts_agent is None:
        _tts_agent = TTSAgent()
    return _tts_agent
