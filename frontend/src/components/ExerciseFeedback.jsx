export default function ExerciseFeedback({ result, mode = "test_cases" }) {
  if (!result) return null;

  const { passed, errors, test_results, summary, expected_output, actual_output, comparison_type } = result;

  const passedCount = test_results ? test_results.filter((tr) => tr.passed).length : 0;
  const totalCount = test_results ? test_results.length : 0;
  const isTestSuite = mode === "test_suite";

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
        {isTestSuite && totalCount > 0 && (
          <span className="text-sm ml-auto">
            {passedCount}/{totalCount} tests passed
          </span>
        )}
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
                  {isTestSuite
                    ? tr.name || `Test ${i + 1}`
                    : `Test ${i + 1}: ${tr.name || (tr.passed ? 'Passed' : 'Failed')}`}
                </span>
              </div>
              {!tr.passed && (
                <div className="mt-2 ml-6 space-y-1 text-sm">
                  {tr.message && (
                    <div className="text-gray-600">{tr.message}</div>
                  )}
                  {/* For test_suite mode, no Expected/Got needed */}
                  {!isTestSuite && tr.comparison_type === "code_contains" ? (
                    /* code_contains: show expected value in code, not program output */
                    <div className="flex gap-4">
                      <div>
                        <span className="text-gray-500">Expected in code: </span>
                        {tr.expected_output && tr.expected_output.trim() ? (
                          <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono">{tr.expected_output}</code>
                        ) : (
                          <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono text-gray-400 italic">character</code>
                        )}
                      </div>
                      <div>
                        <span className="text-gray-500">Got in code: </span>
                        <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono text-gray-400 italic">not found</code>
                      </div>
                    </div>
                  ) : !isTestSuite && tr.comparison_type === "comment" ? (
                    /* comment: message field already says enough, no Expected/Got needed */
                    null
                  ) : !isTestSuite && tr.comparison_type === "regex" ? (
                    /* regex: show message (human-readable) and actual output, not raw pattern */
                    <div className="flex gap-4">
                      <div>
                        <span className="text-gray-500">Got: </span>
                        {tr.actual_output && tr.actual_output.trim() ? (
                          <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono">{tr.actual_output}</code>
                        ) : (
                          <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono text-gray-400 italic">(empty)</code>
                        )}
                      </div>
                    </div>
                  ) : !isTestSuite ? (
                    <div className="flex gap-4">
                      <div>
                        <span className="text-gray-500">Expected: </span>
                        {tr.expected_output && tr.expected_output.trim() ? (
                          <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono">{tr.expected_output}</code>
                        ) : (
                          <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono text-gray-400 italic">non-empty output</code>
                        )}
                      </div>
                      <div>
                        <span className="text-gray-500">Got: </span>
                        {tr.actual_output && tr.actual_output.trim() ? (
                          <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono">{tr.actual_output}</code>
                        ) : (
                          <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono text-gray-400 italic">(empty)</code>
                        )}
                      </div>
                    </div>
                  ) : null}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Expected vs Actual display boxes for failed tests -- hidden in test_suite mode */}
      {!isTestSuite && !passed && (expected_output !== undefined || actual_output !== undefined) && test_results?.length > 0 && (
        <div className="px-4 py-3 border-t border-gray-100">
          <div className="text-sm font-medium text-gray-700 mb-3">Output Comparison</div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {comparison_type === "regex" ? (
              <>
                <div className="sm:col-span-2">
                  <div className="text-xs font-medium uppercase tracking-wider text-gray-500 mb-1">Expected pattern:</div>
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-700">
                    {test_results[0]?.message || "Your output should match a specific pattern"}
                  </div>
                </div>
                <div>
                  <div className="text-xs font-medium uppercase tracking-wider text-gray-500 mb-1">Got:</div>
                  <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm font-mono whitespace-pre-wrap overflow-x-auto min-h-[2.5rem]">
                    {actual_output ? (
                      <span className="text-gray-800">{actual_output}</span>
                    ) : (
                      <span className="text-gray-400 italic">(empty)</span>
                    )}
                  </pre>
                </div>
              </>
            ) : (
              <>
                <div>
                  <div className="text-xs font-medium uppercase tracking-wider text-gray-500 mb-1">Expected:</div>
                  <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm font-mono whitespace-pre-wrap overflow-x-auto min-h-[2.5rem]">
                    {expected_output ? (
                      <span className="text-gray-800">{expected_output}</span>
                    ) : (
                      <span className="text-gray-400 italic">(empty)</span>
                    )}
                  </pre>
                </div>
                <div>
                  <div className="text-xs font-medium uppercase tracking-wider text-gray-500 mb-1">Got:</div>
                  <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm font-mono whitespace-pre-wrap overflow-x-auto min-h-[2.5rem]">
                    {actual_output ? (
                      <span className="text-gray-800">{actual_output}</span>
                    ) : (
                      <span className="text-gray-400 italic">(empty)</span>
                    )}
                  </pre>
                </div>
              </>
            )}
          </div>
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