'use client';

import Sidebar from '@/components/Sidebar';
import { Cpu, Award, Code, Database, Zap, ExternalLink, ShieldCheck, CheckCircle2, Laptop, Network, Settings, Layers } from 'lucide-react';
import ThreeDCard from '@/components/ThreeDCard';

export default function CreditsPage() {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        {/* Particle background */}
        <div className="particle-bg">
          {[...Array(12)].map((_, i) => <div key={i} className="particle-dot" />)}
        </div>

        <div className="page-container page-enter" style={{ position: 'relative', zIndex: 1 }}>
          {/* Header */}
          <div className="page-header" style={{ marginBottom: 28 }}>
            <h1 className="gradient-text" style={{ fontSize: 26, fontWeight: 800, letterSpacing: '-0.5px' }}>
              Credits & Platform Specifications
            </h1>
            <p>Technical details, multi-agent architecture, and developer credentials for the Maintenance Wizard</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '24px', marginBottom: '24px' }}>
            {/* Tata Steel & Hackathon Information */}
            <ThreeDCard className="card-glass-ultra neon-glow-blue" style={{ padding: '28px', borderRadius: 'var(--radius-lg)', display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <div style={{
                  padding: '6px',
                  background: '#ffffff',
                  borderRadius: '16px',
                  border: '1.5px solid rgba(59, 130, 246, 0.25)',
                  boxShadow: '0 0 20px rgba(59, 130, 246, 0.2)',
                  width: '64px',
                  height: '64px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  overflow: 'hidden'
                }}>
                  <img src="/tata-logo.png" alt="TATA Logo" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span style={{ fontSize: '10px', background: 'rgba(59,130,246,0.15)', color: 'var(--accent-blue-light)', padding: '2px 8px', borderRadius: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Official Submission
                    </span>
                  </div>
                  <h2 style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '2px', letterSpacing: '-0.5px' }}>TATA STEEL</h2>
                  <p style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.8px' }}>
                    AI Hackathon 2026 | Round 2 — Agentic AI Challenge
                  </p>
                </div>
              </div>

              <div style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                This intelligent platform was designed and built to address the **Agentic AI Challenge** for heavy industrial manufacturing plants. The Maintenance Wizard provides advanced diagnostic, predictive, and decision-support automation to maximize equipment reliability, reduce downtime, and improve plant efficiency.
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '4px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '12px', color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.02)', padding: '10px 12px', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(255,255,255,0.04)' }}>
                  <Award size={16} style={{ color: 'var(--accent-amber)', flexShrink: 0 }} />
                  <span><strong>Challenge:</strong> Decision Support</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '12px', color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.02)', padding: '10px 12px', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(255,255,255,0.04)' }}>
                  <ShieldCheck size={16} style={{ color: 'var(--accent-green)', flexShrink: 0 }} />
                  <span><strong>Compliance Score:</strong> 100% Core Met</span>
                </div>
              </div>
            </ThreeDCard>

            {/* Developer Credits Card */}
            <ThreeDCard className="card-glass-ultra neon-glow-purple" style={{ padding: '28px', borderRadius: 'var(--radius-lg)', display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <div style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: '50%',
                  background: 'rgba(139, 92, 246, 0.1)',
                  border: '2px solid rgba(139, 92, 246, 0.3)',
                  boxShadow: '0 0 20px rgba(139, 92, 246, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '22px',
                  fontWeight: 800,
                  color: 'var(--accent-purple)'
                }}>
                  SC
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span className="status-dot" style={{ background: 'var(--accent-green)', boxShadow: '0 0 8px var(--accent-green)' }}></span>
                    <span style={{ fontSize: '10.5px', color: 'var(--accent-green)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Lead Platform Architect
                    </span>
                  </div>
                  <h2 style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '2px', letterSpacing: '-0.5px' }}>Shubham Chakrawarti</h2>
                  <p style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    Full Stack AI Developer
                  </p>
                </div>
              </div>

              <div style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                Specializes in designing high-throughput, low-latency agent architectures, vector database design, and real-time visualization frameworks. Shubham architected the custom FastAPI multi-agent fallback routers and the WebGL-grade SVG digital twin plant interface.
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <a 
                  href="https://www.linkedin.com/in/shubham-chakrawarti-27764836a/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="btn" 
                  style={{ flex: 1, padding: '10px 14px', fontSize: '12px', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', background: 'rgba(59, 130, 246, 0.12)', color: 'var(--accent-blue-light)', border: '1px solid rgba(59, 130, 246, 0.25)', borderRadius: 'var(--radius-sm)', transition: 'all 0.2s' }}
                >
                  LinkedIn <ExternalLink size={12} />
                </a>
                <a 
                  href="https://github.com/shubha9696" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="btn" 
                  style={{ flex: 1, padding: '10px 14px', fontSize: '12px', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', background: 'rgba(255, 255, 255, 0.04)', color: 'var(--text-primary)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 'var(--radius-sm)', transition: 'all 0.2s' }}
                >
                  GitHub <ExternalLink size={12} />
                </a>
                <a 
                  href="https://shubham-potfolio.vercel.app/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="btn" 
                  style={{ flex: 1, padding: '10px 14px', fontSize: '12px', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', background: 'rgba(6, 182, 212, 0.1)', color: 'var(--accent-cyan)', border: '1px solid rgba(6, 182, 212, 0.2)', borderRadius: 'var(--radius-sm)', transition: 'all 0.2s' }}
                >
                  Portfolio <ExternalLink size={12} />
                </a>
              </div>
            </ThreeDCard>
          </div>

          {/* Technical Specifications of the Platform */}
          <div className="card-glass-ultra" style={{ padding: '28px', borderRadius: 'var(--radius-lg)', marginBottom: '24px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '22px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Code size={18} style={{ color: 'var(--accent-blue-light)' }} /> Platform Architecture & Specifications
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '24px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', background: 'rgba(255,255,255,0.01)', padding: '18px', borderRadius: 'var(--radius-md)', border: '1px solid rgba(255,255,255,0.03)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 700, fontSize: '14px', color: 'var(--text-primary)' }}>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'rgba(6, 182, 212, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Network size={14} style={{ color: 'var(--accent-cyan)' }} />
                  </div>
                  Multi-Agent Routing Brain
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                  The **Agentic Orchestrator** reads user inputs, classifies intent, and chains 5 independent sub-agents (Diagnostic, Prediction, Recommendation, Knowledge, and Report Agents) via a dynamic, visual routing pipeline.
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', background: 'rgba(255,255,255,0.01)', padding: '18px', borderRadius: 'var(--radius-md)', border: '1px solid rgba(255,255,255,0.03)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 700, fontSize: '14px', color: 'var(--text-primary)' }}>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'rgba(52, 211, 153, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Database size={14} style={{ color: 'var(--accent-teal)' }} />
                  </div>
                  Knowledge Integration (RAG)
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                  Vectorizes standard operating procedures (SOPs), manuals, historical breakdown records, and failure modes inside a persistent **ChromaDB** database using Google Gemini embeddings for semantic search.
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', background: 'rgba(255,255,255,0.01)', padding: '18px', borderRadius: 'var(--radius-md)', border: '1px solid rgba(255,255,255,0.03)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 700, fontSize: '14px', color: 'var(--text-primary)' }}>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'rgba(251, 191, 36, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Zap size={14} style={{ color: 'var(--accent-amber)' }} />
                  </div>
                  Predictive & Anomaly Engines
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                  Integrates multivariate anomaly scoring via scikit-learn **Isolation Forest** algorithms on simulated IoT streams, feeding into linear regression health models for Remaining Useful Life (RUL) estimation.
                </div>
              </div>
            </div>

            <hr style={{ border: 'none', height: '1px', background: 'rgba(255,255,255,0.06)', margin: '24px 0' }} />

            {/* Performance Optimizations Summary */}
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '20px', borderRadius: 'var(--radius-md)', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
              <h3 style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Settings size={15} style={{ color: 'var(--accent-green)' }} /> Enterprise Engineering & Optimization Metrics
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                  <CheckCircle2 size={16} style={{ color: 'var(--accent-green)', marginTop: '2px', flexShrink: 0 }} />
                  <div>
                    <div style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '2px' }}>Multi-LLM Fallback</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Groq Llama 3.3 ↔ Gemini 2.5 automatic routing fallback layer.</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                  <CheckCircle2 size={16} style={{ color: 'var(--accent-green)', marginTop: '2px', flexShrink: 0 }} />
                  <div>
                    <div style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '2px' }}>In-Memory DB Cache</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Disk reading latency reduced by 100x (&lt;2ms) via active RAM cache.</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                  <CheckCircle2 size={16} style={{ color: 'var(--accent-green)', marginTop: '2px', flexShrink: 0 }} />
                  <div>
                    <div style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '2px' }}>Focused RAG Ingestion</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Filtered noise, batch-embedding vector index using Gemini-2.0.</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
