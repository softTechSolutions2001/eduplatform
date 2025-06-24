// Debug script for CourseContentPage.jsx
// Place in a file in the same directory as CourseContentPage.jsx and import with:
// import './debug_course_content.js';

// Function to be called by CourseContentPage to debug lesson structure
window.debugLesson = function (lesson, fieldType) {
  if (!lesson) return;

  console.log(`=== DEBUG LESSON CONTENT (${fieldType || 'all'}) ===`);
  console.log('Lesson Object Structure:', lesson);
  console.log('Field Values:');
  console.log('- guest_content:', lesson.guest_content);
  console.log('- basic_content:', lesson.basic_content);
  console.log('- registered_content:', lesson.registered_content);
  console.log('- intermediate_content:', lesson.intermediate_content);
  console.log('- content:', lesson.content);
  console.log('- access_level:', lesson.access_level);

  if (fieldType) {
    let result;
    switch (fieldType) {
      case 'guest':
        result = lesson.guest_content || lesson.basic_content || '';
        break;
      case 'registered':
        result = lesson.registered_content || lesson.intermediate_content || '';
        break;
      default:
        result = lesson.content || '';
    }
    console.log(`Content for ${fieldType}:`, result);
  }

  console.log('================================');
};
