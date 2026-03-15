import { useState, useCallback, useRef } from "react";
import {
  Cpu, ShieldCheck, Grid3X3, FileText,
  UploadCloud, Layers, Sparkles, FileCheck2, X, Check,
  Zap, ChevronRight, Loader2, AlertCircle,
} from "lucide-react";
import FeaturesTab from "./components/FeaturesTab";
import ValidationTab from "./components/ValidationTab";
import MatrixTab from "./components/MatrixTab";
import ReportTab from "./components/ReportTab";
// import ChatTab from "./components/ChatTab"; // temporarily disabled
import { uploadDocuments, runAnalysis } from "./api";
import "./App.css";

function formatBytes(bytes) {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function CenterDropZone({ label, sublabel, file, onFile, onClear, id }) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped && dropped.name.endsWith(".docx")) onFile(dropped);
  };

  return (
    <div className="center-upload-card">
      <div className="center-upload-card-header">
        <span className="center-upload-label">{label}</span>
        {file && (
          <button className="upload-clear-btn" onClick={onClear} title="Remove file">
            <X size={12} />
          </button>
        )}
      </div>

      <div
        className={`center-drop-zone ${file ? "has-file" : ""} ${dragOver ? "drag-over" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !file && inputRef.current?.click()}
        id={id}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && !file && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".docx"
          onChange={(e) => onFile(e.target.files[0])}
          hidden
        />

        {file ? (
          <div className="center-file-success">
            <div className="center-file-icon">
              <FileCheck2 size={28} />
            </div>
            <div className="center-file-meta">
              <span className="center-file-name">{file.name}</span>
              <span className="center-file-size">
                <span className="file-type-badge">DOCX</span>
                {formatBytes(file.size)}
              </span>
            </div>
            <div className="center-file-tick"><Check size={16} /></div>
          </div>
        ) : (
          <div className="center-drop-idle">
            <div className="center-drop-ring">
              <UploadCloud size={30} className="center-drop-icon" />
            </div>
            <div className="center-drop-texts">
              <span className="center-drop-main">Drop {sublabel} file here</span>
              <span className="center-drop-sub">
                or <span className="center-drop-browse">click to browse</span>
              </span>
            </div>
            <span className="center-drop-hint">.docx only</span>
          </div>
        )}
      </div>
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState("features");
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [progressMsg, setProgressMsg] = useState("");

  // Lifted file state
  const [idfFile, setIdfFile] = useState(null);
  const [prFile, setPrFile] = useState(null);

  const tabs = [
    { id: "features", label: "Key Features", icon: Cpu },
    { id: "validation", label: "PR Validation", icon: ShieldCheck },
    { id: "matrix", label: "Prior Art Matrix", icon: Grid3X3 },
    { id: "report", label: "PDF Report", icon: FileText },
    // { id: "chat", label: "AI Chat", icon: MessageSquare }, // temporarily disabled
  ];

  const bothReady = idfFile && prFile;

  const handleAnalyze = async () => {
    if (!idfFile || !prFile) {
      setError("Please upload both IDF and PR documents.");
      return;
    }

    setIsAnalyzing(true);
    setError("");

    try {
      setProgressMsg("Uploading documents...");
      const uploadRes = await uploadDocuments(idfFile, prFile);

      if (uploadRes.cached) {
        // Same files — backend has cached results, just fetch them
        setProgressMsg("Same files detected — loading cached results...");
      } else {
        setProgressMsg("Running AI analysis... this will take a moment");
      }

      const result = await runAnalysis();

      setAnalysisData(result);
      setActiveTab("features");
      setIsAnalyzing(false);
      setProgressMsg("");
    } catch (err) {
      setError(err.message || "An error occurred during analysis.");
      setIsAnalyzing(false);
      setProgressMsg("");
    }
  };

  return (
    <div className="app-container">
      <main className="main-content">
        {/* ── Compact topbar: brand left, tabs right ── */}
        <header className="topbar">
          <div className="topbar-brand">
            <div className="brand-icon-main">
              <Sparkles size={16} />
            </div>
            <h1 className="topbar-title">Patent Analyzer</h1>
            <span className="topbar-tag">AI</span>
          </div>

          {analysisData && (
            <nav className="topbar-tabs" id="main-tab-nav">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    id={`tab-${tab.id}`}
                    className={`tab-btn ${activeTab === tab.id ? "active" : ""}`}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    <Icon size={14} />
                    {tab.label}
                  </button>
                );
              })}
            </nav>
          )}
        </header>

        {error && <div className="error-banner">{error}</div>}

        <div className="tab-content">
          {/* ── EMPTY STATE: center upload UI ── */}
          {!analysisData && !isAnalyzing && (
            <div className="center-upload-shell">
              <div className="center-upload-hero">
                <div className="center-upload-hero-icon">
                  <UploadCloud size={32} />
                </div>
                <h2>Upload Documents to Begin</h2>
                <p>Drop your IDF &amp; PR files below, then hit <strong>Analyze</strong> to launch the AI pipeline.</p>
              </div>

              <div className="center-upload-grid">
                <CenterDropZone
                  label="IDF Document"
                  sublabel="IDF"
                  file={idfFile}
                  onFile={setIdfFile}
                  onClear={() => setIdfFile(null)}
                  id="center-idf-drop"
                />
                <CenterDropZone
                  label="PR Document"
                  sublabel="PR"
                  file={prFile}
                  onFile={setPrFile}
                  onClear={() => setPrFile(null)}
                  id="center-pr-drop"
                />
              </div>

              <div className="center-upload-footer">
                {!bothReady ? (
                  <p className="center-upload-nudge">
                    <AlertCircle size={14} />
                    {!idfFile && !prFile
                      ? "Upload both documents to get started"
                      : !idfFile
                        ? "Still need the IDF document"
                        : "Still need the PR document"}
                  </p>
                ) : (
                  <button
                    className="center-analyze-btn"
                    onClick={handleAnalyze}
                    id="analyze-btn"
                  >
                    <Zap size={18} />
                    Analyze Documents
                    <ChevronRight size={16} className="btn-arrow" />
                  </button>
                )}
              </div>

              <div className="empty-feature-chips">
                <div className="empty-chip"><Layers size={13} /><span>Feature Extraction</span></div>
                <div className="empty-chip"><ShieldCheck size={13} /><span>PR Validation</span></div>
                <div className="empty-chip"><Grid3X3 size={13} /><span>Prior Art Mapping</span></div>
                <div className="empty-chip"><Sparkles size={13} /><span>AI Chat (Coming Soon)</span></div>
              </div>
            </div>
          )}

          {/* ── ANALYZING STATE ── */}
          {isAnalyzing && (
            <div className="analyzing-state">
              <div className="spinner" />
              <h2>{progressMsg || "Analyzing Documents..."}</h2>
              <p>Extracting features, validating PR coverage, and mapping prior art references. This may take 30–60 seconds.</p>
            </div>
          )}

          {analysisData && activeTab === "features" && (
            <FeaturesTab features={analysisData.features} />
          )}
          {analysisData && activeTab === "validation" && (
            <ValidationTab validation={analysisData.validation} />
          )}
          {analysisData && activeTab === "matrix" && (
            <MatrixTab
              features={analysisData.features}
              mapping={analysisData.mapping}
              priorArtLabels={analysisData.prior_art_labels}
            />
          )}
          {analysisData && activeTab === "report" && <ReportTab />}
          {/* Chat tab temporarily disabled */}
          {/* {activeTab === "chat" && <ChatTab hasAnalysis={!!analysisData} />} */}
        </div>
      </main>
    </div>
  );
}

export default App;
