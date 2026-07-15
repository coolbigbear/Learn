import { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';
import LessonCard from '../components/LessonCard.jsx';
import * as api from '../api/client.js';

const PATH_META = {
  core: {
    label: 'Python Fundamentals',
    description: 'Master Python basics: from printing to modules and packages.',
    color: 'indigo',
    icon: '★',
  },
  'data-processing': {
    label: 'Data Processing',
    description: 'Learn to work with CSV, JSON, and data APIs.',
    color: 'green',
    icon: '📊',
  },
  api: {
    label: 'API Development',
    description: 'Build web APIs with FastAPI.',
    color: 'blue',
    icon: '🔌',
  },
  'machine-learning': {
    label: 'Machine Learning',
    description: 'Coming soon — dive into ML fundamentals.',
    color: 'purple',
    icon: '🤖',
  },
};

const COLOR_CLASSES = {
  indigo: {
    accent: 'bg-indigo-50 border-indigo-200',
    header: 'text-indigo-700',
    badge: 'bg-indigo-100 text-indigo-700',
    line: 'border-indigo-300',
  },
  green: {
    accent: 'bg-green-50 border-green-200',
    header: 'text-green-700',
    badge: 'bg-green-100 text-green-700',
    line: 'border-green-300',
  },
  blue: {
    accent: 'bg-blue-50 border-blue-200',
    header: 'text-blue-700',
    badge: 'bg-blue-100 text-blue-700',
    line: 'border-blue-300',
  },
  purple: {
    accent: 'bg-purple-50 border-purple-200',
    header: 'text-purple-700',
    badge: 'bg-purple-100 text-purple-700',
    line: 'border-purple-300',
  },
};

function BranchDivider() {
  return (
    <div className="relative my-12">
      {/* Vertical line coming down */}
      <div className="flex justify-center">
        <div className="w-0.5 h-8 bg-gray-300" />
      </div>
      {/* Branch icon */}
      <div className="flex justify-center items-center gap-1 my-2">
        <div className="h-px flex-1 bg-gray-300" />
        <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M7 17l-5-5m0 0l5-5m-5 5h18" />
        </svg>
        <div className="h-px flex-1 bg-gray-300" />
      </div>
      {/* Horizontal branch line */}
      <div className="hidden md:flex justify-center relative">
        <div className="flex gap-20 items-center">
          <span className="text-xs text-gray-400 uppercase tracking-wider">Choose your path</span>
        </div>
      </div>
      {/* Three fork lines going down */}
      <div className="flex justify-around max-w-3xl mx-auto mt-2">
        <div className="w-0.5 h-6 bg-green-400" />
        <div className="w-0.5 h-6 bg-blue-400" />
        <div className="w-0.5 h-6 bg-purple-400" />
      </div>
    </div>
  );
}

export default function Lessons() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [groupedLessons, setGroupedLessons] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (authLoading) return;

    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    async function fetchLessons() {
      try {
        const data = await api.getLessonsByPath();
        setGroupedLessons(data);
      } catch (err) {
        // Fallback: if /by-path fails, try the flat list endpoint
        try {
          const data = await api.getLessons();
          // Group client-side by path field if it exists
          if (data.lessons.length > 0 && data.lessons[0].path) {
            const grouped = { core: [], 'data-processing': [], api: [], 'machine-learning': [] };
            for (const lesson of data.lessons) {
              const p = lesson.path || 'core';
              if (!grouped[p]) grouped[p] = [];
              grouped[p].push(lesson);
            }
            setGroupedLessons(grouped);
          } else {
            // Old API without path: fall back to flat list inline
            setGroupedLessons({ core: data.lessons });
          }
        } catch (fallbackErr) {
          setError(fallbackErr.message);
        }
      } finally {
        setLoading(false);
      }
    }
    fetchLessons();
  }, [isAuthenticated, authLoading]);

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500 text-lg">Loading lessons...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
        Failed to load lessons: {error}
      </div>
    );
  }

  // If groupedLessons is flat (no paths detected), render the old flat layout
  if (!groupedLessons || Object.keys(groupedLessons).length === 1 && groupedLessons.core) {
    const lessons = groupedLessons?.core || [];
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Python Tutorials</h1>
          <p className="mt-2 text-gray-500">Continue your learning journey through these interactive lessons.</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {lessons.map((lesson) => (
            <LessonCard key={lesson.id} lesson={lesson} />
          ))}
        </div>
        {lessons.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            No lessons available yet. Check back soon!
          </div>
        )}
      </div>
    );
  }

  // Path order for display
  const pathOrder = ['core', 'data-processing', 'api', 'machine-learning'];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Python Tutorials</h1>
        <p className="mt-2 text-gray-500">Follow the core path, then choose your specialization.</p>
      </div>

      {pathOrder.map((pathKey, idx) => {
        const lessons = groupedLessons[pathKey] || [];
        const meta = PATH_META[pathKey];
        const colors = COLOR_CLASSES[meta.color];
        const isBranch = pathKey !== 'core';
        const isEmpty = lessons.length === 0;

        return (
          <div key={pathKey}>
            {/* Show the branch divider BEFORE each non-core path */}
            {isBranch && <BranchDivider />}

            <div className={`mb-10 rounded-lg border ${colors.accent} p-6`}>
              {/* Path header */}
              <div className="flex items-center gap-3 mb-1">
                <span className="text-2xl">{meta.icon}</span>
                <h2 className={`text-2xl font-bold ${colors.header}`}>{meta.label}</h2>
                {isBranch && (
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${colors.badge}`}>
                    Branch
                  </span>
                )}
              </div>
              <p className="text-gray-600 text-sm mt-1 mb-4">{meta.description}</p>

              {isEmpty ? (
                <div className="text-center py-10">
                  <div className="text-5xl mb-3 opacity-40">{meta.icon}</div>
                  <p className="text-gray-400 font-medium">Coming Soon</p>
                  <p className="text-gray-400 text-sm mt-1">
                    New lessons are being prepared for this path.
                  </p>
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {lessons.map((lesson) => (
                    <LessonCard key={lesson.id} lesson={lesson} />
                  ))}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
