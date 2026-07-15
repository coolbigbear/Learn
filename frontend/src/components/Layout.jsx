import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar.jsx';
import { getVersion } from '../api/client.js';

export default function Layout() {
  const [version, setVersion] = useState(null);

  useEffect(() => {
    getVersion()
      .then((data) => setVersion(data.version))
      .catch(() => {
        // Version endpoint is not critical — fail silently
      });
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-500">
          <span>Interactive Python Tutorials &copy; {new Date().getFullYear()}</span>
          {version && (
            <span className="ml-2 text-gray-400">v{version}</span>
          )}
        </div>
      </footer>
    </div>
  );
}