import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ModuleCard from '../../src/courseBuilder/components/ModuleCard';
import { useCourseStore } from '../../src/courseBuilder/store/courseSlice';

// Mock the Zustand store
vi.mock('../../src/courseBuilder/store/courseSlice', () => ({
  useCourseStore: vi.fn()
}));

// Mock the Sortable component
vi.mock('../../src/courseBuilder/dnd/Sortable', () => ({
  default: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="mock-sortable">{children}</div>
  )
}));

describe('ModuleCard Component', () => {
  const mockUpdateModule = vi.fn();
  const mockDeleteModule = vi.fn();
  const mockAddLesson = vi.fn();
  const mockReorderLessons = vi.fn();

  const mockModule = {
    id: 'module-1',
    title: 'Test Module',
    order: 1,
    lessons: [
      { id: 'lesson-1', title: 'Lesson 1', order: 1, content: '', accessLevel: 'basic', resources: [] }
    ]
  };

  beforeEach(() => {
    (useCourseStore as any).mockReturnValue({
      updateModule: mockUpdateModule,
      deleteModule: mockDeleteModule,
      addLesson: mockAddLesson,
      reorderLessons: mockReorderLessons
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders module title correctly', () => {
    render(<ModuleCard module={mockModule} />);
    expect(screen.getByDisplayValue('Test Module')).toBeInTheDocument();
  });

  it('calls updateModule when title is changed', () => {
    render(<ModuleCard module={mockModule} />);
    const titleInput = screen.getByDisplayValue('Test Module');
    
    fireEvent.change(titleInput, { target: { value: 'Updated Title' } });
    fireEvent.blur(titleInput);
    
    expect(mockUpdateModule).toHaveBeenCalledWith('module-1', { title: 'Updated Title' });
  });

  it('calls deleteModule when delete button is clicked and confirmed', () => {
    // Mock window.confirm to return true
    const originalConfirm = window.confirm;
    window.confirm = vi.fn(() => true);
    
    render(<ModuleCard module={mockModule} />);
    const deleteButton = screen.getByLabelText(/delete module/i);
    
    fireEvent.click(deleteButton);
    
    expect(window.confirm).toHaveBeenCalled();
    expect(mockDeleteModule).toHaveBeenCalledWith('module-1');
    
    // Restore original confirm
    window.confirm = originalConfirm;
  });

  it('calls addLesson when add lesson button is clicked', () => {
    render(<ModuleCard module={mockModule} />);
    const addLessonButton = screen.getByText(/add lesson/i);
    
    fireEvent.click(addLessonButton);
    
    expect(mockAddLesson).toHaveBeenCalledWith('module-1');
  });
});
