#!/usr/bin/env node

/**
 * AI Course Builder Manual Test Script
 * 
 * This script helps test the AI Course Builder flow using mock responses.
 * It starts the frontend in development mode with mock API responses enabled.
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import readline from 'readline';
import { fileURLToPath } from 'url';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  underscore: '\x1b[4m',
  blink: '\x1b[5m',
  reverse: '\x1b[7m',
  hidden: '\x1b[8m',
  
  fg: {
    black: '\x1b[30m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    white: '\x1b[37m'
  },
  
  bg: {
    black: '\x1b[40m',
    red: '\x1b[41m',
    green: '\x1b[42m',
    yellow: '\x1b[43m',
    blue: '\x1b[44m',
    magenta: '\x1b[45m',
    cyan: '\x1b[46m',
    white: '\x1b[47m'
  }
};

// Print a styled header
function printHeader(text) {
  console.log('\n' + colors.bright + colors.fg.blue + '='.repeat(80) + colors.reset);
  console.log(colors.bright + colors.fg.blue + text + colors.reset);
  console.log(colors.bright + colors.fg.blue + '='.repeat(80) + colors.reset + '\n');
}

// Print a styled step
function printStep(num, text) {
  console.log(colors.bright + colors.fg.green + `Step ${num}: ` + colors.reset + colors.fg.white + text + colors.reset);
}

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Create temporary .env file with mock settings enabled
async function setupEnv() {
  printHeader('Setting up test environment');
  
  try {
    // Use __dirname to get the correct path
    const envTemplatePath = path.resolve(__dirname, '..', '.env.template');
    const envPath = path.resolve(__dirname, '..', '.env.test');
    
    if (!fs.existsSync(envTemplatePath)) {
      throw new Error(`Could not find .env.template file at ${envTemplatePath}. Make sure the file exists.`);
    }
    
    let envContent = fs.readFileSync(envTemplatePath, 'utf8');
    
    // Enable mock responses
    envContent = envContent.replace(/VITE_AI_MOCK_RESPONSES=false/g, 'VITE_AI_MOCK_RESPONSES=true');
    envContent = envContent.replace(/VITE_MOCK_AI=false/g, 'VITE_MOCK_AI=true');
    envContent = envContent.replace(/VITE_AI_DEBUG_MODE=false/g, 'VITE_AI_DEBUG_MODE=true');
    
    // Write the test env file
    fs.writeFileSync(envPath, envContent);
    
    console.log(colors.fg.green + '✅ Created .env.test file with mock settings' + colors.reset);
    return envPath;
  } catch (error) {
    console.error(colors.fg.red + '❌ Failed to set up environment:' + colors.reset, error);
    throw error;
  }
}

// Main test flow
async function runTests() {
  try {
    printHeader('AI COURSE BUILDER TEST');
    console.log('This script will help you test the AI Course Builder flow using mock responses.\n');
    
    // Setup environment
    const envPath = await setupEnv();
    
    // Test instructions
    printStep(1, 'We will start the development server with mock responses enabled.');
    printStep(2, 'Navigate to the AI Course Builder in your browser.');
    printStep(3, 'Fill in the course information and follow through each step.');
    printStep(4, 'Verify that mock responses are being used correctly.');
    printStep(5, 'Look for any errors in the browser console or UI.');
    
    console.log('\n' + colors.fg.yellow + 'Press Enter to start the development server, or Ctrl+C to exit...' + colors.reset);
    
    await new Promise((resolve) => rl.once('line', resolve));
    
    // Start the development server with test env
    printHeader('Starting development server');
    
    try {
      execSync(`cross-env DOTENV_CONFIG_PATH=${envPath} npm run dev`, {
        stdio: 'inherit',
        env: { ...process.env, FORCE_COLOR: true }
      });
    } catch (error) {
      // This will be reached if the server is stopped
      printHeader('Server stopped');
    }
    
  } catch (error) {
    console.error(colors.fg.red + '❌ Test script failed:' + colors.reset, error);
  } finally {
    rl.close();
  }
}

// Run the tests
runTests();
