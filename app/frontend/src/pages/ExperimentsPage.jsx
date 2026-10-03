import React from 'react';
import { Cpu, FlaskConical, AlertCircle, BarChart3, Clock, CheckCircle2, Sparkles, Layers, ShieldCheck } from 'lucide-react';
import { EXPERIMENTS_MATRIX } from '../services/api';

export default function ExperimentsPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span className="badge badge-demo">STAGE 7: SYNTHETIC DATA & EXPERIMENT BENCHMARKS</span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>CER / WER Quantitative Tracking</span>
        </div>
        <h2 className="font-display" style={{ fontSize: '1.8rem', color: 'var(--text-primary)', marginBottom: '8px' }}>
          Synthetic Data Engine & OCR Benchmarks
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Physics-inspired synthetic palm-leaf degradation engine paired with empirical CER/WER benchmark tracking.
        </p>
      </div>

      {/* Synthetic Engine Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
            <Sparkles size={14} color="var(--accent-gold)" /> SYNTHETIC SAMPLES
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--accent-gold)' }}>220 Lines</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>150 Train / 35 Val / 35 Test</div>
          <div style={{ marginTop: '8px', fontSize: '0.72rem', color: '#4ade80' }}>Quality Rejections: 0</div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
            <Layers size={14} color="#60a5fa" /> DEGRADATION PRESETS
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#60a5fa' }}>4 Presets</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>LIGHT, MEDIUM, HEAVY, EXTREME</div>
          <div style={{ marginTop: '8px', fontSize: '0.72rem', color: 'var(--text-muted)' }}>Physics-Based Striae & Fading</div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
            <Cpu size={14} color="#c084fc" /> CLEAN CORPUS
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#c084fc' }}>50 Lines</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Tirukkural, Naladiyar, Athichudi</div>
          <div style={{ marginTop: '8px', fontSize: '0.72rem', color: '#c084fc' }}>Zero-Leakage Group Split</div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
            <ShieldCheck size={14} color="#4ade80" /> GOLD STANDARD TEST
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#4ade80' }}>23 Lines</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>CICT GT-133 Real Manuscripts</div>
          <div style={{ marginTop: '8px', fontSize: '0.72rem', color: '#4ade80' }}>Untouched External Benchmark</div>
        </div>
      </div>

      {/* Degradation Pipeline Flow */}
      <div className="glass-panel" style={{ padding: '18px 22px', background: 'rgba(255,255,255,0.02)' }}>
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '10px' }}>
          Synthetic Degradation Architecture (Clean Tamil Unicode → Historical Palm-Leaf Degradation)
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          <span className="badge" style={{ background: 'rgba(96, 165, 250, 0.15)', color: '#60a5fa' }}>1. Clean Line Rendering</span>
          <span>→</span>
          <span className="badge" style={{ background: 'rgba(230, 161, 34, 0.15)', color: 'var(--accent-gold)' }}>2. Fibrous Ochre Texture</span>
          <span>→</span>
          <span className="badge" style={{ background: 'rgba(230, 161, 34, 0.15)', color: 'var(--accent-gold)' }}>3. Stylus Scratches & Veins</span>
          <span>→</span>
          <span className="badge" style={{ background: 'rgba(230, 161, 34, 0.15)', color: 'var(--accent-gold)' }}>4. Ink Fading & Erosion</span>
          <span>→</span>
          <span className="badge" style={{ background: 'rgba(230, 161, 34, 0.15)', color: 'var(--accent-gold)' }}>5. Illumination Gradients</span>
          <span>→</span>
          <span className="badge" style={{ background: 'rgba(74, 222, 128, 0.15)', color: '#4ade80' }}>6. Quality Audited Crop</span>
        </div>
      </div>

      {/* Experiments Benchmark Table */}
      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <strong style={{ fontSize: '0.92rem', color: 'var(--text-primary)' }}>Empirical Preprocessing & Baseline OCR Benchmark Matrix</strong>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Evaluated on CICT-PLM-GT-133 Gold-Standard Lines</span>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
          <thead>
            <tr style={{ background: 'var(--bg-elevated)', borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
              <th style={{ padding: '14px 18px', fontWeight: 600 }}>Experiment ID</th>
              <th style={{ padding: '14px 18px', fontWeight: 600 }}>Pipeline Description</th>
              <th style={{ padding: '14px 18px', fontWeight: 600 }}>Model Backbone</th>
              <th style={{ padding: '14px 18px', fontWeight: 600 }}>Preprocessing Filter</th>
              <th style={{ padding: '14px 18px', fontWeight: 600 }}>CER (Char Error Rate)</th>
              <th style={{ padding: '14px 18px', fontWeight: 600 }}>WER (Word Error Rate)</th>
              <th style={{ padding: '14px 18px', fontWeight: 600 }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {EXPERIMENTS_MATRIX.map((exp, idx) => (
              <tr
                key={exp.id}
                style={{
                  borderBottom: '1px solid var(--border-subtle)',
                  background: idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)'
                }}
              >
                <td style={{ padding: '16px 18px', fontWeight: 600, color: 'var(--accent-gold)' }}>
                  {exp.id}
                </td>
                <td style={{ padding: '16px 18px', fontWeight: 500, color: 'var(--text-primary)' }}>
                  {exp.pipeline}
                </td>
                <td style={{ padding: '16px 18px', color: 'var(--text-secondary)' }}>
                  {exp.model}
                </td>
                <td style={{ padding: '16px 18px', color: 'var(--text-secondary)' }}>
                  {exp.preprocessing}
                </td>
                <td style={{ padding: '16px 18px', color: 'var(--text-primary)', fontWeight: 600, fontFamily: 'monospace' }}>
                  {exp.cer}
                </td>
                <td style={{ padding: '16px 18px', color: 'var(--text-primary)', fontWeight: 600, fontFamily: 'monospace' }}>
                  {exp.wer}
                </td>
                <td style={{ padding: '16px 18px' }}>
                  <span className="badge badge-neutral" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <Clock size={11} /> {exp.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
