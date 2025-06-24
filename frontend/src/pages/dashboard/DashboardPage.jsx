/**
 * File: frontend/src/pages/dashboard/DashboardPage.jsx
 * Purpose: Generic dashboard that redirects to role-specific dashboard
 * Version: 2.0.0
 * Date: 2025-05-22
 *
 * Key features:
 * 1. Automatically redirects users to their role-specific dashboard
 * 2. Serves as a central entry point for all authenticated users
 * 3. Shows loading state while checking user role
 * 4. Fallbacks to student dashboard if role detection fails
 *
 * Implementation notes:
 * - Uses AuthContext to check user role
 * - Redirects to appropriate dashboard based on role
 * - Provides smooth transition with loading state
 */

import React, { useEffect, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const DashboardPage = () => {
  const {
    currentUser,
    userRole,
    loading,
    isInstructor,
    isAdmin,
    isAuthenticated,
  } = useAuth();
  const [dashboardPath, setDashboardPath] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Determine which dashboard to show based on user role
    if (!loading) {
      let path = '/student/dashboard'; // Default

      if (isInstructor()) {
        path = '/instructor/dashboard';
      } else if (isAdmin()) {
        path = '/admin/dashboard';
      }

      console.log('Redirecting to dashboard:', path, 'Role:', userRole);
      setDashboardPath(path);
    }
  }, [loading, userRole, isInstructor, isAdmin]);

  // If not authenticated, redirect to login
  if (!loading && !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // If still loading, show a loading indicator
  if (loading || !dashboardPath) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-700"></div>
        <span className="ml-3 text-primary-700">Loading dashboard...</span>
      </div>
    );
  }

  // Redirect to role-specific dashboard
  return <Navigate to={dashboardPath} replace />;
};

export default DashboardPage;
