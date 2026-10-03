import React, { useState } from 'react';
import { Edit3, Copy, Download, RotateCcw, Check, Save, Info, FileCode } from 'lucide-react';
import { api } from '../services/api';

export default function EditorPage({ manuscript }) {
  const [lines, setLines] = useState(manuscript.lines);
  const [copied, setCopied] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);

  const handleTextChange = (id, newText) => {
    setLines(lines.map(l => l.id === id ? { ...l, correctedText: newText } : l));
  };

  const handleResetLine = (id) => {
    const original = manuscript.lines.find(l => l.id === id);
    if (original) {
      setLines(lines.map(l => l.id === id ? { ...l, correctedText: original.correctedText } : l));
    }
  };

  const handleCopyAll = () => {
    const fullText = lines.map(l => `[${l.id}] ${l.correctedText}`).join('\n');
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSaveAll = async () => {
    setSaveStatus('Saving...');
    for (const l of lines) {
      await api.saveCorrection(manuscript.id, l.id, l.correctedText);
    }
    setSaveStatus('Saved successfully as annotation data!');
    setTimeout(() => setSaveStatus(null), 3000);
  };

  const handleExportJson = () => {
    const exportData = {
      manuscriptId: manuscript.id,
      title: manuscript.title,
      exportedAt: new Date().toISOString(),
      lines: lines.map(l => ({
        id: l.id,
        kural: l.kural,
        numeral: l.numeral,
        rawOcr: l.rawOcr,
        correctedText: l.correctedText,
        bbox: l.bbox
      }))
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${manuscript.id}_transcription.json`;
    a.click();
  };

  const handleExportTxt = () => {
    const textContent = lines.map(l => l.correctedText).join('\n');
    const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${manuscript.id}_tamil_text.txt`;
    a.click();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span className="badge badge-demo">PAGE 6: TAMIL POST-CORRECTION EDITOR</span>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Orthographic Normalization & Verification</span>
          </div>
          <h2 className="font-display" style={{ fontSize: '1.8rem', color: 'var(--text-primary)', marginBottom: '8px' }}>
            Tamil Manuscript Text Editor
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Review raw OCR transcriptions against orthographically corrected Tamil text. All verified corrections can be saved as fine-tuning ground truth.
          </p>
        </div>

        {/* Global Actions */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={handleCopyAll}>
            {copied ? <Check size={16} color="#4ade80" /> : <Copy size={16} />}
            {copied ? 'Copied Full Text' : 'Copy All Text'}
          </button>
          <button className="btn btn-secondary" onClick={handleExportTxt}>
            <Download size={16} /> Export .TXT
          </button>
          <button className="btn btn-secondary" onClick={handleExportJson}>
            <FileCode size={16} /> Export .JSON
          </button>
          <button className="btn btn-primary" onClick={handleSaveAll}>
            <Save size={16} /> Save Corrections
          </button>
        </div>
      </div>

      {saveStatus && (
        <div style={{
          background: 'rgba(46, 125, 90, 0.15)',
          border: '1px solid rgba(46, 125, 90, 0.4)',
          borderRadius: 'var(--radius-sm)',
          padding: '10px 16px',
          color: '#4ade80',
          fontSize: '0.88rem',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Check size={16} /> {saveStatus}
        </div>
      )}

      {/* Editor Lines Table */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {lines.map((line) => (
          <div
            key={line.id}
            className="glass-panel"
            style={{
              padding: '20px 24px',
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '20px'
            }}
          >
            {/* Left Column: Raw OCR Text (Immutable Reference) */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                  RAW OCR PREDICTION ({line.id} · Kural {line.kural})
                </span>
                <span className="badge badge-neutral">Raw Output</span>
              </div>
              <div style={{
                background: 'rgba(18, 16, 14, 0.8)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '6px',
                padding: '12px 16px',
                fontFamily: 'var(--font-tamil)',
                fontSize: '1.08rem',
                color: 'var(--text-muted)',
                lineHeight: 1.8,
                minHeight: '80px',
                userSelect: 'text'
              }}>
                {line.rawOcr}
              </div>
            </div>

            {/* Right Column: Corrected Tamil Text (Editable) */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--accent-gold)', fontWeight: 600 }}>
                  CORRECTED TAMIL (EDITABLE GROUND TRUTH)
                </span>
                <button
                  onClick={() => handleResetLine(line.id)}
                  style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem' }}
                  title="Reset to default transcription"
                >
                  <RotateCcw size={12} /> Reset
                </button>
              </div>
              <textarea
                value={line.correctedText}
                onChange={(e) => handleTextChange(line.id, e.target.value)}
                style={{
                  width: '100%',
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-bright)',
                  borderRadius: '6px',
                  padding: '12px 16px',
                  fontFamily: 'var(--font-tamil)',
                  fontSize: '1.15rem',
                  color: 'var(--text-primary)',
                  lineHeight: 1.8,
                  minHeight: '80px',
                  resize: 'vertical',
                  outline: 'none',
                  boxShadow: 'inset 0 1px 4px rgba(0,0,0,0.5)'
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
