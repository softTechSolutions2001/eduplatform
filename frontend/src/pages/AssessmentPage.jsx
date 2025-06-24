import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const AssessmentPage = () => {
  const { assessmentId } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [results, setResults] = useState(null);
  const [showExplanation, setShowExplanation] = useState({});

  // Current date and time from the provided information
  const currentDateTime = new Date('2025-04-20 09:52:10');

  // Current username
  const currentUsername = 'nanthiniSanthanam';

  useEffect(() => {
    const fetchAssessment = async () => {
      try {
        setLoading(true);

        // In a real application, this would be an API call
        // const response = await api.get(`/api/assessments/${assessmentId}/`);
        // setAssessment(response.data);

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Mock assessment data
        const mockAssessment = {
          id: parseInt(assessmentId || '1'),
          title: 'Advanced React Concepts Assessment',
          description:
            'Test your knowledge of advanced React concepts including hooks, context, and performance optimization.',
          courseId: 1,
          courseName:
            'Advanced React and Redux: Building Scalable Web Applications',
          moduleId: 2,
          moduleName: 'Advanced React Concepts',
          timeLimit: 1800, // 30 minutes in seconds
          passingScore: 70,
          totalQuestions: 10,
          instructions: [
            'Read each question carefully and select the best answer.',
            'You have 30 minutes to complete the assessment.',
            'You can revisit questions before submitting your final answers.',
            'A score of 70% or higher is required to pass this assessment.',
          ],
          questions: [
            {
              id: 1,
              text: 'Which hook would you use to perform side effects in a function component?',
              type: 'single-choice',
              options: [
                { id: 'a', text: 'useState' },
                { id: 'b', text: 'useEffect' },
                { id: 'c', text: 'useContext' },
                { id: 'd', text: 'useReducer' },
              ],
              correctAnswer: 'b',
              explanation:
                'The useEffect hook allows you to perform side effects in function components. It serves the same purpose as componentDidMount, componentDidUpdate, and componentWillUnmount in React class components.',
            },
            {
              id: 2,
              text: 'What is the correct way to update state based on the previous state when using useState?',
              type: 'single-choice',
              options: [
                { id: 'a', text: 'setState(state + 1)' },
                { id: 'b', text: 'setState(state => state + 1)' },
                { id: 'c', text: 'setState(this.state + 1)' },
                {
                  id: 'd',
                  text: 'setState({ ...state, count: state.count + 1 })',
                },
              ],
              correctAnswer: 'b',
              explanation:
                'When updating state based on the previous state, you should use the functional form of setState, which receives the previous state as an argument and returns the new state.',
            },
            {
              id: 3,
              text: 'Which of the following hooks is NOT a built-in React hook?',
              type: 'single-choice',
              options: [
                { id: 'a', text: 'useLocalStorage' },
                { id: 'b', text: 'useRef' },
                { id: 'c', text: 'useCallback' },
                { id: 'd', text: 'useMemo' },
              ],
              correctAnswer: 'a',
              explanation:
                "useLocalStorage is not a built-in React hook. It's a custom hook that developers often create to handle local storage interactions. useRef, useCallback, and useMemo are all built-in React hooks.",
            },
            {
              id: 4,
              text: 'Which of these statements about React Context are true? (Select all that apply)',
              type: 'multiple-choice',
              options: [
                {
                  id: 'a',
                  text: 'Context provides a way to pass data through the component tree without having to pass props down manually at every level',
                },
                {
                  id: 'b',
                  text: 'Context should be used for low-frequency updates like theme changes or user authentication',
                },
                {
                  id: 'c',
                  text: 'Context is the best solution for all state management needs',
                },
                {
                  id: 'd',
                  text: 'Context can be consumed using the useContext hook',
                },
              ],
              correctAnswer: ['a', 'b', 'd'],
              explanation:
                "Context is designed for sharing data that can be considered 'global' for a tree of React components. It's ideal for low-frequency updates but not optimal for high-frequency updates where Redux or another state management library might be better. useContext is the modern way to consume context.",
            },
            {
              id: 5,
              text: 'What does the useMemo hook do?',
              type: 'single-choice',
              options: [
                {
                  id: 'a',
                  text: 'Memoizes a function to prevent unnecessary re-renders',
                },
                {
                  id: 'b',
                  text: 'Memoizes a value to prevent expensive recalculations',
                },
                { id: 'c', text: 'Creates a mutable ref object' },
                {
                  id: 'd',
                  text: 'Manages side effects in function components',
                },
              ],
              correctAnswer: 'b',
              explanation:
                'useMemo memoizes a computed value, only recomputing it when one of the dependencies has changed. This is useful for expensive calculations to prevent them from running on every render.',
            },
            {
              id: 6,
              text: 'When using the useEffect hook, what does the second parameter (dependency array) control?',
              type: 'single-choice',
              options: [
                {
                  id: 'a',
                  text: 'The variables that will be available inside the effect',
                },
                { id: 'b', text: 'When the effect will run' },
                {
                  id: 'c',
                  text: 'The cleanup function that runs before the component unmounts',
                },
                {
                  id: 'd',
                  text: 'The order in which multiple effects are executed',
                },
              ],
              correctAnswer: 'b',
              explanation:
                'The dependency array controls when the effect will run. If any value in the dependency array changes, the effect will run again. If you provide an empty array, the effect will only run once after the initial render.',
            },
            {
              id: 7,
              text: 'Which of the following methods can be used to optimize performance in React? (Select all that apply)',
              type: 'multiple-choice',
              options: [
                { id: 'a', text: 'Using React.memo for component memoization' },
                {
                  id: 'b',
                  text: 'Using useCallback to memoize callback functions',
                },
                { id: 'c', text: 'Using inline styles for all components' },
                {
                  id: 'd',
                  text: 'Implementing shouldComponentUpdate or React.PureComponent',
                },
              ],
              correctAnswer: ['a', 'b', 'd'],
              explanation:
                "React.memo, useCallback, and shouldComponentUpdate/PureComponent are all valid optimization techniques in React. Inline styles aren't generally an optimization technique and can sometimes lead to performance issues when overused.",
            },
            {
              id: 8,
              text: 'What is the correct way to initialize state with props in a function component?',
              type: 'single-choice',
              options: [
                {
                  id: 'a',
                  text: 'const [state, setState] = useState(this.props.initialValue)',
                },
                {
                  id: 'b',
                  text: 'const [state, setState] = useState(props.initialValue)',
                },
                {
                  id: 'c',
                  text: 'const state = { value: props.initialValue }',
                },
                {
                  id: 'd',
                  text: 'const state = new State(props.initialValue)',
                },
              ],
              correctAnswer: 'b',
              explanation:
                'In function components, you can directly access props as a parameter. The correct way to initialize state with props is to pass the prop value to the useState hook.',
            },
            {
              id: 9,
              text: "What is the purpose of React's Suspense component?",
              type: 'single-choice',
              options: [
                { id: 'a', text: 'To handle errors in components' },
                {
                  id: 'b',
                  text: 'To lazy load components and wait for them to load',
                },
                {
                  id: 'c',
                  text: 'To optimize performance by suspending unnecessary renders',
                },
                { id: 'd', text: 'To create animations and transitions' },
              ],
              correctAnswer: 'b',
              explanation:
                "React Suspense lets your components 'wait' for something before rendering. Currently, Suspense only supports one use case: loading components dynamically with React.lazy. In the future, it will support other use cases like data fetching.",
            },
            {
              id: 10,
              text: 'Which statements about React hooks rules are correct? (Select all that apply)',
              type: 'multiple-choice',
              options: [
                {
                  id: 'a',
                  text: 'Hooks can be called inside loops and conditions',
                },
                {
                  id: 'b',
                  text: 'Hooks can only be called at the top level of a component',
                },
                {
                  id: 'c',
                  text: 'Hooks can only be called from React function components',
                },
                { id: 'd', text: 'Hooks can be used inside class components' },
              ],
              correctAnswer: ['b', 'c'],
              explanation:
                'The Rules of Hooks state that hooks should only be called at the top level (not inside loops, conditions, or nested functions) and only from React function components or custom hooks. They cannot be used in class components.',
            },
          ],
        };

        setAssessment(mockAssessment);
        if (mockAssessment.timeLimit) {
          setTimeLeft(mockAssessment.timeLimit);
        }
      } catch (err) {
        console.error('Error fetching assessment:', err);
        setError('Failed to load the assessment. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchAssessment();
  }, [assessmentId]);

  // Timer effect
  useEffect(() => {
    if (!timeLeft || isCompleted) return;

    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          // Auto-submit when time runs out
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, isCompleted]);

  const handleAnswerChange = (questionId, selectedOption) => {
    if (isCompleted) return;

    const question = assessment.questions.find(q => q.id === questionId);

    if (question.type === 'single-choice') {
      setUserAnswers(prev => ({
        ...prev,
        [questionId]: selectedOption,
      }));
    } else if (question.type === 'multiple-choice') {
      setUserAnswers(prev => {
        const currentSelections = prev[questionId] || [];
        if (currentSelections.includes(selectedOption)) {
          // If already selected, remove it
          return {
            ...prev,
            [questionId]: currentSelections.filter(
              opt => opt !== selectedOption
            ),
          };
        } else {
          // If not selected, add it
          return {
            ...prev,
            [questionId]: [...currentSelections, selectedOption],
          };
        }
      });
    }
  };

  const handlePrevQuestion = () => {
    setCurrentQuestionIndex(prevIndex => Math.max(0, prevIndex - 1));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < assessment.questions.length - 1) {
      setCurrentQuestionIndex(prevIndex => prevIndex + 1);
    }
  };

  const handleJumpToQuestion = index => {
    setCurrentQuestionIndex(index);
  };

  const handleSubmit = async () => {
    if (isSubmitting) return;

    const confirmSubmit = window.confirm(
      'Are you sure you want to submit your assessment? You cannot change your answers after submission.'
    );
    if (!confirmSubmit) return;

    setIsSubmitting(true);

    try {
      // In a real application, this would be an API call
      // const response = await api.post(`/api/assessments/${assessmentId}/submit/`, { answers: userAnswers });
      // setResults(response.data);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Calculate results
      let correctAnswers = 0;
      const detailedResults = assessment.questions.map(question => {
        const userAnswer = userAnswers[question.id] || [];
        const isCorrect =
          question.type === 'single-choice'
            ? userAnswer === question.correctAnswer
            : JSON.stringify([...userAnswer].sort()) ===
              JSON.stringify([...question.correctAnswer].sort());

        if (isCorrect) correctAnswers++;

        return {
          questionId: question.id,
          userAnswer,
          correctAnswer: question.correctAnswer,
          isCorrect,
        };
      });

      const scorePercentage = Math.round(
        (correctAnswers / assessment.questions.length) * 100
      );
      const passed = scorePercentage >= assessment.passingScore;

      const mockResults = {
        assessmentId: assessment.id,
        userId: currentUsername,
        submittedAt: currentDateTime.toISOString(),
        timeSpent: assessment.timeLimit - timeLeft,
        score: scorePercentage,
        correctAnswers,
        totalQuestions: assessment.questions.length,
        passed,
        detailedResults,
      };

      setResults(mockResults);
      setIsCompleted(true);
    } catch (err) {
      console.error('Error submitting assessment:', err);
      alert('Failed to submit assessment. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatTime = seconds => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const calculateCompletionStatus = () => {
    const totalQuestions = assessment?.questions?.length || 0;
    const answeredQuestions = Object.keys(userAnswers).length;
    return {
      answered: answeredQuestions,
      total: totalQuestions,
      percentage:
        totalQuestions > 0
          ? Math.round((answeredQuestions / totalQuestions) * 100)
          : 0,
    };
  };

  const toggleExplanation = questionId => {
    setShowExplanation(prev => ({
      ...prev,
      [questionId]: !prev[questionId],
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="mt-12 flex justify-center">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-600"></div>
            </div>
            <p className="mt-4 text-lg text-gray-600">Loading assessment...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
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
            <h2 className="mt-4 text-2xl font-bold text-gray-900">Error</h2>
            <p className="mt-2 text-lg text-gray-600">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-6 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (isCompleted && results) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-4 py-5 sm:p-6">
              <h1 className="text-2xl font-bold text-gray-900 text-center">
                Assessment Results
              </h1>
              <h2 className="text-xl text-gray-700 mt-2 text-center">
                {assessment.title}
              </h2>

              <div className="mt-8 max-w-lg mx-auto">
                <div className="bg-gray-50 border rounded-lg p-6 text-center">
                  <div className="text-5xl font-bold mb-2">
                    {results.score}%
                  </div>
                  <div className="text-lg text-gray-500 mb-4">
                    {results.correctAnswers} of {results.totalQuestions}{' '}
                    questions correct
                  </div>

                  <div
                    className={`inline-flex items-center px-4 py-2 rounded-full text-base font-medium ${results.passed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}
                  >
                    {results.passed ? 'Assessment Passed' : 'Assessment Failed'}
                  </div>

                  <div className="mt-4 text-sm text-gray-500">
                    Submitted on{' '}
                    {new Date(results.submittedAt).toLocaleDateString()} at{' '}
                    {new Date(results.submittedAt).toLocaleTimeString()}
                  </div>
                </div>

                <div className="mt-8">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Question Review
                  </h3>

                  <div className="space-y-6">
                    {assessment.questions.map((question, index) => {
                      const questionResult = results.detailedResults.find(
                        r => r.questionId === question.id
                      );
                      const isCorrect = questionResult?.isCorrect;

                      return (
                        <div
                          key={question.id}
                          className={`border rounded-lg p-4 ${isCorrect ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}
                        >
                          <div className="flex items-start">
                            <span
                              className={`flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-full text-xs font-medium ${isCorrect ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'} mr-3 mt-0.5`}
                            >
                              {index + 1}
                            </span>
                            <div className="flex-1">
                              <p className="text-base font-medium text-gray-900">
                                {question.text}
                              </p>
                              <div className="mt-3 space-y-2">
                                {question.options.map(option => {
                                  const isSelectedByUser =
                                    question.type === 'single-choice'
                                      ? questionResult.userAnswer === option.id
                                      : (
                                          questionResult.userAnswer || []
                                        ).includes(option.id);

                                  const isCorrectOption =
                                    question.type === 'single-choice'
                                      ? question.correctAnswer === option.id
                                      : (question.correctAnswer || []).includes(
                                          option.id
                                        );

                                  let optionClasses =
                                    'pl-9 py-2 px-3 rounded-md flex items-start';

                                  if (isSelectedByUser && isCorrectOption) {
                                    optionClasses += ' bg-green-100';
                                  } else if (
                                    isSelectedByUser &&
                                    !isCorrectOption
                                  ) {
                                    optionClasses += ' bg-red-100';
                                  } else if (
                                    !isSelectedByUser &&
                                    isCorrectOption
                                  ) {
                                    optionClasses +=
                                      ' bg-green-100 border border-green-300';
                                  } else {
                                    optionClasses += ' bg-white';
                                  }

                                  return (
                                    <div
                                      key={option.id}
                                      className={optionClasses}
                                    >
                                      <div className="flex items-center h-5 absolute ml-[-28px]">
                                        {isSelectedByUser && (
                                          <svg
                                            className={`h-5 w-5 ${isCorrectOption ? 'text-green-500' : 'text-red-500'}`}
                                            xmlns="http://www.w3.org/2000/svg"
                                            viewBox="0 0 20 20"
                                            fill="currentColor"
                                          >
                                            {isCorrectOption ? (
                                              <path
                                                fillRule="evenodd"
                                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                                clipRule="evenodd"
                                              />
                                            ) : (
                                              <path
                                                fillRule="evenodd"
                                                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                                                clipRule="evenodd"
                                              />
                                            )}
                                          </svg>
                                        )}
                                        {!isSelectedByUser &&
                                          isCorrectOption && (
                                            <svg
                                              className="h-5 w-5 text-green-500"
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
                                          )}
                                      </div>
                                      <div className="text-sm text-gray-700">
                                        {option.text}
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>

                              <div className="mt-4">
                                <button
                                  type="button"
                                  onClick={() => toggleExplanation(question.id)}
                                  className="text-sm text-primary-600 hover:text-primary-800 font-medium focus:outline-none"
                                >
                                  {showExplanation[question.id]
                                    ? 'Hide Explanation'
                                    : 'Show Explanation'}
                                </button>

                                {showExplanation[question.id] && (
                                  <div className="mt-2 bg-gray-50 rounded-md p-3 text-sm text-gray-700">
                                    <p>
                                      <span className="font-medium">
                                        Explanation:
                                      </span>{' '}
                                      {question.explanation}
                                    </p>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="mt-8 flex justify-center space-x-4">
                  <button
                    onClick={() => navigate(`/courses/${assessment.courseId}`)}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Return to Course
                  </button>
                  <button
                    onClick={() => navigate('/dashboard/my-courses')}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Go to My Courses
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const currentQuestion = assessment?.questions?.[currentQuestionIndex];
  const completionStatus = calculateCompletionStatus();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Assessment Header */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-4 py-5 sm:px-6 flex justify-between items-center flex-wrap">
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {assessment.title}
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                {assessment.courseName} • {assessment.moduleName}
              </p>
            </div>

            <div className="flex items-center mt-2 sm:mt-0">
              {timeLeft !== null && (
                <div
                  className={`flex items-center mr-6 ${timeLeft < 300 ? 'text-red-600' : 'text-gray-700'}`}
                >
                  <svg
                    className="h-5 w-5 mr-1"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <span
                    className={`font-medium ${timeLeft < 300 ? 'text-red-600' : ''}`}
                  >
                    {formatTime(timeLeft)}
                  </span>
                </div>
              )}

              <div className="flex items-center">
                <svg
                  className="h-5 w-5 mr-1 text-gray-500"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
                <span className="text-sm text-gray-700">
                  {completionStatus.answered} of {completionStatus.total}{' '}
                  answered
                </span>
              </div>
            </div>
          </div>

          <div className="px-4 py-3 sm:px-6 bg-gray-50 border-t border-gray-200">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full"
                style={{ width: `${completionStatus.percentage}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Question Navigation */}
        <div className="bg-white shadow rounded-lg p-4 mb-6 overflow-x-auto">
          <div className="flex space-x-2">
            {assessment.questions.map((question, index) => {
              const answered = userAnswers[question.id] !== undefined;
              const current = currentQuestionIndex === index;

              return (
                <button
                  key={question.id}
                  onClick={() => handleJumpToQuestion(index)}
                  className={`w-10 h-10 flex items-center justify-center rounded-full text-sm font-medium 
                    ${current ? 'ring-2 ring-offset-2 ring-primary-600 ' : ''}
                    ${answered ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                >
                  {index + 1}
                </button>
              );
            })}
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-start">
              <span className="flex-shrink-0 bg-primary-100 text-primary-800 px-2.5 py-0.5 rounded-full text-sm font-medium mr-3">
                Question {currentQuestionIndex + 1} of{' '}
                {assessment.questions.length}
              </span>
              <span className="text-xs text-gray-500">
                {currentQuestion.type === 'single-choice'
                  ? 'Select one answer'
                  : 'Select all that apply'}
              </span>
            </div>

            <h2 className="text-lg font-medium text-gray-900 mt-4">
              {currentQuestion.text}
            </h2>

            <div className="mt-6 space-y-4">
              {currentQuestion.options.map(option => {
                const isSelected =
                  currentQuestion.type === 'single-choice'
                    ? userAnswers[currentQuestion.id] === option.id
                    : (userAnswers[currentQuestion.id] || []).includes(
                        option.id
                      );

                return (
                  <div key={option.id} className="relative flex">
                    <div className="flex items-center h-5">
                      {currentQuestion.type === 'single-choice' ? (
                        <input
                          id={`option-${option.id}`}
                          name={`question-${currentQuestion.id}`}
                          type="radio"
                          checked={isSelected}
                          onChange={() =>
                            handleAnswerChange(currentQuestion.id, option.id)
                          }
                          className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300"
                        />
                      ) : (
                        <input
                          id={`option-${option.id}`}
                          name={`question-${currentQuestion.id}`}
                          type="checkbox"
                          checked={isSelected}
                          onChange={() =>
                            handleAnswerChange(currentQuestion.id, option.id)
                          }
                          className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                        />
                      )}
                    </div>
                    <label
                      htmlFor={`option-${option.id}`}
                      className="ml-3 block text-sm font-medium text-gray-700 cursor-pointer"
                    >
                      {option.text}
                    </label>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between">
          <button
            onClick={handlePrevQuestion}
            disabled={currentQuestionIndex === 0}
            className={`inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 ${
              currentQuestionIndex === 0 ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <svg
              className="h-5 w-5 mr-2"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Previous
          </button>

          <div>
            {currentQuestionIndex < assessment.questions.length - 1 ? (
              <button
                onClick={handleNextQuestion}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Next
                <svg
                  className="h-5 w-5 ml-2"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className={`inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 ${
                  isSubmitting ? 'opacity-70 cursor-not-allowed' : ''
                }`}
              >
                {isSubmitting ? (
                  <>
                    <svg
                      className="animate-spin -ml-1 mr-2 h-5 w-5 text-white"
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
                    Submitting...
                  </>
                ) : (
                  <>Submit Assessment</>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssessmentPage;
