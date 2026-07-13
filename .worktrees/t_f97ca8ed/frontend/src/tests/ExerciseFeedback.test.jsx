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
});