import React, { useState } from 'react';
import Header from './components/Header';
import StatusBanner from './components/StatusBanner';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import AnalysisPage from './pages/AnalysisPage';
import PreprocessingPage from './pages/PreprocessingPage';
import OcrResultsPage from './pages/OcrResultsPage';
import EditorPage from './pages/EditorPage';
import ConfidenceReviewPage from './pages/ConfidenceReviewPage';
import DatasetsPage from './pages/DatasetsPage';
import ExperimentsPage from './pages/ExperimentsPage';
import { SAMPLE_MANUSCRIPTS, DATASETS_MANIFEST, EXPERIMENTS_MATRIX, SYSTEM_STATUS } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [manuscript, setManuscript] = useState(SAMPLE_MANUSCRIPTS[0]);
  const [selectedLine, setSelectedLine] = useState(manuscript.lines[0]);

  return (
    <div className="app-container">
      {/* Top Navigation & Brand Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemStatus={SYSTEM_STATUS}
      />

      {/* Global Status Banner */}
      <StatusBanner systemStatus={SYSTEM_STATUS} />

      {/* Main Page Routing Container */}
      <main className="main-content">
        {activeTab === 'dashboard' && (
          <DashboardPage
            setActiveTab={setActiveTab}
            manuscript={manuscript}
            datasets={DATASETS_MANIFEST}
            experiments={EXPERIMENTS_MATRIX}
          />
        )}

        {activeTab === 'upload' && (
          <UploadPage
            setActiveTab={setActiveTab}
            onManuscriptLoaded={(newMs) => {
              setManuscript(newMs);
              setActiveTab('analysis');
            }}
          />
        )}

        {activeTab === 'analysis' && (
          <AnalysisPage
            manuscript={manuscript}
            setActiveTab={setActiveTab}
            selectedLine={selectedLine}
            setSelectedLine={setSelectedLine}
          />
        )}

        {activeTab === 'preprocessing' && (
          <PreprocessingPage
            manuscript={manuscript}
            setActiveTab={setActiveTab}
          />
        )}

        {activeTab === 'ocr-results' && (
          <OcrResultsPage
            manuscript={manuscript}
            setActiveTab={setActiveTab}
            setSelectedLine={setSelectedLine}
          />
        )}

        {activeTab === 'editor' && (
          <EditorPage
            manuscript={manuscript}
          />
        )}

        {activeTab === 'confidence-review' && (
          <ConfidenceReviewPage
            manuscript={manuscript}
            setActiveTab={setActiveTab}
          />
        )}

        {activeTab === 'datasets' && (
          <DatasetsPage />
        )}

        {activeTab === 'experiments' && (
          <ExperimentsPage />
        )}
      </main>

      {/* Footer */}
      <footer style={{
        marginTop: 'auto',
        borderTop: '1px solid var(--border-subtle)',
        background: 'rgba(18, 16, 14, 0.95)',
        padding: '16px 28px',
        textAlign: 'center',
        fontSize: '0.8rem',
        color: 'var(--text-muted)'
      }}>
        <div style={{ maxWidth: '1440px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            Distortion-Aware Tamil Palm-Leaf Manuscript OCR / HTR System · Research Laboratory
          </div>
          <div>
            Hardware Target: NVIDIA RTX 4050 (6GB) · Python 3.11 · PyTorch CUDA 12.4
          </div>
        </div>
      </footer>
    </div>
  );
}
