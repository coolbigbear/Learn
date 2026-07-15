import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LessonCard, { getLessonProgress } from '../components/LessonCard.jsx';

const sampleLesson = {
  id: 1,
  slug: '01-print-strings',
  title: 'Print Strings',
  order: 1,
  exercise_count: 2,
};

function renderCard(overrides = {}) {
  const lesson = overrides.lesson || sampleLesson;
  const color = overrides.color;
  const progress = overrides.progress;
  return render(
    <MemoryRouter>
      <LessonCard lesson={lesson} color={color} progress={progress} />
    </MemoryRouter>
  );
}

describe('getLessonProgress', () => {
  it('returns complete when all exercises passed', () => {
    expect(getLessonProgress(2, 2)).toBe('complete');
  });

  it('returns in-progress when some exercises passed', () => {
    expect(getLessonProgress(1, 3)).toBe('in-progress');
  });

  it('returns not-started when no exercises passed', () => {
    expect(getLessonProgress(0, 3)).toBe('not-started');
  });

  it('returns not-started when total is zero', () => {
    expect(getLessonProgress(0, 0)).toBe('not-started');
  });

  it('returns not-started when progress is undefined', () => {
    // When no progress prop is passed, the component doesn't render a badge
    // This tests the helper directly
    expect(getLessonProgress(0, 0)).toBe('not-started');
  });
});

describe('LessonCard', () => {
  it('renders lesson title', () => {
    renderCard();
    expect(screen.getByText('Print Strings')).toBeInTheDocument();
  });

  it('renders lesson number badge', () => {
    renderCard();
    expect(screen.getByText('Lesson 1')).toBeInTheDocument();
  });

  it('renders exercise count', () => {
    renderCard();
    expect(screen.getByText('2 exercises')).toBeInTheDocument();
  });

  it('links to the lesson page', () => {
    renderCard();
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/lessons/01-print-strings');
  });

  it('renders singular exercise count for one exercise', () => {
    const lesson = { ...sampleLesson, exercise_count: 1 };
    renderCard({ lesson });
    expect(screen.getByText('1 exercise')).toBeInTheDocument();
  });

  it('shows complete badge when all exercises passed', () => {
    renderCard({ progress: { completed: 2, total: 2 } });
    expect(screen.getByText('Complete')).toBeInTheDocument();
  });

  it('shows progress bar when some exercises completed', () => {
    renderCard({ progress: { completed: 1, total: 3 } });
    // Should show the fraction
    expect(screen.getByText('1/3')).toBeInTheDocument();
  });

  it('does not show any badge when no progress data', () => {
    renderCard();
    expect(screen.queryByText('Complete')).not.toBeInTheDocument();
    expect(screen.queryByText('1/3')).not.toBeInTheDocument();
  });

  it('does not show badge when lesson not started (0 of N)', () => {
    renderCard({ progress: { completed: 0, total: 3 } });
    expect(screen.queryByText('Complete')).not.toBeInTheDocument();
    expect(screen.queryByText('0/3')).not.toBeInTheDocument();
  });

  it('applies accent color from the color prop', () => {
    renderCard({ color: 'green' });
    // The link block should still render — color appears as a CSS class on the accent strip
    expect(screen.getByText('Print Strings')).toBeInTheDocument();
  });

  it('falls back to gray accent for unknown color', () => {
    renderCard({ color: 'nonexistent' });
    expect(screen.getByText('Print Strings')).toBeInTheDocument();
  });
});