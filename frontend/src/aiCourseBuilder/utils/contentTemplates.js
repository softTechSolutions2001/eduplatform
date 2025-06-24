// Content Templates for AI Course Builder

/**
 * Course outline templates based on different categories and levels
 */
export const COURSE_TEMPLATES = {
  'web-development': {
    beginner: {
      title: 'Introduction to Web Development',
      description: 'Learn the fundamentals of building websites from scratch',
      duration: 40,
      modules: [
        {
          title: 'HTML Fundamentals',
          description: 'Learn the structure and elements of HTML',
          lessons: [
            {
              title: 'HTML Structure and Elements',
              type: 'video',
              duration: 30,
            },
            { title: 'Forms and Input Elements', type: 'video', duration: 25 },
            { title: 'Semantic HTML', type: 'reading', duration: 20 },
            {
              title: 'HTML Practice Exercise',
              type: 'assignment',
              duration: 45,
            },
          ],
        },
        {
          title: 'CSS Styling',
          description: 'Master the art of styling web pages',
          lessons: [
            {
              title: 'CSS Selectors and Properties',
              type: 'video',
              duration: 35,
            },
            { title: 'Layout with Flexbox', type: 'video', duration: 40 },
            { title: 'Responsive Design', type: 'video', duration: 30 },
            { title: 'CSS Grid System', type: 'reading', duration: 25 },
          ],
        },
      ],
    },
    intermediate: {
      title: 'Advanced Web Development',
      description: 'Build dynamic and interactive web applications',
      duration: 80,
      modules: [
        {
          title: 'JavaScript Fundamentals',
          description: 'Master JavaScript programming concepts',
          lessons: [
            { title: 'Variables and Data Types', type: 'video', duration: 30 },
            { title: 'Functions and Scope', type: 'video', duration: 35 },
            { title: 'DOM Manipulation', type: 'video', duration: 40 },
            { title: 'Event Handling', type: 'video', duration: 30 },
          ],
        },
        {
          title: 'Modern JavaScript',
          description: 'ES6+ features and modern development',
          lessons: [
            {
              title: 'Arrow Functions and Destructuring',
              type: 'video',
              duration: 25,
            },
            { title: 'Promises and Async/Await', type: 'video', duration: 35 },
            { title: 'Modules and Classes', type: 'video', duration: 30 },
            { title: 'JavaScript Project', type: 'assignment', duration: 90 },
          ],
        },
      ],
    },
  },
  'data-science': {
    beginner: {
      title: 'Introduction to Data Science',
      description: 'Learn the basics of data analysis and visualization',
      duration: 60,
      modules: [
        {
          title: 'Data Science Fundamentals',
          description: 'Understanding data science workflow and tools',
          lessons: [
            { title: 'What is Data Science?', type: 'video', duration: 20 },
            {
              title: 'Data Science Tools Overview',
              type: 'reading',
              duration: 25,
            },
            {
              title: 'Setting Up Your Environment',
              type: 'video',
              duration: 30,
            },
            { title: 'First Data Analysis', type: 'assignment', duration: 45 },
          ],
        },
      ],
    },
  },
  business: {
    beginner: {
      title: 'Business Fundamentals',
      description: 'Essential business concepts and strategies',
      duration: 50,
      modules: [
        {
          title: 'Business Strategy',
          description: 'Understanding strategic planning and execution',
          lessons: [
            { title: 'Strategic Planning Basics', type: 'video', duration: 25 },
            { title: 'Market Analysis', type: 'reading', duration: 30 },
            { title: 'Competitive Advantage', type: 'video', duration: 25 },
            { title: 'Strategy Case Study', type: 'assignment', duration: 60 },
          ],
        },
      ],
    },
  },
};

/**
 * Learning objectives templates based on Bloom's taxonomy
 */
export const OBJECTIVE_TEMPLATES = {
  remember: [
    'Define key terms and concepts related to {topic}',
    'List the main components of {topic}',
    'Identify the fundamental principles of {topic}',
    'Recall important facts about {topic}',
  ],
  understand: [
    'Explain the relationship between {concept1} and {concept2}',
    'Describe how {topic} works in practice',
    'Summarize the main ideas of {topic}',
    'Interpret data related to {topic}',
  ],
  apply: [
    'Use {tool/method} to solve {type} problems',
    'Implement {technique} in real-world scenarios',
    'Apply {principle} to new situations',
    'Demonstrate proficiency in {skill}',
  ],
  analyze: [
    'Compare and contrast different approaches to {topic}',
    'Analyze the components of {system/process}',
    'Examine the relationship between {elements}',
    'Break down complex {topic} into manageable parts',
  ],
  evaluate: [
    'Assess the effectiveness of {method/approach}',
    'Critique different solutions to {problem}',
    'Judge the quality of {work/product}',
    'Evaluate the pros and cons of {options}',
  ],
  create: [
    'Design a {solution/system} for {problem}',
    'Develop an original {product/plan}',
    'Create a comprehensive {strategy/framework}',
    'Build a functional {application/model}',
  ],
};

/**
 * Content structure templates
 */
export const CONTENT_TEMPLATES = {
  lesson: {
    video: {
      structure: [
        { type: 'introduction', duration: '10%', content: 'Hook and overview' },
        {
          type: 'main-content',
          duration: '70%',
          content: 'Core concepts and examples',
        },
        {
          type: 'summary',
          duration: '15%',
          content: 'Key takeaways and next steps',
        },
        {
          type: 'call-to-action',
          duration: '5%',
          content: 'Practice exercise preview',
        },
      ],
      template: `# {lesson_title}

## Introduction
Welcome to this lesson on {topic}. In the next {duration} minutes, you'll learn:
- {objective_1}
- {objective_2}
- {objective_3}

## Main Content
### Key Concept 1: {concept_1}
{detailed_explanation_1}

### Key Concept 2: {concept_2}
{detailed_explanation_2}

### Practical Example
{example_content}

## Summary
In this lesson, you learned:
- {takeaway_1}
- {takeaway_2}
- {takeaway_3}

## Next Steps
- Practice with the exercises provided
- Review the additional resources
- Prepare for the next lesson on {next_topic}`,
    },
    reading: {
      structure: [
        {
          type: 'overview',
          content: 'Article summary and learning objectives',
        },
        {
          type: 'sections',
          content: 'Main content divided into logical sections',
        },
        { type: 'examples', content: 'Practical examples and case studies' },
        { type: 'conclusion', content: 'Summary and further reading' },
      ],
      template: `# {lesson_title}

## Overview
{brief_description}

**Learning Objectives:**
- {objective_1}
- {objective_2}
- {objective_3}

**Estimated Reading Time:** {duration} minutes

## Section 1: {section_1_title}
{section_1_content}

## Section 2: {section_2_title}
{section_2_content}

## Practical Examples
### Example 1: {example_1_title}
{example_1_content}

### Example 2: {example_2_title}
{example_2_content}

## Key Takeaways
- {takeaway_1}
- {takeaway_2}
- {takeaway_3}

## Further Reading
- {resource_1}
- {resource_2}
- {resource_3}`,
    },
    quiz: {
      structure: [
        { type: 'instructions', content: 'Quiz overview and guidelines' },
        { type: 'questions', content: 'Mix of question types' },
        { type: 'feedback', content: 'Explanations for answers' },
      ],
      questionTypes: [
        'multiple-choice',
        'true-false',
        'short-answer',
        'matching',
        'fill-in-the-blank',
      ],
    },
    assignment: {
      structure: [
        { type: 'overview', content: 'Assignment description and objectives' },
        { type: 'requirements', content: 'Detailed requirements and criteria' },
        { type: 'resources', content: 'Tools and resources needed' },
        { type: 'submission', content: 'Submission guidelines and deadlines' },
      ],
      template: `# {assignment_title}

## Assignment Overview
{assignment_description}

**Objectives:**
- {objective_1}
- {objective_2}
- {objective_3}

**Estimated Time:** {duration} minutes
**Due Date:** {due_date}

## Requirements
### Core Requirements
1. {requirement_1}
2. {requirement_2}
3. {requirement_3}

### Evaluation Criteria
- {criteria_1} (25%)
- {criteria_2} (25%)
- {criteria_3} (25%)
- {criteria_4} (25%)

## Resources
- {resource_1}
- {resource_2}
- {resource_3}

## Submission Guidelines
{submission_instructions}

## Grading Rubric
{rubric_details}`,
    },
  },
  module: {
    template: `# Module {module_number}: {module_title}

## Module Overview
{module_description}

**Duration:** {total_duration}
**Lessons:** {lesson_count}

## Learning Objectives
By the end of this module, you will be able to:
- {objective_1}
- {objective_2}
- {objective_3}

## Module Structure
{lesson_list}

## Prerequisites
{prerequisites}

## Module Resources
{resources_list}`,
  },
  course: {
    template: `# {course_title}

## Course Description
{course_description}

## What You'll Learn
{learning_outcomes}

## Course Structure
{module_overview}

## Prerequisites
{prerequisites}

## Instructor Information
{instructor_bio}

## Course Requirements
{requirements}

## Certification
{certification_info}`,
  },
};

/**
 * Assessment templates
 */
export const ASSESSMENT_TEMPLATES = {
  'multiple-choice': {
    template: {
      question: '{question_text}',
      options: ['{option_a}', '{option_b}', '{option_c}', '{option_d}'],
      correct: 0,
      explanation: '{explanation_text}',
      difficulty: 'medium',
      points: 1,
    },
  },
  'true-false': {
    template: {
      question: '{question_text}',
      correct: true,
      explanation: '{explanation_text}',
      difficulty: 'easy',
      points: 1,
    },
  },
  'short-answer': {
    template: {
      question: '{question_text}',
      keywords: ['{keyword_1}', '{keyword_2}'],
      sampleAnswer: '{sample_answer}',
      difficulty: 'medium',
      points: 3,
    },
  },
  essay: {
    template: {
      question: '{question_text}',
      requirements: ['{requirement_1}', '{requirement_2}'],
      wordLimit: 500,
      difficulty: 'hard',
      points: 10,
    },
  },
};

/**
 * Template utility functions
 */
export const getTemplateByCategory = (category, level = 'beginner') => {
  return COURSE_TEMPLATES[category]?.[level] || null;
};

export const generateObjectivesByLevel = (topic, level = 'beginner') => {
  const levelMap = {
    beginner: ['remember', 'understand', 'apply'],
    intermediate: ['apply', 'analyze', 'evaluate'],
    advanced: ['analyze', 'evaluate', 'create'],
  };

  const levels = levelMap[level] || levelMap.beginner;
  const objectives = [];

  levels.forEach(bloomLevel => {
    const templates = OBJECTIVE_TEMPLATES[bloomLevel];
    const template = templates[Math.floor(Math.random() * templates.length)];
    objectives.push(template.replace('{topic}', topic));
  });

  return objectives;
};

export const fillTemplate = (template, variables) => {
  let filled = template;
  Object.entries(variables).forEach(([key, value]) => {
    const regex = new RegExp(`{${key}}`, 'g');
    filled = filled.replace(regex, value);
  });
  return filled;
};

export const getContentStructure = contentType => {
  return CONTENT_TEMPLATES.lesson[contentType]?.structure || [];
};

export const generateContentFromTemplate = (type, variables) => {
  const template = CONTENT_TEMPLATES.lesson[type]?.template;
  if (!template) return null;

  return fillTemplate(template, variables);
};

/**
 * Content validation templates
 */
export const VALIDATION_RULES = {
  course: {
    title: { minLength: 5, maxLength: 100, required: true },
    description: { minLength: 50, maxLength: 1000, required: true },
    category: { required: true },
    level: {
      required: true,
      options: ['beginner', 'intermediate', 'advanced'],
    },
    duration: { min: 1, max: 500, required: true },
  },
  module: {
    title: { minLength: 3, maxLength: 80, required: true },
    description: { minLength: 20, maxLength: 500, required: true },
    lessons: { minCount: 2, maxCount: 15, required: true },
  },
  lesson: {
    title: { minLength: 3, maxLength: 80, required: true },
    description: { minLength: 10, maxLength: 300, required: true },
    type: {
      required: true,
      options: ['video', 'reading', 'quiz', 'assignment'],
    },
    duration: { min: 5, max: 180, required: true },
  },
};

export const validateContent = (type, content) => {
  const rules = VALIDATION_RULES[type];
  if (!rules) return { isValid: true, errors: {} };

  const errors = {};

  Object.entries(rules).forEach(([field, rule]) => {
    const value = content[field];

    if (
      rule.required &&
      (!value || (Array.isArray(value) && value.length === 0))
    ) {
      errors[field] = `${field} is required`;
      return;
    }

    if (value) {
      if (rule.minLength && value.length < rule.minLength) {
        errors[field] =
          `${field} must be at least ${rule.minLength} characters`;
      }
      if (rule.maxLength && value.length > rule.maxLength) {
        errors[field] = `${field} must not exceed ${rule.maxLength} characters`;
      }
      if (rule.min && value < rule.min) {
        errors[field] = `${field} must be at least ${rule.min}`;
      }
      if (rule.max && value > rule.max) {
        errors[field] = `${field} must not exceed ${rule.max}`;
      }
      if (
        rule.minCount &&
        Array.isArray(value) &&
        value.length < rule.minCount
      ) {
        errors[field] = `${field} must have at least ${rule.minCount} items`;
      }
      if (
        rule.maxCount &&
        Array.isArray(value) &&
        value.length > rule.maxCount
      ) {
        errors[field] = `${field} must not exceed ${rule.maxCount} items`;
      }
      if (rule.options && !rule.options.includes(value)) {
        errors[field] = `${field} must be one of: ${rule.options.join(', ')}`;
      }
    }
  });

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};
