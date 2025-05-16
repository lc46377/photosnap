import React, { useState } from 'react';
import axios from 'axios';

export default function Auth({ onAuth }) {
    const [mode, setMode] = useState('login');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const API_BASE = process.env.REACT_APP_API_URL;

    const handleSubmit = async e => {
        e.preventDefault();
        const path = mode === 'login' ? '/login' : '/signup';
        try {
            const resp = await axios.post(`${API_BASE}${path}`, { username, password });
            if (mode === 'login') {
                localStorage.setItem('photosnap_jwt', resp.data.access_token);
                axios.defaults.headers.common.Authorization = `Bearer ${resp.data.access_token}`;
                onAuth();
            } else {
                alert('User created! Please log in.');
                setMode('login');
            }
        } catch (err) {
            alert(err.response?.data?.msg || 'Error');
        }
    };

    return (
        <form
            onSubmit={handleSubmit}
            className="max-w-sm mx-auto mt-20 p-6 bg-white rounded shadow space-y-4"
        >
            <h2 className="text-2xl text-center">
                {mode === 'login' ? 'Log In' : 'Sign Up'}
            </h2>
            <input
                className="w-full p-2 border rounded"
                placeholder="Username"
                value={username}
                onChange={e => setUsername(e.target.value)}
            />
            <input
                type="password"
                className="w-full p-2 border rounded"
                placeholder="Password"
                value={password}
                onChange={e => setPassword(e.target.value)}
            />
            <button
                type="submit"
                className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
                {mode === 'login' ? 'Log In' : 'Sign Up'}
            </button>
            <p className="text-center text-sm">
                {mode === 'login' ? (
                    <>No account?{' '}
                        <button
                            type="button"
                            className="underline"
                            onClick={() => setMode('signup')}
                        >
                            Sign up
                        </button>
                    </>
                ) : (
                    <>Have an account?{' '}
                        <button
                            type="button"
                            className="underline"
                            onClick={() => setMode('login')}
                        >
                            Log in
                        </button>
                    </>
                )}
            </p>
        </form>
    );
}
