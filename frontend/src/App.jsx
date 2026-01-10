import React, { useState } from 'react';
import './App.css';

export default function App() {
  const [text, setText] = useState('नमस्ते मैं एक AI हूँ');
  const [emotion, setEmotion] = useState('happy');
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('idle');
  const [progress, setProgress] = useState(0);
  const [errorMsg, setErrorMsg] = useState('');
  const [audioPath, setAudioPath] = useState(null);

  const generateVideo = async () => {
    setStatus('processing');
    setProgress(0);
    setErrorMsg('');
    setAudioPath(null);

    try {
      console.log('Sending request to backend...');
      
      // Step 1: Send text to backend
      const response = await fetch(
        `http://localhost:8000/api/generate?text=${encodeURIComponent(text)}&emotion=${emotion}`,
        { method: 'POST' }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const id = data.job_id;
      setJobId(id);
      console.log('Job created:', id);

      // Step 2: Poll for status
      let pollCount = 0;
      const pollInterval = setInterval(async () => {
        pollCount++;
        try {
          const statusRes = await fetch(`http://localhost:8000/api/status/${id}`);
          const statusData = await statusRes.json();

          console.log('Status:', statusData);
          setProgress(statusData.progress || 0);
          setStatus(statusData.status || 'processing');

          if (statusData.status === 'completed') {
            clearInterval(pollInterval);
            setProgress(100);
            // Try to get audio path from result
            if (statusData.result) {
              setAudioPath(`http://localhost:8000/outputs/${id}_audio.wav`);
            }
            console.log('✅ Video generation complete!');
          } else if (statusData.status === 'failed') {
            clearInterval(pollInterval);
            setErrorMsg(statusData.error || 'Unknown error');
            console.error('❌ Generation failed:', statusData.error);
          }

          // Stop polling after 2 minutes
          if (pollCount > 120) {
            clearInterval(pollInterval);
            setStatus('timeout');
            setErrorMsg('Request timed out');
          }
        } catch (err) {
          console.error('Poll error:', err);
        }
      }, 1000);
    } catch (error) {
      console.error('Error:', error);
      setErrorMsg(error.message);
      setStatus('error');
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🎤 VoiceSync MVP</h1>
        <p>Hindi AI Text-to-Speech Platform</p>
      </div>

      <div className="form">
        <div className="input-group">
          <label>Enter Text (Hindi/English):</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="नमस्ते..."
            rows="4"
          />
        </div>

        <div className="input-group">
          <label>Emotion:</label>
          <select value={emotion} onChange={(e) => setEmotion(e.target.value)}>
            <option value="neutral">😐 Neutral</option>
            <option value="happy">😊 Happy</option>
            <option value="sad">😢 Sad</option>
            <option value="excited">🤩 Excited</option>
          </select>
        </div>

        <button 
          onClick={generateVideo} 
          disabled={status === 'processing'}
          className="btn-generate"
        >
          {status === 'processing' ? '⏳ Generating...' : '🎤 Generate Speech'}
        </button>
      </div>

      {status === 'processing' && (
        <div className="progress">
          <div className="progress-bar" style={{ width: `${progress}%` }}></div>
          <p>{progress}% - Generating audio...</p>
        </div>
      )}

      {status === 'completed' && (
        <div className="success">
          <p>✅ Audio generated successfully!</p>
          {jobId && <p>Job ID: {jobId}</p>}
          
          <div className="audio-player" style={{ marginTop: '20px' }}>
            <h3>🎵 Your Audio:</h3>
            <audio controls style={{ width: '100%', marginTop: '10px' }}>
              <source src={`http://localhost:8000/outputs/${jobId}_audio.wav`} type="audio/wav" />
              Your browser does not support the audio element.
            </audio>
            <a 
              href={`http://localhost:8000/outputs/${jobId}_audio.wav`}
              download={`voicesync_${jobId}.wav`}
              className="btn-download"
              style={{ marginTop: '10px', display: 'block', textAlign: 'center' }}
            >
              📥 Download Audio
            </a>
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="error">
          <p>❌ Error: {errorMsg}</p>
        </div>
      )}

      {status === 'timeout' && (
        <div className="error">
          <p>❌ Request timed out</p>
        </div>
      )}
    </div>
  );
}
