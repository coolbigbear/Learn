import { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';
import LessonCard from '../components/LessonCard.jsx';
import * as api from '../api/client.js';

function BranchDivider() {
  return (
    <div className="relative my-12">
      <div className="flex justify-center">
        <div className="w-0.5 h-8 bg-gray-300" />
      </div>
      <div className="flex justify-center items-center gap-1 my-2">
        <div className="h-px flex-1 bg-gray-300" />
        <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M7 17l-5-5m0 0l5-5m-5 5h18" />
        </svg>
        <div className="h-px flex-1 bg-gray-300" />
      </div>
      <div className="hidden md:flex justify-center relative">
        <div className="flex gap-20 items-center">
          <span className="text-xs text-gray-400 uppercase tracking-wider">Choose your path</span>
        </div>
      </div>
      <div className="flex justify-around max-w-3xl mx-auto mt-2">
        <div className="w-0.5 h-6 bg-green-400" />
        <div className="w-0.5 h-6 bg-blue-400" />
        <div className="w-0.5 h-6 bg-purple-400" />
      </div>
    </div>
  );
}

const COLOR_MAP = {
  indigo: { bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-700', badge: 'bg-indigo-100 text-indigo-700', header: 'text-indigo-800' },
  green: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700', badge: 'bg-green-100 text-green-700', header: 'text-green-800' },
  blue: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', badge: 'bg-blue-100 text-blue-700', header: 'text-blue-800' },
  purple: { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-700', badge: 'bg-purple-100 text-purple-700', header: 'text-purple-800' },
};

export default function Lessons() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [paths, setPaths] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [progressByLesson, setProgressByLesson] = useState({});

  useEffect(() => {
    if (authLoading) return;

    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetchAll() {
      try {
        // Fetch lessons and progress in parallel
        const [lessonsData, progressData] = await Promise.all([
          api.getLessonsByPath(),
          api.getProgress().catch(() => null), // progress is optional — don't block on it
        ]);

        if (cancelled) return;

        // Build progress lookup: lesson_slug -> { completed, total }
        if (progressData) {
          const lookup = {};
          const lessonTotals = progressData.lesson_totals || {};
          if (progressData.progress) {
            for (const p of progressData.progress) {
              const slug = p.lesson_slug;
              if (!lookup[slug]) {
                lookup[slug] = { completed: 0, total: lessonTotals[slug] || 0 };
              }
              if (p.completed) lookup[slug].completed++;
            }
          }
          setProgressByLesson(lookup);
        }

        // Process lessons-by-path data
        const data = lessonsData;
        if (data && data.paths && Array.isArray(data.paths)) {
          setPaths(data.paths);
        } else {
          // Fallback: flat dict format {core: [...], ...}
          const pathOrder = ['core', 'data-processing', 'api', 'machine-learning'];
          const meta = {
            core: { display_name: 'Python Fundamentals', description: 'Master Python basics.', color: 'indigo' },
            'data-processing': { display_name: 'Data Processing', description: 'Work with CSV, JSON, and APIs.', color: 'green' },
            api: { display_name: 'API Development', description: 'Build web APIs with FastAPI.', color: 'blue' },
            'machine-learning': { display_name: 'Machine Learning', description: 'Coming soon.', color: 'purple' },
          };
          const mapped = pathOrder.filter((k) => k in data).map((k) => ({
            path: k,
            display_name: meta[k].display_name,
            description: meta[k].description,
            color: meta[k].color,
            lessons: data[k] || [],
          }));
          setPaths(mapped.length > 0 ? mapped : null);
        }
      } catch (err) {
        // Fallback: try the flat lessons endpoint
        try {
          const [data] = await Promise.all([
            api.getLessons(),
            // progress already fetched above, but if it failed try again here
          ]);
          if (cancelled) return;
          if (data.lessons && data.lessons.length > 0) {
            if (data.lessons[0].path) {
              // Group by path client-side
              const grouped = {};
              for (const lesson of data.lessons) {
                const p = lesson.path || 'core';
                if (!grouped[p]) grouped[p] = [];
                grouped[p].push(lesson);
              }
              const meta = {
                core: { display_name: 'Python Fundamentals', description: 'Master Python basics.', color: 'indigo' },
                'data-processing': { display_name: 'Data Processing', description: 'Work with CSV, JSON, and APIs.', color: 'green' },
                api: { display_name: 'API Development', description: 'Build web APIs with FastAPI.', color: 'blue' },
                'machine-learning': { display_name: 'Machine Learning', description: 'Coming soon.', color: 'purple' },
              };
              const pathOrder = ['core', 'data-processing', 'api', 'machine-learning'];
              setPaths(pathOrder.map((k) => ({
                path: k,
                display_name: meta[k].display_name,
                description: meta[k].description,
                color: meta[k].color,
                lessons: grouped[k] || [],
              })));
            } else {
              // No path field at all — single flat section
              setPaths([{
                path: 'core',
                display_name: 'Python Tutorials',
                description: 'Continue your learning journey through these interactive lessons.',
                color: 'indigo',
                lessons: data.lessons,
              }]);
            }
          } else {
            setPaths([]);
          }
        } catch (fallbackErr) {
          setError(fallbackErr.message);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchAll();
    return () => { cancelled = true; };
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

  if (!paths || paths.length === 0) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Python Tutorials</h1>
          <p className="mt-2 text-gray-500">Continue your learning journey through these interactive lessons.</p>
        </div>
        <div className="text-center py-12 text-gray-400">
          No lessons available yet. Check back soon!
        </div>
      </div>
    );
  }

  function getProgressForLesson(lesson) {
    const p = progressByLesson[lesson.slug];
    if (p) return p;
    // Fallback to lesson_totals if available
    return null;
  }

  // Single path (flat fallback — no path field in API)
  if (paths.length === 1) {
    const section = paths[0];
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{section.display_name}</h1>
          <p className="mt-2 text-gray-500">{section.description}</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {section.lessons.map((lesson) => (
            <LessonCard
              key={lesson.id}
              lesson={lesson}
              progress={getProgressForLesson(lesson)}
            />
          ))}
        </div>
      </div>
    );
  }

  // Multi-path layout
  // Split core path (full-width) from branch paths (horizontal grid on desktop)
  const corePath = paths.find(p => p.path === 'core');
  const branchPaths = paths.filter(p => p.path !== 'core');

  function renderPathSection(section) {
    const isBranch = section.path !== 'core';
    const isEmpty = section.lessons.length === 0;
    const colors = COLOR_MAP[section.color] || COLOR_MAP.indigo;

    return (
      <div key={section.path} className={`rounded-lg border ${colors.bg} ${colors.border} p-6`}>
        <div className="flex items-center gap-3 mb-1">
          <h2 className={`text-2xl font-bold ${colors.header}`}>{section.display_name}</h2>
          {isBranch && (
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${colors.badge}`}>
              Branch
            </span>
          )}
        </div>
        <p className="text-gray-600 text-sm mt-1 mb-4">{section.description}</p>

        {isEmpty ? (
          <div className="text-center py-10">
            <div className="text-5xl mb-3 opacity-40">
              {section.path === 'machine-learning' ? '🤖' : '📚'}
            </div>
            <p className="text-gray-400 font-medium">Coming Soon</p>
            <p className="text-gray-400 text-sm mt-1">
              {section.path === 'machine-learning'
                ? 'Machine Learning lessons are being prepared.'
                : 'New lessons are being prepared for this path.'}
            </p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {section.lessons.map((lesson) => (
              <LessonCard
                key={lesson.id}
                lesson={lesson}
                color={section.color}
                progress={getProgressForLesson(lesson)}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Python Tutorials</h1>
        <p className="mt-2 text-gray-500">Follow the core path, then choose your specialization.</p>
      </div>

      {/* Core path — full width at top */}
      {corePath && (
        <div className="mb-10">
          {renderPathSection(corePath)}
        </div>
      )}

      {/* Branch divider — once between core and branches */}
      {branchPaths.length > 0 && <BranchDivider />}

      {/* Branch paths — 3-column grid on desktop, stacked on mobile */}
      {branchPaths.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {branchPaths.map((section) => renderPathSection(section))}
        </div>
      )}
    </div>
  );
}