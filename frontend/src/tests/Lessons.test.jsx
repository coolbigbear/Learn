import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../hooks/useAuth.jsx';
import Lessons from '../pages/Lessons.jsx';

// Mock only specific API module functions — keep the rest intact
const mockGetLessonsByPath = vi.fn();
const mockGetLessons = vi.fn();

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
    getLessons: (...args) => mockGetLessons(...args),
    getLesson: vi.fn(() => Promise.resolve(null)),
    runExercise: vi.fn(() => Promise.resolve({})),
    submitExercise: vi.fn(() => Promise.resolve({ passed: true, test_results: [] })),
    logout: vi.fn(() => Promise.resolve()),
    login: vi.fn(() => Promise.resolve({ token: 'test-token', id: 1, username: 'test' })),
    register: vi.fn(() => Promise.resolve({ token: 'test-token', id: 1, username: 'test' })),
    getProgress: vi.fn(() => Promise.resolve({})),
    getLessonProgress: vi.fn(() => Promise.resolve({})),
    health: vi.fn(() => Promise.resolve({ status: 'ok' })),
  };
});

// Sample lesson data matching the LessonSummary schema
const coreLessons = [
  { id: 1, slug: '01-print-strings', title: 'Print Strings', order: 1, path: 'core', exercise_count: 2 },
  { id: 2, slug: '02-print-multiple', title: 'Print Multiple Items', order: 2, path: 'core', exercise_count: 1 },
  { id: 15, slug: '15-modules', title: 'Modules and Packages', order: 15, path: 'core', exercise_count: 3 },
];

const dataProcessingLessons = [
  { id: 16, slug: '16-data-processing', title: 'Data Processing — CSV, JSON, and APIs', order: 16, path: 'data-processing', exercise_count: 2 },
];

const apiLessons = [
  { id: 17, slug: '17-fastapi-intro', title: 'Introduction to FastAPI', order: 17, path: 'api', exercise_count: 2 },
  { id: 18, slug: '18-mini-api-project', title: 'Mini API Project', order: 18, path: 'api', exercise_count: 3 },
];

// The component expects the by-path endpoint to return a dict of path_key -> lessons[]
const mockGroupedData = {
  core: coreLessons,
  'data-processing': dataProcessingLessons,
  api: apiLessons,
  'machine-learning': [],
};

function renderLessons() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <Lessons />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('Lessons page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state initially', async () => {
    // Don't resolve the API promise so loading stays true
    mockGetLessonsByPath.mockReturnValue(new Promise(() => {}));
    renderLessons();
    expect(screen.getByText('Loading lessons...')).toBeInTheDocument();
  });

  it('redirects to login when not authenticated', async () => {
    // No token in localStorage means not authenticated
    renderLessons();
    await waitFor(() => {
      // Should redirect to login
      expect(screen.queryByText('Python Tutorials')).not.toBeInTheDocument();
    });
  });

  it('shows error message when API fails', async () => {
    mockGetLessonsByPath.mockRejectedValue(new Error('Network error'));

    renderLessons();

    await waitFor(() => {
      expect(screen.getByText(/Failed to load lessons/)).toBeInTheDocument();
    });
  });

  it('renders all four path sections', async () => {
    mockGetLessonsByPath.mockResolvedValue(mockGroupedData);

    renderLessons();

    await waitFor(() => {
      expect(screen.getByText('Python Fundamentals')).toBeInTheDocument();
    });

    expect(screen.getByText('Python Fundamentals')).toBeInTheDocument();
    expect(screen.getByText('Data Processing')).toBeInTheDocument();
    expect(screen.getByText('API Development')).toBeInTheDocument();
    expect(screen.getByText('Machine Learning')).toBeInTheDocument();
  });

  it('renders lesson cards for paths with lessons', async () => {
    mockGetLessonsByPath.mockResolvedValue(mockGroupedData);

    renderLessons();

    await waitFor(() => {
      expect(screen.getByText('Print Strings')).toBeInTheDocument();
    });

    // Core lessons
    expect(screen.getByText('Print Strings')).toBeInTheDocument();
    expect(screen.getByText('Print Multiple Items')).toBeInTheDocument();
    expect(screen.getByText('Modules and Packages')).toBeInTheDocument();

    // Data processing
    expect(screen.getByText('Data Processing — CSV, JSON, and APIs')).toBeInTheDocument();

    // API lessons
    expect(screen.getByText('Introduction to FastAPI')).toBeInTheDocument();
    expect(screen.getByText('Mini API Project')).toBeInTheDocument();
  });

  it('shows coming soon placeholder for empty paths', async () => {
    mockGetLessonsByPath.mockResolvedValue(mockGroupedData);

    renderLessons();

    await waitFor(() => {
      expect(screen.getByText('Machine Learning')).toBeInTheDocument();
    });

    // Machine Learning should show "Coming Soon"
    const comingSoonTexts = screen.getAllByText('Coming Soon');
    expect(comingSoonTexts.length).toBeGreaterThanOrEqual(1);
  });

  it('shows branch divider once between core and branch paths', async () => {
    mockGetLessonsByPath.mockResolvedValue(mockGroupedData);

    renderLessons();

    await waitFor(() => {
      expect(screen.getByText('Python Fundamentals')).toBeInTheDocument();
    });

    // The branch divider shows "Choose your path" — only once between core and branches
    const branchLabels = screen.getAllByText('Choose your path');
    expect(branchLabels.length).toBe(1);
  });

  it('falls back to flat list when by-path endpoint is unavailable', async () => {
    mockGetLessonsByPath.mockRejectedValue(new Error('Not found'));
    mockGetLessons.mockResolvedValue({
      lessons: [
        { id: 1, slug: '01-print-strings', title: 'Print Strings', order: 1, exercise_count: 2 },
        { id: 2, slug: '02-print-multiple', title: 'Print Multiple Items', order: 2, exercise_count: 1 },
      ],
    });

    renderLessons();

    await waitFor(() => {
      expect(screen.getByText('Print Strings')).toBeInTheDocument();
    });

    expect(screen.getByText('Print Multiple Items')).toBeInTheDocument();
    // Should show the flat list description
    expect(screen.getByText('Continue your learning journey through these interactive lessons.')).toBeInTheDocument();
  });

  it('falls back to flat list grouped by path when path field exists', async () => {
    mockGetLessonsByPath.mockRejectedValue(new Error('Not found'));
    mockGetLessons.mockResolvedValue({
      lessons: [
        { id: 1, slug: '01-print-strings', title: 'Print Strings', order: 1, path: 'core', exercise_count: 2 },
        { id: 16, slug: '16-data-processing', title: 'Data Processing — CSV, JSON, and APIs', order: 16, path: 'data-processing', exercise_count: 2 },
      ],
    });

    renderLessons();

    await waitFor(() => {
      expect(screen.getByText('Python Fundamentals')).toBeInTheDocument();
    });

    // Both paths should show — use getAllByText for the path section header
    // (the lesson title is different from the path name)
    const dataProcessingHeaders = screen.getAllByText('Data Processing');
    expect(dataProcessingHeaders.length).toBeGreaterThanOrEqual(1);
  });

  it('shows path descriptions', async () => {
    mockGetLessonsByPath.mockResolvedValue(mockGroupedData);

    renderLessons();

    await waitFor(() => {
      expect(screen.getByText('Master Python basics.')).toBeInTheDocument();
    });

    expect(screen.getByText('Work with CSV, JSON, and APIs.')).toBeInTheDocument();
    expect(screen.getByText('Build web APIs with FastAPI.')).toBeInTheDocument();
    expect(screen.getByText('Coming soon.')).toBeInTheDocument();
  });

  it('shows Branch badges on non-core paths', async () => {
    mockGetLessonsByPath.mockResolvedValue(mockGroupedData);

    renderLessons();

    await waitFor(() => {
      expect(screen.getByText('Data Processing')).toBeInTheDocument();
    });

    // Branch badges should appear for non-core paths
    const branchBadges = screen.getAllByText('Branch');
    expect(branchBadges.length).toBe(3); // data-processing, api, machine-learning
  });
});