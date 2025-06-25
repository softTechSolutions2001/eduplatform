/**
 * File: tools/validateApiPaths.ts
 * Version: 2.0.0
 * Created: 2025-06-25
 * Author: softTechSolutions2001
 *
 * API Path Validation Tool
 *
 * This script checks for hardcoded API paths in the codebase that don't use
 * the centralized API_ENDPOINTS or API_ROUTES registry from endpoints.ts
 */

import fs from 'fs';
import { glob } from 'glob';

// Configuration
const CONFIG = {
    // File patterns to search (adjusted for your project structure)
    filePatterns: [
        'src/**/*.{ts,tsx,js,jsx}',
        '!src/test/**/*',
        '!src/tests/**/*',
        '!**/*.test.{ts,tsx,js,jsx}',
        '!**/*.spec.{ts,tsx,js,jsx}'
    ],

    // Paths to exclude from validation
    excludedPaths: [
        'node_modules',
        'dist',
        'build',
        'tools',
        'coverage',
        '.git',
        'public',
        'scripts',
        'test',
        'tests',
        'cypress'
    ],

    // Files to exclude completely (your specific files)
    excludedFiles: [
        'endpoints.ts',
        'constants.ts',
        'apiClient.ts',
        'mockResponses.js',
        'setup.ts',
        'server.ts'
    ],

    // API base patterns that should be centralized (based on your endpoints.ts)
    apiBasePaths: ['/api', '/auth', '/instructor', '/student', '/system', '/user', '/courses'],

    // Minimum path length to consider (avoid false positives)
    minPathLength: 4,

    // Additional patterns specific to your project
    allowedPatterns: [
        // Allow environment variable usage
        /process\.env\./,
        // Allow import.meta.env usage (Vite)
        /import\.meta\.env\./,
        // Allow API_BASE_URL usage
        /API_BASE_URL/,
        // Allow API_ENDPOINTS usage
        /API_ENDPOINTS/,
        // Allow API_ROUTES usage
        /API_ROUTES/
    ]
};

interface ValidationIssue {
    file: string;
    line: number;
    column: number;
    match: string;
    context: string;
    severity: 'warning' | 'error';
    suggestion?: string;
}

// Enhanced patterns to detect various API call formats
const API_PATH_PATTERNS = [
    // HTTP client method calls
    {
        pattern: /\.(?:get|post|put|patch|delete|request)\s*\(\s*['"`]([^'"`]+)['"`]/gi,
        description: 'HTTP client method calls',
        severity: 'error' as const
    },

    // Axios method calls
    {
        pattern: /axios\.(?:get|post|put|patch|delete|request)\s*\(\s*['"`]([^'"`]+)['"`]/gi,
        description: 'Axios method calls',
        severity: 'error' as const
    },

    // Fetch calls
    {
        pattern: /fetch\s*\(\s*['"`]([^'"`]+)['"`]/gi,
        description: 'Fetch API calls',
        severity: 'error' as const
    },

    // Template literals with API paths
    {
        pattern: /`[^`]*\/(?:api|auth|instructor|student|system)\/[^`]*`/gi,
        description: 'Template literals with API paths',
        severity: 'warning' as const
    },

    // String concatenation with API paths
    {
        pattern: /['"`][^'"`]*\/(?:api|auth|instructor|student|system)\/[^'"`]*['"`]/gi,
        description: 'String literals with API paths',
        severity: 'warning' as const
    }
];

/**
 * Extract line and column information for a match
 */
function getLineAndColumn(content: string, matchIndex: number): { line: number; column: number } {
    const lines = content.substring(0, matchIndex).split('\n');
    return {
        line: lines.length,
        column: lines[lines.length - 1].length + 1
    };
}

/**
 * Get context around the match for better debugging
 */
function getContext(content: string, matchIndex: number, matchLength: number): string {
    const start = Math.max(0, matchIndex - 50);
    const end = Math.min(content.length, matchIndex + matchLength + 50);
    const context = content.substring(start, end);

    // Replace newlines with spaces for cleaner output
    return context.replace(/\s+/g, ' ').trim();
}

/**
 * Check if a path should be flagged as hardcoded
 */
function shouldFlagPath(extractedPath: string, fullContent: string): boolean {
    // Skip if path is too short (likely not an API path)
    if (extractedPath.length < CONFIG.minPathLength) {
        return false;
    }

    // Skip if path doesn't start with known API base paths
    const startsWithApiPath = CONFIG.apiBasePaths.some(basePath =>
        extractedPath.startsWith(basePath)
    );

    if (!startsWithApiPath) {
        return false;
    }

    // Skip if content contains allowed patterns (env vars, constants)
    if (CONFIG.allowedPatterns.some(pattern => pattern.test(fullContent))) {
        return false;
    }

    // Skip if path contains variables (likely already using constants)
    if (extractedPath.includes('${') ||
        extractedPath.includes('API_') ||
        extractedPath.includes('BASE_URL') ||
        extractedPath.includes('ENDPOINT')) {
        return false;
    }

    // Skip relative paths that don't start with /
    if (!extractedPath.startsWith('/')) {
        return false;
    }

    // Skip mock/test data paths
    if (extractedPath.includes('/mock') ||
        extractedPath.includes('/test') ||
        extractedPath.includes('localhost') ||
        extractedPath.includes('127.0.0.1')) {
        return false;
    }

    return true;
}

/**
 * Generate suggestions for fixing hardcoded paths
 */
function generateSuggestion(match: string): string {
    if (match.includes('/api/user/') || match.includes('/user/')) {
        return 'Consider using API_ENDPOINTS.USER or API_ENDPOINTS.AUTH from endpoints.ts';
    }
    if (match.includes('/api/courses/') || match.includes('/courses/')) {
        return 'Consider using API_ENDPOINTS.COURSE from endpoints.ts';
    }
    if (match.includes('/api/instructor/') || match.includes('/instructor/')) {
        return 'Consider using API_ROUTES.INSTRUCTOR or API_ENDPOINTS.INSTRUCTOR from endpoints.ts';
    }
    if (match.includes('/api/student/') || match.includes('/student/')) {
        return 'Consider using API_ROUTES.STUDENT from endpoints.ts';
    }
    if (match.includes('/api/system/') || match.includes('/system/')) {
        return 'Consider using API_ROUTES.SYSTEM or API_ENDPOINTS.SYSTEM from endpoints.ts';
    }
    if (match.includes('/api/auth/') || match.includes('/auth/')) {
        return 'Consider using API_ENDPOINTS.AUTH or API_ROUTES.AUTH from endpoints.ts';
    }
    if (match.includes('/api/assessments/') || match.includes('/assessments/')) {
        return 'Consider using API_ENDPOINTS.ASSESSMENT from endpoints.ts';
    }
    if (match.includes('/api/modules/') || match.includes('/modules/')) {
        return 'Consider using API_ENDPOINTS.MODULE from endpoints.ts';
    }
    if (match.includes('/api/lessons/') || match.includes('/lessons/')) {
        return 'Consider using API_ENDPOINTS.LESSON from endpoints.ts';
    }
    if (match.includes('/api/notes/') || match.includes('/notes/')) {
        return 'Consider using API_ENDPOINTS.NOTE from endpoints.ts';
    }
    if (match.includes('/api/labs/') || match.includes('/labs/')) {
        return 'Consider using API_ENDPOINTS.LAB from endpoints.ts';
    }
    if (match.includes('/api/certificates/') || match.includes('/certificates/')) {
        return 'Consider using API_ENDPOINTS.CERTIFICATE from endpoints.ts';
    }
    if (match.includes('/api/categories/') || match.includes('/categories/')) {
        return 'Consider using API_ENDPOINTS.CATEGORY from endpoints.ts';
    }
    if (match.includes('/api/blog/') || match.includes('/blog/')) {
        return 'Consider using API_ENDPOINTS.BLOG from endpoints.ts';
    }
    if (match.includes('/api/statistics/') || match.includes('/statistics/')) {
        return 'Consider using API_ENDPOINTS.STATISTICS from endpoints.ts';
    }
    if (match.includes('/api/testimonials/') || match.includes('/testimonials/')) {
        return 'Consider using API_ENDPOINTS.TESTIMONIAL from endpoints.ts';
    }

    return 'Consider using centralized API_ENDPOINTS or API_ROUTES from src/services/http/endpoints.ts';
}

/**
 * Validate a single file for hardcoded API paths
 */
function validateFile(filePath: string): ValidationIssue[] {
    const issues: ValidationIssue[] = [];

    try {
        // Check if file should be excluded
        if (CONFIG.excludedFiles.some(excluded => filePath.includes(excluded))) {
            return issues;
        }

        const content = fs.readFileSync(filePath, 'utf8');

        API_PATH_PATTERNS.forEach(({ pattern, description, severity }) => {
            let match;

            // Reset pattern for each file
            pattern.lastIndex = 0;

            while ((match = pattern.exec(content)) !== null) {
                const fullMatch = match[0];
                const extractedPath = match[1] || fullMatch;

                // Check if this path should be flagged
                if (shouldFlagPath(extractedPath, content)) {
                    const { line, column } = getLineAndColumn(content, match.index);
                    const context = getContext(content, match.index, fullMatch.length);

                    issues.push({
                        file: filePath,
                        line,
                        column,
                        match: fullMatch,
                        context,
                        severity,
                        suggestion: generateSuggestion(fullMatch)
                    });
                }
            }
        });

    } catch (error) {
        console.error(`Error reading file ${filePath}:`, error instanceof Error ? error.message : error);
    }

    return issues;
}

/**
 * Main validation function
 */
async function validateApiPaths(): Promise<void> {
    console.log('🔍 Scanning for hardcoded API paths...\n');

    let allFiles: string[] = [];

    try {
        // Get all matching files
        for (const pattern of CONFIG.filePatterns) {
            const files = await glob(pattern, {
                ignore: CONFIG.excludedPaths.map(p => `**/${p}/**`),
                absolute: false
            });
            allFiles.push(...files);
        }

        // Remove duplicates
        allFiles = [...new Set(allFiles)];

        console.log(`📁 Found ${allFiles.length} files to analyze`);

    } catch (error) {
        console.error('Error finding files:', error instanceof Error ? error.message : error);
        process.exit(1);
    }

    const allIssues: ValidationIssue[] = [];

    // Validate each file
    allFiles.forEach(file => {
        // Skip excluded paths
        if (CONFIG.excludedPaths.some(exclude => file.includes(exclude))) {
            return;
        }

        const issues = validateFile(file);
        allIssues.push(...issues);
    });

    // Report results
    if (allIssues.length > 0) {
        console.log(`\n⚠️  Found ${allIssues.length} potential hardcoded API paths:\n`);

        // Group by severity
        const errors = allIssues.filter(issue => issue.severity === 'error');
        const warnings = allIssues.filter(issue => issue.severity === 'warning');

        // Display errors first
        if (errors.length > 0) {
            console.log('🚨 ERRORS (must fix):');
            errors.forEach(({ file, line, column, match, context, suggestion }) => {
                console.log(`  📄 ${file}:${line}:${column}`);
                console.log(`     Match: ${match}`);
                console.log(`     Context: ...${context}...`);
                if (suggestion) {
                    console.log(`     💡 ${suggestion}`);
                }
                console.log('');
            });
        }

        // Display warnings
        if (warnings.length > 0) {
            console.log('⚠️  WARNINGS (should review):');
            warnings.forEach(({ file, line, column, match, context, suggestion }) => {
                console.log(`  📄 ${file}:${line}:${column}`);
                console.log(`     Match: ${match}`);
                console.log(`     Context: ...${context}...`);
                if (suggestion) {
                    console.log(`     💡 ${suggestion}`);
                }
                console.log('');
            });
        }

        console.log('📋 Summary:');
        console.log(`   - ${errors.length} errors found`);
        console.log(`   - ${warnings.length} warnings found`);
        console.log('\n🔧 Please use centralized API_ENDPOINTS or API_ROUTES from src/services/http/endpoints.ts');

        // Exit with error code if errors found
        if (errors.length > 0) {
            process.exit(1);
        }

    } else {
        console.log('✅ No hardcoded API paths found! Great job! 🎉');
    }
}

/**
 * CLI argument parsing
 */
function parseArgs(): { verbose: boolean; fix: boolean } {
    const args = process.argv.slice(2);
    return {
        verbose: args.includes('--verbose') || args.includes('-v'),
        fix: args.includes('--fix') || args.includes('-f')
    };
}

/**
 * Display help information
 */
function showHelp(): void {
    console.log(`
API Path Validation Tool v2.0.0

Usage: node tools/validateApiPaths.js [options]

Options:
  -v, --verbose    Show detailed output
  -f, --fix        Show fix suggestions (default: enabled)
  -h, --help       Show this help message

Examples:
  node tools/validateApiPaths.js
  node tools/validateApiPaths.js --verbose

The tool will:
1. Scan all TypeScript/JavaScript files in src/
2. Look for hardcoded API paths
3. Suggest using centralized API_ENDPOINTS or API_ROUTES
4. Exit with code 1 if errors are found (useful for CI/CD)
`);
}

// Main execution
if (require.main === module) {
    const args = parseArgs();

    if (process.argv.includes('--help') || process.argv.includes('-h')) {
        showHelp();
        process.exit(0);
    }

    validateApiPaths().catch(error => {
        console.error('💥 Validation failed:', error instanceof Error ? error.message : error);
        process.exit(1);
    });
}

export { validateApiPaths, validateFile, ValidationIssue };
