/**
 * File: frontend/src/pages/certificates/CertificatePage.jsx
 * Purpose: Display and allow download of course completion certificates for premium users
 *
 * This component:
 * 1. Fetches certificate data based on certificateId URL parameter
 * 2. Displays the certificate using the Certificate component
 * 3. Allows users to download their certificate
 * 4. Shows appropriate loading and error states
 *
 * Prerequisites:
 * - User must be authenticated
 * - User must have a premium subscription
 * - User must have completed the course
 *
 * Variables to modify:
 * - ERROR_MESSAGES: Customize error messages shown to users
 *
 * Backend Connection Points:
 * - GET /certificates/:certificateId - Fetches certificate details
 *
 * Created by: Professor Santhanam
 * Last updated: 2025-04-27
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { certificateService } from '../../services/api';
import { Certificate, Button, Alert } from '../../components/common';
import { MainLayout } from '../../components/layouts';
import { useAuth } from '../../contexts/AuthContext';

// Customizable error messages
const ERROR_MESSAGES = {
  notFound:
    "We couldn't find this certificate. It may have been removed or you don't have access to it.",
  loadFailed: 'Failed to load the certificate. Please try again later.',
  subscriptionRequired:
    'Certificates are only available to premium subscribers. Please upgrade your subscription to access this feature.',
};

const CertificatePage = () => {
  // Get certificate ID from URL params
  const { certificateId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, isSubscriber } = useAuth();

  // State for the certificate data and UI states
  const [certificate, setCertificate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load certificate data when component mounts
  useEffect(() => {
    const loadCertificate = async () => {
      // Make sure user is authenticated and has premium subscription
      if (!isAuthenticated()) {
        navigate('/login', {
          state: { from: `/certificates/${certificateId}` },
        });
        return;
      }

      if (!isSubscriber()) {
        setError(ERROR_MESSAGES.subscriptionRequired);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await certificateService.getCertificate(certificateId);
        setCertificate(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error loading certificate:', err);
        setError(
          err.status === 404
            ? ERROR_MESSAGES.notFound
            : ERROR_MESSAGES.loadFailed
        );
        setLoading(false);
      }
    };

    loadCertificate();
  }, [certificateId, isAuthenticated, isSubscriber, navigate]);

  // Handle certificate download
  const handleDownloadCertificate = () => {
    if (!certificate) return;

    // This function is implemented in the Certificate component
    // It will be triggered by a ref or method call
    // For now, we'll simulate it with an alert
    alert('Certificate download started!');
  };

  // Show loading state
  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-700 mx-auto mb-4"></div>
            <p className="text-primary-700 font-medium">
              Loading certificate...
            </p>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Show error state
  if (error) {
    return (
      <MainLayout>
        <div className="max-w-4xl mx-auto px-4 py-8">
          <Alert type="error" title="Certificate Error">
            {error}
          </Alert>
          <div className="mt-6 flex justify-center">
            <Button color="primary" onClick={() => navigate('/dashboard')}>
              Back to Dashboard
            </Button>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Show certificate
  if (certificate) {
    return (
      <MainLayout>
        <div className="max-w-5xl mx-auto px-4 py-8">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Course Completion Certificate
            </h1>
            <p className="text-gray-600">
              Congratulations on completing {certificate.course.title}!
            </p>
          </div>

          <div className="bg-white shadow-lg rounded-lg p-6 mb-8">
            <Certificate
              userName={`${certificate.user.first_name} ${certificate.user.last_name}`}
              courseName={certificate.course.title}
              completionDate={certificate.issue_date}
              certificateId={certificate.certificate_number}
            />
          </div>

          <div className="flex justify-center space-x-4">
            <Button
              color="primary"
              onClick={handleDownloadCertificate}
              iconRight={
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              }
            >
              Download Certificate
            </Button>
            <Button color="secondary" onClick={() => navigate('/dashboard')}>
              Back to Dashboard
            </Button>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Fallback if something went wrong
  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto px-4 py-8 text-center">
        <p>Something went wrong. Please try again later.</p>
      </div>
    </MainLayout>
  );
};

export default CertificatePage;
