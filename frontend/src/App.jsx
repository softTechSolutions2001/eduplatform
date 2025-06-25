/**
 * File: frontend/src/App.jsx
 * Version: 2.6.0 (Merged)
 * Date: 2025-06-20 15:28:31
 * Author: mohithasanthanam, cadsanthanam
 * Last Modified: 2025-06-20 15:28:31 UTC
 * Merged By: sujibeautysalon
 *
 * Enhanced Main Application Component with Comprehensive Route Management
 *
 * MERGE RESOLUTION v2.6.0:
 * - Combined features from both HEAD (v2.5.1) and branch (v2.3.1)
 * - Maintained logical course creation flow from HEAD
 * - Preserved enhanced content access control from branch
 * - Unified import statements and route organization
 * - Added missing components and maintained backward compatibility
 * - Integrated toast notifications and network debugging
 *
 * Key Features:
 * 1. Logical Course Management Flow (Create → Module → Lesson)
 * 2. Enhanced Content Access Control with Tiered Educational Content
 * 3. Dual Course Creation Paths (Traditional, Wizard, AI Builder, Drag-Drop)
 * 4. Comprehensive Social Authentication Support
 * 5. Smart Route Protection and Role-Based Access Control
 * 6. Toast Notification System for User Feedback
 * 7. Network Debugging Capabilities in Development Mode
 * 8. Complete Backward Compatibility with Legacy Routes
 *
 * Route Access Levels:
 * - Public routes: Accessible to all users (homepage, about, login, register)
 * - Protected routes: Require basic authentication (course content, profile)
 * - Role-specific routes: Require specific user roles (admin dashboard, instructor dashboard)
 * - Subscription routes: Require premium subscription (certificates)
 * - Tiered content routes: Access based on content level and user status
 */

import { HelmetProvider } from 'react-helmet-async';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import { AuthProvider } from './contexts/AuthContext';

// Development Tools

// Layouts
import MainLayout from './components/layouts/MainLayout';

// Public Pages
import AboutPage from './pages/AboutPage';
import HomePage from './pages/HomePage';
import NotFoundPage from './pages/NotFoundPage';

// Auth Pages
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';
import SocialAuthCallback from './pages/auth/SocialAuthCallback';
import VerifyEmailPage from './pages/auth/VerifyEmailPage';

// Course Pages
import AssessmentPage from './pages/courses/AssessmentPage';
import CourseContentPage from './pages/courses/CourseContentPage';
import CourseLandingPage from './pages/courses/CourseLandingPage';
import CoursesListPage from './pages/courses/CoursesListPage';
import InstructorCourseDetailPage from './pages/courses/InstructorCourseDetailPage';

// Instructor Pages - Organized by logical flow
import { AICourseBuilder } from './aiCourseBuilder';
import CourseCreationOptions from './pages/instructor/CourseCreationOptions';
import CoursesCleanup from './pages/instructor/CoursesCleanup';
import CourseWizardWrapper from './pages/instructor/CourseWizardWrapper';
import CreateCoursePage from './pages/instructor/CreateCoursePage';
import CreateLessonPage from './pages/instructor/CreateLessonPage';
import CreateModulePage from './pages/instructor/CreateModulePage';
import EditCoursePage from './pages/instructor/EditCoursePage';

// Course Builder - Modern Drag-and-Drop Course Builder
import CourseBuilder from './courseBuilder/CourseBuilder';

// Dashboard Pages
import AdminDashboard from './pages/dashboard/AdminDashboard';
import DashboardPage from './pages/dashboard/DashboardPage';
import InstructorDashboard from './pages/dashboard/InstructorDashboard';
import StudentDashboard from './pages/dashboard/StudentDashboard';

// User Pages
import ProfilePage from './pages/user/ProfilePage';

// Subscription Pages
import CheckoutPage from './pages/subscription/CheckoutPage';
import PricingPage from './pages/subscription/PricingPage';
import SubscriptionSuccessPage from './pages/subscription/SubscriptionSuccessPage';

// Certificate Pages
import CertificatePage from './pages/certificates/CertificatePage';

// Route Components
import CourseContentRouteChecker from './components/routes/CourseContentRouteChecker';
import ProtectedRoute from './components/routes/ProtectedRoute';

// Styles
import 'react-toastify/dist/ReactToastify.css';
import './index.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <HelmetProvider>
          <Routes>
            {/* Public Routes */}
            <Route
              path="/"
              element={
                <MainLayout>
                  <HomePage />
                </MainLayout>
              }
            />
            <Route
              path="/about"
              element={
                <MainLayout>
                  <AboutPage />
                </MainLayout>
              }
            />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route
              path="/reset-password/:token"
              element={<ResetPasswordPage />}
            />
            <Route path="/verify-email" element={<VerifyEmailPage />} />

            {/* Social Authentication Callback Route */}
            <Route
              path="/auth/social/:provider/callback"
              element={<SocialAuthCallback />}
            />

            {/* Course Landing Pages - Public but with tiered content */}
            <Route
              path="/courses/:courseSlug"
              element={
                <MainLayout>
                  <CourseLandingPage />
                </MainLayout>
              }
            />

            {/* Module Detail Page - Public view for browsing course structure */}
            <Route
              path="/courses/:courseSlug/modules/:moduleId"
              element={
                <MainLayout>
                  <CourseContentPage previewMode={true} />
                </MainLayout>
              }
            />

            {/* Subscription Plans - Public but with auth redirects */}
            <Route
              path="/pricing"
              element={
                <MainLayout>
                  <PricingPage />
                </MainLayout>
              }
            />

            {/* Routes requiring basic authentication (registered users) */}
            <Route
              path="/checkout/:planId"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <CheckoutPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/subscription/success"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <SubscriptionSuccessPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            {/* Course Content - Smart access control based on content tier */}
            <Route
              path="/courses/:courseSlug/content/:moduleId/:lessonId"
              element={<CourseContentRouteChecker />}
            />
            <Route
              path="/courses/:courseSlug/assessment/:lessonId"
              element={
                <ProtectedRoute requireEmailVerified={true}>
                  <MainLayout>
                    <AssessmentPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            {/* Dashboard Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />

            {/* Course List Page */}
            <Route
              path="/courses"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <CoursesListPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            {/* Role-Specific Dashboards */}
            <Route
              path="/student/dashboard"
              element={
                <ProtectedRoute requiredRoles={['student']}>
                  <MainLayout>
                    <StudentDashboard />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/instructor/dashboard"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <InstructorDashboard />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/instructor/cleanup"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <CoursesCleanup />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/dashboard"
              element={
                <ProtectedRoute requiredRoles={['admin']}>
                  <MainLayout>
                    <AdminDashboard />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            {/* User Routes */}
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <ProfilePage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            {/* Certificate Routes - Only for paid subscribers */}
            <Route
              path="/certificates/:certificateId"
              element={
                <ProtectedRoute requiredSubscription="premium">
                  <MainLayout>
                    <CertificatePage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            {/* LOGICAL FLOW: Instructor Course Management - Organized by Creation Flow */}

            {/* STEP 1: Course Creation - Multiple Methods */}

            {/* Traditional Course Creation */}
            <Route
              path="/instructor/create-course"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <CreateCoursePage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/instructor/courses/traditional/new"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <CreateCoursePage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            {/* Course Creation Options (Selection Interface) */}
            <Route
              path="/instructor/courses/new"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <CourseCreationOptions />
                </ProtectedRoute>
              }
            />

            {/* Course Wizard - New and Edit Modes */}
            <Route
              path="/instructor/courses/wizard"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <CourseWizardWrapper />
                </ProtectedRoute>
              }
            />

            <Route
              path="/instructor/courses/wizard/:courseSlug"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <CourseWizardWrapper />
                </ProtectedRoute>
              }
            />

            {/* Modern Drag-and-Drop Course Builder */}
            <Route
              path="/instructor/courses/builder/:courseSlug?/*"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <CourseBuilder />
                </ProtectedRoute>
              }
            />

            {/* AI Course Builder - Advanced AI-powered course creation */}
            <Route
              path="/instructor/courses/ai-builder"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <AICourseBuilder />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/instructor/courses/ai-builder/:courseId?"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <AICourseBuilder />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            {/* Course Details and Management */}
            <Route
              path="/instructor/courses/:courseIdentifier"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <InstructorCourseDetailPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/instructor/courses/:courseIdentifier/manage"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <InstructorCourseDetailPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            {/* Course Editing - Support both traditional and wizard */}
            <Route
              path="/instructor/courses/:courseIdentifier/edit"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <EditCoursePage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            {/* STEP 2: Module Creation (After Course Creation) */}
            <Route
              path="/instructor/courses/:courseIdentifier/modules/new"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <CreateModulePage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/instructor/courses/:courseIdentifier/modules/create"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <CreateModulePage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            {/* STEP 3: Lesson Creation Routes */}
            <Route
              path="/instructor/courses/:courseSlug/modules/:moduleId/lessons/new"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <CreateLessonPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/instructor/courses/:courseSlug/modules/:moduleId/lessons/create"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <CreateLessonPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            {/* Legacy routes for backward compatibility */}
            <Route
              path="/courses/:courseSlug/modules/new"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <CreateModulePage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/courses/:courseSlug/modules/create"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <CreateModulePage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/courses/:courseSlug/modules/:moduleId/lessons/create"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <CreateLessonPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/courses/:courseSlug/modules/:moduleId/lessons/new"
              element={
                <ProtectedRoute requiredRoles={['instructor', 'admin']}>
                  <MainLayout>
                    <CreateLessonPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />

            {/* 404 Route */}
            <Route
              path="*"
              element={
                <MainLayout>
                  <NotFoundPage />
                </MainLayout>
              }
            />
          </Routes>

          {/* Global Toast Notification Container */}
          <ToastContainer
            position="top-right"
            autoClose={3000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="light"
          />

          {/* Network Debugger - Development Mode Only */}
          {/*  {process.env.NODE_ENV === 'development' && <NetworkDebugger />} */}
        </HelmetProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
