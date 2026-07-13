export default function OutputPanel({ output, error, loading, onClear }) {
  if (loading) {
    return (
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
        <div className="flex items-center space-x-3 text-gray-400 text-sm">
          <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span>Running code...</span>
        </div>
      </div>
    );
  }

  if (!output && !error) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-gray-400 text-sm flex items-center gap-2">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
        </svg>
        Run your code to see output here
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium uppercase tracking-wider text-gray-500">
          {error ? 'Errors' : 'Output'}
        </span>
        {onClear && (
          <button
            onClick={onClear}
            className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
            title="Clear output"
          >
            Clear
          </button>
        )}
      </div>
      <div className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
        <pre className="p-4 font-mono text-sm leading-relaxed overflow-x-auto whitespace-pre-wrap">
          {error ? (
            <span className="text-red-400">{error}</span>
          ) : (
            <span className="text-green-400">{output}</span>
          )}
        </pre>
      </div>
    </div>
  );
}