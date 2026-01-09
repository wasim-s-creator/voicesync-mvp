from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import os
from pathlib import Path

# Import agents (will create these next)
# from agents.tts_agent import TTSAgent
# from agents.lipsync_agent import LipSyncAgent
# from agents.compositor_agent import CompositorAgent

app = FastAPI(title="VoiceSync MVP API", version="0.1.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage (use Redis in production)
jobs = {}

# Directories
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)


class GenerateRequest(BaseModel):
    text: str
    emotion: str = "neutral"
    character: str = "character1"
    background: str = "cinematic_blue"
    voice: str = "male_young"
    speed: float = 1.0


class JobResponse(BaseModel):
    job_id: str
    status: str
    video_url: str = None
    error: str = None
    progress: int = 0


@app.get("/")
async def root():
    return {
        "service": "VoiceSync MVP API",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "generate": "/api/generate",
            "status": "/api/status/{job_id}",
            "video": "/api/video/{job_id}"
        }
    }


@app.post("/api/generate")
async def generate_video(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
):
    """Generate talking character video from text"""
    
    # Validate input
    if not request.text or len(request.text) < 3:
        raise HTTPException(status_code=400, detail="Text must be at least 3 characters")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job
    jobs[job_id] = {
        "status": "queued",
        "progress": 0,
        "error": None,
        "video_url": None
    }
    
    # Queue processing
    background_tasks.add_task(process_video, job_id, request)
    
    return {"job_id": job_id, "status": "queued"}


@app.get("/api/status/{job_id}", response_model=JobResponse)
async def get_status(job_id: str):
    """Get job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return JobResponse(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        video_url=job["video_url"],
        error=job["error"]
    )


@app.get("/api/video/{job_id}")
async def get_video(job_id: str):
    """Download generated video"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Video not ready")
    
    video_path = OUTPUT_DIR / f"{job_id}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=f"voicesync_{job_id}.mp4"
    )


async def process_video(job_id: str, request: GenerateRequest):
    """Main video processing pipeline"""
    try:
        # Update status: Generating audio
        jobs[job_id]["status"] = "generating_audio"
        jobs[job_id]["progress"] = 10
        
        # TODO: TTS Agent
        # audio_path = await tts_agent.generate(request.text, request.emotion, request.voice)
        audio_path = None  # Placeholder
        
        jobs[job_id]["progress"] = 40
        
        # Update status: Generating lip-sync
        jobs[job_id]["status"] = "generating_lipsync"
        
        # TODO: LipSync Agent
        # face_video_path = await lipsync_agent.generate(audio_path, request.character)
        face_video_path = None  # Placeholder
        
        jobs[job_id]["progress"] = 70
        
        # Update status: Compositing
        jobs[job_id]["status"] = "compositing"
        
        # TODO: Compositor Agent
        # final_video_path = await compositor_agent.generate(
        #     face_video_path,
        #     request.character,
        #     request.background
        # )
        final_video_path = OUTPUT_DIR / f"{job_id}.mp4"
        
        jobs[job_id]["progress"] = 100
        
        # Complete
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["video_url"] = f"/api/video/{job_id}"
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        print(f"Error processing job {job_id}: {e}")


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
