#!/usr/bin/env node

/**
 * AI Course Builder Manual Test Script
 * 
 * This script helps test the AI Course Builder flow using mock responses.
 * It sets up the environment for testing with mock API responses.
 */

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  blue: '\x1b[34m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
};

console.log(colors.bright + colors.blue + '='.repeat(80) + colors.reset);
console.log(colors.bright + colors.blue + 'AI COURSE BUILDER TEST SETUP' + colors.reset);
console.log(colors.bright + colors.blue + '='.repeat(80) + colors.reset + '\n');

console.log(colors.bright + 'This script sets up your environment for testing the AI Course Builder with mock data.\n' + colors.reset);

console.log(colors.green + '1. Setting up environment variables for mock mode:' + colors.reset);
console.log('   - Create a .env file in the frontend directory with the following content:\n');

console.log(colors.yellow + `# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api

# AI Mock Configuration
VITE_MOCK_AI=true
VITE_AI_MOCK_RESPONSES=true
VITE_AI_DEBUG_MODE=true

# Feature Flags
VITE_ENABLE_AI_COURSE_BUILDER=true
VITE_ENABLE_AI_SUGGESTIONS=true
VITE_ENABLE_AI_CONTENT_ENHANCEMENT=true
VITE_ENABLE_AI_ASSESSMENT_GENERATION=true` + colors.reset);

console.log('\n' + colors.green + '2. Start the frontend development server:' + colors.reset);
console.log('   npm run dev');

console.log('\n' + colors.green + '3. Navigate to the AI Course Builder in your browser:' + colors.reset);
console.log('   Open http://localhost:5173/instructor/courses/create/ai');

console.log('\n' + colors.green + '4. Complete the testing steps:' + colors.reset);
console.log('   - Fill out the course information form');
console.log('   - Add learning objectives');
console.log('   - Verify course outline generation works with mock data');
console.log('   - Check module content generation');
console.log('   - Complete the course creation process');

console.log('\n' + colors.green + '5. Watch the browser console for:' + colors.reset);
console.log('   - "AI Course Builder is using mock responses for development"');
console.log('   - "Using mock initialize response"');
console.log('   - Other debug messages showing the mock API in action');

console.log('\n' + colors.bright + colors.blue + '='.repeat(80) + colors.reset);
