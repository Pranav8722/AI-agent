import React, { useState } from "react";

export default function UploadUI({ onColumnsLoaded }) {
  const [file, setFile] = useState(null);
  const [columns, setColumns] = useState([]);

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://127.0.0.1:8000/upload", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setColumns(data.columns);
    onColumnsLoaded(data.columns);
  };

  return (
    <div className="upload-ui">
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Upload</button>
      {columns.length > 0 && <p>Columns: {columns.join(", ")}</p>}
    </div>
  );
}
