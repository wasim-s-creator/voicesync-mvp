"""
VoiceSync MVP - FastAPI Orchestrator
Main entry point for the API
"""

from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid
import logging
from pathlib import Path
import json

from config import HOST, PORT, DEBUG
from agents.tts_agent import get_tts_agent
from agents.lipsync_agent import get_lipsync_agent
from agents.compositor_agent import get_compositor_agent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="VoiceSync MVP API",
    description="Hindi AI Text-to-Speech + Talking Character Platform",
    version="0.1.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
