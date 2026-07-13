export default function ExerciseFeedback({ result }) {
  if (!result) return null;

  const { passed, errors, test_results, summary } = result;

  return (
    <div
      className={`rounded-lg border overflow-hidden ${
        passed
          ? 'border-green-200'
          : 'border-red-200'
      }`}
    >
      {/* Header */}
      <div
        className={`px-4 py-3 flex items-center gap-2 ${
          passed
            ? 'bg-green-50 text-green-800'
            : 'bg-red-50 text-red-800'
        }`}
      >
        {passed ? (
          <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        ) : (
          <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )}
        <span className="font-semibold text-sm">
          {passed ? 'All tests passed!' : 'Some tests failed'}
        </span>
      </div>

      {/* Summary */}
      {summary && (
        <div className="px-4 py-2 text-sm text-gray-600 border-b border-gray-100">
          {summary}
        </div>
      )}

      {/* Errors */}
      {errors && (
        <div className="px-4 py-3">
          <div className="text-sm font-medium text-red-700 mb-1">Errors:</div>
          <pre className="text-sm bg-red-50 border border-red-100 p-3 rounded whitespace-pre-wrap font-mono text-red-600 overflow-x-auto">
            {errors}
          </pre>
        </div>
      )}

      {/* Test results */}
      {test_results?.length > 0 && (
        <div className="divide-y divide-gray-100">
          {test_results.map((tr, i) => (
            <div key={i} className="px-4 py-3">
              <div className="flex items-center gap-2">
                {tr.passed ? (
                  <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                )}
                <span className={`text-sm font-medium ${tr.passed ? 'text-green-700' : 'text-red-700'}`}>
                  Test {i + 1}: {tr.name || (tr.passed ? 'Passed' : 'Failed')}
                </span>
              </div>
              {!tr.passed && (
                <div className="mt-2 ml-6 space-y-1 text-sm">
                  {tr.message && (
                    <div className="text-gray-600">{tr.message}</div>
                  )}
                  {tr.expected_output !== undefined && (
                    <div className="flex gap-4">
                      <div>
                        <span className="text-gray-500">Expected: </span>
                        <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono">{tr.expected_output}</code>
                      </div>
                      <div>
                        <span className="text-gray-500">Got: </span>
                        <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono">{tr.actual_output}</code>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* No tests to display */}
      {(!test_results || test_results.length === 0) && !errors && (
        <div className="px-4 py-3 text-sm text-gray-500">
          {passed ? 'Exercise completed successfully.' : 'No test results available.'}
        </div>
      )}
    </div>
  );
}