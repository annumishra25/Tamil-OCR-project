import React, { useState } from 'react';
import { Sparkles, CheckCircle, AlertTriangle, RefreshCw, Edit3, ArrowRight, ShieldAlert } from 'lucide-react';

export default function OcrResultsPage({ manuscript, setActiveTab, setSelectedLine }) {
  const [filterConfidence, setFilterConfidence] = useState('ALL');

  const filteredLines = manuscript.lines.filter(l => {
    if (filterConfidence === 'HIGH') return l.status === 'HIGH_CONFIDENCE';
    if (filterConfidence === 'LOW') return l.status === 'LOW_CONFIDENCE';
    return true;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span className="badge badge-demo">PAGE 5: OCR RESULTS INSPECTOR</span>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Line-Level Recognition & Reliability</span>
          </div>
          <h2 className="font-display" style={{ fontSize: '1.8rem', color: 'var(--text-primary)', marginBottom: '8px' }}>
            Tamil OCR Line Predictions
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Line-by-line model predictions showing character transcription, confidence probabilities, and second-pass triggers.
          </p>
        </div>

        {/* Filter Tabs */}
        <div style={{ display: 'flex', gap: '8px', background: 'var(--bg-elevated)', padding: '4px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
          <button
            onClick={() => setFilterConfidence('ALL')}
            className={`btn btn-sm ${filterConfidence === 'ALL' ? 'btn-primary' : 'btn-secondary'}`}
          >
            All Lines ({manuscript.lines.length})
          </button>
          <button
            onClick={() => setFilterConfidence('HIGH')}
            className={`btn btn-sm ${filterConfidence === 'HIGH' ? 'btn-primary' : 'btn-secondary'}`}
          >
            High Confidence
          </button>
          <button
            onClick={() => setFilterConfidence('LOW')}
            className={`btn btn-sm ${filterConfidence === 'LOW' ? 'btn-terracotta' : 'btn-secondary'}`}
          >
            Low Confidence / 2nd Pass
          </button>
        </div>
      </div>

      {/* Disclaimers & Model Indicators */}
      <div style={{
        background: 'rgba(230, 161, 34, 0.08)',
        border: '1px solid rgba(230, 161, 34, 0.25)',
        borderRadius: 'var(--radius-sm)',
        padding: '12px 18px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        fontSize: '0.82rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldAlert size={16} color="#f59e0b" />
          <span><strong>OCR STATUS:</strong> DEMO / MOCK ADAPTER · <strong>MODEL:</strong> Zero-shot baseline candidate (Stage 3)</span>
        </div>
        <div style={{ color: 'var(--text-muted)' }}>
          Confidence metrics are simulated demonstrations until PyTorch inference model is wired.
        </div>
      </div>

      {/* Line Predictions List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {filteredLines.map((line, idx) => (
          <div
            key={line.id}
            className="glass-panel"
            style={{
              padding: '20px 24px',
              borderLeft: line.status === 'HIGH_CONFIDENCE' ? '4px solid #4ade80' : '4px solid #f87171',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontWeight: 700, color: 'var(--accent-gold)', fontSize: '0.95rem' }}>
                  {line.id}
                </span>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  Kural {line.kural} · Numeral: {line.numeral}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--border-bright)' }}>
                  [BBox: {line.bbox.x},{line.bbox.y},{line.bbox.w},{line.bbox.h}]
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {line.status === 'HIGH_CONFIDENCE' ? (
                  <span className="badge badge-success">
                    <CheckCircle size={12} /> Confidence: {(line.confidence * 100).toFixed(0)}% (DEMO)
                  </span>
                ) : (
                  <span className="badge badge-danger">
                    <AlertTriangle size={12} /> Low Confidence: {(line.confidence * 100).toFixed(0)}% (DEMO)
                  </span>
                )}
                {line.secondPassApplied && (
                  <span className="badge badge-demo">2nd Pass Active</span>
                )}
              </div>
            </div>

            {/* Tamil Text Box */}
            <div style={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              padding: '14px 18px',
              fontFamily: 'var(--font-tamil)',
              fontSize: '1.18rem',
              color: 'var(--text-primary)',
              lineHeight: 1.8
            }}>
              {line.rawOcr}
            </div>

            {/* Secondary details */}
            {line.secondPassApplied && (
              <div style={{
                background: 'rgba(168, 66, 43, 0.08)',
                border: '1px solid rgba(168, 66, 43, 0.25)',
                padding: '10px 14px',
                borderRadius: '4px',
                fontSize: '0.85rem'
              }}>
                <span style={{ color: '#f87171', fontWeight: 600 }}>Second-Pass OCR Reprocessing: </span>
                <span style={{ fontFamily: 'var(--font-tamil)', color: 'var(--text-secondary)' }}>{line.secondPassOcr}</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Action Footer */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
        <button className="btn btn-secondary" onClick={() => setActiveTab('confidence-review')}>
          Open Confidence Review Workflow
        </button>
        <button className="btn btn-primary" onClick={() => setActiveTab('editor')}>
          <Edit3 size={16} /> Open Tamil Text Editor <ArrowRight size={16} />
        </button>
      </div>
    </div>
  );
}
