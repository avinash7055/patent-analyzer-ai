function FeaturesTab({ features }) {
    if (!features || features.length === 0) {
        return <div className="card"><p>No features extracted yet.</p></div>;
    }

    return (
        <div className="card">
            <div className="card-header">
                <h2>Key Features Extracted from IDF</h2>
                <span className="badge badge-success">{features.length} features</span>
            </div>
            <div className="table-scroll">
                <table className="data-table">
                    <thead>
                        <tr>
                            <th style={{ width: "60px" }}>ID</th>
                            <th style={{ width: "180px" }}>Feature</th>
                            <th>Description</th>
                            <th style={{ width: "100px" }}>IDF Section</th>
                        </tr>
                    </thead>
                    <tbody>
                        {features.map((f, i) => (
                            <tr key={i}>
                                <td><strong>{f.id || `KF${i + 1}`}</strong></td>
                                <td>{f.name}</td>
                                <td>{f.description}</td>
                                <td>{f.idf_section}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default FeaturesTab;
