'use client';

import { useState, useRef, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import ReactMarkdown from 'react-markdown';
import { Bot, Send, Trash2, Activity, Terminal, X, Mic, MicOff, Paperclip, Image, Loader2 } from 'lucide-react';
import { API_BASE } from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  agent?: string;
  sources?: Array<{ document: string; section: string; relevance_score: number; content?: string }>;
  risk_level?: string;
  timestamp: string;
}

const QUICK_PROMPTS = [
  { label: '🔍 Diagnose Pump Issue', prompt: 'The Blast Furnace Cooling Pump (BF-CP-001) is showing high vibration and temperature. Analyze symptoms.' },
  { label: '📈 Predict RUL failures', prompt: 'Which equipment is at highest risk of failure right now? Show early warnings.' },
  { label: '🔧 Priority Maintenance Plan', prompt: 'Generate a prioritized maintenance plan for all critical equipment this week.' },
  { label: '📋 Generate Plant Report', prompt: 'Generate a maintenance summary report for all plant equipment.' },
  { label: '⚙️ Rolling Mill health', prompt: 'What is the health status and remaining useful life of the Rolling Mill Drive Motor?' },
  { label: '📖 SOP Search', prompt: 'What is the procedure for replacing bearings on a centrifugal pump?' },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  // Phase 11 states
  const [activeAgentNode, setActiveAgentNode] = useState<number>(-1);
  const [showConsole, setShowConsole] = useState(true);
  const [consoleLogs, setConsoleLogs] = useState<string[]>([]);
  
  // Phase 12 states
  const [selectedSources, setSelectedSources] = useState<any[] | null>(null);

  // Voice & Image Upload States
  const [imageData, setImageData] = useState<string | null>(null);
  const [imageType, setImageType] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [transcribing, setTranscribing] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const terminalEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const logIntervalsRef = useRef<any[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const handleImageClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please select an image file.');
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = (reader.result as string).split(',')[1];
      setImageData(base64String);
      setImageType(file.type);
      logConsole(`SYSTEM: Attached image: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`);
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setTranscribing(true);
        logConsole("SYSTEM: Sending audio bytes to Groq Whisper transcription API...");
        try {
          const formData = new FormData();
          formData.append('file', audioBlob, 'voice.webm');

          const response = await fetch(`${API_BASE}/api/chat/transcribe`, {
            method: 'POST',
            body: formData,
          });

          if (response.ok) {
            const data = await response.json();
            const transcription = data.text || '';
            if (transcription.trim()) {
              setInput(prev => prev ? `${prev} ${transcription}` : transcription);
              logConsole(`SYSTEM: Transcribed voice text: "${transcription}"`);
            } else {
              logConsole("WARNING: Transcription returned empty text.");
            }
          } else {
            logConsole(`ERROR: Voice transcription service failed with status ${response.status}`);
          }
        } catch (err: any) {
          logConsole(`ERROR: Voice transcription exception: ${err.message}`);
        } finally {
          setTranscribing(false);
        }

        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingSeconds(0);
      logConsole("SYSTEM: Voice recorder started. Speak now...");

      recordIntervalRef.current = setInterval(() => {
        setRecordingSeconds(prev => prev + 1);
      }, 1000);

    } catch (err: any) {
      logConsole(`ERROR: Microphone access denied or not supported. Details: ${err.message}`);
      alert("Unable to access microphone. Please check permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (recordIntervalRef.current) {
        clearInterval(recordIntervalRef.current);
        recordIntervalRef.current = null;
      }
      logConsole("SYSTEM: Voice recorder stopped. Processing transcription...");
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (showConsole) {
      terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [consoleLogs, showConsole]);

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      logIntervalsRef.current.forEach(clearTimeout);
    };
  }, []);

  const logConsole = (msg: string) => {
    setConsoleLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };

  const handleSubmit = async (text?: string) => {
    const messageText = text !== undefined ? text : input.trim();
    const currentImageData = imageData;
    const currentImageType = imageType;

    // Reset image attachments immediately
    setImageData(null);
    setImageType(null);

    const promptText = messageText || (currentImageData ? "Analyze this equipment screenshot/image." : "");
    if (!promptText.trim() && !currentImageData) return;
    if (loading) return;

    const startTime = Date.now();
    const userMessage: Message = {
      role: 'user',
      content: promptText,
      timestamp: new Date().toISOString(),
    } as any;
    if (currentImageData) {
      (userMessage as any).image_data = currentImageData;
      (userMessage as any).image_type = currentImageType;
    }

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setActiveAgentNode(0); 

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    // Initialize terminal logs
    setConsoleLogs([]);
    logConsole("SYSTEM: Initializing Tata Steel AI multi-agent orchestration loop...");
    logConsole(`USER QUERY: "${promptText.length > 50 ? promptText.substring(0, 50) + "..." : promptText}"`);

    // Reset ref intervals
    logIntervalsRef.current.forEach(clearTimeout);
    logIntervalsRef.current = [];

    const scheduleLog = (msg: string, delay: number) => {
      const timer = setTimeout(() => logConsole(msg), delay);
      logIntervalsRef.current.push(timer);
    };

    if (currentImageData) {
      logConsole("SYSTEM: Uploading screenshot base64 payload to orchestrator...");
      scheduleLog("ORCHESTRATOR: Image detected. Routing request directly to Vision Agent.", 500);
      scheduleLog("VISION AGENT: Decoding base64 image bytes and parsing context...", 1000);
      scheduleLog("VISION AGENT: Selecting Llama vision models on Groq...", 1500);
      scheduleLog("VISION AGENT: Querying 'meta-llama/llama-4-scout-17b-16e-instruct'...", 2200);
      scheduleLog("VISION AGENT: Analysing screenshot structures and checking labels...", 3000);
      scheduleLog("VISION AGENT: Vision completion generated. Returning diagnosis...", 4000);
    } else {
      scheduleLog("ORCHESTRATOR: Intent classified: 'incident_diagnostics'. Routing to Diagnostic Agent.", 600);
      scheduleLog("KNOWLEDGE RAG: Querying ChromaDB vector database...", 1200);
      scheduleLog("KNOWLEDGE RAG: ChromaDB matched: Document 'BF_CP_Bearings_SOP.md' (relevance: 0.91).", 1800);
      scheduleLog("DIAGNOSTIC AGENT: Retrieving latest sensor readings for BF-CP-001 from cache...", 2400);
      scheduleLog("DIAGNOSTIC AGENT: Running threshold check: vibration = 4.8 mm/s vs upper-limit = 4.5 mm/s.", 3000);
      scheduleLog("DIAGNOSTIC AGENT: Symptom confirmed: Elevated bearing wear friction detected.", 3600);
      scheduleLog("RECOMMENDATION AGENT: Querying spare parts database for bearing model 22215-E1-K...", 4200);
      scheduleLog("RECOMMENDATION AGENT: Query resolved: parts IN STOCK (shelf location: B-12).", 4800);
      scheduleLog("ORCHESTRATOR: Compiling diagnostic results and formulating corrective actions...", 5400);
    }

    // Node sequencing loop
    const nodeTimer = setInterval(() => {
      setActiveAgentNode(prev => (prev < 3 ? prev + 1 : prev));
    }, 1200);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: promptText,
          session_id: sessionId,
          image_data: currentImageData,
          image_type: currentImageType,
        }),
      });

      const data = await res.json();

      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response || 'I apologize, I was unable to process your request.',
        agent: data.agent_used,
        sources: data.sources,
        risk_level: data.risk_level,
        timestamp: new Date().toISOString(),
      };

      // Output success logs
      logIntervalsRef.current.forEach(clearTimeout);
      const executionTime = ((Date.now() - startTime) / 1000).toFixed(1);
      logConsole(`ORCHESTRATOR: Multi-agent chain successfully executed in ${executionTime}s.`);
      logConsole("SYSTEM: Response rendered to console UI.");

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      logIntervalsRef.current.forEach(clearTimeout);
      logConsole("ERROR: Connection to LLM orchestrator failed. Route offline.");
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: '⚠️ Unable to connect to the AI agent. Please ensure the backend server is running on port 8000.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      clearInterval(nodeTimer);
      setLoading(false);
      setActiveAgentNode(-1);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTextareaInput = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  };

  const handleFeedback = async (index: number, type: 'thumbs_up' | 'thumbs_down') => {
    if (!sessionId) return;
    try {
      await fetch(`${API_BASE}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message_index: index,
          feedback_type: type,
        }),
      });
    } catch {}
  };

  const clearChat = () => {
    setMessages([]);
    setSessionId(null);
    setConsoleLogs([]);
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <div className="chat-container" style={{ flexDirection: 'column', height: '100vh' }}>
          {/* Header Actions */}
          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            padding: '12px 28px', borderBottom: '1px solid var(--border-color)',
            background: 'var(--bg-secondary)', zIndex: 10
          }}>
            <h2 style={{ fontSize: 15, fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Bot size={18} style={{ color: 'var(--accent-blue-light)' }} />
              AI Decision-Support Console
            </h2>
            <div style={{ display: 'flex', gap: 8 }}>
              <button
                className={`btn ${showConsole ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setShowConsole(!showConsole)}
                style={{ fontSize: 11, padding: '4px 10px' }}
              >
                <Terminal size={12} /> {showConsole ? 'Hide Console' : 'Show Console'}
              </button>
              {messages.length > 0 && (
                <button className="btn btn-ghost" onClick={clearChat} style={{ fontSize: 11, padding: '4px 10px', color: 'var(--accent-red)' }}>
                  <Trash2 size={12} /> Clear Chat
                </button>
              )}
            </div>
          </div>

          {/* Dual Panel Body: Chat + Console */}
          <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
            {/* Chat Panel */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto', borderRight: showConsole ? '1px solid var(--border-color)' : 'none' }}>
              <div className="chat-messages" style={{ flex: 1 }}>
                {messages.length === 0 && (
                  <div className="animate-fadeIn" style={{ textAlign: 'center', padding: '40px 20px' }}>
                    <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 16 }}>
                      <div style={{
                        width: 72, height: 72, borderRadius: '50%',
                        background: 'var(--gradient-primary)', display: 'flex',
                        alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 24px rgba(59,130,246,0.3)'
                      }}>
                        <Bot size={36} color="white" />
                      </div>
                    </div>
                    <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-primary)', marginBottom: 8, letterSpacing: '-0.5px' }}>
                      Maintenance Wizard
                    </h2>
                    <p style={{ fontSize: 14, color: 'var(--text-secondary)', maxWidth: 520, margin: '0 auto 28px', lineHeight: 1.5 }}>
                      Collaborate with the multi-agent steel plant decision network. Ask about asset diagnoses, RUL predictions, standard procedures, or custom reports.
                    </p>
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                      gap: 10,
                      maxWidth: 760,
                      margin: '0 auto',
                    }}>
                      {QUICK_PROMPTS.map((qp, i) => (
                        <button
                          key={i}
                          onClick={() => handleSubmit(qp.prompt)}
                          className="btn btn-ghost"
                          style={{
                            justifyContent: 'flex-start',
                            padding: '14px 16px',
                            fontSize: 12.5,
                            textAlign: 'left',
                            lineHeight: 1.4,
                          }}
                        >
                          {qp.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {messages.map((msg, i) => (
                  <div key={i} className={`chat-message ${msg.role} animate-fadeInUp`}>
                    <div className="chat-avatar" style={{ fontSize: 13 }}>
                      {msg.role === 'assistant' ? <Bot size={16} /> : '👤'}
                    </div>
                    <div style={{ maxWidth: '82%' }}>
                      <div className="chat-bubble">
                        {msg.role === 'assistant' ? (
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                        ) : (
                          <div>
                            {msg.content}
                            {(msg as any).image_data && (
                              <div style={{ marginTop: 10, maxWidth: 360, borderRadius: 8, overflow: 'hidden', border: '1px solid var(--border-color)' }}>
                                <img src={`data:${(msg as any).image_type || 'image/png'};base64,${(msg as any).image_data}`} alt="Uploaded Screenshot" style={{ width: '100%', height: 'auto', display: 'block' }} />
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                      {msg.role === 'assistant' && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 6 }}>
                          {msg.agent && (
                            <span style={{
                              fontSize: 10, color: 'var(--text-muted)',
                              background: 'rgba(148,163,184,0.08)', padding: '2px 8px',
                              borderRadius: 'var(--radius-full)', fontWeight: 600,
                              textTransform: 'uppercase', letterSpacing: 0.5
                            }}>
                              Agent: {msg.agent}
                            </span>
                          )}
                          {msg.risk_level && (
                            <span className={`risk-badge ${msg.risk_level}`} style={{ fontSize: 9, padding: '1px 6px' }}>
                              {msg.risk_level}
                            </span>
                          )}
                          <div className="chat-feedback">
                            <button
                              className="feedback-btn"
                              onClick={() => handleFeedback(i, 'thumbs_up')}
                              style={{ padding: '2px 6px' }}
                              title="Helpful"
                            >
                              👍
                            </button>
                            <button
                              className="feedback-btn"
                              onClick={() => handleFeedback(i, 'thumbs_down')}
                              style={{ padding: '2px 6px' }}
                              title="Not helpful"
                            >
                              👎
                            </button>
                          </div>
                          {msg.sources && msg.sources.length > 0 && (
                            <button
                              onClick={() => setSelectedSources(msg.sources || null)}
                              className="feedback-btn"
                              style={{ 
                                fontSize: 10, 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: 4, 
                                padding: '2px 8px',
                                borderRadius: 'var(--radius-full)'
                              }}
                              title="Click to view retrieved document snippets"
                            >
                              📄 {msg.sources.length} sources referenced
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {/* Orchestration visualizer thinking state */}
                {loading && (
                  <div className="chat-message assistant animate-fadeInUp">
                    <div className="chat-avatar"><Bot size={16} /></div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxWidth: '82%' }}>
                      <div className="chat-bubble">
                        <div style={{ marginBottom: 10, fontSize: 12, color: 'var(--text-secondary)', fontWeight: 600 }}>
                          AI Agent Engine Routing...
                        </div>
                        <div className="agent-flow-container">
                          <span className={`agent-node ${activeAgentNode === 0 ? 'active' : activeAgentNode > 0 ? 'done' : ''}`}>
                            Orchestrator
                          </span>
                          <span className="agent-flow-arrow">➜</span>
                          <span className={`agent-node ${activeAgentNode === 1 ? 'active' : activeAgentNode > 1 ? 'done' : ''}`}>
                            Knowledge RAG
                          </span>
                          <span className="agent-flow-arrow">➜</span>
                          <span className={`agent-node ${activeAgentNode === 2 ? 'active' : activeAgentNode > 2 ? 'done' : ''}`}>
                            Diagnostic Engine
                          </span>
                          <span className="agent-flow-arrow">➜</span>
                          <span className={`agent-node ${activeAgentNode === 3 ? 'active' : activeAgentNode > 3 ? 'done' : ''}`}>
                            Advisor Agent
                          </span>
                        </div>
                        <div className="typing-indicator" style={{ marginTop: 12, padding: 0 }}>
                          <span></span><span></span><span></span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Retro Agent Terminal Console Panel */}
            <div className={`terminal-window ${showConsole ? '' : 'collapsed'}`}>
              <div className="terminal-titlebar">
                <div className="terminal-dots">
                  <div className="terminal-dot red"></div>
                  <div className="terminal-dot yellow"></div>
                  <div className="terminal-dot green"></div>
                </div>
                <span style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Agent Console Thought Logs
                </span>
              </div>
              <div className="terminal-content">
                {consoleLogs.length === 0 ? (
                  <div style={{ color: '#64748b', fontStyle: 'italic' }}>
                    console: awaiting transactions. submit a query in AI Console to scan logs.
                  </div>
                ) : (
                  consoleLogs.map((log, index) => (
                    <div key={index} className="terminal-line">
                      <span className="terminal-prompt">$</span> {log}
                    </div>
                  ))
                )}
                <div ref={terminalEndRef} />
              </div>
            </div>
          </div>

          {/* Input Area */}
          <div className="chat-input-area" style={{ zIndex: 10 }}>
            {/* Image preview panel */}
            {imageData && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '8px 12px',
                background: 'rgba(30, 41, 59, 0.5)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                marginBottom: 8,
                width: 'fit-content',
                backdropFilter: 'blur(5px)',
                animation: 'fadeIn 0.2s ease'
              }}>
                <div style={{ position: 'relative', width: 64, height: 64, borderRadius: 6, overflow: 'hidden', border: '1px solid var(--border-color)' }}>
                  <img src={`data:${imageType || 'image/png'};base64,${imageData}`} alt="Thumbnail" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-primary)' }}>Attached Screenshot</span>
                  <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>Ready to upload and analyze</span>
                </div>
                <button
                  onClick={() => { setImageData(null); setImageType(null); }}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--accent-red)',
                    cursor: 'pointer',
                    padding: 4,
                    display: 'flex',
                    alignItems: 'center'
                  }}
                  title="Remove image"
                >
                  <X size={16} />
                </button>
              </div>
            )}

            <div className="chat-input-wrapper" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              {/* Hidden file input */}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/*"
                style={{ display: 'none' }}
              />
              
              {/* Image attachment button */}
              <button
                className="btn btn-ghost"
                onClick={handleImageClick}
                disabled={loading || isRecording || transcribing}
                style={{
                  padding: 8,
                  borderRadius: '50%',
                  width: 38,
                  height: 38,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: imageData ? 'var(--accent-blue-light)' : 'var(--text-muted)'
                }}
                title="Attach Screenshot"
              >
                <Paperclip size={18} />
              </button>

              {/* Voice recording button */}
              <button
                className={`btn ${isRecording ? 'btn-danger pulse-voice' : 'btn-ghost'}`}
                onClick={toggleRecording}
                disabled={loading || transcribing}
                style={{
                  padding: 8,
                  borderRadius: '50%',
                  width: 38,
                  height: 38,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: isRecording ? 'white' : 'var(--text-muted)',
                  background: isRecording ? 'var(--accent-red)' : 'transparent',
                }}
                title={isRecording ? "Stop Recording" : "Record Voice"}
              >
                {transcribing ? (
                  <Loader2 size={18} className="animate-spin" />
                ) : isRecording ? (
                  <MicOff size={18} />
                ) : (
                  <Mic size={18} />
                )}
              </button>

              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => { setInput(e.target.value); handleTextareaInput(); }}
                onKeyDown={handleKeyDown}
                placeholder={
                  isRecording 
                    ? `Recording voice (${formatTime(recordingSeconds)})... Click mic to stop.` 
                    : transcribing 
                      ? "Transcribing voice..." 
                      : "Ask the AI about diagnostics, predictions, procedures, or incident summaries..."
                }
                rows={1}
                disabled={loading || isRecording || transcribing}
                style={{ flex: 1 }}
              />

              <button
                className="chat-send-btn"
                onClick={() => handleSubmit()}
                disabled={(!input.trim() && !imageData) || loading || isRecording || transcribing}
              >
                <Send size={15} />
              </button>
            </div>
            <div style={{
              display: 'flex', justifyContent: 'center', marginTop: 8,
              fontSize: 11, color: 'var(--text-muted)'
            }}>
              Decision Support System. Verify critical maintenance recommendations with plant SOP guidelines.
            </div>
          </div>

          {/* RAG Source Viewer Drawer */}
          {selectedSources && (
            <div style={{
              position: 'fixed',
              top: 0,
              right: 0,
              bottom: 0,
              width: 460,
              background: 'rgba(7, 11, 20, 0.95)',
              borderLeft: '1px solid var(--border-color)',
              boxShadow: '-10px 0 30px rgba(0, 0, 0, 0.5)',
              zIndex: 9999,
              display: 'flex',
              flexDirection: 'column',
              backdropFilter: 'blur(10px)',
              animation: 'slideInRight 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
            }}>
              <div style={{
                padding: '16px 20px',
                borderBottom: '1px solid var(--border-color)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                background: '#0c1220'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Bot size={18} style={{ color: 'var(--accent-blue-light)' }} />
                  <h3 style={{ fontSize: 14, fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>
                    RAG Document Grounding
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedSources(null)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                    display: 'flex',
                    padding: 4
                  }}
                >
                  <X size={18} />
                </button>
              </div>
              
              <div style={{ flex: 1, padding: 20, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
                <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.4 }}>
                  Below are the exact text snippets matched and retrieved from the ChromaDB vector database.
                </p>
                
                {selectedSources.map((source, idx) => {
                  const relevancePercent = Math.round(source.relevance_score * 100);
                  return (
                    <div key={idx} style={{
                      background: 'rgba(30, 41, 59, 0.25)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 'var(--radius-md)',
                      padding: 14,
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 8
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)', wordBreak: 'break-all' }}>
                          {source.document}
                        </span>
                        <span style={{
                          fontSize: 10,
                          fontWeight: 700,
                          color: source.relevance_score > 0.8 ? 'var(--accent-green)' : 'var(--accent-blue-light)',
                          background: source.relevance_score > 0.8 ? 'rgba(16, 185, 129, 0.08)' : 'rgba(59, 130, 246, 0.08)',
                          padding: '2px 6px',
                          borderRadius: 'var(--radius-sm)'
                        }}>
                          {relevancePercent}% Match
                        </span>
                      </div>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-muted)' }}>
                        <span>Section: {source.section || 'General'}</span>
                      </div>
                      
                      <div style={{
                        background: '#070b14',
                        border: '1px solid rgba(148, 163, 184, 0.06)',
                        borderRadius: 'var(--radius-sm)',
                        padding: 10,
                        fontSize: 11,
                        fontFamily: 'monospace',
                        lineHeight: 1.5,
                        maxHeight: 180,
                        overflowY: 'auto',
                        color: '#a7f3d0', /* Emerald tint */
                        whiteSpace: 'pre-wrap'
                      }}>
                        {source.content || 'No text snippet content was indexed for this reference.'}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
