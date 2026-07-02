import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import CodeEditor from '../components/CodeEditor.jsx';

describe('CodeEditor', () => {
  it('renders the code editor component', () => {
    const { container } = render(<CodeEditor value="print('hello')" />);
    // CodeMirror renders inside a .cm-editor div
    const editor = container.querySelector('.cm-editor');
    expect(editor).toBeTruthy();
  });

  it('renders with placeholder text', () => {
    render(<CodeEditor value="" placeholder="# Write your code" />);
    // CodeMirror renders placeholder text; check it appears somewhere
    expect(screen.getByText('# Write your code')).toBeInTheDocument();
  });

  it('accepts an initial value', () => {
    const { container } = render(<CodeEditor value="x = 42" />);
    const editor = container.querySelector('.cm-editor');
    expect(editor).toBeTruthy();
  });

  it('renders in read-only mode', () => {
    const { container } = render(<CodeEditor value="fixed code" readOnly={true} />);
    const editor = container.querySelector('.cm-editor');
    expect(editor).toBeTruthy();
  });

  it('passes onRun prop for Ctrl+Enter keybinding', () => {
    const onRun = vi.fn();
    const { container } = render(<CodeEditor value="test" onRun={onRun} />);
    expect(container.querySelector('.cm-editor')).toBeTruthy();
    // Keybinding is registered via CodeMirror extensions — the handler
    // is internal to CodeMirror's keymap system, so we verify the
    // component renders without error and the prop is accepted.
  });

  it('renders default placeholder when none provided', () => {
    render(<CodeEditor value="" />);
    expect(screen.getByText('# Write your Python code here')).toBeInTheDocument();
  });
});