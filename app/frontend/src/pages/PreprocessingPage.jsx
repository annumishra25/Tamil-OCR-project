import React, { useState } from 'react';
import { Sliders, Layers, Info, CheckCircle, ArrowRight } from 'lucide-react';
import { PREPROCESSING_VARIANTS } from '../services/api';

export default function PreprocessingPage({ manuscript, setActiveTab }) {
  const [activeVariant, setActiveVariant] = useState('sauvola');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span className="badge badge-demo">PAGE 4: PREPROCESSING STUDIO</span>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Adaptive Manuscript Image Enhancement</span>
          </div>
          <h2 className="font-display" style={{ fontSize: '1.8rem', color: 'var(--text-primary)', marginBottom: '8px' }}>
            Multi-Scale Preprocessing Studio
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', maxWidth: '800px' }}>
            Historical palm leaves suffer from dark fiber staining, uneven illumination, incised fading, and baseline skew. Below is the multi-stage filter studio comparing raw captures against adaptive transforms.
          </p>
        </div>

        <div style={{
          background: 'rgba(230, 161, 34, 0.1)',
          border: '1px solid rgba(230, 161, 34, 0.3)',
          borderRadius: 'var(--radius-sm)',
          padding: '12px 16px',
          maxWidth: '380px',
          fontSize: '0.82rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#f59e0b', fontWeight: 600, marginBottom: '4px' }}>
            <Info size={15} /> Scientific Preprocessing Rule
          </div>
          <p style={{ color: 'var(--text-secondary)' }}>
            Aggressive global thresholding destroys faint stylus incisions. The pipeline uses adaptive local variance (Sauvola) and preserves raw images for second-pass fallback.
          </p>
        </div>
      </div>

      {/* 6-Panel Filter Comparison Matrix */}
      <div className="grid-cols-3">
        {PREPROCESSING_VARIANTS.map((v) => {
          const isSelected = activeVariant === v.id;
          return (
            <div
              key={v.id}
              className="glass-panel"
              onClick={() => setActiveVariant(v.id)}
              style={{
                padding: '20px',
                cursor: 'pointer',
                borderColor: isSelected ? 'var(--accent-gold)' : 'var(--border-subtle)',
                boxShadow: isSelected ? 'var(--shadow-gold)' : 'var(--shadow-sm)',
                transition: 'var(--transition)',
                display: 'flex',
                flexDirection: 'column',
                gap: '14px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="badge badge-neutral">{v.badge}</span>
                {isSelected && <span className="badge badge-success"><CheckCircle size={12} /> Active</span>}
              </div>

              {/* Filter Simulation Preview */}
              <div style={{
                height: '130px',
                borderRadius: '6px',
                background: v.id === 'original'
                  ? 'linear-gradient(180deg, #3a2e1d, #4a3b25, #312617)'
                  : v.id === 'grayscale'
                  ? 'linear-gradient(180deg, #444, #666, #333)'
                  : v.id === 'clahe'
                  ? 'linear-gradient(180deg, #222, #777, #111)'
                  : v.id === 'denoised'
                  ? 'linear-gradient(180deg, #383838, #555555, #2e2e2e)'
                  : v.id === 'sauvola'
                  ? '#000000'
                  : 'linear-gradient(180deg, #111, #444, #111)',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '12px',
                position: 'relative',
                overflow: 'hidden'
              }}>
                <div style={{
                  fontFamily: 'var(--font-tamil)',
                  fontSize: '1rem',
                  color: v.id === 'sauvola' ? '#ffffff' : v.id === 'original' ? '#f0d999' : '#e0e0e0',
                  textAlign: 'center',
                  lineHeight: 1.6,
                  transform: v.id === 'deskewed' ? 'rotate(0deg)' : v.id === 'original' ? 'rotate(-1.8deg)' : 'none'
                }}>
                  இல்லைத் தவற் வாக்காயினு மூடுதல்
                </div>
              </div>

              <div>
                <h4 style={{ color: isSelected ? 'var(--accent-gold)' : 'var(--text-primary)', fontSize: '1.05rem', marginBottom: '6px' }}>
                  {v.name}
                </h4>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.84rem', lineHeight: 1.5 }}>
                  {v.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Bottom Action Footer */}
      <div className="glass-panel" style={{ padding: '20px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>SELECTED PIPELINE:</span>
          <h4 style={{ color: 'var(--accent-gold)', fontSize: '1.05rem' }}>
            {PREPROCESSING_VARIANTS.find(v => v.id === activeVariant)?.name}
          </h4>
        </div>
        <button className="btn btn-primary" onClick={() => setActiveTab('ocr-results')}>
          View OCR Recognition Under Filter <ArrowRight size={16} />
        </button>
      </div>
    </div>
  );
}
