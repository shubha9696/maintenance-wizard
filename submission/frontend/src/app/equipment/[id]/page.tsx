'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import Link from 'next/link';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Play, Square, Flame, Zap, Activity, ShieldAlert, ArrowLeft, Heart, Calendar, Clock } from 'lucide-react';
import { API_BASE } from '@/lib/api';

interface EquipmentDetail {
  id: string;
  name: string;
  area: string;
  type: string;
  criticality: string;
  status: string;
  health_score: number;
  risk_level?: string;
  last_maintenance?: string;
  sensor_readings: Array<{
    timestamp: string;
    vibration: number;
    temperature: number;
    pressure: number;
    current: number;
  }>;
  maintenance_history: Array<{
    date: string;
    action_type: string;
    failure_mode: string;
    downtime_hours: number;
    technician: string;
  }>;
  spare_parts: Array<{
    name: string;
    part_no: string;
    cost: number;
    lead_time_days: number;
    stock: number;
  }>;
}

interface HealthData {
  rul: {
    rul_days: number;
    confidence: number;
    current_health: number;
    health_trend: string;
    degradation_rate: number;
    failure_probability_30d: number;
    risk_level: string;
    health_history?: Array<{ timestamp: string; health_index: number }>;
  };
  anomalies: {
    anomaly_count: number;
    max_severity: string;
    trend: string;
  };
}

// Reusable Circular SVG Gauge
function CircularGauge({ value, max = 100, label, color, suffix = '' }: { value: number; max?: number; label: string; color: string; suffix?: string }) {
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (Math.min(value, max) / max) * circumference;
  return (
    <div className="progress-ring-container">
      <svg width="96" height="96">
        <circle className="progress-ring-bg" cx="48" cy="48" r={radius} strokeWidth="6" />
        <circle
          className="progress-ring-fill"
          cx="48"
          cy="48"
          r={radius}
          strokeWidth="6"
          stroke={color}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
        />
      </svg>
      <div className="progress-ring-text">
        <span style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)' }}>{value.toFixed(0)}{suffix}</span>
        <span style={{ fontSize: 9, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5, marginTop: 2 }}>{label}</span>
      </div>
    </div>
  );
}

export default function EquipmentDetailPage() {
  const params = useParams();
  const equipmentId = params.id as string;
  const [equipment, setEquipment] = useState<EquipmentDetail | null>(null);
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeChart, setActiveChart] = useState<'vibration' | 'temperature' | 'pressure' | 'current'>('vibration');

  // Simulation states
  const [simulatedReadings, setSimulatedReadings] = useState<any[]>([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [anomalyInjected, setAnomalyInjected] = useState<'none' | 'vibration' | 'temperature' | 'pressure' | 'current'>('none');
  const [liveAnalysis, setLiveAnalysis] = useState<any>(null);

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/api/equipment/${equipmentId}`).then(r => r.json()),
      fetch(`${API_BASE}/api/equipment/${equipmentId}/health`).then(r => r.json()),
    ])
      .then(([eq, h]) => {
        setEquipment(eq);
        setHealth(h);
        setSimulatedReadings(eq.sensor_readings || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [equipmentId]);

  // Live IoT telemetry loop
  useEffect(() => {
    if (!isSimulating || !equipment) return;

    const interval = setInterval(() => {
      setSimulatedReadings(prev => {
        const last = prev[prev.length - 1] || {
          vibration: 2.2,
          temperature: 68.0,
          pressure: 3.4,
          current: 44.0,
        };

        // Walk noise
        let vibration = last.vibration + (Math.random() - 0.5) * 0.25;
        let temperature = last.temperature + (Math.random() - 0.5) * 0.9;
        let pressure = last.pressure + (Math.random() - 0.5) * 0.15;
        let current = last.current + (Math.random() - 0.5) * 0.6;

        vibration = Math.max(0.1, vibration);
        temperature = Math.max(20, temperature);
        pressure = Math.max(0.1, pressure);
        current = Math.max(1, current);

        // Inject anomaly levels if selected
        if (anomalyInjected === 'vibration') {
          vibration = 11.5 + Math.random() * 2.5; // Exceed limit
        } else if (anomalyInjected === 'temperature') {
          temperature = 110.0 + Math.random() * 12; // Exceed limit
        } else if (anomalyInjected === 'pressure') {
          pressure = 8.2 + Math.random() * 1.8; // Exceed limit
        } else if (anomalyInjected === 'current') {
          current = 92.0 + Math.random() * 12; // Exceed limit
        }

        const newReading = {
          timestamp: new Date().toISOString(),
          vibration: parseFloat(vibration.toFixed(2)),
          temperature: parseFloat(temperature.toFixed(2)),
          pressure: parseFloat(pressure.toFixed(2)),
          current: parseFloat(current.toFixed(2)),
        };

        // Query FastAPI backend for immediate telemetry check
        fetch(`${API_BASE}/api/equipment/${equipmentId}/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            vibration: newReading.vibration,
            temperature: newReading.temperature,
            pressure: newReading.pressure,
            current: newReading.current
          })
        })
          .then(res => res.json())
          .then(analysis => {
            setLiveAnalysis(analysis);
          })
          .catch(err => console.error(err));

        const sliced = prev.length >= 30 ? prev.slice(1) : prev;
        return [...sliced, newReading];
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [isSimulating, anomalyInjected, equipment, equipmentId]);

  if (loading) {
    return (
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <div className="page-container">
            <div className="loading-container"><div className="loading-spinner"></div><span>Loading asset metadata...</span></div>
          </div>
        </main>
      </div>
    );
  }

  if (!equipment) {
    return (
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <div className="page-container">
            <div className="empty-state"><h3>Equipment not found</h3></div>
          </div>
        </main>
      </div>
    );
  }

  // Map simulated readings for charts
  const chartData = simulatedReadings.map(r => ({
    time: new Date(r.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    vibration: r.vibration,
    temperature: r.temperature,
    pressure: r.pressure,
    current: r.current,
  }));

  const healthHistory = health?.rul?.health_history?.map(h => ({
    time: new Date(h.timestamp).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
    health: h.health_index,
  })) || [];

  const chartColors: Record<string, string> = {
    vibration: '#3b82f6',
    temperature: '#f87171',
    pressure: '#34d399',
    current: '#fbbf24',
  };

  const chartUnits: Record<string, string> = {
    vibration: 'mm/s',
    temperature: '°C',
    pressure: 'bar',
    current: 'A',
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-container">
          {/* Nav Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
            <Link href="/equipment" className="btn btn-ghost" style={{ padding: '6px 12px', fontSize: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
              <ArrowLeft size={14} /> Back to Fleet
            </Link>
          </div>

          <div className="page-header animate-fadeIn">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <h1>{equipment.name}</h1>
                <p>{equipment.area} • {equipment.type} • ID: <span style={{ fontFamily: 'monospace' }}>{equipment.id}</span></p>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <span className={`health-badge ${equipment.status}`} style={{ fontSize: 12, padding: '5px 12px' }}>
                  {equipment.status.toUpperCase()}
                </span>
                <span className={`risk-badge ${equipment.risk_level || 'low'}`} style={{ padding: '5px 12px', fontSize: 11 }}>
                  {(equipment.risk_level || 'low').toUpperCase()} RISK
                </span>
              </div>
            </div>
          </div>

          {/* IoT Simulator Widget & SVG Circular Gauges */}
          <div className="section-grid animate-fadeInUp" style={{ gridTemplateColumns: '1.6fr 1fr', marginBottom: 24 }}>
            <div className={`simulator-panel ${liveAnalysis?.is_anomaly ? 'anomaly-active' : ''}`} style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <h3 style={{ fontSize: 14, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6, margin: 0 }}>
                  <Activity size={16} style={{ color: 'var(--accent-blue-light)' }} /> Live Telemetry Simulator
                </h3>
                {isSimulating ? (
                  <div className="live-badge"><span></span>Streaming</div>
                ) : (
                  <span style={{ fontSize: 10, color: 'var(--text-muted)', background: 'rgba(148, 163, 184, 0.08)', padding: '2px 8px', borderRadius: 4 }}>IDLE</span>
                )}
              </div>

              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
                <button
                  className={`btn ${isSimulating ? 'btn-ghost' : 'btn-primary'}`}
                  onClick={() => {
                    setIsSimulating(!isSimulating);
                    if (!isSimulating) {
                      setLiveAnalysis(null);
                      setAnomalyInjected('none');
                    }
                  }}
                  style={{ fontSize: 12, padding: '6px 12px' }}
                >
                  {isSimulating ? <><Square size={13} /> Stop Simulator</> : <><Play size={13} /> Start Live Stream</>}
                </button>

                {isSimulating && (
                  <>
                    <button
                      className={`btn ${anomalyInjected === 'vibration' ? 'btn-primary' : 'btn-ghost'}`}
                      onClick={() => setAnomalyInjected(anomalyInjected === 'vibration' ? 'none' : 'vibration')}
                      style={{ fontSize: 11, padding: '6px 12px', borderColor: 'rgba(248,113,113,0.3)', color: anomalyInjected === 'vibration' ? 'white' : 'var(--accent-red)' }}
                    >
                      <Activity size={12} /> Spike Vib
                    </button>
                    <button
                      className={`btn ${anomalyInjected === 'temperature' ? 'btn-primary' : 'btn-ghost'}`}
                      onClick={() => setAnomalyInjected(anomalyInjected === 'temperature' ? 'none' : 'temperature')}
                      style={{ fontSize: 11, padding: '6px 12px', borderColor: 'rgba(248,113,113,0.3)', color: anomalyInjected === 'temperature' ? 'white' : 'var(--accent-red)' }}
                    >
                      <Flame size={12} /> Spike Temp
                    </button>
                    <button
                      className={`btn ${anomalyInjected === 'current' ? 'btn-primary' : 'btn-ghost'}`}
                      onClick={() => setAnomalyInjected(anomalyInjected === 'current' ? 'none' : 'current')}
                      style={{ fontSize: 11, padding: '6px 12px', borderColor: 'rgba(248,113,113,0.3)', color: anomalyInjected === 'current' ? 'white' : 'var(--accent-red)' }}
                    >
                      <Zap size={12} /> Spike Current
                    </button>
                  </>
                )}
              </div>

              {/* Simulation Response Alerts */}
              {isSimulating && liveAnalysis ? (
                <div style={{
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-sm)',
                  background: liveAnalysis.is_anomaly ? 'rgba(248, 113, 113, 0.08)' : 'rgba(52, 211, 153, 0.05)',
                  border: `1px solid ${liveAnalysis.is_anomaly ? 'rgba(248, 113, 113, 0.2)' : 'rgba(52, 211, 153, 0.15)'}`,
                  fontSize: 12,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8
                }}>
                  <span className={`glow-indicator ${liveAnalysis.is_anomaly ? 'glow-red' : 'glow-green'}`}></span>
                  <span style={{ color: liveAnalysis.is_anomaly ? 'var(--accent-red)' : 'var(--accent-green)', fontWeight: 600 }}>
                    {liveAnalysis.is_anomaly ? `THRESHOLD EXCEEDED: ${liveAnalysis.issues[0]?.message}` : 'All simulated metrics operating normally.'}
                  </span>
                </div>
              ) : isSimulating && (
                <div style={{ fontSize: 12, color: 'var(--text-muted)', padding: 4 }}>Waiting for telemetry packets...</div>
              )}
            </div>

            {/* SVG Progress Gauges */}
            <div className="card" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, padding: '16px 24px', alignItems: 'center' }}>
              <CircularGauge
                value={equipment.health_score}
                label="Health Index"
                color={equipment.health_score >= 80 ? 'var(--accent-green)' : equipment.health_score >= 50 ? 'var(--accent-orange)' : 'var(--accent-red)'}
              />
              <CircularGauge
                value={health?.rul?.rul_days || 0}
                max={50}
                label="RUL Forecast"
                color={(health?.rul?.rul_days || 0) >= 28 ? 'var(--accent-green)' : (health?.rul?.rul_days || 0) >= 14 ? 'var(--accent-orange)' : 'var(--accent-red)'}
                suffix=" Days"
              />
            </div>
          </div>

          {/* Sensor Trends Area Charts */}
          <div className="section-grid" style={{ marginBottom: 24 }}>
            <div className="chart-container animate-fadeInUp">
              <div className="chart-header">
                <h3 style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Activity size={14} style={{ color: chartColors[activeChart] }} /> Sensor Waveforms
                </h3>
                <div style={{ display: 'flex', gap: 4 }}>
                  {(['vibration', 'temperature', 'pressure', 'current'] as const).map(s => (
                    <button
                      key={s}
                      className={`btn ${activeChart === s ? 'btn-primary' : 'btn-ghost'}`}
                      onClick={() => setActiveChart(s)}
                      style={{ fontSize: 10, padding: '4px 8px' }}
                    >
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              <ResponsiveContainer width="100%" height={240}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={chartColors[activeChart]} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={chartColors[activeChart]} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.06)" />
                  <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 9 }} tickLine={false} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 9 }} tickLine={false} axisLine={false} unit={` ${chartUnits[activeChart]}`} />
                  <Tooltip
                    contentStyle={{ background: '#1a1f35', border: '1px solid rgba(148,163,184,0.1)', borderRadius: 8, fontSize: 11 }}
                    labelStyle={{ color: '#94a3b8' }}
                  />
                  <Area
                    type="monotone"
                    dataKey={activeChart}
                    stroke={chartColors[activeChart]}
                    fill="url(#colorFill)"
                    strokeWidth={2}
                    dot={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-container animate-fadeInUp" style={{ animationDelay: '0.1s' }}>
              <div className="chart-header">
                <h3 style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Heart size={14} style={{ color: 'var(--accent-blue-light)' }} /> Health Index Degradation Curve
                </h3>
                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  {health?.rul?.health_trend?.replace(/_/g, ' ').toUpperCase()}
                </span>
              </div>
              <ResponsiveContainer width="100%" height={240}>
                <AreaChart data={healthHistory}>
                  <defs>
                    <linearGradient id="healthGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.06)" />
                  <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 9 }} tickLine={false} />
                  <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 9 }} tickLine={false} axisLine={false} unit="%" />
                  <Tooltip
                    contentStyle={{ background: '#1a1f35', border: '1px solid rgba(148,163,184,0.1)', borderRadius: 8, fontSize: 11 }}
                  />
                  <Area type="monotone" dataKey="health" stroke="#3b82f6" fill="url(#healthGrad)" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Maintenance Records & Spare Parts */}
          <div className="section-grid">
            <div className="card animate-fadeInUp">
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Clock size={15} style={{ color: 'var(--accent-blue-light)' }} /> Maintenance Event Records
              </h3>
              <table className="data-table">
                <thead>
                  <tr><th>Date</th><th>Action Taken</th><th>Failure Mode</th><th>Downtime</th></tr>
                </thead>
                <tbody>
                  {equipment.maintenance_history?.slice(0, 5).map((log, i) => (
                    <tr key={i}>
                      <td>{log.date}</td>
                      <td>{log.action_type}</td>
                      <td style={{ maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {log.failure_mode}
                      </td>
                      <td style={{ fontWeight: 600 }}>{log.downtime_hours} hrs</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="card animate-fadeInUp" style={{ animationDelay: '0.1s' }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Calendar size={15} style={{ color: 'var(--accent-blue-light)' }} /> Connected Spare Parts Inventory
              </h3>
              {equipment.spare_parts?.length ? (
                <table className="data-table">
                  <thead>
                    <tr><th>Component Name</th><th>In Stock</th><th>Lead Time</th><th>Procurement Cost</th></tr>
                  </thead>
                  <tbody>
                    {equipment.spare_parts.map((sp, i) => (
                      <tr key={i}>
                        <td style={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {sp.name}
                        </td>
                        <td>
                          <span style={{ color: sp.stock > 0 ? 'var(--accent-green)' : 'var(--accent-red)', fontWeight: 600 }}>
                            {sp.stock > 0 ? `${sp.stock} Units` : 'OUT OF STOCK'}
                          </span>
                        </td>
                        <td>{sp.lead_time_days} days</td>
                        <td style={{ fontWeight: 600 }}>₹{sp.cost.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>No spare parts registered for this asset type.</p>
              )}

              <div style={{ marginTop: 16 }}>
                <Link
                  href={`/chat`}
                  className="btn btn-primary"
                  style={{ width: '100%', justifyContent: 'center', fontSize: 12 }}
                >
                  🤖 Query AI Assistant about this Asset
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
