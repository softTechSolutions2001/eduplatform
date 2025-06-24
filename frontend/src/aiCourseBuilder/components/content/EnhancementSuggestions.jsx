import {
  ArrowRightIcon,
  CheckIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  LightBulbIcon,
  SparklesIcon,
  XMarkIcon,
} from '@heroicons/react/24/solid';
import React from 'react';
import { Badge, Button, Card } from '../../../components/common';
import { useAIBuilderStore } from '../../store/aiBuilderStore';

const EnhancementSuggestions = ({
  content,
  contentType = 'lesson',
  onApplySuggestion,
  onDismiss,
}) => {
  const { generateContent, isGenerating } = useAIBuilderStore();
  const [suggestions, setSuggestions] = React.useState([]);
  const [loading, setLoading] = React.useState(false);
  const [appliedSuggestions, setAppliedSuggestions] = React.useState(new Set());

  React.useEffect(() => {
    if (content) {
      generateSuggestions();
    }
  }, [content]);

  const generateSuggestions = async () => {
    setLoading(true);
    try {
      const response = await generateContent({
        type: 'enhancement-suggestions',
        context: {
          content,
          contentType,
          criteria: [
            'clarity',
            'engagement',
            'learning_objectives',
            'structure',
            'accessibility',
            'interactivity',
          ],
        },
      });

      if (response && response.suggestions) {
        setSuggestions(response.suggestions);
      } else {
        // Fallback to mock suggestions for demo
        setSuggestions(generateMockSuggestions());
      }
    } catch (error) {
      console.error('Failed to generate suggestions:', error);
      setSuggestions(generateMockSuggestions());
    } finally {
      setLoading(false);
    }
  };

  const generateMockSuggestions = () => {
    const mockSuggestions = [
      {
        id: 1,
        type: 'engagement',
        priority: 'high',
        title: 'Add Interactive Elements',
        description:
          'Consider adding questions, polls, or interactive exercises to boost engagement.',
        suggestion: 'Add a "Knowledge Check" quiz after the main concepts.',
        implementation:
          'Insert interactive quiz components at strategic points.',
        impact: 'High - Increases retention and engagement by 40%',
      },
      {
        id: 2,
        type: 'clarity',
        priority: 'medium',
        title: 'Improve Content Structure',
        description:
          'Break down complex paragraphs into digestible chunks with clear headings.',
        suggestion:
          'Use bullet points and subheadings to organize information better.',
        implementation:
          'Restructure content with H3 headings and bullet lists.',
        impact: 'Medium - Improves comprehension and readability',
      },
      {
        id: 3,
        type: 'learning_objectives',
        priority: 'medium',
        title: 'Align with Learning Objectives',
        description:
          'Ensure content directly supports the stated learning objectives.',
        suggestion:
          'Add specific examples that demonstrate each learning objective.',
        implementation: 'Include practical examples and case studies.',
        impact: 'Medium - Better objective achievement tracking',
      },
      {
        id: 4,
        type: 'accessibility',
        priority: 'low',
        title: 'Enhance Accessibility',
        description:
          'Add alt text for images and improve content for screen readers.',
        suggestion: 'Include descriptive text for visual elements.',
        implementation: 'Add image descriptions and audio transcripts.',
        impact: 'Low - Improves accessibility for diverse learners',
      },
    ];

    return mockSuggestions.slice(0, Math.floor(Math.random() * 3) + 2);
  };

  const applySuggestion = suggestion => {
    setAppliedSuggestions(prev => new Set(prev).add(suggestion.id));
    onApplySuggestion?.(suggestion);
  };

  const dismissSuggestion = suggestionId => {
    setSuggestions(prev => prev.filter(s => s.id !== suggestionId));
    onDismiss?.(suggestionId);
  };

  const getPriorityColor = priority => {
    switch (priority) {
      case 'high':
        return 'red';
      case 'medium':
        return 'yellow';
      case 'low':
        return 'green';
      default:
        return 'gray';
    }
  };

  const getTypeIcon = type => {
    switch (type) {
      case 'engagement':
        return <SparklesIcon className="h-5 w-5" />;
      case 'clarity':
        return <LightBulbIcon className="h-5 w-5" />;
      case 'learning_objectives':
        return <CheckIcon className="h-5 w-5" />;
      case 'accessibility':
        return <InformationCircleIcon className="h-5 w-5" />;
      case 'structure':
        return <ExclamationTriangleIcon className="h-5 w-5" />;
      default:
        return <LightBulbIcon className="h-5 w-5" />;
    }
  };

  const getTypeColor = type => {
    switch (type) {
      case 'engagement':
        return 'purple';
      case 'clarity':
        return 'blue';
      case 'learning_objectives':
        return 'green';
      case 'accessibility':
        return 'orange';
      case 'structure':
        return 'gray';
      default:
        return 'gray';
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="flex items-center space-x-3">
            <div className="h-6 w-6 bg-gray-300 rounded"></div>
            <div className="h-4 bg-gray-300 rounded w-1/3"></div>
          </div>
          {[1, 2, 3].map(i => (
            <div key={i} className="space-y-3">
              <div className="h-4 bg-gray-300 rounded w-3/4"></div>
              <div className="h-3 bg-gray-300 rounded w-full"></div>
              <div className="h-3 bg-gray-300 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (!suggestions || suggestions.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center">
          <CheckIcon className="h-12 w-12 mx-auto mb-4 text-green-500" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Content Looks Great!
          </h3>
          <p className="text-gray-500 mb-4">
            No enhancement suggestions at this time.
          </p>
          <Button
            variant="outline"
            onClick={generateSuggestions}
            disabled={loading}
          >
            <SparklesIcon className="h-4 w-4 mr-2" />
            Re-analyze Content
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <SparklesIcon className="h-6 w-6 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            Enhancement Suggestions
          </h3>
          <Badge variant="purple" size="sm">
            {suggestions.length} suggestions
          </Badge>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={generateSuggestions}
          disabled={loading}
        >
          Refresh
        </Button>
      </div>

      <div className="space-y-4">
        {suggestions.map(suggestion => (
          <Card
            key={suggestion.id}
            className="p-4 border-l-4 border-l-gray-200"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                <div
                  className={`p-2 rounded-lg ${suggestion.type === 'engagement' ? 'bg-purple-100' : suggestion.type === 'clarity' ? 'bg-blue-100' : suggestion.type === 'learning_objectives' ? 'bg-green-100' : suggestion.type === 'accessibility' ? 'bg-orange-100' : 'bg-gray-100'}`}
                >
                  <div
                    className={`${suggestion.type === 'engagement' ? 'text-purple-600' : suggestion.type === 'clarity' ? 'text-blue-600' : suggestion.type === 'learning_objectives' ? 'text-green-600' : suggestion.type === 'accessibility' ? 'text-orange-600' : 'text-gray-600'}`}
                  >
                    {getTypeIcon(suggestion.type)}
                  </div>
                </div>

                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="text-base font-medium text-gray-900">
                      {suggestion.title}
                    </h4>
                    <Badge
                      variant={getPriorityColor(suggestion.priority)}
                      size="xs"
                    >
                      {suggestion.priority} priority
                    </Badge>
                    <Badge variant={getTypeColor(suggestion.type)} size="xs">
                      {suggestion.type.replace('_', ' ')}
                    </Badge>
                  </div>

                  <p className="text-sm text-gray-600 mb-3">
                    {suggestion.description}
                  </p>

                  <div className="space-y-2">
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <h5 className="text-xs font-medium text-blue-800 mb-1">
                        Suggestion
                      </h5>
                      <p className="text-sm text-blue-700">
                        {suggestion.suggestion}
                      </p>
                    </div>

                    {suggestion.implementation && (
                      <div className="bg-gray-50 p-3 rounded-lg">
                        <h5 className="text-xs font-medium text-gray-800 mb-1">
                          How to implement
                        </h5>
                        <p className="text-sm text-gray-700">
                          {suggestion.implementation}
                        </p>
                      </div>
                    )}

                    {suggestion.impact && (
                      <div className="bg-green-50 p-3 rounded-lg">
                        <h5 className="text-xs font-medium text-green-800 mb-1">
                          Expected impact
                        </h5>
                        <p className="text-sm text-green-700">
                          {suggestion.impact}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2 ml-4">
                {appliedSuggestions.has(suggestion.id) ? (
                  <Badge
                    variant="green"
                    size="sm"
                    className="flex items-center space-x-1"
                  >
                    <CheckIcon className="h-3 w-3" />
                    <span>Applied</span>
                  </Badge>
                ) : (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => dismissSuggestion(suggestion.id)}
                      className="text-gray-600 hover:text-gray-800"
                    >
                      <XMarkIcon className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => applySuggestion(suggestion)}
                      className="flex items-center space-x-1"
                    >
                      <span>Apply</span>
                      <ArrowRightIcon className="h-3 w-3" />
                    </Button>
                  </>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-lg font-semibold text-red-600">
              {suggestions.filter(s => s.priority === 'high').length}
            </div>
            <div className="text-xs text-gray-600">High Priority</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-yellow-600">
              {suggestions.filter(s => s.priority === 'medium').length}
            </div>
            <div className="text-xs text-gray-600">Medium Priority</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-green-600">
              {appliedSuggestions.size}
            </div>
            <div className="text-xs text-gray-600">Applied</div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="mt-6 flex justify-end space-x-3">
        <Button variant="outline">Export Report</Button>
        <Button variant="primary" disabled={appliedSuggestions.size === 0}>
          Apply All High Priority
        </Button>
      </div>
    </Card>
  );
};

export default EnhancementSuggestions;
