import React, { useState } from 'react';
import axios from 'axios';
import Auth from './components/Auth';
import UploadSnap from './components/UploadSnap';
import ViewSnap from './components/ViewSnap';

export default function App() {
  const [authed, setAuthed] = useState(!!localStorage.getItem('photosnap_jwt'));
  const token = localStorage.getItem('photosnap_jwt');

  if (token) {
    axios.defaults.headers.common.Authorization = `Bearer ${token}`;
  }

  const handleLogout = () => {
    localStorage.removeItem('photosnap_jwt');
    delete axios.defaults.headers.common.Authorization;
    setAuthed(false);
  };

  if (!authed) {
    return <Auth onAuth={() => setAuthed(true)} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-xl mx-auto p-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">PhotoSnap</h1>
          <button
            onClick={handleLogout}
            className="text-red-600 hover:underline"
          >
            Log Out
          </button>
        </div>
      </header>
      <main className="max-w-xl mx-auto p-6 space-y-8">
        <UploadSnap />
        <hr />
        <ViewSnap />
      </main>
    </div>
  );
}
