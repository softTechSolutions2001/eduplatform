/**
 * Mock responses for AI Course Builder API
 * Used when useMockResponses is true in development/testing
 */

const mockResponses = {
  // Course outline generation
  outline: {
    modules: [
      {
        title: 'Introduction to Web Development',
        description:
          'Learn the fundamentals of web development including HTML, CSS, and basic JavaScript',
        order: 1,
        duration_minutes: 180,
        estimatedDuration: '3 hours',
        objectives: [
          'Understand the structure of web pages using HTML',
          'Apply basic styling with CSS',
          'Implement simple interactivity with JavaScript',
        ],
        lessons: [
          {
            title: 'HTML Fundamentals',
            description: 'Learn HTML structure, elements, and semantic markup',
            type: 'video',
            duration_minutes: 45,
            estimatedDuration: '45 minutes',
            accessLevel: 'guest',
          },
          {
            title: 'CSS Styling Basics',
            description:
              'Introduction to CSS selectors, properties, and layout',
            type: 'video',
            duration_minutes: 60,
            estimatedDuration: '1 hour',
            accessLevel: 'registered',
          },
          {
            title: 'JavaScript Fundamentals',
            description: 'Basic JavaScript concepts and DOM manipulation',
            type: 'interactive',
            duration_minutes: 75,
            estimatedDuration: '1.25 hours',
            accessLevel: 'premium',
          },
        ],
      },
      {
        title: 'Advanced Web Technologies',
        description: 'Explore modern web development frameworks and tools',
        order: 2,
        duration_minutes: 240,
        estimatedDuration: '4 hours',
        objectives: [
          'Build responsive layouts with modern CSS',
          'Understand component-based architecture',
          'Deploy web applications',
        ],
        lessons: [
          {
            title: 'Responsive Design',
            description: 'Create layouts that work on all devices',
            type: 'video',
            duration_minutes: 90,
            estimatedDuration: '1.5 hours',
            accessLevel: 'registered',
          },
          {
            title: 'Introduction to Frameworks',
            description: 'Overview of popular frontend frameworks',
            type: 'reading',
            duration_minutes: 60,
            estimatedDuration: '1 hour',
            accessLevel: 'premium',
          },
          {
            title: 'Project: Build a Portfolio Site',
            description: 'Apply your skills to create a personal portfolio',
            type: 'assignment',
            duration_minutes: 90,
            estimatedDuration: '1.5 hours',
            accessLevel: 'premium',
          },
        ],
      },
    ],
    assessmentStrategy:
      'Formative assessments through hands-on exercises and a final portfolio project',
    prerequisites: ['Basic computer literacy', 'Understanding of file systems'],
    estimatedTotalDuration: '2-3 weeks',
    courseStructure: {
      totalModules: 2,
      totalLessons: 6,
      assessmentTypes: ['quiz', 'assignment', 'project'],
    },
  },

  // Module content generation
  module: {
    lessons: [
      {
        title: 'Introduction to HTML',
        description:
          'Comprehensive introduction to HTML structure and elements',
        content:
          '# Introduction to HTML\n\nHTML (HyperText Markup Language) is the standard markup language for creating web pages...',
        type: 'video',
        duration_minutes: 45,
        estimatedDuration: '45 minutes',
        accessLevel: 'guest',
        objectives: ['Understand HTML structure', 'Create basic HTML elements'],
        keyPoints: ['HTML tags', 'Document structure', 'Semantic elements'],
        activities: [
          {
            type: 'exercise',
            title: 'Create Your First HTML Page',
            description:
              'Build a simple HTML page with headers, paragraphs, and links',
            estimatedTime: '20 minutes',
          },
        ],
        resources: [
          {
            title: 'HTML Reference Guide',
            type: 'article',
            url: 'placeholder-url',
            description: 'Complete HTML element reference',
          },
        ],
      },
    ],
    objectives: ['Master HTML fundamentals', 'Create structured web content'],
    assessments: [
      {
        type: 'quiz',
        title: 'HTML Knowledge Check',
        description: 'Test your understanding of HTML basics',
        estimatedTime: '15 minutes',
        pointsValue: 20,
        rubric: 'Multiple choice questions covering HTML structure and syntax',
      },
    ],
    resources: [
      {
        title: 'HTML Tutorial Series',
        type: 'video',
        description: 'Comprehensive video tutorials on HTML',
        url: 'placeholder-url',
        isRequired: true,
      },
    ],
  },

  // Lesson content generation
  lesson: {
    content:
      '# CSS Fundamentals\n\n## Introduction\n\nCSS (Cascading Style Sheets) is used to style HTML elements and control the layout of web pages...\n\n## Key Concepts\n\n- Selectors\n- Properties\n- Values\n- Cascading\n- Inheritance',
    objectives: [
      'Apply CSS styling to HTML elements',
      'Understand the CSS box model',
      'Create responsive layouts',
    ],
    keyTakeaways: [
      'CSS controls presentation',
      'Selectors target elements',
      'Properties define styling',
    ],
    activities: [
      {
        type: 'exercise',
        title: 'Style a Web Page',
        instructions:
          'Apply CSS styling to the HTML page created in the previous lesson',
        estimatedTime: '30 minutes',
        materials: ['Code editor', 'Web browser'],
      },
    ],
    assessments: [
      {
        type: 'formative',
        format: 'quiz',
        questions: ['What is CSS?', 'How do you apply styles to HTML?'],
        rubric: 'Understanding of CSS basics',
      },
    ],
    resources: [
      {
        title: 'CSS Reference',
        type: 'website',
        description: 'Complete CSS property reference',
        url: 'placeholder-url',
        isRequired: false,
      },
    ],
  },

  // Content enhancement
  enhancement: {
    enhancedContent:
      'Enhanced version of the original content with improved engagement, accessibility, or depth',
    improvements: [
      'Added interactive examples',
      'Included visual diagrams',
      'Enhanced accessibility features',
      'Expanded explanations',
    ],
    suggestions: [
      'Consider adding video demonstrations',
      'Include more hands-on exercises',
      'Add checkpoint quizzes',
    ],
  },

  // Assessment generation
  assessment: {
    questions: [
      {
        type: 'multiple_choice',
        question: 'What does HTML stand for?',
        options: [
          'HyperText Markup Language',
          'High Tech Modern Language',
          'Home Tool Markup Language',
          'Hyperlink and Text Markup Language',
        ],
        correctAnswer: 'HyperText Markup Language',
        explanation:
          'HTML stands for HyperText Markup Language, which is the standard markup language for creating web pages.',
        difficulty: 'easy',
        learningObjective: 'Understand basic web development terminology',
      },
      {
        type: 'short_answer',
        question: 'Explain the difference between HTML and CSS.',
        keywords: ['structure', 'styling', 'content', 'presentation'],
        sampleAnswer:
          'HTML provides the structure and content of web pages, while CSS controls the styling and presentation.',
        difficulty: 'medium',
        learningObjective:
          'Distinguish between content and presentation layers',
      },
    ],
    rubric: {
      criteria: [
        {
          name: 'Understanding',
          description: 'Demonstrates clear understanding of concepts',
          levels: {
            excellent: '90-100 points - Complete understanding with examples',
            good: '80-89 points - Good understanding with minor gaps',
            satisfactory: '70-79 points - Basic understanding',
            needs_improvement: 'Below 70 points - Limited understanding',
          },
        },
      ],
    },
    estimatedTime: '20 minutes',
  },

  // Generic response for unknown types
  generic: {
    success: true,
    message: 'Mock response generated successfully',
    data: {
      content: 'Generic mock content for testing purposes',
      timestamp: new Date().toISOString(),
    },
  },
};

export default mockResponses;
