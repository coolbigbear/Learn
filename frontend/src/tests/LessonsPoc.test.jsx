import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LessonsPoc from '../components/LessonsPoc.jsx';

const sampleLessons = {
  core: [
    { id: 1, slug: '01-print-strings', title: 'Print Strings', order: 1, exercise_count: 2 },
    { id: 2, slug: '02-print-multiple', title: 'Print Multiple Items', order: 2, exercise_count: 1 },
    { id: 15, slug: '15-modules', title: 'Modules and Packages', order: 15, exercise_count: 3 },
  ],
  'data-processing': [
    { id: 16, slug: '16-csv-processing', title: 'CSV Processing', order: 16, exercise_count: 2 },
    { id: 17, slug: '17-json-processing', title: 'JSON Processing', order: 17, exercise_count: 2 },
    { id: 18, slug: '18-data-processing-libraries', title: 'Data Processing Libraries', order: 18, exercise_count: 2 },
  ],
  api: [
    { id: 17, slug: '17-fastapi-intro', title: 'Introduction to FastAPI', order: 17, exercise_count: 2 },
    { id: 18, slug: '18-mini-api-project', title: 'Mini API Project', order: 18, exercise_count: 3 },
  ],
  'machine-learning': [],
};

const samplePaths = [
  { path: 'core', display_name: 'Python Fundamentals', description: 'Master Python basics.', color: 'indigo', lessons: sampleLessons.core },
  { path: 'data-processing', display_name: 'Data Processing', description: 'Work with CSV, JSON, and APIs.', color: 'green', lessons: sampleLessons['data-processing'] },
  { path: 'api', display_name: 'API Development', description: 'Build web APIs with FastAPI.', color: 'blue', lessons: sampleLessons.api },
  { path: 'machine-learning', display_name: 'Machine Learning', description: 'Coming soon.', color: 'purple', lessons: sampleLessons['machine-learning'] },
];

function renderPoc(props = {}) {
  const paths = 'paths' in props ? props.paths : samplePaths;
  return render(
    <MemoryRouter>
      <LessonsPoc paths={paths} getProgressForLesson={props.getProgressForLesson} />
    </MemoryRouter>
  );
}

describe('LessonsPoc - overview state (selectedPath === null)', () => {
  it('renders heading and subtitle', () => {
    renderPoc();
    expect(screen.getByText('Python Tutorials')).toBeInTheDocument();
    expect(screen.getByText('Follow the core path, then choose your specialization.')).toBeInTheDocument();
  });

  it('renders all path cards', () => {
    renderPoc();
    expect(screen.getByText('Python Fundamentals')).toBeInTheDocument();
    expect(screen.getByText('Data Processing')).toBeInTheDocument();
    expect(screen.getByText('API Development')).toBeInTheDocument();
    expect(screen.getByText('Machine Learning')).toBeInTheDocument();
  });

  it('renders path descriptions on cards', () => {
    renderPoc();
    expect(screen.getByText('Master Python basics.')).toBeInTheDocument();
    expect(screen.getByText('Work with CSV, JSON, and APIs.')).toBeInTheDocument();
    expect(screen.getByText('Build web APIs with FastAPI.')).toBeInTheDocument();
    expect(screen.getByText('Coming soon.')).toBeInTheDocument();
  });

  it('renders lesson counts on each card', () => {
    renderPoc();
    // core has 3, data-processing has 3, api has 2, ml has 0
    const threeLessonCards = screen.getAllByText('3 lessons');
    expect(threeLessonCards.length).toBe(2);
    expect(screen.getByText('2 lessons')).toBeInTheDocument();  // api
    expect(screen.getByText('0 lessons')).toBeInTheDocument();  // machine-learning
  });

  it('renders correct icons on each card', () => {
    renderPoc();
    // Core icon
    const coreIcon = screen.getByTestId('path-icon-core');
    expect(coreIcon.textContent).toBe('\uD83D\uDCD6');
    // Data icon
    const dataIcon = screen.getByTestId('path-icon-data-processing');
    expect(dataIcon.textContent).toBe('\uD83D\uDCCA');
    // API icon
    const apiIcon = screen.getByTestId('path-icon-api');
    expect(apiIcon.textContent).toBe('\u2699\uFE0F');
    // ML icon
    const mlIcon = screen.getByTestId('path-icon-machine-learning');
    expect(mlIcon.textContent).toBe('\uD83E\uDD16');
  });

  it('renders clickable path cards', () => {
    renderPoc();
    const coreCard = screen.getByTestId('path-card-core');
    expect(coreCard).toBeInTheDocument();
    expect(coreCard.tagName).toBe('BUTTON');
  });

  it('does not render lesson cards in overview state', () => {
    renderPoc();
    // Lesson titles come from LessonCard, should not be visible in overview
    expect(screen.queryByText('Print Strings')).not.toBeInTheDocument();
    expect(screen.queryByText('Introduction to FastAPI')).not.toBeInTheDocument();
  });

  it('does not render tabs in overview state', () => {
    renderPoc();
    expect(screen.queryByTestId('tab-bar')).not.toBeInTheDocument();
  });

  it('does not render back link in overview state', () => {
    renderPoc();
    expect(screen.queryByTestId('back-all-paths')).not.toBeInTheDocument();
  });
});

describe('LessonsPoc - path detail state', () => {
  it('shows lesson cards when a path card is clicked', () => {
    renderPoc();

    // Click the core path card
    fireEvent.click(screen.getByTestId('path-card-core'));

    // Lesson titles should now appear
    expect(screen.getByText('Print Strings')).toBeInTheDocument();
    expect(screen.getByText('Print Multiple Items')).toBeInTheDocument();
    expect(screen.getByText('Modules and Packages')).toBeInTheDocument();
  });

  it('shows the back-to-all-paths link in detail view', () => {
    renderPoc();
    fireEvent.click(screen.getByTestId('path-card-core'));

    expect(screen.getByTestId('back-all-paths')).toBeInTheDocument();
    expect(screen.getByText('All paths')).toBeInTheDocument();
  });

  it('shows tab bar with all paths in detail view', () => {
    renderPoc();
    fireEvent.click(screen.getByTestId('path-card-core'));

    expect(screen.getByTestId('tab-bar')).toBeInTheDocument();
    // All tabs should be present
    expect(screen.getByTestId('tab-core')).toBeInTheDocument();
    expect(screen.getByTestId('tab-data-processing')).toBeInTheDocument();
    expect(screen.getByTestId('tab-api')).toBeInTheDocument();
    expect(screen.getByTestId('tab-machine-learning')).toBeInTheDocument();
  });

  it('highlights the active tab with data-active attribute', () => {
    renderPoc();
    fireEvent.click(screen.getByTestId('path-card-core'));

    expect(screen.getByTestId('tab-core').getAttribute('data-active')).toBe('true');
    expect(screen.getByTestId('tab-data-processing').getAttribute('data-active')).toBe('false');
    expect(screen.getByTestId('tab-api').getAttribute('data-active')).toBe('false');
    expect(screen.getByTestId('tab-machine-learning').getAttribute('data-active')).toBe('false');
  });

  it('switches lessons when clicking a different tab', () => {
    renderPoc();
    fireEvent.click(screen.getByTestId('path-card-core'));

    // Core lessons visible
    expect(screen.getByText('Print Strings')).toBeInTheDocument();

    // Click Data Processing tab
    fireEvent.click(screen.getByTestId('tab-data-processing'));

    // Core lessons should no longer be visible
    expect(screen.queryByText('Print Strings')).not.toBeInTheDocument();
    // Data processing lessons should be visible
    expect(screen.getByText('CSV Processing')).toBeInTheDocument();

    // Active tab should switch
    expect(screen.getByTestId('tab-data-processing').getAttribute('data-active')).toBe('true');
    expect(screen.getByTestId('tab-core').getAttribute('data-active')).toBe('false');
  });

  it('returns to overview when back link is clicked', () => {
    renderPoc();
    fireEvent.click(screen.getByTestId('path-card-core'));

    // Now in detail view
    expect(screen.getByText('Print Strings')).toBeInTheDocument();

    // Click back
    fireEvent.click(screen.getByTestId('back-all-paths'));

    // Back to overview — lesson titles gone, path cards back
    expect(screen.queryByText('Print Strings')).not.toBeInTheDocument();
    expect(screen.getByTestId('path-card-core')).toBeInTheDocument();
  });

  it('shows active path header', () => {
    renderPoc();
    fireEvent.click(screen.getByTestId('path-card-api'));

    // Should show the API path header
    expect(screen.getByText('API Development')).toBeInTheDocument();
    expect(screen.getByText('Build web APIs with FastAPI.')).toBeInTheDocument();
  });

  it('handles tab click on path with no lessons — shows coming soon', () => {
    renderPoc();
    fireEvent.click(screen.getByTestId('path-card-core')); // go to detail view first

    fireEvent.click(screen.getByTestId('tab-machine-learning'));

    expect(screen.getByText('Machine Learning')).toBeInTheDocument();
    expect(screen.getByText('Coming Soon')).toBeInTheDocument();
    expect(screen.getByText('Machine Learning lessons are being prepared.')).toBeInTheDocument();
  });

  it('shows lesson grid with correct grid classes', () => {
    renderPoc();
    fireEvent.click(screen.getByTestId('path-card-core'));

    const grid = screen.getByTestId('lesson-grid');
    expect(grid).toBeInTheDocument();
  });

  it('renders correct number of lesson cards for a path', () => {
    renderPoc();
    fireEvent.click(screen.getByTestId('path-card-core'));

    // Core has 3 lessons
    const links = screen.getAllByRole('link');
    expect(links.length).toBe(3);
  });

  it('calls getProgressForLesson for each lesson', () => {
    const getProgressForLesson = vi.fn(() => null);
    renderPoc({ getProgressForLesson });

    fireEvent.click(screen.getByTestId('path-card-core'));

    // Should have been called 3 times (one per core lesson)
    expect(getProgressForLesson).toHaveBeenCalledTimes(3);
    expect(getProgressForLesson).toHaveBeenCalledWith(sampleLessons.core[0]);
    expect(getProgressForLesson).toHaveBeenCalledWith(sampleLessons.core[1]);
    expect(getProgressForLesson).toHaveBeenCalledWith(sampleLessons.core[2]);
  });
});

describe('LessonsPoc - edge cases', () => {
  it('renders empty state when paths is empty array', () => {
    renderPoc({ paths: [] });
    expect(screen.getByText('Python Tutorials')).toBeInTheDocument();
    expect(screen.getByText(/No lessons available yet/)).toBeInTheDocument();
  });

  it('renders empty state when paths is null/undefined', () => {
    renderPoc({ paths: undefined });
    expect(screen.getByText('Python Tutorials')).toBeInTheDocument();
    expect(screen.getByText(/No lessons available yet/)).toBeInTheDocument();
  });

  it('handles missing lessons array gracefully', () => {
    const pathsWithoutLessons = [
      { path: 'core', display_name: 'Python Fundamentals', description: 'Test.', color: 'indigo' },
    ];
    renderPoc({ paths: pathsWithoutLessons });

    // Should show the card
    expect(screen.getByText('Python Fundamentals')).toBeInTheDocument();
    expect(screen.getByText('0 lessons')).toBeInTheDocument();
  });

  it('handles clicking a path with no lessons array in detail view', () => {
    const pathNoLessons = [
      { path: 'core', display_name: 'Python Fundamentals', description: 'Test.', color: 'indigo' },
      { path: 'api', display_name: 'API Dev', description: 'Test api.', color: 'blue', lessons: [] },
    ];
    renderPoc({ paths: pathNoLessons });

    fireEvent.click(screen.getByTestId('path-card-core'));
    // Core has no lessons array, should show coming soon
    expect(screen.getByTestId('empty-path-placeholder')).toBeInTheDocument();
  });

  it('handles unknown path color gracefully', () => {
    const pathsWithUnknownColor = [
      { path: 'core', display_name: 'Python Fundamentals', description: 'Test.', color: 'nonexistent', lessons: sampleLessons.core },
    ];
    renderPoc({ paths: pathsWithUnknownColor });

    // Should render without error
    expect(screen.getByText('Python Fundamentals')).toBeInTheDocument();
  });

  it('shows singular "lesson" for exactly one lesson', () => {
    const singleLessonPath = [
      { path: 'core', display_name: 'Core', description: 'Test', color: 'indigo', lessons: [
        { id: 1, slug: '01-print-strings', title: 'Print Strings', order: 1, exercise_count: 2 },
      ] },
    ];
    renderPoc({ paths: singleLessonPath });
    expect(screen.getByText('1 lesson')).toBeInTheDocument();
  });

  it('shows singular "lesson" in empty path with placeholder text', () => {
    const singlePath = [
      { path: 'ml', display_name: 'ML Path', description: 'Test', color: 'purple', lessons: [] },
    ];
    renderPoc({ paths: singlePath });

    fireEvent.click(screen.getByTestId('path-card-ml'));
    expect(screen.getByText('Coming Soon')).toBeInTheDocument();
    expect(screen.getByText(/New lessons are being prepared/)).toBeInTheDocument();
  });

  it('renders tabs with icons for each path', () => {
    renderPoc();
    fireEvent.click(screen.getByTestId('path-card-core'));

    const tabBar = screen.getByTestId('tab-bar');
    expect(tabBar.textContent).toContain('\uD83D\uDCD6');
    expect(tabBar.textContent).toContain('\uD83D\uDCCA');
    expect(tabBar.textContent).toContain('\u2699\uFE0F');
    expect(tabBar.textContent).toContain('\uD83E\uDD16');
  });
});
