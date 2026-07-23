import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    setMobileMenuOpen(false);
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <nav className="bg-indigo-700 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="text-xl font-bold tracking-tight" onClick={closeMobileMenu}>
              Python Tutorials
            </Link>
            {/* Desktop navigation links */}
            <div className="hidden md:flex space-x-4">
              <Link
                to="/lessons"
                className="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-600 transition-colors"
              >
                Lessons
              </Link>
              {isAuthenticated && (
                <Link
                  to="/progress"
                  className="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-600 transition-colors"
                >
                  My Progress
                </Link>
              )}
            </div>
          </div>
          {/* Desktop auth section */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <span className="text-sm text-indigo-200">
                  {user?.username}
                </span>
                <button
                  onClick={handleLogout}
                  className="px-3 py-2 rounded-md text-sm font-medium bg-indigo-600 hover:bg-indigo-500 transition-colors"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="px-3 py-2 rounded-md text-sm font-medium bg-indigo-600 hover:bg-indigo-500 transition-colors"
              >
                Login
              </Link>
            )}
          </div>
          {/* Mobile hamburger button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-indigo-200 hover:text-white hover:bg-indigo-600 transition-colors"
              aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? (
                /* X icon */
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                /* Hamburger icon */
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>
      {/* Mobile dropdown menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-indigo-600">
          <div className="px-4 py-3 space-y-2">
            <Link
              to="/lessons"
              onClick={closeMobileMenu}
              className="block px-3 py-2 rounded-md text-base font-medium hover:bg-indigo-600 transition-colors"
            >
              Lessons
            </Link>
            {isAuthenticated && (
              <Link
                to="/progress"
                onClick={closeMobileMenu}
                className="block px-3 py-2 rounded-md text-base font-medium hover:bg-indigo-600 transition-colors"
              >
                My Progress
              </Link>
            )}
            <hr className="border-indigo-600" />
            {isAuthenticated ? (
              <div className="space-y-2">
                <span className="block px-3 py-2 text-sm text-indigo-200">
                  {user?.username}
                </span>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-3 py-2 rounded-md text-base font-medium hover:bg-indigo-600 transition-colors"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                onClick={closeMobileMenu}
                className="block px-3 py-2 rounded-md text-base font-medium hover:bg-indigo-600 transition-colors"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
