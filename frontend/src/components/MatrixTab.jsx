import { useState } from "react";
import "./MatrixTab.css";

function MatrixTab({ features, mapping, priorArtLabels }) {
    const [expandedCell, setExpandedCell] = useState(null);

    if (!features || !mapping || Object.keys(mapping).length === 0) {
        return <div className="card"><p>No mapping data available.</p></div>;
    }

    const priorArtIds = Object.keys(priorArtLabels || {});
    if (priorArtIds.length === 0) {
        const allKeys = new Set();
        Object.values(mapping).forEach((m) => Object.keys(m).forEach((k) => allKeys.add(k)));
        priorArtIds.push(...[...allKeys].sort());
    }

    const getCellClass = (value) => {
        if (!value || value === "N/A") return "cell-na";
        if (value === "NO") return "cell-novel";
        if (value.toLowerCase().startsWith("yes, partially")) return "cell-partial";
        return "cell-match";
    };

    const handleExportCSV = () => {
        let csv = "Key Feature," + priorArtIds.map((id) => `"${id}"`).join(",") + "\n";
        features.forEach((f) => {
            const fid = f.id || "";
            const featureMapping = mapping[fid] || {};
            const row = [
                `"${fid}: ${f.name}"`,
                ...priorArtIds.map((pa) => `"${(featureMapping[pa] || "N/A").replace(/"/g, '""')}"`),
            ];
            csv += row.join(",") + "\n";
        });

        const blob = new Blob([csv], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "prior_art_mapping.csv";
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="card">
            <div className="card-header">
                <h2>Prior Art Mapping Matrix</h2>
                <button className="btn btn-secondary" onClick={handleExportCSV}>
                    Export CSV
                </button>
            </div>

            <div className="matrix-legend">
                <span className="legend-item"><span className="legend-dot novel"></span> NO (Novel)</span>
                <span className="legend-item"><span className="legend-dot partial"></span> Yes, Partially</span>
                <span className="legend-item"><span className="legend-dot match"></span> Exact Match</span>
            </div>

            <div className="table-scroll">
                <table className="data-table matrix-table">
                    <thead>
                        <tr>
                            <th className="sticky-col">Key Feature</th>
                            {priorArtIds.map((pa) => (
                                <th key={pa}>
                                    {pa}
                                    {priorArtLabels[pa] && (
                                        <div className="pa-label">{priorArtLabels[pa]}</div>
                                    )}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {features.map((f, i) => {
                            const fid = f.id || `KF${i + 1}`;
                            const featureMapping = mapping[fid] || {};
                            return (
                                <tr key={i}>
                                    <td className="sticky-col feature-cell">
                                        <strong>{fid}</strong>
                                        <div className="feature-name">{f.name}</div>
                                    </td>
                                    {priorArtIds.map((pa) => {
                                        const value = featureMapping[pa] || "N/A";
                                        const cellKey = `${fid}-${pa}`;
                                        const isExpanded = expandedCell === cellKey;
                                        const isLong = value.length > 50;

                                        return (
                                            <td
                                                key={pa}
                                                className={`matrix-cell ${getCellClass(value)}`}
                                                onClick={() => isLong && setExpandedCell(isExpanded ? null : cellKey)}
                                                style={{ cursor: isLong ? "pointer" : "default" }}
                                            >
                                                {isExpanded ? value : (isLong ? value.substring(0, 50) + "..." : value)}
                                            </td>
                                        );
                                    })}
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default MatrixTab;
