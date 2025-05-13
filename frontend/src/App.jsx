import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import UploadSnap from './components/UploadSnap';
import ViewSnap from './components/ViewSnap';

export default function App() {
  return (
    <Router>
      <header className="bg-white shadow p-4">
        <nav className="flex space-x-6 justify-center">
          <Link to="/upload" className="text-xl font-medium text-blue-600 hover:underline">Upload</Link>
          <Link to="/view" className="text-xl font-medium text-blue-600 hover:underline">View</Link>
        </nav>
      </header>
      <main className="max-w-xl mx-auto p-6">
        <Routes>
          <Route path="/upload" element={<UploadSnap />} />
          <Route path="/view" element={<ViewSnap />} />
        </Routes>
      </main>
    </Router>
  );
}
