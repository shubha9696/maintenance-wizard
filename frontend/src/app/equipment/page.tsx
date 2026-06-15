'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import ThreeDCard from '@/components/ThreeDCard';
import Link from 'next/link';
import { Search, SlidersHorizontal, Cpu, ShieldAlert } from 'lucide-react';
import { API_BASE, getCachedData, setCachedData } from '@/lib/api';

interface Equipment {
  id: string;
  name: string;
  area: string;
  type: string;
  criticality: string;
  status: string;
  health_score: number;
  risk_level?: string;
  last_maintenance?: string;
}
export default function EquipmentPage() {
  const [equipment, setEquipment] = useState<Equipment[]>(() => {
    const cached = getCachedData('/api/equipment');
    return cached ? (cached.equipment || []) : [];
  });
  const [loading, setLoading] = useState(() => {
    return !getCachedData('/api/equipment');
  });
  const [filter, setFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    const cacheKey = '/api/equipment';
    fetch(`${API_BASE}${cacheKey}`)
      .then(r => r.json())
      .then(d => {
        setEquipment(d.equipment || []);
        setCachedData(cacheKey, d);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const status = params.get('status');
      if (status) {
        setStatusFilter(status);
      }
    }
  }, []);

  const areas = [...new Set(equipment.map(e => e.area))];

  const filtered = equipment.filter(e => {
    if (filter !== 'all' && e.area !== filter) return false;
    
    // Status/health filter
    if (statusFilter === 'healthy' && e.health_score < 80) return false;
    if (statusFilter === 'warning' && (e.health_score >= 80 || e.health_score < 50)) return false;
    if (statusFilter === 'critical' && e.health_score >= 50) return false;
    
    if (search && !e.name.toLowerCase().includes(search.toLowerCase()) &&
        !e.id.toLowerCase().includes(search.toLowerCase()) &&
        !e.type.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  // Sort by health score ascending (worst first)
  filtered.sort((a, b) => a.health_score - b.health_score);

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-container">
          <div className="page-header animate-fadeIn">
            <h1>Equipment Fleet</h1>
            <p>{equipment.length} assets monitoring active across {areas.length} sectors</p>
          </div>

          {/* Filters Panel */}
          <div style={{ display: 'flex', gap: 10, marginBottom: 24, flexWrap: 'wrap', alignItems: 'center' }} className="animate-fadeInUp">
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
              <Search size={16} style={{ position: 'absolute', left: 12, color: 'var(--text-muted)' }} />
              <input
                type="text"
                placeholder="Search fleet (ID, Name, Type)..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                style={{
                  background: 'var(--bg-input)', border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)', padding: '10px 14px 10px 36px', color: 'var(--text-primary)',
                  fontSize: 13, width: 280, outline: 'none', fontFamily: 'inherit',
                  transition: 'border-color 0.2s',
                }}
              />
            </div>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <SlidersHorizontal size={14} style={{ color: 'var(--text-muted)', marginRight: 4 }} />
              <button
                className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setFilter('all')}
                style={{ fontSize: 12, padding: '6px 12px' }}
              >
                All ({equipment.length})
              </button>
              {areas.map(area => (
                <button
                  key={area}
                  className={`btn ${filter === area ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => setFilter(area)}
                  style={{ fontSize: 12, padding: '6px 12px' }}
                >
                  {area} ({equipment.filter(e => e.area === area).length})
                </button>
              ))}
            </div>

            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 10, marginRight: 4 }}>Health:</span>
              <button
                className={`btn ${statusFilter === 'all' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setStatusFilter('all')}
                style={{ fontSize: 12, padding: '6px 12px' }}
              >
                All
              </button>
              <button
                className={`btn ${statusFilter === 'healthy' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setStatusFilter('healthy')}
                style={{ fontSize: 12, padding: '6px 12px', color: statusFilter === 'healthy' ? 'white' : 'var(--accent-green)' }}
              >
                Healthy (≥80)
              </button>
              <button
                className={`btn ${statusFilter === 'warning' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setStatusFilter('warning')}
                style={{ fontSize: 12, padding: '6px 12px', color: statusFilter === 'warning' ? 'white' : 'var(--accent-orange)' }}
              >
                Warning (50-79)
              </button>
            </div>
          </div>

          {loading ? (
            <div className="loading-container"><div className="loading-spinner"></div><span>Loading fleet data...</span></div>
          ) : (
            <div className="equipment-grid">
              {filtered.map((eq, i) => (
                <Link href={`/equipment/${eq.id}`} key={eq.id} style={{ textDecoration: 'none' }}>
                  <ThreeDCard className="equipment-card animate-fadeInUp" style={{ animationDelay: `${i * 0.02}s` }}>
                    <div className="equipment-card-header">
                      <div>
                        <h3 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <Cpu size={15} style={{ color: 'var(--accent-blue-light)' }} />
                          {eq.name}
                        </h3>
                        <div className="area-tag">{eq.area} • {eq.type}</div>
                      </div>
                      <span className={`health-badge ${eq.status}`} style={{ fontSize: 10, padding: '3px 8px' }}>
                        {eq.status.toUpperCase()}
                      </span>
                    </div>

                    <div className="health-bar-container">
                      <div className="health-bar-label">
                        <span>Health Score</span>
                        <span style={{
                          fontWeight: 'bold',
                          color: eq.health_score >= 80 ? 'var(--accent-green)' :
                                 eq.health_score >= 50 ? 'var(--accent-orange)' : 'var(--accent-red)'
                        }}>
                          {eq.health_score}%
                        </span>
                      </div>
                      <div className="health-bar">
                        <div
                          className={`health-bar-fill ${eq.health_score >= 80 ? 'good' : eq.health_score >= 50 ? 'warn' : 'bad'}`}
                          style={{ width: `${eq.health_score}%` }}
                        />
                      </div>
                    </div>

                    <div className="equipment-meta">
                      <div className="equipment-meta-item">
                        <span className="label">Criticality</span>
                        <span className="value" style={{
                          display: 'flex', alignItems: 'center', gap: 4, fontSize: 11,
                          color: eq.criticality === 'critical' ? 'var(--accent-red)' :
                                 eq.criticality === 'high' ? 'var(--accent-orange)' : 'var(--text-secondary)'
                        }}>
                          {eq.criticality === 'critical' && <ShieldAlert size={12} />}
                          {eq.criticality.toUpperCase()}
                        </span>
                      </div>
                      <div className="equipment-meta-item">
                        <span className="label">Risk Level</span>
                        <span className={`risk-badge ${eq.risk_level || 'low'}`} style={{ fontSize: 9, padding: '1px 6px' }}>
                          {eq.risk_level || 'low'}
                        </span>
                      </div>
                      <div className="equipment-meta-item">
                        <span className="label">Asset ID</span>
                        <span className="value" style={{ fontFamily: 'monospace' }}>{eq.id}</span>
                      </div>
                    </div>
                  </ThreeDCard>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
