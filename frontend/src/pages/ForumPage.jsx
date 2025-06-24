import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const ForumPage = () => {
  const { courseId, discussionId } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [courseForum, setCourseForum] = useState(null);
  const [discussions, setDiscussions] = useState([]);
  const [currentDiscussion, setCurrentDiscussion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('recent');
  const [newDiscussionTitle, setNewDiscussionTitle] = useState('');
  const [newDiscussionContent, setNewDiscussionContent] = useState('');
  const [showNewDiscussionForm, setShowNewDiscussionForm] = useState(false);
  const [replyContent, setReplyContent] = useState('');
  const [isPostingReply, setIsPostingReply] = useState(false);
  const [isCreatingDiscussion, setIsCreatingDiscussion] = useState(false);

  // Current date and time from the provided information
  const currentDate = new Date('2025-04-20 14:21:16');

  // Current username from the provided information
  const currentUsername = 'nanthiniSanthanam';

  useEffect(() => {
    const fetchForumData = async () => {
      try {
        setLoading(true);

        // In a real application, these would be API calls
        // const courseResponse = await api.get(`/api/courses/${courseId}`);
        // const forumResponse = discussionId
        //   ? await api.get(`/api/courses/${courseId}/discussions/${discussionId}`)
        //   : await api.get(`/api/courses/${courseId}/discussions`);

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Mock course forum data
        const mockCourseForum = {
          id: parseInt(courseId || '1'),
          title: 'Advanced React and Redux: Building Scalable Web Applications',
          instructor: 'Alex Johnson',
          categories: [
            { id: 'general', name: 'General', count: 8 },
            { id: 'lectures', name: 'Lectures', count: 12 },
            { id: 'assignments', name: 'Assignments', count: 6 },
            { id: 'projects', name: 'Projects', count: 5 },
            { id: 'technical', name: 'Technical Issues', count: 4 },
          ],
          totalDiscussions: 35,
          activeUsers: 28,
        };

        // Mock discussions data
        const mockDiscussions = [
          {
            id: 1,
            title: 'How to optimize Redux state updates?',
            author: {
              id: 101,
              name: 'Michael Rodriguez',
              avatar:
                'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
            },
            category: 'lectures',
            createdAt: '2025-04-15T10:30:00Z',
            updatedAt: '2025-04-19T15:45:00Z',
            views: 45,
            replies: 8,
            lastReplyBy: 'Sarah Chen',
            isPinned: true,
            isAnswered: true,
            content:
              "I'm working on a large application and noticing some performance issues when updating my Redux state. I've read about memoization and the useSelector hook, but I'm still seeing render issues. Any advice on best practices or patterns for optimizing Redux state updates in large applications?",
            tags: ['redux', 'performance', 'react-hooks'],
          },
          {
            id: 2,
            title: 'Understanding React Suspense and data fetching',
            author: {
              id: 102,
              name: 'Lisa Washington',
              avatar:
                'https://images.unsplash.com/photo-1534528741775-53994a69daeb?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
            },
            category: 'lectures',
            createdAt: '2025-04-18T08:20:00Z',
            updatedAt: '2025-04-20T09:15:00Z',
            views: 32,
            replies: 5,
            lastReplyBy: 'Alex Johnson',
            isPinned: false,
            isAnswered: true,
            content:
              "In Module 3, we briefly covered React Suspense for code splitting, but I'm curious about using it for data fetching as well. The documentation mentions experimental features for data fetching with Suspense. Has anyone experimented with this in a production environment? What libraries are you using with it?",
            tags: ['react-suspense', 'data-fetching', 'async'],
          },
          {
            id: 3,
            title: 'Issue with Assignment 2: Redux Middleware',
            author: {
              id: 103,
              name: 'nanthiniSanthanam',
              avatar:
                'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
            },
            category: 'assignments',
            createdAt: '2025-04-19T14:50:00Z',
            updatedAt: '2025-04-19T18:30:00Z',
            views: 18,
            replies: 3,
            lastReplyBy: 'David Kim',
            isPinned: false,
            isAnswered: false,
            content:
              "I'm having trouble with the second assignment where we need to implement a custom middleware for API calls. I've set up the middleware correctly (I think), but I'm getting an error: 'Error: Actions must be plain objects. Use custom middleware for async actions.' Can someone point me in the right direction? Here's my code:\n\n```javascript\nconst apiMiddleware = store => next => action => {\n  if (action.type !== 'API_REQUEST') {\n    return next(action);\n  }\n  \n  // Handle API request\n  const { url, method, data, onSuccess, onFailure } = action.payload;\n  \n  // Rest of the middleware...\n};\n```",
            tags: ['redux-middleware', 'assignment-help', 'api'],
          },
          {
            id: 4,
            title: 'Best practices for structuring large React applications',
            author: {
              id: 104,
              name: 'David Kim',
              avatar:
                'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
            },
            category: 'general',
            createdAt: '2025-04-10T11:25:00Z',
            updatedAt: '2025-04-17T09:10:00Z',
            views: 64,
            replies: 12,
            lastReplyBy: 'Michael Rodriguez',
            isPinned: true,
            isAnswered: true,
            content:
              "As our final project is approaching, I'm thinking about the best way to structure a large React application. Should we organize by features or by types (components, reducers, actions, etc.)? Are there any recommended patterns or examples of well-structured large React applications that you'd recommend studying?",
            tags: ['project-structure', 'architecture', 'best-practices'],
          },
          {
            id: 5,
            title: 'Testing Redux: Jest vs React Testing Library',
            author: {
              id: 105,
              name: 'Sarah Chen',
              avatar:
                'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
            },
            category: 'lectures',
            createdAt: '2025-04-12T16:40:00Z',
            updatedAt: '2025-04-18T13:20:00Z',
            views: 37,
            replies: 6,
            lastReplyBy: 'Lisa Washington',
            isPinned: false,
            isAnswered: true,
            content:
              "In Module 6, we covered testing React components with Jest and React Testing Library. I'm curious about best approaches for testing Redux specifically. Are there any recommended patterns or libraries for testing Redux actions, reducers, and connected components? How do you handle testing async actions?",
            tags: ['testing', 'jest', 'redux-testing'],
          },
          {
            id: 6,
            title: 'Error when deploying to Netlify',
            author: {
              id: 106,
              name: 'Robert Johnson',
              avatar:
                'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
            },
            category: 'technical',
            createdAt: '2025-04-17T19:15:00Z',
            updatedAt: '2025-04-18T10:05:00Z',
            views: 21,
            replies: 4,
            lastReplyBy: 'Alex Johnson',
            isPinned: false,
            isAnswered: true,
            content:
              "I'm trying to deploy my project to Netlify but keep getting build errors. The app works fine locally, but the build fails with: 'Failed to compile. Module not found: Error: Can't resolve './styles/main.css'. Has anyone else encountered this issue? How did you fix it?",
            tags: ['deployment', 'netlify', 'build-error'],
          },
          {
            id: 7,
            title: 'Final Project: Team Collaboration Tools',
            author: {
              id: 107,
              name: 'Emily Chen',
              avatar:
                'https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
            },
            category: 'projects',
            createdAt: '2025-04-16T08:30:00Z',
            updatedAt: '2025-04-19T11:45:00Z',
            views: 29,
            replies: 7,
            lastReplyBy: 'nanthiniSanthanam',
            isPinned: false,
            isAnswered: false,
            content:
              "For those working in teams for the final project, what collaboration tools are you using? We're using GitHub for version control, but I'm curious about project management tools, communication platforms, and any other tools that might help with team coordination.",
            tags: ['collaboration', 'project-management', 'teamwork'],
          },
          {
            id: 8,
            title: 'React 18 Features in Course Material',
            author: {
              id: 101,
              name: 'Michael Rodriguez',
              avatar:
                'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
            },
            category: 'general',
            createdAt: '2025-04-14T13:10:00Z',
            updatedAt: '2025-04-18T16:20:00Z',
            views: 42,
            replies: 9,
            lastReplyBy: 'Alex Johnson',
            isPinned: false,
            isAnswered: true,
            content:
              "I noticed that our course materials are using React 17, but React 18 has been out for a while now. I'm curious about the new features in React 18 like automatic batching, concurrent rendering, and the new suspense SSR architecture. Will we be covering any of these topics in the later modules?",
            tags: ['react-18', 'course-material', 'new-features'],
          },
        ];

        // Mock discussion detail data (replies)
        const mockDiscussionDetail = discussionId
          ? {
              id: parseInt(discussionId),
              ...mockDiscussions.find(d => d.id === parseInt(discussionId)),
              replies: [
                {
                  id: 101,
                  author: {
                    id: 102,
                    name: 'Lisa Washington',
                    avatar:
                      'https://images.unsplash.com/photo-1534528741775-53994a69daeb?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
                  },
                  content:
                    "I've been using the Redux Toolkit which has really simplified a lot of this. It includes utilities like createSlice that automatically generate action creators and handle immutable updates. Have you tried it?\n\nAlso, make sure you're not doing deep comparisons or complex operations in your selectors. The useSelector hook with reselect can help a lot with memoization.",
                  createdAt: '2025-04-15T14:45:00Z',
                  isInstructorResponse: false,
                  likes: 8,
                  isAcceptedAnswer: false,
                },
                {
                  id: 102,
                  author: {
                    id: 104,
                    name: 'David Kim',
                    avatar:
                      'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
                  },
                  content:
                    "Another thing to check is if you're normalizing your state. Having deeply nested state can cause performance issues because React has to do deep comparisons. The Redux docs recommend normalizing state, especially for collections of items: https://redux.js.org/recipes/structuring-reducers/normalizing-state-shape",
                  createdAt: '2025-04-16T09:20:00Z',
                  isInstructorResponse: false,
                  likes: 5,
                  isAcceptedAnswer: false,
                },
                {
                  id: 103,
                  author: {
                    id: 108,
                    name: 'Alex Johnson',
                    avatar:
                      'https://images.unsplash.com/photo-1531427186611-ecfd6d936c79?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
                  },
                  content:
                    "Great question, Michael. Let me add a few points to what Lisa and David mentioned:\n\n1. **Use memoized selectors**: The `reselect` library (included in Redux Toolkit) helps prevent unnecessary recalculations.\n\n2. **Batch your dispatches**: React 18's `flushSync` or libraries like `redux-batched-actions` can help.\n\n3. **Consider middleware carefully**: Some middleware can add overhead, especially during development.\n\n4. **State structure matters**: As David mentioned, normalize your state for collections.\n\n5. **Use Redux DevTools in development only**: The DevTools can slow things down in production.\n\nIn Module 5, we'll be covering advanced Redux optimization techniques, so we'll dive deeper into this topic soon.",
                  createdAt: '2025-04-16T11:35:00Z',
                  isInstructorResponse: true,
                  likes: 15,
                  isAcceptedAnswer: true,
                },
                {
                  id: 104,
                  author: {
                    id: 101,
                    name: 'Michael Rodriguez',
                    avatar:
                      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
                  },
                  content:
                    "Thank you all for the helpful responses! I've started implementing Redux Toolkit and normalizing my state structure, and I'm already seeing performance improvements. Looking forward to Module 5 to learn more optimization techniques.",
                  createdAt: '2025-04-17T08:15:00Z',
                  isInstructorResponse: false,
                  likes: 3,
                  isAcceptedAnswer: false,
                },
                {
                  id: 105,
                  author: {
                    id: 105,
                    name: 'Sarah Chen',
                    avatar:
                      'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
                  },
                  content:
                    "I ran into similar issues and found that using the `shallowEqual` function as the second argument to `useSelector` helped a lot:\n\n```jsx\nimport { shallowEqual, useSelector } from 'react-redux';\n\nconst MyComponent = () => {\n  const { prop1, prop2 } = useSelector(state => ({\n    prop1: state.something.prop1,\n    prop2: state.something.prop2\n  }), shallowEqual);\n  \n  // Rest of component\n};\n```\n\nThis prevents unnecessary re-renders when other parts of the state change.",
                  createdAt: '2025-04-19T15:45:00Z',
                  isInstructorResponse: false,
                  likes: 7,
                  isAcceptedAnswer: false,
                },
              ],
            }
          : null;

        setCourseForum(mockCourseForum);
        setDiscussions(mockDiscussions);

        if (mockDiscussionDetail) {
          setCurrentDiscussion(mockDiscussionDetail);
        }
      } catch (err) {
        console.error('Error fetching forum data:', err);
        setError('Failed to load forum data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchForumData();
  }, [courseId, discussionId]);

  const handleCategoryChange = category => {
    setActiveCategory(category);
  };

  const handleSearch = e => {
    e.preventDefault();
    // In a real app, you would filter discussions or make an API call
    console.log('Searching for:', searchQuery);
  };

  const handleCreateDiscussion = async e => {
    e.preventDefault();

    if (!newDiscussionTitle.trim() || !newDiscussionContent.trim()) {
      alert('Please enter both a title and content for your discussion');
      return;
    }

    setIsCreatingDiscussion(true);

    try {
      // In a real app, you would make an API call to create a new discussion
      // await api.post(`/api/courses/${courseId}/discussions`, { title: newDiscussionTitle, content: newDiscussionContent });

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Create a new mock discussion
      const newDiscussion = {
        id: discussions.length + 1,
        title: newDiscussionTitle,
        author: {
          id: 999,
          name: currentUsername,
          avatar:
            'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
        },
        category: 'general',
        createdAt: currentDate.toISOString(),
        updatedAt: currentDate.toISOString(),
        views: 1,
        replies: 0,
        lastReplyBy: null,
        isPinned: false,
        isAnswered: false,
        content: newDiscussionContent,
        tags: [],
      };

      // Add the new discussion to the list
      setDiscussions([newDiscussion, ...discussions]);

      // Reset form
      setNewDiscussionTitle('');
      setNewDiscussionContent('');
      setShowNewDiscussionForm(false);

      // Navigate to the new discussion
      navigate(`/courses/${courseId}/discussions/${newDiscussion.id}`);
    } catch (err) {
      console.error('Error creating discussion:', err);
      alert('Failed to create discussion. Please try again.');
    } finally {
      setIsCreatingDiscussion(false);
    }
  };

  const handleReply = async e => {
    e.preventDefault();

    if (!replyContent.trim()) {
      alert('Please enter your reply before posting');
      return;
    }

    setIsPostingReply(true);

    try {
      // In a real app, you would make an API call to post a reply
      // await api.post(`/api/courses/${courseId}/discussions/${discussionId}/replies`, { content: replyContent });

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Create a new mock reply
      const newReply = {
        id: currentDiscussion.replies.length + 1,
        author: {
          id: 999,
          name: currentUsername,
          avatar:
            'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80',
        },
        content: replyContent,
        createdAt: currentDate.toISOString(),
        isInstructorResponse: false,
        likes: 0,
        isAcceptedAnswer: false,
      };

      // Add the new reply to the discussion
      setCurrentDiscussion({
        ...currentDiscussion,
        replies: [...currentDiscussion.replies, newReply],
        updatedAt: currentDate.toISOString(),
      });

      // Reset form
      setReplyContent('');
    } catch (err) {
      console.error('Error posting reply:', err);
      alert('Failed to post reply. Please try again.');
    } finally {
      setIsPostingReply(false);
    }
  };

  const formatDate = dateString => {
    const date = new Date(dateString);
    const now = currentDate;
    const diff = Math.floor((now - date) / 1000); // difference in seconds

    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)} days ago`;

    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  // Filter and sort discussions based on selected criteria
  const filteredDiscussions = discussions
    .filter(discussion => {
      const matchesCategory =
        activeCategory === 'all' || discussion.category === activeCategory;
      const matchesSearch =
        !searchQuery ||
        discussion.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        discussion.content.toLowerCase().includes(searchQuery.toLowerCase());

      return matchesCategory && matchesSearch;
    })
    .sort((a, b) => {
      if (a.isPinned && !b.isPinned) return -1;
      if (!a.isPinned && b.isPinned) return 1;

      if (sortBy === 'recent') {
        return new Date(b.updatedAt) - new Date(a.updatedAt);
      } else if (sortBy === 'popular') {
        return b.views - a.views;
      } else if (sortBy === 'most-replies') {
        return b.replies - a.replies;
      }

      return 0;
    });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="mt-12 flex justify-center">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-600"></div>
            </div>
            <p className="mt-4 text-lg text-gray-600">Loading forum...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
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

  // Discussion detail view
  if (currentDiscussion) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6">
            <nav className="flex" aria-label="Breadcrumb">
              <ol className="flex items-center space-x-2">
                <li>
                  <Link
                    to={`/courses/${courseId}`}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    Course
                  </Link>
                </li>
                <li>
                  <svg
                    className="h-5 w-5 text-gray-400"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </li>
                <li>
                  <Link
                    to={`/courses/${courseId}/discussions`}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    Discussions
                  </Link>
                </li>
                <li>
                  <svg
                    className="h-5 w-5 text-gray-400"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </li>
                <li
                  className="text-gray-700 font-medium truncate"
                  style={{ maxWidth: '300px' }}
                >
                  {currentDiscussion.title}
                </li>
              </ol>
            </nav>
          </div>

          {/* Discussion Header */}
          <div className="bg-white shadow sm:rounded-lg mb-6">
            <div className="px-4 py-5 sm:px-6">
              <div className="flex items-center justify-between flex-wrap sm:flex-nowrap">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    {currentDiscussion.title}
                  </h1>
                  <p className="mt-1 text-sm text-gray-500">
                    Started by {currentDiscussion.author.name} •{' '}
                    {formatDate(currentDiscussion.createdAt)}
                  </p>
                </div>
                <div className="flex space-x-3">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {currentDiscussion.category}
                  </span>
                  {currentDiscussion.isPinned && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      Pinned
                    </span>
                  )}
                  {currentDiscussion.isAnswered && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Answered
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
              <div className="flex space-x-4">
                <div className="flex-shrink-0">
                  <img
                    className="h-10 w-10 rounded-full"
                    src={currentDiscussion.author.avatar}
                    alt={currentDiscussion.author.name}
                  />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-medium text-gray-900">
                    {currentDiscussion.author.name}
                  </div>
                  <div
                    className="mt-1 text-sm text-gray-700 prose max-w-none"
                    dangerouslySetInnerHTML={{
                      __html: currentDiscussion.content.replace(/\n/g, '<br>'),
                    }}
                  />

                  {currentDiscussion.tags &&
                    currentDiscussion.tags.length > 0 && (
                      <div className="mt-4 flex flex-wrap">
                        {currentDiscussion.tags.map(tag => (
                          <span
                            key={tag}
                            className="mr-2 mb-2 inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-gray-100 text-gray-800"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}

                  <div className="mt-2 flex items-center space-x-4">
                    <button className="text-gray-400 hover:text-gray-500 flex items-center text-sm">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-4 w-4 mr-1"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
                        />
                      </svg>
                      Like
                    </button>
                    <button className="text-gray-400 hover:text-gray-500 flex items-center text-sm">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-4 w-4 mr-1"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
                        />
                      </svg>
                      Share
                    </button>
                    <button className="text-gray-400 hover:text-gray-500 flex items-center text-sm">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-4 w-4 mr-1"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"
                        />
                      </svg>
                      Report
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Replies Section */}
          <div className="bg-white shadow sm:rounded-lg mb-6">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">
                Replies ({currentDiscussion.replies.length})
              </h2>
            </div>

            <div className="divide-y divide-gray-200">
              {currentDiscussion.replies.map(reply => (
                <div
                  key={reply.id}
                  className={`px-4 py-6 sm:px-6 ${reply.isAcceptedAnswer ? 'bg-green-50' : ''}`}
                >
                  <div className="flex space-x-4">
                    <div className="flex-shrink-0">
                      <img
                        className="h-10 w-10 rounded-full"
                        src={reply.author.avatar}
                        alt={reply.author.name}
                      />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between">
                        <div className="text-sm font-medium text-gray-900 flex items-center">
                          {reply.author.name}
                          {reply.isInstructorResponse && (
                            <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              Instructor
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-gray-500">
                          {formatDate(reply.createdAt)}
                        </div>
                      </div>
                      <div
                        className="mt-2 text-sm text-gray-700 prose max-w-none"
                        dangerouslySetInnerHTML={{
                          __html: reply.content.replace(/\n/g, '<br>'),
                        }}
                      />

                      <div className="mt-2 flex items-center space-x-4">
                        <button
                          className={`flex items-center text-sm ${reply.likes > 0 ? 'text-primary-600' : 'text-gray-400 hover:text-gray-500'}`}
                        >
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-4 w-4 mr-1"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="2"
                              d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
                            />
                          </svg>
                          {reply.likes > 0 ? `${reply.likes} likes` : 'Like'}
                        </button>
                        <button className="text-gray-400 hover:text-gray-500 flex items-center text-sm">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-4 w-4 mr-1"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="2"
                              d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"
                            />
                          </svg>
                          Report
                        </button>
                      </div>

                      {reply.isAcceptedAnswer && (
                        <div className="mt-2 flex items-center text-green-600">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5 mr-1"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="2"
                              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                          </svg>
                          <span className="text-sm font-medium">
                            Accepted Answer
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Reply Form */}
            <div className="px-4 py-6 sm:px-6 border-t border-gray-200">
              <div className="flex space-x-4">
                <div className="flex-shrink-0">
                  <img
                    className="h-10 w-10 rounded-full"
                    src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=100&h=100&q=80"
                    alt="Your avatar"
                  />
                </div>
                <div className="min-w-0 flex-1">
                  <form onSubmit={handleReply}>
                    <div>
                      <label htmlFor="reply" className="sr-only">
                        Reply to discussion
                      </label>
                      <textarea
                        id="reply"
                        name="reply"
                        rows={3}
                        className="shadow-sm block w-full focus:ring-primary-500 focus:border-primary-500 sm:text-sm border border-gray-300 rounded-md"
                        placeholder="Write your reply..."
                        value={replyContent}
                        onChange={e => setReplyContent(e.target.value)}
                      />
                    </div>
                    <div className="mt-3 flex items-center justify-end">
                      <button
                        type="submit"
                        disabled={isPostingReply}
                        className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 ${
                          isPostingReply ? 'opacity-70 cursor-not-allowed' : ''
                        }`}
                      >
                        {isPostingReply ? (
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
                            Posting...
                          </>
                        ) : (
                          'Post Reply'
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Discussions list view
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-primary-700 pt-8 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold leading-7 text-white sm:text-3xl sm:truncate">
                Course Discussions
              </h1>
              <p className="mt-2 text-lg text-primary-200">
                {courseForum.title}
              </p>
            </div>
            <div className="mt-4 flex md:mt-0">
              <button
                onClick={() => setShowNewDiscussionForm(!showNewDiscussionForm)}
                className="ml-3 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <svg
                  className="-ml-1 mr-2 h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
                    clipRule="evenodd"
                  />
                </svg>
                New Discussion
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8">
        {/* Forum Stats */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-primary-100 rounded-md p-3">
                  <svg
                    className="h-6 w-6 text-primary-600"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                    />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Discussions
                    </dt>
                    <dd>
                      <div className="text-lg font-medium text-gray-900">
                        {courseForum.totalDiscussions}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-primary-100 rounded-md p-3">
                  <svg
                    className="h-6 w-6 text-primary-600"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Active Users
                    </dt>
                    <dd>
                      <div className="text-lg font-medium text-gray-900">
                        {courseForum.activeUsers}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-primary-100 rounded-md p-3">
                  <svg
                    className="h-6 w-6 text-primary-600"
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
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Last Activity
                    </dt>
                    <dd>
                      <div className="text-lg font-medium text-gray-900">
                        {discussions.length > 0
                          ? formatDate(discussions[0].updatedAt)
                          : 'No activity'}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* New Discussion Form */}
        {showNewDiscussionForm && (
          <div className="bg-white shadow rounded-lg my-6">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Create New Discussion
              </h2>
              <form onSubmit={handleCreateDiscussion}>
                <div className="space-y-6">
                  <div>
                    <label
                      htmlFor="title"
                      className="block text-sm font-medium text-gray-700"
                    >
                      Title
                    </label>
                    <div className="mt-1">
                      <input
                        type="text"
                        name="title"
                        id="title"
                        className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                        placeholder="Enter discussion title"
                        value={newDiscussionTitle}
                        onChange={e => setNewDiscussionTitle(e.target.value)}
                      />
                    </div>
                  </div>

                  <div>
                    <label
                      htmlFor="content"
                      className="block text-sm font-medium text-gray-700"
                    >
                      Content
                    </label>
                    <div className="mt-1">
                      <textarea
                        id="content"
                        name="content"
                        rows={6}
                        className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border border-gray-300 rounded-md"
                        placeholder="Describe your question or topic..."
                        value={newDiscussionContent}
                        onChange={e => setNewDiscussionContent(e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <button
                      type="button"
                      className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 mr-3"
                      onClick={() => setShowNewDiscussionForm(false)}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={isCreatingDiscussion}
                      className={`inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 ${
                        isCreatingDiscussion
                          ? 'opacity-70 cursor-not-allowed'
                          : ''
                      }`}
                    >
                      {isCreatingDiscussion ? (
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
                          Creating...
                        </>
                      ) : (
                        'Create Discussion'
                      )}
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Filter and Search */}
        <div className="bg-white shadow rounded-lg my-6">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex overflow-x-auto pb-3 space-x-4 md:pb-0">
                  <button
                    onClick={() => handleCategoryChange('all')}
                    className={`whitespace-nowrap px-3 py-1.5 rounded-md text-sm font-medium ${activeCategory === 'all' ? 'bg-primary-100 text-primary-700' : 'text-gray-700 hover:bg-gray-100'}`}
                  >
                    All Topics
                  </button>

                  {courseForum.categories.map(category => (
                    <button
                      key={category.id}
                      onClick={() => handleCategoryChange(category.id)}
                      className={`whitespace-nowrap px-3 py-1.5 rounded-md text-sm font-medium ${activeCategory === category.id ? 'bg-primary-100 text-primary-700' : 'text-gray-700 hover:bg-gray-100'}`}
                    >
                      {category.name} ({category.count})
                    </button>
                  ))}
                </div>
              </div>

              <div className="mt-4 md:mt-0 flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
                <div className="flex-grow">
                  <form onSubmit={handleSearch}>
                    <div className="relative flex items-center">
                      <input
                        type="text"
                        name="search"
                        id="search"
                        className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full pr-10 sm:text-sm border-gray-300 rounded-md"
                        placeholder="Search discussions"
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                      />
                      <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                        <svg
                          className="h-5 w-5 text-gray-400"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                          aria-hidden="true"
                        >
                          <path
                            fillRule="evenodd"
                            d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </div>
                    </div>
                  </form>
                </div>

                <div className="flex-shrink-0">
                  <select
                    id="sort"
                    name="sort"
                    className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                    value={sortBy}
                    onChange={e => setSortBy(e.target.value)}
                  >
                    <option value="recent">Most Recent</option>
                    <option value="popular">Most Popular</option>
                    <option value="most-replies">Most Replies</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Discussions List */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-900">Discussions</h2>
            <span className="text-sm text-gray-500">
              {filteredDiscussions.length} results
            </span>
          </div>

          <div className="divide-y divide-gray-200">
            {filteredDiscussions.length === 0 ? (
              <div className="text-center py-12">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                  ></path>
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">
                  No discussions found
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  {activeCategory !== 'all'
                    ? `There are no discussions in the ${activeCategory} category.`
                    : 'No discussions match your search criteria.'}
                </p>
                {(activeCategory !== 'all' || searchQuery) && (
                  <div className="mt-6">
                    <button
                      onClick={() => {
                        setActiveCategory('all');
                        setSearchQuery('');
                      }}
                      className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      View All Discussions
                    </button>
                  </div>
                )}
              </div>
            ) : (
              filteredDiscussions.map(discussion => (
                <div
                  key={discussion.id}
                  className={`px-4 py-5 sm:px-6 hover:bg-gray-50 ${discussion.isPinned ? 'bg-yellow-50' : ''}`}
                >
                  <div className="flex items-center justify-between">
                    <Link
                      to={`/courses/${courseId}/discussions/${discussion.id}`}
                      className="flex-1 min-w-0"
                    >
                      <div className="flex items-start">
                        <div className="flex-shrink-0">
                          <img
                            className="h-10 w-10 rounded-full"
                            src={discussion.author.avatar}
                            alt={discussion.author.name}
                          />
                        </div>
                        <div className="ml-3 min-w-0 flex-1">
                          <p className="text-base font-medium text-gray-900 truncate">
                            {discussion.title}
                          </p>
                          <div className="flex items-center text-xs text-gray-500">
                            <span>{discussion.author.name}</span>
                            <span className="mx-1">•</span>
                            <span>{formatDate(discussion.createdAt)}</span>
                          </div>
                        </div>
                      </div>
                    </Link>
                    <div className="ml-4 flex flex-col items-end">
                      <div className="flex space-x-2 mb-1">
                        {discussion.isPinned && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            <svg
                              className="h-3 w-3 mr-1"
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 20 20"
                              fill="currentColor"
                            >
                              <path d="M9.293 1.55l.707.708.707-.707a1 1 0 011.414 0l3.586 3.586a1 1 0 010 1.414l-.707.707.707.707a1 1 0 01-1.414 1.414l-.707-.707-6.586 6.586a1 1 0 01-1.414 0l-2.586-2.586a1 1 0 010-1.414l6.586-6.586-.707-.707a1 1 0 010-1.414 1 1 0 011.414 0z" />
                            </svg>
                            Pinned
                          </span>
                        )}
                        {discussion.isAnswered && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <svg
                              className="h-3 w-3 mr-1"
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
                            Answered
                          </span>
                        )}
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {discussion.category}
                        </span>
                      </div>
                      <div className="flex text-sm text-gray-500">
                        <span className="mr-4 flex items-center">
                          <svg
                            className="h-4 w-4 mr-1 text-gray-400"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                          >
                            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                            <path
                              fillRule="evenodd"
                              d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                          {discussion.views}
                        </span>
                        <span className="flex items-center">
                          <svg
                            className="h-4 w-4 mr-1 text-gray-400"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                          >
                            <path
                              fillRule="evenodd"
                              d="M18 5v8a2 2 0 01-2 2h-5l-5 4v-4H4a2 2 0 01-2-2V5a2 2 0 012-2h12a2 2 0 012 2zM7 8H5v2h2V8zm2 0h2v2H9V8zm6 0h-2v2h2V8z"
                              clipRule="evenodd"
                            />
                          </svg>
                          {discussion.replies}
                          {discussion.lastReplyBy && (
                            <span className="ml-1 text-xs">
                              (last by {discussion.lastReplyBy})
                            </span>
                          )}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="px-4 py-4 sm:px-6 border-t border-gray-200 flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-700">
                Showing <span className="font-medium">1</span> to{' '}
                <span className="font-medium">
                  {filteredDiscussions.length}
                </span>{' '}
                of{' '}
                <span className="font-medium">
                  {filteredDiscussions.length}
                </span>{' '}
                discussions
              </p>
            </div>
            <div>
              <nav
                className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px"
                aria-label="Pagination"
              >
                <a
                  href="#"
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span className="sr-only">Previous</span>
                  <svg
                    className="h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </a>
                <a
                  href="#"
                  aria-current="page"
                  className="z-10 bg-primary-50 border-primary-500 text-primary-600 relative inline-flex items-center px-4 py-2 border text-sm font-medium"
                >
                  1
                </a>
                <a
                  href="#"
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span className="sr-only">Next</span>
                  <svg
                    className="h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </a>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForumPage;
