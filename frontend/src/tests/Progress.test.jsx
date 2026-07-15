import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../hooks/useAuth.jsx';
import Progress from '../pages/Progress.jsx';

// Mock the API module
const mockGetProgress = vi.fn();
const mockGetLessonsByPath = vi.fn();

vi.mock('../api/client.js', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    getToken: vi.fn(() => 'test-token'),
    setToken: vi.fn(),
    isTokenExpired: vi.fn(() => false),
    decodeToken: vi.fn(() => ({ sub: '1' })),
    setOnUnauthorized: vi.fn(),
    clearToken: vi.fn(),
    getLessonsByPath: (...args) => mockGetLessonsByPath(...args),
    getLessons: vi.fn(() => Promise.resolve({ lessons: [] })),
    getLesson: vi.fn(() => Promise.resolve(null)),
    runExercise: vi.fn(() => Promise.resolve({})),
    submitExercise: vi.fn(() => Promise.resolve({ passed: true, test_results: [] })),
    logout: vi.fn(() => Promise.resolve()),
    login: vi.fn(() => Promise.resolve({ token: 'test-token', id: 1, username: 'test' })),
    register: vi.fn(() => Promise.resolve({ token: 'test-token', id: 1, username: 'test' })),
    getProgress: (...args) => mockGetProgress(...args),
    getLessonProgress: vi.fn(() => Promise.resolve({})),
    health: vi.fn(() => Promise.resolve({ status: 'ok' })),
  };
});

// Sample data matching the API response shapes
const coreLessons = [
  { id: 1, slug: '01-print-strings', title: 'Print Strings', order: 1, path: 'core', exercise_count: 2 },
  { id: 2, slug: '02-print-multiple', title: 'Print Multiple Items', order: 2, path: 'core', exercise_count: 1 },
  { id: 3, slug: '03-variables', title: 'Variables', order: 3, path: 'core', exercise_count: 3 },
];

const dataProcessingLessons = [
  { id: 16, slug: '16-data-processing', title: 'Data Processing — CSV, JSON, and APIs', order: 16, path: 'data-processing', exercise_count: 2 },
];

const pathsData = [
  { path: 'core', display_name: 'Python Fundamentals', description: 'Master Python basics.', color: 'indigo', lessons: coreLessons },
  { path: 'data-processing', display_name: 'Data Processing', description: 'Work with CSV, JSON, and APIs.', color: 'green', lessons: dataProcessingLessons },
  { path: 'api', display_name: 'API Development', description: 'Build web APIs with FastAPI.', color: 'blue', lessons: [] },
  { path: 'machine-learning', display_name: 'Machine Learning', description: 'Coming soon.', color: 'purple', lessons: [] },
];

const sampleProgressData = {
  summary: {
    total_exercises: 6,
    completed_exercises: 3,
  },
  lesson_totals: {
    '01-print-strings': 2,
    '02-print-multiple': 1,
    '03-variables': 3,
    '16-data-processing': 2,
  },
  progress: [
    {
      exercise_id: 1, lesson_slug: '01-print-strings', exercise_slug: 'ex1',
      exercise_title: 'Print Hello', completed: true, attempts: 3,
    },
    {
      exercise_id: 2, lesson_slug: '01-print-strings', exercise_slug: 'ex2',
      exercise_title: 'Print Your Name', completed: false, attempts: 1,
    },
    {
      exercise_id: 3, lesson_slug: '02-print-multiple', exercise_slug: 'ex3',
      exercise_title: 'Print Multiple Items', completed: true, attempts: 2,
    },
  ],
};

function renderProgress() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <Progress />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('Progress page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state initially', async () => {
    // Don't resolve promises so loading stays true
    mockGetProgress.mockReturnValue(new Promise(() => {}));
    mockGetLessonsByPath.mockReturnValue(new Promise(() => {}));
    renderProgress();
    expect(screen.getByText('Loading progress...')).toBeInTheDocument();
  });

  it('renders overall summary bar with progress data', async () => {
    mockGetProgress.mockResolvedValue(sampleProgressData);
    mockGetLessonsByPath.mockResolvedValue({ paths: pathsData });

    renderProgress();

    await waitFor(() => {
      expect(screen.getByText('Overall Progress')).toBeInTheDocument();
    });

    // Summary should show completed/total
    expect(screen.getByText('3 / 6 completed')).toBeInTheDocument();
  });

  it('renders path sections with display names', async () => {
    mockGetProgress.mockResolvedValue(sampleProgressData);
    mockGetLessonsByPath.mockResolvedValue({ paths: pathsData });

    renderProgress();

    await waitFor(() => {
      expect(screen.getByText('Python Fundamentals')).toBeInTheDocument();
    });

    expect(screen.getByText('Data Processing')).toBeInTheDocument();
    expect(screen.getByText('API Development')).toBeInTheDocument();
    expect(screen.getByText('Machine Learning')).toBeInTheDocument();
  });

  it('shows per-lesson status badges', async () => {
    mockGetProgress.mockResolvedValue(sampleProgressData);
    mockGetLessonsByPath.mockResolvedValue({ paths: pathsData });

    renderProgress();

    await waitFor(() => {
      expect(screen.getByText('Print Strings')).toBeInTheDocument();
    });

    // Print Strings has 1/2 completed — should be In Progress
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    // Print Multiple Items has 1/1 completed — should be Complete
    expect(screen.getByText('Complete')).toBeInTheDocument();
    // There are 2 lessons with "Not Started" status (Variables + Data Processing)
    const notStarted = screen.getAllByText('Not Started');
    expect(notStarted.length).toBe(2);
  });

  it('shows "All exercises passed" badge for completed lessons', async () => {
    mockGetProgress.mockResolvedValue(sampleProgressData);
    mockGetLessonsByPath.mockResolvedValue({ paths: pathsData });

    renderProgress();

    await waitFor(() => {
      expect(screen.getByText('Print Multiple Items')).toBeInTheDocument();
    });

    // Lesson 2 is complete (1/1)
    const allPassedBadges = screen.getAllByText('All exercises passed');
    expect(allPassedBadges.length).toBeGreaterThanOrEqual(1);
  });

  it('expands lesson to show exercises on click', async () => {
    mockGetProgress.mockResolvedValue(sampleProgressData);
    mockGetLessonsByPath.mockResolvedValue({ paths: pathsData });

    renderProgress();

    // Wait for the page to render
    await waitFor(() => {
      expect(screen.getByText('Print Strings')).toBeInTheDocument();
    });

    // Click the "Print Strings" lesson header button to expand
    // The button contains the text "Print Strings" and "Lesson 1"
    const lessonButtons = screen.getAllByRole('button');
    // Find the one that contains "Print Strings"
    const printStringsBtn = lessonButtons.find(btn => btn.textContent.includes('Print Strings'));
    expect(printStringsBtn).not.toBeUndefined();
    fireEvent.click(printStringsBtn);

    // Now exercises should be visible with their titles
    await waitFor(() => {
      expect(screen.getByText('Print Hello')).toBeInTheDocument();
    });
    expect(screen.getByText('Print Your Name')).toBeInTheDocument();
  });

  it('shows passed icon for completed exercises', async () => {
    mockGetProgress.mockResolvedValue(sampleProgressData);
    mockGetLessonsByPath.mockResolvedValue({ paths: pathsData });

    renderProgress();

    await waitFor(() => {
      expect(screen.getByText('Print Strings')).toBeInTheDocument();
    });

    // Expand the lesson
    const lessonButtons = screen.getAllByRole('button');
    const printStringsBtn = lessonButtons.find(btn => btn.textContent.includes('Print Strings'));
    fireEvent.click(printStringsBtn);

    await waitFor(() => {
      expect(screen.getByText('Print Hello')).toBeInTheDocument();
    });

    // "Print Hello" is completed — should show "Passed"
    const passedLabels = screen.getAllByText('Passed');
    expect(passedLabels.length).toBeGreaterThanOrEqual(1);

    // "Print Your Name" is attempted but not passed — should show "Attempted"
    const attemptedLabels = screen.getAllByText('Attempted');
    expect(attemptedLabels.length).toBeGreaterThanOrEqual(1);
  });

  it('shows attempt count for exercises with attempts', async () => {
    mockGetProgress.mockResolvedValue(sampleProgressData);
    mockGetLessonsByPath.mockResolvedValue({ paths: pathsData });

    renderProgress();

    await waitFor(() => {
      expect(screen.getByText('Print Strings')).toBeInTheDocument();
    });

    // Expand the lesson
    const lessonButtons = screen.getAllByRole('button');
    const printStringsBtn = lessonButtons.find(btn => btn.textContent.includes('Print Strings'));
    fireEvent.click(printStringsBtn);

    await waitFor(() => {
      expect(screen.getByText('Print Hello')).toBeInTheDocument();
    });

    // Print Hello has 3 attempts
    expect(screen.getByText('3 attempts')).toBeInTheDocument();
  });

  it('shows empty state when no progress and no paths', async () => {
    mockGetProgress.mockResolvedValue({ summary: null, lesson_totals: {}, progress: [] });
    mockGetLessonsByPath.mockResolvedValue({ paths: [] });

    renderProgress();

    await waitFor(() => {
      expect(screen.getByText('No progress yet. Start a lesson to begin tracking!')).toBeInTheDocument();
    });
  });

  it('shows congratulations banner when all exercises completed', async () => {
    const allCompleteData = {
      summary: {
        total_exercises: 6,
        completed_exercises: 6,
      },
      lesson_totals: {
        '01-print-strings': 2,
        '02-print-multiple': 1,
        '03-variables': 3,
      },
      progress: [
        { exercise_id: 1, lesson_slug: '01-print-strings', exercise_slug: 'ex1', exercise_title: 'Print Hello', completed: true, attempts: 1 },
        { exercise_id: 2, lesson_slug: '01-print-strings', exercise_slug: 'ex2', exercise_title: 'Print Your Name', completed: true, attempts: 1 },
        { exercise_id: 3, lesson_slug: '02-print-multiple', exercise_slug: 'ex3', exercise_title: 'Print Multiple', completed: true, attempts: 1 },
        { exercise_id: 4, lesson_slug: '03-variables', exercise_slug: 'ex4', exercise_title: 'Variables', completed: true, attempts: 1 },
        { exercise_id: 5, lesson_slug: '03-variables', exercise_slug: 'ex5', exercise_title: 'Data Types', completed: true, attempts: 1 },
        { exercise_id: 6, lesson_slug: '03-variables', exercise_slug: 'ex6', exercise_title: 'Type Conversion', completed: true, attempts: 1 },
      ],
    };

    // Only core lessons with all complete
    const corePaths = [{
      path: 'core',
      display_name: 'Python Fundamentals',
      description: 'Master Python basics.',
      color: 'indigo',
      lessons: coreLessons,
    }];

    mockGetProgress.mockResolvedValue(allCompleteData);
    mockGetLessonsByPath.mockResolvedValue({ paths: corePaths });

    renderProgress();

    await waitFor(() => {
      expect(screen.getByText(/Congratulations/)).toBeInTheDocument();
    });
  });

  it('shows error state when progress fails to load', async () => {
    mockGetProgress.mockRejectedValue(new Error('Failed to fetch'));
    mockGetLessonsByPath.mockResolvedValue({ paths: pathsData });

    renderProgress();

    await waitFor(() => {
      expect(screen.getByText(/Failed to load progress/)).toBeInTheDocument();
    });
  });

  it('shows "Not Yet" for exercises with no attempts', async () => {
    const progressWithNoAttempts = {
      summary: { total_exercises: 2, completed_exercises: 0 },
      lesson_totals: { '01-print-strings': 2 },
      progress: [
        { exercise_id: 1, lesson_slug: '01-print-strings', exercise_slug: 'ex1',
          exercise_title: 'Print Hello', completed: false, attempts: 0 },
        { exercise_id: 2, lesson_slug: '01-print-strings', exercise_slug: 'ex2',
          exercise_title: 'Print Your Name', completed: false, attempts: 0 },
      ],
    };

    const singlePath = [{
      path: 'core', display_name: 'Python Fundamentals', description: 'Master Python basics.',
      color: 'indigo', lessons: [coreLessons[0]],
    }];

    mockGetProgress.mockResolvedValue(progressWithNoAttempts);
    mockGetLessonsByPath.mockResolvedValue({ paths: singlePath });

    renderProgress();

    await waitFor(() => {
      expect(screen.getByText('Print Strings')).toBeInTheDocument();
    });

    // Expand the lesson
    const lessonButtons = screen.getAllByRole('button');
    const printStringsBtn = lessonButtons.find(btn => btn.textContent.includes('Print Strings'));
    fireEvent.click(printStringsBtn);

    await waitFor(() => {
      expect(screen.getByText('Print Hello')).toBeInTheDocument();
    });

    // Should show "Not Yet" for exercises with no attempts
    const notYetLabels = screen.getAllByText('Not Yet');
    expect(notYetLabels.length).toBeGreaterThanOrEqual(1);
  });

  it('shows path error notice when lessons-by-path fails', async () => {
    mockGetProgress.mockResolvedValue(sampleProgressData);
    mockGetLessonsByPath.mockRejectedValue(new Error('Failed to load paths'));

    renderProgress();

    await waitFor(() => {
      expect(screen.getByText(/Failed to load lesson paths/)).toBeInTheDocument();
    });
  });

  it('renders lesson numbers in lesson rows', async () => {
    mockGetProgress.mockResolvedValue(sampleProgressData);
    mockGetLessonsByPath.mockResolvedValue({ paths: pathsData });

    renderProgress();

    await waitFor(() => {
      expect(screen.getByText('Lesson 1')).toBeInTheDocument();
    });

    expect(screen.getByText('Lesson 2')).toBeInTheDocument();
    expect(screen.getByText('Lesson 3')).toBeInTheDocument();
  });

  it('shows "Coming Soon" for empty path sections', async () => {
    mockGetProgress.mockResolvedValue(sampleProgressData);
    mockGetLessonsByPath.mockResolvedValue({ paths: pathsData });

    renderProgress();

    await waitFor(() => {
      expect(screen.getByText('API Development')).toBeInTheDocument();
    });

    const comingSoonTexts = screen.getAllByText('Coming Soon');
    expect(comingSoonTexts.length).toBeGreaterThanOrEqual(1);
  });
});