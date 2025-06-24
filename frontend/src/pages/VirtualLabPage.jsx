import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import hljs from 'highlight.js/lib/core';
import javascript from 'highlight.js/lib/languages/javascript';
import python from 'highlight.js/lib/languages/python';
import java from 'highlight.js/lib/languages/java';
import 'highlight.js/styles/atom-one-dark.css';

// Register languages for syntax highlighting
hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('python', python);
hljs.registerLanguage('java', java);

const VirtualLabPage = () => {
  const { labId } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [lab, setLab] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentTask, setCurrentTask] = useState(0);
  const [activeFile, setActiveFile] = useState(null);
  const [completedTasks, setCompletedTasks] = useState([]);
  const [showInstructions, setShowInstructions] = useState(true);
  const [showHint, setShowHint] = useState(false);
  const [editorTheme, setEditorTheme] = useState('vs-dark');
  const [fontSize, setFontSize] = useState(14);
  const [isLabCompleted, setIsLabCompleted] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const editorRef = useRef(null);

  // Current date and time from the provided information
  const currentDate = new Date('2025-04-20 14:32:58');

  // Current username from the provided information
  const currentUsername = 'nanthiniSanthanam';

  useEffect(() => {
    const fetchLabData = async () => {
      try {
        setLoading(true);

        // In a real application, this would be an API call
        // const response = await api.get(`/api/labs/${labId}`);
        // setLab(response.data);

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Mock lab data
        const mockLab = {
          id: parseInt(labId || '1'),
          title: 'Building a React State Management System',
          description:
            "In this lab, you'll build a lightweight state management system for React applications similar to Redux but with a simpler API. You'll implement actions, reducers, and a store along with React hooks to connect components.",
          courseId: 1,
          courseName:
            'Advanced React and Redux: Building Scalable Web Applications',
          moduleId: 3,
          moduleName: 'Redux State Management',
          language: 'javascript',
          estimatedTime: 60, // minutes
          difficulty: 'Intermediate',
          prerequisites: [
            'Basic understanding of React hooks',
            'Familiarity with Redux concepts',
            'Experience with JavaScript ES6+',
          ],
          objectives: [
            'Implement a simplified state management store',
            'Create a provider component for context',
            'Build custom hooks for accessing state and dispatching actions',
            'Connect the state management system to React components',
          ],
          files: [
            {
              id: 1,
              name: 'store.js',
              content: `// MiniStore - A lightweight state management system
// TODO: Implement the createStore function that accepts a reducer
// and returns an object with getState, dispatch, and subscribe methods

export const createStore = (reducer, initialState = {}) => {
  // Your code here
};

// Example usage:
// const store = createStore(reducer, { count: 0 });
// store.dispatch({ type: 'INCREMENT' });
// console.log(store.getState()); // { count: 1 }`,
              readOnly: false,
              isMainFile: true,
            },
            {
              id: 2,
              name: 'provider.jsx',
              content: `import React, { createContext, useContext } from 'react';

// Create context for the store
export const StoreContext = createContext(null);

// TODO: Implement the StoreProvider component
export const StoreProvider = ({ store, children }) => {
  // Your code here
};

// TODO: Implement useStore hook to access the store
export const useStore = () => {
  // Your code here
};

// TODO: Implement useDispatch hook
export const useDispatch = () => {
  // Your code here
};

// TODO: Implement useSelector hook to select specific slice of state
export const useSelector = (selector) => {
  // Your code here
};`,
              readOnly: false,
              isMainFile: false,
            },
            {
              id: 3,
              name: 'test-app.jsx',
              content: `import React from 'react';
import { createStore } from './store';
import { StoreProvider, useSelector, useDispatch } from './provider';

// Simple counter reducer
const counterReducer = (state = { count: 0 }, action) => {
  switch (action.type) {
    case 'INCREMENT':
      return { ...state, count: state.count + 1 };
    case 'DECREMENT':
      return { ...state, count: state.count - 1 };
    default:
      return state;
  }
};

// Create a store with the counter reducer
const store = createStore(counterReducer, { count: 0 });

// Counter component using our custom hooks
function Counter() {
  const count = useSelector(state => state.count);
  const dispatch = useDispatch();
  
  return (
    <div>
      <h2>Counter: {count}</h2>
      <button onClick={() => dispatch({ type: 'INCREMENT' })}>
        Increment
      </button>
      <button onClick={() => dispatch({ type: 'DECREMENT' })}>
        Decrement
      </button>
    </div>
  );
}

// Main app component
export default function App() {
  return (
    <StoreProvider store={store}>
      <div className="app">
        <h1>MiniStore Demo</h1>
        <Counter />
      </div>
    </StoreProvider>
  );
}`,
              readOnly: true,
              isMainFile: false,
            },
          ],
          tasks: [
            {
              id: 1,
              title: 'Implement the createStore function',
              description:
                'Create a store factory function that returns an object with getState, dispatch, and subscribe methods.',
              hint: 'Remember that the store keeps track of the state, has a way to update it (dispatch), and notifies subscribers when the state changes.',
              testCriteria:
                'The createStore function should properly manage state and allow state modifications via dispatched actions.',
            },
            {
              id: 2,
              title: 'Implement the StoreProvider component',
              description:
                'Create a React context provider that makes the store accessible to all child components.',
              hint: 'Use React.createContext and context.Provider to share the store instance with the component tree.',
              testCriteria:
                'The StoreProvider should properly pass the store instance through context.',
            },
            {
              id: 3,
              title:
                'Implement the useStore, useDispatch, and useSelector hooks',
              description:
                'Create custom hooks that allow components to interact with the store.',
              hint: 'useStore should return the whole store, useDispatch should return the dispatch method, and useSelector should return a specific part of the state using a selector function.',
              testCriteria:
                'Components should be able to read from the store and dispatch actions to update the state.',
            },
          ],
        };

        // Set initial data
        setLab(mockLab);
        setActiveFile(
          mockLab.files.find(file => file.isMainFile) || mockLab.files[0]
        );
        setCode(
          mockLab.files.find(file => file.isMainFile)?.content ||
            mockLab.files[0].content
        );

        // Check if there are previously completed tasks (simulating getting from API)
        setCompletedTasks([]);
      } catch (err) {
        console.error('Error fetching lab data:', err);
        setError('Failed to load lab data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchLabData();
  }, [labId]);

  // Handle running the code
  const handleRunCode = async () => {
    setIsRunning(true);
    setOutput('');

    try {
      // In a real app, this would send code to a backend execution environment
      // const response = await api.post('/api/labs/run', { code, language: lab.language });
      // setOutput(response.data.output);

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      // For demonstration, simulate a code evaluation response
      let simulatedOutput = '';

      // Simulate different test results based on code content
      if (lab.language === 'javascript') {
        if (
          code.includes('getState') &&
          code.includes('dispatch') &&
          code.includes('subscribe')
        ) {
          simulatedOutput = `✅ Store implementation looks good!\n\n`;

          // Adding a simulated test result
          simulatedOutput += 'Running tests...\n\n';
          simulatedOutput += 'Test: Basic store functionality\n';
          simulatedOutput += '- Creating store: ✓\n';
          simulatedOutput += '- Initial state: ✓\n';
          simulatedOutput += '- State after dispatch: ✓\n';
          simulatedOutput += '- Subscribe notification: ✓\n\n';
          simulatedOutput += 'All tests passed!\n';
        } else {
          simulatedOutput =
            '⚠️ Your implementation is missing some required functionality.\n\n';

          if (!code.includes('getState')) {
            simulatedOutput += 'Error: Store should have a getState method\n';
          }
          if (!code.includes('dispatch')) {
            simulatedOutput += 'Error: Store should have a dispatch method\n';
          }
          if (!code.includes('subscribe')) {
            simulatedOutput += 'Error: Store should have a subscribe method\n';
          }
          simulatedOutput += '\nPlease review the requirements and try again.';
        }
      } else if (lab.language === 'python') {
        simulatedOutput = 'Python execution is not available in this demo.';
      } else {
        simulatedOutput =
          'Execution for this language is not available in the demo.';
      }

      setOutput(simulatedOutput);
    } catch (err) {
      console.error('Error running code:', err);
      setOutput('An error occurred while running your code. Please try again.');
    } finally {
      setIsRunning(false);
    }
  };

  // Handle switching to a different file
  const handleFileChange = file => {
    // Save current file content before switching
    if (activeFile) {
      const updatedFiles = lab.files.map(f =>
        f.id === activeFile.id ? { ...f, content: code } : f
      );
      setLab({ ...lab, files: updatedFiles });
    }

    // Switch to the new file
    setActiveFile(file);
    setCode(file.content);
  };

  // Handle task completion check
  const handleCheckTask = async () => {
    setIsSubmitting(true);

    try {
      // In a real app, this would send code to be checked against task criteria
      // const response = await api.post(`/api/labs/${labId}/tasks/${lab.tasks[currentTask].id}/check`, { code });

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Simulated task check results
      const taskPassed =
        currentTask === 0
          ? code.includes('getState') &&
            code.includes('dispatch') &&
            code.includes('subscribe')
          : currentTask === 1
            ? code.includes('StoreContext.Provider') &&
              code.includes('value={store}')
            : code.includes('useStore') &&
              code.includes('useDispatch') &&
              code.includes('useSelector');

      if (taskPassed) {
        // Update the completed tasks
        const newCompletedTasks = [...completedTasks];
        if (!newCompletedTasks.includes(currentTask)) {
          newCompletedTasks.push(currentTask);
        }
        setCompletedTasks(newCompletedTasks);

        // Show success feedback
        setFeedback({
          type: 'success',
          message: `Great job! You've completed the task: ${lab.tasks[currentTask].title}`,
        });

        // If all tasks are completed, mark the lab as completed
        if (newCompletedTasks.length === lab.tasks.length) {
          setIsLabCompleted(true);
        } else {
          // Move to the next task if not on the last one
          if (currentTask < lab.tasks.length - 1) {
            setTimeout(() => {
              setCurrentTask(currentTask + 1);
              setFeedback(null);
            }, 2000);
          }
        }
      } else {
        // Show failure feedback
        setFeedback({
          type: 'error',
          message: `Your solution doesn't meet all the criteria for this task. Please review the requirements and try again.`,
        });
      }
    } catch (err) {
      console.error('Error checking task:', err);
      setFeedback({
        type: 'error',
        message:
          'An error occurred while checking your solution. Please try again.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle lab submission
  const handleSubmitLab = async () => {
    setIsSubmitting(true);

    try {
      // In a real app, this would submit the completed lab
      // const response = await api.post(`/api/labs/${labId}/submit`, {
      //   files: lab.files.map(file => ({ id: file.id, content: file.id === activeFile.id ? code : file.content }))
      // });

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Set lab as completed
      setIsLabCompleted(true);

      // Show success feedback
      setFeedback({
        type: 'success',
        message: 'Congratulations! You have successfully completed this lab.',
      });

      // In a real app, you would redirect to a success page or back to the course
      setTimeout(() => {
        // navigate(`/courses/${lab.courseId}/completed-lab/${labId}`);
      }, 3000);
    } catch (err) {
      console.error('Error submitting lab:', err);
      setFeedback({
        type: 'error',
        message:
          'An error occurred while submitting your lab. Please try again.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="mt-12 flex justify-center">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
            </div>
            <p className="mt-4 text-lg text-gray-300">
              Loading virtual lab environment...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="mx-auto h-16 w-16 text-red-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <h2 className="mt-4 text-2xl font-bold">Error</h2>
            <p className="mt-2 text-lg text-gray-300">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-6 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-gray-900 bg-blue-500 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen overflow-hidden bg-gray-900 text-white flex flex-col">
      {/* Top header with lab title and controls */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center">
          <h1 className="text-lg font-medium truncate mr-4">{lab.title}</h1>
          <span className="text-xs px-2 py-1 rounded-full bg-blue-900 text-blue-200">
            {lab.language === 'javascript'
              ? 'JavaScript'
              : lab.language === 'python'
                ? 'Python'
                : lab.language}
          </span>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center">
            <span className="text-sm text-gray-300 mr-2">Theme:</span>
            <select
              value={editorTheme}
              onChange={e => setEditorTheme(e.target.value)}
              className="text-sm bg-gray-700 border border-gray-600 rounded px-2 py-1 text-gray-200"
            >
              <option value="vs-dark">Dark</option>
              <option value="vs-light">Light</option>
            </select>
          </div>
          <div className="flex items-center">
            <span className="text-sm text-gray-300 mr-2">Font Size:</span>
            <select
              value={fontSize}
              onChange={e => setFontSize(parseInt(e.target.value))}
              className="text-sm bg-gray-700 border border-gray-600 rounded px-2 py-1 text-gray-200"
            >
              {[12, 14, 16, 18, 20].map(size => (
                <option key={size} value={size}>
                  {size}px
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Main content area */}
      <div className="flex-grow flex overflow-hidden">
        {/* Left sidebar - Tasks and Instructions */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col overflow-hidden">
          {/* Task navigation */}
          <div className="px-4 py-3 border-b border-gray-700">
            <h2 className="font-medium text-lg">Tasks</h2>
            <div className="mt-2 space-y-2">
              {lab.tasks.map((task, index) => (
                <button
                  key={task.id}
                  onClick={() => setCurrentTask(index)}
                  className={`w-full text-left px-3 py-2 rounded flex items-center text-sm ${
                    currentTask === index
                      ? 'bg-blue-600 text-white'
                      : completedTasks.includes(index)
                        ? 'bg-green-800 text-white'
                        : 'bg-gray-700 text-gray-200 hover:bg-gray-600'
                  }`}
                >
                  <span className="mr-2">
                    {completedTasks.includes(index) ? (
                      <svg
                        className="h-5 w-5"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clipRule="evenodd"
                        />
                      </svg>
                    ) : (
                      <span className="flex items-center justify-center h-5 w-5 rounded-full border border-current">
                        {index + 1}
                      </span>
                    )}
                  </span>
                  <span className="truncate">{task.title}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Task instructions */}
          <div className="flex-grow overflow-y-auto p-4">
            {showInstructions ? (
              <div>
                <h3 className="font-medium text-lg">
                  {lab.tasks[currentTask].title}
                </h3>
                <p className="mt-2 text-gray-300 text-sm">
                  {lab.tasks[currentTask].description}
                </p>

                {showHint && (
                  <div className="mt-4 p-3 bg-gray-700 rounded-md text-sm">
                    <h4 className="font-medium text-yellow-400 mb-1">Hint:</h4>
                    <p className="text-gray-300">
                      {lab.tasks[currentTask].hint}
                    </p>
                  </div>
                )}

                <div className="mt-4">
                  <button
                    onClick={() => setShowHint(!showHint)}
                    className="text-sm text-blue-400 hover:text-blue-300"
                  >
                    {showHint ? 'Hide Hint' : 'Show Hint'}
                  </button>
                </div>

                <h4 className="font-medium mt-6 mb-2 text-gray-200">
                  Test Criteria:
                </h4>
                <p className="text-gray-300 text-sm">
                  {lab.tasks[currentTask].testCriteria}
                </p>

                <h4 className="font-medium mt-6 mb-2 text-gray-200">
                  Lab Objectives:
                </h4>
                <ul className="list-disc pl-5 space-y-1">
                  {lab.objectives.map((objective, index) => (
                    <li key={index} className="text-sm text-gray-300">
                      {objective}
                    </li>
                  ))}
                </ul>

                <div className="mt-6 pt-4 border-t border-gray-700">
                  <button
                    onClick={handleCheckTask}
                    disabled={isSubmitting}
                    className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 ${
                      isSubmitting ? 'opacity-70 cursor-not-allowed' : ''
                    }`}
                  >
                    {isSubmitting ? (
                      <>
                        <svg
                          className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                        >
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                          ></circle>
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          ></path>
                        </svg>
                        Checking...
                      </>
                    ) : (
                      'Check Task Completion'
                    )}
                  </button>

                  {completedTasks.length === lab.tasks.length && (
                    <button
                      onClick={handleSubmitLab}
                      disabled={isSubmitting || isLabCompleted}
                      className={`w-full mt-3 flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                        isSubmitting || isLabCompleted
                          ? 'opacity-70 cursor-not-allowed'
                          : ''
                      }`}
                    >
                      {isSubmitting
                        ? 'Submitting...'
                        : isLabCompleted
                          ? 'Lab Completed'
                          : 'Submit Lab'}
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-16">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p className="mt-2 text-sm text-gray-300">
                  Click "Show Instructions" to see task details
                </p>
              </div>
            )}
          </div>

          {/* Instructions toggle button */}
          <div className="p-3 border-t border-gray-700">
            <button
              onClick={() => setShowInstructions(!showInstructions)}
              className="w-full flex items-center justify-center px-4 py-2 border border-gray-600 rounded-md text-sm font-medium text-gray-300 hover:bg-gray-700"
            >
              {showInstructions ? (
                <>
                  <svg
                    className="h-4 w-4 mr-2"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                  Hide Instructions
                </>
              ) : (
                <>
                  <svg
                    className="h-4 w-4 mr-2"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  Show Instructions
                </>
              )}
            </button>
          </div>
        </div>

        {/* Main editor area */}
        <div className="flex-grow flex flex-col overflow-hidden">
          {/* File tabs */}
          <div className="bg-gray-800 border-b border-gray-700 px-1">
            <div className="flex overflow-x-auto">
              {lab.files.map(file => (
                <button
                  key={file.id}
                  onClick={() => handleFileChange(file)}
                  className={`px-4 py-2 text-sm font-medium whitespace-nowrap ${
                    activeFile?.id === file.id
                      ? 'text-white border-b-2 border-blue-500'
                      : 'text-gray-400 hover:text-gray-100'
                  }`}
                >
                  {file.name}
                  {file.readOnly && (
                    <span className="ml-1 text-xs text-gray-500">
                      (read-only)
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Code editor */}
          <div className="flex-grow relative">
            {/* Simple text area for demo - in a real app, use Monaco Editor or CodeMirror */}
            <textarea
              value={code}
              onChange={e => !activeFile?.readOnly && setCode(e.target.value)}
              className="w-full h-full bg-gray-900 text-white font-mono p-4 focus:outline-none resize-none"
              style={{ fontSize: `${fontSize}px` }}
              disabled={activeFile?.readOnly}
              placeholder="Write your code here..."
            />
          </div>

          {/* Bottom panel for output and controls */}
          <div className="bg-gray-800 border-t border-gray-700">
            {/* Controls */}
            <div className="flex justify-between items-center px-4 py-2 border-b border-gray-700">
              <div className="flex space-x-2">
                <button
                  onClick={handleRunCode}
                  disabled={isRunning}
                  className={`inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 ${
                    isRunning ? 'opacity-70 cursor-not-allowed' : ''
                  }`}
                >
                  {isRunning ? (
                    <>
                      <svg
                        className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      Running...
                    </>
                  ) : (
                    <>
                      <svg
                        className="h-4 w-4 mr-1"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      Run Code
                    </>
                  )}
                </button>

                <button
                  onClick={() => {
                    if (
                      activeFile &&
                      !activeFile.readOnly &&
                      confirm('Reset this file to its initial state?')
                    ) {
                      const originalFile = lab.files.find(
                        f => f.id === activeFile.id
                      );
                      if (originalFile) {
                        setCode(originalFile.content);
                      }
                    }
                  }}
                  className="inline-flex items-center px-3 py-1.5 border border-gray-600 text-sm font-medium rounded-md text-gray-300 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                >
                  <svg
                    className="h-4 w-4 mr-1"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                  Reset
                </button>
              </div>

              <div>
                {feedback && (
                  <div
                    className={`px-3 py-1.5 rounded-md text-sm ${
                      feedback.type === 'success'
                        ? 'bg-green-800 text-green-100'
                        : 'bg-red-800 text-red-100'
                    }`}
                  >
                    {feedback.message}
                  </div>
                )}
              </div>
            </div>

            {/* Output console */}
            <div className="h-40 overflow-y-auto p-4 font-mono text-sm bg-black">
              {output ? (
                <pre className="text-gray-300">{output}</pre>
              ) : (
                <p className="text-gray-500 italic">
                  Run your code to see output here...
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VirtualLabPage;
