import React from 'react';
import { Database, CheckCircle, AlertCircle, FileText, Shield, HardDrive, Layers, Lock, AlertTriangle } from 'lucide-react';
import { DATASETS_MANIFEST } from '../services/api';

export default function DatasetsPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span className="badge badge-demo">STAGE 6: RESEARCH DATASETS & LEAKAGE-SAFE SPLITS</span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Scientific Data Hierarchy & Unified Manifest</span>
        </div>
        <h2 className="font-display" style={{ fontSize: '1.8rem', color: 'var(--text-primary)', marginBottom: '8px' }}>
          Historical Manuscript Corpora & Split Manifest
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Catalog of verified manuscript archives, isolated character sets, unlabeled folios, and zero-leakage partitions.
        </p>
      </div>

      {/* Hierarchy Status Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
            <Shield size={14} color="#4ade80" /> LEVEL 3: GOLD STANDARD
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#4ade80' }}>23 Lines</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>CICT GT-133 (PAGE XML Verified)</div>
          <div style={{ marginTop: '8px', fontSize: '0.72rem', color: 'var(--accent-gold)' }}>Split: external_test.jsonl</div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
            <Layers size={14} color="#60a5fa" /> LEVEL 2: CHARACTER POOL
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#60a5fa' }}>7,100 Chars</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>palmleaf-tamil (71 Classes × 100)</div>
          <div style={{ marginTop: '8px', fontSize: '0.72rem', color: 'var(--text-muted)' }}>Split: character_pool.jsonl</div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
            <HardDrive size={14} color="var(--accent-gold)" /> LEVEL 5: UNLABELED FOLIOS
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--accent-gold)' }}>158 Folios</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>THPLMD (46 Auto Lines Extracted)</div>
          <div style={{ marginTop: '8px', fontSize: '0.72rem', color: 'var(--text-muted)' }}>Split: unlabeled_pool.jsonl</div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
            <Lock size={14} color="#c084fc" /> ZERO-LEAKAGE RULE
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#c084fc' }}>source_group_id</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Folio-level partition isolation</div>
          <div style={{ marginTop: '8px', fontSize: '0.72rem', color: '#4ade80' }}>Audit: 0 Cross-Contaminations</div>
        </div>
      </div>

      {/* Dataset Status Legend Panel */}
      <div className="glass-panel" style={{ padding: '16px 20px', background: 'rgba(255,255,255,0.02)', borderLeft: '4px solid var(--accent-gold)' }}>
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '6px' }}>
          Scientific Label Integrity Policy
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          <div><strong style={{ color: '#4ade80' }}>● GROUND TRUTH:</strong> Verified Unicode transcriptions aligned with authoritative PAGE XML polygons.</div>
          <div><strong style={{ color: '#60a5fa' }}>● CHARACTER POOL:</strong> Isolated character crops for morphology pre-adaptation and synthesis.</div>
          <div><strong style={{ color: 'var(--accent-gold)' }}>● AUTOMATIC / UNLABELED:</strong> Manuscript images/crops without human transcription. Never treated as training labels.</div>
          <div><strong style={{ color: '#c084fc' }}>● SYNTHETIC:</strong> Physics-degraded Tamil lines generated from Unicode literature (Stage 7).</div>
        </div>
      </div>

      {/* Dataset Table */}
      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
          <thead>
            <tr style={{ background: 'var(--bg-elevated)', borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
              <th style={{ padding: '14px 18px', fontWeight: 600 }}>Dataset / Collection</th>
              <th style={{ padding: '14px 18px', fontWeight: 600 }}>Scientific Tier</th>
              <th style={{ padding: '14px 18px', fontWeight: 600 }}>Verified Items</th>
              <th style={{ padding: '14px 18px', fontWeight: 600 }}>Label Status</th>
              <th style={{ padding: '14px 18px', fontWeight: 600 }}>Split Assignment</th>
              <th style={{ padding: '14px 18px', fontWeight: 600 }}>License</th>
            </tr>
          </thead>
          <tbody>
            {DATASETS_MANIFEST.map((ds, idx) => (
              <tr
                key={ds.id}
                style={{
                  borderBottom: '1px solid var(--border-subtle)',
                  background: idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)'
                }}
              >
                <td style={{ padding: '16px 18px' }}>
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{ds.name}</div>
                  <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>{ds.type}</div>
                </td>
                <td style={{ padding: '16px 18px', color: 'var(--text-secondary)', fontSize: '0.82rem' }}>
                  {ds.tier}
                </td>
                <td style={{ padding: '16px 18px', color: ds.imagesCount > 0 ? 'var(--accent-gold)' : 'var(--text-muted)', fontWeight: 600 }}>
                  {ds.imagesCount > 0 ? `${ds.imagesCount.toLocaleString()} items` : '0 (Offline)'}
                </td>
                <td style={{ padding: '16px 18px' }}>
                  {ds.groundTruth.includes('Verified') ? (
                    <span className="badge badge-success">{ds.groundTruth}</span>
                  ) : ds.groundTruth.includes('Classes') ? (
                    <span className="badge" style={{ background: 'rgba(96, 165, 250, 0.2)', color: '#60a5fa' }}>{ds.groundTruth}</span>
                  ) : ds.groundTruth.includes('Unlabeled') ? (
                    <span className="badge badge-neutral">{ds.groundTruth}</span>
                  ) : (
                    <span className="badge badge-demo" style={{ background: 'rgba(248, 113, 113, 0.2)', color: '#f87171' }}>{ds.groundTruth}</span>
                  )}
                </td>
                <td style={{ padding: '16px 18px' }}>
                  <span style={{ fontSize: '0.8rem', color: ds.role.includes('EXTERNAL') ? '#4ade80' : 'var(--text-secondary)', fontFamily: 'monospace' }}>
                    {ds.role}
                  </span>
                </td>
                <td style={{ padding: '16px 18px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  {ds.license}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
