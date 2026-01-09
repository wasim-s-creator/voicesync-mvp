import os
from dotenv import load_dotenv

load_dotenv()

# Server Config
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Model Config
TTS_MODEL_NAME = "ai4bharat/indic-parler-tts"
LIPSYNC_MODEL_PATH = "./backend/models/musetalk"
CHARACTER_FACE_SIZE = 256

# File Paths
UPLOADS_DIR = "./backend/uploads"
OUTPUTS_DIR = "./backend/outputs"
MODELS_DIR = "./backend/models"

# Job Config
MAX_CONCURRENT_JOBS = 2
JOB_TIMEOUT_SECONDS = 600

# Video Config
VIDEO_FPS = 30
VIDEO_BITRATE = "2000k"
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Create directories if they don't exist
for directory in [UPLOADS_DIR, OUTPUTS_DIR, MODELS_DIR]:
    os.makedirs(directory, exist_ok=True)
