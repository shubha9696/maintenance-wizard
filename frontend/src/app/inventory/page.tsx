'use client';

import { useState, useEffect, useRef } from 'react';
import Sidebar from '@/components/Sidebar';
import ThreeDCard from '@/components/ThreeDCard';
import { 
  Package, 
  Clock, 
  DollarSign, 
  Search, 
  AlertTriangle, 
  PlusCircle, 
  CheckCircle, 
  RefreshCw, 
  SlidersHorizontal, 
  Cpu, 
  ShieldAlert, 
  Wrench,
  AlertOctagon,
  X
} from 'lucide-react';
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

interface SparePart {
  name: string;
  part_no: string;
  cost: number;
  lead_time_days: number;
  stock: number;
}

interface GroupedParts {
  [category: string]: SparePart[];
}

interface RiskItem {
  equipmentId: string;
  equipmentName: string;
  equipmentType: string;
  healthScore: number;
  part: SparePart;
  exposureCost: number;
  area: string;
}

interface ToastMessage {
  id: string;
  text: string;
  type: 'success' | 'warning' | 'info';
}

export default function InventoryPage() {
  const [equipment, setEquipment] = useState<Equipment[]>(() => {
    const cachedEq = getCachedData('/api/equipment');
    return cachedEq ? (cachedEq.equipment || []) : [];
  });
  const [parts, setParts] = useState<GroupedParts>(() => {
    return getCachedData('/api/equipment/spare-parts/all') || {};
  });
  const [loading, setLoading] = useState(() => {
    const cachedEq = getCachedData('/api/equipment');
    const cachedParts = getCachedData('/api/equipment/spare-parts/all');
    return !(cachedEq && cachedParts);
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [stockFilter, setStockFilter] = useState<'all' | 'out' | 'low'>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'none' | 'cost_desc' | 'cost_asc' | 'lead_desc' | 'lead_asc'>('none');
  
  // PO & Countdown states
  const [selectedPO, setSelectedPO] = useState<{ category: string; part: SparePart; isExpedited?: boolean } | null>(null);
  const [activeOrders, setActiveOrders] = useState<{ [partNo: string]: { remaining: number; total: number; expedited?: boolean } }>({});
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  
  // Ref for the countdown timer
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Load backend data
  useEffect(() => {
    const cacheKeyEq = '/api/equipment';
    const cacheKeyParts = '/api/equipment/spare-parts/all';

    const fetchData = async () => {
      try {
        const [eqRes, partsRes] = await Promise.all([
          fetch(`${API_BASE}${cacheKeyEq}`),
          fetch(`${API_BASE}${cacheKeyParts}`)
        ]);
        
        const eqData = await eqRes.json();
        const partsData = await partsRes.json();
        
        setEquipment(eqData.equipment || []);
        setParts(partsData || {});
        setCachedData(cacheKeyEq, eqData);
        setCachedData(cacheKeyParts, partsData);
      } catch (err) {
        console.error('Error loading inventory data:', err);
        showToast('Failed to connect to backend server API.', 'warning');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  // Handle count-downs for active orders
  useEffect(() => {
    const activePartNumbers = Object.keys(activeOrders);
    if (activePartNumbers.length === 0) {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      return;
    }

    if (!timerRef.current) {
      timerRef.current = setInterval(() => {
        setActiveOrders(prev => {
          const next = { ...prev };
          let updated = false;

          for (const partNo of Object.keys(next)) {
            if (next[partNo].remaining > 1) {
              next[partNo] = {
                ...next[partNo],
                remaining: next[partNo].remaining - 1
              };
              updated = true;
            } else {
              // Time's up! Replenish stock.
              updated = true;
              delete next[partNo];
              
              // Increment stock count in our local parts state
              setParts(currentParts => {
                const updatedParts = { ...currentParts };
                for (const cat of Object.keys(updatedParts)) {
                  const partIdx = updatedParts[cat].findIndex(p => p.part_no === partNo);
                  if (partIdx !== -1) {
                    const originalPart = updatedParts[cat][partIdx];
                    const newPart = { ...originalPart, stock: originalPart.stock + 1 };
                    const newList = [...updatedParts[cat]];
                    newList[partIdx] = newPart;
                    updatedParts[cat] = newList;
                    
                    // Trigger dynamic success Toast
                    showToast(`Replenished: 1 unit of ${originalPart.name} (${originalPart.part_no}) has arrived!`, 'success');
                    break;
                  }
                }
                return updatedParts;
              });
            }
          }

          return updated ? next : prev;
        });
      }, 1000);
    }

    return () => {
      if (timerRef.current && Object.keys(activeOrders).length === 0) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [activeOrders]);

  const showToast = (text: string, type: 'success' | 'warning' | 'info' = 'info') => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts(prev => [...prev, { id, text, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  // Calculate high-risk items dynamically
  // Degraded assets (health_score < 70) with out-of-stock spares (stock === 0)
  const getRiskItems = (): RiskItem[] => {
    const items: RiskItem[] = [];
    const degradedAssets = equipment.filter(e => e.health_score < 70);
    
    degradedAssets.forEach(eq => {
      const categorySpares = parts[eq.type] || [];
      const outOfStockSpares = categorySpares.filter(p => p.stock === 0 && !activeOrders[p.part_no]);
      
      outOfStockSpares.forEach(part => {
        // Exposure cost = part cost + production loss rate of $10,000/day * lead time
        // E.g., if lead time is 60 days, exposure is cost + $600,000
        const productionLossRate = 10000;
        const exposureCost = part.cost + (productionLossRate * part.lead_time_days);
        
        items.push({
          equipmentId: eq.id,
          equipmentName: eq.name,
          equipmentType: eq.type,
          healthScore: eq.health_score,
          part,
          exposureCost,
          area: eq.area
        });
      });
    });
    
    return items.sort((a, b) => b.exposureCost - a.exposureCost);
  };

  const riskItems = getRiskItems();
  const totalRiskExposure = riskItems.reduce((acc, curr) => acc + curr.exposureCost, 0);

  // Calculate overall catalog statistics
  const getInventoryStats = () => {
    let totalItems = 0;
    let outOfStockCount = 0;
    let lowStockCount = 0; // stock === 1 or 2
    let totalValue = 0;

    Object.values(parts).forEach(list => {
      list.forEach(p => {
        totalItems++;
        if (p.stock === 0) {
          outOfStockCount++;
        } else if (p.stock <= 2) {
          lowStockCount++;
        }
        totalValue += p.stock * p.cost;
      });
    });

    return {
      totalItems,
      outOfStockCount,
      lowStockCount,
      totalValue
    };
  };

  const stats = getInventoryStats();

  // Handle PO initiation
  const initiatePO = (category: string, part: SparePart, isExpedited = false) => {
    setSelectedPO({ category, part, isExpedited });
  };

  const confirmPO = () => {
    if (!selectedPO) return;
    const { part, isExpedited } = selectedPO;
    
    // Check if already being ordered
    if (activeOrders[part.part_no]) {
      showToast(`Part ${part.part_no} is already in transit.`, 'info');
      setSelectedPO(null);
      return;
    }

    // Set countdown duration
    // Standard order = 10s, Expedited order = 5s for visualization purposes
    const duration = isExpedited ? 5 : 10;

    setActiveOrders(prev => ({
      ...prev,
      [part.part_no]: {
        remaining: duration,
        total: duration,
        expedited: isExpedited
      }
    }));

    showToast(`Purchase Order authorized for ${part.name}. Order status: In Transit.`, 'info');
    setSelectedPO(null);
  };

  // Compile final filtered & sorted flat list of parts
  const getFilteredPartsList = () => {
    let list: { category: string; part: SparePart }[] = [];

    Object.keys(parts).forEach(category => {
      if (selectedCategory !== 'all' && selectedCategory !== category) return;

      parts[category].forEach(part => {
        // Search filter
        const matchesSearch = 
          part.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          part.part_no.toLowerCase().includes(searchTerm.toLowerCase());
        if (!matchesSearch) return;

        // Stock level filter
        if (stockFilter === 'out' && part.stock > 0) return;
        if (stockFilter === 'low' && (part.stock === 0 || part.stock > 2)) return;

        list.push({ category, part });
      });
    });

    // Sorting
    if (sortBy === 'cost_desc') {
      list.sort((a, b) => b.part.cost - a.part.cost);
    } else if (sortBy === 'cost_asc') {
      list.sort((a, b) => a.part.cost - b.part.cost);
    } else if (sortBy === 'lead_desc') {
      list.sort((a, b) => b.part.lead_time_days - a.part.lead_time_days);
    } else if (sortBy === 'lead_asc') {
      list.sort((a, b) => a.part.lead_time_days - b.part.lead_time_days);
    }

    return list;
  };

  const filteredParts = getFilteredPartsList();
  const categories = Object.keys(parts);

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-container animate-fadeIn">
          {/* Header */}
          <div className="page-header" style={{ marginBottom: 20 }}>
            <h1>Industrial Spares & Risk Optimizer</h1>
            <p>AI-driven logistics monitoring, out-of-stock risk valuation, and instant procurement dispatch</p>
          </div>

          {/* Toast Notification Container */}
          <div style={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
            zIndex: 9999,
            maxWidth: 380
          }}>
            {toasts.map(toast => (
              <div key={toast.id} className="animate-slideInRight" style={{
                background: toast.type === 'success' ? 'rgba(6, 78, 59, 0.95)' : toast.type === 'warning' ? 'rgba(127, 29, 29, 0.95)' : 'rgba(30, 41, 59, 0.95)',
                color: 'var(--text-primary)',
                border: `1px solid ${toast.type === 'success' ? 'var(--accent-green)' : toast.type === 'warning' ? 'var(--accent-red)' : 'var(--border-color)'}`,
                boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
                borderRadius: 'var(--radius-sm)',
                padding: '12px 16px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: 12,
                backdropFilter: 'blur(8px)'
              }}>
                <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                  {toast.type === 'success' ? (
                    <CheckCircle size={18} style={{ color: 'var(--accent-green)', flexShrink: 0, marginTop: 1 }} />
                  ) : toast.type === 'warning' ? (
                    <AlertTriangle size={18} style={{ color: 'var(--accent-red)', flexShrink: 0, marginTop: 1 }} />
                  ) : (
                    <Package size={18} style={{ color: 'var(--accent-blue-light)', flexShrink: 0, marginTop: 1 }} />
                  )}
                  <span style={{ fontSize: 12.5, fontWeight: 500, lineHeight: 1.4 }}>{toast.text}</span>
                </div>
                <button 
                  onClick={() => removeToast(toast.id)} 
                  style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', padding: 0 }}
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>

          {/* Stats Bar */}
          <div className="stats-container" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 20 }}>
            <div className="stat-card" style={{ display: 'flex', alignItems: 'center', gap: 16, background: 'var(--bg-card)', padding: '16px 20px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ width: 44, height: 44, borderRadius: '50%', background: 'rgba(59, 130, 246, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-blue-light)' }}>
                <Package size={22} />
              </div>
              <div>
                <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Cataloged Spares</span>
                <h3 style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-primary)', margin: '4px 0 0' }}>{stats.totalItems}</h3>
              </div>
            </div>

            <div className="stat-card" style={{ display: 'flex', alignItems: 'center', gap: 16, background: 'var(--bg-card)', padding: '16px 20px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ width: 44, height: 44, borderRadius: '50%', background: 'rgba(239, 68, 68, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-red)' }}>
                <ShieldAlert size={22} />
              </div>
              <div>
                <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Out of Stock Spares</span>
                <h3 style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-primary)', margin: '4px 0 0' }}>{stats.outOfStockCount}</h3>
              </div>
            </div>

            <div className="stat-card" style={{ display: 'flex', alignItems: 'center', gap: 16, background: 'var(--bg-card)', padding: '16px 20px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ width: 44, height: 44, borderRadius: '50%', background: 'rgba(245, 158, 11, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-orange)' }}>
                <AlertTriangle size={22} />
              </div>
              <div>
                <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Low Stock Spares</span>
                <h3 style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-primary)', margin: '4px 0 0' }}>{stats.lowStockCount}</h3>
              </div>
            </div>

            <div className="stat-card" style={{ display: 'flex', alignItems: 'center', gap: 16, background: 'var(--bg-card)', padding: '16px 20px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ width: 44, height: 44, borderRadius: '50%', background: 'rgba(16, 185, 129, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-green)' }}>
                <DollarSign size={22} />
              </div>
              <div>
                <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>On-Hand Value</span>
                <h3 style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-primary)', margin: '4px 0 0' }}>₹{stats.totalValue.toLocaleString()}</h3>
              </div>
            </div>
          </div>

          {/* Risk Exposure Banner */}
          {riskItems.length > 0 ? (
            <div className="animate-fadeIn" style={{
              background: 'radial-gradient(circle at 10% 20%, rgba(127, 29, 29, 0.35) 0%, rgba(26, 12, 12, 0.8) 100%)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              boxShadow: '0 0 20px rgba(239, 68, 68, 0.15), inset 0 0 10px rgba(239, 68, 68, 0.1)',
              borderRadius: 'var(--radius-md)',
              padding: '20px 24px',
              marginBottom: 24,
              position: 'relative',
              overflow: 'hidden'
            }}>
              <div style={{ position: 'absolute', right: -20, bottom: -20, opacity: 0.05, transform: 'rotate(15deg)' }}>
                <AlertOctagon size={160} color="red" />
              </div>

              <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
                <div style={{
                  width: 52, height: 52, borderRadius: 'var(--radius-sm)',
                  background: 'rgba(239, 68, 68, 0.15)',
                  border: '1px solid var(--accent-red)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--accent-red)',
                  animation: 'pulse-glow 1.5s infinite ease-in-out',
                  flexShrink: 0
                }}>
                  <AlertOctagon size={28} />
                </div>
                
                <div style={{ flex: 1, minWidth: 260 }}>
                  <span style={{ fontSize: 10, fontWeight: 800, textTransform: 'uppercase', letterSpacing: 1, color: 'var(--accent-red)', display: 'block' }}>
                    Critical Spares Shortage Risk Alert
                  </span>
                  <h2 style={{ fontSize: 20, fontWeight: 900, color: 'var(--text-primary)', margin: '4px 0' }}>
                    Production Downtime Risk Exposure: <span style={{ color: 'var(--accent-red)' }}>₹{totalRiskExposure.toLocaleString()}</span>
                  </h2>
                  <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0 }}>
                    There are <strong>{riskItems.length}</strong> degraded or critical plant assets missing matching spare parts. Production losses accumulate daily during parts lead-time.
                  </p>
                </div>
              </div>

              {/* Risk Exposure Table */}
              <div style={{ marginTop: 16, borderTop: '1px solid rgba(239, 68, 68, 0.2)', paddingTop: 16 }}>
                <h4 style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 10, letterSpacing: 0.5 }}>
                  Active Exposure Breakdown (Loss Cost = Part Cost + Lead Time × ₹10,000/day)
                </h4>
                
                <div style={{ overflowX: 'auto' }}>
                  <table className="data-table" style={{ border: 'none' }}>
                    <thead>
                      <tr>
                        <th style={{ background: 'transparent', borderBottom: '1px solid rgba(239, 68, 68, 0.2)', color: 'var(--text-muted)' }}>Degraded Asset</th>
                        <th style={{ background: 'transparent', borderBottom: '1px solid rgba(239, 68, 68, 0.2)', color: 'var(--text-muted)' }}>Health</th>
                        <th style={{ background: 'transparent', borderBottom: '1px solid rgba(239, 68, 68, 0.2)', color: 'var(--text-muted)' }}>Missing Spare Part</th>
                        <th style={{ background: 'transparent', borderBottom: '1px solid rgba(239, 68, 68, 0.2)', color: 'var(--text-muted)', textAlign: 'center' }}>Lead Time</th>
                        <th style={{ background: 'transparent', borderBottom: '1px solid rgba(239, 68, 68, 0.2)', color: 'var(--text-muted)', textAlign: 'right' }}>Risk Valuation</th>
                        <th style={{ background: 'transparent', borderBottom: '1px solid rgba(239, 68, 68, 0.2)', color: 'var(--text-muted)', textAlign: 'center' }}>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {riskItems.map((item, idx) => (
                        <tr key={idx} style={{ background: 'transparent' }}>
                          <td style={{ borderBottom: '1px solid rgba(239, 68, 68, 0.1)', fontWeight: 700, color: 'var(--text-primary)' }}>
                            {item.equipmentName}
                            <span style={{ display: 'block', fontSize: 10, fontWeight: 400, color: 'var(--text-muted)' }}>
                              {item.area} • ID: {item.equipmentId}
                            </span>
                          </td>
                          <td style={{ borderBottom: '1px solid rgba(239, 68, 68, 0.1)' }}>
                            <span className="risk-badge critical" style={{ fontSize: 10, padding: '2px 6px', fontWeight: 700 }}>
                              {item.healthScore.toFixed(1)}%
                            </span>
                          </td>
                          <td style={{ borderBottom: '1px solid rgba(239, 68, 68, 0.1)', color: 'var(--text-secondary)' }}>
                            {item.part.name}
                            <span style={{ display: 'block', fontSize: 10, fontFamily: 'monospace', color: 'var(--text-muted)' }}>
                              {item.part.part_no} • Cost: ₹{item.part.cost.toLocaleString()}
                            </span>
                          </td>
                          <td style={{ borderBottom: '1px solid rgba(239, 68, 68, 0.1)', textAlign: 'center', fontWeight: 600, color: 'var(--accent-orange)' }}>
                            {item.part.lead_time_days} Days
                          </td>
                          <td style={{ borderBottom: '1px solid rgba(239, 68, 68, 0.1)', textAlign: 'right', fontWeight: 800, color: 'var(--accent-red)' }}>
                            ₹{item.exposureCost.toLocaleString()}
                          </td>
                          <td style={{ borderBottom: '1px solid rgba(239, 68, 68, 0.1)', textAlign: 'center' }}>
                            <button
                              className="btn btn-primary"
                              onClick={() => initiatePO(item.equipmentType, item.part, true)}
                              style={{
                                padding: '4px 10px',
                                fontSize: 10.5,
                                background: 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)',
                                boxShadow: '0 2px 8px rgba(239, 68, 68, 0.3)',
                                border: 'none'
                              }}
                            >
                              Expedite PO
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : !loading && (
            <div style={{
              background: 'rgba(6, 78, 59, 0.2)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: 'var(--radius-md)',
              padding: '16px 20px',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              color: 'var(--accent-green)',
              marginBottom: 24
            }}>
              <CheckCircle size={20} />
              <span style={{ fontSize: 13, fontWeight: 600 }}>
                Logistics Safe Zone: All critical assets have spare parts fully stocked. No active downtime exposure detected.
              </span>
            </div>
          )}

          {/* Search, Filter & Sort Row */}
          <div style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: 16,
            marginBottom: 20,
            display: 'flex',
            flexDirection: 'column',
            gap: 14
          }}>
            {/* First line: Search + filters */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', flex: 1, minWidth: 260, position: 'relative' }}>
                <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  placeholder="Search spare parts by name or part number..."
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'var(--bg-input)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '8px 12px 8px 36px',
                    fontSize: 13,
                    color: 'var(--text-primary)',
                    outline: 'none'
                  }}
                />
              </div>

              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <SlidersHorizontal size={14} style={{ color: 'var(--text-muted)' }} />
                <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginRight: 4 }}>Filter Stock:</span>
                
                <button
                  onClick={() => setStockFilter('all')}
                  className={`btn ${stockFilter === 'all' ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ padding: '6px 12px', fontSize: 11.5 }}
                >
                  All
                </button>
                <button
                  onClick={() => setStockFilter('out')}
                  className={`btn ${stockFilter === 'out' ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ padding: '6px 12px', fontSize: 11.5, color: stockFilter === 'out' ? 'white' : 'var(--accent-red)' }}
                >
                  Out of Stock
                </button>
                <button
                  onClick={() => setStockFilter('low')}
                  className={`btn ${stockFilter === 'low' ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ padding: '6px 12px', fontSize: 11.5, color: stockFilter === 'low' ? 'white' : 'var(--accent-amber)' }}
                >
                  Low Stock
                </button>
              </div>
            </div>

            {/* Second line: Categories + Sort */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid rgba(148, 163, 184, 0.08)', paddingTop: 12 }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                <button
                  onClick={() => setSelectedCategory('all')}
                  className={`btn ${selectedCategory === 'all' ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ padding: '4px 10px', fontSize: 11 }}
                >
                  All Asset Types
                </button>
                {categories.map(cat => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`btn ${selectedCategory === cat ? 'btn-primary' : 'btn-ghost'}`}
                    style={{ padding: '4px 10px', fontSize: 11 }}
                  >
                    {cat}
                  </button>
                ))}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Sort By:</span>
                <select
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value as any)}
                  style={{
                    background: 'var(--bg-input)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '4px 8px',
                    fontSize: 11.5,
                    color: 'var(--text-primary)',
                    outline: 'none',
                    cursor: 'pointer'
                  }}
                >
                  <option value="none">Default</option>
                  <option value="cost_desc">Cost: High to Low</option>
                  <option value="cost_asc">Cost: Low to High</option>
                  <option value="lead_desc">Lead Time: Longest</option>
                  <option value="lead_asc">Lead Time: Shortest</option>
                </select>
              </div>
            </div>
          </div>

          {/* Spares Catalog Grid */}
          {loading ? (
            <div className="loading-container" style={{ padding: '60px 0' }}>
              <div className="loading-spinner"></div>
              <span>Fetching spares inventory directory...</span>
            </div>
          ) : (
            <div>
              {filteredParts.length === 0 ? (
                <div style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-md)',
                  padding: 40,
                  textAlign: 'center',
                  color: 'var(--text-muted)'
                }}>
                  <Package size={36} style={{ opacity: 0.3, marginBottom: 12, margin: '0 auto' }} />
                  <p style={{ fontSize: 14 }}>No spare parts matching your current filters were found.</p>
                </div>
              ) : (
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                  gap: 16
                }}>
                  {filteredParts.map(({ category, part }) => {
                    const isOrdering = !!activeOrders[part.part_no];
                    const orderState = activeOrders[part.part_no];
                    const progressPercent = isOrdering ? ((orderState.total - orderState.remaining) / orderState.total) * 100 : 0;
                    
                    return (
                      <ThreeDCard key={part.part_no} style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 220 }}>
                        {/* Card Header */}
                        <div style={{ borderBottom: '1px solid rgba(148, 163, 184, 0.08)', paddingBottom: 10, marginBottom: 12 }}>
                          <span style={{ fontSize: 10, color: 'var(--accent-blue-light)', fontWeight: 700, textTransform: 'uppercase', display: 'block' }}>
                            {category}
                          </span>
                          <h3 style={{ fontSize: 14, fontWeight: 800, color: 'var(--text-primary)', margin: '4px 0 2px', lineHeight: 1.3 }}>
                            {part.name}
                          </h3>
                          <span style={{ fontSize: 10.5, fontFamily: 'monospace', color: 'var(--text-muted)' }}>
                            PART NO: {part.part_no}
                          </span>
                        </div>

                        {/* Card Details */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: 12.5, color: 'var(--text-secondary)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Stock Level:</span>
                            {isOrdering ? (
                              <span style={{ color: 'var(--accent-blue-light)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
                                <RefreshCw size={11} className="animate-spin" /> In Transit
                              </span>
                            ) : part.stock === 0 ? (
                              <span style={{
                                color: 'var(--accent-red)', fontWeight: 800,
                                background: 'rgba(239, 68, 68, 0.1)', padding: '2px 8px',
                                borderRadius: 'var(--radius-sm)', border: '1px solid rgba(239, 68, 68, 0.2)',
                                animation: 'pulse-glow 1.5s infinite ease-in-out'
                              }}>
                                OUT OF STOCK
                              </span>
                            ) : part.stock <= 2 ? (
                              <span style={{
                                color: 'var(--accent-amber)', fontWeight: 800,
                                background: 'rgba(245, 158, 11, 0.1)', padding: '2px 8px',
                                borderRadius: 'var(--radius-sm)', border: '1px solid rgba(245, 158, 11, 0.2)'
                              }}>
                                LOW STOCK ({part.stock})
                              </span>
                            ) : (
                              <span style={{
                                color: 'var(--accent-green)', fontWeight: 700,
                                background: 'rgba(16, 185, 129, 0.08)', padding: '2px 8px',
                                borderRadius: 'var(--radius-sm)'
                              }}>
                                IN STOCK ({part.stock})
                              </span>
                            )}
                          </div>

                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Unit Cost:</span>
                            <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>₹{part.cost.toLocaleString()}</span>
                          </div>

                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Standard Lead Time:</span>
                            <span style={{ fontWeight: 600 }}>{part.lead_time_days} Days</span>
                          </div>
                        </div>

                        {/* Order Progress Bar */}
                        {isOrdering && (
                          <div style={{ marginTop: 14 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-muted)', marginBottom: 4 }}>
                              <span>Procuring (Expedited: {orderState.expedited ? 'Yes' : 'No'})...</span>
                              <span>{orderState.remaining}s remaining</span>
                            </div>
                            <div style={{ width: '100%', height: 4, background: 'var(--border-color)', borderRadius: 2, overflow: 'hidden' }}>
                              <div style={{
                                width: `${progressPercent}%`,
                                height: '100%',
                                background: 'var(--accent-blue-light)',
                                transition: 'width 1s linear'
                              }} />
                            </div>
                          </div>
                        )}

                        {/* Card Actions */}
                        <div style={{ marginTop: 'auto', paddingTop: 16 }}>
                          {isOrdering ? (
                            <button
                              disabled
                              className="btn btn-ghost"
                              style={{ width: '100%', justifyContent: 'center', fontSize: 11.5, opacity: 0.6, cursor: 'not-allowed' }}
                            >
                              Dispatching Cargo Carrier...
                            </button>
                          ) : (
                            <button
                              onClick={() => initiatePO(category, part)}
                              className={`btn ${part.stock === 0 ? 'btn-primary' : 'btn-ghost'}`}
                              style={{
                                width: '100%',
                                justifyContent: 'center',
                                fontSize: 11.5,
                                fontWeight: 700,
                                border: part.stock === 0 ? 'none' : '1px solid var(--border-color)'
                              }}
                            >
                              <PlusCircle size={14} /> 1-Click Purchase Order
                            </button>
                          )}
                        </div>
                      </ThreeDCard>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* PO Order Confirmation Modal */}
          {selectedPO && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(5, 7, 12, 0.85)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 99999,
              backdropFilter: 'blur(4px)'
            }} className="animate-fadeIn">
              <div style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
                borderRadius: 'var(--radius-md)',
                width: '100%',
                maxWidth: 440,
                padding: 24,
                position: 'relative'
              }} className="animate-scaleIn">
                <button
                  onClick={() => setSelectedPO(null)}
                  style={{
                    position: 'absolute',
                    top: 16,
                    right: 16,
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                    display: 'flex'
                  }}
                >
                  <X size={18} />
                </button>

                <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 16 }}>
                  <div style={{
                    width: 38, height: 38, borderRadius: '50%',
                    background: 'rgba(59, 130, 246, 0.1)', display: 'flex',
                    alignItems: 'center', justifyContent: 'center', color: 'var(--accent-blue-light)'
                  }}>
                    <Wrench size={18} />
                  </div>
                  <div>
                    <h3 style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                      Confirm Purchase Order
                    </h3>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>AI Procurement Dispatch Network</span>
                  </div>
                </div>

                <div style={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)',
                  padding: 14,
                  marginBottom: 16,
                  fontSize: 12.5,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 8
                }}>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Spare Part:</span>
                    <strong style={{ display: 'block', color: 'var(--text-primary)', marginTop: 2 }}>
                      {selectedPO.part.name}
                    </strong>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 4 }}>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Part Number:</span>
                      <span style={{ display: 'block', fontWeight: 600, marginTop: 2, fontFamily: 'monospace' }}>
                        {selectedPO.part.part_no}
                      </span>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Standard Lead:</span>
                      <span style={{ display: 'block', fontWeight: 600, marginTop: 2 }}>
                        {selectedPO.part.lead_time_days} Days
                      </span>
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 12.5, marginBottom: 20 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Item Cost:</span>
                    <span style={{ fontWeight: 600 }}>₹{selectedPO.part.cost.toLocaleString()}</span>
                  </div>
                  
                  {selectedPO.isExpedited && (
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--accent-orange)' }}>
                      <span>Expedited Air Shipping:</span>
                      <span style={{ fontWeight: 600 }}>+₹1,500</span>
                    </div>
                  )}

                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Supplier:</span>
                    <span>TATA Industrial Logistics</span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-color)', paddingTop: 8, marginTop: 4 }}>
                    <strong style={{ color: 'var(--text-primary)' }}>Total Order Cost:</strong>
                    <strong style={{ color: 'var(--accent-blue-light)', fontSize: 14 }}>
                      ₹{(selectedPO.part.cost + (selectedPO.isExpedited ? 1500 : 0)).toLocaleString()}
                    </strong>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    onClick={() => setSelectedPO(null)}
                    className="btn btn-ghost"
                    style={{ flex: 1, justifyContent: 'center', fontSize: 12 }}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={confirmPO}
                    className="btn btn-primary"
                    style={{ 
                      flex: 1.5, 
                      justifyContent: 'center', 
                      fontSize: 12,
                      background: selectedPO.isExpedited ? 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)' : 'var(--gradient-primary)'
                    }}
                  >
                    {selectedPO.isExpedited ? 'Dispatch Expedited PO' : 'Authorize Order'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
