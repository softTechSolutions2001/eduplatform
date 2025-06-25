/**
 * File: src/services/instructorService.js
 * Version: 4.0.0
 * Date: 2025-06-25 08:43:44
 * Author: softTechSolutions2001
 * Last Modified: 2025-06-25 08:43:44 UTC
 *
 * Enhanced Instructor API Service - Production Ready
 *
 * MAJOR REFACTOR (v4.0.0):
 * 1. Converted to modular structure with 6 focused service files
 * 2. Reuses central API infrastructure for request handling
 * 3. Adds TypeScript support
 * 4. Maintains 100% backward compatibility via facade pattern
 * 5. Fixes edge-case bugs in slug validation and data sanitization
 * 6. No API contract changes
 */

// Legacy shim – delegate to new TypeScript implementation
import instructorFacade, { InstructorService } from './instructor/index';

// Direct re-export to maintain backward compatibility
export default instructorFacade;
export { InstructorService };
