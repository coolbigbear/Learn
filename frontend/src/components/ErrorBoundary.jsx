import { Component } from 'react';
import { Link } from 'react-router-dom';

/**
 * ErrorBoundary — catches uncaught rendering errors anywhere in the child tree
 * and displays a fallback UI with a navigation bar instead of a blank page.
 *
 * Also exposes a static `caughtError` flag so tests and the App shell can detect
 * that an error was handled without inspecting DOM text.
 */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
    ErrorBoundary.caughtError = false;
  }

  static getDerivedStateFromError(error) {
    ErrorBoundary.caughtError = true;
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // Log to console for debugging (never silently swallows)
    console.error('[ErrorBoundary] Caught rendering error:', error, info);
  }

  handleReset = () => {
    ErrorBoundary.caughtError = false;
    this.setState({ hasError: false, error: null });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Render a minimal but complete UI — fixed navbar + error message
      // This ensures the user always sees navigation controls even after a crash.
      return (
        <div className="min-h-screen flex flex-col bg-gray-50">
          {/* Minimal navbar matching the main Navbar styling */}
          <nav className="bg-indigo-700 text-white shadow-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-16">
                <Link
                  to="/"
                  onClick={this.handleReset}
                  className="text-xl font-bold tracking-tight"
                >
                  Python Tutorials
                </Link>
                <div className="flex items-center space-x-4">
                  <Link
                    to="/lessons"
                    onClick={this.handleReset}
                    className="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-600 transition-colors"
                  >
                    Lessons
                  </Link>
                  <Link
                    to="/login"
                    onClick={this.handleReset}
                    className="px-3 py-2 rounded-md text-sm font-medium bg-indigo-600 hover:bg-indigo-500 transition-colors"
                  >
                    Login
                  </Link>
                </div>
              </div>
            </div>
          </nav>

          {/* Error message */}
          <main className="flex-1 flex items-center justify-center p-8">
            <div className="max-w-lg w-full bg-white rounded-xl shadow-md border border-red-200 p-8 text-center">
              <div className="text-red-500 text-5xl mb-4">!</div>
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                Something went wrong
              </h2>
              <p className="text-gray-500 mb-6">
                The application encountered an unexpected error. This may happen
                after a page reload or navigation.
              </p>
              {this.state.error && (
                <details className="mb-6 text-left">
                  <summary className="text-sm text-gray-400 cursor-pointer hover:text-gray-600">
                    Error details
                  </summary>
                  <pre className="mt-2 p-3 bg-gray-100 rounded text-xs text-red-700 overflow-auto max-h-32">
                    {this.state.error.message}
                  </pre>
                </details>
              )}
              <button
                onClick={this.handleReload}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
              >
                Reload page
              </button>
            </div>
          </main>
        </div>
      );
    }

    return this.props.children;
  }
}
