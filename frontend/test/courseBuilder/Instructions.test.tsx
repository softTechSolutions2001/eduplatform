import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Instructions from '../../src/courseBuilder/pages/Instructions';

describe('Instructions Component', () => {
  // Helper function to render component with router
  const renderWithRouter = (ui: React.ReactElement) => {
    return render(ui, { wrapper: BrowserRouter });
  };

  it('renders the instructions page title', () => {
    renderWithRouter(<Instructions />);
    expect(screen.getByText('Course Builder Guide')).toBeInTheDocument();
  });

  it('displays all main section headers', () => {
    renderWithRouter(<Instructions />);
    expect(screen.getByText('Getting Started')).toBeInTheDocument();
    expect(screen.getByText('Modules')).toBeInTheDocument();
    expect(screen.getByText('Lessons')).toBeInTheDocument();
    expect(screen.getByText('Resources')).toBeInTheDocument();
    expect(screen.getByText('Autosave & Publishing')).toBeInTheDocument();
    expect(screen.getByText('Accessibility Features')).toBeInTheDocument();
  });

  it('contains a link to start building a course', () => {
    renderWithRouter(<Instructions />);
    const link = screen.getByText('Start Building Your Course');
    expect(link).toBeInTheDocument();
    expect(link.closest('a')).toHaveAttribute('href', '/instructor/courses/builder');
  });
});
