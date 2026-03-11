const API_BASE = "http://localhost:8000";

export async function uploadDocuments(idfFile, prFile) {
    const formData = new FormData();
    formData.append("idf_file", idfFile);
    formData.append("pr_file", prFile);

    const response = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Upload failed");
    }
    return response.json();
}

export async function runAnalysis() {
    const response = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Analysis failed");
    }
    return response.json();
}

export async function getResults() {
    const response = await fetch(`${API_BASE}/api/results`);
    if (!response.ok) return null;
    return response.json();
}

export async function sendChatMessage(message) {
    const response = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Chat failed");
    }
    return response.json();
}

export function getReportUrl() {
    return `${API_BASE}/api/report/pdf`;
}

export function getImageUrl(docType, filename) {
    return `${API_BASE}/api/images/${docType}/${filename}`;
}

export async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        return response.json();
    } catch {
        return { status: "offline", has_analysis: false };
    }
}
