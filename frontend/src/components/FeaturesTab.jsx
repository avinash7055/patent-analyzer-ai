import { Cpu, Hash, BookOpen, Bookmark } from "lucide-react";

function FeaturesTab({ features }) {
  if (!features || features.length === 0) {
    return (
      <div className="card">
        <div className="empty-tab">
          <Cpu size={32} className="empty-tab-icon" />
          <p>No features extracted yet.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>
          <Cpu size={18} style={{ verticalAlign: "middle", marginRight: 8, color: "var(--accent)" }} />
          Key Features Extracted from IDF
        </h2>
        <span className="badge badge-accent">{features.length} features</span>
      </div>
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: "65px" }}>
                <Hash size={11} style={{ verticalAlign: "middle", marginRight: 4 }} />
                ID
              </th>
              <th style={{ width: "200px" }}>
                <Bookmark size={11} style={{ verticalAlign: "middle", marginRight: 4 }} />
                Feature
              </th>
              <th>
                <BookOpen size={11} style={{ verticalAlign: "middle", marginRight: 4 }} />
                Description
              </th>
              <th style={{ width: "110px" }}>IDF Section</th>
            </tr>
          </thead>
          <tbody>
            {features.map((f, i) => (
              <tr key={i} style={{ animationDelay: `${i * 0.03}s` }}>
                <td>
                  <span className="feature-id">{f.id || `KF${i + 1}`}</span>
                </td>
                <td className="feature-cell-name">{f.name}</td>
                <td>{f.description}</td>
                <td>
                  <span className="badge badge-accent">{f.idf_section || f.source_section || "—"}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default FeaturesTab;
