// src/components/UploadSnap.jsx
import axios from "axios";
import { useState } from "react";

export default function UploadSnap() {
    const [file, setFile] = useState(null);

    async function handleUpload() {
        if (!file) return alert("Select a file first");

        const apiBase = process.env.REACT_APP_API_URL;
        const { data } = await axios.post(
            `${apiBase}/upload`,
            { filename: file.name }
        );

        await axios.put(data.put_url, file, {
            headers: { "Content-Type": file.type },
        });

        console.log("view URL:", data.get_url);
    }

    return (
        <div>
            <input
                type="file"
                onChange={(e) => setFile(e.target.files[0])}
            />
            <button onClick={handleUpload}>Upload</button>
        </div>
    );
}
