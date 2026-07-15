import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { useAuth } from '../hooks/useAuth.jsx';
import CodeEditor from '../components/CodeEditor.jsx';
import OutputPanel from '../components/OutputPanel.jsx';
import ExerciseFeedback from '../components/ExerciseFeedback.jsx';
import * as api from '../api/client.js';

export default function LessonView() {
  const { slug } = useParams();
  const { isAuthenticated } = useAuth();
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeExercise, setActiveExercise] = useState(null);
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [runError, setRunError] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    async function fetchLesson() {
      try {
        const data = await api.getLesson(slug);
        if (!data) {
          setLesson(null);
          return;
        }
        setLesson(data);
        if (data.exercises && data.exercises.length > 0) {
          setActiveExercise(data.exercises[0]);
          setCode(data.exercises[0].starter_code || '');
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchLesson();
  }, [slug]);

  const handleExerciseChange = (exercise) => {
    setActiveExercise(exercise);
    setCode(exercise.starter_code || '');
    setOutput('');
    setRunError('');
    setFeedback(null);
  };

  const handleRun = async () => {
    if (!activeExercise || !isAuthenticated) return;
    setRunning(true);
    setOutput('');
    setRunError('');
    setFeedback(null);
    try {
      const result = await api.runExercise(activeExercise.id, code);
      if (result.errors) {
        setRunError(result.errors);
      } else {
        setOutput(result.actual_output || '');
      }
    } catch (err) {
      setRunError(err.message);
    } finally {
      setRunning(false);
    }
  };

  const handleSubmit = async () => {
    if (!activeExercise || !isAuthenticated) return;
    setRunning(true);
    setOutput('');
    setRunError('');
    setFeedback(null);
    try {
      const result = await api.submitExercise(activeExercise.id, code);
      setFeedback(result);
      if (result.errors) {
        setRunError(result.errors);
      } else {
        setOutput(result.actual_output || '');
      }
    } catch (err) {
      setRunError(err.message);
    } finally {
      setRunning(false);
    }
  };

  const handleClearOutput = () => {
    setOutput('');
    setRunError('');
    setFeedback(null);
  };

  const handleEditorRun = () => {
    handleRun();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-3 text-gray-500 text-lg">
          <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span>Loading lesson...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
        <p className="font-medium mb-1">Failed to load lesson</p>
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900">Lesson not found</h2>
        <p className="mt-2 text-gray-500">The lesson you're looking for doesn't exist or has been removed.</p>
        <Link to="/lessons" className="mt-4 text-indigo-600 hover:text-indigo-500 inline-block font-medium">
          &larr; Back to lessons
        </Link>
      </div>
    );
  }

  return (
    <>
      {/* Desktop: fixed full-height split layout — breaks out of Layout's max-w-7xl */}
      <div className="hidden md:flex md:fixed md:inset-x-0 md:top-16 md:bottom-0 flex-col bg-gray-50">
        {/* Breadcrumb bar */}
        <div className="flex-shrink-0 bg-white border-b border-gray-200 px-6 lg:px-8 py-3">
          <Link
            to="/lessons"
            className="text-sm text-indigo-600 hover:text-indigo-500 inline-flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Lessons
          </Link>
        </div>

        {/* Split layout */}
        <div className="flex-1 flex min-h-0">
          {/* Left panel: lesson content */}
          <div className="w-1/2 overflow-y-auto bg-white border-r border-gray-200">
            <div className="px-6 lg:px-8 py-6">
              <div className="mb-4">
                <h1 className="text-2xl font-bold text-gray-900">{lesson.title}</h1>
                {lesson.description && (
                  <p className="mt-1 text-base text-gray-500">{lesson.description}</p>
                )}
              </div>

              <div className="prose prose-indigo max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeHighlight]}
                >
                  {lesson.content}
                </ReactMarkdown>
              </div>
            </div>
          </div>

          {/* Right panel: exercises + editor + output */}
          <div className="w-1/2 overflow-y-auto">
            <div className="px-6 lg:px-8 py-6 flex flex-col min-h-full">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Exercises</h2>

              {/* Exercise tabs */}
              <div className="flex space-x-2 mb-4 overflow-x-auto pb-1">
                {lesson.exercises?.map((ex, idx) => (
                  <button
                    key={ex.id}
                    onClick={() => handleExerciseChange(ex)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                      activeExercise?.id === ex.id
                        ? 'bg-indigo-600 text-white shadow-sm'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {idx + 1}. {ex.title}
                  </button>
                ))}
              </div>

              {activeExercise ? (
                <div className="flex-1">
                  {/* Exercise instructions */}
                  {activeExercise.instruction && (
                    <div className="mb-4 text-sm text-gray-700 prose prose-sm max-w-none">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeHighlight]}
                      >
                        {activeExercise.instruction}
                      </ReactMarkdown>
                    </div>
                  )}

                  {/* Code editor */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Your Code
                    </label>
                    <CodeEditor
                      key={activeExercise.id}
                      value={code}
                      onChange={setCode}
                      placeholder={activeExercise.starter_code || '# Write your Python code here'}
                      onRun={handleEditorRun}
                    />
                  </div>

                  {/* Action buttons */}
                  <div className="flex space-x-3 mb-4">
                    <button
                      onClick={handleRun}
                      disabled={running || !isAuthenticated}
                      className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium flex items-center space-x-1.5"
                    >
                      {running ? (
                        <>
                          <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                          <span>Running...</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span>Run Code</span>
                        </>
                      )}
                    </button>
                    <button
                      onClick={handleSubmit}
                      disabled={running || !isAuthenticated}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium flex items-center space-x-1.5"
                    >
                      {running ? (
                        <>
                          <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                          <span>Submitting...</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span>Submit</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Authentication prompt */}
                  {!isAuthenticated && (
                    <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-lg text-sm">
                      <Link to="/login" className="underline font-medium">Sign in</Link> to run and submit code.
                    </div>
                  )}

                  {/* Output panel */}
                  <OutputPanel
                    output={output}
                    error={runError}
                    loading={running && !feedback}
                    onClear={handleClearOutput}
                  />

                  {/* Exercise feedback */}
                  {feedback && (
                    <div className="mt-4">
                      <ExerciseFeedback result={feedback} />
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center text-gray-400">
                  <p>No exercises available for this lesson yet.</p>
                </div>
              )}

            </div>
          </div>
        </div>
      </div>

      {/* Mobile: stacked layout within normal page flow */}
      <div className="md:hidden flex flex-col">
        {/* Breadcrumb */}
        <div className="flex-shrink-0 mb-4">
          <Link
            to="/lessons"
            className="text-sm text-indigo-600 hover:text-indigo-500 inline-flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Lessons
          </Link>
        </div>

        {/* Lesson title */}
        <div className="flex-shrink-0 mb-4">
          <h1 className="text-2xl font-bold text-gray-900">{lesson.title}</h1>
          {lesson.description && (
            <p className="mt-1 text-base text-gray-500">{lesson.description}</p>
          )}
        </div>

        {/* Lesson content */}
        <div className="prose prose-indigo max-w-none mb-8">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeHighlight]}
          >
            {lesson.content}
          </ReactMarkdown>
        </div>

        {/* Exercise area */}
        <div className="min-w-0">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Exercises</h2>

          {/* Exercise tabs */}
          <div className="flex space-x-2 mb-4 overflow-x-auto pb-1">
            {lesson.exercises?.map((ex, idx) => (
              <button
                key={ex.id}
                onClick={() => handleExerciseChange(ex)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                  activeExercise?.id === ex.id
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {idx + 1}. {ex.title}
              </button>
            ))}
          </div>

          {activeExercise ? (
            <div>
              {/* Exercise instructions */}
              {activeExercise.instruction && (
                <div className="mb-4 text-sm text-gray-700 prose prose-sm max-w-none">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeHighlight]}
                  >
                    {activeExercise.instruction}
                  </ReactMarkdown>
                </div>
              )}

              {/* Code editor */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Code
                </label>
                <CodeEditor
                  key={activeExercise.id}
                  value={code}
                  onChange={setCode}
                  placeholder={activeExercise.starter_code || '# Write your Python code here'}
                  onRun={handleEditorRun}
                />
              </div>

              {/* Action buttons */}
              <div className="flex space-x-3 mb-4">
                <button
                  onClick={handleRun}
                  disabled={running || !isAuthenticated}
                  className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium flex items-center space-x-1.5"
                >
                  {running ? (
                    <>
                      <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      <span>Running...</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>Run Code</span>
                    </>
                  )}
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={running || !isAuthenticated}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium flex items-center space-x-1.5"
                >
                  {running ? (
                    <>
                      <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      <span>Submitting...</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>Submit</span>
                    </>
                  )}
                </button>
              </div>

              {/* Authentication prompt */}
              {!isAuthenticated && (
                <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-lg text-sm">
                  <Link to="/login" className="underline font-medium">Sign in</Link> to run and submit code.
                </div>
              )}

              {/* Output panel */}
              <OutputPanel
                output={output}
                error={runError}
                loading={running && !feedback}
                onClear={handleClearOutput}
              />

              {/* Exercise feedback */}
              {feedback && (
                <div className="mt-4">
                  <ExerciseFeedback result={feedback} />
                </div>
              )}
            </div>
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center text-gray-400">
              <p>No exercises available for this lesson yet.</p>
            </div>
          )}

        </div>
      </div>
    </>
  );
}