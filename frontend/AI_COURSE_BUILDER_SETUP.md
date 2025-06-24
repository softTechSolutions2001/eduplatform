# AI Course Builder Quick Start Guide

## Installation

To install the required dependencies for the AI Course Builder, run:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install @mui/icons-material @mui/material @emotion/react @emotion/styled

# Add Heroicons (optional, already migrated to Material UI)
npm install @heroicons/react
```

## Configuration

1. Copy the `.env.template` file to `.env`:

   ```bash
   cp .env.template .env
   ```

2. Configure your AI service provider:
   ```
   VITE_AI_SERVICE_PROVIDER=openai
   VITE_OPENAI_API_KEY=your_api_key_here
   VITE_ENABLE_AI_COURSE_BUILDER=true
   ```

## Usage

1. Start the backend:

   ```bash
   cd backend
   venv\scripts\activate
   python manage.py runserver
   ```

2. Start the frontend:

   ```bash
   cd frontend
   npm run dev
   ```

3. Navigate to the Instructor Dashboard and click on the "AI Course Builder" button

## Troubleshooting

If you encounter any issues with icons, ensure you have the required dependencies:

```bash
npm install @mui/icons-material @mui/material
```

For any other issues, check the console for errors and verify that your environment variables are correctly set.

## Development Notes

- Material UI is used for icons and some components
- Tailwind CSS is used for styling
- React Context and Zustand are used for state management
- The AI Course Builder is isolated in the `src/aiCourseBuilder` directory
