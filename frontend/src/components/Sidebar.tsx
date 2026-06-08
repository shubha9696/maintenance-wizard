'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Bot, Wrench, Bell, FileText, Activity, AlertTriangle, FileSpreadsheet, Calendar, Package, Cpu, TrendingUp, Award, Database } from 'lucide-react';
import { API_BASE } from '@/lib/api';

export default function Sidebar() {
  const pathname = usePathname();
  const [alertCount, setAlertCount] = useState(0);
  const [clock, setClock] = useState('');
  const [uptime, setUptime] = useState('');

  useEffect(() => {
    fetch(`${API_BASE}/api/alerts/summary`)
      .then(r => r.json())
      .then(d => setAlertCount(d.critical + d.high))
      .catch(() => {});
  }, []);

  // Live clock
  useEffect(() => {
    const update = () => {
      const now = new Date();
      setClock(now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }));
      // Simulated uptime
      const hrs = Math.floor((Date.now() % 86400000) / 3600000);
      const mins = Math.floor((Date.now() % 3600000) / 60000);
      setUptime(`${hrs}h ${mins}m`);
    };
    update();
    const timer = setInterval(update, 1000);
    return () => clearInterval(timer);
  }, []);

  const navItems = [
    { label: 'Dashboard', href: '/', icon: <LayoutDashboard size={18} /> },
    { label: 'AI Chat', href: '/chat', icon: <Bot size={18} /> },
    { label: 'Equipment', href: '/equipment', icon: <Wrench size={18} /> },
    { label: 'Analytics', href: '/analytics', icon: <TrendingUp size={18} /> },
    { label: 'Scheduler', href: '/scheduler', icon: <Calendar size={18} /> },
    { label: 'Inventory', href: '/inventory', icon: <Package size={18} /> },
    { label: 'Alerts', href: '/alerts', icon: <Bell size={18} />, badge: alertCount },
    { label: 'Reports', href: '/reports', icon: <FileText size={18} /> },
    { label: 'Knowledge Center', href: '/knowledge', icon: <Database size={18} /> },
    { label: 'Credits', href: '/credits', icon: <Award size={18} /> },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header sidebar-header-aurora">
        <div className="sidebar-logo" style={{ boxShadow: '0 0 16px rgba(59, 130, 246, 0.3)', background: '#ffffff', padding: '3px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <img src="/tata-logo.png" alt="Tata Logo" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
        </div>
        <div className="sidebar-title">
          <h1>Maintenance Wizard</h1>
          <span>Tata Steel AI Platform</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Main</div>
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`nav-item ${pathname === item.href ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
            {item.badge ? <span className="nav-badge">{item.badge}</span> : null}
          </Link>
        ))}

        <div className="sidebar-section-label">Quick Actions</div>
        <Link href="/chat" className="nav-item">
          <span className="nav-icon"><Activity size={16} style={{ color: 'var(--accent-blue-light)' }} /></span>
          <span>Diagnose Issue</span>
        </Link>
        <Link href="/chat" className="nav-item">
          <span className="nav-icon"><AlertTriangle size={16} style={{ color: 'var(--accent-orange)' }} /></span>
          <span>Predict Failures</span>
        </Link>
        <Link href="/reports" className="nav-item">
          <span className="nav-icon"><FileSpreadsheet size={16} style={{ color: 'var(--accent-teal)' }} /></span>
          <span>Generate Report</span>
        </Link>
      </nav>

      {/* Developer Credits Section */}
      <div className="sidebar-credits">
        <Link href="/credits" style={{ textDecoration: 'none', display: 'block' }}>
          <div className="credits-header">
            <div className="credits-avatar">
              <Cpu size={13} style={{ color: 'var(--accent-cyan)' }} />
            </div>
            <div className="credits-info">
              <span className="developer-name" title="Shubham Chakrawarti">Shubham C.</span>
              <span className="developer-role">Lead Platform Architect</span>
            </div>
          </div>
        </Link>
        <div className="credits-socials">
          <a href="https://github.com/shubha9696" target="_blank" rel="noopener noreferrer" title="GitHub Profile">
            <svg viewBox="0 0 24 24" width="13.5" height="13.5" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
            </svg>
          </a>
          <a href="https://www.linkedin.com/in/shubham-chakrawarti-27764836a/" target="_blank" rel="noopener noreferrer" title="LinkedIn Profile">
            <svg viewBox="0 0 24 24" width="13.5" height="13.5" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
              <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
              <rect x="2" y="9" width="4" height="12"></rect>
              <circle cx="4" cy="4" r="2"></circle>
            </svg>
          </a>
          <a href="https://shubham-potfolio.vercel.app/" target="_blank" rel="noopener noreferrer" title="Portfolio Website">
            <svg viewBox="0 0 24 24" width="13.5" height="13.5" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="2" y1="12" x2="22" y2="12"></line>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
            </svg>
          </a>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="sidebar-status" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span className="status-dot"></span>
            <span>AI Engine Active</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%' }}>
            <span className="live-clock">{clock}</span>
            <span className="system-uptime">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              {uptime}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
