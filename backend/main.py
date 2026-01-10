"""
VoiceSync MVP - FastAPI Orchestrator
Main entry point for the API
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid
import logging
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= JOB MANAGEMENT =============

# In-memory job storage
jobs_db = {}

class Job:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.status = "queued"
        self.current_step = None
        self.progress = 0
        self.result = None
        self.error = None

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "status": self.status,
            "current_step": self.current_step,
            "progress": self.progress,
            "result": self.result,
            "error": self.error
        }

# ============= API ENDPOINTS =============

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "🎤 VoiceSync MVP is running!",
        "version": "0.1.0",
        "endpoints": {
            "generate": "POST /api/generate",
            "status": "GET /api/status/{job_id}",
            "voices": "GET /api/voices",
            "emotions": "GET /api/emotions"
        }
    }

@app.get("/api/voices")
async def get_voices():
    """Get available voices"""
    try:
        return {
            "voices": [
                {"id": "male_deep_hi", "name": "🎤 Deep Male (Hindi)"},
                {"id": "male_natural_hi", "name": "🎤 Natural Male (Hindi)"},
                {"id": "female_natural_hi", "name": "👩 Natural Female (Hindi)"},
                {"id": "male_english_in", "name": "🎤 Male English (India)"},
                {"id": "female_english_in", "name": "👩 Female English (India)"},
                {"id": "male_hinglish", "name": "🎙️ Male Hinglish"},
                {"id": "female_hinglish", "name": "🎙️ Female Hinglish"},
            ]
        }
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/emotions")
async def get_emotions():
    """Get available emotions"""
    try:
        tts = get_tts_agent()
        return {"emotions": tts.get_available_emotions()}
    except Exception as e:
        logger.error(f"Error getting emotions: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/generate")
async def generate_video(
    text: str,
    voice: str = "male_adult",
    emotion: str = "neutral",
    character: str = "character1",
    background: str = "bg1",
    background_tasks: BackgroundTasks = None
):
    """Generate talking character video"""
    try:
        if not text or len(text) < 3:
            return JSONResponse(
                status_code=400,
                content={"error": "Text must be at least 3 characters"}
            )

        job_id = str(uuid.uuid4())
        job = Job(job_id)
        jobs_db[job_id] = job

        logger.info(f"📝 New job created: {job_id}")
        logger.info(f"   Text: {text[:50]}...")
        logger.info(f"   Voice: {voice}, Emotion: {emotion}")

        if background_tasks:
            background_tasks.add_task(
                process_video_pipeline,
                job_id,
                text,
                voice,
                emotion,
                character,
                background
            )

        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Video generation queued. Check status with /api/status/{job_id}"
        }

    except Exception as e:
        logger.error(f"❌ Error creating job: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Get job status"""
    if job_id not in jobs_db:
        return JSONResponse(
            status_code=404,
            content={"error": f"Job {job_id} not found"}
        )

    job = jobs_db[job_id]
    return job.to_dict()

@app.get("/outputs/{file_path:path}")
async def get_output(file_path: str):
    """Serve generated output files (audio, video)"""
    try:
        file_location = Path("./backend/outputs") / file_path
        
        # Security check - prevent path traversal
        file_location = file_location.resolve()
        base_path = Path("./backend/outputs").resolve()
        
        if not str(file_location).startswith(str(base_path)):
            return JSONResponse(status_code=403, content={"error": "Access denied"})
        
        if file_location.exists():
            logger.info(f"📥 Serving file: {file_location}")
            
            # Determine media type
            if str(file_location).endswith('.wav'):
                media_type = "audio/wav"
            elif str(file_location).endswith('.mp4'):
                media_type = "video/mp4"
            else:
                media_type = "application/octet-stream"
            
            return FileResponse(
                path=file_location,
                media_type=media_type,
                filename=file_path.split('/')[-1]
            )
        else:
            logger.warning(f"File not found: {file_location}")
            return JSONResponse(status_code=404, content={"error": "File not found"})
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ============= PROCESSING PIPELINE =============

async def process_video_pipeline(
    job_id: str,
    text: str,
    voice: str,
    emotion: str,
    character: str,
    background: str
):
    """Main video processing pipeline"""
    job = jobs_db[job_id]

    try:
        # STEP 1: TTS
        logger.info(f"[{job_id}] ⏳ STEP 1/3: Generating speech...")
        job.current_step = "tts"
        job.status = "processing"
        job.progress = 0

        tts_agent = get_tts_agent()
        audio_path = await tts_agent.generate_speech(
            text=text,
            voice=voice,
            emotion=emotion,
            output_path=f"./backend/outputs/{job_id}_audio.wav",
        )
        logger.info(f"[{job_id}] ✅ Audio generated: {audio_path}")
        job.progress = 33

        # STEP 2: LipSync
        logger.info(f"[{job_id}] ⏳ STEP 2/3: Generating lip-sync...")
        job.current_step = "lipsync"
        job.progress = 33

        lipsync_agent = get_lipsync_agent()
        character_image = f"./assets/characters/{character}.png"
        lipsync_video = lipsync_agent.generate_lipsync(
            character_image=character_image,
            audio_path=audio_path,
            output_path=f"./backend/outputs/{job_id}_lipsync.mp4"
        )
        logger.info(f"[{job_id}] ✅ Lip-sync video generated: {lipsync_video}")
        job.progress = 66

        # STEP 3: Composite
        logger.info(f"[{job_id}] ⏳ STEP 3/3: Compositing final video...")
        job.current_step = "compositor"
        job.progress = 66

        compositor_agent = get_compositor_agent()
        background_image = f"./assets/backgrounds/{background}.png"
        final_video = compositor_agent.composite_video(
            lipsync_video=lipsync_video,
            character_body=character_image,
            background=background_image,
            output_path=f"./backend/outputs/{job_id}_final.mp4"
        )
        logger.info(f"[{job_id}] ✅ Final video created: {final_video}")
        job.progress = 100

        # COMPLETED
        job.status = "completed"
        job.result = final_video
        logger.info(f"[{job_id}] 🎉 Job completed successfully!")

    except Exception as e:
        logger.error(f"[{job_id}] ❌ Pipeline failed: {e}")
        job.status = "failed"
        job.error = str(e)

# ============= STARTUP/SHUTDOWN =============

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    logger.info("🚀 VoiceSync MVP starting up...")
    # Create outputs directory if it doesn't exist
    Path("./backend/outputs").mkdir(parents=True, exist_ok=True)
    try:
        logger.info("📥 Loading TTS Agent...")
        get_tts_agent()
        logger.info("✅ TTS Agent loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load TTS Agent: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 VoiceSync MVP shutting down...")

# ============= RUN SERVER =============

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🌐 Starting server on {HOST}:{PORT}")
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG
    )
