import { Link } from 'react-router-dom';

// Map color names to Tailwind classes for the accent strip
const ACCENT_COLORS = {
  indigo: 'bg-indigo-500',
  green: 'bg-green-500',
  blue: 'bg-blue-500',
  purple: 'bg-purple-500',
  gray: 'bg-gray-300',
};

function getLessonProgress(completed, total) {
  if (total === 0) return 'not-started';
  if (completed >= total) return 'complete';
  if (completed > 0) return 'in-progress';
  return 'not-started';
}

export default function LessonCard({ lesson, color = 'indigo', progress }) {
  const accentClass = ACCENT_COLORS[color] || ACCENT_COLORS.gray;
  const status = progress ? getLessonProgress(progress.completed, progress.total) : null;
  const percentage = progress && progress.total > 0
    ? Math.round((progress.completed / progress.total) * 100)
    : 0;

  return (
    <Link
      to={`/lessons/${lesson.slug}`}
      className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border border-gray-200 overflow-hidden"
    >
      <div className={`h-1 ${accentClass}`} />
      <div className="p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            {lesson.title}
          </h3>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
            Lesson {lesson.order}
          </span>
        </div>
        <p className="mt-2 text-sm text-gray-500">
          {lesson.exercise_count} {lesson.exercise_count === 1 ? 'exercise' : 'exercises'}
        </p>

        {/* Compact completion badge */}
        {status === 'complete' && (
          <div className="mt-2 flex items-center gap-1 text-xs text-green-600">
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
            <span className="font-medium">Complete</span>
          </div>
        )}
        {status === 'in-progress' && (
          <div className="mt-2 flex items-center gap-2">
            <div className="flex-1 max-w-[100px] bg-gray-100 rounded-full h-1.5">
              <div
                className="bg-amber-400 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${percentage}%` }}
              />
            </div>
            <span className="text-xs text-amber-600 font-medium whitespace-nowrap">
              {progress.completed}/{progress.total}
            </span>
          </div>
        )}
      </div>
    </Link>
  );
}

export { getLessonProgress };