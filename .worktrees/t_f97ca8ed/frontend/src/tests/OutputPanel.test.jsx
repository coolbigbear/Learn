import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import OutputPanel from '../components/OutputPanel.jsx';

describe('OutputPanel', () => {
  it('shows placeholder when no output or error', () => {
    render(<OutputPanel />);
    expect(screen.getByText(/Run your code to see output here/)).toBeInTheDocument();
  });

  it('shows placeholder when output is empty string', () => {
    render(<OutputPanel output="" error="" />);
    expect(screen.getByText(/Run your code to see output here/)).toBeInTheDocument();
  });

  it('displays standard output', () => {
    render(<OutputPanel output="Hello, World!" />);
    expect(screen.getByText('Hello, World!')).toBeInTheDocument();
    expect(screen.getByText('Output')).toBeInTheDocument();
  });

  it('displays error output', () => {
    render(<OutputPanel error="SyntaxError: invalid syntax" />);
    expect(screen.getByText('SyntaxError: invalid syntax')).toBeInTheDocument();
    expect(screen.getByText('Errors')).toBeInTheDocument();
  });

  it('shows loading state when loading=true', () => {
    render(<OutputPanel loading={true} />);
    expect(screen.getByText('Running code...')).toBeInTheDocument();
  });

  it('hides placeholder when loading', () => {
    render(<OutputPanel loading={true} />);
    expect(screen.queryByText(/run your code to see output/i)).not.toBeInTheDocument();
  });

  it('shows Clear button when onClear is provided', () => {
    const onClear = vi.fn();
    render(<OutputPanel output="some output" onClear={onClear} />);
    expect(screen.getByText('Clear')).toBeInTheDocument();
  });

  it('does not show Clear button when onClear is not provided', () => {
    render(<OutputPanel output="some output" />);
    expect(screen.queryByText('Clear')).not.toBeInTheDocument();
  });

  it('calls onClear when Clear button is clicked', async () => {
    const { userEvent } = await import('@testing-library/user-event');
    const onClear = vi.fn();
    render(<OutputPanel output="some output" onClear={onClear} />);
    const clearBtn = screen.getByText('Clear');
    await userEvent.click(clearBtn);
    expect(onClear).toHaveBeenCalledOnce();
  });

  it('applies green styling to output text', () => {
    const { container } = render(<OutputPanel output="Success" />);
    const span = container.querySelector('span.text-green-400');
    expect(span).toBeTruthy();
    expect(span.textContent).toBe('Success');
  });

  it('applies red styling to error text', () => {
    const { container } = render(<OutputPanel error="Error message" />);
    const span = container.querySelector('span.text-red-400');
    expect(span).toBeTruthy();
    expect(span.textContent).toBe('Error message');
  });
});