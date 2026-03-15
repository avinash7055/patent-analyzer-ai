import { FileText, Download, FileCheck } from "lucide-react";
import { getReportUrl } from "../api";

function ReportTab() {
  const handleDownload = () => {
    window.open(getReportUrl(), "_blank");
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>
          <FileText size={18} style={{ verticalAlign: "middle", marginRight: 8, color: "var(--accent)" }} />
          Analysis Report
        </h2>
        <button className="btn btn-primary" onClick={handleDownload} id="download-pdf-header">
          <Download size={14} />
          Download PDF
        </button>
      </div>
      <div className="report-preview">
        <div className="report-icon-wrapper">
          <FileCheck size={48} />
        </div>
        <h3 className="report-title">Patent Analysis Report</h3>
        <p className="report-description">
          A comprehensive PDF report has been generated containing the invention overview,
          key features, PR validation, prior art mapping matrix with color-coded cells,
          and gap analysis.
        </p>
        <div className="report-features-list">
          <div className="report-feature">
            <span className="rf-dot" />
            Invention Overview & Key Features
          </div>
          <div className="report-feature">
            <span className="rf-dot" />
            PR Coverage Validation Table
          </div>
          <div className="report-feature">
            <span className="rf-dot" />
            Prior Art Mapping Matrix
          </div>
          <div className="report-feature">
            <span className="rf-dot" />
            Gap Analysis & Recommendations
          </div>
        </div>
        <button className="btn btn-primary report-download-btn" onClick={handleDownload} id="download-pdf-main">
          <Download size={16} />
          Download PDF Report
        </button>
      </div>
    </div>
  );
}

export default ReportTab;
