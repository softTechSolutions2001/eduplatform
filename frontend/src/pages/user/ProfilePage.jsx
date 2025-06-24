import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';

const ProfilePage = () => {
  const { currentUser } = useAuth();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('account');
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    username: '',
    bio: '',
    location: '',
    website: '',
    twitter: '',
    linkedin: '',
    github: '',
    profileImage: null,
  });
  const [successMessage, setSuccessMessage] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [newPassword, setNewPassword] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    courseUpdates: true,
    newMessages: true,
    marketingEmails: false,
    reminders: true,
  });

  // Current date and time for "Last login" information
  const currentDate = new Date('2025-04-20 09:44:09');
  const lastLogin = currentDate.toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  // Using the provided username
  const currentUsername = 'nanthiniSanthanam';

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        setLoading(true);

        // In a real application, you would fetch user data from an API
        // const response = await api.get('/api/users/profile/');
        // setUser(response.data);

        // For demonstration purposes, we'll use mock data
        await new Promise(resolve => setTimeout(resolve, 800));

        const mockUser = {
          id: 1,
          firstName: 'Nanthini',
          lastName: 'Santhanam',
          email: 'nanthini.santhanam@example.com',
          username: currentUsername,
          bio: 'Full-stack developer passionate about learning new technologies and building educational tools.',
          location: 'Chennai, India',
          website: 'https://nanthinisanthanam.dev',
          twitter: 'nanthinisanthanam',
          linkedin: 'nanthini-santhanam',
          github: 'nanthinisanthanam',
          profileImage:
            'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=3&w=256&h=256&q=80',
          joined: '2025-01-15',
          lastLogin: currentDate.toISOString(),
          coursesEnrolled: 7,
          coursesCompleted: 4,
          certificatesEarned: 3,
          totalHours: 125,
          averageRating: 4.8,
        };

        setUser(mockUser);
        setFormData({
          firstName: mockUser.firstName,
          lastName: mockUser.lastName,
          email: mockUser.email,
          username: mockUser.username,
          bio: mockUser.bio,
          location: mockUser.location,
          website: mockUser.website,
          twitter: mockUser.twitter,
          linkedin: mockUser.linkedin,
          github: mockUser.github,
          profileImage: null,
        });
      } catch (err) {
        console.error('Error fetching user profile:', err);
        setError('Failed to load profile. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, [currentUsername]);

  const handleInputChange = e => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleImageChange = e => {
    if (e.target.files && e.target.files[0]) {
      setFormData(prev => ({
        ...prev,
        profileImage: e.target.files[0],
      }));
    }
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setIsSaving(true);

    try {
      // In a real application, you would update the user profile via API
      // const formDataToSend = new FormData();
      // Object.keys(formData).forEach(key => {
      //   formDataToSend.append(key, formData[key]);
      // });
      // await api.patch('/api/users/profile/', formDataToSend);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      setSuccessMessage('Profile updated successfully');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error updating profile:', err);
      setError('Failed to update profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handlePasswordChange = async e => {
    e.preventDefault();

    // Basic validation
    if (newPassword.newPassword !== newPassword.confirmPassword) {
      setPasswordError('Passwords do not match');
      return;
    }

    if (newPassword.newPassword.length < 8) {
      setPasswordError('Password must be at least 8 characters long');
      return;
    }

    setPasswordError('');

    try {
      // In a real application, you would update the password via API
      // await api.post('/api/users/change-password/', newPassword);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      setPasswordSuccess('Password changed successfully');
      setNewPassword({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });

      setTimeout(() => setPasswordSuccess(''), 3000);
    } catch (err) {
      console.error('Error changing password:', err);
      setPasswordError(
        'Failed to change password. Please check your current password and try again.'
      );
    }
  };

  const handleNotificationChange = e => {
    const { name, checked } = e.target;
    setNotifications(prev => ({
      ...prev,
      [name]: checked,
    }));
  };

  const handleSaveNotifications = async () => {
    try {
      // In a real application, you would update notification settings via API
      // await api.post('/api/users/notifications/', notifications);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 800));

      setSuccessMessage('Notification preferences updated successfully');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error updating notifications:', err);
      setError('Failed to update notification settings. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-center">
            <div className="w-full max-w-3xl">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Loading profile...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-center">
            <div className="w-full max-w-3xl">
              <div className="bg-white shadow overflow-hidden rounded-lg p-6">
                <div className="flex items-center">
                  <svg
                    className="h-8 w-8 text-red-500"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                  <h2 className="ml-3 text-lg font-medium text-gray-900">
                    Error
                  </h2>
                </div>
                <p className="mt-2 text-gray-600">{error}</p>
                <button
                  onClick={() => window.location.reload()}
                  className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row">
          {/* Profile Summary */}
          <div className="w-full lg:w-1/3 lg:pr-8 mb-8 lg:mb-0">
            <div className="bg-white shadow overflow-hidden rounded-lg sticky top-6">
              <div className="px-4 py-5 sm:px-6 border-b border-gray-200 bg-gray-50">
                <h3 className="text-lg font-medium leading-6 text-gray-900">
                  Profile Summary
                </h3>
              </div>

              <div className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 h-24 w-24 relative">
                    <img
                      className="h-24 w-24 rounded-full object-cover"
                      src={user.profileImage}
                      alt="Profile"
                    />
                    <div className="absolute bottom-0 right-0 h-6 w-6 rounded-full bg-green-400 border-2 border-white"></div>
                  </div>
                  <div className="ml-5">
                    <h2 className="text-xl font-bold text-gray-900">{`${user.firstName} ${user.lastName}`}</h2>
                    <p className="text-sm text-gray-500">@{user.username}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      {user.location}
                    </p>
                  </div>
                </div>

                <div className="mt-6 border-t border-gray-200 pt-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-primary-600">
                        {user.coursesEnrolled}
                      </p>
                      <p className="text-sm text-gray-500">Courses Enrolled</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-primary-600">
                        {user.coursesCompleted}
                      </p>
                      <p className="text-sm text-gray-500">Courses Completed</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-primary-600">
                        {user.certificatesEarned}
                      </p>
                      <p className="text-sm text-gray-500">Certificates</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-primary-600">
                        {user.totalHours}
                      </p>
                      <p className="text-sm text-gray-500">Learning Hours</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 border-t border-gray-200 pt-4">
                  <dl className="space-y-2">
                    <div className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">
                        Member Since
                      </dt>
                      <dd className="text-sm text-gray-900">
                        {new Date(user.joined).toLocaleDateString()}
                      </dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">
                        Last Login
                      </dt>
                      <dd className="text-sm text-gray-900">{lastLogin}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">
                        Rating
                      </dt>
                      <dd className="text-sm text-gray-900 flex items-center">
                        {user.averageRating}
                        <svg
                          className="ml-1 h-4 w-4 text-yellow-400"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      </dd>
                    </div>
                  </dl>
                </div>

                <div className="mt-6 flex justify-center">
                  <Link
                    to="/dashboard/my-courses"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700"
                  >
                    View My Courses
                  </Link>
                </div>
              </div>

              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                <h4 className="text-sm font-medium text-gray-500">Connect</h4>
                <div className="mt-2 flex space-x-3">
                  {user.twitter && (
                    <a
                      href={`https://twitter.com/${user.twitter}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-gray-500"
                    >
                      <span className="sr-only">Twitter</span>
                      <svg
                        className="h-5 w-5"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84" />
                      </svg>
                    </a>
                  )}
                  {user.linkedin && (
                    <a
                      href={`https://linkedin.com/in/${user.linkedin}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-gray-500"
                    >
                      <span className="sr-only">LinkedIn</span>
                      <svg
                        className="h-5 w-5"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.338 16.338H13.67V12.16c0-.995-.017-2.277-1.387-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248H8.014v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.778 3.203 4.092v4.711zM5.005 6.575a1.548 1.548 0 11-.003-3.096 1.548 1.548 0 01.003 3.096zm-1.337 9.763H6.34v-8.59H3.667v8.59zM17.668 1H2.328C1.595 1 1 1.581 1 2.298v15.403C1 18.418 1.595 19 2.328 19h15.34c.734 0 1.332-.582 1.332-1.299V2.298C19 1.581 18.402 1 17.668 1z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </a>
                  )}
                  {user.github && (
                    <a
                      href={`https://github.com/${user.github}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-gray-500"
                    >
                      <span className="sr-only">GitHub</span>
                      <svg
                        className="h-5 w-5"
                        fill="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          fillRule="evenodd"
                          d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 12.017C20 6.484 15.522 2 12 2z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </a>
                  )}
                  {user.website && (
                    <a
                      href={user.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-gray-500"
                    >
                      <span className="sr-only">Website</span>
                      <svg
                        className="h-5 w-5"
                        fill="currentColor"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                      >
                        <path d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Settings Tabs */}
          <div className="w-full lg:w-2/3">
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex" aria-label="Tabs">
                  {['account', 'security', 'notifications', 'integrations'].map(
                    tab => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`${
                          activeTab === tab
                            ? 'border-primary-500 text-primary-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        } whitespace-nowrap py-4 px-4 border-b-2 font-medium text-sm capitalize flex-1 text-center`}
                      >
                        {tab}
                      </button>
                    )
                  )}
                </nav>
              </div>

              <div className="p-6">
                {/* Account Settings Tab */}
                {activeTab === 'account' && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-6">
                      Account Information
                    </h3>

                    {successMessage && (
                      <div className="mb-6 bg-green-50 border-l-4 border-green-400 p-4">
                        <div className="flex">
                          <div className="flex-shrink-0">
                            <svg
                              className="h-5 w-5 text-green-400"
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
                          </div>
                          <div className="ml-3">
                            <p className="text-sm text-green-700">
                              {successMessage}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    <form onSubmit={handleSubmit}>
                      <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                        <div className="sm:col-span-6">
                          <label
                            htmlFor="profileImage"
                            className="block text-sm font-medium text-gray-700"
                          >
                            Profile Picture
                          </label>
                          <div className="mt-2 flex items-center">
                            <span className="h-12 w-12 rounded-full overflow-hidden bg-gray-100 flex-shrink-0">
                              {formData.profileImage ? (
                                <img
                                  src={URL.createObjectURL(
                                    formData.profileImage
                                  )}
                                  alt="Profile preview"
                                  className="h-full w-full object-cover"
                                />
                              ) : (
                                <img
                                  src={user.profileImage}
                                  alt="Profile"
                                  className="h-full w-full object-cover"
                                />
                              )}
                            </span>
                            <label
                              htmlFor="fileInput"
                              className="ml-5 bg-white py-2 px-3 border border-gray-300 rounded-md shadow-sm text-sm leading-4 font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 cursor-pointer"
                            >
                              Change
                              <input
                                id="fileInput"
                                name="profileImage"
                                type="file"
                                accept="image/*"
                                className="sr-only"
                                onChange={handleImageChange}
                              />
                            </label>
                          </div>
                        </div>

                        <div className="sm:col-span-3">
                          <label
                            htmlFor="firstName"
                            className="block text-sm font-medium text-gray-700"
                          >
                            First Name
                          </label>
                          <div className="mt-1">
                            <input
                              type="text"
                              name="firstName"
                              id="firstName"
                              value={formData.firstName}
                              onChange={handleInputChange}
                              className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                            />
                          </div>
                        </div>

                        <div className="sm:col-span-3">
                          <label
                            htmlFor="lastName"
                            className="block text-sm font-medium text-gray-700"
                          >
                            Last Name
                          </label>
                          <div className="mt-1">
                            <input
                              type="text"
                              name="lastName"
                              id="lastName"
                              value={formData.lastName}
                              onChange={handleInputChange}
                              className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                            />
                          </div>
                        </div>

                        <div className="sm:col-span-6">
                          <label
                            htmlFor="email"
                            className="block text-sm font-medium text-gray-700"
                          >
                            Email Address
                          </label>
                          <div className="mt-1">
                            <input
                              type="email"
                              name="email"
                              id="email"
                              value={formData.email}
                              onChange={handleInputChange}
                              className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                            />
                          </div>
                        </div>

                        <div className="sm:col-span-6">
                          <label
                            htmlFor="username"
                            className="block text-sm font-medium text-gray-700"
                          >
                            Username
                          </label>
                          <div className="mt-1">
                            <input
                              type="text"
                              name="username"
                              id="username"
                              value={formData.username}
                              onChange={handleInputChange}
                              className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                            />
                          </div>
                          <p className="mt-1 text-sm text-gray-500">
                            This will be displayed publicly as your profile URL.
                          </p>
                        </div>

                        <div className="sm:col-span-6">
                          <label
                            htmlFor="bio"
                            className="block text-sm font-medium text-gray-700"
                          >
                            Bio
                          </label>
                          <div className="mt-1">
                            <textarea
                              id="bio"
                              name="bio"
                              rows={4}
                              value={formData.bio}
                              onChange={handleInputChange}
                              className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                            />
                          </div>
                          <p className="mt-2 text-sm text-gray-500">
                            Brief description for your profile. URLs are
                            hyperlinked.
                          </p>
                        </div>

                        <div className="sm:col-span-6">
                          <label
                            htmlFor="location"
                            className="block text-sm font-medium text-gray-700"
                          >
                            Location
                          </label>
                          <div className="mt-1">
                            <input
                              type="text"
                              name="location"
                              id="location"
                              value={formData.location}
                              onChange={handleInputChange}
                              className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                            />
                          </div>
                        </div>

                        <div className="sm:col-span-6">
                          <label
                            htmlFor="website"
                            className="block text-sm font-medium text-gray-700"
                          >
                            Website
                          </label>
                          <div className="mt-1 flex rounded-md shadow-sm">
                            <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 sm:text-sm">
                              https://
                            </span>
                            <input
                              type="text"
                              name="website"
                              id="website"
                              value={formData.website.replace(
                                /^https?:\/\//,
                                ''
                              )}
                              onChange={handleInputChange}
                              className="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md focus:ring-primary-500 focus:border-primary-500 sm:text-sm border-gray-300"
                              placeholder="www.example.com"
                            />
                          </div>
                        </div>

                        <h4 className="sm:col-span-6 text-base font-medium text-gray-900">
                          Social Profiles
                        </h4>

                        <div className="sm:col-span-3">
                          <label
                            htmlFor="twitter"
                            className="block text-sm font-medium text-gray-700"
                          >
                            Twitter
                          </label>
                          <div className="mt-1 flex rounded-md shadow-sm">
                            <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 sm:text-sm">
                              twitter.com/
                            </span>
                            <input
                              type="text"
                              name="twitter"
                              id="twitter"
                              value={formData.twitter}
                              onChange={handleInputChange}
                              className="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md focus:ring-primary-500 focus:border-primary-500 sm:text-sm border-gray-300"
                            />
                          </div>
                        </div>

                        <div className="sm:col-span-3">
                          <label
                            htmlFor="linkedin"
                            className="block text-sm font-medium text-gray-700"
                          >
                            LinkedIn
                          </label>
                          <div className="mt-1 flex rounded-md shadow-sm">
                            <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 sm:text-sm">
                              linkedin.com/in/
                            </span>
                            <input
                              type="text"
                              name="linkedin"
                              id="linkedin"
                              value={formData.linkedin}
                              onChange={handleInputChange}
                              className="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md focus:ring-primary-500 focus:border-primary-500 sm:text-sm border-gray-300"
                            />
                          </div>
                        </div>

                        <div className="sm:col-span-3">
                          <label
                            htmlFor="github"
                            className="block text-sm font-medium text-gray-700"
                          >
                            GitHub
                          </label>
                          <div className="mt-1 flex rounded-md shadow-sm">
                            <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 sm:text-sm">
                              github.com/
                            </span>
                            <input
                              type="text"
                              name="github"
                              id="github"
                              value={formData.github}
                              onChange={handleInputChange}
                              className="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md focus:ring-primary-500 focus:border-primary-500 sm:text-sm border-gray-300"
                            />
                          </div>
                        </div>
                      </div>

                      <div className="pt-8 flex justify-end">
                        <button
                          type="button"
                          className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 mr-3"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          disabled={isSaving}
                          className={`inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 ${
                            isSaving ? 'opacity-70 cursor-not-allowed' : ''
                          }`}
                        >
                          {isSaving ? (
                            <span className="flex items-center">
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
                              Saving...
                            </span>
                          ) : (
                            'Save'
                          )}
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {/* Security Settings Tab */}
                {activeTab === 'security' && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-6">
                      Security Settings
                    </h3>

                    {/* Password Change Form */}
                    <div className="bg-white shadow sm:rounded-lg mb-8">
                      <div className="px-4 py-5 sm:p-6">
                        <h3 className="text-base font-medium leading-6 text-gray-900">
                          Change Password
                        </h3>

                        {passwordError && (
                          <div className="mt-2 bg-red-50 border-l-4 border-red-400 p-4">
                            <div className="flex">
                              <div className="flex-shrink-0">
                                <svg
                                  className="h-5 w-5 text-red-400"
                                  xmlns="http://www.w3.org/2000/svg"
                                  viewBox="0 0 20 20"
                                  fill="currentColor"
                                >
                                  <path
                                    fillRule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                                    clipRule="evenodd"
                                  />
                                </svg>
                              </div>
                              <div className="ml-3">
                                <p className="text-sm text-red-700">
                                  {passwordError}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}

                        {passwordSuccess && (
                          <div className="mt-2 bg-green-50 border-l-4 border-green-400 p-4">
                            <div className="flex">
                              <div className="flex-shrink-0">
                                <svg
                                  className="h-5 w-5 text-green-400"
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
                              </div>
                              <div className="ml-3">
                                <p className="text-sm text-green-700">
                                  {passwordSuccess}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}

                        <form
                          onSubmit={handlePasswordChange}
                          className="mt-5 space-y-6"
                        >
                          <div>
                            <label
                              htmlFor="currentPassword"
                              className="block text-sm font-medium text-gray-700"
                            >
                              Current Password
                            </label>
                            <div className="mt-1">
                              <input
                                id="currentPassword"
                                name="currentPassword"
                                type="password"
                                required
                                value={newPassword.currentPassword}
                                onChange={e =>
                                  setNewPassword({
                                    ...newPassword,
                                    currentPassword: e.target.value,
                                  })
                                }
                                className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                              />
                            </div>
                          </div>

                          <div>
                            <label
                              htmlFor="newPassword"
                              className="block text-sm font-medium text-gray-700"
                            >
                              New Password
                            </label>
                            <div className="mt-1">
                              <input
                                id="newPassword"
                                name="newPassword"
                                type="password"
                                required
                                value={newPassword.newPassword}
                                onChange={e =>
                                  setNewPassword({
                                    ...newPassword,
                                    newPassword: e.target.value,
                                  })
                                }
                                className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                              />
                            </div>
                          </div>

                          <div>
                            <label
                              htmlFor="confirmPassword"
                              className="block text-sm font-medium text-gray-700"
                            >
                              Confirm New Password
                            </label>
                            <div className="mt-1">
                              <input
                                id="confirmPassword"
                                name="confirmPassword"
                                type="password"
                                required
                                value={newPassword.confirmPassword}
                                onChange={e =>
                                  setNewPassword({
                                    ...newPassword,
                                    confirmPassword: e.target.value,
                                  })
                                }
                                className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                              />
                            </div>
                          </div>

                          <div>
                            <button
                              type="submit"
                              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                            >
                              Change Password
                            </button>
                          </div>
                        </form>
                      </div>
                    </div>

                    {/* Two-Factor Authentication */}
                    <div className="bg-white shadow sm:rounded-lg mb-8">
                      <div className="px-4 py-5 sm:p-6">
                        <h3 className="text-base font-medium leading-6 text-gray-900">
                          Two-factor Authentication
                        </h3>
                        <div className="mt-2 max-w-xl text-sm text-gray-500">
                          <p>
                            Add an extra layer of security to your account by
                            enabling two-factor authentication.
                          </p>
                        </div>
                        <div className="mt-5">
                          <button
                            type="button"
                            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                          >
                            Enable Two-Factor Authentication
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Sessions */}
                    <div className="bg-white shadow sm:rounded-lg mb-8">
                      <div className="px-4 py-5 sm:p-6">
                        <h3 className="text-base font-medium leading-6 text-gray-900">
                          Active Sessions
                        </h3>
                        <div className="mt-2 max-w-xl text-sm text-gray-500">
                          <p>
                            These are devices that have logged into your
                            account. Remove those that you don't recognize.
                          </p>
                        </div>
                        <div className="mt-4 divide-y divide-gray-200">
                          <div className="py-4 flex justify-between">
                            <div>
                              <p className="text-sm font-medium text-gray-900">
                                Current Session (Windows - Chrome)
                              </p>
                              <p className="text-xs text-gray-500">
                                Chennai, India - {lastLogin}
                              </p>
                            </div>
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Active
                            </span>
                          </div>
                          <div className="py-4 flex justify-between">
                            <div>
                              <p className="text-sm font-medium text-gray-900">
                                iOS - Safari
                              </p>
                              <p className="text-xs text-gray-500">
                                Chennai, India - 2 days ago
                              </p>
                            </div>
                            <button
                              type="button"
                              className="text-sm text-red-600 hover:text-red-800"
                            >
                              Remove
                            </button>
                          </div>
                        </div>
                        <div className="mt-5">
                          <button
                            type="button"
                            className="text-sm font-medium text-red-600 hover:text-red-800"
                          >
                            Sign out of all other sessions
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Account Deletion */}
                    <div className="bg-white shadow sm:rounded-lg border border-red-200">
                      <div className="px-4 py-5 sm:p-6">
                        <h3 className="text-base font-medium leading-6 text-gray-900">
                          Delete Account
                        </h3>
                        <div className="mt-2 max-w-xl text-sm text-gray-500">
                          <p>
                            Once you delete your account, all of your data will
                            be permanently removed. This action cannot be
                            undone.
                          </p>
                        </div>
                        <div className="mt-5">
                          <button
                            type="button"
                            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                          >
                            Delete Account
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Notifications Settings Tab */}
                {activeTab === 'notifications' && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-6">
                      Notification Preferences
                    </h3>

                    {successMessage && (
                      <div className="mb-6 bg-green-50 border-l-4 border-green-400 p-4">
                        <div className="flex">
                          <div className="flex-shrink-0">
                            <svg
                              className="h-5 w-5 text-green-400"
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
                          </div>
                          <div className="ml-3">
                            <p className="text-sm text-green-700">
                              {successMessage}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="space-y-6">
                      <div>
                        <h4 className="text-base font-medium text-gray-900">
                          Email Notifications
                        </h4>
                        <div className="mt-4 space-y-4">
                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="emailNotifications"
                                name="emailNotifications"
                                type="checkbox"
                                checked={notifications.emailNotifications}
                                onChange={handleNotificationChange}
                                className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label
                                htmlFor="emailNotifications"
                                className="font-medium text-gray-700"
                              >
                                Enable email notifications
                              </label>
                              <p className="text-gray-500">
                                Receive updates about your account via email.
                              </p>
                            </div>
                          </div>

                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="courseUpdates"
                                name="courseUpdates"
                                type="checkbox"
                                checked={notifications.courseUpdates}
                                onChange={handleNotificationChange}
                                className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label
                                htmlFor="courseUpdates"
                                className="font-medium text-gray-700"
                              >
                                Course updates
                              </label>
                              <p className="text-gray-500">
                                Get notified when an instructor posts an update
                                to a course you're taking.
                              </p>
                            </div>
                          </div>

                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="newMessages"
                                name="newMessages"
                                type="checkbox"
                                checked={notifications.newMessages}
                                onChange={handleNotificationChange}
                                className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label
                                htmlFor="newMessages"
                                className="font-medium text-gray-700"
                              >
                                New messages
                              </label>
                              <p className="text-gray-500">
                                Receive an email when someone sends you a direct
                                message.
                              </p>
                            </div>
                          </div>

                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="reminders"
                                name="reminders"
                                type="checkbox"
                                checked={notifications.reminders}
                                onChange={handleNotificationChange}
                                className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label
                                htmlFor="reminders"
                                className="font-medium text-gray-700"
                              >
                                Learning reminders
                              </label>
                              <p className="text-gray-500">
                                Receive reminders to continue your learning
                                journey.
                              </p>
                            </div>
                          </div>

                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="marketingEmails"
                                name="marketingEmails"
                                type="checkbox"
                                checked={notifications.marketingEmails}
                                onChange={handleNotificationChange}
                                className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label
                                htmlFor="marketingEmails"
                                className="font-medium text-gray-700"
                              >
                                Marketing emails
                              </label>
                              <p className="text-gray-500">
                                Receive emails about new courses, promotions,
                                and other marketing communications.
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h4 className="text-base font-medium text-gray-900">
                          Push Notifications
                        </h4>
                        <p className="text-sm text-gray-500 mt-1">
                          Configure push notifications to stay updated on mobile
                          and desktop.
                        </p>
                        <div className="mt-4">
                          <button
                            type="button"
                            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                          >
                            Configure Push Notifications
                          </button>
                        </div>
                      </div>

                      <div className="pt-5">
                        <div className="flex justify-end">
                          <button
                            type="button"
                            onClick={handleSaveNotifications}
                            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                          >
                            Save Preferences
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Integrations Tab */}
                {activeTab === 'integrations' && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-6">
                      Connected Accounts
                    </h3>

                    <div className="space-y-6">
                      <div className="flex items-center justify-between py-4 border-b border-gray-200">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <svg
                              className="h-8 w-8 text-gray-500"
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 24 24"
                              fill="currentColor"
                            >
                              <path d="M12 22c5.421 0 10-4.579 10-10S17.421 2 12 2 2 6.579 2 12s4.579 10 10 10zm0-18c4.337 0 8 3.663 8 8s-3.663 8-8 8-8-3.663-8-8 3.663-8 8-8z" />
                              <path d="M17.5 9a1.5 1.5 0 10-1.5-1.5A1.5 1.5 0 0017.5 9zM6.5 9A1.5 1.5 0 108 7.5 1.5 1.5 0 006.5 9zm8.695 5.534l1.632-1.906a.5.5 0 00-.42-.808h-3.256a.499.499 0 00-.444.271l-1.6 2.857a.5.5 0 00.835.544l1.567-2.11 1.686 1.152z" />
                            </svg>
                          </div>
                          <div className="ml-4">
                            <h4 className="text-base font-medium text-gray-900">
                              Google
                            </h4>
                            <p className="text-sm text-gray-500">
                              Connect your Google account for seamless sign-in
                              and calendar integration.
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                        >
                          Connect
                        </button>
                      </div>

                      <div className="flex items-center justify-between py-4 border-b border-gray-200">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <svg
                              className="h-8 w-8 text-gray-500"
                              fill="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                            </svg>
                          </div>
                          <div className="ml-4">
                            <h4 className="text-base font-medium text-gray-900">
                              Facebook
                            </h4>
                            <p className="text-sm text-gray-500">
                              Connect your Facebook account to share
                              achievements and find friends.
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                        >
                          Connect
                        </button>
                      </div>

                      <div className="flex items-center justify-between py-4 border-b border-gray-200">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <svg
                              className="h-8 w-8 text-gray-500"
                              fill="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm4.441 16.892c-2.102.144-6.784.144-8.883 0C5.282 16.736 5.017 15.622 5 12c.017-3.629.285-4.736 2.558-4.892 2.099-.144 6.782-.144 8.883 0C18.718 7.264 18.982 8.378 19 12c-.018 3.629-.285 4.736-2.559 4.892zM10 9.658l4.917 2.338L10 14.342V9.658z" />
                            </svg>
                          </div>
                          <div className="ml-4">
                            <h4 className="text-base font-medium text-gray-900">
                              GitHub
                            </h4>
                            <p className="text-sm text-gray-500">
                              Connect your GitHub account to showcase your
                              coding projects.
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                        >
                          Connect
                        </button>
                      </div>

                      <div className="flex items-center justify-between py-4 border-b border-gray-200">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <svg
                              className="h-8 w-8 text-gray-500"
                              fill="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path d="M7.799 0H22.6c.77 0 1.399.63 1.399 1.4v21.2c0 .77-.63 1.4-1.4 1.4H7.8c-.77 0-1.4-.63-1.4-1.4V1.4C6.4.63 7.03 0 7.8 0zM0 8.68v6.64c0 .77.63 1.4 1.4 1.4h2.8v-9.44H1.4C.63 7.28 0 7.91 0 8.68zm4.2-2.8v12.04h11.2V5.88H4.2zm14 0v12.04h4.2V5.88h-4.2z" />
                            </svg>
                          </div>
                          <div className="ml-4">
                            <h4 className="text-base font-medium text-gray-900">
                              Slack
                            </h4>
                            <p className="text-sm text-gray-500">
                              Connect your Slack account for learning community
                              notifications.
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                        >
                          Connect
                        </button>
                      </div>

                      <div className="flex items-center justify-between py-4">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <svg
                              className="h-8 w-8 text-gray-500"
                              fill="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                            </svg>
                          </div>
                          <div className="ml-4">
                            <h4 className="text-base font-medium text-gray-900">
                              LinkedIn
                            </h4>
                            <p className="text-sm text-gray-500">
                              Connect your LinkedIn account to add certificates
                              to your profile.
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                        >
                          Connect
                        </button>
                      </div>
                    </div>

                    <div className="mt-10">
                      <h3 className="text-lg font-medium text-gray-900 mb-6">
                        API Access
                      </h3>

                      <div className="bg-white shadow sm:rounded-lg border border-gray-200">
                        <div className="px-4 py-5 sm:p-6">
                          <h3 className="text-base font-medium leading-6 text-gray-900">
                            Developer API
                          </h3>
                          <div className="mt-2 max-w-xl text-sm text-gray-500">
                            <p>
                              Generate API keys to access your data
                              programmatically.
                            </p>
                          </div>
                          <div className="mt-5">
                            <button
                              type="button"
                              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                            >
                              Generate API Key
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
