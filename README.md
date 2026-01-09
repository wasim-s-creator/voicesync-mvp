# VoiceSync MVP - Hindi AI Text-to-Speech + Talking Character Platform

**Goal**: Ship production-ready MVP in 10 days

## 🎯 What VoiceSync Does

Convert Hindi/English text into cinematic talking character videos with:
- Natural AI speech (Indic-Parler TTS)
- Accurate lip-sync (MuseTalk v1.5)
- Animated character with emotions
- Cinematic backgrounds
- Export-ready for Reels, Shorts, and films

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- NVIDIA GPU (RTX 3060+ recommended) or Cloud GPU access
- Git

### Backend Setup

```bash
# Clone repository
git clone https://github.com/wasim-s-creator/voicesync-mvp.git
cd voicesync-mvp/backend

# Create virtual environment
conda create -n voicesync python=3.10
conda activate voicesync

# Install dependencies
pip install -r requirements.txt

# Download models (first time only)
python scripts/download_models.py

# Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Access at: `http://localhost:5173`

## 📁 Project Structure

```
voicesync-mvp/
├── backend/
│   ├── main.py                 # FastAPI orchestrator
│   ├── agents/
│   │   ├── tts_agent.py       # Indic-Parler TTS
│   │   ├── lipsync_agent.py   # MuseTalk integration
│   │   └── compositor_agent.py # FFmpeg video compositing
│   ├── models/                 # Model weights (gitignored)
│   ├── uploads/                # User inputs
│   └── outputs/                # Generated videos
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   └── utils/
│   └── public/
│       └── characters/
├── assets/
│   ├── characters/             # Character images
│   ├── backgrounds/            # Cinematic backgrounds
│   └── samples/                # Demo videos
└── docs/
    └── ARCHITECTURE.md         # Technical architecture
```

## 🛠️ Tech Stack

### AI Models
- **TTS**: Indic-Parler TTS (ai4bharat/indic-parler-tts)
- **Lip-Sync**: MuseTalk v1.5
- **Video**: FFmpeg

### Backend
- Python 3.10
- FastAPI
- PyTorch
- Transformers (HuggingFace)

### Frontend
- React 18
- Vite
- Tailwind CSS
- Axios

## 📋 Development Roadmap

### Week 1 (Days 1-7)
- [x] Repository setup
- [ ] TTS Agent implementation
- [ ] MuseTalk lip-sync integration
- [ ] Video compositing pipeline
- [ ] Basic frontend UI

### Week 2 (Days 8-14)
- [ ] End-to-end integration
- [ ] Error handling & optimization
- [ ] Character & background assets
- [ ] Deployment setup
- [ ] Beta testing

## 🎬 Features

### MVP (Week 1-2)
- ✅ Hindi + English text input
- ✅ 3 character options
- ✅ 5 background templates
- ✅ Emotion control (happy, sad, neutral, excited)
- ✅ Speed & pitch control
- ✅ MP4 video export
- ✅ Job queue with status polling

### Post-MVP (Week 3+)
- Character motion (head tilt, blink)
- Dynamic video backgrounds
- Batch processing
- Multi-scene support
- 3D avatar integration
- Real-time preview

## 📝 Usage Example

```javascript
// Frontend API call
const response = await fetch('http://localhost:8000/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: "नमस्ते, मैं VoiceSync हूँ",
    emotion: "happy",
    character: "character1",
    background: "cinematic_blue",
    voice: "male_young"
  })
})

const { job_id } = await response.json()

// Poll for completion
const checkStatus = async () => {
  const status = await fetch(`http://localhost:8000/api/status/${job_id}`)
  const data = await status.json()
  
  if (data.status === 'completed') {
    window.location.href = data.video_url
  } else {
    setTimeout(checkStatus, 2000)
  }
}
```

## 🚨 Known Issues & Workarounds

1. **MuseTalk slow on CPU**: Use cloud GPU or reduce resolution to 256x256
2. **Large model downloads**: First run takes 10-15 mins (downloads ~5GB)
3. **Video rendering time**: 1-3 mins per video depending on length

## 🤝 Contributing

This is an MVP sprint project. Focus areas:
- Performance optimization
- Character asset creation
- Bug fixes
- Documentation

## 📄 License

MIT License - See LICENSE file

## 🔗 Resources

- [Indic-Parler TTS](https://huggingface.co/ai4bharat/indic-parler-tts)
- [MuseTalk GitHub](https://github.com/TMElyralab/MuseTalk)
- [Project Documentation](./docs/ARCHITECTURE.md)

---

**Built by**: [@wasim-s-creator](https://github.com/wasim-s-creator)  
**Status**: 🚧 In Development (Day 1/10)  
**Target Launch**: January 19, 2026
