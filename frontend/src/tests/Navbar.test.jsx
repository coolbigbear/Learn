import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../hooks/useAuth.jsx';
import Navbar from '../components/Navbar.jsx';

function renderNavbar() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <Navbar />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('Navbar', () => {
  it('shows Login link when not authenticated', () => {
    renderNavbar();
    expect(screen.getByText('Login')).toBeInTheDocument();
    expect(screen.getByText('Lessons')).toBeInTheDocument();
  });

  it('renders hamburger menu button on mobile', () => {
    renderNavbar();
    const menuButton = screen.getByLabelText('Open menu');
    expect(menuButton).toBeInTheDocument();
  });

  it('shows mobile menu when hamburger is clicked', () => {
    renderNavbar();
    fireEvent.click(screen.getByLabelText('Open menu'));
    expect(screen.getByLabelText('Close menu')).toBeInTheDocument();
    // Mobile menu dropdown should show nav links
    const lessonLinks = screen.getAllByText('Lessons');
    expect(lessonLinks.length).toBeGreaterThanOrEqual(2); // one desktop, one mobile
  });

  it('closes mobile menu when a link is clicked', () => {
    renderNavbar();
    // Open menu
    fireEvent.click(screen.getByLabelText('Open menu'));
    expect(screen.getByLabelText('Close menu')).toBeInTheDocument();
    // Click the mobile Lessons link
    const mobileLessonLinks = screen.getAllByText('Lessons');
    fireEvent.click(mobileLessonLinks[mobileLessonLinks.length - 1]);
    // Menu should close — hamburger should be back
    expect(screen.getByLabelText('Open menu')).toBeInTheDocument();
  });

  it('toggles menu when hamburger is clicked twice', () => {
    renderNavbar();
    fireEvent.click(screen.getByLabelText('Open menu'));
    expect(screen.getByLabelText('Close menu')).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText('Close menu'));
    expect(screen.getByLabelText('Open menu')).toBeInTheDocument();
  });

  it('shows My Progress link in mobile menu when authenticated', () => {
    // Set a valid-ish token — AuthProvider detects it on mount
    const payload = btoa(JSON.stringify({ sub: '1', username: 'testuser', exp: 9999999999 }));
    const header = btoa(JSON.stringify({ alg: 'HS256' }));
    const token = `${header}.${payload.replace(/=/g, '').replace(/[+]/g, '-').replace(/[/]/g, '_')}.fakesig`;
    localStorage.setItem('auth_token', token);

    renderNavbar();
    fireEvent.click(screen.getByLabelText('Open menu'));
    const progressLinks = screen.getAllByText('My Progress');
    expect(progressLinks.length).toBeGreaterThanOrEqual(1);

    // Should show logout button in mobile menu
    const logoutButtons = screen.getAllByText('Logout');
    expect(logoutButtons.length).toBeGreaterThanOrEqual(1);

    // Username should be visible in the mobile menu after token restore
    // When mobile menu is open, username appears in both desktop and mobile nav
    const usernameSpans = screen.getAllByText('testuser');
    expect(usernameSpans.length).toBeGreaterThanOrEqual(2);

    localStorage.removeItem('auth_token');
  });

  it('shows username in desktop navbar when authenticated via stored token', () => {
    // Simulate a page reload with a valid stored JWT that includes username
    const payload = btoa(JSON.stringify({ sub: '1', username: 'johndoe', exp: 9999999999 }));
    const header = btoa(JSON.stringify({ alg: 'HS256' }));
    const token = `${header}.${payload.replace(/=/g, '').replace(/[+]/g, '-').replace(/[/]/g, '_')}.fakesig`;
    localStorage.setItem('auth_token', token);

    // Ensure API mock is set for the token-based auth path
    renderNavbar();

    // The username from the JWT payload should be rendered in the desktop navbar
    expect(screen.getByText('johndoe')).toBeInTheDocument();

    // Desktop should show Logout button (not Login link)
    expect(screen.getByText('Logout')).toBeInTheDocument();
    expect(screen.queryByText('Login')).not.toBeInTheDocument();

    localStorage.removeItem('auth_token');
  });

  it('does not show My Progress in mobile menu when not authenticated', () => {
    renderNavbar();
    fireEvent.click(screen.getByLabelText('Open menu'));
    expect(screen.queryByText('My Progress')).not.toBeInTheDocument();
    // There are two Login links when mobile menu is open (desktop + mobile)
    const loginLinks = screen.getAllByText('Login');
    expect(loginLinks.length).toBeGreaterThanOrEqual(1);
  });
});
