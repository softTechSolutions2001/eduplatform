/**
 * File: frontend/src/components/common/Certificate.jsx
 * Purpose: Display and allow download of completion certificates
 *
 * This component:
 * 1. Displays a certificate of completion for a course
 * 2. Provides options to download or share the certificate
 * 3. Shows certificate details including user name, course, and date
 *
 * Usage:
 * <Certificate
 *   userName="John Doe"
 *   courseName="Advanced Web Development"
 *   completionDate="2025-04-27"
 *   certificateId="CERT-123456"
 * />
 *
 * Variables to modify:
 * - CERTIFICATE_BACKGROUND: URL to certificate background image
 * - CERTIFICATE_LOGO: URL to logo to display on certificate
 */

import React, { useRef } from 'react';
import { saveAs } from 'file-saver';
import html2canvas from 'html2canvas';
import Button from './Button';

// Customizable variables
const CERTIFICATE_BACKGROUND = '/images/certificate-background.jpg';
const CERTIFICATE_LOGO = '/images/logo-full.png';

const Certificate = ({
  userName,
  courseName,
  completionDate,
  certificateId,
  instructorName = 'Professor Santhanam',
  instructorTitle = 'Lead Instructor',
}) => {
  const certificateRef = useRef(null);

  const formatDate = dateString => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const downloadCertificate = async () => {
    const certificateElement = certificateRef.current;

    try {
      const canvas = await html2canvas(certificateElement, {
        scale: 2,
        logging: false,
        useCORS: true,
      });

      canvas.toBlob(blob => {
        saveAs(blob, `${userName}-${courseName}-Certificate.png`);
      });
    } catch (error) {
      console.error('Error generating certificate:', error);
      alert('Failed to download certificate. Please try again.');
    }
  };

  return (
    <div className="flex flex-col items-center">
      {/* Certificate display */}
      <div
        ref={certificateRef}
        className="relative w-full max-w-4xl aspect-[1.4/1] border border-gray-200 rounded-lg shadow-lg overflow-hidden mb-6"
        style={{
          backgroundImage: `url(${CERTIFICATE_BACKGROUND})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div className="absolute inset-0 bg-white bg-opacity-90"></div>

        <div className="relative z-10 flex flex-col items-center justify-center h-full p-8 text-center">
          <img
            src={CERTIFICATE_LOGO}
            alt="EduPlatform Logo"
            className="h-16 mb-6"
          />

          <div className="mb-2 text-gray-500 uppercase tracking-widest text-sm font-semibold">
            Certificate of Completion
          </div>

          <div className="w-1/3 border-b-2 border-primary-600 mb-6"></div>

          <h1 className="text-4xl font-bold text-gray-800 mb-2">{userName}</h1>

          <p className="text-lg text-gray-600 mb-6">
            has successfully completed the course
          </p>

          <h2 className="text-3xl font-semibold text-primary-700 mb-6">
            {courseName}
          </h2>

          <p className="text-lg text-gray-600 mb-8">
            Completed on {formatDate(completionDate)}
          </p>

          <div className="flex justify-center w-full gap-x-16 mt-4">
            <div className="text-center">
              <div className="border-t-2 border-gray-400 w-40 pt-2">
                <p className="font-semibold">{instructorName}</p>
                <p className="text-sm text-gray-500">{instructorTitle}</p>
              </div>
            </div>

            <div className="text-center">
              <div className="border-t-2 border-gray-400 w-40 pt-2">
                <p className="font-semibold">Certificate ID</p>
                <p className="text-sm text-gray-500">{certificateId}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-4 justify-center">
        <Button onClick={downloadCertificate} variant="primary">
          Download Certificate
        </Button>

        <Button variant="secondary">Share Certificate</Button>
      </div>
    </div>
  );
};

export default Certificate;
