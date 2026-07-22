import { useState } from 'react';
import LessonCard from './LessonCard.jsx';

const PATH_ICONS = {
  core: '\uD83D\uDCD6',
  'data-processing': '\uD83D\uDCCA',
  api: '\u2699\uFE0F',
  'machine-learning': '\uD83E\uDD16',
};

const ACCENT_MAP = {
  indigo: {
    border: 'border-indigo-200',
    bg: 'bg-indigo-50',
    text: 'text-indigo-700',
    hover: 'hover:border-indigo-300',
    tabBorder: 'border-indigo-500',
    tabText: 'text-indigo-600',
    header: 'text-indigo-800',
  },
  green: {
    border: 'border-green-200',
    bg: 'bg-green-50',
    text: 'text-green-700',
    hover: 'hover:border-green-300',
    tabBorder: 'border-green-500',
    tabText: 'text-green-600',
    header: 'text-green-800',
  },
  blue: {
    border: 'border-blue-200',
    bg: 'bg-blue-50',
    text: 'text-blue-700',
    hover: 'hover:border-blue-300',
    tabBorder: 'border-blue-500',
    tabText: 'text-blue-600',
    header: 'text-blue-800',
  },
  purple: {
    border: 'border-purple-200',
    bg: 'bg-purple-50',
    text: 'text-purple-700',
    hover: 'hover:border-purple-300',
    tabBorder: 'border-purple-500',
    tabText: 'text-purple-600',
    header: 'text-purple-800',
  },
};

function getAccent(color) {
  return ACCENT_MAP[color] || ACCENT_MAP.indigo;
}

const FALLBACK_ICONS = {
  'machine-learning': '\uD83E\uDD16',
};

export default function LessonsPoc({ paths = [], getProgressForLesson }) {
  const [selectedPath, setSelectedPath] = useState(null);

  // Empty state
  if (!paths || paths.length === 0) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Python Tutorials</h1>
          <p className="mt-2 text-gray-500">Follow the core path, then choose your specialization.</p>
        </div>
        <div className="text-center py-12 text-gray-400">
          No lessons available yet. Check back soon!
        </div>
      </div>
    );
  }

  // Overview state: path cards
  if (selectedPath === null) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Python Tutorials</h1>
          <p className="mt-2 text-gray-500">Follow the core path, then choose your specialization.</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {paths.map((pathItem) => {
            const accent = getAccent(pathItem.color);
            const icon = PATH_ICONS[pathItem.path] || '\uD83D\uDCDA';
            const lessonCount = pathItem.lessons ? pathItem.lessons.length : 0;
            return (
              <button
                key={pathItem.path}
                type="button"
                onClick={() => setSelectedPath(pathItem.path)}
                className={`text-left rounded-lg border-2 ${accent.border} ${accent.bg} p-6 shadow-sm ${accent.hover} hover:shadow-md transition-all cursor-pointer w-full`}
                data-testid={`path-card-${pathItem.path}`}
              >
                <div className="text-4xl mb-3" data-testid={`path-icon-${pathItem.path}`}>{icon}</div>
                <h3 className={`text-xl font-semibold ${accent.text}`}>{pathItem.display_name}</h3>
                <p className="mt-1 text-sm text-gray-600">{pathItem.description}</p>
                <p className="mt-3 text-xs font-medium text-gray-400">
                  {lessonCount} {lessonCount === 1 ? 'lesson' : 'lessons'}
                </p>
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  // Path detail state: tab bar + lesson cards
  const selectedPathData = paths.find((p) => p.path === selectedPath);
  const selectedAccent = getAccent(selectedPathData ? selectedPathData.color : 'indigo');

  return (
    <div data-testid="path-detail-view">
      {/* Back link */}
      <button
        type="button"
        onClick={() => setSelectedPath(null)}
        className="mb-4 inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors"
        data-testid="back-all-paths"
      >
        <span aria-hidden="true">&larr;</span>
        <span>All paths</span>
      </button>

      {/* Tab bar */}
      <div className="overflow-x-auto -mx-4 px-4 mb-6">
        <div className="flex gap-6 border-b border-gray-200 min-w-max" data-testid="tab-bar">
          {paths.map((pathItem) => {
            const isActive = pathItem.path === selectedPath;
            const accent = getAccent(pathItem.color);
            return (
              <button
                key={pathItem.path}
                type="button"
                onClick={() => setSelectedPath(pathItem.path)}
                className={`pb-2 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                  isActive
                    ? `${accent.tabBorder} ${accent.tabText}`
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
                data-testid={`tab-${pathItem.path}`}
                data-active={isActive ? 'true' : 'false'}
              >
                {PATH_ICONS[pathItem.path] || '\uD83D\uDCDA'} {pathItem.display_name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected path header */}
      {selectedPathData && (
        <div className="mb-6">
          <h2 className={`text-2xl font-bold ${selectedAccent.header}`}>
            {selectedPathData.display_name}
          </h2>
          <p className="text-gray-600 text-sm mt-1">{selectedPathData.description}</p>
        </div>
      )}

      {/* Lesson cards grid */}
      {selectedPathData && selectedPathData.lessons && selectedPathData.lessons.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3" data-testid="lesson-grid">
          {selectedPathData.lessons.map((lesson) => (
            <LessonCard
              key={lesson.id}
              lesson={lesson}
              color={selectedPathData.color}
              progress={getProgressForLesson ? getProgressForLesson(lesson) : undefined}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12" data-testid="empty-path-placeholder">
          <div className="text-5xl mb-3 opacity-40">
            {(selectedPathData && FALLBACK_ICONS[selectedPathData.path]) || '\uD83D\uDCDA'}
          </div>
          <p className="text-gray-400 font-medium">Coming Soon</p>
          <p className="text-gray-400 text-sm mt-1">
            {selectedPathData && selectedPathData.path === 'machine-learning'
              ? 'Machine Learning lessons are being prepared.'
              : 'New lessons are being prepared for this path.'}
          </p>
        </div>
      )}
    </div>
  );
}
