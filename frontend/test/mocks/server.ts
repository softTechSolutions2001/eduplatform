// MSW server for mocking API requests in tests
import { setupServer } from 'msw/node'
import { rest } from 'msw'

// Mock API handlers
export const handlers = [
  // Mock course endpoints
  rest.get('/api/courses/:id', (req, res, ctx) => {
    return res(
      ctx.json({
        id: 1,
        title: 'Test Course',
        description: 'A test course',
        slug: 'test-course',
        modules: []
      })
    )
  }),

  rest.post('/api/courses', (req, res, ctx) => {
    return res(
      ctx.json({
        id: 1,
        title: 'New Course',
        description: 'A new course',
        slug: 'new-course',
        modules: []
      })
    )
  }),

  rest.put('/api/courses/:id', (req, res, ctx) => {
    return res(
      ctx.json({
        id: 1,
        title: 'Updated Course',
        description: 'An updated course',
        slug: 'updated-course',
        modules: []
      })
    )
  }),

  // Mock module endpoints
  rest.post('/api/courses/:courseId/modules', (req, res, ctx) => {
    return res(
      ctx.json({
        id: 1,
        title: 'New Module',
        description: 'A new module',
        orderIndex: 0,
        lessons: []
      })
    )
  }),

  // Mock lesson endpoints
  rest.post('/api/modules/:moduleId/lessons', (req, res, ctx) => {
    return res(
      ctx.json({
        id: 1,
        title: 'New Lesson',
        description: 'A new lesson',
        orderIndex: 0,
        resources: []
      })
    )
  }),

  // Mock resource endpoints
  rest.post('/api/lessons/:lessonId/resources', (req, res, ctx) => {
    return res(
      ctx.json({
        id: 1,
        title: 'New Resource',
        type: 'video',
        url: 'https://example.com/video.mp4',
        orderIndex: 0
      })
    )
  })
]

export const server = setupServer(...handlers)
