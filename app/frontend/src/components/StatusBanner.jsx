import React from 'react';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';

export default function StatusBanner({ systemStatus }) {
  return (
    <div style={{
      background: 'rgba(36, 30, 26, 0.7)',
      borderBottom: '1px solid rgba(194, 155, 56, 0.15)',
      padding: '8px 28px',
      fontSize: '0.82rem',
      color: 'var(--text-secondary)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '12px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Info size={15} color="var(--accent-gold)" />
        <span>
          <strong>Research Environment:</strong> PyTorch with CUDA acceleration enabled on <strong>NVIDIA RTX 4050</strong> (6 GB VRAM).
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#4ade80' }}></span>
          <span>CUDA: Active</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <AlertTriangle size={14} color="#f59e0b" />
          <span style={{ color: '#f59e0b' }}>OCR Model: Not Connected (Stage 1 Mock Adapter)</span>
        </div>
      </div>
    </div>
  );
}
