import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <nav className="bg-indigo-700 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="text-xl font-bold tracking-tight">
              Python Tutorials
            </Link>
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
          <div className="flex items-center space-x-4">
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
        </div>
      </div>
    </nav>
  );
}