import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Alert,
  Badge,
  Button,
  Card,
  ProgressBar,
} from '../../components/common';
import { AssessmentErrorBoundary } from '../../components/common/errorBoundaries';
import { Header } from '../../components/layouts';
import { useAuth } from '../../contexts/AuthContext';
import { courseService } from '../../services/api';

/**
 * File: frontend/src/pages/courses/AssessmentPage.jsx
 * Date: 2025-07-24 18:20:45
 *
 * Assessment page for course lessons with improved access control for free content
 * FIXED: Issue with free assessments redirecting to login page
 */

const AssessmentPage = () => {
  const { courseSlug, lessonId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const [attempt, setAttempt] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [results, setResults] = useState(null);

  // Check authentication and redirect if needed
  useEffect(() => {
    const checkAccessAndAuth = async () => {
      try {
        console.log('Checking assessment access for lesson:', lessonId);
        // First check if this is a free lesson by fetching lesson details
        const lessonResponse = await courseService.getLessonDetails(
          lessonId,
          true
        ); // Use non-authenticated request

        // CRITICAL FIX: Treat undefined access_level as 'basic' (free content)
        const accessLevel = lessonResponse?.access_level || 'basic';
        console.log('Lesson access level determined:', accessLevel);

        // If lesson exists and it's not basic (free) content, then check authentication
        if (accessLevel !== 'basic') {
          if (!isAuthenticated) {
            console.log('Assessment requires login - redirecting');
            navigate('/login', {
              state: { from: `/courses/${courseSlug}/assessment/${lessonId}` },
            });
          }
        } else {
          console.log(
            'Free assessment content - allowing access without login'
          );
        }
      } catch (error) {
        console.error('Error checking lesson access level:', error);
        // On error, default to requiring authentication
        if (!isAuthenticated) {
          navigate('/login', {
            state: { from: `/courses/${courseSlug}/assessment/${lessonId}` },
          });
        }
      }
    };

    checkAccessAndAuth();
  }, [isAuthenticated, navigate, courseSlug, lessonId]);

  // Load assessment data
  useEffect(() => {
    const fetchAssessment = async () => {
      try {
        setLoading(true);

        // First, get the lesson details to find the assessment
        let lessonResponse;
        try {
          // Try to get lesson details, first assuming it might be free content
          lessonResponse = await courseService.getLessonDetails(lessonId, true);
          console.log(
            'Lesson access level:',
            lessonResponse.access_level || 'basic (default)'
          );
        } catch (error) {
          // If that fails, try authenticated request (will only work if user is logged in)
          console.log(
            'Free content fetch failed, trying authenticated request'
          );
          lessonResponse = await courseService.getLessonDetails(lessonId);
        }

        if (!lessonResponse?.has_assessment) {
          throw new Error('This lesson does not have an assessment.');
        }

        // Check if the assessment details are already included in the lesson response
        if (lessonResponse.assessment) {
          console.log(
            'Assessment found in lesson response:',
            lessonResponse.assessment
          );
          setAssessment(lessonResponse.assessment);

          if (lessonResponse.assessment.time_limit > 0) {
            setTimeRemaining(lessonResponse.assessment.time_limit * 60); // Convert minutes to seconds
          }
        } else {
          // If not, fetch the assessment separately
          console.log('Fetching assessment separately using assessment ID');
          const assessmentResponse = await courseService.getAssessmentDetails(
            lessonResponse.assessment_id
          );
          setAssessment(assessmentResponse);

          if (assessmentResponse.time_limit > 0) {
            setTimeRemaining(assessmentResponse.time_limit * 60); // Convert minutes to seconds
          }
        }

        setLoading(false);
      } catch (err) {
        console.error('Failed to load assessment:', err);
        setError(
          err.message || 'Failed to load assessment. Please try again later.'
        );
        setLoading(false);
      }
    };

    // CRITICAL FIX: Allow loading assessments for non-authenticated users
    fetchAssessment();
  }, [lessonId, isAuthenticated]);

  // Start the assessment
  const startAssessment = async () => {
    try {
      const response = await courseService.startAssessment(assessment.id);
      setAttempt(response);
      // Initialize answers object with empty arrays for multiple choice
      const initialAnswers = {};
      assessment.questions.forEach(question => {
        initialAnswers[question.id] =
          question.question_type === 'multiple_choice' ? [] : null;
      });
      setAnswers(initialAnswers);
    } catch (err) {
      console.error('Failed to start assessment:', err);
      setError('Failed to start the assessment. Please try again later.');
    }
  };

  // Handle question navigation
  const goToNextQuestion = () => {
    if (currentQuestionIndex < assessment.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const goToPreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  // Handle answer selection
  const handleAnswerChange = (questionId, answerId, isMultiple = false) => {
    if (isMultiple) {
      setAnswers(prev => {
        const currentAnswers = prev[questionId] || [];
        if (currentAnswers.includes(answerId)) {
          return {
            ...prev,
            [questionId]: currentAnswers.filter(id => id !== answerId),
          };
        } else {
          return {
            ...prev,
            [questionId]: [...currentAnswers, answerId],
          };
        }
      });
    } else {
      setAnswers(prev => ({
        ...prev,
        [questionId]: answerId,
      }));
    }
  };

  // Submit the assessment
  const handleSubmit = async () => {
    try {
      setHasSubmitted(true);
      const formattedAnswers = Object.entries(answers).map(
        ([questionId, answer]) => ({
          question_id: parseInt(questionId),
          answer_id: Array.isArray(answer)
            ? answer.map(id => parseInt(id))
            : parseInt(answer),
        })
      );

      const response = await courseService.submitAssessment(attempt.id, {
        answers: formattedAnswers,
      });

      setResults(response);

      // If passed, also mark the lesson as completed
      if (response.passed) {
        try {
          await courseService.completeLesson(lessonId);
        } catch (err) {
          console.error('Failed to mark lesson as complete:', err);
        }
      }
    } catch (err) {
      console.error('Failed to submit assessment:', err);
      setError('Failed to submit assessment. Please try again later.');
    }
  };

  // Format time remaining
  const formatTimeRemaining = seconds => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // Return to lesson
  const handleReturnToLesson = () => {
    navigate(
      `/courses/${courseSlug}/content/${assessment?.lesson?.module_id || '1'}/${lessonId}`
    );
  };

  // Timer countdown for timed assessments
  useEffect(() => {
    if (timeRemaining && timeRemaining > 0 && attempt && !hasSubmitted) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            handleSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [timeRemaining, attempt, hasSubmitted]);

  // Calculate completion percentage
  const calculateCompletion = () => {
    if (!assessment || !answers) return 0;

    const answeredQuestions = Object.values(answers).filter(
      answer =>
        answer !== null && (Array.isArray(answer) ? answer.length > 0 : true)
    ).length;

    return (answeredQuestions / assessment.questions.length) * 100;
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex flex-col min-h-screen">
        <Header />
        <div className="flex-grow flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-700 mx-auto mb-4"></div>
            <p className="text-primary-700 font-medium">
              Loading assessment...
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col min-h-screen">
        <Header />
        <div className="flex-grow flex items-center justify-center">
          <div className="text-center max-w-md mx-auto">
            <Alert type="error" title="Error Loading Assessment">
              {error}
            </Alert>
            <Button
              color="primary"
              className="mt-4"
              onClick={handleReturnToLesson}
            >
              Back to Lesson
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Assessment start screen
  if (assessment && !attempt && !results) {
    return (
      <div className="flex flex-col min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto py-12 px-4">
          <Card className="max-w-xl mx-auto p-8">
            <div className="text-center mb-6">
              <h1 className="text-2xl font-display font-bold text-gray-900 mb-2">
                {assessment.title}
              </h1>
              <p className="text-gray-600">{assessment.description}</p>
            </div>

            <div className="mb-8">
              <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg
                      className="h-5 w-5 text-blue-500"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800">
                      Assessment Information
                    </h3>
                    <div className="mt-2 text-sm text-blue-700 space-y-1">
                      <p>• {assessment.questions?.length || 0} questions</p>
                      {assessment.time_limit > 0 && (
                        <p>• Time limit: {assessment.time_limit} minutes</p>
                      )}
                      <p>• Passing score: {assessment.passing_score}%</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="text-center">
              <Button variant="primary" size="large" onClick={startAssessment}>
                Start Assessment
              </Button>

              <button
                className="block mt-4 text-gray-600 hover:text-gray-900 mx-auto"
                onClick={handleReturnToLesson}
              >
                Return to lesson
              </button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  // Assessment results screen
  if (results) {
    return (
      <div className="flex flex-col min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto py-12 px-4">
          <Card className="max-w-xl mx-auto p-8">
            <div className="text-center mb-8">
              <div className="mb-4">
                {results.passed ? (
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full">
                    <svg
                      className="w-8 h-8 text-green-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                ) : (
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full">
                    <svg
                      className="w-8 h-8 text-red-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </div>
                )}
              </div>

              <h1 className="text-2xl font-display font-bold text-gray-900 mb-2">
                {results.passed ? 'Assessment Passed!' : 'Assessment Failed'}
              </h1>
              <div className="text-gray-600 mb-4">
                Your score:{' '}
                <span className="font-medium">{results.score}%</span>
                <span className="text-sm text-gray-500 ml-1">
                  (Passing score: {assessment.passing_score}%)
                </span>
              </div>

              {results.passed ? (
                <div className="bg-green-50 text-green-700 p-4 rounded-md mb-6">
                  <p>
                    Congratulations! You've successfully completed this
                    assessment.
                  </p>
                </div>
              ) : (
                <div className="bg-amber-50 text-amber-700 p-4 rounded-md mb-6">
                  <p>
                    Don't worry! You can review the lesson material and try
                    again.
                  </p>
                </div>
              )}
            </div>

            <div className="space-y-6">
              <h2 className="text-lg font-semibold border-b pb-2">
                Results Review
              </h2>

              {assessment.questions.map((question, index) => {
                const userAnswer = results.answers.find(
                  a => a.question_id === question.id
                );
                const isCorrect = userAnswer?.is_correct ?? false;

                return (
                  <div
                    key={question.id}
                    className={`p-4 rounded-md ${
                      isCorrect
                        ? 'bg-green-50 border border-green-100'
                        : 'bg-red-50 border border-red-100'
                    }`}
                  >
                    <div className="flex items-start">
                      <div className="mr-3">
                        <span
                          className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-sm ${
                            isCorrect
                              ? 'bg-green-200 text-green-800'
                              : 'bg-red-200 text-red-800'
                          }`}
                        >
                          {index + 1}
                        </span>
                      </div>
                      <div className="flex-1">
                        <p className="font-medium mb-2">
                          {question.question_text}
                        </p>

                        <div className="ml-2 space-y-1 text-sm">
                          {question.answers.map(answer => (
                            <div
                              key={answer.id}
                              className={`flex items-center ${
                                answer.is_correct
                                  ? 'text-green-800 font-medium'
                                  : userAnswer?.answer_id === answer.id
                                    ? 'text-red-800'
                                    : ''
                              }`}
                            >
                              <svg
                                className="w-4 h-4 mr-1"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                              >
                                {answer.is_correct ? (
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M5 13l4 4L19 7"
                                  />
                                ) : userAnswer?.answer_id === answer.id ? (
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M6 18L18 6M6 6l12 12"
                                  />
                                ) : (
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M9 5l7 7-7 7"
                                  />
                                )}
                              </svg>
                              {answer.answer_text}
                              {answer.is_correct && (
                                <Badge
                                  size="small"
                                  variant="success"
                                  className="ml-2"
                                >
                                  Correct
                                </Badge>
                              )}
                            </div>
                          ))}
                        </div>

                        {userAnswer?.explanation && (
                          <div className="mt-3 text-sm bg-white p-3 rounded border">
                            <p className="font-medium text-gray-700">
                              Explanation:
                            </p>
                            <p className="text-gray-600">
                              {userAnswer.explanation}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="flex justify-between mt-8 pt-6 border-t">
              <Button
                variant="outline"
                size="medium"
                onClick={handleReturnToLesson}
              >
                Return to Lesson
              </Button>

              {!results.passed && (
                <Button
                  variant="primary"
                  size="medium"
                  onClick={() => {
                    setResults(null);
                    setAttempt(null);
                    setAnswers({});
                    setHasSubmitted(false);
                  }}
                >
                  Try Again
                </Button>
              )}
            </div>
          </Card>
        </div>
      </div>
    );
  }

  // Assessment in progress
  if (attempt && assessment?.questions) {
    const currentQuestion = assessment.questions[currentQuestionIndex];

    if (!currentQuestion) {
      return (
        <div className="flex flex-col min-h-screen">
          <Header />
          <div className="flex-grow flex items-center justify-center">
            <div className="text-center max-w-md mx-auto">
              <Alert type="error" title="Error">
                Question data is not available.
              </Alert>
              <Button
                color="primary"
                className="mt-4"
                onClick={handleReturnToLesson}
              >
                Back to Lesson
              </Button>
            </div>
          </div>
        </div>
      );
    }

    const isMultipleChoice =
      currentQuestion.question_type === 'multiple_choice';
    const userAnswer = answers[currentQuestion.id];
    const isAnswered = isMultipleChoice
      ? Array.isArray(userAnswer) && userAnswer.length > 0
      : userAnswer !== null && userAnswer !== undefined;
    const isLastQuestion =
      currentQuestionIndex === assessment.questions.length - 1;

    return (
      <div className="flex flex-col min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto py-8 px-4">
          <div className="max-w-3xl mx-auto">
            {/* Assessment header */}
            <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
              <div className="flex justify-between items-center">
                <h1 className="text-xl font-display font-bold text-gray-900">
                  {assessment.title}
                </h1>

                {/* Time remaining */}
                {timeRemaining > 0 && (
                  <div
                    className={`flex items-center ${
                      timeRemaining < 300 ? 'text-red-600' : 'text-gray-700'
                    }`}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-5 w-5 mr-1"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <span className="font-medium">
                      {formatTimeRemaining(timeRemaining)}
                    </span>
                  </div>
                )}
              </div>

              {/* Progress bar */}
              <div className="mt-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>
                    Question {currentQuestionIndex + 1} of{' '}
                    {assessment.questions.length}
                  </span>
                  <span>Completion: {Math.round(calculateCompletion())}%</span>
                </div>
                <ProgressBar
                  value={calculateCompletion()}
                  color="primary"
                  height="small"
                />
              </div>
            </div>

            {/* Question card */}
            <Card className="p-6 mb-6">
              <h2 className="text-lg font-semibold mb-4">
                {currentQuestion.question_text}
              </h2>

              {/* Question type indicator */}
              <div className="mb-6">
                <Badge
                  variant={isMultipleChoice ? 'warning' : 'info'}
                  className="text-xs"
                >
                  {isMultipleChoice
                    ? 'Select multiple answers'
                    : 'Select one answer'}
                </Badge>
              </div>

              {/* Answer options */}
              <div className="space-y-3">
                {currentQuestion.answers.map(answer => {
                  const isSelected = isMultipleChoice
                    ? Array.isArray(userAnswer) &&
                      userAnswer.includes(answer.id)
                    : userAnswer === answer.id;

                  return (
                    <button
                      key={answer.id}
                      onClick={() =>
                        handleAnswerChange(
                          currentQuestion.id,
                          answer.id,
                          isMultipleChoice
                        )
                      }
                      className={`w-full text-left p-3 rounded-md border transition-all ${
                        isSelected
                          ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-500 ring-opacity-50'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center">
                        <div
                          className={`flex-shrink-0 h-5 w-5 mr-2 rounded ${
                            isMultipleChoice ? 'border' : 'rounded-full border'
                          } ${
                            isSelected
                              ? 'border-primary-500 bg-primary-500'
                              : 'border-gray-300'
                          }`}
                        >
                          {isSelected && (
                            <svg
                              className="h-full w-full text-white"
                              viewBox="0 0 20 20"
                              fill="currentColor"
                            >
                              {isMultipleChoice ? (
                                <path
                                  fillRule="evenodd"
                                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                  clipRule="evenodd"
                                />
                              ) : (
                                <circle cx="10" cy="10" r="4" />
                              )}
                            </svg>
                          )}
                        </div>
                        <span>{answer.answer_text}</span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </Card>

            {/* Navigation buttons */}
            <div className="flex justify-between">
              <Button
                variant="outline"
                onClick={goToPreviousQuestion}
                disabled={currentQuestionIndex === 0}
              >
                Previous
              </Button>

              <div className="flex space-x-3">
                {isLastQuestion ? (
                  <Button
                    variant="primary"
                    disabled={!isAnswered || hasSubmitted}
                    onClick={handleSubmit}
                  >
                    Submit Assessment
                  </Button>
                ) : (
                  <Button
                    variant="primary"
                    disabled={!isAnswered}
                    onClick={goToNextQuestion}
                  >
                    Next Question
                  </Button>
                )}
              </div>
            </div>

            {/* Questions nav */}
            <div className="mt-8 bg-white rounded-lg shadow-sm p-4">
              <h3 className="text-sm font-medium text-gray-700 mb-3">
                Question Navigator
              </h3>
              <div className="flex flex-wrap gap-2">
                {assessment.questions.map((question, index) => {
                  const questionIsAnswered =
                    answers[question.id] !== null &&
                    (Array.isArray(answers[question.id])
                      ? answers[question.id].length > 0
                      : answers[question.id] !== undefined);

                  return (
                    <button
                      key={question.id}
                      onClick={() => setCurrentQuestionIndex(index)}
                      className={`flex items-center justify-center h-8 w-8 rounded-full text-sm font-medium ${
                        index === currentQuestionIndex
                          ? 'bg-primary-600 text-white'
                          : questionIsAnswered
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {index + 1}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Fallback state
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <div className="flex-grow flex items-center justify-center">
        <div className="text-center max-w-md mx-auto">
          <Alert type="error" title="Error">
            Something went wrong. Please try again.
          </Alert>
          <Button
            color="primary"
            className="mt-4"
            onClick={handleReturnToLesson}
          >
            Back to Lesson
          </Button>
        </div>
      </div>
    </div>
  );
};

export default function AssessmentPageWithErrorBoundary() {
  const navigate = useNavigate();

  const handleNavigateBack = () => {
    navigate(-1); // Go back to previous page
  };

  const handleError = (error, errorInfo, context) => {
    console.error('Assessment Error:', { error, errorInfo, context });
    // Could send to error tracking service here
  };

  return (
    <AssessmentErrorBoundary
      onNavigateBack={handleNavigateBack}
      onError={handleError}
    >
      <AssessmentPage />
    </AssessmentErrorBoundary>
  );
}
