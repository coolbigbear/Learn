import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../hooks/useAuth.jsx';
import Navbar from '../components/Navbar.jsx';

describe('Navbar', () => {
  it('shows Login link when not authenticated', () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <Navbar />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(screen.getByText('Login')).toBeInTheDocument();
    expect(screen.getByText('Lessons')).toBeInTheDocument();
  });
});