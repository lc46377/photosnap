// src/components/ViewSnap.jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

export default function ViewSnap() {
    const API_BASE = process.env.REACT_APP_API_URL;
    const [snaps, setSnaps] = useState([]);
    const [selectedId, setSelectedId] = useState('');
    const [imageUrl, setImageUrl] = useState('');
    const [error, setError] = useState('');

    // fetch your incoming snaps on mount
    useEffect(() => {
        axios.get(`${API_BASE}/snaps/list`)
            .then(({ data }) => {
                setSnaps(data);
                if (data.length) setSelectedId(data[0].id);
            })
            .catch(() => setSnaps([]));
    }, []);

    const handleView = async () => {
        setError('');
        try {
            const { data } = await axios.get(`${API_BASE}/view/${selectedId}`);
            setImageUrl(data.get_url);
        } catch (err) {
            setError(err.response?.data?.msg || 'Unable to fetch snap');
        }
    };

    return (
        <div className="space-y-4 bg-white p-6 rounded shadow">
            <h2 className="text-xl font-medium">View a Snap</h2>

            <label className="block">
                Pick a Snap:
                <select
                    className="w-full border p-2 rounded mt-1"
                    value={selectedId}
                    onChange={e => setSelectedId(e.target.value)}
                >
                    {snaps.map(s => (
                        <option key={s.id} value={s.id}>
                            {s.owner} – {s.id}
                        </option>
                    ))}
                </select>
            </label>

            <button
                onClick={handleView}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
                Show Snap
            </button>

            {error && <p className="text-red-600">{error}</p>}
            {imageUrl && <img src={imageUrl} alt="Snap" className="mt-4 rounded shadow" />}
        </div>
    );
}
