import { useState, useCallback } from "react";
import Sidebar from "./components/Sidebar";
import FeaturesTab from "./components/FeaturesTab";
import ValidationTab from "./components/ValidationTab";
import MatrixTab from "./components/MatrixTab";
import ReportTab from "./components/ReportTab";
import ChatTab from "./components/ChatTab";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("features");
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");

  const handleAnalysisComplete = useCallback((data) => {
    setAnalysisData(data);
    setIsAnalyzing(false);
    setActiveTab("features");
    setError("");
  }, []);

  const handleAnalysisStart = useCallback(() => {
    setIsAnalyzing(true);
    setError("");
  }, []);

  const handleError = useCallback((msg) => {
    setError(msg);
    setIsAnalyzing(false);
  }, []);

  const tabs = [
    { id: "features", label: "Key Features" },
    { id: "validation", label: "PR Validation" },
    { id: "matrix", label: "Prior Art Matrix" },
    { id: "report", label: "PDF Report" },
    { id: "chat", label: "Chat" },
  ];

  return (
    <div className="app-container">
      <Sidebar
        onAnalysisComplete={handleAnalysisComplete}
        onAnalysisStart={handleAnalysisStart}
        onError={handleError}
        isAnalyzing={isAnalyzing}
        hasResults={!!analysisData}
      />

      <main className="main-content">
        <header className="main-header">
          <h1>Patent Analysis System</h1>
          <p className="subtitle">IDF vs PR - Key Features Correlation Analysis</p>
        </header>

        {error && <div className="error-banner">{error}</div>}

        <nav className="tab-nav">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab-btn ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => setActiveTab(tab.id)}
              disabled={!analysisData && tab.id !== "chat"}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <div className="tab-content">
          {!analysisData && !isAnalyzing && (
            <div className="empty-state">
              <div className="empty-icon">&#9881;</div>
              <h2>Upload Documents to Begin</h2>
              <p>Upload an IDF and PR document using the sidebar to start the analysis.</p>
            </div>
          )}

          {isAnalyzing && (
            <div className="analyzing-state">
              <div className="spinner"></div>
              <h2>Analyzing Documents...</h2>
              <p>Extracting features, validating PR, and mapping prior art. This may take 30-60 seconds.</p>
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
          {activeTab === "chat" && <ChatTab hasAnalysis={!!analysisData} />}
        </div>
      </main>
    </div>
  );
}

export default App;
