import { Link } from 'react-router-dom';

export default function LessonCard({ lesson }) {
  return (
    <Link
      to={`/lessons/${lesson.slug}`}
      className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border border-gray-200 overflow-hidden"
    >
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