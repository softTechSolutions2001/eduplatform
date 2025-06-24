// File: frontend/src/components/instructor/UploadResourceModal.jsx
/**
 * Upload Resource Modal Component
 * Version: 2.0.0
 * Date: 2025-05-27 14:49:18
 * Author: mohithasanthanam
 * Last Modified: 2025-05-27 14:49:18 UTC
 *
 * This component provides a modal interface for uploading resources with:
 * 1. Progress tracking with visual feedback
 * 2. Proper handling of presigned URL uploads
 * 3. Backend confirmation of successful uploads
 * 4. Support for various file types with validation
 *
 * Usage:
 * <UploadResourceModal
 *   open={boolean}
 *   onClose={function}
 *   lessonId={number|string}
 *   onUploadComplete={function}
 * />
 */

import React, { useState } from 'react';
import axios from 'axios';
import instructorService from '../../services/instructorService';
import Modal from '../common/Modal';
import Button from '../common/Button';
import Alert from '../common/Alert';

// Allowed resource file types - matching backend validation
const ALLOWED_RESOURCE_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'text/plain',
  'text/csv',
  'application/zip',
  'application/x-zip-compressed',
];

const MAX_RESOURCE_SIZE = 100 * 1024 * 1024; // 100MB to match service layer

const UploadResourceModal = ({ open, onClose, lessonId, onUploadComplete }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [uploadStep, setUploadStep] = useState('select'); // 'select', 'uploading', 'confirming', 'complete'
  // File selection handler
  const handleFileSelect = e => {
    const file = e.target.files[0];
    if (!file) return;

    setError('');

    // Validate file type
    if (!ALLOWED_RESOURCE_TYPES.includes(file.type)) {
      setError(
        `File type not supported. Allowed types: PDF, Word, Excel, PowerPoint, Text, CSV, ZIP`
      );
      return;
    }

    // Validate file size (100MB max to match service layer)
    if (file.size > MAX_RESOURCE_SIZE) {
      setError('File size must be less than 100MB');
      return;
    }

    setSelectedFile(file);
  };

  // Upload handler
  const handleUpload = async () => {
    if (!selectedFile || !lessonId) {
      setError('Please select a file and ensure lesson is specified');
      return;
    }

    try {
      setIsUploading(true);
      setUploadStep('uploading');
      setProgress(0);
      setError('');

      // Step 1: Get presigned URL from backend
      const presignedData = await instructorService.getPresignedUrl({
        file_name: selectedFile.name,
        content_type: selectedFile.type,
        lesson_id: lessonId,
      });

      // Step 2: Upload file directly to storage using presigned URL
      await axios.post(
        presignedData.url,
        {
          ...presignedData.fields,
          file: selectedFile,
        },
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: progressEvent => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percentCompleted);
          },
        }
      );

      // Step 3: Confirm upload with backend
      setUploadStep('confirming');
      const resourceData = await instructorService.confirmResourceUpload({
        resource_id: presignedData.resource_id,
        storage_key: presignedData.fields.key,
        filesize: selectedFile.size,
        mime_type: selectedFile.type,
        lesson_id: lessonId,
        premium: false, // Default to free resource
      });

      // Step 4: Complete
      setUploadStep('complete');

      // Notify parent component
      if (onUploadComplete) {
        onUploadComplete(resourceData);
      }

      // Reset after short delay
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err) {
      console.error('Upload failed:', err);
      setError(err.message || 'Upload failed. Please try again.');
      setUploadStep('select');
    } finally {
      setIsUploading(false);
    }
  };

  // Reset and close
  const handleClose = () => {
    setSelectedFile(null);
    setProgress(0);
    setError('');
    setUploadStep('select');
    setIsUploading(false);
    onClose();
  };

  return (
    <Modal
      open={open}
      onClose={isUploading ? null : handleClose}
      title="Upload Resource"
      size="md"
    >
      <div className="p-4 space-y-4">
        {error && <Alert type="error">{error}</Alert>}

        {uploadStep === 'select' && (
          <>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              {selectedFile ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-center">
                    <svg
                      className="h-8 w-8 text-green-500"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                  <div className="text-sm font-medium">{selectedFile.name}</div>
                  <div className="text-xs text-gray-500">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="text-xs text-red-500 hover:text-red-700"
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <>
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                  </svg>
                  <p className="mt-2 text-sm text-gray-600">
                    Drag and drop your file here, or click to browse
                  </p>
                  <p className="mt-1 text-xs text-gray-500">
                    Max file size: 10MB
                  </p>
                </>
              )}
              <input
                type="file"
                id="resource-file"
                className="hidden"
                onChange={handleFileSelect}
                accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.zip"
              />
              <label
                htmlFor="resource-file"
                className="mt-4 inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer"
              >
                {selectedFile ? 'Change File' : 'Select File'}
              </label>
            </div>
            <div className="bg-blue-50 p-3 rounded">
              <h4 className="text-blue-700 text-sm font-medium mb-1">
                Resource Tips
              </h4>
              <ul className="text-xs text-blue-700 list-disc list-inside">
                <li>
                  Supported: PDF, Word, Excel, PowerPoint, Text, CSV, ZIP files
                </li>
                <li>Maximum file size: 100MB</li>
                <li>Resources can be downloaded by students</li>
                <li>Keep file names descriptive and concise</li>
                <li>Consider accessibility when preparing materials</li>
              </ul>
            </div>
          </>
        )}

        {uploadStep === 'uploading' && (
          <div className="text-center py-4 space-y-4">
            <div className="flex justify-center">
              <svg
                className="animate-spin h-8 w-8 text-primary-500"
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
            </div>
            <div className="text-lg font-medium">Uploading...</div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-primary-600 h-2.5 rounded-full"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <div className="text-sm text-gray-500">{progress}% complete</div>
          </div>
        )}

        {uploadStep === 'confirming' && (
          <div className="text-center py-4 space-y-4">
            <div className="flex justify-center">
              <svg
                className="animate-spin h-8 w-8 text-primary-500"
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
            </div>
            <div className="text-lg font-medium">Confirming upload...</div>
            <div className="text-sm text-gray-500">
              Please wait while we process your file
            </div>
          </div>
        )}

        {uploadStep === 'complete' && (
          <div className="text-center py-4 space-y-4">
            <div className="flex justify-center">
              <svg
                className="h-16 w-16 text-green-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <div className="text-lg font-medium text-green-600">
              Upload Complete!
            </div>
            <div className="text-sm text-gray-500">
              Your resource has been uploaded successfully
            </div>
          </div>
        )}

        <div className="flex justify-end space-x-3 mt-6">
          {uploadStep === 'select' && (
            <>
              <Button
                variant="outlined"
                color="secondary"
                onClick={handleClose}
              >
                Cancel
              </Button>
              <Button
                variant="contained"
                color="primary"
                disabled={!selectedFile}
                onClick={handleUpload}
              >
                Upload
              </Button>
            </>
          )}

          {uploadStep === 'complete' && (
            <Button variant="contained" color="primary" onClick={handleClose}>
              Done
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
};

export default UploadResourceModal;
