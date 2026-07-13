import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../hooks/useAuth.jsx';
import Layout from '../components/Layout.jsx';

describe('Layout', () => {
  it('renders navbar and footer', () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <Layout />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(screen.getByText('Python Tutorials')).toBeInTheDocument();
    expect(screen.getByText(/Interactive Python Tutorials/)).toBeInTheDocument();
  });
});