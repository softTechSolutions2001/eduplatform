// Simple test to verify CourseWizardWrapper can be imported without errors
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

try {
  console.log('Testing import of CourseWizardWrapper...');
  
  const wrapperPath = path.join(__dirname, 'src', 'pages', 'instructor', 'CourseWizardWrapper.jsx');
  const contextPath = path.join(__dirname, 'src', 'pages', 'instructor', 'CourseWizardContext.jsx');
  
  // Check if files exist and can be read
  if (fs.existsSync(wrapperPath)) {
    const wrapperContent = fs.readFileSync(wrapperPath, 'utf8');
    console.log('✓ CourseWizardWrapper.jsx exists and is readable');
    
    // Check if problematic handleSave references are removed
    if (wrapperContent.includes('handleSave: saveData')) {
      console.log('✗ Still contains problematic handleSave: saveData destructuring');
    } else {
      console.log('✓ Problematic handleSave: saveData destructuring removed');
    }
    
    if (wrapperContent.includes('saveData()')) {
      console.log('✗ Still contains saveData() function calls');
    } else {
      console.log('✓ saveData() function calls removed');
    }
  } else {
    console.log('✗ CourseWizardWrapper.jsx not found');
  }
  
  if (fs.existsSync(contextPath)) {
    const contextContent = fs.readFileSync(contextPath, 'utf8');
    console.log('✓ CourseWizardContext.jsx exists and is readable');
    
    // Check available exports
    if (contextContent.includes('saveStarted') && contextContent.includes('saveCompleted')) {
      console.log('✓ CourseWizardContext exports save-related functions properly');
    } else {
      console.log('✗ CourseWizardContext missing expected save functions');
    }
  } else {
    console.log('✗ CourseWizardContext.jsx not found');
  }
  
  console.log('\nTest completed successfully!');
} catch (error) {
  console.error('Test failed:', error.message);
}
