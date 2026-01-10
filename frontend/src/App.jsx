import React, { useState, useEffect } from 'react';
import './App.css';

export default function App() {
  const [text, setText] = useState('नमस्ते मैं एक AI हूँ');
  const [voice, setVoice] = useState('male_natural');
  const [emotion, setEmotion] = useState('happy');
  const [voices, setVoices] = useState([]);
  const [emotions, setEmotions] = useState([]);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('idle');
  const [progress, setProgress] = useState(0);
  const [errorMsg, setErrorMsg] = useState('');

  // Load voices and emotions on mount
  useEffect(() => {
    loadOptions();
  }, []);

  const loadOptions = async () => {
    try {
      // Get voices
      const voicesRes = await fetch('http://localhost:8000/api/voices');
      const voicesData = await voicesRes.json();
      console.log('Voices:', voicesData);
      if (voicesData.voices) {
        setVoices(voicesData.voices);
      }

      // Get emotions
      const emotionsRes = await fetch('http://localhost:8000/api/emotions');
      const emotionsData = await emotionsRes.json();
      console.log('Emotions:', emotionsData);
      if (emotionsData.emotions) {
        setEmotions(emotionsData.emotions);
      }
    } catch (err) {
      console.error('Error loading options:', err);
      setErrorMsg('Failed to load voice options');
    }
  };

  const generateAudio = async () => {
    setStatus('processing');
    setProgress(0);
    setErrorMsg('');

    try {
      console.log('Generating audio with voice:', voice, 'emotion:', emotion);
      
      const response = await fetch(
        `http://localhost:8000/api/generate?text=${encodeURIComponent(text)}&voice=${voice}&emotion=${emotion}`,
        { method: 'POST' }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const id = data.job_id;
      setJobId(id);
      console.log('Job created:', id);

      // Poll for status
      let pollCount = 0;
      const pollInterval = setInterval(async () => {
        pollCount++;
        try {
          const statusRes = await fetch(`http://localhost:8000/api/status/${id}`);
          const statusData = await statusRes.json();

          setProgress(statusData.progress || 0);
          setStatus(statusData.status || 'processing');
          console.log('Status update:', statusData.status, statusData.progress);

          if (statusData.status === 'completed') {
            clearInterval(pollInterval);
            setProgress(100);
            console.log('✅ Audio generation complete!');
          } else if (statusData.status === 'failed') {
            clearInterval(pollInterval);
            setErrorMsg(statusData.error || 'Unknown error');
            console.error('❌ Generation failed:', statusData.error);
          }

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
        <p>Hindi & Hinglish AI Text-to-Speech</p>
      </div>

      <div className="form">
        <div className="input-group">
          <label>📝 Enter Text (Hindi/English/Hinglish):</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="नमस्ते... / Hello... / Namaste bhai..."
            rows="4"
          />
          <small style={{ color: '#999', marginTop: '5px' }}>
            Supports Hindi, English, and Hinglish (mixed)
          </small>
        </div>

        <div className="input-group">
          <label>🎙️ Voice ({voices.length} available):</label>
          {voices.length > 0 ? (
            <select value={voice} onChange={(e) => setVoice(e.target.value)}>
              {voices.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name}
                </option>
              ))}
            </select>
          ) : (
            <select disabled>
              <option>Loading voices...</option>
            </select>
          )}
        </div>

        <div className="input-group">
          <label>😊 Emotion ({emotions.length} available):</label>
          {emotions.length > 0 ? (
            <select value={emotion} onChange={(e) => setEmotion(e.target.value)}>
              {emotions.map((e) => (
                <option key={e} value={e}>
                  {e.charAt(0).toUpperCase() + e.slice(1)}
                </option>
              ))}
            </select>
          ) : (
            <select disabled>
              <option>Loading emotions...</option>
            </select>
          )}
        </div>

        <button 
          onClick={generateAudio} 
          disabled={status === 'processing' || voices.length === 0}
          className="btn-generate"
        >
          {status === 'processing' ? '⏳ Generating...' : '🎤 Generate Audio'}
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
          {jobId && <p className="small-text">Job ID: {jobId}</p>}
          
          <div className="audio-player">
            <h3>🎵 Your Audio:</h3>
            <audio controls style={{ width: '100%', marginTop: '10px' }}>
              <source src={`http://localhost:8000/outputs/${jobId}_audio.wav`} type="audio/wav" />
              Your browser does not support the audio element.
            </audio>
            <a 
              href={`http://localhost:8000/outputs/${jobId}_audio.wav`}
              download={`voicesync_${jobId}.wav`}
              className="btn-download"
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

      <div className="footer">
        <p>💡 Tip: Try "नमस्ते भैया, कैसे हो?" for Hinglish!</p>
      </div>
    </div>
  );
}
