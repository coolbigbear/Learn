import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from '../hooks/useAuth.jsx';
import LessonView from '../pages/LessonView.jsx';

const mockLesson = {
  id: 'lesson-1',
  title: 'Python Basics',
  description: 'Learn the fundamentals of Python',
  content: '# Variables\n\nIn Python, you can assign variables like this:\n\n```python\nx = 10\nprint(x)\n```',
  exercises: [
    {
      id: 'ex-1',
      title: 'Hello World',
      instruction: 'Write a program that prints "Hello, World!"',
      starter_code: '# Print hello world\n',
    },
    {
      id: 'ex-2',
      title: 'Variables',
      instruction: 'Create a variable and print it',
      starter_code: '# Create a variable\n',
    },
  ],
};

// Fully mock the API module to include all exports used by useAuth and other modules
vi.mock('../api/client.js', () => ({
  getToken: vi.fn(() => null),
  setToken: vi.fn(),
  getLesson: vi.fn((slug) => {
    if (slug === 'python-basics') {
      return Promise.resolve(mockLesson);
    }
    return Promise.reject(new Error('Lesson not found'));
  }),
  runExercise: vi.fn(() => Promise.resolve({ actual_output: 'Hello, World!\n' })),
  submitExercise: vi.fn(() =>
    Promise.resolve({
      passed: true,
      test_results: [{ name: 'Test 1', passed: true }],
      summary: 'Good job!',
    })
  ),
  logout: vi.fn(() => Promise.resolve()),
  login: vi.fn(() => Promise.resolve({ token: 'test-token', id: 1, username: 'test' })),
  register: vi.fn(() => Promise.resolve({ token: 'test-token', id: 1, username: 'test' })),
  getLessons: vi.fn(() => Promise.resolve({ lessons: [] })),
  getProgress: vi.fn(() => Promise.resolve({})),
  getLessonProgress: vi.fn(() => Promise.resolve({})),
  health: vi.fn(() => Promise.resolve({ status: 'ok' })),
}));

function renderLessonView(slug = 'python-basics') {
  return render(
    <MemoryRouter initialEntries={['/lessons/' + slug]}>
      <AuthProvider>
        <Routes>
          <Route path="/lessons/:slug" element={<LessonView />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('LessonView', () => {
  it('shows loading state initially', () => {
    renderLessonView();
    expect(screen.getByText('Loading lesson...')).toBeInTheDocument();
  });

  it('renders lesson title in multiple places (mobile + desktop headings) after loading', async () => {
    renderLessonView();
    // The title appears twice: once in the mobile branch and once in the desktop branch
    const titles = await screen.findAllByText('Python Basics', {}, { timeout: 3000 });
    expect(titles.length).toBe(2);
    expect(titles[0]).toBeInTheDocument();
    expect(titles[1]).toBeInTheDocument();
  });

  it('renders description text after loading', async () => {
    renderLessonView();
    // Description also appears twice (mobile + desktop)
    const descs = await screen.findAllByText('Learn the fundamentals of Python', {}, { timeout: 3000 });
    expect(descs.length).toBe(2);
  });

  it('renders exercise tabs', async () => {
    renderLessonView();
    // Each exercise tab appears twice (once per desktop/mobile branch)
    const helloTabs = await screen.findAllByText('1. Hello World', {}, { timeout: 3000 });
    expect(helloTabs.length).toBe(2);
    const varTabs = await screen.findAllByText('2. Variables', {}, { timeout: 3000 });
    expect(varTabs.length).toBe(2);
  });

  it('shows back link to lessons', async () => {
    renderLessonView();
    // Appears twice: once in desktop breadcrumb, once in mobile breadcrumb
    const links = await screen.findAllByText('Back to Lessons', {}, { timeout: 3000 });
    expect(links.length).toBe(2);
  });

  it('shows "Lesson not found" for unknown slug', async () => {
    renderLessonView('unknown-lesson');
    expect(await screen.findByText('Lesson not found', {}, { timeout: 3000 })).toBeInTheDocument();
  });

  it('renders markdown content', async () => {
    renderLessonView();
    // Wait for the lesson to load (title will appear twice)
    await screen.findAllByText('Python Basics', {}, { timeout: 3000 });
    // Markdown content appears in both desktop and mobile branches
    const content = await screen.findAllByText(/In Python, you can assign variables/);
    expect(content.length).toBe(2);
  });

  it('highlights the first exercise as active', async () => {
    renderLessonView();
    // Both desktop and mobile tabs render; the first desktop tab is the one to check
    const helloTabs = await screen.findAllByText('1. Hello World', {}, { timeout: 3000 });
    // Both the desktop and mobile active exercise buttons should have bg-indigo-600
    helloTabs.forEach(tab => {
      expect(tab.closest('button').className).toContain('bg-indigo-600');
    });
  });

  it('shows "Exercises" heading', async () => {
    renderLessonView();
    // Appears twice: desktop and mobile
    const headings = await screen.findAllByText('Exercises', {}, { timeout: 3000 });
    expect(headings.length).toBe(2);
  });

  it('renders desktop split layout container with fixed positioning', async () => {
    renderLessonView();
    await screen.findAllByText('Python Basics', {}, { timeout: 3000 });
    // Desktop container uses md:fixed for full-height viewport split
    const desktopContainer = document.querySelector('.md\\:fixed');
    expect(desktopContainer).toBeInTheDocument();
  });
});