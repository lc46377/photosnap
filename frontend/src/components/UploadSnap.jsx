import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function UploadSnap() {
    const API_BASE = process.env.REACT_APP_API_URL;
    const [file, setFile] = useState(null);
    const [friends, setFriends] = useState([]);
    const [recipients, setRecipients] = useState([]);

    useEffect(() => {
        axios
            .get(`${API_BASE}/friends/list`)
            .then(response => setFriends(response.data))
            .catch(() => setFriends([]));
    }, []);

    const handleUpload = async () => {
        const { data } = await axios.post(`${API_BASE}/upload`, {
            filename: file.name,
            file_type: file.type,
            recipients,
        });

        await fetch(data.put_url, {
            method: 'PUT',
            body: file,
        });

        alert(`Uploaded! Snap ID: ${data.id}`);
    };

    return (
        <div className="space-y-4 bg-white p-6 rounded shadow">
            <h2 className="text-xl font-medium">Upload a Snap</h2>

            <label className="block">
                Select Recipients:
                <select
                    multiple
                    className="w-full border p-2 rounded mt-1"
                    value={recipients}
                    onChange={e =>
                        setRecipients(Array.from(e.target.selectedOptions, o => o.value))
                    }
                >
                    {friends.map(f => (
                        <option key={f.id} value={f.id}>
                            {f.username}
                        </option>
                    ))}
                </select>
            </label>

            <label className="block">
                Choose File:
                <input
                    type="file"
                    className="block w-full mt-2"
                    onChange={e => setFile(e.target.files[0])}
                />
            </label>

            <button
                onClick={handleUpload}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
                Upload Snap
            </button>
        </div>
    );
}
