'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import ReactMarkdown from 'react-markdown';
import { Printer, FileText, BarChart2, Bell, ShieldAlert, Sparkles, Download, ChevronDown } from 'lucide-react';

interface Report {
  id: string;
  title: string;
  type: string;
  generated_at: string;
  content: string;
  summary: string;
  equipment_covered: string[];
}

const REPORT_TYPES = [
  { id: 'maintenance_summary', name: 'Maintenance Summary', icon: <BarChart2 size={24} style={{ color: 'var(--accent-blue-light)' }}  />, desc: 'Overview of recent maintenance activities' },
  { id: 'alert_summary', name: 'Alert Summary', icon: <Bell size={24} style={{ color: 'var(--accent-orange)' }}  />, desc: 'Current anomaly alerts and recommended actions' },
  { id: 'equipment_health', name: 'Equipment Health Card', icon: <FileText size={24} style={{ color: 'var(--accent-teal)' }}  />, desc: 'Detailed health report for specific equipment' },
  { id: 'failure_analysis', name: 'Failure Analysis', icon: <ShieldAlert size={24} style={{ color: 'var(--accent-red)' }}  />, desc: 'Analysis of failure patterns and root causes' },
];

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [generating, setGenerating] = useState(false);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [equipmentId, setEquipmentId] = useState('');
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/api/reports')
      .then(r => r.json())
      .then(d => setReports(d.reports || []))
      .catch(() => {});
  }, []);

  const generateReport = async (type: string) => {
    setGenerating(true);
    try {
      const body: Record<string, string> = { report_type: type };
      if (type === 'equipment_health' && equipmentId) {
        body.equipment_id = equipmentId;
      }
      const res = await fetch('http://localhost:8000/api/reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const report = await res.json();
      setReports(prev => [report, ...prev]);
      setSelectedReport(report);
    } catch (e) {
      alert('Failed to generate report. Make sure the backend is running.');
    } finally {
      setGenerating(false);
    }
  };

  const downloadReport = (format: 'md' | 'txt' | 'html' | 'pdf') => {
    if (!selectedReport) return;

    if (format === 'pdf') {
      window.print();
      return;
    }

    let filename = `${selectedReport.title.toLowerCase().replace(/[^a-z0-9]/g, '_')}_${selectedReport.id}`;
    let content = '';
    let mimeType = 'text/plain';

    if (format === 'md') {
      filename += '.md';
      content = `# ${selectedReport.title}\n\n*Generated on: ${new Date(selectedReport.generated_at).toLocaleString()}*\n\n${selectedReport.content}`;
      mimeType = 'text/markdown';
    } else if (format === 'txt') {
      filename += '.txt';
      content = `REPORT: ${selectedReport.title}\n`;
      content += `Generated on: ${new Date(selectedReport.generated_at).toLocaleString()}\n`;
      content += `========================================\n\n`;
      content += selectedReport.content
        .replace(/#/g, '')
        .replace(/\*\*/g, '')
        .replace(/\*/g, '')
        .replace(/`/g, '');
      mimeType = 'text/plain';
    } else if (format === 'html') {
      filename += '.html';
      content = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${selectedReport.title}</title>
  <style>
    body {
      background: #0a0e1a;
      color: #f1f5f9;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      line-height: 1.7;
      max-width: 820px;
      margin: 40px auto;
      padding: 0 24px;
    }
    h1 { color: #60a5fa; border-bottom: 1px solid rgba(148, 163, 184, 0.1); padding-bottom: 12px; margin-bottom: 6px; }
    h2 { color: #22d3ee; margin-top: 32px; border-bottom: 1px solid rgba(148, 163, 184, 0.05); padding-bottom: 6px; }
    h3 { color: #2dd4bf; margin-top: 24px; }
    pre { background: rgba(148, 163, 184, 0.08); padding: 12px; border-radius: 6px; overflow-x: auto; font-family: monospace; border: 1px solid rgba(148, 163, 184, 0.05); }
    code { font-family: monospace; background: rgba(148, 163, 184, 0.1); padding: 2px 5px; border-radius: 4px; }
    table { border-collapse: collapse; width: 100%; margin: 20px 0; }
    th, td { border: 1px solid rgba(148, 163, 184, 0.1); padding: 10px 14px; text-align: left; font-size: 13.5px; }
    th { background: rgba(59, 130, 246, 0.1); color: #94a3b8; }
    ul, ol { padding-left: 24px; }
    li { margin-bottom: 6px; color: #cbd5e1; }
    strong { color: #ffffff; }
    p { margin-bottom: 12px; color: #cbd5e1; }
    .meta { color: #64748b; font-size: 12px; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 0.5px; }
  </style>
</head>
<body>
  <h1>${selectedReport.title}</h1>
  <div class="meta">Compiled: ${new Date(selectedReport.generated_at).toLocaleString()} | ID: ${selectedReport.id}</div>
  <div class="content">
    ${selectedReport.content
      .replace(/### (.*)/g, '<h3>$1</h3>')
      .replace(/## (.*)/g, '<h2>$1</h2>')
      .replace(/# (.*)/g, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^- (.*)/gm, '<li>$1</li>')
      .replace(/(<li>[\s\S]*<\/li>)/g, '<ul>$1</ul>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\n\n/g, '<p></p>')
    }
  </div>
</body>
</html>`;
      mimeType = 'text/html';
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    setShowDownloadMenu(false);
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-container">
          <div className="page-header animate-fadeIn">
            <h1>Reports Console</h1>
            <p>Generate AI-compiled plant maintenance documentation and incident briefs</p>
          </div>

          {/* New Report Selector */}
          <div className="animate-fadeInUp" style={{ marginBottom: 24 }}>
            <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
              <Sparkles size={15} style={{ color: 'var(--accent-blue-light)' }} /> Generate AI Maintenance Brief
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 12 }}>
              {REPORT_TYPES.map(rt => (
                <button
                  key={rt.id}
                  className="card"
                  onClick={() => generateReport(rt.id)}
                  disabled={generating}
                  style={{
                    cursor: generating ? 'wait' : 'pointer',
                    textAlign: 'left',
                    border: '1px solid var(--border-color)',
                    background: 'var(--bg-card)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 8
                  }}
                >
                  <div style={{ marginBottom: 4 }}>{rt.icon}</div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 2 }}>{rt.name}</div>
                  <div style={{ fontSize: 11.5, color: 'var(--text-muted)', lineHeight: 1.4 }}>{rt.desc}</div>
                </button>
              ))}
            </div>

            {/* Equipment Filter Parameter */}
            <div style={{ marginTop: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Target Equipment ID (for specific Health Card):</span>
              <input
                type="text"
                placeholder="e.g., BF-CP-001"
                value={equipmentId}
                onChange={e => setEquipmentId(e.target.value)}
                style={{
                  background: 'var(--bg-input)', border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)', padding: '6px 12px', color: 'var(--text-primary)',
                  fontSize: 12, width: 180, outline: 'none', fontFamily: 'inherit',
                }}
              />
            </div>
          </div>

          {generating && (
            <div className="loading-container" style={{ marginBottom: 20 }}>
              <div className="loading-spinner"></div>
              <span>Assembling report. Compiling knowledge base documents, incident logs, and diagnostics...</span>
            </div>
          )}

          {/* Report Registry Grid */}
          <div className="section-grid" style={{ gridTemplateColumns: '320px 1fr' }}>
            <div className="card" style={{ maxHeight: 'calc(100vh - 380px)', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 12 }}>
              <h3 style={{ fontSize: 14, fontWeight: 700, margin: 0 }}>Compiled Logs</h3>
              {reports.length === 0 ? (
                <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>No reports compiled in current session.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {reports.map(r => (
                    <button
                      key={r.id}
                      onClick={() => setSelectedReport(r)}
                      style={{
                        background: selectedReport?.id === r.id ? 'rgba(59,130,246,0.1)' : 'transparent',
                        border: '1px solid',
                        borderColor: selectedReport?.id === r.id ? 'var(--border-glow)' : 'transparent',
                        borderRadius: 'var(--radius-sm)',
                        padding: '10px 12px',
                        textAlign: 'left',
                        cursor: 'pointer',
                        color: 'var(--text-primary)',
                        fontFamily: 'inherit',
                        width: '100%'
                      }}
                    >
                      <div style={{ fontSize: 13, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.title}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 3 }}>
                        {new Date(r.generated_at).toLocaleString('en-IN', {
                          day: '2-digit', month: 'short', year: 'numeric',
                          hour: '2-digit', minute: '2-digit'
                        })}
                      </div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                        {r.summary}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div>
              {selectedReport ? (
                <div className="report-content animate-fadeIn">
                  <div style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    marginBottom: 16, paddingBottom: 16, borderBottom: '1px solid var(--border-color)'
                  }}>
                    <div>
                      <h2 style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-primary)', margin: 0, letterSpacing: '-0.3px' }}>
                        {selectedReport.title}
                      </h2>
                      <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
                        Compiled: {new Date(selectedReport.generated_at).toLocaleString()} | ID: {selectedReport.id}
                      </p>
                    </div>
                    
                    <div style={{ display: 'flex', gap: 8, position: 'relative' }}>
                      <button
                        className="btn btn-ghost"
                        onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                        style={{ fontSize: 12, padding: '6px 12px', display: 'flex', alignItems: 'center', gap: 6 }}
                      >
                        <Download size={14} /> Download File <ChevronDown size={12} />
                      </button>

                      {showDownloadMenu && (
                        <div style={{
                          position: 'absolute',
                          top: '100%',
                          right: 0,
                          marginTop: 6,
                          background: 'var(--bg-card)',
                          border: '1px solid var(--border-color)',
                          borderRadius: 'var(--radius-sm)',
                          boxShadow: 'var(--shadow-card)',
                          zIndex: 60,
                          minWidth: 160,
                          display: 'flex',
                          flexDirection: 'column',
                          overflow: 'hidden'
                        }}>
                          <button
                            onClick={() => downloadReport('md')}
                            style={{
                              background: 'transparent', border: 'none', color: 'var(--text-primary)',
                              padding: '10px 14px', fontSize: 12, cursor: 'pointer', textAlign: 'left',
                              fontFamily: 'inherit', transition: 'background 0.2s',
                            }}
                            onMouseEnter={e => e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)'}
                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                          >
                            Markdown (.md)
                          </button>
                          <button
                            onClick={() => downloadReport('html')}
                            style={{
                              background: 'transparent', border: 'none', color: 'var(--text-primary)',
                              padding: '10px 14px', fontSize: 12, cursor: 'pointer', textAlign: 'left',
                              fontFamily: 'inherit', transition: 'background 0.2s',
                            }}
                            onMouseEnter={e => e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)'}
                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                          >
                            Standalone HTML (.html)
                          </button>
                          <button
                            onClick={() => downloadReport('pdf')}
                            style={{
                              background: 'transparent', border: 'none', color: 'var(--text-primary)',
                              padding: '10px 14px', fontSize: 12, cursor: 'pointer', textAlign: 'left',
                              fontFamily: 'inherit', transition: 'background 0.2s',
                            }}
                            onMouseEnter={e => e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)'}
                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                          >
                            PDF Document (.pdf)
                          </button>
                          <button
                            onClick={() => downloadReport('txt')}
                            style={{
                              background: 'transparent', border: 'none', color: 'var(--text-primary)',
                              padding: '10px 14px', fontSize: 12, cursor: 'pointer', textAlign: 'left',
                              fontFamily: 'inherit', transition: 'background 0.2s',
                            }}
                            onMouseEnter={e => e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)'}
                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                          >
                            Plain Text (.txt)
                          </button>
                        </div>
                      )}

                      <button
                        className="btn btn-ghost"
                        onClick={() => window.print()}
                        style={{ fontSize: 12, padding: '6px 12px', display: 'flex', alignItems: 'center', gap: 6 }}
                      >
                        <Printer size={14} /> Export PDF
                      </button>
                    </div>
                  </div>
                  <ReactMarkdown>{selectedReport.content}</ReactMarkdown>
                </div>
              ) : (
                <div className="empty-state">
                  <div className="icon">📋</div>
                  <h3>Select report from list</h3>
                  <p>Choose a maintenance overview or click one of the generators above.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
