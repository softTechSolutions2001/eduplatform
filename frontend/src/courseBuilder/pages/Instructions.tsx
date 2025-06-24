import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Instructional page for the course builder
 * Provides tips and guidance on how to use the drag-and-drop course builder
 */
const CourseBuilderInstructions: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto p-4 bg-white rounded-lg shadow-sm mt-8 mb-16">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold mb-2">Course Builder Guide</h1>
        <p className="text-gray-600">
          Learn how to create amazing courses with our drag-and-drop builder
        </p>
      </div>

      <div className="mb-8 pb-6 border-b border-gray-200">
        <h2 className="text-2xl font-semibold mb-4">Getting Started</h2>
        <p className="mb-4">
          The Course Builder provides an intuitive drag-and-drop interface to
          create and organize your course content. Here's how to get started:
        </p>

        <ol className="list-decimal pl-6 space-y-2">
          <li>
            <span className="font-medium">Create a new course</span> or select
            an existing course to edit
          </li>
          <li>
            <span className="font-medium">Add modules</span> to organize your
            content into logical sections
          </li>
          <li>
            <span className="font-medium">Add lessons</span> within each module
            to provide specific content
          </li>
          <li>
            <span className="font-medium">Add resources</span> to each lesson
            for supplementary materials
          </li>
          <li>
            <span className="font-medium">Review and publish</span> your course
            when you're ready
          </li>
        </ol>
      </div>

      <div className="mb-8 pb-6 border-b border-gray-200">
        <h2 className="text-2xl font-semibold mb-4">Modules</h2>
        <p className="mb-4">
          Modules are the main organizational units of your course. They help
          group related lessons together.
        </p>

        <div className="bg-gray-50 p-4 rounded-md mb-4 border border-gray-200">
          <h3 className="font-medium mb-2">Working with Modules</h3>
          <ul className="list-disc pl-6 space-y-1">
            <li>Click the "Add Module" button to create a new module</li>
            <li>Click the pencil icon to edit a module's title</li>
            <li>
              Use drag handles to reorder modules by dragging them up or down
            </li>
            <li>
              Click the trash icon to delete a module (note: this will delete
              all lessons within it)
            </li>
            <li>
              Click the module title or the arrow icon to expand/collapse its
              lessons
            </li>
          </ul>
        </div>
      </div>

      <div className="mb-8 pb-6 border-b border-gray-200">
        <h2 className="text-2xl font-semibold mb-4">Lessons</h2>
        <p className="mb-4">
          Lessons contain the actual content your students will engage with.
          Each lesson belongs to a module.
        </p>

        <div className="bg-gray-50 p-4 rounded-md mb-4 border border-gray-200">
          <h3 className="font-medium mb-2">Working with Lessons</h3>
          <ul className="list-disc pl-6 space-y-1">
            <li>
              Click the "Add Lesson" button within a module to create a new
              lesson
            </li>
            <li>
              Edit lesson titles by clicking the pencil icon next to a lesson
            </li>
            <li>
              Set access levels for lessons (guest, basic, premium) to control
              visibility
            </li>
            <li>Reorder lessons by dragging them within their module</li>
            <li>Click a lesson title to expand it and manage its resources</li>
          </ul>
        </div>
      </div>

      <div className="mb-8 pb-6 border-b border-gray-200">
        <h2 className="text-2xl font-semibold mb-4">Resources</h2>
        <p className="mb-4">
          Resources are additional materials students can access within a
          lesson, such as PDFs, videos, or links.
        </p>

        <div className="bg-gray-50 p-4 rounded-md mb-4 border border-gray-200">
          <h3 className="font-medium mb-2">Working with Resources</h3>
          <ul className="list-disc pl-6 space-y-1">
            <li>Click the "Add Resource" button within an expanded lesson</li>
            <li>Select the resource type (document, video, link, etc.)</li>
            <li>Upload files or provide URLs for your resources</li>
            <li>
              Toggle the premium setting to make resources available only to
              premium subscribers
            </li>
            <li>
              Add descriptions to help students understand the purpose of each
              resource
            </li>
          </ul>
        </div>
      </div>

      <div className="mb-8 pb-6 border-b border-gray-200">
        <h2 className="text-2xl font-semibold mb-4">Autosave & Publishing</h2>
        <p className="mb-4">
          The Course Builder automatically saves your changes as you work, so
          you don't need to worry about losing your progress.
        </p>

        <div className="bg-gray-50 p-4 rounded-md mb-4 border border-gray-200">
          <h3 className="font-medium mb-2">Important Notes:</h3>
          <ul className="list-disc pl-6 space-y-1">
            <li>
              Your course is automatically saved every few seconds after changes
            </li>
            <li>The save status is displayed at the top of the builder</li>
            <li>
              You'll be warned if you try to navigate away with unsaved changes
            </li>
            <li>
              Use the "Review & Publish" button when your course is ready to be
              published
            </li>
            <li>
              A published course will be visible to students based on your
              access settings
            </li>
          </ul>
        </div>
      </div>

      <div className="mb-8 pb-6 border-b border-gray-200">
        <h2 className="text-2xl font-semibold mb-4">Accessibility Features</h2>
        <p className="mb-4">
          The Course Builder is designed with accessibility in mind, ensuring
          all educators can create content effectively.
        </p>

        <div className="bg-gray-50 p-4 rounded-md mb-4 border border-gray-200">
          <h3 className="font-medium mb-2">Accessibility Support:</h3>
          <ul className="list-disc pl-6 space-y-1">
            <li>Keyboard navigation throughout the builder</li>
            <li>Screen reader compatibility with ARIA attributes</li>
            <li>High contrast visual design</li>
            <li>Manageable focus states for all interactive elements</li>
            <li>Helpful error messages and instructions</li>
          </ul>
        </div>
      </div>

      <div className="flex justify-center mt-10">
        <Link
          to="/instructor/courses/builder"
          className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-200"
        >
          Start Building Your Course
        </Link>
      </div>
    </div>
  );
};

export default CourseBuilderInstructions;
