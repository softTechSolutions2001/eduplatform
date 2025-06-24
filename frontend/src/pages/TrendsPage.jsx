import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const TrendsPage = () => {
  const { currentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [trendingCourses, setTrendingCourses] = useState([]);
  const [trendingSkills, setTrendingSkills] = useState([]);
  const [industryInsights, setIndustryInsights] = useState([]);
  const [careerPaths, setCareerPaths] = useState([]);
  const [recommendedCourses, setRecommendedCourses] = useState([]);
  const [activeTab, setActiveTab] = useState('skills');

  // Current date and time from the provided information
  const currentDate = new Date('2025-04-20 14:32:58');

  // Current username from the provided information
  const currentUsername = 'nanthiniSanthanam';

  useEffect(() => {
    const fetchTrendsData = async () => {
      try {
        setLoading(true);

        // In a real application, these would be API calls
        // const skillsResponse = await api.get('/api/trends/skills');
        // const coursesResponse = await api.get('/api/trends/courses');
        // const insightsResponse = await api.get('/api/trends/insights');
        // const pathsResponse = await api.get('/api/trends/career-paths');
        // const recommendedResponse = await api.get(`/api/users/${currentUser.id}/recommended-courses`);

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1200));

        // Mock trending skills data
        const mockTrendingSkills = [
          {
            id: 1,
            name: 'Artificial Intelligence',
            growth: 72,
            demandLevel: 'Very High',
            averageSalary: '$135,000',
            relatedCourses: 24,
            description:
              'AI encompasses machine learning, deep learning, and neural networks. Professionals with AI skills are in high demand across industries.',
            trending: true,
            icon: '🤖',
          },
          {
            id: 2,
            name: 'Cloud Computing',
            growth: 65,
            demandLevel: 'High',
            averageSalary: '$128,000',
            relatedCourses: 31,
            description:
              'With more businesses moving to cloud infrastructure, skills in AWS, Azure, and Google Cloud Platform are increasingly valuable.',
            trending: true,
            icon: '☁️',
          },
          {
            id: 3,
            name: 'Cybersecurity',
            growth: 59,
            demandLevel: 'Very High',
            averageSalary: '$124,000',
            relatedCourses: 18,
            description:
              'As cyber threats continue to evolve, security professionals are needed to protect sensitive data and systems.',
            trending: true,
            icon: '🔒',
          },
          {
            id: 4,
            name: 'React Development',
            growth: 54,
            demandLevel: 'High',
            averageSalary: '$115,000',
            relatedCourses: 26,
            description:
              'React remains one of the most popular frontend frameworks, with strong demand for skilled developers.',
            trending: true,
            icon: '⚛️',
          },
          {
            id: 5,
            name: 'DevOps',
            growth: 48,
            demandLevel: 'High',
            averageSalary: '$120,000',
            relatedCourses: 15,
            description:
              'DevOps practices continue to be adopted by organizations seeking to improve development efficiency and reliability.',
            trending: true,
            icon: '🔄',
          },
          {
            id: 6,
            name: 'Data Science',
            growth: 45,
            demandLevel: 'High',
            averageSalary: '$122,000',
            relatedCourses: 29,
            description:
              'Organizations are increasingly relying on data-driven decision making, creating demand for data scientists.',
            trending: false,
            icon: '📊',
          },
          {
            id: 7,
            name: 'Blockchain Development',
            growth: 43,
            demandLevel: 'Medium',
            averageSalary: '$115,000',
            relatedCourses: 12,
            description:
              'Beyond cryptocurrency, blockchain technology is finding applications in finance, supply chain, and many other industries.',
            trending: true,
            icon: '⛓️',
          },
          {
            id: 8,
            name: 'UX/UI Design',
            growth: 38,
            demandLevel: 'Medium',
            averageSalary: '$100,000',
            relatedCourses: 17,
            description:
              'User experience continues to be a competitive differentiator for digital products, driving demand for UX professionals.',
            trending: false,
            icon: '🎨',
          },
        ];

        // Mock trending courses data
        const mockTrendingCourses = [
          {
            id: 101,
            title: 'Machine Learning Engineering with Python',
            instructor: 'Dr. Alan Wong',
            enrollments: 12450,
            growth: 92,
            rating: 4.9,
            thumbnail:
              'https://images.unsplash.com/photo-1527474305487-b87b222841cc?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            price: 79.99,
            duration: '32 hours',
          },
          {
            id: 102,
            title: 'AWS Solutions Architect Certification',
            instructor: 'Sarah Wilson',
            enrollments: 10230,
            growth: 85,
            rating: 4.8,
            thumbnail:
              'https://images.unsplash.com/photo-1607799279861-4dd421887fb3?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            price: 129.99,
            duration: '45 hours',
          },
          {
            id: 103,
            title: 'Ethical Hacking and Penetration Testing',
            instructor: 'Michael Rodriguez',
            enrollments: 8760,
            growth: 78,
            rating: 4.7,
            thumbnail:
              'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            price: 89.99,
            duration: '38 hours',
          },
          {
            id: 104,
            title: 'Advanced React and Redux',
            instructor: 'Alex Johnson',
            enrollments: 7820,
            growth: 74,
            rating: 4.8,
            thumbnail:
              'https://images.unsplash.com/photo-1633356122544-f134324a6cee?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            price: 69.99,
            duration: '28 hours',
          },
          {
            id: 105,
            title: 'DevOps CI/CD Pipeline Implementation',
            instructor: 'Emily Chen',
            enrollments: 6540,
            growth: 67,
            rating: 4.6,
            thumbnail:
              'https://images.unsplash.com/photo-1607706189992-eae578626c86?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            price: 74.99,
            duration: '30 hours',
          },
        ];

        // Mock industry insights data
        const mockIndustryInsights = [
          {
            id: 201,
            title: 'AI Integration Accelerating in Healthcare',
            summary:
              'Healthcare organizations are rapidly adopting AI solutions for diagnostics, patient care, and operational efficiency.',
            source: 'Tech Health Report 2025',
            date: '2025-04-10T00:00:00Z',
            category: 'Healthcare',
            impact: 'High',
            thumbnail:
              'https://images.unsplash.com/photo-1576091160550-2173dba999ef?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            url: '#',
          },
          {
            id: 202,
            title: 'Quantum Computing Skills Gap Widening',
            summary:
              'As quantum computing becomes more practical, companies are struggling to find qualified talent in this emerging field.',
            source: 'Quantum Technology Review',
            date: '2025-04-08T00:00:00Z',
            category: 'Computing',
            impact: 'Medium',
            thumbnail:
              'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            url: '#',
          },
          {
            id: 203,
            title: 'Remote Work Driving Cybersecurity Evolution',
            summary:
              'The continued prevalence of remote and hybrid work models is reshaping enterprise security strategies and creating new job roles.',
            source: 'Workplace Security Annual Report',
            date: '2025-04-15T00:00:00Z',
            category: 'Workplace',
            impact: 'High',
            thumbnail:
              'https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            url: '#',
          },
          {
            id: 204,
            title: 'Sustainability Tech Jobs Growing Exponentially',
            summary:
              'As companies commit to environmental goals, demand for professionals with sustainability technology skills has increased by 120% in the last year.',
            source: 'Green Tech Employment Index',
            date: '2025-04-05T00:00:00Z',
            category: 'Sustainability',
            impact: 'Medium',
            thumbnail:
              'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            url: '#',
          },
        ];

        // Mock career paths data
        const mockCareerPaths = [
          {
            id: 301,
            title: 'Machine Learning Engineer',
            description:
              'Design and implement machine learning models and systems to solve complex problems.',
            growthRate: '25% annually',
            avgSalaryRange: '$120,000 - $180,000',
            keySkills: [
              'Python',
              'TensorFlow/PyTorch',
              'Data Modeling',
              'Cloud ML Services',
              'Statistics',
            ],
            difficulty: 'High',
            preparation: '3-5 years',
            recommendedCourses: [101, 205, 310],
            icon: '🧠',
          },
          {
            id: 302,
            title: 'Cloud Solutions Architect',
            description:
              'Design and implement cloud infrastructure solutions that meet business requirements and optimize performance.',
            growthRate: '22% annually',
            avgSalaryRange: '$125,000 - $175,000',
            keySkills: [
              'AWS/Azure/GCP',
              'Infrastructure as Code',
              'Security',
              'Networking',
              'Cost Optimization',
            ],
            difficulty: 'Medium-High',
            preparation: '2-4 years',
            recommendedCourses: [102, 215, 322],
            icon: '☁️',
          },
          {
            id: 303,
            title: 'Cybersecurity Analyst',
            description:
              'Monitor, detect, investigate, and respond to security threats and incidents.',
            growthRate: '31% annually',
            avgSalaryRange: '$95,000 - $140,000',
            keySkills: [
              'Security Frameworks',
              'Threat Detection',
              'Incident Response',
              'Risk Assessment',
              'Compliance',
            ],
            difficulty: 'Medium',
            preparation: '1-3 years',
            recommendedCourses: [103, 207, 315],
            icon: '🔒',
          },
          {
            id: 304,
            title: 'Full Stack Developer',
            description:
              'Build and maintain both front-end and back-end components of web applications.',
            growthRate: '18% annually',
            avgSalaryRange: '$90,000 - $150,000',
            keySkills: [
              'JavaScript/TypeScript',
              'React/Angular/Vue',
              'Node.js',
              'Databases',
              'APIs',
            ],
            difficulty: 'Medium',
            preparation: '1-2 years',
            recommendedCourses: [104, 201, 308],
            icon: '💻',
          },
        ];

        // Mock recommended courses data - based on user profile
        const mockRecommendedCourses = [
          {
            id: 104,
            title: 'Advanced React and Redux',
            instructor: 'Alex Johnson',
            match: 97,
            reason:
              'Based on your completion of Intro to React and your interest in web development',
            thumbnail:
              'https://images.unsplash.com/photo-1633356122544-f134324a6cee?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            duration: '28 hours',
          },
          {
            id: 208,
            title: 'TypeScript for React Developers',
            instructor: 'Lisa Washington',
            match: 94,
            reason: 'Complements your recent React courses and GitHub activity',
            thumbnail:
              'https://images.unsplash.com/photo-1587620962725-abab7fe55159?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            duration: '18 hours',
          },
          {
            id: 315,
            title: 'Node.js API Development',
            instructor: 'David Kim',
            match: 89,
            reason: 'Based on your interest in full-stack development',
            thumbnail:
              'https://images.unsplash.com/photo-1555066931-4365d14bab8c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            duration: '22 hours',
          },
          {
            id: 102,
            title: 'AWS Solutions Architect Certification',
            instructor: 'Sarah Wilson',
            match: 85,
            reason: 'Popular next step for developers with your profile',
            thumbnail:
              'https://images.unsplash.com/photo-1607799279861-4dd421887fb3?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&q=80',
            duration: '45 hours',
          },
        ];

        // Set state with the mock data
        setTrendingSkills(mockTrendingSkills);
        setTrendingCourses(mockTrendingCourses);
        setIndustryInsights(mockIndustryInsights);
        setCareerPaths(mockCareerPaths);
        setRecommendedCourses(mockRecommendedCourses);
      } catch (err) {
        console.error('Error fetching trends data:', err);
        setError('Failed to load trends data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchTrendsData();
  }, []);

  const formatDate = dateString => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="mt-12 flex justify-center">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-600"></div>
            </div>
            <p className="mt-4 text-lg text-gray-600">
              Loading trends and insights...
            </p>
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

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-primary-700 pt-10 pb-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-3xl font-extrabold text-white sm:text-4xl">
              Tech Skills Trends & Industry Insights
            </h1>
            <p className="mt-4 max-w-2xl mx-auto text-xl text-primary-200">
              Stay ahead of the curve with the latest trends in technology,
              in-demand skills, and career opportunities.
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-20">
        {/* Personalized Recommendations */}
        <div className="bg-white rounded-lg shadow px-5 py-6 sm:px-6 mb-8">
          <div className="border-b border-gray-200 pb-5 mb-5">
            <h2 className="text-2xl font-bold leading-7 text-gray-900 flex items-center">
              <span className="mr-3 text-2xl">👋</span>
              Recommendations for {currentUsername}
              <span className="ml-3 inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                Personalized
              </span>
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              Based on your learning history, skills, and career goals
            </p>
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {recommendedCourses.map(course => (
              <div
                key={course.id}
                className="relative flex flex-col rounded-lg border border-gray-200 bg-white overflow-hidden hover:shadow-md transition-shadow"
              >
                <span className="absolute top-2 right-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {course.match}% Match
                </span>
                <div className="flex-shrink-0">
                  <img
                    className="h-40 w-full object-cover"
                    src={course.thumbnail}
                    alt={course.title}
                  />
                </div>
                <div className="flex-1 p-4 flex flex-col justify-between">
                  <div>
                    <Link to={`/courses/${course.id}`} className="block">
                      <h3 className="text-lg font-medium text-gray-900 hover:text-primary-600">
                        {course.title}
                      </h3>
                    </Link>
                    <p className="mt-1 text-sm text-gray-600">
                      By {course.instructor} •{' '}
                      {course.duration_display || course.duration}
                    </p>
                    <p className="mt-2 text-xs text-gray-500">
                      {course.reason}
                    </p>
                  </div>
                  <div className="mt-4">
                    <Link
                      to={`/courses/${course.id}`}
                      className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      View Course
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main content tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex" aria-label="Tabs">
              {[
                { key: 'skills', name: 'In-Demand Skills' },
                { key: 'courses', name: 'Trending Courses' },
                { key: 'insights', name: 'Industry Insights' },
                { key: 'careers', name: 'Career Paths' },
              ].map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`${
                    activeTab === tab.key
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
                >
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab content */}
          <div className="px-5 py-6 sm:px-6">
            {/* In-Demand Skills tab */}
            {activeTab === 'skills' && (
              <div>
                <div className="border-b border-gray-200 pb-5 mb-5 flex flex-col sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">
                      Most In-Demand Skills in 2025
                    </h2>
                    <p className="mt-1 text-sm text-gray-500">
                      Based on industry growth, job listings, and employer
                      surveys
                    </p>
                  </div>
                  <div className="mt-3 sm:mt-0">
                    <span className="text-sm text-gray-500">
                      Last updated: {formatDate(`2025-04-20T14:39:32`)}
                    </span>
                  </div>
                </div>

                <div className="space-y-6">
                  {trendingSkills.map(skill => (
                    <div
                      key={skill.id}
                      className="bg-white overflow-hidden border border-gray-200 rounded-lg"
                    >
                      <div className="px-4 py-5 sm:px-6 flex flex-wrap sm:flex-nowrap sm:items-center gap-4">
                        <div className="flex-none text-center">
                          <span className="text-4xl">{skill.icon}</span>
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap justify-between mb-1">
                            <h3 className="text-lg font-medium text-gray-900 flex items-center">
                              {skill.name}
                              {skill.trending && (
                                <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                  Hot 🔥
                                </span>
                              )}
                            </h3>
                            <div className="flex items-center text-sm">
                              <span className="text-green-600 font-medium">
                                {skill.growth}% growth
                              </span>
                              <svg
                                className="ml-1 h-4 w-4 text-green-500"
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                              >
                                <path
                                  fillRule="evenodd"
                                  d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z"
                                  clipRule="evenodd"
                                />
                              </svg>
                            </div>
                          </div>
                          <p className="text-sm text-gray-600">
                            {skill.description}
                          </p>
                        </div>
                      </div>

                      <div className="bg-gray-50 px-4 py-4 sm:px-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm border-t border-gray-200">
                        <div>
                          <span className="text-gray-500">Demand Level:</span>
                          <span
                            className={`ml-1 font-medium ${skill.demandLevel === 'Very High' ? 'text-red-600' : skill.demandLevel === 'High' ? 'text-orange-600' : 'text-yellow-600'}`}
                          >
                            {skill.demandLevel}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-500">Average Salary:</span>
                          <span className="ml-1 font-medium text-gray-900">
                            {skill.averageSalary}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-500">
                            Related Courses:
                          </span>
                          <Link
                            to="/courses"
                            className="ml-1 text-primary-600 hover:text-primary-500"
                          >
                            View {skill.relatedCourses} courses
                          </Link>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-8 flex justify-center">
                  <Link
                    to="/skills-explorer"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Explore All Skills
                  </Link>
                </div>
              </div>
            )}

            {/* Trending Courses tab */}
            {activeTab === 'courses' && (
              <div>
                <div className="border-b border-gray-200 pb-5 mb-5 flex flex-col sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">
                      Trending Courses
                    </h2>
                    <p className="mt-1 text-sm text-gray-500">
                      Most popular courses by enrollment growth in the past 30
                      days
                    </p>
                  </div>
                  <div className="mt-3 sm:mt-0">
                    <span className="text-sm text-gray-500">
                      Last updated: {formatDate(`2025-04-20T14:39:32`)}
                    </span>
                  </div>
                </div>

                <div className="space-y-6">
                  {trendingCourses.map(course => (
                    <div
                      key={course.id}
                      className="bg-white overflow-hidden border border-gray-200 rounded-lg"
                    >
                      <div className="md:flex">
                        <div className="md:flex-shrink-0">
                          <img
                            className="h-48 w-full object-cover md:w-48"
                            src={course.thumbnail}
                            alt={course.title}
                          />
                        </div>
                        <div className="p-6 flex-1">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <Link
                                to={`/courses/${course.id}`}
                                className="block"
                              >
                                <h3 className="text-xl font-medium text-gray-900 hover:text-primary-600">
                                  {course.title}
                                </h3>
                              </Link>
                              <p className="mt-1 text-sm text-gray-600">
                                By {course.instructor}
                              </p>
                            </div>
                            <div className="ml-4 flex-shrink-0">
                              <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                +{course.growth}% enrollment
                              </div>
                            </div>
                          </div>

                          <div className="mt-6 flex items-center justify-between">
                            <div className="flex items-center">
                              <div className="flex items-center">
                                {[0, 1, 2, 3, 4].map(rating => (
                                  <svg
                                    key={rating}
                                    className={`h-5 w-5 ${rating < Math.floor(course.rating) ? 'text-yellow-400' : 'text-gray-300'}`}
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                  >
                                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                  </svg>
                                ))}
                              </div>
                              <p className="ml-2 text-sm text-gray-600">
                                {course.rating} •{' '}
                                {course.enrollments.toLocaleString()} students
                              </p>
                            </div>
                            <div className="text-sm">
                              <span className="font-medium text-gray-900">
                                ${course.price}
                              </span>
                              <span className="text-gray-500">
                                {' '}
                                • {course.duration}
                              </span>
                            </div>
                          </div>

                          <div className="mt-4">
                            <Link
                              to={`/courses/${course.id}`}
                              className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                            >
                              View Course
                            </Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-8 flex justify-center">
                  <Link
                    to="/courses"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Browse All Courses
                  </Link>
                </div>
              </div>
            )}

            {/* Industry Insights tab */}
            {activeTab === 'insights' && (
              <div>
                <div className="border-b border-gray-200 pb-5 mb-5 flex flex-col sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">
                      Industry Insights
                    </h2>
                    <p className="mt-1 text-sm text-gray-500">
                      Latest tech industry trends and developments that could
                      impact your career
                    </p>
                  </div>
                  <div className="mt-3 sm:mt-0">
                    <span className="text-sm text-gray-500">
                      Last updated: {formatDate(`2025-04-20T14:39:32`)}
                    </span>
                  </div>
                </div>

                <div className="grid gap-6 lg:grid-cols-2">
                  {industryInsights.map(insight => (
                    <div
                      key={insight.id}
                      className="bg-white overflow-hidden border border-gray-200 rounded-lg flex flex-col"
                    >
                      <div className="flex-shrink-0">
                        <img
                          className="h-48 w-full object-cover"
                          src={insight.thumbnail}
                          alt={insight.title}
                        />
                      </div>
                      <div className="flex-1 p-6">
                        <div>
                          <div className="flex items-center">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                              {insight.category}
                            </span>
                            <span
                              className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium ${
                                insight.impact === 'High'
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-yellow-100 text-yellow-800'
                              }`}
                            >
                              {insight.impact} Impact
                            </span>
                          </div>
                          <a href={insight.url} className="block mt-2">
                            <h3 className="text-xl font-medium text-gray-900 hover:text-primary-600">
                              {insight.title}
                            </h3>
                          </a>
                          <p className="mt-3 text-base text-gray-600">
                            {insight.summary}
                          </p>
                        </div>
                        <div className="mt-6 flex items-center justify-between">
                          <div className="flex text-sm text-gray-500">
                            <span>Source: {insight.source}</span>
                          </div>
                          <div className="text-sm text-gray-500">
                            {formatDate(insight.date)}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-8 flex justify-center">
                  <Link
                    to="/insights"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    View All Insights
                  </Link>
                </div>
              </div>
            )}

            {/* Career Paths tab */}
            {activeTab === 'careers' && (
              <div>
                <div className="border-b border-gray-200 pb-5 mb-5 flex flex-col sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">
                      In-Demand Career Paths
                    </h2>
                    <p className="mt-1 text-sm text-gray-500">
                      Explore high-growth tech careers and their required skills
                    </p>
                  </div>
                  <div className="mt-3 sm:mt-0">
                    <span className="text-sm text-gray-500">
                      Last updated: {formatDate(`2025-04-20T14:39:32`)}
                    </span>
                  </div>
                </div>

                <div className="space-y-8">
                  {careerPaths.map(career => (
                    <div
                      key={career.id}
                      className="bg-white overflow-hidden border border-gray-200 rounded-lg"
                    >
                      <div className="px-6 py-5">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 text-4xl mr-4">
                            {career.icon}
                          </div>
                          <div>
                            <h3 className="text-2xl font-bold text-gray-900">
                              {career.title}
                            </h3>
                            <p className="mt-1 text-gray-600">
                              {career.description}
                            </p>
                          </div>
                        </div>

                        <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
                          <div>
                            <h4 className="text-sm font-medium text-gray-500">
                              Growth Rate
                            </h4>
                            <p className="mt-1 text-lg font-medium text-green-600">
                              {career.growthRate}
                            </p>
                          </div>
                          <div>
                            <h4 className="text-sm font-medium text-gray-500">
                              Salary Range
                            </h4>
                            <p className="mt-1 text-lg font-medium text-gray-900">
                              {career.avgSalaryRange}
                            </p>
                          </div>
                          <div>
                            <h4 className="text-sm font-medium text-gray-500">
                              Difficulty
                            </h4>
                            <p className="mt-1 text-lg font-medium text-gray-900">
                              {career.difficulty}
                            </p>
                          </div>
                          <div>
                            <h4 className="text-sm font-medium text-gray-500">
                              Preparation Time
                            </h4>
                            <p className="mt-1 text-lg font-medium text-gray-900">
                              {career.preparation}
                            </p>
                          </div>
                        </div>

                        <div className="mt-6">
                          <h4 className="text-sm font-medium text-gray-500">
                            Key Skills
                          </h4>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {career.keySkills.map((skill, index) => (
                              <span
                                key={index}
                                className="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div className="mt-6 flex justify-end">
                          <Link
                            to={`/career-path/${career.id}`}
                            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                          >
                            Explore Career Path
                          </Link>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-8 flex justify-center">
                  <Link
                    to="/career-explorer"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    View All Career Paths
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Newsletter subscription */}
        <div className="mt-8 bg-gray-800 shadow rounded-lg">
          <div className="px-5 py-6 sm:px-6">
            <div className="text-center">
              <h2 className="text-xl font-bold text-white">
                Stay Updated with Tech Trends
              </h2>
              <p className="mt-1 text-sm text-gray-300">
                Subscribe to our newsletter for the latest industry trends,
                skills insights, and career opportunities.
              </p>
              <form className="mt-5 sm:flex sm:max-w-md sm:mx-auto">
                <label htmlFor="email-address" className="sr-only">
                  Email address
                </label>
                <input
                  type="email"
                  name="email-address"
                  id="email-address"
                  autoComplete="email"
                  required
                  className="appearance-none min-w-0 w-full bg-white border border-gray-300 rounded-md shadow-sm py-2 px-4 text-base text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Enter your email"
                />
                <div className="mt-3 rounded-md sm:mt-0 sm:ml-3 sm:flex-shrink-0">
                  <button
                    type="submit"
                    className="w-full bg-primary-600 flex items-center justify-center border border-transparent rounded-md py-2 px-4 text-base font-medium text-white hover:bg-primary-700 focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Subscribe
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrendsPage;
