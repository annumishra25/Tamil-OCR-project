import React, { useState } from 'react';
import { ZoomIn, ZoomOut, Maximize2, ChevronLeft, ChevronRight, Sliders, Sparkles, CheckCircle2, AlertTriangle, Eye } from 'lucide-react';
import { PREPROCESSING_VARIANTS } from '../services/api';

export default function AnalysisPage({ manuscript, setActiveTab, setSelectedLine, selectedLine }) {
  const [zoom, setZoom] = useState(100);
  const [selectedVariant, setSelectedVariant] = useState('sauvola');
  const [activeLineIndex, setActiveLineIndex] = useState(0);

  const currentLine = manuscript.lines[activeLineIndex] || manuscript.lines[0];

  const handleNextLine = () => {
    if (activeLineIndex < manuscript.lines.length - 1) {
      setActiveLineIndex(activeLineIndex + 1);
    }
  };

  const handlePrevLine = () => {
    if (activeLineIndex > 0) {
      setActiveLineIndex(activeLineIndex - 1);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Controls Bar */}
      <div className="glass-panel" style={{
        padding: '14px 20px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>ACTIVE FOLIO:</span>
            <strong style={{ color: 'var(--accent-gold)', marginLeft: '6px' }}>{manuscript.title}</strong>
          </div>
          <span className="badge badge-demo">DEMO WORKSPACE</span>
        </div>

        {/* Zoom & Navigation Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', background: 'var(--bg-elevated)', borderRadius: '4px', padding: '2px 6px' }}>
            <button
              onClick={() => setZoom(Math.max(50, zoom - 15))}
              style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '4px' }}
              title="Zoom Out"
            >
              <ZoomOut size={16} />
            </button>
            <span style={{ fontSize: '0.8rem', minWidth: '42px', textAlign: 'center' }}>{zoom}%</span>
            <button
              onClick={() => setZoom(Math.min(200, zoom + 15))}
              style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '4px' }}
              title="Zoom In"
            >
              <ZoomIn size={16} />
            </button>
            <button
              onClick={() => setZoom(100)}
              style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '4px' }}
              title="Reset Zoom"
            >
              <Maximize2 size={14} />
            </button>
          </div>

          {/* Line Stepper */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <button
              className="btn btn-secondary btn-sm"
              onClick={handlePrevLine}
              disabled={activeLineIndex === 0}
              style={{ opacity: activeLineIndex === 0 ? 0.4 : 1 }}
            >
              <ChevronLeft size={16} /> Prev Line
            </button>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', padding: '0 4px' }}>
              Line {activeLineIndex + 1} of {manuscript.lines.length}
            </span>
            <button
              className="btn btn-secondary btn-sm"
              onClick={handleNextLine}
              disabled={activeLineIndex === manuscript.lines.length - 1}
              style={{ opacity: activeLineIndex === manuscript.lines.length - 1 ? 0.4 : 1 }}
            >
              Next Line <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* 3-Column Synchronized Workspace */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1.1fr 1.1fr 0.9fr',
        gap: '20px',
        minHeight: '520px'
      }}>
        {/* Pane 1: Original Manuscript View */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '12px 18px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Eye size={16} color="var(--accent-gold)" />
              <strong style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>1. Original Manuscript</strong>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Raw Photography</span>
          </div>

          <div style={{
            flex: 1,
            background: '#0d0b09',
            padding: '20px',
            overflow: 'auto',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative'
          }}>
            {/* Palm Leaf Manuscript Graphic Representation */}
            <div style={{
              width: `${zoom}%`,
              minHeight: '260px',
              background: 'linear-gradient(180deg, #3a2e1d 0%, #4a3b25 25%, #352a1a 50%, #483924 75%, #312617 100%)',
              border: '2px solid #5a472c',
              borderRadius: '6px',
              boxShadow: 'inset 0 0 30px rgba(0,0,0,0.8), 0 8px 24px rgba(0,0,0,0.9)',
              position: 'relative',
              padding: '16px 20px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-around',
              filter: 'sepia(0.3) contrast(1.1)'
            }}>
              {/* String Binding Hole */}
              <div style={{
                position: 'absolute',
                left: '40px',
                top: '50%',
                transform: 'translateY(-50%)',
                width: '18px',
                height: '18px',
                borderRadius: '50%',
                background: '#120f0a',
                border: '2px solid #2a2014',
                boxShadow: 'inset 0 0 6px rgba(0,0,0,0.9)'
              }}></div>

              {/* Inscribed Lines */}
              {manuscript.lines.map((ln, idx) => (
                <div
                  key={ln.id}
                  onClick={() => setActiveLineIndex(idx)}
                  style={{
                    fontFamily: 'var(--font-tamil)',
                    fontSize: '0.85rem',
                    letterSpacing: '0.08em',
                    color: activeLineIndex === idx ? '#fff3d1' : 'rgba(255, 235, 185, 0.45)',
                    textShadow: '0 1px 2px rgba(0,0,0,0.9)',
                    padding: '2px 8px 2px 60px',
                    borderRadius: '3px',
                    background: activeLineIndex === idx ? 'rgba(212, 175, 55, 0.25)' : 'transparent',
                    border: activeLineIndex === idx ? '1px solid rgba(212, 175, 55, 0.6)' : '1px solid transparent',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    transition: 'var(--transition)'
                  }}
                >
                  <span style={{ color: 'var(--accent-gold)', marginRight: '8px', fontSize: '0.75rem' }}>{ln.numeral}</span>
                  {ln.rawOcr}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Pane 2: Preprocessed / Line Slices */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '12px 18px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sliders size={16} color="var(--accent-gold)" />
              <strong style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>2. Adaptive Slicing</strong>
            </div>
            
            <select
              value={selectedVariant}
              onChange={(e) => setSelectedVariant(e.target.value)}
              style={{
                background: 'var(--bg-elevated)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '4px',
                padding: '3px 8px',
                fontSize: '0.8rem'
              }}
            >
              {PREPROCESSING_VARIANTS.map(v => (
                <option key={v.id} value={v.id}>{v.name}</option>
              ))}
            </select>
          </div>

          <div style={{
            flex: 1,
            background: '#080706',
            padding: '20px',
            overflow: 'auto',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            gap: '16px'
          }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              CURRENT SEGMENTED LINE CROP: <strong>{currentLine.id} (Kural {currentLine.kural})</strong>
            </div>

            {/* Binarized Line Crop Simulation */}
            <div style={{
              background: '#000000',
              border: '2px solid var(--accent-gold)',
              borderRadius: '6px',
              padding: '16px 20px',
              minHeight: '100px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px rgba(212, 175, 55, 0.15)'
            }}>
              <div style={{
                fontFamily: 'var(--font-tamil)',
                fontSize: '1.25rem',
                color: '#ffffff',
                letterSpacing: '0.06em',
                lineHeight: 1.8,
                textAlign: 'center'
              }}>
                {currentLine.rawOcr}
              </div>
            </div>

            <div style={{
              background: 'var(--bg-elevated)',
              padding: '12px',
              borderRadius: '4px',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.82rem',
              display: 'flex',
              justifyContent: 'space-between'
            }}>
              <span>Filter: <strong>{PREPROCESSING_VARIANTS.find(v => v.id === selectedVariant)?.name}</strong></span>
              <span style={{ color: 'var(--accent-gold)' }}>BBox: [X: {currentLine.bbox.x}, Y: {currentLine.bbox.y}, W: {currentLine.bbox.w}, H: {currentLine.bbox.h}]</span>
            </div>
          </div>
        </div>

        {/* Pane 3: OCR Prediction & Confidence */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '12px 18px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={16} color="var(--accent-gold)" />
              <strong style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>3. OCR Recognition</strong>
            </div>
            <span className="badge badge-demo">DEMO INFERENCE</span>
          </div>

          <div style={{ flex: 1, padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px', overflowY: 'auto' }}>
            {/* Confidence Score Pill */}
            <div style={{
              background: 'var(--bg-elevated)',
              padding: '14px',
              borderRadius: '6px',
              border: '1px solid var(--border-subtle)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>RELIABILITY SCORE</span>
                {currentLine.status === 'HIGH_CONFIDENCE' ? (
                  <span className="badge badge-success">
                    <CheckCircle2 size={12} /> High ({Math.round(currentLine.confidence * 100)}%)
                  </span>
                ) : (
                  <span className="badge badge-demo">
                    <AlertTriangle size={12} /> Low ({Math.round(currentLine.confidence * 100)}%)
                  </span>
                )}
              </div>

              {/* Progress bar */}
              <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{
                  width: `${currentLine.confidence * 100}%`,
                  height: '100%',
                  background: currentLine.status === 'HIGH_CONFIDENCE' ? 'linear-gradient(90deg, #d4af37, #4ade80)' : 'linear-gradient(90deg, #a8422b, #f59e0b)'
                }}></div>
              </div>
            </div>

            {/* OCR Raw Text */}
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                RAW OCR PREDICTION (UNFILTERED):
              </div>
              <div style={{
                background: '#0d0b09',
                border: '1px solid var(--border-subtle)',
                borderRadius: '6px',
                padding: '14px',
                fontFamily: 'var(--font-tamil)',
                fontSize: '1.05rem',
                color: 'var(--text-primary)',
                lineHeight: 1.7
              }}>
                {currentLine.rawOcr}
              </div>
            </div>

            {/* Second Pass status */}
            {currentLine.secondPassApplied && (
              <div style={{
                background: 'rgba(168, 66, 43, 0.1)',
                border: '1px solid rgba(168, 66, 43, 0.3)',
                padding: '12px',
                borderRadius: '6px',
                fontSize: '0.82rem'
              }}>
                <div style={{ color: '#f87171', fontWeight: 600, marginBottom: '4px' }}>
                  Second-Pass Triggered (Alternative Preprocessing)
                </div>
                <div style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-tamil)' }}>
                  {currentLine.secondPassOcr}
                </div>
              </div>
            )}

            <div style={{ marginTop: 'auto', display: 'flex', gap: '8px' }}>
              <button className="btn btn-secondary btn-sm" style={{ flex: 1 }} onClick={() => setActiveTab('editor')}>
                Edit in Tamil Editor
              </button>
              <button className="btn btn-primary btn-sm" style={{ flex: 1 }} onClick={() => setActiveTab('preprocessing')}>
                Explore Filters
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
