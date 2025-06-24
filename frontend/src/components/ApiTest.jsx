import React, { useState, useEffect } from 'react';
import { courseService } from '../services/api';

const ApiTest = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    const testApi = async () => {
      try {
        setLoading(true);
        const response = await courseService.getAllCourses();
        setCourses(response.data.results || response.data);
        setLoading(false);
      } catch (err) {
        console.error('API Test Error:', err);
        setError(err.message || 'Failed to fetch courses');
        setLoading(false);
      }
    };

    testApi();
  }, []);

  if (loading) {
    return <div className="text-center p-8">Loading...</div>;
  }

  if (error) {
    return (
      <div className="p-8 bg-red-50 border border-red-200 rounded-md">
        <h2 className="text-lg font-bold text-red-700">API Error</h2>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h2 className="text-xl font-bold mb-4">API Connection Test</h2>
      <div className="p-4 bg-green-50 border border-green-200 rounded-md mb-4">
        <p className="text-green-700">✅ API connection successful!</p>
        <p className="text-sm text-green-600">Found {courses.length} courses</p>
      </div>

      <h3 className="text-lg font-semibold mb-2">Courses Data:</h3>
      <div className="bg-gray-50 p-4 rounded-md overflow-auto max-h-96">
        <pre>{JSON.stringify(courses, null, 2)}</pre>
      </div>
    </div>
  );
};

export default ApiTest;
