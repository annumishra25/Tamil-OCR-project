import React, { useState, useRef } from 'react';
import { UploadCloud, FileImage, CheckCircle, AlertCircle, ArrowRight, Trash2, RefreshCw } from 'lucide-react';

export default function UploadPage({ setActiveTab, onManuscriptLoaded }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [fileDetails, setFileDetails] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file) => {
    const validExtensions = ['image/jpeg', 'image/png', 'image/tiff', 'image/jpg'];
    if (!validExtensions.includes(file.type) && !file.name.match(/\.(jpe?g|png|tiff?)$/i)) {
      alert('Please upload a valid image file (JPG, JPEG, PNG, TIFF)');
      return;
    }

    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      setSelectedFile(file);
      setPreviewUrl(url);
      setFileDetails({
        name: file.name,
        size: (file.size / (1024 * 1024)).toFixed(2) + ' MB',
        width: img.naturalWidth,
        height: img.naturalHeight,
        aspectRatio: (img.naturalWidth / img.naturalHeight).toFixed(2)
      });
    };
    img.src = url;
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setFileDetails(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const loadDemoManuscript = () => {
    setActiveTab('analysis');
  };

  return (
    <div style={{ maxWidth: '980px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span className="badge badge-demo">PAGE 2: UPLOAD MANUSCRIPT</span>
        </div>
        <h2 className="font-display" style={{ fontSize: '1.8rem', color: 'var(--text-primary)', marginBottom: '8px' }}>
          Upload Historical Palm-Leaf Folio
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Upload high-resolution manuscript scans for automated preprocessing, text band extraction, and Tamil OCR recognition.
        </p>
      </div>

      {/* Upload Box / Drag & Drop Area */}
      {!selectedFile ? (
        <div
          className="glass-panel"
          style={{
            border: `2px dashed ${dragActive ? 'var(--accent-gold)' : 'var(--border-subtle)'}`,
            padding: '60px 40px',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'var(--transition)',
            background: dragActive ? 'rgba(212, 175, 55, 0.05)' : 'var(--bg-card)'
          }}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current && fileInputRef.current.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/tiff"
            style={{ display: 'none' }}
            onChange={handleFileInput}
          />
          
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 20px auto'
          }}>
            <UploadCloud size={32} color="var(--accent-gold)" />
          </div>

          <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', marginBottom: '8px' }}>
            Drag and drop your manuscript image here
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '24px' }}>
            Supported formats: <strong>JPG, JPEG, PNG, TIFF</strong> (High-resolution recommended)
          </p>

          <button className="btn btn-secondary" type="button" onClick={(e) => {
            e.stopPropagation();
            fileInputRef.current && fileInputRef.current.click();
          }}>
            <FileImage size={16} /> Browse Local File
          </button>
        </div>
      ) : (
        /* Preview Card */
        <div className="glass-panel" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <CheckCircle size={20} color="#4ade80" />
              <h3 style={{ fontSize: '1.15rem', color: 'var(--text-primary)' }}>
                Manuscript Image Loaded
              </h3>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={handleReset}>
              <Trash2 size={14} /> Remove / Replace
            </button>
          </div>

          {/* Image Preview */}
          <div style={{
            background: '#0a0908',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-subtle)',
            padding: '12px',
            marginBottom: '20px',
            textAlign: 'center',
            maxHeight: '300px',
            overflow: 'hidden',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <img
              src={previewUrl}
              alt="Manuscript preview"
              style={{ maxWidth: '100%', maxHeight: '280px', objectFit: 'contain' }}
            />
          </div>

          {/* Metadata Grid */}
          <div className="grid-cols-4" style={{ marginBottom: '24px' }}>
            <div style={{ background: 'var(--bg-elevated)', padding: '12px', borderRadius: '4px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>FILENAME</div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {fileDetails.name}
              </div>
            </div>
            <div style={{ background: 'var(--bg-elevated)', padding: '12px', borderRadius: '4px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>FILE SIZE</div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontWeight: 500 }}>
                {fileDetails.size}
              </div>
            </div>
            <div style={{ background: 'var(--bg-elevated)', padding: '12px', borderRadius: '4px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>DIMENSIONS</div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontWeight: 500 }}>
                {fileDetails.width} × {fileDetails.height} px
              </div>
            </div>
            <div style={{ background: 'var(--bg-elevated)', padding: '12px', borderRadius: '4px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>ASPECT RATIO</div>
              <div style={{ fontSize: '0.9rem', color: 'var(--accent-gold)', fontWeight: 500 }}>
                {fileDetails.aspectRatio} : 1
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
            <button className="btn btn-primary" onClick={() => setActiveTab('analysis')}>
              Begin Analysis <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Quick Demo Loader */}
      <div className="glass-panel" style={{ padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h4 style={{ color: 'var(--accent-gold)', fontSize: '0.98rem', marginBottom: '4px' }}>
            Want to test immediately with verified ground-truth data?
          </h4>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            Load the CICT Tirukkural Chapter 133 benchmark folio with pre-aligned 10-line PAGE XML annotations.
          </p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={loadDemoManuscript}>
          <RefreshCw size={14} /> Load CICT-GT-133
        </button>
      </div>
    </div>
  );
}
