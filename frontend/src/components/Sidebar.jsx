import { useState, useRef } from "react";
import { uploadDocuments, runAnalysis } from "../api";
import "./Sidebar.css";

function Sidebar({ onAnalysisComplete, onAnalysisStart, onError, isAnalyzing, hasResults }) {
    const [idfFile, setIdfFile] = useState(null);
    const [prFile, setPrFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState("");
    const [steps, setSteps] = useState([]);
    const idfRef = useRef(null);
    const prRef = useRef(null);

    const updateStep = (label, status) => {
        setSteps((prev) => {
            const existing = prev.findIndex((s) => s.label === label);
            if (existing >= 0) {
                const updated = [...prev];
                updated[existing] = { label, status };
                return updated;
            }
            return [...prev, { label, status }];
        });
    };

    const handleAnalyze = async () => {
        if (!idfFile || !prFile) {
            onError("Please upload both IDF and PR documents.");
            return;
        }

        onAnalysisStart();
        setSteps([]);

        try {
            updateStep("Uploading documents", "running");
            await uploadDocuments(idfFile, prFile);
            updateStep("Uploading documents", "done");

            updateStep("Running AI analysis", "running");
            const result = await runAnalysis();
            updateStep("Running AI analysis", "done");

            updateStep("Generating report", "done");
            updateStep("Building search index", "done");

            onAnalysisComplete(result);
        } catch (err) {
            const failedStep = steps.find((s) => s.status === "running");
            if (failedStep) updateStep(failedStep.label, "error");
            onError(err.message);
        }
    };

    const handleDrop = (e, setter) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        if (file && file.name.endsWith(".docx")) {
            setter(file);
        }
    };

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <h2 className="sidebar-title">Patent Analyzer</h2>
                <span className="sidebar-version">v1.0</span>
            </div>

            <div className="sidebar-section">
                <label className="section-label">IDF Document</label>
                <div
                    className={`drop-zone ${idfFile ? "has-file" : ""}`}
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={(e) => handleDrop(e, setIdfFile)}
                    onClick={() => idfRef.current?.click()}
                >
                    <input
                        ref={idfRef}
                        type="file"
                        accept=".docx"
                        onChange={(e) => setIdfFile(e.target.files[0])}
                        hidden
                    />
                    {idfFile ? (
                        <div className="file-info">
                            <span className="file-icon">&#128196;</span>
                            <span className="file-name">{idfFile.name}</span>
                        </div>
                    ) : (
                        <div className="drop-text">
                            <span>Drop IDF .docx here or click to browse</span>
                        </div>
                    )}
                </div>
            </div>

            <div className="sidebar-section">
                <label className="section-label">PR Document</label>
                <div
                    className={`drop-zone ${prFile ? "has-file" : ""}`}
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={(e) => handleDrop(e, setPrFile)}
                    onClick={() => prRef.current?.click()}
                >
                    <input
                        ref={prRef}
                        type="file"
                        accept=".docx"
                        onChange={(e) => setPrFile(e.target.files[0])}
                        hidden
                    />
                    {prFile ? (
                        <div className="file-info">
                            <span className="file-icon">&#128196;</span>
                            <span className="file-name">{prFile.name}</span>
                        </div>
                    ) : (
                        <div className="drop-text">
                            <span>Drop PR .docx here or click to browse</span>
                        </div>
                    )}
                </div>
            </div>

            <button
                className="btn btn-primary analyze-btn"
                onClick={handleAnalyze}
                disabled={!idfFile || !prFile || isAnalyzing}
            >
                {isAnalyzing ? "Analyzing..." : "Analyze Documents"}
            </button>

            {steps.length > 0 && (
                <div className="progress-steps">
                    {steps.map((step, i) => (
                        <div key={i} className={`step ${step.status}`}>
                            <span className="step-indicator">
                                {step.status === "done" && <span>&#10003;</span>}
                                {step.status === "running" && <span className="step-spinner"></span>}
                                {step.status === "error" && <span>&#10007;</span>}
                            </span>
                            <span className="step-label">{step.label}</span>
                        </div>
                    ))}
                </div>
            )}

            {hasResults && (
                <div className="sidebar-status">
                    <span className="status-dot"></span>
                    Analysis complete
                </div>
            )}
        </aside>
    );
}

export default Sidebar;
