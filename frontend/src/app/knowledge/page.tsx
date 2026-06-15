'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import ThreeDCard from '@/components/ThreeDCard';
import { Database, Upload, FileText, CheckCircle2, RefreshCw, Search, ShieldCheck, Terminal, AlertCircle } from 'lucide-react';
import { API_BASE, getCachedData, setCachedData } from '@/lib/api';

interface DocItem {
  id: string;
  name: string;
  type: string;
  chunks: number;
  date: string;
  size: string;
}

const INITIAL_DOCS: DocItem[] = [
  { id: '1', name: 'general_maintenance_manual.md', type: 'Manual', chunks: 140, date: '2026-05-10', size: '112 KB' },
  { id: '2', name: 'sop_centrifugal_pump.md', type: 'SOP', chunks: 48, date: '2026-05-12', size: '36 KB' },
  { id: '3', name: 'sop_helical_gearbox.md', type: 'SOP', chunks: 52, date: '2026-05-12', size: '42 KB' },
  { id: '4', name: 'sop_induction_motor.md', type: 'SOP', chunks: 44, date: '2026-05-14', size: '32 KB' },
  { id: '5', name: 'sop_steam_turbine.md', type: 'SOP', chunks: 65, date: '2026-05-15', size: '51 KB' },
  { id: '6', name: 'failure_modes.json', type: 'Failure Database', chunks: 25, date: '2026-05-18', size: '10.9 KB' },
  { id: '7', name: 'failure_reports.json', type: 'Failure Database', chunks: 80, date: '2026-05-18', size: '108 KB' },
  { id: '8', name: 'maintenance_logs.json', type: 'Logs', chunks: 600, date: '2026-05-18', size: '406 KB' },
  { id: '9', name: 'bearing_fitting_guide_skf.pdf', type: 'Manual', chunks: 310, date: '2026-05-20', size: '3.4 MB' },
  { id: '10', name: 'blast_furnace_operation_standard.pdf', type: 'Manual', chunks: 520, date: '2026-05-22', size: '4.8 MB' },
];

export default function KnowledgeCenterPage() {
  const [docs, setDocs] = useState<DocItem[]>([]);
  const [docCount, setDocCount] = useState(48);
  const [chunkCount, setChunkCount] = useState(4200);
  const [lastIndexed, setLastIndexed] = useState('2 min ago');
  const [search, setSearch] = useState('');
  
  const [selectedType, setSelectedType] = useState('SOP');
  const [dragging, setDragging] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    fetchStats();
    fetchDocs();
  }, []);

  const fetchStats = async () => {
    const cacheKey = '/api/knowledge/stats';
    const cached = getCachedData(cacheKey);
    if (cached) {
      setDocCount(cached.documents);
      setChunkCount(cached.chunks);
    }
    try {
      const res = await fetch(`${API_BASE}${cacheKey}`);
      const data = await res.json();
      setDocCount(data.documents);
      setChunkCount(data.chunks);
      setCachedData(cacheKey, data);
    } catch (e) {
      console.error("Failed to fetch knowledge stats:", e);
    }
  };

  const fetchDocs = async () => {
    const cacheKey = '/api/knowledge/documents';
    const cached = getCachedData(cacheKey);
    if (cached) {
      setDocs(cached);
    }
    try {
      const res = await fetch(`${API_BASE}${cacheKey}`);
      const data = await res.json();
      setDocs(data);
      setCachedData(cacheKey, data);
    } catch (e) {
      console.error("Failed to fetch documents list:", e);
    }
  };

  const fileTypes = [
    { id: 'SOP', name: 'SOP PDF', desc: 'Standard Operating Procedures' },
    { id: 'Manual', name: 'Equipment Manual', desc: 'Technical & OEM specification manuals' },
    { id: 'Failure Report', name: 'Failure Report', desc: 'Incident analysis and post-mortem logs' },
    { id: 'Checklist', name: 'Inspection Checklist', desc: 'Routine preventative checklist sheets' },
  ];

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragging(true);
    } else if (e.type === 'dragleave') {
      setDragging(false);
    }
  };

  const uploadDocument = async (file: File) => {
    setIngesting(true);
    setLogs([
      `[INFO] Initializing dynamic file parser for type: ${selectedType}...`,
      `[INFO] Preparing file payload: ${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)...`,
    ]);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('doc_type', selectedType);

      setLogs(prev => [...prev, `[INFO] Running semantic chunking (Chunk size: 800, Overlap: 100)...`]);
      setLogs(prev => [...prev, `[INFO] Invoking Gemini embeddings API (model: models/gemini-embedding-004)...`]);

      const res = await fetch(`${API_BASE}/api/knowledge/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Upload failed');
      }

      const data = await res.json();

      setLogs(prev => [
        ...prev,
        `[SUCCESS] File parsed and uploaded: ${data.filename}`,
        `[SUCCESS] Generated ${data.chunks} high-density vectors (3072 dimensions).`,
        `[SUCCESS] Ingested vectors into ChromaDB collection 'knowledge_docs'.`,
        `[SUCCESS] Dynamic Ingestion completed. Stats updated.`,
      ]);

      // Refresh data
      fetchStats();
      fetchDocs();
      setLastIndexed('Just now');
      setSelectedFile(null);
    } catch (err: any) {
      setLogs(prev => [
        ...prev,
        `[ERROR] Ingestion failed: ${err.message || err}`,
      ]);
    } finally {
      setIngesting(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      uploadDocument(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      uploadDocument(file);
    }
  };

  const filteredDocs = docs.filter(d => 
    d.name.toLowerCase().includes(search.toLowerCase()) ||
    d.type.toLowerCase().includes(search.toLowerCase())
  );

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
              Knowledge Center
            </h1>
            <p>Dynamic Enterprise Knowledge Ingestion & Vector Ingestion Engine</p>
          </div>

          {/* Stats Bar */}
          <div className="stats-grid stagger-enter" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
            <ThreeDCard className="stat-card blue card-glass-ultra">
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Documents Ingested</span>
                <span style={{ fontSize: 28, fontWeight: 800, color: 'var(--text-primary)', marginTop: 4 }}>{docCount}</span>
              </div>
            </ThreeDCard>
            <ThreeDCard className="stat-card green card-glass-ultra">
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Text Chunks Created</span>
                <span style={{ fontSize: 28, fontWeight: 800, color: 'var(--text-primary)', marginTop: 4 }}>{chunkCount.toLocaleString()}</span>
              </div>
            </ThreeDCard>
            <ThreeDCard className="stat-card cyan card-glass-ultra">
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Gemini Embeddings</span>
                <span style={{ fontSize: 16, fontWeight: 800, color: 'var(--accent-green)', marginTop: 14, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span className="status-dot" style={{ background: 'var(--accent-green)', boxShadow: '0 0 8px var(--accent-green)' }} /> ACTIVE
                </span>
              </div>
            </ThreeDCard>
            <ThreeDCard className="stat-card orange card-glass-ultra">
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Last Index Refresh</span>
                <span style={{ fontSize: 18, fontWeight: 800, color: 'var(--accent-orange)', marginTop: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <RefreshCw size={15} className={ingesting ? 'spin' : ''} /> {lastIndexed}
                </span>
              </div>
            </ThreeDCard>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
            {/* Upload & Ingest Segment */}
            <div className="card-glass-ultra" style={{ padding: '24px', borderRadius: 'var(--radius-lg)', display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <h2 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Upload size={18} style={{ color: 'var(--accent-blue-light)' }} /> Enterprise Document Ingestion
              </h2>

              {/* Ingestion Options */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                {fileTypes.map(type => (
                  <button
                    key={type.id}
                    onClick={() => setSelectedType(type.id)}
                    style={{
                      background: selectedType === type.id ? 'rgba(59, 130, 246, 0.12)' : 'rgba(255,255,255,0.02)',
                      border: selectedType === type.id ? '1px solid rgba(59, 130, 246, 0.4)' : '1px solid rgba(255,255,255,0.05)',
                      borderRadius: 'var(--radius-md)',
                      padding: '12px',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.2s',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, fontSize: '12.5px', color: selectedType === type.id ? 'var(--accent-blue-light)' : 'var(--text-primary)' }}>
                      <FileText size={15} />
                      {type.name}
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>{type.desc}</div>
                  </button>
                ))}
              </div>

              {/* Upload Box */}
              <div
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                style={{
                  height: '140px',
                  border: dragging ? '2px dashed var(--accent-blue-light)' : '1px dashed rgba(255,255,255,0.1)',
                  borderRadius: 'var(--radius-md)',
                  background: dragging ? 'rgba(59, 130, 246, 0.05)' : 'rgba(255,255,255,0.01)',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '12px',
                  cursor: 'pointer',
                  position: 'relative',
                  transition: 'all 0.2s',
                }}
              >
                <input
                  type="file"
                  id="doc-upload"
                  accept=".pdf,.doc,.docx,.txt,.md,.json,.csv"
                  onChange={handleFileChange}
                  disabled={ingesting}
                  style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer' }}
                />
                <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'rgba(59, 130, 246, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Upload size={18} style={{ color: 'var(--accent-blue-light)' }} />
                </div>
                <div style={{ textAlign: 'center' }}>
                  <p style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {ingesting ? 'Analyzing document...' : 'Drag & Drop document or click to browse'}
                  </p>
                  <p style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>
                    Supports PDF, DOCX, TXT, MD, JSON, CSV
                  </p>
                </div>
              </div>
            </div>

            {/* Ingestion Progress Console */}
            <div className="card-glass-ultra" style={{ padding: '24px', borderRadius: 'var(--radius-lg)', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <h2 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Terminal size={18} style={{ color: 'var(--accent-cyan)' }} /> Embedding Engine Console
              </h2>

              <div style={{
                flex: 1,
                background: '#070b14',
                border: '1px solid rgba(255,255,255,0.05)',
                borderRadius: 'var(--radius-md)',
                padding: '16px',
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '11px',
                lineHeight: '1.6',
                overflowY: 'auto',
                minHeight: '210px',
                maxHeight: '210px',
                color: 'var(--accent-cyan)'
              }}>
                {logs.length === 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', gap: '8px' }}>
                    <AlertCircle size={22} style={{ opacity: 0.5 }} />
                    <span>Upload a document to monitor pipeline execution</span>
                  </div>
                ) : (
                  logs.map((log, idx) => (
                    <div 
                      key={idx} 
                      style={{ 
                        color: log.startsWith('[SUCCESS]') ? 'var(--accent-green)' : log.startsWith('[ERROR]') ? 'var(--accent-red)' : 'var(--accent-cyan)',
                        marginBottom: '6px'
                      }}
                    >
                      {log}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Database Viewer */}
          <div className="card-glass-ultra" style={{ padding: '24px', borderRadius: 'var(--radius-lg)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
              <h2 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Database size={18} style={{ color: 'var(--accent-teal)' }} /> Knowledge Store Index
              </h2>
              <div style={{ position: 'relative', width: '220px' }}>
                <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  placeholder="Search index..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '6px 12px 6px 30px',
                    fontSize: '12px',
                    background: 'rgba(255,255,255,0.02)',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-primary)',
                    outline: 'none',
                  }}
                />
              </div>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', border: 'none' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', textAlign: 'left' }}>
                    <th style={{ padding: '12px 14px', fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Source Document</th>
                    <th style={{ padding: '12px 14px', fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Type</th>
                    <th style={{ padding: '12px 14px', fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Size</th>
                    <th style={{ padding: '12px 14px', fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Indexed Chunks</th>
                    <th style={{ padding: '12px 14px', fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Ingestion Date</th>
                    <th style={{ padding: '12px 14px', fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Vector Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredDocs.map(doc => (
                    <tr key={doc.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.02)', fontSize: '12.5px', color: 'var(--text-secondary)' }}>
                      <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--text-primary)' }}>{doc.name}</td>
                      <td style={{ padding: '12px 14px' }}>
                        <span style={{
                          fontSize: '10px',
                          fontWeight: 700,
                          background: doc.type === 'SOP' ? 'rgba(59,130,246,0.1)' : doc.type === 'Manual' ? 'rgba(6,182,212,0.1)' : 'rgba(139,92,246,0.1)',
                          color: doc.type === 'SOP' ? 'var(--accent-blue-light)' : doc.type === 'Manual' ? 'var(--accent-cyan)' : 'var(--accent-purple)',
                          padding: '2px 8px',
                          borderRadius: '8px'
                        }}>
                          {doc.type}
                        </span>
                      </td>
                      <td style={{ padding: '12px 14px' }}>{doc.size}</td>
                      <td style={{ padding: '12px 14px', fontFamily: "'JetBrains Mono', monospace", fontSize: '11.5px' }}>{doc.chunks}</td>
                      <td style={{ padding: '12px 14px' }}>{doc.date}</td>
                      <td style={{ padding: '12px 14px' }}>
                        <span style={{ color: 'var(--accent-green)', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', fontWeight: 600 }}>
                          <CheckCircle2 size={13} /> Ingested
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
