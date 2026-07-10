import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';
import { useProgress } from '../hooks/useProgress.jsx';
import ProgressBar from '../components/ProgressBar.jsx';

export default function Progress() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const { progress, loading, error, refetch } = useProgress();

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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500 text-lg">Loading progress...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
        Failed to load progress: {error}
      </div>
    );
  }

  const summary = progress?.summary;

  // Group progress by lesson slug
  const byLesson = {};
  const lessonTotals = progress?.lesson_totals || {};
  progress?.progress?.forEach((p) => {
    const slug = p.lesson_slug;
    if (!byLesson[slug]) byLesson[slug] = { completed: 0 };
    if (p.completed) byLesson[slug].completed++;
  });

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Progress</h1>
        <p className="mt-2 text-gray-500">
          Track your learning journey across all lessons.
        </p>
      </div>

      {summary && (
        <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Overall Progress</h2>
          <ProgressBar
            completed={summary.completed_exercises}
            total={summary.total_exercises}
          />
          {summary.completed_exercises === summary.total_exercises && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm">
              Congratulations! You've completed all exercises! 🎉
            </div>
          )}
        </div>
      )}

      <div className="space-y-4">
        {Object.entries(byLesson).map(([slug, data]) => (
          <div
            key={slug}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-gray-900 capitalize">
                {slug.replace(/^\d+-/, '').replace(/-/g, ' ')}
              </h3>
              <span className="text-sm text-gray-500">
                {data.completed}/{lessonTotals[slug] || 0} exercises
              </span>
            </div>
            <ProgressBar completed={data.completed} total={lessonTotals[slug] || 0} />
          </div>
        ))}

        {(!progress?.progress || progress.progress.length === 0) && (
          <div className="text-center py-12 text-gray-400">
            No progress yet. Start a lesson to begin tracking!
          </div>
        )}
      </div>
    </div>
  );
}