import { describe, it, expect } from 'vitest';
import ProgressBar from '../components/ProgressBar.jsx';
import { render, screen } from '@testing-library/react';

describe('ProgressBar', () => {
  it('renders with correct percentage', () => {
    render(<ProgressBar completed={3} total={10} />);
    expect(screen.getByText('3 / 10 completed')).toBeInTheDocument();
    expect(screen.getByText('30%')).toBeInTheDocument();
  });

  it('handles zero total gracefully', () => {
    render(<ProgressBar completed={0} total={0} />);
    expect(screen.getByText('0%')).toBeInTheDocument();
  });
});