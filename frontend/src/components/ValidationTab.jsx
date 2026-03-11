function ValidationTab({ validation }) {
    if (!validation || validation.length === 0) {
        return <div className="card"><p>No validation data available.</p></div>;
    }

    const captured = validation.filter((v) => v.captured).length;
    const total = validation.length;

    return (
        <div className="card">
            <div className="card-header">
                <h2>PR Coverage Validation</h2>
                <div style={{ display: "flex", gap: "8px" }}>
                    <span className="badge badge-success">{captured} captured</span>
                    {total - captured > 0 && (
                        <span className="badge badge-danger">{total - captured} missing</span>
                    )}
                </div>
            </div>
            <div className="table-scroll">
                <table className="data-table">
                    <thead>
                        <tr>
                            <th style={{ width: "60px" }}>ID</th>
                            <th style={{ width: "180px" }}>Feature</th>
                            <th style={{ width: "100px" }}>PR Element</th>
                            <th style={{ width: "80px" }}>Status</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        {validation.map((v, i) => (
                            <tr key={i}>
                                <td><strong>{v.feature_id}</strong></td>
                                <td>{v.feature_name}</td>
                                <td>{v.pr_element || "N/A"}</td>
                                <td>
                                    {v.captured ? (
                                        <span className="badge badge-success">Yes</span>
                                    ) : (
                                        <span className="badge badge-danger">No</span>
                                    )}
                                </td>
                                <td>{v.details}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default ValidationTab;
