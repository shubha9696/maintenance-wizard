'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import ThreeDCard from '@/components/ThreeDCard';
import Link from 'next/link';
import { API_BASE } from '@/lib/api';
import {
  TrendingUp, TrendingDown, AlertTriangle, Shield, Activity,
  BarChart3, PieChart, ArrowDownRight, ArrowUpRight, Minus,
  DollarSign, Clock, Zap, Target
} from 'lucide-react';

interface AnalyticsData {
  risk_distribution: { critical: number; high: number; medium: number; low: number };
  failure_timeline: Array<{
    id: string; name: string; area: string;
    rul_days: number; health: number; risk: string; failure_prob_30d: number;
  }>;
  degradation_leaderboard: Array<{
    id: string; name: string; area: string;
    health: number; degradation_rate: number; trend: string;
    failure_prob_30d: number; rul_days: number;
  }>;
  anomaly_trends: Array<{
    id: string; name: string; anomaly_count: number;
    max_severity: string; trend: string;
  }>;
  roi: {
    prevented_downtime_hours: number; unplanned_cost_per_hour: number;
    savings_from_prevention: number; planned_maintenance_cost: number;
    net_savings: number;
  };
  total_equipment: number;
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/equipment/analytics`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const getRulBand = (days: number) => {
    if (days <= 7) return 'band-red';
    if (days <= 30) return 'band-orange';
    if (days <= 90) return 'band-yellow';
    return 'band-green';
  };

  const getRulColor = (days: number) => {
    if (days <= 7) return 'var(--accent-red)';
    if (days <= 30) return 'var(--accent-orange)';
    if (days <= 90) return 'var(--accent-amber)';
    return 'var(--accent-green)';
  };

  const getTrendIcon = (trend: string) => {
    if (trend.includes('degradation') || trend === 'worsening') return <ArrowDownRight size={13} />;
    if (trend === 'improving') return <ArrowUpRight size={13} />;
    return <Minus size={13} />;
  };

  const getTrendClass = (trend: string) => {
    if (trend.includes('degradation') || trend === 'worsening') return 'degrading';
    if (trend === 'improving') return 'improving';
    return 'stable';
  };

  const formatCurrency = (val: number) => {
    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`;
    if (val >= 1000) return `$${(val / 1000).toFixed(0)}K`;
    return `$${val}`;
  };

  // Donut chart SVG generation
  const renderDonut = () => {
    if (!data) return null;
    const { critical, high, medium, low } = data.risk_distribution;
    const total = critical + high + medium + low || 1;
    const segments = [
      { count: critical, color: '#f87171', label: 'Critical' },
      { count: high, color: '#fb923c', label: 'High' },
      { count: medium, color: '#fbbf24', label: 'Medium' },
      { count: low, color: '#34d399', label: 'Low' },
    ];

    let offset = 0;
    const radius = 70;
    const circumference = 2 * Math.PI * radius;

    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
        <div className="donut-container" style={{ width: 180, height: 180 }}>
          <svg width="180" height="180" viewBox="0 0 180 180">
            {segments.map((seg, i) => {
              const pct = seg.count / total;
              const dashLength = pct * circumference;
              const dashOffset = -offset * circumference;
              offset += pct;
              return (
                <circle
                  key={i}
                  cx="90" cy="90" r={radius}
                  fill="none"
                  stroke={seg.color}
                  strokeWidth="18"
                  strokeDasharray={`${dashLength} ${circumference - dashLength}`}
                  strokeDashoffset={dashOffset}
                  strokeLinecap="round"
                  style={{
                    transform: 'rotate(-90deg)',
                    transformOrigin: '90px 90px',
                    transition: 'stroke-dasharray 1s ease',
                    filter: `drop-shadow(0 0 4px ${seg.color}40)`
                  }}
                />
              );
            })}
          </svg>
          <div className="donut-center-text">
            <span className="donut-center-value">{total}</span>
            <span className="donut-center-label">Assets</span>
          </div>
        </div>
        <div className="donut-legend">
          {segments.map((seg, i) => (
            <div key={i} className="donut-legend-item">
              <span className="donut-legend-dot" style={{ background: seg.color, boxShadow: `0 0 6px ${seg.color}50` }} />
              <span style={{ fontWeight: 700, minWidth: 24 }}>{seg.count}</span>
              <span>{seg.label} Risk</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

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
              <h1 className="gradient-text">Predictive Analytics</h1>
              <p>Loading fleet intelligence...</p>
            </div>
            <div className="stats-grid">
              {[1,2,3,4].map(i => <div key={i} className="shimmer-card" />)}
            </div>
            <div className="section-grid" style={{ gap: 16 }}>
              <div className="shimmer-card" style={{ height: 300 }} />
              <div className="shimmer-card" style={{ height: 300 }} />
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <div className="page-container">
            <div className="empty-state">
              <div className="icon">📊</div>
              <h3>Analytics Unavailable</h3>
              <p>Unable to load fleet analytics. Make sure the backend is running.</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const { risk_distribution: risk, roi } = data;
  const totalRisk = risk.critical + risk.high;

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
            <h1 className="gradient-text" style={{ fontSize: 28, fontWeight: 800, letterSpacing: '-0.5px' }}>
              Predictive Analytics Engine
            </h1>
            <p style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="live-badge"><span></span> LIVE</span>
              Fleet-wide failure prediction, risk analysis & maintenance ROI
            </p>
          </div>

          {/* KPI Stats */}
          <div className="stats-grid stagger-enter" style={{ marginBottom: 24 }}>
            <ThreeDCard className="stat-card red card-glass-ultra neon-glow-red">
              <div className="stat-icon"><AlertTriangle size={20} style={{ color: 'var(--accent-red)' }} /></div>
              <div className="stat-value stat-value-animated">{risk.critical}</div>
              <div className="stat-label">Critical Risk</div>
            </ThreeDCard>
            <ThreeDCard className="stat-card orange card-glass-ultra neon-glow-blue">
              <div className="stat-icon"><Shield size={20} style={{ color: 'var(--accent-orange)' }} /></div>
              <div className="stat-value stat-value-animated">{risk.high}</div>
              <div className="stat-label">High Risk</div>
            </ThreeDCard>
            <ThreeDCard className="stat-card blue card-glass-ultra neon-glow-purple">
              <div className="stat-icon"><Target size={20} style={{ color: 'var(--accent-blue-light)' }} /></div>
              <div className="stat-value stat-value-animated">{data.total_equipment}</div>
              <div className="stat-label">Fleet Size</div>
            </ThreeDCard>
            <ThreeDCard className="stat-card green card-glass-ultra neon-glow-green">
              <div className="stat-icon"><DollarSign size={20} style={{ color: 'var(--accent-green)' }} /></div>
              <div className="stat-value stat-value-animated">{formatCurrency(roi.net_savings)}</div>
              <div className="stat-label">Net Savings</div>
            </ThreeDCard>
          </div>

          {/* Row 1: Failure Timeline + Risk Donut */}
          <div className="section-grid stagger-enter" style={{ gridTemplateColumns: '1.6fr 1fr', gap: 16, marginBottom: 24 }}>
            <ThreeDCard className="card card-glass-ultra">
              <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <BarChart3 size={16} style={{ color: 'var(--accent-blue-light)' }} />
                Fleet Failure Forecast Timeline
              </h3>
              <div className="forecast-bar-container">
                {data.failure_timeline.slice(0, 12).map((item, i) => {
                  const maxRul = Math.max(...data.failure_timeline.map(f => f.rul_days), 1);
                  const pct = Math.min(100, (item.rul_days / maxRul) * 100);
                  return (
                    <Link href={`/equipment/${item.id}`} key={item.id} style={{ textDecoration: 'none' }}>
                      <div className="forecast-bar-row" style={{ animationDelay: `${i * 0.05}s` }}>
                        <div>
                          <div className="forecast-bar-name">{item.name}</div>
                          <div className="forecast-bar-area">{item.area}</div>
                        </div>
                        <div className="forecast-bar-track">
                          <div
                            className={`forecast-bar-fill ${getRulBand(item.rul_days)}`}
                            style={{ width: `${Math.max(8, pct)}%` }}
                          >
                            {item.rul_days}d
                          </div>
                        </div>
                        <div className="forecast-rul-value" style={{ color: getRulColor(item.rul_days) }}>
                          {item.rul_days}d
                        </div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </ThreeDCard>

            <ThreeDCard className="card card-glass-ultra">
              <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <PieChart size={16} style={{ color: 'var(--accent-purple)' }} />
                Risk Distribution
              </h3>
              {renderDonut()}
              <div style={{ marginTop: 16, padding: '10px 14px', background: 'rgba(248, 113, 113, 0.06)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(248, 113, 113, 0.15)' }}>
                <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                  ⚠️ <strong style={{ color: 'var(--accent-red)' }}>{totalRisk}</strong> assets require immediate attention
                </span>
              </div>
            </ThreeDCard>
          </div>

          {/* Row 2: Degradation Leaderboard */}
          <ThreeDCard className="card card-glass-ultra" style={{ marginBottom: 24 }}>
            <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <TrendingDown size={16} style={{ color: 'var(--accent-red)' }} />
              Health Degradation Leaderboard
              <span style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--text-muted)', fontWeight: 500 }}>
                Top 15 fastest degrading assets
              </span>
            </h3>
            <div style={{ overflowX: 'auto' }}>
              <table className="leaderboard-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Asset</th>
                    <th>Area</th>
                    <th>Health</th>
                    <th>Degradation</th>
                    <th>Trend</th>
                    <th>30d Fail %</th>
                    <th>RUL</th>
                  </tr>
                </thead>
                <tbody>
                  {data.degradation_leaderboard.map((item, i) => (
                    <tr key={item.id}>
                      <td style={{ fontWeight: 700, color: i < 3 ? 'var(--accent-red)' : 'var(--text-muted)', fontSize: 13 }}>
                        {i + 1}
                      </td>
                      <td>
                        <Link href={`/equipment/${item.id}`} style={{ color: 'var(--text-primary)', textDecoration: 'none', fontWeight: 600 }}>
                          {item.name}
                        </Link>
                      </td>
                      <td style={{ color: 'var(--text-muted)', fontSize: 11 }}>{item.area}</td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{ width: 50, height: 5, background: 'rgba(148,163,184,0.1)', borderRadius: 3, overflow: 'hidden' }}>
                            <div style={{
                              width: `${item.health}%`, height: '100%', borderRadius: 3,
                              background: item.health >= 70 ? 'var(--accent-green)' : item.health >= 50 ? 'var(--accent-orange)' : 'var(--accent-red)'
                            }} />
                          </div>
                          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, fontWeight: 700 }}>
                            {item.health}%
                          </span>
                        </div>
                      </td>
                      <td style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: item.degradation_rate > 0 ? 'var(--accent-red)' : 'var(--text-muted)' }}>
                        {item.degradation_rate > 0 ? `-${item.degradation_rate}/d` : '0'}
                      </td>
                      <td>
                        <span className={`trend-arrow ${getTrendClass(item.trend)}`}>
                          {getTrendIcon(item.trend)}
                          {item.trend.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td>
                        <span style={{
                          fontFamily: 'JetBrains Mono, monospace', fontSize: 11, fontWeight: 700,
                          color: item.failure_prob_30d > 0.5 ? 'var(--accent-red)' : item.failure_prob_30d > 0.2 ? 'var(--accent-orange)' : 'var(--accent-green)'
                        }}>
                          {(item.failure_prob_30d * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, fontWeight: 700, color: getRulColor(item.rul_days) }}>
                        {item.rul_days}d
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ThreeDCard>

          {/* Row 3: Anomaly Trends + ROI */}
          <div className="section-grid stagger-enter" style={{ gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
            <ThreeDCard className="card card-glass-ultra">
              <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Zap size={16} style={{ color: 'var(--accent-amber)' }} />
                Anomaly Detection Summary
              </h3>
              <div className="anomaly-grid">
                {data.anomaly_trends.filter(a => a.anomaly_count > 0).sort((a, b) => b.anomaly_count - a.anomaly_count).slice(0, 12).map(item => (
                  <Link href={`/equipment/${item.id}`} key={item.id} style={{ textDecoration: 'none' }}>
                    <div className="anomaly-mini-card">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '70%' }}>
                          {item.name}
                        </span>
                        <span className={`glow-indicator ${item.max_severity === 'critical' ? 'glow-red' : item.max_severity === 'high' ? 'glow-orange' : 'glow-blue'}`}
                          style={{ width: 6, height: 6 }} />
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)' }}>{item.anomaly_count}</span>
                        <span className={`trend-arrow ${getTrendClass(item.trend)}`} style={{ fontSize: 10 }}>
                          {getTrendIcon(item.trend)} {item.trend}
                        </span>
                      </div>
                      {/* Mini sparkline */}
                      <div className="sparkline-container" style={{ height: 20 }}>
                        {[...Array(7)].map((_, j) => {
                          const h = Math.max(3, Math.min(20, (item.anomaly_count / 10) * (4 + Math.sin(j * 1.5) * 3) * 3));
                          return (
                            <div key={j} className="sparkline-bar" style={{
                              height: h,
                              background: item.max_severity === 'critical' ? 'rgba(248, 113, 113, 0.6)' :
                                         item.max_severity === 'high' ? 'rgba(251, 146, 60, 0.6)' :
                                         'rgba(59, 130, 246, 0.5)',
                            }} />
                          );
                        })}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
              {data.anomaly_trends.filter(a => a.anomaly_count > 0).length === 0 && (
                <div className="empty-state" style={{ padding: 24 }}>
                  <p style={{ fontSize: 12 }}>✅ No anomalies detected across fleet</p>
                </div>
              )}
            </ThreeDCard>

            {/* ROI Calculator */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <ThreeDCard className="roi-card card-glass-ultra">
                <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <DollarSign size={16} style={{ color: 'var(--accent-green)' }} />
                  Predictive Maintenance ROI
                </h3>
                <div style={{ marginBottom: 8 }}>
                  <span style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                    Net Cost Savings
                  </span>
                  <div className="roi-value">{formatCurrency(roi.net_savings)}</div>
                </div>
                <div className="roi-breakdown">
                  <div className="roi-metric">
                    <span className="roi-metric-value">{roi.prevented_downtime_hours}h</span>
                    <span className="roi-metric-label">Prevented Downtime</span>
                  </div>
                  <div className="roi-metric">
                    <span className="roi-metric-value">{formatCurrency(roi.savings_from_prevention)}</span>
                    <span className="roi-metric-label">Avoided Losses</span>
                  </div>
                  <div className="roi-metric">
                    <span className="roi-metric-value">{formatCurrency(roi.planned_maintenance_cost)}</span>
                    <span className="roi-metric-label">Maint. Cost</span>
                  </div>
                </div>
              </ThreeDCard>

              <ThreeDCard className="card card-glass-ultra" style={{ flex: 1 }}>
                <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Clock size={16} style={{ color: 'var(--accent-cyan)' }} />
                  Cost Analysis Breakdown
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: 'rgba(248, 113, 113, 0.06)', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Unplanned Downtime Cost/Hr</span>
                    <span style={{ fontSize: 14, fontWeight: 800, color: 'var(--accent-red)', fontFamily: 'JetBrains Mono, monospace' }}>
                      $10,000
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: 'rgba(52, 211, 153, 0.06)', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Avg Planned Maint. Cost</span>
                    <span style={{ fontSize: 14, fontWeight: 800, color: 'var(--accent-green)', fontFamily: 'JetBrains Mono, monospace' }}>
                      $2,500
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: 'rgba(59, 130, 246, 0.06)', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>ROI Multiplier</span>
                    <span style={{ fontSize: 14, fontWeight: 800, color: 'var(--accent-blue-light)', fontFamily: 'JetBrains Mono, monospace' }}>
                      {roi.planned_maintenance_cost > 0 ? `${(roi.savings_from_prevention / roi.planned_maintenance_cost).toFixed(1)}x` : '∞'}
                    </span>
                  </div>
                </div>
              </ThreeDCard>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
