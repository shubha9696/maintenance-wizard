'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import ThreeDCard from '@/components/ThreeDCard';
import Link from 'next/link';
import { Cpu, CheckCircle2, AlertTriangle, AlertCircle, TrendingUp, Activity, ArrowRight, Zap, Shield } from 'lucide-react';

import { API_BASE, getCachedData, setCachedData } from '@/lib/api';

interface DashboardData {
  total_equipment: number;
  healthy_count: number;
  warning_count: number;
  critical_count: number;
  active_alerts: number;
  avg_health_score: number;
  maintenance_due: number;
  recent_activities: Array<{
    equipment_name: string;
    action_type: string;
    date: string;
    downtime_hours: number;
    area: string;
  }>;
  area_stats: Array<{
    area: string;
    avg_health: number;
    equipment_count: number;
    critical_count: number;
  }>;
}

interface Equipment {
  id: string;
  name: string;
  area: string;
  type: string;
  criticality: string;
  status: string;
  health_score: number;
  risk_level?: string;
}

// Zone layout for digital twin
const ZONE_LAYOUT: Array<{
  area: string;
  top: string; left: string; width: string; height: string;
}> = [
  { area: 'Blast Furnace', top: '5%', left: '3%', width: '30%', height: '42%' },
  { area: 'Rolling Mill', top: '5%', left: '36%', width: '28%', height: '42%' },
  { area: 'Coke Oven', top: '5%', left: '67%', width: '30%', height: '42%' },
  { area: 'Power Plant', top: '52%', left: '3%', width: '30%', height: '42%' },
  { area: 'Steel Melting Shop', top: '52%', left: '36%', width: '28%', height: '42%' },
  { area: 'Sinter Plant', top: '52%', left: '67%', width: '30%', height: '42%' },
];

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(() => {
    return getCachedData('/api/equipment/dashboard');
  });
  const [equipment, setEquipment] = useState<Equipment[]>(() => {
    const cached = getCachedData('/api/equipment');
    return cached ? (cached.equipment || []) : [];
  });
  const [loading, setLoading] = useState(() => {
    const cachedDash = getCachedData('/api/equipment/dashboard');
    const cachedEq = getCachedData('/api/equipment');
    return !(cachedDash && cachedEq);
  });
  const [error, setError] = useState('');
  const [hoveredNode, setHoveredNode] = useState<Equipment | null>(null);

  useEffect(() => {
    const cacheKeyDash = '/api/equipment/dashboard';
    const cacheKeyEq = '/api/equipment';

    Promise.all([
      fetch(`${API_BASE}${cacheKeyDash}`).then(r => r.json()),
      fetch(`${API_BASE}${cacheKeyEq}`).then(r => r.json()),
    ])
      .then(([dash, eq]) => {
        setDashboard(dash);
        setEquipment(eq.equipment || []);
        setCachedData(cacheKeyDash, dash);
        setCachedData(cacheKeyEq, eq);
        setLoading(false);
      })
      .catch(e => {
        console.error('Dashboard reload error:', e);
        const hasCached = getCachedData(cacheKeyDash);
        if (!hasCached) {
          setError('Failed to connect to backend. Make sure the API server is running.');
        }
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <div className="particle-bg">
            {[...Array(12)].map((_, i) => <div key={i} className="particle-dot" />)}
          </div>
          <div className="page-container" style={{ position: 'relative', zIndex: 1 }}>
            <div className="page-header">
              <h1 className="gradient-text">Plant Dashboard</h1>
              <p>Loading real-time intelligence...</p>
            </div>
            <div className="stats-grid">
              {[1,2,3,4].map(i => <div key={i} className="shimmer-card" style={{ height: 100 }} />)}
            </div>
            <div className="section-grid" style={{ gap: 16 }}>
              <div className="shimmer-card" style={{ height: 280 }} />
              <div className="shimmer-card" style={{ height: 280 }} />
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <div className="page-container">
            <div className="empty-state">
              <div className="icon">⚠️</div>
              <h3>Connection Error</h3>
              <p>{error}</p>
              <p style={{marginTop: 12, fontSize: 12, color: 'var(--text-muted)'}}>
                Run: <code>uvicorn backend.main:app --reload --port 8000</code>
              </p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const criticalEquipment = equipment.filter(e => e.risk_level === 'critical' || e.health_score < 50);
  const warningEquipment = equipment.filter(e => e.risk_level === 'high' || (e.health_score >= 50 && e.health_score < 70));

  // Deduplicate combined list by id to prevent duplicate keys warning in React
  const combinedAttention = Array.from(
    new Map(
      [...criticalEquipment, ...warningEquipment].map(eq => [eq.id, eq])
    ).values()
  );

  // Group equipment by area for digital twin
  const areaEquipmentMap: Record<string, Equipment[]> = {};
  equipment.forEach(eq => {
    if (!areaEquipmentMap[eq.area]) areaEquipmentMap[eq.area] = [];
    areaEquipmentMap[eq.area].push(eq);
  });

  const getNodeColor = (eq: Equipment) => {
    if (eq.health_score >= 80) return 'green';
    if (eq.health_score >= 50) return 'amber';
    return 'red';
  };

  const getZoneStatus = (area: string): string => {
    const areaData = dashboard?.area_stats?.find(a => a.area === area);
    if (!areaData) return 'healthy';
    if (areaData.avg_health >= 75) return 'healthy';
    if (areaData.avg_health >= 55) return 'warning';
    return 'critical';
  };

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
          <div className="page-header">
            <h1 className="gradient-text" style={{ fontSize: 26, fontWeight: 800, letterSpacing: '-0.5px' }}>
              Plant Dashboard
            </h1>
            <p style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="live-badge"><span></span> LIVE</span>
              Real-time equipment health monitoring and maintenance intelligence
            </p>
          </div>

          {/* Stats Grid with 3D hover effects & glassmorphism */}
          <div className="stats-grid stagger-enter">
            <ThreeDCard className="stat-card blue card-glass-ultra neon-glow-blue">
              <div className="stat-icon"><Cpu size={20} /></div>
              <div className="stat-value stat-value-animated">{dashboard?.total_equipment}</div>
              <div className="stat-label">Total Assets</div>
            </ThreeDCard>
            <ThreeDCard className="stat-card green card-glass-ultra neon-glow-green">
              <div className="stat-icon"><CheckCircle2 size={20} style={{ color: 'var(--accent-green)' }} /></div>
              <div className="stat-value stat-value-animated">{dashboard?.healthy_count}</div>
              <div className="stat-label">Healthy Assets</div>
            </ThreeDCard>
            <ThreeDCard className="stat-card orange card-glass-ultra">
              <div className="stat-icon"><AlertTriangle size={20} style={{ color: 'var(--accent-orange)' }} /></div>
              <div className="stat-value stat-value-animated">{dashboard?.warning_count}</div>
              <div className="stat-label">Warning Status</div>
            </ThreeDCard>
            <ThreeDCard className="stat-card red card-glass-ultra neon-glow-red">
              <div className="stat-icon"><AlertCircle size={20} style={{ color: 'var(--accent-red)' }} /></div>
              <div className="stat-value stat-value-animated">{dashboard?.active_alerts}</div>
              <div className="stat-label">Active Alerts</div>
            </ThreeDCard>
          </div>

          {/* Digital Twin + Plant Health */}
          <div className="section-grid stagger-enter" style={{ gridTemplateColumns: '1.8fr 1fr', marginBottom: 24, gap: 16 }}>
            {/* Digital Twin Plant Schematic */}
            <ThreeDCard className="card card-glass-ultra" style={{ padding: 16, minHeight: 320 }}>
              <h3 style={{ fontSize: 13, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Zap size={15} style={{ color: 'var(--accent-cyan)' }} />
                <span className="gradient-text">Digital Twin — Plant Floor</span>
                <span className="live-badge" style={{ marginLeft: 'auto', fontSize: 9 }}><span></span> SYNCED</span>
              </h3>
              <div className="digital-twin-container" style={{ height: 260 }}>
                <div className="twin-grid-bg" />

                {/* Zones */}
                {ZONE_LAYOUT.map(zone => {
                  const areaData = dashboard?.area_stats?.find(a => a.area === zone.area);
                  const zoneStatus = getZoneStatus(zone.area);
                  const zoneEquipment = areaEquipmentMap[zone.area] || [];

                  return (
                    <div
                      key={zone.area}
                      className={`twin-zone ${zoneStatus}`}
                      style={{ top: zone.top, left: zone.left, width: zone.width, height: zone.height }}
                    >
                      <div className="twin-zone-label">{zone.area}</div>
                      <div className="twin-zone-health">{areaData?.avg_health || '—'}%</div>
                      <div style={{ fontSize: 9, color: 'var(--text-muted)', marginTop: 2 }}>
                        {areaData?.equipment_count || 0} assets
                        {(areaData?.critical_count || 0) > 0 && (
                          <span style={{ color: 'var(--accent-red)', marginLeft: 6 }}>
                            {areaData?.critical_count} alert{(areaData?.critical_count || 0) > 1 ? 's' : ''}
                          </span>
                        )}
                      </div>

                      {/* Equipment nodes removed for clean layout */}
                    </div>
                  );
                })}

                {/* Tooltip for hovered node */}
                {hoveredNode && (
                  <div className="twin-tooltip" style={{ bottom: 10, right: 10 }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>
                      {hoveredNode.name}
                    </div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', display: 'flex', gap: 8 }}>
                      <span>Health: <strong style={{ color: hoveredNode.health_score >= 70 ? 'var(--accent-green)' : 'var(--accent-red)' }}>{hoveredNode.health_score}%</strong></span>
                      <span>Type: {hoveredNode.type}</span>
                    </div>
                  </div>
                )}
              </div>
            </ThreeDCard>

            {/* Plant Health + 3D Scan */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <ThreeDCard className="card card-glass-ultra" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: 140 }}>
                <h3 style={{ fontSize: 13, fontWeight: 700, marginBottom: 12, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                  <TrendingUp size={15} style={{ color: 'var(--accent-blue-light)' }} /> Plant Health
                </h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16, flex: 1 }}>
                  <div style={{
                    width: 90, height: 90, borderRadius: '50%',
                    background: `conic-gradient(${(dashboard?.avg_health_score || 0) >= 70 ? 'var(--accent-green)' : 'var(--accent-orange)'} ${(dashboard?.avg_health_score || 0) * 3.6}deg, rgba(148,163,184,0.08) 0deg)`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    boxShadow: `0 0 20px ${(dashboard?.avg_health_score || 0) >= 70 ? 'rgba(52, 211, 153, 0.2)' : 'rgba(251, 146, 60, 0.2)'}`, flexShrink: 0
                  }}>
                    <div style={{
                      width: 76, height: 76, borderRadius: '50%', background: 'var(--bg-card)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column'
                    }}>
                      <span style={{ fontSize: 22, fontWeight: 800 }}>{dashboard?.avg_health_score}%</span>
                      <span style={{ fontSize: 8, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Rating</span>
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: 11.5, color: 'var(--text-secondary)', marginBottom: 8, lineHeight: 1.4 }}>
                      <strong>{dashboard?.maintenance_due}</strong> assets require scheduled maintenance.
                    </div>
                    <Link href="/chat" className="btn btn-primary" style={{ fontSize: 11, padding: '5px 12px' }}>
                      🤖 Ask AI Wizard <ArrowRight size={11} />
                    </Link>
                  </div>
                </div>
              </ThreeDCard>

              {/* Holographic 3D Scan */}
              <ThreeDCard className="card card-glass-ultra" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', flex: 1 }}>
                <h3 style={{ fontSize: 13, fontWeight: 700, marginBottom: 10, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Activity size={15} style={{ color: 'var(--accent-blue-light)' }} /> Cyber Scan BF Stack
                </h3>
                <div className="hologram-viewport">
                  <div className="isometric-radar">
                    <span className="glow-indicator glow-red" style={{ width: 6, height: 6 }}></span> Scan Layer Active
                  </div>
                  <div className="isometric-tower">
                    <div className="tower-layer layer-1"></div>
                    <div className="tower-layer layer-2"></div>
                    <div className="tower-layer layer-3"></div>
                    <div className="tower-layer layer-4"></div>
                    <div className="tower-layer layer-5"></div>
                  </div>
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', textAlign: 'center', marginTop: 4, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                  Thermal Profile Stack
                </div>
              </ThreeDCard>
            </div>
          </div>

          {/* Attention + Recent activities */}
          <div className="section-grid stagger-enter" style={{ gap: 16 }}>
            <ThreeDCard className="card card-glass-ultra">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
                <h3 style={{ fontSize: 13, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Shield size={14} style={{ color: 'var(--accent-red)' }} />
                  Critical Assets Attention
                </h3>
                <Link href="/equipment" className="btn btn-ghost" style={{ fontSize: 10, padding: '4px 8px' }}>View All</Link>
              </div>
              {combinedAttention.slice(0, 4).map(eq => (
                <Link href={`/equipment/${eq.id}`} key={eq.id} className="alert-card" style={{ marginBottom: 6, padding: 12, textDecoration: 'none' }}>
                  <div className={`alert-dot ${eq.risk_level || (eq.health_score < 50 ? 'critical' : 'high')}`} />
                  <div className="alert-content">
                    <h4 style={{ fontSize: 12.5 }}>{eq.name}</h4>
                    <p style={{ fontSize: 11 }}>{eq.area} • {eq.type}</p>
                  </div>
                  <div>
                    <span className={`health-badge ${eq.status}`} style={{ fontSize: 10, padding: '2px 6px' }}>
                      {eq.health_score}%
                    </span>
                  </div>
                </Link>
              ))}
              {combinedAttention.length === 0 && (
                <div className="empty-state" style={{ padding: 16 }}>
                  <p style={{ fontSize: 12 }}>✅ All assets operating normally</p>
                </div>
              )}
            </ThreeDCard>

            <ThreeDCard className="card card-glass-ultra">
              <h3 style={{ fontSize: 13, fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Activity size={14} style={{ color: 'var(--accent-blue-light)' }} />
                Recent Maintenance Logs
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {dashboard?.recent_activities?.slice(0, 4).map((act, i) => (
                  <div key={i} style={{
                    padding: '8px 0',
                    borderBottom: '1px solid var(--border-color)',
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                  }}>
                    <div>
                      <div style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-primary)' }}>
                        {act.equipment_name}
                      </div>
                      <div style={{ fontSize: 10.5, color: 'var(--text-muted)', marginTop: 2 }}>
                        {act.action_type} • {act.area}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: 10.5, color: 'var(--text-muted)' }}>{act.date}</div>
                      {act.downtime_hours > 0 && (
                        <div style={{ fontSize: 9.5, color: 'var(--accent-orange)', marginTop: 2 }}>
                          {act.downtime_hours}h downtime
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </ThreeDCard>
          </div>
        </div>
      </main>
    </div>
  );
}
