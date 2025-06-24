/**
 * Objectives Input - Learning Objectives Management Component
 * Version: 1.0.0
 * Author: GitHub Copilot
 *
 * Advanced interface for defining and managing course learning objectives
 * with AI-powered suggestions and validation.
 */

import { useEffect, useState } from 'react';
import Alert from '../../../components/common/Alert';
import Button from '../../../components/common/Button';
import { useAIGeneration } from '../../hooks/useAIGeneration';

const ObjectivesInput = ({ data, onChange, errors }) => {
  const [localData, setLocalData] = useState({
    objectives: [],
    skillLevel: 'beginner',
    targetSkills: [],
    assessmentMethods: [],
    ...data,
  });

  const [newObjective, setNewObjective] = useState('');
  const [suggestedObjectives, setSuggestedObjectives] = useState([]);
  const [isGeneratingSuggestions, setIsGeneratingSuggestions] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('knowledge');

  const { generateObjectiveSuggestions } = useAIGeneration();

  // Objective categories based on Bloom's Taxonomy - updated version
  const objectiveCategories = [
    {
      id: 'remember',
      label: 'Remember',
      description: 'Recall facts and basic concepts',
    },
    {
      id: 'understand',
      label: 'Understand',
      description: 'Explain ideas or concepts',
    },
    {
      id: 'apply',
      label: 'Apply',
      description: 'Use information in new situations',
    },
    {
      id: 'analyze',
      label: 'Analyze',
      description: 'Draw connections among ideas',
    },
    {
      id: 'evaluate',
      label: 'Evaluate',
      description: 'Justify a stand or decision',
    },
    {
      id: 'create',
      label: 'Create',
      description: 'Produce new or original work',
    },
  ];

  // Action verbs for different categories - updated to match Bloom's updated taxonomy
  const actionVerbs = {
    remember: ['define', 'list', 'identify', 'describe', 'recall', 'recognize'],
    understand: ['explain', 'summarize', 'interpret', 'classify', 'compare'],
    apply: ['apply', 'demonstrate', 'solve', 'implement', 'execute'],
    analyze: [
      'analyze',
      'examine',
      'investigate',
      'differentiate',
      'categorize',
    ],
    evaluate: ['evaluate', 'assess', 'critique', 'judge', 'recommend'],
    create: ['create', 'design', 'develop', 'construct', 'formulate'],
  };

  // Update parent component when local data changes
  useEffect(() => {
    onChange(localData);
  }, [localData, onChange]);

  // Generate AI suggestions for objectives
  const handleGenerateSuggestions = async () => {
    try {
      setIsGeneratingSuggestions(true);
      const suggestions = await generateObjectiveSuggestions({
        category: selectedCategory,
        existingObjectives: localData.objectives,
        skillLevel: localData.skillLevel,
      });
      setSuggestedObjectives(suggestions);
    } catch (error) {
      console.error('Failed to generate objective suggestions:', error);
    } finally {
      setIsGeneratingSuggestions(false);
    }
  };

  // Add new objective
  const handleAddObjective = () => {
    if (!newObjective.trim()) return;

    const objective = {
      id: Date.now(),
      text: newObjective.trim(),
      category: selectedCategory,
      priority: 'medium',
    };

    const updatedData = {
      ...localData,
      objectives: [...localData.objectives, objective],
    };

    setLocalData(updatedData);
    setNewObjective('');
  };

  // Remove objective
  const handleRemoveObjective = objectiveId => {
    const updatedData = {
      ...localData,
      objectives: localData.objectives.filter(obj => obj.id !== objectiveId),
    };
    setLocalData(updatedData);
  };

  // Add suggested objective
  const handleAddSuggestion = suggestion => {
    const objective = {
      id: Date.now(),
      text: suggestion,
      category: selectedCategory,
      priority: 'medium',
    };

    const updatedData = {
      ...localData,
      objectives: [...localData.objectives, objective],
    };

    setLocalData(updatedData);
    setSuggestedObjectives(suggestedObjectives.filter(s => s !== suggestion));
  };

  // Update objective priority
  const handleUpdatePriority = (objectiveId, priority) => {
    const updatedData = {
      ...localData,
      objectives: localData.objectives.map(obj =>
        obj.id === objectiveId ? { ...obj, priority } : obj
      ),
    };
    setLocalData(updatedData);
  };

  // Generate objective template
  const generateObjectiveTemplate = () => {
    const verbs = actionVerbs[selectedCategory];
    const randomVerb = verbs[Math.floor(Math.random() * verbs.length)];
    const template = `Students will be able to ${randomVerb} `;
    setNewObjective(template);
  };

  return (
    <div className="space-y-6">
      {/* Instructions */}
      <Alert type="info">
        <div>
          <h4 className="font-medium">Define Learning Objectives</h4>
          <p className="text-sm mt-1">
            Clear learning objectives help AI generate better course content.
            Use action verbs and be specific about what students will achieve.
          </p>
        </div>
      </Alert>

      {/* Objective Categories */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Objective Category (Bloom's Taxonomy)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {objectiveCategories.map(category => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`p-3 text-left border rounded-lg transition-colors ${
                selectedCategory === category.id
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="font-medium text-sm">{category.label}</div>
              <div className="text-xs text-gray-600 mt-1">
                {category.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Add New Objective */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Add Learning Objective
        </label>
        <div className="flex space-x-2">
          <div className="flex-1">
            <textarea
              value={newObjective}
              onChange={e => setNewObjective(e.target.value)}
              placeholder="Students will be able to..."
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div className="flex flex-col space-y-2">
            <Button
              variant="outline"
              size="small"
              onClick={generateObjectiveTemplate}
              className="whitespace-nowrap"
            >
              Template
            </Button>
            <Button
              variant="primary"
              size="small"
              onClick={handleAddObjective}
              disabled={!newObjective.trim()}
              className="whitespace-nowrap"
            >
              Add
            </Button>
          </div>
        </div>

        {/* Action Verbs Helper */}
        <div className="mt-2">
          <p className="text-xs text-gray-600 mb-1">
            Suggested verbs for{' '}
            {objectiveCategories.find(c => c.id === selectedCategory)?.label}:
          </p>
          <div className="flex flex-wrap gap-1">
            {actionVerbs[selectedCategory].map(verb => (
              <button
                key={verb}
                onClick={() => setNewObjective(prev => prev + verb + ' ')}
                className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded text-gray-700"
              >
                {verb}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* AI Suggestions */}
      <div>
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-sm font-medium text-gray-700">AI Suggestions</h3>
          <Button
            variant="outline"
            size="small"
            onClick={handleGenerateSuggestions}
            loading={isGeneratingSuggestions}
            disabled={isGeneratingSuggestions}
          >
            Generate Suggestions
          </Button>
        </div>

        {suggestedObjectives.length > 0 && (
          <div className="space-y-2">
            {suggestedObjectives.map((suggestion, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg"
              >
                <span className="text-sm text-blue-900">{suggestion}</span>
                <Button
                  variant="text"
                  size="small"
                  onClick={() => handleAddSuggestion(suggestion)}
                  className="text-blue-600 hover:text-blue-800"
                >
                  Add
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Current Objectives */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">
          Learning Objectives ({localData.objectives.length})
        </h3>

        {errors.objectives && (
          <Alert type="error" className="mb-3">
            {errors.objectives}
          </Alert>
        )}

        {localData.objectives.length === 0 ? (
          <div className="text-center py-8 bg-gray-50 rounded-lg">
            <p className="text-gray-500">No learning objectives added yet.</p>
            <p className="text-sm text-gray-400 mt-1">
              Add objectives to help AI generate better course content.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {localData.objectives.map((objective, index) => (
              <div
                key={objective.id}
                className="flex items-start justify-between p-4 bg-white border border-gray-200 rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-sm font-medium text-gray-900">
                      #{index + 1}
                    </span>
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        objective.category === 'knowledge'
                          ? 'bg-blue-100 text-blue-800'
                          : objective.category === 'comprehension'
                            ? 'bg-green-100 text-green-800'
                            : objective.category === 'application'
                              ? 'bg-yellow-100 text-yellow-800'
                              : objective.category === 'analysis'
                                ? 'bg-purple-100 text-purple-800'
                                : objective.category === 'synthesis'
                                  ? 'bg-pink-100 text-pink-800'
                                  : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {
                        objectiveCategories.find(
                          c => c.id === objective.category
                        )?.label
                      }
                    </span>
                  </div>
                  <p className="text-gray-700">{objective.text}</p>

                  {/* Priority Selection */}
                  <div className="mt-2">
                    <select
                      value={objective.priority}
                      onChange={e =>
                        handleUpdatePriority(objective.id, e.target.value)
                      }
                      className="text-xs border border-gray-300 rounded px-2 py-1"
                    >
                      <option value="low">Low Priority</option>
                      <option value="medium">Medium Priority</option>
                      <option value="high">High Priority</option>
                    </select>
                  </div>
                </div>

                <Button
                  variant="text"
                  size="small"
                  onClick={() => handleRemoveObjective(objective.id)}
                  className="text-red-600 hover:text-red-800 ml-3"
                >
                  Remove
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Objective Summary */}
      {localData.objectives.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-2">Objective Summary</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            {objectiveCategories.map(category => {
              const count = localData.objectives.filter(
                obj => obj.category === category.id
              ).length;
              return (
                <div key={category.id} className="flex justify-between">
                  <span className="text-gray-600">{category.label}:</span>
                  <span className="font-medium">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ObjectivesInput;
