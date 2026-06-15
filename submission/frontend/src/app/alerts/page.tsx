'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import Link from 'next/link';
import { API_BASE } from '@/lib/api';

interface Alert {
  id: string;
  equipment_id: string;
  equipment_name: string;
  area: string;
  type: string;
  severity: string;
  message: string;
  timestamp: string;
  status: string;
  sensor_values: Record<string, number>;
}

interface AlertSummary {
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  by_area: Record<string, number>;
  alerts: Alert[];
}

export default function AlertsPage() {
  const [summary, setSummary] = useState<AlertSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('all');

  useEffect(() => {
    fetch(`${API_BASE}/api/alerts/summary`)
      .then(r => r.json())
      .then(d => { setSummary(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const filtered = summary?.alerts?.filter(a =>
    severityFilter === 'all' || a.severity === severityFilter
  ) || [];

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-container">
          <div className="page-header animate-fadeIn">
            <h1>Anomaly Alerts</h1>
            <p>Real-time anomaly detection and equipment health alerts</p>
          </div>

          {loading ? (
            <div className="loading-container"><div className="loading-spinner"></div><span>Scanning for anomalies...</span></div>
          ) : (
            <>
              {/* Summary Stats */}
              <div className="stats-grid animate-fadeInUp">
                <div className="stat-card red">
                  <div className="stat-icon">🔴</div>
                  <div className="stat-value">{summary?.critical || 0}</div>
                  <div className="stat-label">Critical Alerts</div>
                </div>
                <div className="stat-card orange">
                  <div className="stat-icon">🟠</div>
                  <div className="stat-value">{summary?.high || 0}</div>
                  <div className="stat-label">High Alerts</div>
                </div>
                <div className="stat-card blue">
                  <div className="stat-icon">🟡</div>
                  <div className="stat-value">{summary?.medium || 0}</div>
                  <div className="stat-label">Medium Alerts</div>
                </div>
                <div className="stat-card green">
                  <div className="stat-icon">🔵</div>
                  <div className="stat-value">{summary?.total || 0}</div>
                  <div className="stat-label">Total Alerts</div>
                </div>
              </div>

              {/* Filters */}
              <div style={{ display: 'flex', gap: 8, marginBottom: 20 }} className="animate-fadeInUp">
                {['all', 'critical', 'high', 'medium', 'low'].map(s => (
                  <button
                    key={s}
                    className={`btn ${severityFilter === s ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setSeverityFilter(s)}
                    style={{ fontSize: 12, textTransform: 'capitalize' }}
                  >
                    {s === 'all' ? `All (${summary?.total})` : `${s} (${summary?.[s as keyof AlertSummary] || 0})`}
                  </button>
                ))}
              </div>

              {/* By Area */}
              {summary?.by_area && Object.keys(summary.by_area).length > 0 && (
                <div className="card animate-fadeInUp" style={{ marginBottom: 20 }}>
                  <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>Alerts by Area</h3>
                  <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                    {Object.entries(summary.by_area).sort((a, b) => b[1] - a[1]).map(([area, count]) => (
                      <div key={area} style={{
                        background: 'rgba(59,130,246,0.08)', borderRadius: 'var(--radius-sm)',
                        padding: '8px 14px', fontSize: 13
                      }}>
                        <span style={{ color: 'var(--text-secondary)' }}>{area}: </span>
                        <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Alert List */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {filtered.map((alert, i) => (
                  <div key={alert.id} className="alert-card animate-fadeInUp" style={{ animationDelay: `${i * 0.02}s` }}>
                    <div className={`alert-dot ${alert.severity}`} />
                    <div className="alert-content">
                      <h4>
                        <Link href={`/equipment/${alert.equipment_id}`} style={{ color: 'inherit', textDecoration: 'none' }}>
                          {alert.equipment_name}
                        </Link>
                      </h4>
                      <p>{alert.message}</p>
                      <div style={{ display: 'flex', gap: 12, marginTop: 6 }}>
                        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>📍 {alert.area}</span>
                        {alert.sensor_values && (
                          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                            Vib: {alert.sensor_values.vibration?.toFixed(1)} | Temp: {alert.sensor_values.temperature?.toFixed(1)}°C | Curr: {alert.sensor_values.current?.toFixed(1)}A
                          </span>
                        )}
                      </div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6 }}>
                      <span className={`risk-badge ${alert.severity}`}>{alert.severity}</span>
                      <span className="alert-time">{new Date(alert.timestamp).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                  </div>
                ))}
                {filtered.length === 0 && (
                  <div className="empty-state">
                    <div className="icon">✅</div>
                    <h3>No alerts matching filter</h3>
                    <p>All equipment is operating within normal parameters.</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
