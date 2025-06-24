/**
 * AI Prompt Templates for Course Generation
 *
 * Carefully crafted prompts for different phases of course creation
 */

export const promptTemplates = {
  /**
   * Course Outline Generation Prompt
   */
  courseOutline: basicInfo => `
You are an expert educational content designer tasked with creating a comprehensive course outline.

Course Details:
- Title: ${basicInfo.title}
- Description: ${basicInfo.description}
- Target Audience: ${basicInfo.targetAudience}
- Level: ${basicInfo.level}
- Learning Objectives: ${basicInfo.learningObjectives.join(', ')}

Create a detailed course outline with the following structure:

{
  "modules": [
    {
      "title": "Module title",
      "description": "Module description",
      "order": 1,
      "duration_minutes": 120,
      "estimatedDuration": "2-3 hours", // Legacy field, please use duration_minutes instead
      "objectives": ["Learning objective 1", "Learning objective 2"],
      "lessons": [
        {
          "title": "Lesson title",
          "description": "Lesson description",
          "type": "video|text|interactive|assignment",
          "duration_minutes": 30,
          "estimatedDuration": "30 minutes", // Legacy field, please use duration_minutes instead
          "accessLevel": "guest|registered|premium"
        }
      ]
    }
  ],
  "assessmentStrategy": "Description of overall assessment approach",
  "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
  "estimatedTotalDuration": "6-8 weeks",
  "courseStructure": {
    "totalModules": 6,
    "totalLessons": 24,
    "assessmentTypes": ["quiz", "assignment", "project"]
  }
}

Guidelines:
1. Create 4-8 modules that logically progress from basic to advanced concepts
2. Each module should have 3-6 lessons
3. Mix content types (video, text, interactive, assignments)
4. Set appropriate access levels: guest (free preview), registered (basic), premium (advanced)
5. Ensure learning objectives are specific, measurable, and achievable
6. Consider different learning styles and engagement techniques
7. Include practical applications and real-world examples
8. Plan for formative and summative assessments

Return only the JSON structure without additional text.
`,

  /**
   * Module Content Generation Prompt
   */
  moduleContent: (moduleData, courseContext) => `
You are creating detailed content for a course module.

Course Context:
- Course Title: ${courseContext.title}
- Course Level: ${courseContext.level}
- Target Audience: ${courseContext.targetAudience}

Module Information:
- Title: ${moduleData.title}
- Description: ${moduleData.description}
- Learning Objectives: ${moduleData.objectives?.join(', ') || 'To be defined'}

Generate comprehensive module content with this structure:

{
  "lessons": [
    {
      "title": "Lesson title",
      "description": "Detailed lesson description",
      "content": "Comprehensive lesson content in markdown format",
      "type": "video|text|interactive|assignment",
      "duration_minutes": 35,
      "estimatedDuration": "30-45 minutes", // Legacy field, please use duration_minutes instead
      "accessLevel": "guest|registered|premium",
      "objectives": ["Specific lesson objective"],
      "keyPoints": ["Key point 1", "Key point 2"],
      "activities": [
        {
          "type": "reading|exercise|discussion|quiz",
          "title": "Activity title",
          "description": "Activity description",
          "estimatedTime": "15 minutes"
        }
      ],
      "resources": [
        {
          "title": "Resource title",
          "type": "video|article|tool|download",
          "url": "placeholder-url",
          "description": "Resource description"
        }
      ]
    }
  ],
  "assessments": [
    {
      "type": "quiz|assignment|project|discussion",
      "title": "Assessment title",
      "description": "Assessment description",
      "estimatedTime": "30 minutes",
      "pointsValue": 100,
      "rubric": "Assessment criteria"
    }
  ],
  "supplementaryResources": [
    {
      "title": "Additional reading",
      "type": "article|book|video|website",
      "description": "Why this resource is valuable"
    }
  ]
}

Guidelines:
1. Create engaging, informative lesson content
2. Use markdown formatting for rich text
3. Include practical examples and case studies
4. Design interactive elements and activities
5. Provide diverse assessment options
6. Suggest relevant external resources
7. Ensure content flows logically between lessons
8. Consider different learning preferences

Return only the JSON structure.
`,

  /**
   * Lesson Content Generation Prompt
   */
  lessonContent: (lessonData, moduleContext, courseContext) => `
Generate detailed content for a specific lesson.

Course Context:
- Title: ${courseContext.title}
- Level: ${courseContext.level}
- Target Audience: ${courseContext.targetAudience}

Module Context:
- Module: ${moduleContext.title}
- Module Objectives: ${moduleContext.objectives?.join(', ') || ''}

Lesson Details:
- Title: ${lessonData.title}
- Type: ${lessonData.type}
- Duration: ${lessonData.duration_minutes ? `${lessonData.duration_minutes} minutes` : lessonData.estimatedDuration || 'Not specified'}
- Access Level: ${lessonData.accessLevel}

Create comprehensive lesson content:

{
  "content": "# Lesson Title\\n\\nDetailed lesson content in markdown format with:\\n- Clear explanations\\n- Examples\\n- Code snippets (if applicable)\\n- Images/diagrams suggestions\\n- Interactive elements",
  "objectives": ["Specific, measurable learning objectives"],
  "keyTakeaways": ["Key point 1", "Key point 2", "Key point 3"],
  "activities": [
    {
      "type": "exercise|discussion|quiz|reflection",
      "title": "Activity title",
      "instructions": "Step-by-step instructions",
      "estimatedTime": "15 minutes",
      "materials": ["Required materials"]
    }
  ],
  "assessments": [
    {
      "type": "formative|summative",
      "format": "quiz|essay|project|presentation",
      "questions": ["Assessment question 1", "Question 2"],
      "rubric": "Evaluation criteria"
    }
  ],
  "resources": [
    {
      "title": "Resource title",
      "type": "video|article|tool|template",
      "description": "How this resource supports learning",
      "url": "placeholder-url",
      "isRequired": true
    }
  ],
  "prerequisites": ["Required prior knowledge"],
  "nextSteps": "How this lesson connects to the next one",
  "troubleshooting": {
    "commonIssues": ["Common problem 1", "Common problem 2"],
    "solutions": ["Solution 1", "Solution 2"]
  }
}

Guidelines:
1. Write clear, engaging content appropriate for the target audience
2. Include practical examples and real-world applications
3. Use active voice and conversational tone
4. Break complex topics into digestible sections
5. Suggest multimedia elements (videos, images, diagrams)
6. Design meaningful activities that reinforce learning
7. Create fair and comprehensive assessments
8. Provide helpful resources and references

Return only the JSON structure.
`,

  /**
   * Content Enhancement Prompt
   */
  contentEnhancement: (content, enhancementType) => `
Enhance the following educational content to improve learning outcomes and engagement.

Enhancement Type: ${enhancementType}
Content to Enhance: ${JSON.stringify(content, null, 2)}

Apply these enhancements based on the type:

${
  enhancementType === 'engagement'
    ? `
- Add interactive elements and activities
- Include storytelling and real-world examples
- Suggest multimedia integration points
- Create discussion prompts
- Add gamification elements
`
    : ''
}

${
  enhancementType === 'accessibility'
    ? `
- Improve readability and clarity
- Add alternative text suggestions for images
- Include multiple content formats for different learning styles
- Ensure inclusive language
- Add closed caption suggestions for videos
`
    : ''
}

${
  enhancementType === 'depth'
    ? `
- Expand on key concepts with more detail
- Add advanced examples and case studies
- Include additional practice exercises
- Suggest further reading and resources
- Create extension activities for advanced learners
`
    : ''
}

${
  enhancementType === 'structure'
    ? `
- Improve content organization and flow
- Add clear headings and subheadings
- Create better transitions between sections
- Include summary sections and key takeaways
- Add navigation aids and progress indicators
`
    : ''
}

Return the enhanced content maintaining the original JSON structure but with improved and expanded content.
`,

  /**
   * Assessment Generation Prompt
   */
  assessmentGeneration: (lessonContent, assessmentType) => `
Create comprehensive assessments for the following lesson content.

Lesson Content: ${typeof lessonContent === 'string' ? lessonContent : JSON.stringify(lessonContent)}
Assessment Type: ${assessmentType}

Generate assessments in this format:

{
  "formativeAssessments": [
    {
      "type": "quiz|exercise|discussion",
      "title": "Assessment title",
      "questions": [
        {
          "type": "multiple_choice|true_false|short_answer|essay",
          "question": "Question text",
          "options": ["Option A", "Option B", "Option C", "Option D"],
          "correctAnswer": "Correct answer or index",
          "explanation": "Why this is the correct answer",
          "difficulty": "easy|medium|hard",
          "learningObjective": "Which objective this assesses"
        }
      ],
      "estimatedTime": "15 minutes",
      "instructions": "Clear instructions for learners"
    }
  ],
  "summativeAssessments": [
    {
      "type": "project|essay|presentation|portfolio",
      "title": "Assessment title",
      "description": "Detailed assignment description",
      "requirements": ["Requirement 1", "Requirement 2"],
      "deliverables": ["What students must submit"],
      "estimatedTime": "2-3 hours",
      "pointsValue": 100,
      "rubric": {
        "criteria": [
          {
            "name": "Criteria name",
            "description": "What to evaluate",
            "levels": {
              "excellent": "90-100 points description",
              "good": "80-89 points description",
              "satisfactory": "70-79 points description",
              "needs_improvement": "Below 70 points description"
            }
          }
        ]
      }
    }
  ],
  "selfAssessments": [
    {
      "type": "reflection|checklist|peer_review",
      "title": "Self-assessment title",
      "prompts": ["Reflection question 1", "Question 2"],
      "checklist": ["I can do X", "I understand Y"],
      "instructions": "How to complete the self-assessment"
    }
  ]
}

Guidelines:
1. Create diverse question types and formats
2. Align assessments with learning objectives
3. Include various difficulty levels
4. Provide clear rubrics and criteria
5. Ensure fair and unbiased questions
6. Include immediate feedback when possible
7. Create authentic, practical assessments
8. Consider different assessment methods for diverse learners

Return only the JSON structure.
`,

  /**
   * Learning Objective Refinement Prompt
   */
  refineObjectives: (objectives, courseLevel, targetAudience) => `
Refine and improve these learning objectives to be more specific, measurable, and achievable.

Current Objectives: ${objectives.join(', ')}
Course Level: ${courseLevel}
Target Audience: ${targetAudience}

Return refined objectives using Bloom's Taxonomy and SMART criteria:

{
  "refinedObjectives": [
    {
      "original": "Original objective",
      "refined": "Improved SMART objective",
      "bloomsLevel": "remember|understand|apply|analyze|evaluate|create",
      "assessmentMethod": "How this will be assessed",
      "timeFrame": "When this should be achieved"
    }
  ],
  "suggestions": [
    "Suggestion for further improvement"
  ]
}

Guidelines:
1. Use action verbs from Bloom's Taxonomy
2. Make objectives specific and measurable
3. Ensure objectives are achievable for the target audience
4. Align with the course level
5. Consider different types of learning (cognitive, psychomotor, affective)
6. Include conditions and criteria for success

Return only the JSON structure.
`,

  /**
   * Course Improvement Suggestions Prompt
   */
  improvementSuggestions: courseData => `
Analyze this course and provide improvement suggestions.

Course Data: ${JSON.stringify(courseData, null, 2)}

Provide comprehensive improvement suggestions:

{
  "overallFeedback": "General assessment of the course quality",
  "strengths": ["Strength 1", "Strength 2"],
  "areasForImprovement": [
    {
      "area": "Content organization",
      "issue": "Specific issue identified",
      "suggestion": "Concrete improvement suggestion",
      "priority": "high|medium|low",
      "implementationTime": "estimated time to implement"
    }
  ],
  "contentSuggestions": [
    {
      "module": "Module name",
      "lesson": "Lesson name (if specific)",
      "suggestion": "Specific content improvement",
      "rationale": "Why this improvement is needed"
    }
  ],
  "engagementEnhancements": [
    "Suggestion to increase learner engagement"
  ],
  "assessmentImprovements": [
    "Suggestion for better assessments"
  ],
  "accessibilityRecommendations": [
    "Suggestion for better accessibility"
  ],
  "nextSteps": [
    "Immediate action items for improvement"
  ]
}

Guidelines:
1. Provide constructive, actionable feedback
2. Focus on evidence-based improvements
3. Consider different learning styles and needs
4. Suggest specific tools and resources
5. Prioritize suggestions by impact and feasibility
6. Include implementation guidance

Return only the JSON structure.
`,
};

export default promptTemplates;
