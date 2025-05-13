import { useState } from 'react';
import axios from 'axios';
import { API_BASE } from '../config';

export default function ViewSnap() {
    const [snapId, setSnapId] = useState('');
    const [imageUrl, setImageUrl] = useState('');
    const [error, setError] = useState('');

    const handleView = async () => {
        setError('');
        try {
            const { data } = await axios.get(`${API_BASE}/view/${snapId}`);
            setImageUrl(data.get_url);
        } catch (err) {
            console.error(err);
            setError('Snap not found or expired');
        }
    };

    return (
        <div className="space-y-4">
            <input
                type="text"
                placeholder="Enter Snap ID"
                value={snapId}
                onChange={e => setSnapId(e.target.value)}
                className="block w-full p-2 border border-gray-300 rounded"
            />
            <button
                onClick={handleView}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
                View Snap
            </button>
            {error && <p className="text-red-600">{error}</p>}
            {imageUrl && (
                <img src={imageUrl} alt="Snap" className="mt-4 rounded shadow" />
            )}
        </div>
    );
}
