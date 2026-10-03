import React from 'react';
import { Scroll, Cpu, Layers, Database, Sparkles, Sliders, FileText, CheckCircle2 } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, systemStatus }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Layers },
    { id: 'upload', label: 'Upload', icon: FileText },
    { id: 'analysis', label: 'Analysis Workspace', icon: Scroll },
    { id: 'preprocessing', label: 'Preprocessing Studio', icon: Sliders },
    { id: 'ocr-results', label: 'OCR Results', icon: Sparkles },
    { id: 'editor', label: 'Tamil Editor', icon: FileText },
    { id: 'confidence-review', label: 'Confidence Review', icon: CheckCircle2 },
    { id: 'datasets', label: 'Datasets', icon: Database },
    { id: 'experiments', label: 'Experiments', icon: Cpu },
  ];

  return (
    <header style={{
      background: 'rgba(18, 16, 14, 0.92)',
      borderBottom: '1px solid var(--border-subtle)',
      backdropFilter: 'blur(16px)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{
        maxWidth: '1440px',
        margin: '0 auto',
        padding: '12px 28px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        {/* Brand & Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #d4af37, #8a3420)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(212, 175, 55, 0.3)'
          }}>
            <Scroll color="#12100e" size={24} strokeWidth={2.2} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 className="font-display" style={{
                fontSize: '1.25rem',
                color: 'var(--text-primary)',
                letterSpacing: '0.04em',
                fontWeight: 700
              }}>
                TAMIL PALM-LEAF OCR
              </h1>
              <span className="badge badge-demo">LABORATORY PROTOTYPE</span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Distortion-Aware Historical Manuscript Digitization System
            </p>
          </div>
        </div>

        {/* System Indicator Pill */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          background: 'rgba(29, 25, 22, 0.8)',
          padding: '6px 14px',
          borderRadius: '20px',
          border: '1px solid var(--border-subtle)',
          fontSize: '0.8rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#4ade80',
              boxShadow: '0 0 8px #4ade80'
            }}></span>
            <span style={{ color: 'var(--text-secondary)' }}>GPU:</span>
            <strong style={{ color: 'var(--accent-gold)' }}>RTX 4050 (6GB)</strong>
          </div>
          <span style={{ color: 'var(--border-subtle)' }}>|</span>
          <div style={{ color: 'var(--text-muted)' }}>
            Stage 1 Verified
          </div>
        </div>
      </div>

      {/* Navigation Bar */}
      <nav style={{
        maxWidth: '1440px',
        margin: '0 auto',
        padding: '0 28px',
        display: 'flex',
        gap: '4px',
        overflowX: 'auto'
      }}>
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 16px',
                background: 'transparent',
                border: 'none',
                borderBottom: isActive ? '2px solid var(--accent-gold)' : '2px solid transparent',
                color: isActive ? 'var(--accent-gold)' : 'var(--text-secondary)',
                fontSize: '0.88rem',
                fontFamily: 'var(--font-body)',
                fontWeight: isActive ? 600 : 400,
                cursor: 'pointer',
                transition: 'var(--transition)',
                whiteSpace: 'nowrap'
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.color = 'var(--text-primary)';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.color = 'var(--text-secondary)';
              }}
            >
              <Icon size={16} />
              {item.label}
            </button>
          );
        })}
      </nav>
    </header>
  );
}
