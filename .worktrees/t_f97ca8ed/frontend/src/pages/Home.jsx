import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center py-16">
        <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
          Learn Python
          <span className="text-indigo-600"> Interactively</span>
        </h1>
        <p className="mt-4 text-xl text-gray-500 max-w-2xl mx-auto">
          Master Python programming through hands-on exercises, real-time code execution,
          and step-by-step tutorials — all from your browser.
        </p>
        <div className="mt-10 flex items-center justify-center space-x-4">
          <Link
            to="/lessons"
            className="px-8 py-3 rounded-lg text-lg font-medium text-white bg-indigo-600 hover:bg-indigo-700 shadow-lg hover:shadow-xl transition-all"
          >
            {isAuthenticated ? 'Continue Learning' : 'Start Learning'}
          </Link>
          {!isAuthenticated && (
            <Link
              to="/login"
              className="px-8 py-3 rounded-lg text-lg font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 transition-colors"
            >
              Sign In
            </Link>
          )}
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-8 py-16">
        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Write Real Code</h3>
          <p className="mt-2 text-gray-500">
            Type Python code directly in your browser with syntax highlighting and instant execution.
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Instant Feedback</h3>
          <p className="mt-2 text-gray-500">
            Get immediate results — see if your code passes tests and what output it produces.
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Track Progress</h3>
          <p className="mt-2 text-gray-500">
            Monitor your learning journey across 15 lessons and dozens of exercises.
          </p>
        </div>
      </div>
    </div>
  );
}