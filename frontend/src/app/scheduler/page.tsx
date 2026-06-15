'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import ThreeDCard from '@/components/ThreeDCard';
import Link from 'next/link';
import { Calendar, User, Wrench, ShieldCheck, Clock, CheckCircle, AlertTriangle } from 'lucide-react';
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
}

interface MaintenanceTask {
  id: string;
  equipmentId: string;
  equipmentName: string;
  area: string;
  action: string;
  technician: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  startDay: number; // 0 = Mon, 6 = Sun
  duration: number; // in days
  sparesStatus: 'In Stock' | 'Out of Stock';
  durationHours: number;
}

const DAYS_OF_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

function generateTasksList(assets: Equipment[]): MaintenanceTask[] {
  const list: MaintenanceTask[] = [];
  
  // Sort assets by health score ascending (worst first)
  const sorted = [...assets].sort((a, b) => a.health_score - b.health_score);

  sorted.forEach((eq) => {
    let priority: 'critical' | 'high' | 'medium' | 'low' = 'low';
    let startDay = 5; 
    let duration = 1;
    let action = 'Routine Lubrication & Clean';
    let technician = 'R. Kumar';
    let durationHours = 2;
    let sparesStatus: 'In Stock' | 'Out of Stock' = 'In Stock';

    if (eq.health_score < 50 || eq.risk_level === 'critical') {
      priority = 'critical';
      startDay = 0; // Monday
      duration = 2; // Spans 2 days
      action = 'Emergency Bearings Swap & Shaft Realignment';
      technician = 'H. Prasad (Senior Lead Specialist)';
      durationHours = 8;
      sparesStatus = 'In Stock';
    } else if (eq.health_score < 70 || eq.risk_level === 'high') {
      priority = 'high';
      startDay = 2; // Wednesday
      duration = 1;
      action = 'Thermal Overload Sweep & Coil Re-winding';
      technician = 'M. Singh';
      durationHours = 4;
      sparesStatus = 'In Stock';
    } else if (eq.health_score < 80 || eq.risk_level === 'medium') {
      priority = 'medium';
      startDay = 3; // Thursday
      duration = 1;
      action = 'Filter Core Flush & Hydraulic Seal Check';
      technician = 'S. Chawla';
      durationHours = 3;
      sparesStatus = 'Out of Stock';
    } else if (eq.criticality === 'critical') {
      priority = 'low';
      startDay = 4; // Friday
      duration = 1;
      action = 'Vibration Drift Check & Coupling Calibration';
      technician = 'A. Sengupta';
      durationHours = 2;
      sparesStatus = 'In Stock';
    } else {
      return; // Skip normal healthy items to keep Gantt clean
    }

    list.push({
      id: `task-${eq.id}`,
      equipmentId: eq.id,
      equipmentName: eq.name,
      area: eq.area,
      action,
      technician,
      priority,
      startDay,
      duration,
      sparesStatus,
      durationHours
    });
  });

  return list;
}

export default function SchedulerPage() {
  const [equipment, setEquipment] = useState<Equipment[]>(() => {
    const cached = getCachedData('/api/equipment');
    return cached ? (cached.equipment || []) : [];
  });
  const [loading, setLoading] = useState(() => {
    return !getCachedData('/api/equipment');
  });
  
  const [tasks, setTasks] = useState<MaintenanceTask[]>(() => {
    const cached = getCachedData('/api/equipment');
    return cached ? generateTasksList(cached.equipment || []) : [];
  });
  
  const [selectedTask, setSelectedTask] = useState<MaintenanceTask | null>(() => {
    const cached = getCachedData('/api/equipment');
    const list = cached ? generateTasksList(cached.equipment || []) : [];
    return list.length > 0 ? list[0] : null;
  });

  useEffect(() => {
    const cacheKey = '/api/equipment';
    fetch(`${API_BASE}${cacheKey}`)
      .then(r => r.json())
      .then(d => {
        const list = d.equipment || [];
        setEquipment(list);
        
        const generated = generateTasksList(list);
        setTasks(generated);
        setSelectedTask(prev => {
          if (prev) {
            // Keep selection if it exists in the new list
            const found = generated.find(t => t.id === prev.id);
            return found || (generated.length > 0 ? generated[0] : null);
          }
          return generated.length > 0 ? generated[0] : null;
        });
        
        setCachedData(cacheKey, d);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-container animate-fadeIn">
          <div className="page-header">
            <h1>Dynamic Gantt Scheduler</h1>
            <p>AI-prioritized 7-day maintenance timeline based on asset health risks and spares logistics</p>
          </div>

          {loading ? (
            <div className="loading-container"><div className="loading-spinner"></div><span>Compiling timeline...</span></div>
          ) : (
            <div className="section-grid" style={{ gridTemplateColumns: '2.2fr 1fr', gap: 16 }}>
              {/* Gantt Timeline wrapper */}
              <div>
                <ThreeDCard className="gantt-wrapper">
                  <div className="gantt-header-row">
                    <div className="gantt-col-header asset">Asset Description</div>
                    {DAYS_OF_WEEK.map(day => (
                      <div key={day} className="gantt-col-header">{day}</div>
                    ))}
                  </div>

                  {tasks.length === 0 ? (
                    <div className="empty-state" style={{ padding: 40 }}>
                      <p>✅ All fleet assets reporting normal parameters. No tasks scheduled.</p>
                    </div>
                  ) : (
                    tasks.map(task => (
                      <div key={task.id} className="gantt-row">
                        <div className="gantt-asset-info">
                          <span className="gantt-asset-name">{task.equipmentName}</span>
                          <span className="gantt-asset-area">{task.area} • <span style={{ fontFamily: 'monospace' }}>{task.equipmentId}</span></span>
                        </div>
                        
                        <div style={{ display: 'contents' }}>
                          {DAYS_OF_WEEK.map((_, dayIndex) => {
                            const isStart = dayIndex === task.startDay;
                            return (
                              <div key={dayIndex} className="gantt-cell">
                                {isStart && (
                                  <div
                                    className={`gantt-bar ${task.priority}`}
                                    style={{
                                      gridColumn: `span ${task.duration}`,
                                      width: `calc(${task.duration * 100}% - 8px)`,
                                      zIndex: 10,
                                      outline: selectedTask?.id === task.id ? '2px solid var(--accent-blue-light)' : 'none'
                                    }}
                                    onClick={() => setSelectedTask(task)}
                                  >
                                    {task.action}
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ))
                  )}
                </ThreeDCard>
              </div>

              {/* Task Detail Card */}
              <div>
                {selectedTask ? (
                  <ThreeDCard className="card animate-slideInRight" style={{ display: 'flex', flexDirection: 'column', gap: 16, minHeight: 420 }}>
                    <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: 12 }}>
                      <span className={`risk-badge ${selectedTask.priority}`} style={{ fontSize: 9, marginBottom: 8 }}>
                        {selectedTask.priority.toUpperCase()} PRIORITY
                      </span>
                      <h2 style={{ fontSize: 16, fontWeight: 800, color: 'var(--text-primary)', marginTop: 4 }}>
                        {selectedTask.equipmentName}
                      </h2>
                      <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Asset ID: {selectedTask.equipmentId}</span>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                      <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                        <Wrench size={16} style={{ color: 'var(--accent-blue-light)', marginTop: 2, flexShrink: 0 }} />
                        <div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Scope of Work</div>
                          <div style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 600, marginTop: 2 }}>{selectedTask.action}</div>
                        </div>
                      </div>

                      <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                        <User size={16} style={{ color: 'var(--accent-blue-light)', marginTop: 2, flexShrink: 0 }} />
                        <div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Assigned Engineer</div>
                          <div style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 600, marginTop: 2 }}>{selectedTask.technician}</div>
                        </div>
                      </div>

                      <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                        <Clock size={16} style={{ color: 'var(--accent-blue-light)', marginTop: 2, flexShrink: 0 }} />
                        <div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Estimated Downtime</div>
                          <div style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 600, marginTop: 2 }}>{selectedTask.durationHours} Hours</div>
                        </div>
                      </div>

                      <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                        <ShieldCheck size={16} style={{ color: 'var(--accent-blue-light)', marginTop: 2, flexShrink: 0 }} />
                        <div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Spare Parts Verification</div>
                          <div style={{
                            fontSize: 13, fontWeight: 700, marginTop: 2,
                            color: selectedTask.sparesStatus === 'In Stock' ? 'var(--accent-green)' : 'var(--accent-red)'
                          }}>
                            {selectedTask.sparesStatus.toUpperCase()}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
                      <button
                        className="btn btn-primary"
                        onClick={() => {
                          alert(`Job dispatched. Notification sent to technician: ${selectedTask.technician}.`);
                        }}
                        style={{ width: '100%', justifyContent: 'center', fontSize: 12 }}
                      >
                        <CheckCircle size={14} /> Dispatch Technician
                      </button>
                      <Link
                        href={`/equipment/${selectedTask.equipmentId}`}
                        className="btn btn-ghost"
                        style={{ width: '100%', justifyContent: 'center', fontSize: 12 }}
                      >
                        View Telemetry Stream
                      </Link>
                    </div>
                  </ThreeDCard>
                ) : (
                  <ThreeDCard className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 420 }}>
                    <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                      <Calendar size={36} style={{ opacity: 0.3, marginBottom: 12 }} />
                      <p style={{ fontSize: 13 }}>Select any schedule bar to view diagnostic briefs</p>
                    </div>
                  </ThreeDCard>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
