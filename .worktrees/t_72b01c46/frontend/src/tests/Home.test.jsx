import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Home from '../pages/Home.jsx';
import { AuthProvider } from '../hooks/useAuth.jsx';

describe('Home', () => {
  it('renders the landing page heading and CTA', () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <Home />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(screen.getByText('Learn Python')).toBeInTheDocument();
    expect(screen.getByText('Start Learning')).toBeInTheDocument();
  });
});