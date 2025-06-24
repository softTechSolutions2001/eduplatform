import {
  DocumentTextIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  XMarkIcon,
} from '@heroicons/react/24/solid';
import React from 'react';
import { Badge, Button, Card } from '../../../components/common';
import { useAIBuilderStore } from '../../store/aiBuilderStore';

const ContentEditor = ({ content, lessonId, onSave, onCancel }) => {
  const { generateContent, isGenerating } = useAIBuilderStore();
  const [editingContent, setEditingContent] = React.useState(content || '');
  const [contentBlocks, setContentBlocks] = React.useState([]);
  const [selectedBlockType, setSelectedBlockType] = React.useState('text');
  const [isEditing, setIsEditing] = React.useState(false);

  React.useEffect(() => {
    // Parse content into blocks for better editing
    if (content) {
      const blocks = parseContentIntoBlocks(content);
      setContentBlocks(blocks);
    }
  }, [content]);

  const parseContentIntoBlocks = content => {
    // Simple content block parser
    const lines = content.split('\n\n');
    return lines
      .map((line, index) => {
        if (line.startsWith('# ')) {
          return {
            id: index,
            type: 'heading',
            content: line.replace('# ', ''),
            level: 1,
          };
        } else if (line.startsWith('## ')) {
          return {
            id: index,
            type: 'heading',
            content: line.replace('## ', ''),
            level: 2,
          };
        } else if (line.startsWith('### ')) {
          return {
            id: index,
            type: 'heading',
            content: line.replace('### ', ''),
            level: 3,
          };
        } else if (line.includes('```')) {
          return {
            id: index,
            type: 'code',
            content: line.replace(/```\w*\n?|\n?```/g, ''),
          };
        } else if (
          line.trim().startsWith('- ') ||
          line.trim().startsWith('* ')
        ) {
          return { id: index, type: 'list', content: line };
        } else if (line.trim().length > 0) {
          return { id: index, type: 'paragraph', content: line };
        }
        return null;
      })
      .filter(Boolean);
  };

  const blockTypesToContent = blocks => {
    return blocks
      .map(block => {
        switch (block.type) {
          case 'heading':
            const prefix = '#'.repeat(block.level || 1);
            return `${prefix} ${block.content}`;
          case 'code':
            return `\`\`\`\n${block.content}\n\`\`\``;
          case 'list':
            return block.content;
          case 'paragraph':
          default:
            return block.content;
        }
      })
      .join('\n\n');
  };

  const handleSave = () => {
    const finalContent = isEditing
      ? blockTypesToContent(contentBlocks)
      : editingContent;
    onSave(finalContent);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditingContent(content || '');
    setContentBlocks(parseContentIntoBlocks(content || ''));
    setIsEditing(false);
    onCancel?.();
  };

  const addContentBlock = (type, id = Date.now(), initialContent = null) => {
    const newBlock = {
      id: id,
      type,
      content: initialContent || getDefaultContentForType(type),
    };
    setContentBlocks([...contentBlocks, newBlock]);
    return id;
  };

  const getDefaultContentForType = type => {
    switch (type) {
      case 'heading':
        return 'New Heading';
      case 'paragraph':
        return 'Enter your content here...';
      case 'list':
        return '- List item 1\n- List item 2\n- List item 3';
      case 'code':
        return 'console.log("Hello, World!");';
      default:
        return '';
    }
  };

  const updateBlock = (blockId, newContent) => {
    setContentBlocks(blocks =>
      blocks.map(block =>
        block.id === blockId ? { ...block, content: newContent } : block
      )
    );
  };

  const removeBlock = blockId => {
    setContentBlocks(blocks => blocks.filter(block => block.id !== blockId));
  };

  const moveBlock = (blockId, direction) => {
    const currentIndex = contentBlocks.findIndex(block => block.id === blockId);
    if (
      (direction === 'up' && currentIndex === 0) ||
      (direction === 'down' && currentIndex === contentBlocks.length - 1)
    ) {
      return;
    }

    const newBlocks = [...contentBlocks];
    const targetIndex =
      direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    [newBlocks[currentIndex], newBlocks[targetIndex]] = [
      newBlocks[targetIndex],
      newBlocks[currentIndex],
    ];
    setContentBlocks(newBlocks);
  };

  const generateAIContent = async (blockType, prompt) => {
    try {
      // Create block with loading state first
      const tempId = Date.now();
      addContentBlock(blockType, tempId, '⌛ Generating...');

      const generatedContent = await generateContent({
        type: 'lesson-content',
        context: {
          lessonId,
          blockType,
          prompt,
        },
      });

      if (generatedContent) {
        // Update the existing block with the generated content
        updateBlock(tempId, generatedContent);
      }
    } catch (error) {
      console.error('Failed to generate content:', error);
    }
  };

  const renderBlockEditor = block => {
    switch (block.type) {
      case 'heading':
        return (
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <select
                value={block.level || 1}
                onChange={e =>
                  updateBlock(block.id, {
                    ...block,
                    level: parseInt(e.target.value),
                  })
                }
                className="text-xs border rounded px-2 py-1"
              >
                <option value={1}>H1</option>
                <option value={2}>H2</option>
                <option value={3}>H3</option>
              </select>
            </div>
            <input
              type="text"
              value={block.content}
              onChange={e => updateBlock(block.id, e.target.value)}
              className="w-full text-lg font-bold border-none focus:ring-0 p-0"
              placeholder="Enter heading..."
            />
          </div>
        );

      case 'code':
        return (
          <textarea
            value={block.content}
            onChange={e => updateBlock(block.id, e.target.value)}
            className="w-full font-mono text-sm bg-gray-100 border rounded p-3 min-h-32"
            placeholder="Enter code..."
          />
        );

      case 'list':
        return (
          <textarea
            value={block.content}
            onChange={e => updateBlock(block.id, e.target.value)}
            className="w-full border rounded p-3 min-h-24"
            placeholder="- List item 1&#10;- List item 2"
          />
        );

      case 'paragraph':
      default:
        return (
          <textarea
            value={block.content}
            onChange={e => updateBlock(block.id, e.target.value)}
            className="w-full border rounded p-3 min-h-32"
            placeholder="Enter your content..."
          />
        );
    }
  };

  const renderBlockPreview = block => {
    switch (block.type) {
      case 'heading':
        const HeadingTag = `h${block.level || 1}`;
        const headingClasses = {
          1: 'text-2xl font-bold',
          2: 'text-xl font-semibold',
          3: 'text-lg font-medium',
        };
        return React.createElement(
          HeadingTag,
          { className: headingClasses[block.level || 1] },
          block.content
        );

      case 'code':
        return (
          <pre className="bg-gray-100 rounded p-3 overflow-x-auto">
            <code>{block.content}</code>
          </pre>
        );

      case 'list':
        return (
          <div className="space-y-1">
            {block.content.split('\n').map((item, index) => (
              <div key={index} className="flex items-start space-x-2">
                <span className="text-gray-400 mt-1">•</span>
                <span>{item.replace(/^[-*]\s*/, '')}</span>
              </div>
            ))}
          </div>
        );

      case 'paragraph':
      default:
        return <p className="text-gray-700 leading-relaxed">{block.content}</p>;
    }
  };

  if (!isEditing && contentBlocks.length === 0 && !content) {
    return (
      <Card className="p-6">
        <div className="text-center">
          <DocumentTextIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Content Yet
          </h3>
          <p className="text-gray-500 mb-4">
            Start creating engaging lesson content.
          </p>
          <Button variant="primary" onClick={() => setIsEditing(true)}>
            <PencilIcon className="h-4 w-4 mr-2" />
            Start Writing
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Content Editor</h3>
        <div className="flex items-center space-x-3">
          {isEditing ? (
            <>
              <Button variant="outline" onClick={handleCancel}>
                <XMarkIcon className="h-4 w-4 mr-2" />
                Cancel
              </Button>
              <Button variant="primary" onClick={handleSave}>
                <SaveIcon className="h-4 w-4 mr-2" />
                Save
              </Button>
            </>
          ) : (
            <>
              <Button variant="outline" onClick={() => setIsEditing(true)}>
                <PencilIcon className="h-4 w-4 mr-2" />
                Edit
              </Button>
              <Button variant="outline">
                <EyeIcon className="h-4 w-4 mr-2" />
                Preview
              </Button>
            </>
          )}
        </div>
      </div>

      {isEditing ? (
        <div className="space-y-6">
          {/* Add Content Block Controls */}
          <div className="flex flex-wrap gap-2 p-4 bg-gray-50 rounded-lg">
            <span className="text-sm font-medium text-gray-700 mr-3">
              Add Content:
            </span>
            {[
              { type: 'paragraph', label: 'Paragraph', icon: DocumentTextIcon },
              { type: 'heading', label: 'Heading', icon: DocumentTextIcon },
              { type: 'list', label: 'List', icon: DocumentTextIcon },
              { type: 'code', label: 'Code', icon: DocumentTextIcon },
            ].map(({ type, label, icon: Icon }) => (
              <Button
                key={type}
                variant="outline"
                size="sm"
                onClick={() => addContentBlock(type)}
              >
                <Icon className="h-4 w-4 mr-1" />
                {label}
              </Button>
            ))}
          </div>

          {/* Content Blocks */}
          <div className="space-y-4">
            {contentBlocks.map((block, index) => (
              <div key={block.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <Badge variant="gray" size="sm" className="capitalize">
                    {block.type}
                  </Badge>
                  <div className="flex items-center space-x-2">
                    {index > 0 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => moveBlock(block.id, 'up')}
                      >
                        ↑
                      </Button>
                    )}
                    {index < contentBlocks.length - 1 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => moveBlock(block.id, 'down')}
                      >
                        ↓
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeBlock(block.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                {renderBlockEditor(block)}
              </div>
            ))}
          </div>

          {contentBlocks.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p>
                No content blocks added yet. Use the controls above to start
                creating content.
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {contentBlocks.map(block => (
            <div key={block.id}>{renderBlockPreview(block)}</div>
          ))}
        </div>
      )}

      {/* AI Generation Section */}
      {isEditing && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-3">
            AI Content Generation
          </h4>
          <div className="flex items-center space-x-3">
            <select
              value={selectedBlockType}
              onChange={e => setSelectedBlockType(e.target.value)}
              className="border rounded px-3 py-2 text-sm"
            >
              <option value="paragraph">Paragraph</option>
              <option value="heading">Heading</option>
              <option value="list">List</option>
              <option value="code">Code Example</option>
            </select>
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                generateAIContent(selectedBlockType, 'Generate content')
              }
              disabled={isGenerating}
            >
              {isGenerating ? 'Generating...' : 'Generate with AI'}
            </Button>
          </div>
        </div>
      )}
    </Card>
  );
};

export default ContentEditor;
