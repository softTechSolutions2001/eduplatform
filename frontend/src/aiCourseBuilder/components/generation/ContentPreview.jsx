/**
 * Content Preview - AI Generation Preview Component
 * Version: 1.0.0
 * Author: GitHub Copilot
 *
 * Displays real-time preview of AI-generated content during the creation process.
 */

import { useEffect, useState } from 'react';
import Card from '../../../components/common/Card';
import { useAIBuilderStore } from '../../store/aiBuilderStore';

const ContentPreview = ({ title, description, showSkeleton = true }) => {
  const { generationStatus, currentContent, isGenerating } =
    useAIBuilderStore();
  const [displayedContent, setDisplayedContent] = useState('');

  // Simulate typewriter effect for generated content
  useEffect(() => {
    if (currentContent) {
      let index = 1; // Start from 1 to avoid skipping first character
      const typeContent = () => {
        setDisplayedContent(currentContent.slice(0, index));
        index++;
        if (index > currentContent.length) {
          clearInterval(interval);
        }
      };

      const interval = setInterval(typeContent, 50);
      return () => clearInterval(interval);
    }
  }, [currentContent]);

  return (
    <Card className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600">{description}</p>
        </div>

        {isGenerating && (
          <div className="flex items-center space-x-2 text-blue-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span className="text-sm">Generating...</span>
          </div>
        )}
      </div>

      {/* Content Preview */}
      <div className="space-y-4">
        {showSkeleton && isGenerating && !displayedContent ? (
          <SkeletonLoader />
        ) : (
          <div className="prose max-w-none">
            {displayedContent && (
              <div className="whitespace-pre-line text-gray-700">
                {displayedContent}
                {isGenerating && <span className="animate-pulse">|</span>}
              </div>
            )}
          </div>
        )}

        {/* Status Message */}
        {generationStatus && (
          <div className="text-sm text-blue-600 font-medium">
            {generationStatus}
          </div>
        )}
      </div>

      {/* Generation Tips */}
      {isGenerating && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="text-sm font-medium text-blue-900 mb-2">
            💡 While AI generates your content:
          </h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Content is tailored to your learning objectives</li>
            <li>• Each module builds upon previous knowledge</li>
            <li>• Interactive elements are automatically included</li>
            <li>• You can edit and customize everything later</li>
          </ul>
        </div>
      )}
    </Card>
  );
};

// Skeleton Loader Component
const SkeletonLoader = () => (
  <div className="space-y-4 animate-pulse">
    {/* Title skeleton */}
    <div className="h-6 bg-gray-200 rounded w-3/4"></div>

    {/* Paragraph skeletons */}
    <div className="space-y-2">
      <div className="h-4 bg-gray-200 rounded w-full"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
      <div className="h-4 bg-gray-200 rounded w-4/5"></div>
    </div>

    {/* List skeleton */}
    <div className="space-y-2 ml-4">
      <div className="h-3 bg-gray-200 rounded w-2/3"></div>
      <div className="h-3 bg-gray-200 rounded w-3/4"></div>
      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
    </div>

    {/* Another paragraph */}
    <div className="space-y-2">
      <div className="h-4 bg-gray-200 rounded w-full"></div>
      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
    </div>
  </div>
);

export default ContentPreview;
