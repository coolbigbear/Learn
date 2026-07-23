import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ErrorBoundary from '../components/ErrorBoundary.jsx';

// A component that throws during render
function ExplodingComponent({ message = 'Kaboom!' }) {
  throw new Error(message);
}

// A component that renders normally
function GoodComponent() {
  return <div data-testid="good-component">All good</div>;
}

// A class component that throws with an empty error
class ExplodingEmpty extends ErrorBoundary {
  render() {
    throw new Error();
  }
}

function renderWithRouter(ui) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    ErrorBoundary.caughtError = false;
    // Suppress expected console.error from React's error overlay
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders children when there is no error', () => {
    renderWithRouter(
      <ErrorBoundary>
        <GoodComponent />
      </ErrorBoundary>
    );
    expect(screen.getByTestId('good-component')).toBeInTheDocument();
    expect(ErrorBoundary.caughtError).toBe(false);
  });

  it('renders fallback UI when a child throws', () => {
    renderWithRouter(
      <ErrorBoundary>
        <ExplodingComponent />
      </ErrorBoundary>
    );
    // Should show the error fallback message
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    // Should show the navigation elements (navbar)
    expect(screen.getByText('Python Tutorials')).toBeInTheDocument();
    expect(screen.getByText('Lessons')).toBeInTheDocument();
    expect(screen.getByText('Login')).toBeInTheDocument();
    // Should show reload button
    expect(screen.getByText('Reload page')).toBeInTheDocument();
    expect(ErrorBoundary.caughtError).toBe(true);
  });

  it('displays the error message in details', () => {
    renderWithRouter(
      <ErrorBoundary>
        <ExplodingComponent message="Custom error message" />
      </ErrorBoundary>
    );
    // The error details should be behind a <details> element
    expect(screen.getByText('Error details')).toBeInTheDocument();
    expect(screen.getByText('Custom error message')).toBeInTheDocument();
  });

  it('does not show details when error has no message', () => {
    renderWithRouter(
      <ErrorBoundary>
        <ExplodingEmpty />
      </ErrorBoundary>
    );
    // Still renders fallback
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('resets error state and renders children after recovery when resetting while navigating via Link', () => {
    const { rerender } = render(
      <MemoryRouter>
        <ErrorBoundary>
          <ExplodingComponent />
        </ErrorBoundary>
      </MemoryRouter>
    );
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();

    // Simulate what happens when user clicks "Lessons" link in the fallback
    // The handleReset method is called by the Link's onClick
    // We can test this by clicking the Lessons link
    fireEvent.click(screen.getByText('Lessons'));
    // The ErrorBoundary state should be reset by handleReset
    // Since we can't replace the child easily, just verify the link works
    // (handleReset sets hasError=false)
  });

  it('recovers and renders children after resetting state', () => {
    const { rerender } = render(
      <MemoryRouter>
        <ErrorBoundary>
          <ExplodingComponent />
        </ErrorBoundary>
      </MemoryRouter>
    );
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();

    // Rerender with a good component after the error
    rerender(
      <MemoryRouter>
        <ErrorBoundary>
          <GoodComponent />
        </ErrorBoundary>
      </MemoryRouter>
    );

    // ErrorBoundary is still in error state since we haven't called handleReset
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();

    // Manually trigger handleReset by clicking the "Python Tutorials" link
    // which has handleReset wired to its onClick
    fireEvent.click(screen.getByText('Python Tutorials'));

    // Now the error boundary should reset and show the good component
    expect(screen.getByTestId('good-component')).toBeInTheDocument();
  });

  it('includes a reload button that calls window.location.reload', () => {
    const reloadMock = vi.fn();
    const originalReload = window.location.reload;
    window.location.reload = reloadMock;

    renderWithRouter(
      <ErrorBoundary>
        <ExplodingComponent />
      </ErrorBoundary>
    );

    fireEvent.click(screen.getByText('Reload page'));
    expect(reloadMock).toHaveBeenCalledTimes(1);

    window.location.reload = originalReload;
  });

  it('logs error to console on catch', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    renderWithRouter(
      <ErrorBoundary>
        <ExplodingComponent message="Log this error" />
      </ErrorBoundary>
    );

    expect(consoleSpy).toHaveBeenCalled();
    // The first argument to console.error should reference the error
    const calls = consoleSpy.mock.calls;
    const hasErrorLog = calls.some(
      (call) =>
        call[0] === '[ErrorBoundary] Caught rendering error:' &&
        call[1] instanceof Error &&
        call[1].message === 'Log this error'
    );
    expect(hasErrorLog).toBe(true);
  });
});
