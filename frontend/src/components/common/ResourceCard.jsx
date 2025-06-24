// Updated on 2024-06-28 - Created component for displaying lesson resources consistently

import React from 'react';
import Card from './Card';
import Badge from './Badge';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

/**
 * ResourceCard component to display lesson resources
 * @param {Object} props
 * @param {Object} props.resource - The resource object
 */
const ResourceCard = ({ resource }) => {
  const navigate = useNavigate();
  const { isAuthenticated, getAccessLevel } = useAuth();
  const userAccessLevel = getAccessLevel();

  // Determine if the user can access this resource
  const canAccess =
    isAuthenticated && (!resource.premium || userAccessLevel === 'advanced');

  // Helper function to render the appropriate icon
  const renderResourceIcon = type => {
    switch (type) {
      case 'document':
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
            />
          </svg>
        );
      case 'video':
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
        );
      case 'link':
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
            />
          </svg>
        );
      case 'code':
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
            />
          </svg>
        );
      case 'tool':
      default:
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
        );
    }
  };

  const handleResourceAction = () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: window.location.pathname } });
      return;
    }

    if (resource.premium && userAccessLevel !== 'advanced') {
      navigate('/subscription');
      return;
    }

    // Open the resource URL or file in a new tab
    if (resource.url) {
      window.open(resource.url, '_blank', 'noopener,noreferrer');
    } else if (resource.file) {
      window.open(resource.file, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start">
        <div className="mr-3 text-primary-600">
          {renderResourceIcon(resource.type)}
        </div>
        <div>
          <h4 className="font-medium text-primary-800 mb-1">
            {resource.title}
          </h4>
          {resource.description && (
            <p className="text-sm text-gray-600 mb-2">{resource.description}</p>
          )}

          {/* Show premium badge if applicable */}
          {resource.premium && (
            <Badge variant="warning" className="mb-2">
              Premium Resource
            </Badge>
          )}

          {/* Resource action button */}
          <div className="mt-2">
            <button
              onClick={handleResourceAction}
              className={`text-sm font-medium flex items-center ${
                canAccess
                  ? 'text-primary-600 hover:text-primary-800'
                  : 'text-gray-500 cursor-default'
              }`}
              disabled={!canAccess}
            >
              {!isAuthenticated ? (
                'Sign in to access'
              ) : resource.premium && userAccessLevel !== 'advanced' ? (
                'Upgrade to access'
              ) : resource.file ? (
                <>
                  Download
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 ml-1"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </>
              ) : (
                <>
                  Visit Resource
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 ml-1"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                    <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ResourceCard;
