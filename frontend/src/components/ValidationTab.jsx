import { ShieldCheck, CheckCircle2, XCircle, Hash, FileText } from "lucide-react";

function ValidationTab({ validation }) {
  if (!validation || validation.length === 0) {
    return (
      <div className="card">
        <div className="empty-tab">
          <ShieldCheck size={32} className="empty-tab-icon" />
          <p>No validation data available.</p>
        </div>
      </div>
    );
  }

  const captured = validation.filter((v) => v.captured).length;
  const total = validation.length;
  const percentage = Math.round((captured / total) * 100);

  return (
    <div className="card">
      <div className="card-header">
        <h2>
          <ShieldCheck size={18} style={{ verticalAlign: "middle", marginRight: 8, color: "var(--accent)" }} />
          PR Coverage Validation
        </h2>
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <span className="badge badge-success">{captured} captured</span>
          {total - captured > 0 && (
            <span className="badge badge-danger">{total - captured} missing</span>
          )}
          <span className="badge badge-accent">{percentage}%</span>
        </div>
      </div>

      {/* Coverage Progress Bar */}
      <div className="coverage-bar-wrapper">
        <div className="coverage-bar">
          <div
            className="coverage-fill"
            style={{ width: `${percentage}%` }}
          />
        </div>
        <span className="coverage-label">{percentage}% coverage</span>
      </div>

      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: "65px" }}>
                <Hash size={11} style={{ verticalAlign: "middle", marginRight: 4 }} />
                ID
              </th>
              <th style={{ width: "200px" }}>Feature</th>
              <th style={{ width: "120px" }}>
                <FileText size={11} style={{ verticalAlign: "middle", marginRight: 4 }} />
                PR Element
              </th>
              <th style={{ width: "90px" }}>Status</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {validation.map((v, i) => (
              <tr key={i}>
                <td>
                  <span className="feature-id">{v.feature_id}</span>
                </td>
                <td className="feature-cell-name">{v.feature_name}</td>
                <td>{v.pr_element || "N/A"}</td>
                <td>
                  {v.captured ? (
                    <span className="status-pill success">
                      <CheckCircle2 size={12} />
                      Yes
                    </span>
                  ) : (
                    <span className="status-pill danger">
                      <XCircle size={12} />
                      No
                    </span>
                  )}
                </td>
                <td className="details-cell">{v.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ValidationTab;
