import { Link } from 'react-router-dom';

// Map color names to Tailwind classes for the accent strip
const ACCENT_COLORS = {
  indigo: 'bg-indigo-500',
  green: 'bg-green-500',
  blue: 'bg-blue-500',
  purple: 'bg-purple-500',
  gray: 'bg-gray-300',
};

export default function LessonCard({ lesson, color = 'indigo' }) {
  const accentClass = ACCENT_COLORS[color] || ACCENT_COLORS.gray;

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
      </div>
    </Link>
  );
}