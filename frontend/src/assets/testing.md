frontend/ ├── src/ │ ├── pages/ │ │ ├── courses/ │ │ │ ├── testing/ │ │ │ │ ├──
CourseLandingPage.jsx # Course main landing page │ │ │ │ ├── CourseOverviewPage.jsx # Course
structure overview │ │ │ │ ├── ModuleLayoutPage.jsx # Template for all module pages │ │ │ │ ├──
CertificationGuidePage.jsx # Certification paths page │ │ │ │ └── CourseCompletionPage.jsx #
Completion and next steps │ │ │ │ │ │ │ └── testing-modules/ # Individual module pages │ │ │ ├──
FoundationsModulePage.jsx │ │ │ ├── MethodologiesModulePage.jsx │ │ │ ├── AutomationModulePage.jsx │
│ │ ├── PerformanceSecurityModulePage.jsx │ │ │ ├── MobileAPIModulePage.jsx │ │ │ ├──
AIMLTestingModulePage.jsx │ │ │ └── CertificationPrepPage.jsx │ │ │ │ │ └── assessments/ │ │ ├──
testing/ │ │ │ ├── QuizPage.jsx # Quiz assessment page │ │ │ ├── PracticalAssessmentPage.jsx #
Practical assignments │ │ │ ├── CertificationExamPage.jsx # Mock certification exams │ │ │ └──
ProjectSubmissionPage.jsx # Capstone project submission │ │ │ ├── components/ │ │ ├── courses/ │ │ │
├── testing/ │ │ │ │ ├── CourseHeader.jsx # Course-specific header │ │ │ │ ├── CourseSidebar.jsx #
Module navigation sidebar │ │ │ │ ├── ModuleCard.jsx # Module preview card │ │ │ │ ├──
LessonNavigation.jsx # Next/prev lesson buttons │ │ │ │ ├── CertificationCard.jsx # Certification
info card │ │ │ │ └── CourseProgressBar.jsx # Progress tracking component │ │ │ │ │ ├── lessons/ │ │
│ ├── testing/ │ │ │ │ ├── LessonContent.jsx # Lesson content container │ │ │ │ ├──
ConceptExplanation.jsx # Concept explanation component │ │ │ │ ├── CodeSample.jsx # Code example
display │ │ │ │ ├── InteractiveDemo.jsx # Interactive demonstration │ │ │ │ └──
KeyPointsSummary.jsx # Key points highlight box │ │ │ │ │ ├── interactive/ │ │ │ ├── testing/ │ │ │
│ ├── CodeEditor.jsx # Interactive code editor │ │ │ │ ├── TestSimulator.jsx # Test execution
simulator │ │ │ │ ├── BugHuntingGame.jsx # Bug finding exercises │ │ │ │ ├── TestCaseBuilder.jsx #
Interactive test case creator │ │ │ │ ├── TestAutomationWorkbench.jsx # Automation script workspace
│ │ │ │ └── PerformanceDashboard.jsx # Performance testing visualization │ │ │ │ │ ├── assessments/
│ │ │ ├── testing/ │ │ │ │ ├── MultipleChoiceQuestion.jsx # MCQ component │ │ │ │ ├──
CodingChallenge.jsx # Code-based question │ │ │ │ ├── ScenarioQuestion.jsx # Scenario analysis
question │ │ │ │ ├── DragDropQuestion.jsx # Drag and drop exercises │ │ │ │ ├──
CertificationExamTimer.jsx # Exam timer component │ │ │ │ └── AssessmentResult.jsx # Results display
component │ │ │ │ │ └── visualizations/ │ │ ├── testing/ │ │ │ ├── TestProcessFlow.jsx # Testing
process visualization │ │ │ ├── TestCoverageChart.jsx # Test coverage visualization │ │ │ ├──
BugLifecycleAnimation.jsx # Bug lifecycle visualization │ │ │ ├── MethodologyComparison.jsx #
Testing methods comparison │ │ │ └── PerformanceTestGraph.jsx # Performance test results graph │ │ │
├── contexts/ │ │ ├── CourseProgressContext.jsx # Track course progress │ │ ├──
TestingSimulationContext.jsx # Manage simulation state │ │ └── AssessmentContext.jsx # Manage
assessment state │ │ │ ├── services/ │ │ ├── courseApi.js # Course content API service │ │ ├──
assessmentApi.js # Assessment handling service │ │ ├── codeExecutionService.js # Code execution
service │ │ └── simulationService.js # Testing simulation service │ │ │ ├── assets/ │ │ ├── images/
│ │ │ ├── testing/ # Course-specific images │ │ │ │ ├── module-icons/ # Icons for each module │ │ │
│ ├── certifications/ # Certification logos │ │ │ │ ├── tool-screenshots/ # Testing tool screenshots
│ │ │ │ └── diagrams/ # Process diagrams │ │ │ │ │ ├── animations/ │ │ │ ├── testing/ #
Course-specific animations │ │ │ │ ├── test-process.json # Test process animation │ │ │ │ ├──
bug-lifecycle.json # Bug lifecycle animation │ │ │ │ └── ci-cd-pipeline.json # CI/CD pipeline
animation │ │ │ │ │ └── videos/ │ │ ├── testing/ # Course demo videos │ │ │ ├── tool-demos/ #
Testing tool demonstrations │ │ │ ├── expert-interviews/ # Industry expert interviews │ │ │ └──
case-studies/ # Real-world case studies │ │ │ └── utils/ │ ├── testingUtils.js # Testing-specific
utilities │ ├── codeValidation.js # Code validation helpers │ └── certificationHelpers.js #
Certification exam utilities
