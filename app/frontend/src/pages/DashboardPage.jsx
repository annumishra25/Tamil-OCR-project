import React from 'react';
import { Scroll, UploadCloud, Cpu, Database, ArrowRight, ShieldCheck, CheckCircle2, Clock, AlertCircle } from 'lucide-react';

export default function DashboardPage({ setActiveTab, manuscript, datasets, experiments }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Hero Welcome Banner */}
      <div className="glass-panel" style={{
        padding: '36px',
        position: 'relative',
        overflow: 'hidden',
        border: '1px solid var(--border-bright)',
        background: 'linear-gradient(135deg, rgba(36, 30, 26, 0.95), rgba(22, 19, 16, 0.95))'
      }}>
        <div style={{
          position: 'absolute',
          top: '-20px',
          right: '-20px',
          opacity: 0.05,
          pointerEvents: 'none',
          fontFamily: 'var(--font-tamil)',
          fontSize: '14rem',
          lineHeight: 1,
          color: 'var(--accent-gold)'
        }}>
          திருக்குறள்
        </div>

        <div style={{ maxWidth: '820px', position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <span className="badge badge-demo">RESEARCH PROTOTYPE</span>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Tamil HTR / Palm-Leaf Digitization Lab</span>
          </div>

          <h2 className="font-display" style={{
            fontSize: '2.2rem',
            color: 'var(--text-primary)',
            fontWeight: 700,
            marginBottom: '14px',
            lineHeight: 1.2
          }}>
            Distortion-Aware Tamil Palm-Leaf Manuscript Digitization
          </h2>

          <p style={{ fontSize: '1.05rem', color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: 1.7 }}>
            A specialized pipeline adapting open-source Indic/Tamil OCR models to severe historical palm-leaf degradation through illumination normalization, adaptive Sauvola binarization, confidence-guided second-pass inference, and conservative Tamil orthographic post-correction.
          </p>

          <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
            <button className="btn btn-primary" onClick={() => setActiveTab('upload')}>
              <UploadCloud size={18} />
              Upload Manuscript
            </button>
            <button className="btn btn-secondary" onClick={() => setActiveTab('analysis')}>
              <Scroll size={18} />
              Explore Sample (Tirukkural GT-133)
            </button>
            <button className="btn btn-secondary" onClick={() => setActiveTab('datasets')}>
              <Database size={18} />
              View Dataset Manifest
            </button>
          </div>
        </div>
      </div>

      {/* System Status Cards */}
      <div className="grid-cols-4">
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              GPU Accelerator
            </span>
            <Cpu size={18} color="var(--accent-gold)" />
          </div>
          <div style={{ fontSize: '1.3rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
            RTX 4050 (6 GB)
          </div>
          <div style={{ fontSize: '0.8rem', color: '#4ade80', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <CheckCircle2 size={13} /> CUDA 12.4 Verified
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              OCR / HTR Model
            </span>
            <Sparkles size={18} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '1.3rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Not Configured
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Evaluation scheduled in Stage 3
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Datasets
            </span>
            <Database size={18} color="var(--accent-gold)" />
          </div>
          <div style={{ fontSize: '1.3rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
            158 Raw Images
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            THPLMD + CICT GT-133
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Pipeline Status
            </span>
            <Clock size={18} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '1.3rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Stage 1 Foundation
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Frontend UI & Environment Ready
          </div>
        </div>
      </div>

      {/* Two Column Layout: Recent Manuscripts & Target Architecture */}
      <div className="grid-cols-2">
        {/* Recent / Available Manuscripts */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
            <h3 className="font-display" style={{ fontSize: '1.15rem', color: 'var(--text-primary)' }}>
              Available Manuscript Folios
            </h3>
            <span className="badge badge-neutral">Ground Truth Aligned</span>
          </div>

          <div style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '16px',
            cursor: 'pointer',
            transition: 'var(--transition)'
          }}
          onClick={() => setActiveTab('analysis')}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
              <div>
                <h4 style={{ color: 'var(--accent-gold)', fontSize: '1.05rem', fontWeight: 600 }}>
                  {manuscript.title}
                </h4>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  {manuscript.author} · Leaf {manuscript.folioNumber} · {manuscript.linesCount} Inscribed Lines
                </div>
              </div>
              <span className="badge badge-success">PAGE XML</span>
            </div>

            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
              Includes 10 couplets (K1321–K1330) with exact polygon coordinates, baseline geometry, and verified Tamil transcriptions.
            </p>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>Institution: {manuscript.sourceInstitution}</span>
              <span style={{ color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                Open in Workspace <ArrowRight size={14} />
              </span>
            </div>
          </div>
        </div>

        {/* 10-Stage Roadmap Summary */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
            <h3 className="font-display" style={{ fontSize: '1.15rem', color: 'var(--text-primary)' }}>
              Staged Development Roadmap
            </h3>
            <span className="badge badge-demo">10 Stages</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.86rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(46, 125, 90, 0.1)', border: '1px solid rgba(46, 125, 90, 0.3)', borderRadius: '4px' }}>
              <span style={{ color: '#4ade80' }}>Stage 1: GPU Setup & Frontend Shell</span>
              <span className="badge badge-success">Active / Complete</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: '4px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Stage 2 & 2.5: Dataset Ingestion & GT Linking</span>
              <span className="badge badge-neutral">Next Step</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: '4px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Stage 3: Pretrained OCR Selection & Baseline</span>
              <span className="badge badge-neutral">Planned</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: '4px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Stage 4–7: Preprocessing, Slicing & Synthetic Data</span>
              <span className="badge badge-neutral">Planned</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: '4px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Stage 8–10: Fine-Tuning, 2nd Pass & Benchmarking</span>
              <span className="badge badge-neutral">Planned</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Sparkles(props) {
  return <Cpu {...props} />;
}
