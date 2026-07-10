import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ExerciseFeedback from '../components/ExerciseFeedback.jsx';

describe('ExerciseFeedback', () => {
  it('returns null when result is null', () => {
    const { container } = render(<ExerciseFeedback result={null} />);
    expect(container.innerHTML).toBe('');
  });

  it('returns null when result is undefined', () => {
    const { container } = render(<ExerciseFeedback />);
    expect(container.innerHTML).toBe('');
  });

  it('shows "All tests passed!" when all tests pass', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: true,
          test_results: [
            { passed: true, name: 'Test 1' },
            { passed: true, name: 'Test 2' },
          ],
        }}
      />
    );
    expect(screen.getByText('All tests passed!')).toBeInTheDocument();
  });

  it('shows "Some tests failed" when tests fail', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: false,
          test_results: [
            { passed: true, name: 'Test 1' },
            { passed: false, name: 'Test 2', expected_output: '5', actual_output: '3' },
          ],
        }}
      />
    );
    expect(screen.getByText('Some tests failed')).toBeInTheDocument();
  });

  it('displays compile/runtime errors with header', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: false,
          errors: 'ZeroDivisionError: division by zero',
          test_results: [],
        }}
      />
    );
    expect(screen.getByText('Errors:')).toBeInTheDocument();
    expect(screen.getByText('ZeroDivisionError: division by zero')).toBeInTheDocument();
  });

  it('shows test result details with expected vs actual', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: false,
          test_results: [
            {
              passed: false,
              name: 'Addition test',
              expected_output: '5',
              actual_output: '3',
            },
          ],
        }}
      />
    );
    expect(screen.getByText(/Expected/)).toBeInTheDocument();
    expect(screen.getByText(/Got/)).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('shows test result name in format "Test N: name"', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: true,
          test_results: [{ passed: true, name: 'should return correct sum' }],
        }}
      />
    );
    expect(screen.getByText(/should return correct sum/)).toBeInTheDocument();
    expect(screen.getByText(/Test 1/)).toBeInTheDocument();
  });

  it('shows success message when no test results but passed', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: true,
          test_results: [],
        }}
      />
    );
    expect(screen.getByText('All tests passed!')).toBeInTheDocument();
    expect(screen.getByText('Exercise completed successfully.')).toBeInTheDocument();
  });

  it('shows no results message when no test results and failed', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: false,
          test_results: [],
        }}
      />
    );
    expect(screen.getByText('No test results available.')).toBeInTheDocument();
  });

  it('displays summary when provided', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: true,
          summary: 'Great job! All tests passed.',
          test_results: [{ passed: true }],
        }}
      />
    );
    expect(screen.getByText('Great job! All tests passed.')).toBeInTheDocument();
  });

  it('displays test message when test fails with message', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: false,
          test_results: [
            {
              passed: false,
              name: 'Division test',
              message: 'Expected 2.5 but got 0',
              expected_output: '2.5',
              actual_output: '0',
            },
          ],
        }}
      />
    );
    expect(screen.getByText('Expected 2.5 but got 0')).toBeInTheDocument();
  });

  it('shows "(empty)" label when actual_output is empty', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: false,
          test_results: [
            {
              passed: false,
              name: 'No output test',
              expected_output: 'hello',
              actual_output: '',
            },
          ],
        }}
      />
    );
    expect(screen.getByText('(empty)')).toBeInTheDocument();
    expect(screen.getByText('hello')).toBeInTheDocument();
  });

  it('shows "non-empty output" label when expected_output is empty', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: false,
          test_results: [
            {
              passed: false,
              name: 'Print something',
              expected_output: '',
              actual_output: '',
            },
          ],
        }}
      />
    );
    expect(screen.getByText('non-empty output')).toBeInTheDocument();
    expect(screen.getByText('(empty)')).toBeInTheDocument();
  });

  it('renders dedicated Expected/Got display boxes with top-level outputs', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: false,
          expected_output: 'Hello, World!\n',
          actual_output: 'Hellow World\n',
          test_results: [
            {
              passed: false,
              name: 'Print Hello World',
              expected_output: 'Hello, World!\n',
              actual_output: 'Hellow World\n',
              message: "Expected: 'Hello, World!\\n', but got: 'Hellow World\\n'",
            },
          ],
        }}
      />
    );
    expect(screen.getByText('Output Comparison')).toBeInTheDocument();
    // "Expected:" label is the uppercase heading for the box
    const expectedLabels = screen.getAllByText('Expected:');
    expect(expectedLabels.length).toBe(2); // one in inline, one in box
    const gotLabels = screen.getAllByText('Got:');
    expect(gotLabels.length).toBe(2); // one in inline, one in box
    // Content appears in both inline code and box pre
    expect(screen.getAllByText('Hello, World!').length).toBe(2);
    expect(screen.getAllByText('Hellow World').length).toBe(2);
  });

  it('does not show Output Comparison section when tests pass', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: true,
          expected_output: 'Hello, World!\n',
          actual_output: 'Hello, World!\n',
          test_results: [
            { passed: true, name: 'Print Hello World' },
          ],
        }}
      />
    );
    expect(screen.queryByText('Output Comparison')).not.toBeInTheDocument();
  });

  it('shows "(empty)" in Expected box when top-level expected_output is empty for failed test', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: false,
          expected_output: '',
          actual_output: 'some output',
          test_results: [
            {
              passed: false,
              name: 'Non-empty test',
              expected_output: '',
              actual_output: 'some output',
            },
          ],
        }}
      />
    );
    expect(screen.getByText('Output Comparison')).toBeInTheDocument();
    // The inline Expected shows "non-empty output" while the box shows "(empty)"
    // The box Got shows "some output" so only 1 "(empty)" total
    expect(screen.getAllByText('(empty)').length).toBe(1);
  });

  it('shows "(empty)" in Got box when actual_output is empty string (comment-only submission)', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: false,
          expected_output: 'Hello, World!\n',
          actual_output: '',
          test_results: [
            {
              passed: false,
              name: 'Print Hello World',
              expected_output: 'Hello, World!\n',
              actual_output: '',
              message: "Expected: 'Hello, World!\\n', but got: ''",
            },
          ],
        }}
      />
    );
    // Dedicated Output Comparison boxes
    expect(screen.getByText('Output Comparison')).toBeInTheDocument();
    // "Hello, World!" appears in both inline code and dedicated box
    expect(screen.getAllByText('Hello, World!').length).toBe(2);
    // "(empty)" appears in the Got box (once), and the inline Got also shows "(empty)"
    expect(screen.getAllByText('(empty)').length).toBe(2);
  });

  it('shows "(empty)" in both dedicated boxes when both top-level outputs are empty', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: false,
          expected_output: '',
          actual_output: '',
          test_results: [
            {
              passed: false,
              name: 'Both empty test',
              expected_output: '',
              actual_output: '',
            },
          ],
        }}
      />
    );
    expect(screen.getByText('Output Comparison')).toBeInTheDocument();
    // The dedicated boxes: both show "(empty)"
    // The inline display shows "non-empty output" for expected and "(empty)" for Got
    // total: 2 from boxes + 1 from inline Got = 3
    expect(screen.getAllByText('(empty)').length).toBe(3);
    expect(screen.getByText('non-empty output')).toBeInTheDocument();
  });

  it('shows Output Comparison when top-level outputs are provided but test_results missing', () => {
    render(
      <ExerciseFeedback
        result={{
          passed: false,
          expected_output: 'expected value',
          actual_output: 'actual value',
          test_results: [
            {
              passed: false,
              name: 'Fallback test',
              expected_output: 'expected value',
              actual_output: 'actual value',
            },
          ],
        }}
      />
    );
    expect(screen.getByText('Output Comparison')).toBeInTheDocument();
    // Text appears in both inline code and dedicated box
    expect(screen.getAllByText('expected value').length).toBe(2);
    expect(screen.getAllByText('actual value').length).toBe(2);
  });
});