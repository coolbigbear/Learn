import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../hooks/useAuth.jsx';
import Layout from '../components/Layout.jsx';

// Mock only getVersion, keep the rest of the API client intact
vi.mock('../api/client.js', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    getVersion: vi.fn(),
  };
});

import { getVersion } from '../api/client.js';

describe('Layout', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders navbar and footer', () => {
    getVersion.mockResolvedValue({ version: '0.1.0' });
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

  it('displays version when API returns successfully', async () => {
    getVersion.mockResolvedValue({ version: '0.1.0' });
    render(
      <MemoryRouter>
        <AuthProvider>
          <Layout />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('v0.1.0')).toBeInTheDocument();
    });
  });

  it('does not display version when API call fails', async () => {
    getVersion.mockRejectedValue(new Error('Network error'));
    render(
      <MemoryRouter>
        <AuthProvider>
          <Layout />
        </AuthProvider>
      </MemoryRouter>
    );

    // Wait a tick for the effect to run
    await waitFor(() => {
      expect(getVersion).toHaveBeenCalledTimes(1);
    });

    // The version should not appear in the document
    expect(screen.queryByText(/v0\.1\.0/)).not.toBeInTheDocument();
  });

  it('calls getVersion on mount', () => {
    getVersion.mockResolvedValue({ version: '0.1.0' });
    render(
      <MemoryRouter>
        <AuthProvider>
          <Layout />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(getVersion).toHaveBeenCalledTimes(1);
  });
});