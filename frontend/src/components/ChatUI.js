import React, { useState } from "react";
import "./ChatUI.css";

// Replace with your Render backend URL
const BACKEND_URL = "https://ai-agent-8-y2rc.onrender.com";

export default function ChatUI() {
  const [q, setQ] = useState("");
  const [lastQuestion, setLastQuestion] = useState("");
  const [resp, setResp] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedCols, setUploadedCols] = useState([]);
  const [uploadMessage, setUploadMessage] = useState("");

  // Ask SQL question
  async function ask() {
    if (!q) return;
    setLoading(true);
    try {
      const r = await fetch(`${BACKEND_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await r.json();
      setResp(data);
      setLastQuestion(q);
    } catch (err) {
      setResp({ sql: null, answer: "Error: " + err.message, result: null });
      setLastQuestion(q);
    } finally {
      setQ("");
      setLoading(false);
    }
  }

  // Handle file upload
  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setUploadMessage("");
    setUploadedCols([]);

    const fd = new FormData();
    fd.append("file", file);

    try {
      const r = await fetch(`${BACKEND_URL}/upload`, {
        method: "POST",
        body: fd,
      });

      if (!r.ok) {
        const text = await r.text();
        throw new Error(text || "Upload failed");
      }

      const data = await r.json();
      if (data.error) {
        setUploadMessage("❌ " + data.error);
      } else {
        setUploadMessage("✅ " + data.message);
        setUploadedCols(data.columns || []);
      }
    } catch (err) {
      setUploadMessage("❌ Upload failed: " + err.message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="chat-container">
      <h2 className="chat-header">Business SQL Assistant</h2>

      {/* File Upload */}
      <div className="upload-card">
        <label className="upload-label">Upload CSV / Excel / PDF:</label>
        <input type="file" onChange={handleUpload} />
        {uploading && <div>Uploading...</div>}
        {uploadMessage && <div className="upload-status">{uploadMessage}</div>}
        {uploadedCols.length > 0 && (
          <div className="columns-list">
            <strong>Columns:</strong>
            <ul>{uploadedCols.map((c, i) => <li key={i}>{c}</li>)}</ul>
          </div>
        )}
      </div>

      {/* Question Input */}
      <div className="input-card">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Type your question..."
        />
        <button onClick={ask} disabled={loading}>
          {loading ? "..." : "Ask"}
        </button>
      </div>

      {/* Response */}
      {resp && (
        <div className="response-card">
          <div><strong>Question:</strong> {lastQuestion}</div>
          {resp.sql && <div><strong>SQL:</strong><pre>{resp.sql}</pre></div>}
          <div><strong>Answer:</strong><p>{resp.answer}</p></div>

          {/* Raw Table */}
          {resp.result?.rows?.length > 0 && (
            <div className="table-container">
              <strong>Raw Data:</strong>
              <table>
                <thead>
                  <tr>{resp.result.columns.map((c, i) => <th key={i}>{c}</th>)}</tr>
                </thead>
                <tbody>
                  {resp.result.rows.map((row, ri) => (
                    <tr key={ri}>
                      {row.map((cell, ci) => <td key={ci}>{cell ?? "NULL"}</td>)}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Aggregated Table */}
          {resp.aggregated_result?.length > 0 && (
            <div className="table-container">
              <strong>Aggregated Data:</strong>
              <table>
                <thead>
                  <tr>
                    {Object.keys(resp.aggregated_result[0]).map((c, i) => <th key={i}>{c}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {resp.aggregated_result.map((row, ri) => (
                    <tr key={ri}>
                      {Object.values(row).map((cell, ci) => <td key={ci}>{cell ?? "NULL"}</td>)}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Plot */}
          {resp.plot && (
            <div className="plot-container">
              <strong>Plot:</strong>
              <img src={resp.plot} alt="plot" style={{ maxWidth: "100%", marginTop: 10 }} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
