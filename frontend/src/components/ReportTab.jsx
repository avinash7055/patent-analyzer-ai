import { getReportUrl } from "../api";

function ReportTab() {
    const handleDownload = () => {
        window.open(getReportUrl(), "_blank");
    };

    return (
        <div className="card">
            <div className="card-header">
                <h2>Analysis Report</h2>
                <button className="btn btn-primary" onClick={handleDownload}>
                    Download PDF
                </button>
            </div>
            <div style={{ textAlign: "center", padding: "60px 20px" }}>
                <div style={{ fontSize: "64px", marginBottom: "16px", opacity: "0.6" }}>&#128196;</div>
                <h3 style={{ marginBottom: "8px" }}>Patent Analysis Report</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "14px", maxWidth: "500px", margin: "0 auto 24px" }}>
                    A comprehensive PDF report has been generated containing the invention overview,
                    key features, PR validation, prior art mapping matrix with color-coded cells,
                    and gap analysis.
                </p>
                <button className="btn btn-primary" onClick={handleDownload}>
                    Download PDF Report
                </button>
            </div>
        </div>
    );
}

export default ReportTab;
