import { useCallback } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import { keymap } from '@codemirror/view';
import { EditorState } from '@codemirror/state';

const customDarkTheme = oneDark;

export default function CodeEditor({ value, onChange, placeholder, readOnly = false, onRun }) {
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
      />
    </div>
  );
}