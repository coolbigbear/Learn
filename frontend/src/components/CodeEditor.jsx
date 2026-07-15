import { useCallback, useEffect, useRef } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import { keymap } from '@codemirror/view';
import { EditorState } from '@codemirror/state';

const customDarkTheme = oneDark;

export default function CodeEditor({ value, onChange, placeholder, readOnly = false, onRun }) {
  const viewRef = useRef(null);
  // Track the focus listener so we can clean it up
  const focusHandlerRef = useRef(null);

  const extensions = [
    python(),
  ];

  // Add Ctrl/Cmd+Enter keybinding if onRun is provided
  if (onRun) {
    extensions.push(
      keymap.of([
        {
          key: 'Mod-Enter',
          run: () => {
            onRun();
            return true;
          },
        },
      ])
    );
  }

  // Store the CodeMirror editor view and set up the focus handler.
  // Select all text when the editor gains focus so the learner's first
  // keystroke replaces the content instead of appending to it.
  const handleCreateEditor = useCallback((view) => {
    viewRef.current = view;

    // Clean up any previously attached listener (safety net for hot-reload)
    if (focusHandlerRef.current) {
      focusHandlerRef.current();
    }

    const handleFocus = () => {
      // Defer to next microtask so CodeMirror finishes processing
      // the current event (focusin/focus) before we dispatch a
      // selection change — otherwise CodeMirror throws
      // "Calls to EditorView.update are not allowed while an
      // update is in progress".
      queueMicrotask(() => {
        view.dispatch({
          selection: { anchor: 0, head: view.state.doc.length },
        });
      });
    };

    view.dom.addEventListener('focusin', handleFocus);

    // Store the cleanup function
    focusHandlerRef.current = () => {
      view.dom.removeEventListener('focusin', handleFocus);
    };
  }, []);

  // Clean up the focus listener when the component unmounts
  useEffect(() => {
    return () => {
      if (focusHandlerRef.current) {
        focusHandlerRef.current();
      }
    };
  }, []);

  return (
    <div className="border border-gray-700 rounded-lg overflow-hidden">
      <CodeMirror
        value={value}
        onChange={(val) => onChange?.(val)}
        extensions={extensions}
        theme={customDarkTheme}
        height="auto"
        minHeight="180px"
        maxHeight="600px"
        basicSetup={{
          lineNumbers: true,
          foldGutter: true,
          highlightActiveLine: true,
          bracketMatching: true,
          closeBrackets: true,
          indentOnInput: true,
          tabSize: 4,
          indentUnit: 4,
        }}
        editable={!readOnly}
        placeholder={placeholder || '# Write your Python code here'}
        onCreateEditor={handleCreateEditor}
      />
    </div>
  );
}