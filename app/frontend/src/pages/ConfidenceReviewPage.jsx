import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, ArrowRight, ShieldCheck, RefreshCw, Layers } from 'lucide-react';

export default function ConfidenceReviewPage({ manuscript, setActiveTab }) {
  const lowConfidenceLines = manuscript.lines.filter(l => l.status === 'LOW_CONFIDENCE');
  const [selectedDecisions, setSelectedDecisions] = useState({});

  const handleSelectDecision = (lineId, choice) => {
    setSelectedDecisions(prev => ({ ...prev, [lineId]: choice }));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span className="badge badge-demo">PAGE 7: CONFIDENCE-BASED SECOND-PASS REVIEW</span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Reliability Routing & Alternative Preprocessing</span>
        </div>
        <h2 className="font-display" style={{ fontSize: '1.8rem', color: 'var(--text-primary)', marginBottom: '8px' }}>
          Low-Confidence Line Arbitration
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Lines falling below confidence threshold &tau; are routed through alternative preprocessing pipelines (e.g., Faint Stroke Filter / Bilateral Denoising) for a second OCR pass.
        </p>
      </div>

      {/* Decision Workflow Diagram */}
      <div className="glass-panel" style={{ padding: '20px', background: 'var(--bg-elevated)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around', flexWrap: 'wrap', gap: '12px', fontSize: '0.84rem' }}>
          <div style={{ textAlign: 'center' }}>
            <span className="badge badge-neutral">1. Sliced Line</span>
            <div style={{ color: 'var(--text-muted)', marginTop: '4px' }}>Original Crop</div>
          </div>
          <ArrowRight size={16} color="var(--border-bright)" />
          <div style={{ textAlign: 'center' }}>
            <span className="badge badge-danger">2. Pass 1 (OCR)</span>
            <div style={{ color: '#f87171', marginTop: '4px' }}>Low Confidence (&lt; 0.70)</div>
          </div>
          <ArrowRight size={16} color="var(--border-bright)" />
          <div style={{ textAlign: 'center' }}>
            <span className="badge badge-demo">3. Alt Preprocessing</span>
            <div style={{ color: '#f59e0b', marginTop: '4px' }}>CLAHE + Faint Stroke</div>
          </div>
          <ArrowRight size={16} color="var(--border-bright)" />
          <div style={{ textAlign: 'center' }}>
            <span className="badge badge-success">4. Pass 2 (OCR)</span>
            <div style={{ color: '#4ade80', marginTop: '4px' }}>Re-inference</div>
          </div>
          <ArrowRight size={16} color="var(--border-bright)" />
          <div style={{ textAlign: 'center' }}>
            <span className="badge badge-primary">5. Final Selection</span>
            <div style={{ color: 'var(--accent-gold)', marginTop: '4px' }}>Conservative Choice</div>
          </div>
        </div>
      </div>

      {/* Review Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {lowConfidenceLines.map((line) => {
          const currentChoice = selectedDecisions[line.id] || 'pass2';
          return (
            <div
              key={line.id}
              className="glass-panel"
              style={{
                padding: '24px',
                border: '1px solid var(--border-bright)',
                display: 'flex',
                flexDirection: 'column',
                gap: '16px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontWeight: 700, color: 'var(--accent-gold)', fontSize: '1.05rem' }}>
                    {line.id} · Kural {line.kural}
                  </span>
                  <span className="badge badge-danger">Low Confidence Trigger</span>
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Reliability: {(line.confidence * 100).toFixed(0)}% (DEMO)
                </div>
              </div>

              {/* Side-by-Side Comparison */}
              <div className="grid-cols-2">
                {/* Pass 1: Standard Sauvola */}
                <div
                  onClick={() => handleSelectDecision(line.id, 'pass1')}
                  style={{
                    background: currentChoice === 'pass1' ? 'rgba(212, 175, 55, 0.1)' : 'var(--bg-elevated)',
                    border: currentChoice === 'pass1' ? '2px solid var(--accent-gold)' : '1px solid var(--border-subtle)',
                    borderRadius: '6px',
                    padding: '16px',
                    cursor: 'pointer',
                    transition: 'var(--transition)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                      PASS 1 (Standard Sauvola Binarization)
                    </span>
                    <span className="badge badge-neutral">Conf: {(line.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-tamil)',
                    fontSize: '1.1rem',
                    color: 'var(--text-primary)',
                    lineHeight: 1.8,
                    marginBottom: '10px'
                  }}>
                    {line.rawOcr}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    Faint strokes in center characters partially disconnected during global thresholding.
                  </div>
                </div>

                {/* Pass 2: Alternative Preprocessing */}
                <div
                  onClick={() => handleSelectDecision(line.id, 'pass2')}
                  style={{
                    background: currentChoice === 'pass2' ? 'rgba(46, 125, 90, 0.12)' : 'var(--bg-elevated)',
                    border: currentChoice === 'pass2' ? '2px solid #4ade80' : '1px solid var(--border-subtle)',
                    borderRadius: '6px',
                    padding: '16px',
                    cursor: 'pointer',
                    transition: 'var(--transition)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#4ade80' }}>
                      PASS 2 (Bilateral Denoise + CLAHE Stroke Enhancement)
                    </span>
                    <span className="badge badge-success">Conf: {Math.min(95, Math.round(line.confidence * 100 + 24))}%</span>
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-tamil)',
                    fontSize: '1.1rem',
                    color: '#ffffff',
                    lineHeight: 1.8,
                    marginBottom: '10px'
                  }}>
                    {line.secondPassOcr}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    Stroke reconstruction restored disconnected loops (Recommended Selection).
                  </div>
                </div>
              </div>

              {/* Status footer */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '8px', borderTop: '1px solid var(--border-subtle)' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  Selected arbitration: <strong style={{ color: 'var(--accent-gold)' }}>{currentChoice === 'pass2' ? 'Pass 2 (Alternative Preprocessing)' : 'Pass 1 (Original)'}</strong>
                </span>
                <span className="badge badge-demo">Stage 9 Feature</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
