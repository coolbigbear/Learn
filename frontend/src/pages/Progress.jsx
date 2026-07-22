import React, { useState, useEffect, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';
import { useProgress } from '../hooks/useProgress.jsx';
import * as api from '../api/client.js';
import ProgressBar from '../components/ProgressBar.jsx';

const STATUS_ICON = {
  complete: '✅',
  'in-progress': '🟡',
  'not-started': '⚪',
};

const STATUS_LABEL = {
  complete: 'Complete',
  'in-progress': 'In Progress',
  'not-started': 'Not Started',
};

function getLessonStatus(completed, total) {
  if (total === 0) return 'not-started';
  if (completed >= total) return 'complete';
  if (completed > 0) return 'in-progress';
  return 'not-started';
}

function getStatusBarColor(status) {
  switch (status) {
    case 'complete':
      return 'bg-green-500';
    case 'in-progress':
      return 'bg-amber-400';
    default:
      return 'bg-gray-300';
  }
}

/** Single exercise row inside an expanded lesson. */
const ExerciseRow = React.memo(function ExerciseRow({ exercise, progressItem }) {
  const icon = progressItem?.completed ? '✅' : progressItem?.attempts > 0 ? '🔄' : '❌';
  const label = progressItem?.completed
    ? 'Passed'
    : progressItem?.attempts > 0
      ? 'Attempted'
      : 'Not Yet';

  return (
    <div className="flex items-center justify-between py-2 px-3 rounded hover:bg-gray-50 transition-colors">
      <div className="flex items-center gap-2">
        <span className="text-sm">{icon}</span>
        <span className="text-sm text-gray-800">{exercise.exercise_title || exercise.title}</span>
      </div>
      <div className="flex items-center gap-3">
        {progressItem?.attempts > 0 && (
          <span className="text-xs text-gray-400">
            {progressItem.attempts} {progressItem.attempts === 1 ? 'attempt' : 'attempts'}
          </span>
        )}
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
          progressItem?.completed
            ? 'bg-green-100 text-green-700'
            : progressItem?.attempts > 0
              ? 'bg-amber-100 text-amber-700'
              : 'bg-gray-100 text-gray-500'
        }`}>
          {label}
        </span>
      </div>
    </div>
  );
});

/** Single lesson row with expand/collapse. */
const LessonProgressRow = React.memo(function LessonProgressRow({
  lesson,
  completed,
  total,
  exercises,
  progressByExercise,
  isExpanded,
  onToggle,
}) {
  const status = getLessonStatus(completed, total);
  const barColor = getStatusBarColor(status);
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      {/* Lesson header — clickable to expand */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 bg-white hover:bg-gray-50 transition-colors text-left"
        aria-expanded={isExpanded}
      >
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <span className="text-lg flex-shrink-0">{STATUS_ICON[status]}</span>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <h4 className="font-medium text-gray-900 truncate">{lesson.title}</h4>
              {status === 'complete' && (
                <span className="text-xs text-green-600 bg-green-50 px-1.5 py-0.5 rounded whitespace-nowrap">
                  All exercises passed
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs text-gray-400">Lesson {lesson.order}</span>
              <span className={`text-xs font-medium px-1.5 py-0.5 rounded-full ${
                status === 'complete'
                  ? 'bg-green-100 text-green-700'
                  : status === 'in-progress'
                    ? 'bg-amber-100 text-amber-700'
                    : 'bg-gray-100 text-gray-500'
              }`}>
                {STATUS_LABEL[status]}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0 ml-4">
          <span className="text-sm text-gray-500 whitespace-nowrap">
            {completed}/{total}
          </span>
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Progress bar */}
      <div className="px-4 pb-2">
        <div className="w-full bg-gray-100 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full transition-all duration-300 ${barColor}`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Expanded exercise detail */}
      {isExpanded && (
        <div className="border-t border-gray-100 bg-gray-50 px-4 py-2 space-y-0.5">
          {exercises.length > 0 ? (
            exercises.map((exercise) => (
              <ExerciseRow
                key={exercise.exercise_id || exercise.id || exercise.slug}
                exercise={exercise}
                progressItem={progressByExercise[exercise.exercise_id || exercise.id || exercise.slug]}
              />
            ))
          ) : (
            <div className="text-center py-4 text-gray-400 text-sm">
              No exercises for this lesson.
            </div>
          )}
        </div>
      )}
    </div>
  );
});

/** Path section with all its lessons. */
function PathSection({ pathData, mergedLessons, onToggleLesson, expandedLessons }) {
  const colors = {
    indigo: { border: 'border-indigo-200', bg: 'bg-indigo-50', header: 'text-indigo-800' },
    green: { border: 'border-green-200', bg: 'bg-green-50', header: 'text-green-800' },
    blue: { border: 'border-blue-200', bg: 'bg-blue-50', header: 'text-blue-800' },
    purple: { border: 'border-purple-200', bg: 'bg-purple-50', header: 'text-purple-800' },
  };
  const c = colors[pathData.color] || colors.indigo;
  const isEmpty = mergedLessons.length === 0;

  return (
    <div className={`rounded-lg border ${c.border} ${c.bg} p-5`}>
      <h2 className={`text-xl font-bold ${c.header} mb-1`}>{pathData.display_name}</h2>
      <p className="text-sm text-gray-600 mb-4">{pathData.description}</p>

      {isEmpty ? (
        <div className="text-center py-8">
          <p className="text-gray-400 font-medium">Coming Soon</p>
          <p className="text-gray-400 text-sm mt-1">Lessons are being prepared for this path.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {mergedLessons.map((item) => (
            <LessonProgressRow
              key={item.lesson.slug}
              lesson={item.lesson}
              completed={item.completed}
              total={item.total}
              exercises={item.exercises}
              progressByExercise={item.progressByExercise}
              isExpanded={expandedLessons.has(item.lesson.slug)}
              onToggle={() => onToggleLesson(item.lesson.slug)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function Progress() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const { progress, loading: progressLoading, error: progressError } = useProgress();

  const [pathsData, setPathsData] = useState(null);
  const [pathsLoading, setPathsLoading] = useState(true);
  const [pathsError, setPathsError] = useState(null);
  const [expandedLessons, setExpandedLessons] = useState(new Set());

  // Fetch lessons-by-path data
  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      setPathsLoading(false);
      return;
    }

    async function fetchPaths() {
      try {
        const data = await api.getLessonsByPath();
        if (data && data.paths && Array.isArray(data.paths)) {
          setPathsData(data.paths);
        } else {
          // Fallback — try flat grouped format
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
          setPathsData(mapped.length > 0 ? mapped : []);
        }
      } catch {
        setPathsData([]);
        setPathsError('Failed to load lesson paths.');
      } finally {
        setPathsLoading(false);
      }
    }

    fetchPaths();
  }, [isAuthenticated, authLoading]);

  const handleToggleLesson = useCallback((slug) => {
    setExpandedLessons((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) {
        next.delete(slug);
      } else {
        next.add(slug);
      }
      return next;
    });
  }, []);

  // Loading state
  if (authLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500 text-lg">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (progressLoading || pathsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500 text-lg">Loading progress...</div>
      </div>
    );
  }

  // Error state — show what we can
  const hasFatalError = progressError && !progress?.summary;

  if (hasFatalError) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
        Failed to load progress: {progressError}
      </div>
    );
  }

  const summary = progress?.summary;
  const lessonTotals = progress?.lesson_totals || {};

  // Build a lookup: lesson_slug -> { completed, exercises[] }
  const progressByLesson = {};

  if (progress?.progress) {
    for (const p of progress.progress) {
      const slug = p.lesson_slug;
      if (!progressByLesson[slug]) {
        progressByLesson[slug] = { completed: 0, exercises: [] };
      }
      if (p.completed) progressByLesson[slug].completed++;
      progressByLesson[slug].exercises.push(p);
    }
  }

  // Merge lessons data with progress
  const mergedPaths = (pathsData || []).map((path) => {
    const mergedLessons = path.lessons.map((lesson) => {
      // Use lesson progress data as the primary exercise source, cross-referencing metadata
      const lessonProg = progressByLesson[lesson.slug] || { completed: 0, exercises: [] };
      const total = lessonTotals[lesson.slug] || lesson.exercise_count || 0;

      // Build exercise list from progress data
      const exercises = lessonProg.exercises.length > 0
        ? lessonProg.exercises
        : [];

      // Lookup: given an exercise dict from progress, find it by exercise_id
      const progressByExercise = {};
      for (const ex of exercises) {
        progressByExercise[ex.exercise_id] = ex;
      }

      return {
        lesson,
        completed: lessonProg.completed,
        total,
        exercises,
        progressByExercise,
      };
    });

    return { pathData: path, mergedLessons };
  });

  // Check if all done
  const allComplete = summary && summary.total_exercises > 0
    && summary.completed_exercises === summary.total_exercises;

  // Empty state — no progress at all and no lessons data
  if (
    (!progress?.progress || progress.progress.length === 0) &&
    (!pathsData || pathsData.length === 0)
  ) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Progress</h1>
          <p className="mt-2 text-gray-500">Track your learning journey across all lessons.</p>
        </div>
        <div className="text-center py-12 text-gray-400">
          No progress yet. Start a lesson to begin tracking!
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Progress</h1>
        <p className="mt-2 text-gray-500">Track your learning journey across all lessons.</p>
      </div>

      {/* Overall summary */}
      {summary && (
        <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Overall Progress</h2>
          <ProgressBar
            completed={summary.completed_exercises}
            total={summary.total_exercises}
          />
          {allComplete && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm">
              Congratulations! You've completed all exercises! 🎉
            </div>
          )}
        </div>
      )}

      {/* Path sections */}
      {mergedPaths.length > 0 ? (
        <div className="space-y-6">
          {mergedPaths.map(({ pathData, mergedLessons }) => (
            <PathSection
              key={pathData.path}
              pathData={pathData}
              mergedLessons={mergedLessons}
              onToggleLesson={handleToggleLesson}
              expandedLessons={expandedLessons}
            />
          ))}
        </div>
      ) : (
        /* Show lessons grouped by slug if no path data (fallback) */
        <div className="space-y-4">
          {Object.entries(progressByLesson).map(([slug, data]) => {
            const total = lessonTotals[slug] || 0;
            const status = getLessonStatus(data.completed, total);
            const barColor = getStatusBarColor(status);
            const percentage = total > 0 ? Math.round((data.completed / total) * 100) : 0;

            return (
              <div key={slug} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span>{STATUS_ICON[status]}</span>
                    <h3 className="font-medium text-gray-900 capitalize">
                      {slug.replace(/^\d+-/, '').replace(/-/g, ' ')}
                    </h3>
                  </div>
                  <span className="text-sm text-gray-500">
                    {data.completed}/{total} exercises
                  </span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${barColor}`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Path error notice */}
      {pathsError && (
        <div className="mt-4 text-sm text-amber-600 bg-amber-50 border border-amber-200 rounded-lg p-3">
          {pathsError} Progress is shown grouped by lesson slug.
        </div>
      )}
    </div>
  );
}