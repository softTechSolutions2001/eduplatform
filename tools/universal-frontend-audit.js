#!/usr/bin/env node
/**
 * Universal Frontend Audit Tool
 * A comprehensive static and runtime analysis tool for frontend codebases
 * 
 * Features:
 * - Framework-agnostic analysis (React, Vue, Angular, Svelte)
 * - Static code analysis with AST parsing
 * - Runtime performance metrics
 * - Accessibility compliance checking
 * - Best practices enforcement
 * - Security vulnerability detection
 * - Comprehensive reporting
 */

// Core dependencies
const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const { performance } = require('perf_hooks');
const { promisify } = require('util');
const { createHash } = require('crypto');
const readline = require('readline');

// Try to load optional dependencies
let parsers = {
  javascript: null,
  typescript: null,
  vue: null,
  svelte: null,
  html: null,
  css: null
};

let tools = {
  eslint: null,
  cssValidator: null,
  lighthouse: null,
  axe: null,
  puppeteer: null
};

// Safely require packages
function safeRequire(packageName, alias = null) {
  try {
    return require(packageName);
  } catch (error) {
    console.log(`⚠️ Optional dependency ${packageName} not found. Some features will be disabled.`);
    return null;
  }
}

// Load parsers
parsers.javascript = safeRequire('@babel/parser');
parsers.typescript = safeRequire('@typescript/parser');
parsers.vue = safeRequire('vue-template-compiler');
parsers.svelte = safeRequire('svelte/compiler');
parsers.html = safeRequire('node-html-parser');
parsers.css = safeRequire('css-tree');

// Load tools
tools.eslint = safeRequire('eslint');
tools.cssValidator = safeRequire('css-validator');
tools.lighthouse = safeRequire('lighthouse');
tools.axe = safeRequire('@axe-core/puppeteer');
tools.puppeteer = safeRequire('puppeteer');

// Enhanced configuration with framework detection
const CONFIG = {
  // Core settings
  scanDirs: ['./src'],
  outputDir: './audit-results',
  
  // Analysis options
  analysis: {
    static: true,           // Static code analysis
    runtime: true,          // Runtime analysis
    dependencies: true,     // Dependency analysis
    security: true,         // Security scanning
    performance: true,      // Performance metrics
    accessibility: true,    // A11y compliance
    bestPractices: true     // Best practices enforcement
  },

  // File types
  fileTypes: {
    // JavaScript and TypeScript
    code: ['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'],
    
    // Component files
    components: ['.jsx', '.tsx', '.vue', '.svelte'],
    
    // Styling files
    styles: ['.css', '.scss', '.sass', '.less', '.styl', '.pcss'],
    
    // Template files
    templates: ['.html', '.ejs', '.pug', '.hbs', '.njk'],
    
    // Config files
    configs: [
      'package.json', '.eslintrc', '.prettierrc', 'tsconfig.json', 
      'babel.config.js', 'webpack.config.js', 'vite.config.js'
    ]
  },

  // Framework-specific patterns
  frameworks: {
    react: {
      imports: ['react', 'react-dom', 'next', 'preact'],
      components: ['useState', 'useEffect', 'Component', 'React.Component'],
      filePatterns: ['.jsx', '.tsx', '/react/', '/pages/']
    },
    vue: {
      imports: ['vue', 'nuxt', '@vue/'],
      components: ['defineComponent', 'createApp', 'onMounted'],
      filePatterns: ['.vue', 'Vue.extend', '/components/']
    },
    angular: {
      imports: ['@angular/core', '@angular/common'],
      components: ['Component', 'NgModule', 'Injectable'],
      filePatterns: ['.component.ts', '.module.ts', '.service.ts']
    },
    svelte: {
      imports: ['svelte', 'svelte/store'],
      components: ['onMount', 'onDestroy', 'createEventDispatcher'],
      filePatterns: ['.svelte', '<script>', '<style>']
    }
  },

  // Component patterns to analyze
  patterns: {
    // UI component patterns
    components: ['Button', 'Card', 'Modal', 'Form', 'Input', 'Select', 'Table', 'List', 'Menu', 'Nav', 
                'Header', 'Footer', 'Layout', 'Container', 'Grid', 'Flex', 'Box', 'Text', 'Image'],
    
    // State management patterns
    state: ['useState', 'useReducer', 'store', 'createStore', 'State', 'Observable', 'Subject', 'BehaviorSubject'],
    
    // Styling patterns (expanded)
    styles: [
      // Utility classes
      'container', 'flex', 'grid', 'block', 'inline', 'hidden', 'visible',
      'relative', 'absolute', 'fixed', 'sticky', 'static',
      
      // Text utilities
      'text-', 'font-', 'italic', 'underline', 'uppercase', 'lowercase',
      
      // Spacing utilities
      'p-', 'pt-', 'pr-', 'pb-', 'pl-', 'px-', 'py-',
      'm-', 'mt-', 'mr-', 'mb-', 'ml-', 'mx-', 'my-',
      'gap-', 'space-',
      
      // Color utilities
      'bg-', 'text-', 'border-', 'fill-', 'stroke-',
      
      // Size utilities
      'w-', 'h-', 'min-w-', 'min-h-', 'max-w-', 'max-h-',
      
      // Effects
      'shadow-', 'opacity-', 'rounded-', 'border-'
    ],
    
    // Accessibility patterns
    a11y: ['aria-', 'role=', 'tabIndex', 'alt=', 'title=', 'lang=', 'sr-only']
  },
  
  // File path patterns for categorization 
  fileTypePatterns: [
    { type: 'page', patterns: ['/pages/', '/views/', '/screens/', '.page.', '.view.', '.screen.'] },
    { type: 'component', patterns: ['/components/', '/ui/', '.component.'] },
    { type: 'hook', patterns: ['/hooks/', '.hook.', 'use', '.use.'] },
    { type: 'store', patterns: ['/store/', '/stores/', '/state/', '.store.', '.state.'] },
    { type: 'context', patterns: ['/contexts/', '/providers/', '.context.', '.provider.'] },
    { type: 'util', patterns: ['/utils/', '/helpers/', '/lib/', '.util.', '.helper.'] },
    { type: 'service', patterns: ['/services/', '/api/', '.service.', '.api.'] },
    { type: 'model', patterns: ['/models/', '/types/', '/interfaces/', '.model.', '.type.', '.interface.'] },
    { type: 'style', patterns: ['/styles/', '/css/', '/scss/', '.style.', '.css', '.scss'] },
    { type: 'test', patterns: ['/tests/', '/test/', '/spec/', '.test.', '.spec.'] },
    { type: 'config', patterns: ['/config/', '.config.'] },
  ],

  // Exclusion patterns
  exclude: {
    dirs: ['node_modules', 'dist', 'build', '.git', 'coverage', '.next', '.nuxt', '.svelte-kit'],
    files: ['*.min.js', '*.bundle.js', '.d.ts'],
    content: ['@generated', '@deprecated']
  },
  
  // Security checks
  securityChecks: {
    patterns: [
      { name: 'Hard-coded API key', pattern: /api[_-]?key["\s]*[:=]["\s]*['"]([a-zA-Z0-9_\-]{20,})['"]/ },
      { name: 'Hard-coded credential', pattern: /(password|passwd|pwd|secret)["\s]*[:=]["\s]*['"]([^'"]{4,})['"]/ },
      { name: 'Insecure randomness', pattern: /Math\.random\(\)/ },
      { name: 'Insecure DOM', pattern: /(innerHTML|outerHTML|document\.write|eval\(|new Function\()/ },
      { name: 'Potential XSS', pattern: /dangerouslySetInnerHTML|v-html|[^_]html:/ },
      { name: 'Potential SQL Injection', pattern: /executeQuery|executeUpdate|createStatement/ },
      { name: 'Console statements', pattern: /console\.(log|debug|info|warn|error)/ }
    ]
  },
  
  // Runtime analysis settings
  runtime: {
    baseUrl: 'http://localhost:3000',
    routes: ['/'],
    viewport: { width: 1280, height: 800 },
    screenSizes: [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1280, height: 800 }
    ],
    lighthouse: true,
    axe: true,
    screenshots: true,
    performanceMetrics: true,
    browserStack: false
  }
};

// Enhanced results structure
const results = {
  summary: {
    startTime: null,
    endTime: null,
    duration: null,
    detectedFramework: null,
    totalFiles: 0,
    totalLines: 0,
    fileTypes: {},
    frameworks: {},
    issues: {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0
    }
  },
  
  static: {
    componentAnalysis: [],
    fileAnalysis: [],
    dependencyGraph: {},
    duplicationData: {},
    complexityData: {},
    securityIssues: [],
    bestPracticeIssues: [],
    accessibilityIssues: []
  },
  
  runtime: {
    performanceMetrics: {},
    a11yViolations: [],
    consoleMessages: [],
    resourceUsage: {},
    screenshots: {}
  }
};

// Framework detection function
function detectFramework(files) {
  const frameworkScores = {
    react: 0,
    vue: 0,
    angular: 0,
    svelte: 0
  };
  
  // Check package.json
  try {
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    const allDeps = { 
      ...packageJson.dependencies || {}, 
      ...packageJson.devDependencies || {} 
    };
    
    // Check for framework dependencies
    Object.keys(allDeps).forEach(dep => {
      if (dep === 'react' || dep === 'react-dom' || dep.startsWith('react-')) {
        frameworkScores.react += 10;
      } else if (dep === 'vue' || dep.startsWith('@vue/')) {
        frameworkScores.vue += 10;
      } else if (dep === '@angular/core' || dep.startsWith('@angular/')) {
        frameworkScores.angular += 10;
      } else if (dep === 'svelte' || dep.startsWith('svelte-')) {
        frameworkScores.svelte += 10;
      }
    });
    
    // Check for framework-specific configuration files
    if (allDeps['next'] || fs.existsSync('next.config.js')) {
      frameworkScores.react += 5;
    }
    if (allDeps['nuxt'] || fs.existsSync('nuxt.config.js')) {
      frameworkScores.vue += 5;
    }
    if (allDeps['@sveltejs/kit'] || fs.existsSync('svelte.config.js')) {
      frameworkScores.svelte += 5;
    }
    if (fs.existsSync('angular.json')) {
      frameworkScores.angular += 5;
    }
    
  } catch (error) {
    console.log('⚠️ Could not analyze package.json');
  }
  
  // Look at file patterns
  files.forEach(file => {
    const ext = path.extname(file);
    const content = fs.readFileSync(file, 'utf8');
    
    // Check file extensions
    if (ext === '.jsx' || ext === '.tsx') {
      frameworkScores.react += 2;
    } else if (ext === '.vue') {
      frameworkScores.vue += 3;
    } else if (ext === '.svelte') {
      frameworkScores.svelte += 3;
    } else if (file.includes('.component.ts')) {
      frameworkScores.angular += 2;
    }
    
    // Check imports
    Object.entries(CONFIG.frameworks).forEach(([framework, patterns]) => {
      patterns.imports.forEach(importPattern => {
        if (content.includes(`from '${importPattern}'`) || 
            content.includes(`from "${importPattern}"`)) {
          frameworkScores[framework] += 1;
        }
      });
      
      // Check component patterns
      patterns.components.forEach(componentPattern => {
        if (content.includes(componentPattern)) {
          frameworkScores[framework] += 0.5;
        }
      });
    });
  });
  
  // Determine primary framework
  const primaryFramework = Object.entries(frameworkScores)
    .sort((a, b) => b[1] - a[1])[0];
    
  // Only assign if score is significant
  results.summary.frameworks = frameworkScores;
  
  if (primaryFramework[1] > 5) {
    console.log(`📊 Detected primary framework: ${primaryFramework[0]} (score: ${primaryFramework[1]})`);
    return primaryFramework[0];
  }
  
  console.log('📊 No dominant framework detected. Treating as vanilla JS/HTML/CSS.');
  return 'vanilla';
}

// Helper: Get relative path
function getRelativePath(absolutePath) {
  const basePath = process.cwd();
  return path.relative(basePath, absolutePath);
}

// Helper: Get file type based on path
function getFileType(filePath) {
  for (const { type, patterns } of CONFIG.fileTypePatterns) {
    if (patterns.some(pattern => filePath.includes(pattern))) {
      return type;
    }
  }
  return 'other';
}

// Find all relevant files in the provided directories
function findFiles(directories) {
  let targetFiles = [];
  const startTime = performance.now();
  const scannedDirs = new Set();
  
  directories.forEach(dir => {
    const resolvedDir = path.resolve(dir);
    if (!fs.existsSync(resolvedDir)) {
      console.log(`⚠️ Directory not found: ${resolvedDir}`);
      return;
    }
    
    scanDir(resolvedDir);
  });
  
  function scanDir(currentDir) {
    // Prevent infinite loops with symbolic links
    if (scannedDirs.has(currentDir)) return;
    scannedDirs.add(currentDir);
    
    try {
      const items = fs.readdirSync(currentDir);
      
      for (const item of items) {
        // Skip excluded directories and files
        if (CONFIG.exclude.dirs.some(excludeDir => item === excludeDir || item.startsWith(excludeDir + '/'))) {
          continue;
        }
        
        const fullPath = path.join(currentDir, item);
        
        // Use try-catch for each file/directory to make the process more robust
        try {
          const stat = fs.statSync(fullPath);
          
          if (stat.isDirectory()) {
            scanDir(fullPath);
          } else if (stat.isFile()) {
            const ext = path.extname(item).toLowerCase();
            
            // Skip excluded file patterns
            if (CONFIG.exclude.files.some(pattern => {
              if (pattern.startsWith('*.')) {
                return ext === pattern.substring(1);
              }
              return item.includes(pattern);
            })) {
              continue;
            }
            
            // Check if file extension matches any of our target extensions
            const allExtensions = [
              ...CONFIG.fileTypes.code, 
              ...CONFIG.fileTypes.components,
              ...CONFIG.fileTypes.styles, 
              ...CONFIG.fileTypes.templates
            ];
            
            if (allExtensions.includes(ext) || CONFIG.fileTypes.configs.includes(item)) {
              targetFiles.push(fullPath);
            }
          }
        } catch (innerError) {
          console.log(`⚠️ Error processing ${fullPath}: ${innerError.message}`);
        }
      }
    } catch (error) {
      console.log(`⚠️ Error scanning directory ${currentDir}: ${error.message}`);
    }
  }
  
  const endTime = performance.now();
  console.log(`📂 Found ${targetFiles.length} files in ${((endTime - startTime) / 1000).toFixed(2)}s`);
  
  return targetFiles;
}

// Get detailed file metadata including git history when available
function getFileMetadata(filePath) {
  const relativePath = getRelativePath(filePath);
  const result = {
    path: relativePath,
    extension: path.extname(filePath).toLowerCase(),
    size: 0,
    lines: 0,
    created: null,
    modified: null,
    git: null,
    content: null,
    hash: null
  };
  
  try {
    // Get file stats
    const stats = fs.statSync(filePath);
    result.size = stats.size;
    result.created = stats.birthtime;
    result.modified = stats.mtime;
    
    // Read content
    const content = fs.readFileSync(filePath, 'utf8');
    result.content = content;
    result.lines = content.split('\n').length;
    
    // Generate content hash for cache invalidation
    result.hash = createHash('md5').update(content).digest('hex');
    
    // Try to get git info
    try {
      const lastCommitInfo = execSync(
        `git log -1 --format="%H|%an|%ae|%ad|%s" -- "${filePath}"`, 
        { encoding: 'utf8' }
      ).trim();
      
      if (lastCommitInfo && lastCommitInfo !== '') {
        const [hash, author, email, date, message] = lastCommitInfo.split('|');
        result.git = { hash, author, email, date, message };
      }
      
      // Get number of commits for this file
      const commitCount = execSync(
        `git rev-list --count HEAD -- "${filePath}"`,
        { encoding: 'utf8' }
      ).trim();
      
      if (commitCount && commitCount !== '') {
        result.git = result.git || {};
        result.git.commitCount = parseInt(commitCount, 10) || 0;
      }
    } catch (gitError) {
      // Git info is optional, so just continue without it
    }
    
  } catch (error) {
    console.log(`⚠️ Error reading file ${relativePath}: ${error.message}`);
    result.error = error.message;
  }
  
  return result;
}

// Process a file using the appropriate parser
function processFile(filePath) {
  console.log(`🔍 Analyzing ${getRelativePath(filePath)}...`);
  
  // Get file metadata
  const metadata = getFileMetadata(filePath);
  if (metadata.error) {
    return {
      path: metadata.path,
      error: metadata.error
    };
  }
  
  const content = metadata.content;
  const fileType = getFileType(filePath);
  
  // Increment file type counter
  results.summary.totalFiles++;
  results.summary.totalLines += metadata.lines;
  
  if (!results.summary.fileTypes[fileType]) {
    results.summary.fileTypes[fileType] = 0;
  }
  results.summary.fileTypes[fileType]++;
  
  // Initialize file result
  const fileResult = {
    path: metadata.path,
    type: fileType,
    metadata: {
      extension: metadata.extension,
      size: metadata.size,
      lines: metadata.lines,
      created: metadata.created,
      modified: metadata.modified,
      git: metadata.git
    },
    content: {
      imports: [],
      exports: [],
      dependencies: [],
      hooks: [],
      components: {},
      state: {},
      styles: [],
      security: [],
      accessibility: []
    },
    metrics: {
      complexity: 0,
      maintainability: 0,
      dependencies: 0,
      depth: 0
    },
    issues: []
  };
  
  // Process file according to type
  try {
    const ext = metadata.extension;
    
    // JavaScript/TypeScript processing
    if (CONFIG.fileTypes.code.includes(ext)) {
      analyzeCodeFile(fileResult, content, ext);
    }
    
    // Component file processing
    if (CONFIG.fileTypes.components.includes(ext)) {
      analyzeComponentFile(fileResult, content, ext);
    }
    
    // Style file processing
    if (CONFIG.fileTypes.styles.includes(ext)) {
      analyzeStyleFile(fileResult, content, ext);
    }
    
    // Template file processing
    if (CONFIG.fileTypes.templates.includes(ext)) {
      analyzeTemplateFile(fileResult, content, ext);
    }
    
    // Generic analysis for all file types
    analyzeFileContent(fileResult, content);
    
    // Analyze metrics
    calculateMetrics(fileResult, content);
    
    // Scan for security issues
    scanForSecurityIssues(fileResult, content);
    
    // Scan for accessibility issues
    scanForA11yIssues(fileResult, content);
    
    // Add result to array
    results.static.fileAnalysis.push(fileResult);
    return fileResult;
    
  } catch (error) {
    console.error(`⚠️ Error analyzing ${metadata.path}: ${error.message}`);
    fileResult.error = error.message;
    results.static.fileAnalysis.push(fileResult);
    return fileResult;
  }
}

// Analyze JavaScript/TypeScript file
function analyzeCodeFile(fileResult, content, extension) {
  // Extract imports using AST or regex
  if (parsers.javascript) {
    try {
      // Use AST parser
      const ast = parsers.javascript.parse(content, {
        sourceType: 'module',
        plugins: [
          'jsx',
          'typescript',
          'classProperties',
          'dynamicImport'
        ]
      });
      
      // Process AST for imports, exports, and more
      traverseAst(ast, fileResult);
    } catch (error) {
      // Fall back to regex if AST parsing fails
      console.log(`⚠️ AST parsing failed for ${fileResult.path}, using regex fallback`);
      analyzeCodeWithRegex(fileResult, content);
    }
  } else {
    // No AST parser available, use regex
    analyzeCodeWithRegex(fileResult, content);
  }
  
  // Calculate complexity
  fileResult.metrics.complexity = calculateComplexity(content);
}

// Analyze code using AST
function traverseAst(ast, fileResult) {
  // Simple AST traversal for imports and exports
  if (ast.program && ast.program.body) {
    for (const node of ast.program.body) {
      // Import declarations
      if (node.type === 'ImportDeclaration') {
        const source = node.source.value;
        const importedItems = [];
        
        if (node.specifiers) {
          for (const specifier of node.specifiers) {
            if (specifier.imported) {
              importedItems.push(specifier.imported.name);
            } else if (specifier.local) {
              importedItems.push(specifier.local.name);
            }
          }
        }
        
        fileResult.content.imports.push({
          source,
          imported: importedItems,
          line: node.loc ? node.loc.start.line : null
        });
        
        // Track dependencies
        fileResult.content.dependencies.push(source);
      }
      
      // Export declarations
      if (node.type === 'ExportNamedDeclaration' || node.type === 'ExportDefaultDeclaration') {
        let exportName = 'default';
        
        if (node.declaration && node.declaration.id) {
          exportName = node.declaration.id.name;
        } else if (node.declaration && node.declaration.declarations) {
          for (const decl of node.declaration.declarations) {
            if (decl.id && decl.id.name) {
              exportName = decl.id.name;
            }
          }
        }
        
        fileResult.content.exports.push({
          name: exportName,
          isDefault: node.type === 'ExportDefaultDeclaration',
          line: node.loc ? node.loc.start.line : null
        });
      }
      
      // Function declarations (could be components or hooks)
      if (node.type === 'FunctionDeclaration' && node.id && node.id.name) {
        const name = node.id.name;
        
        // Check if it's a hook
        if (name.startsWith('use') && /^use[A-Z]/.test(name)) {
          fileResult.content.hooks.push({
            name,
            line: node.loc ? node.loc.start.line : null,
            params: node.params ? node.params.length : 0
          });
        }
        
        // Check if it could be a component
        else if (name[0] === name[0].toUpperCase()) {
          fileResult.content.components[name] = {
            type: 'function',
            line: node.loc ? node.loc.start.line : null
          };
        }
      }
      
      // Class declarations (could be components)
      if (node.type === 'ClassDeclaration' && node.id && node.id.name) {
        const name = node.id.name;
        
        if (name[0] === name[0].toUpperCase()) {
          let isComponent = false;
          
          // Check if it extends React.Component or Component
          if (node.superClass) {
            if (node.superClass.type === 'MemberExpression' && 
                node.superClass.object.name === 'React' && 
                node.superClass.property.name === 'Component') {
              isComponent = true;
            } else if (node.superClass.type === 'Identifier' && 
                      node.superClass.name === 'Component') {
              isComponent = true;
            }
          }
          
          fileResult.content.components[name] = {
            type: 'class',
            isComponent,
            line: node.loc ? node.loc.start.line : null
          };
        }
      }
    }
  }
}

// Fallback to regex analysis for code files
function analyzeCodeWithRegex(fileResult, content) {
  const lines = content.split('\n');
  
  // Import analysis
  const importLines = lines.filter(line => line.trim().startsWith('import '));
  importLines.forEach(line => {
    const importMatch = line.match(/import\s+(.+?)\s+from\s+['"](.+?)['"]/);
    if (importMatch) {
      const [, imported, source] = importMatch;
      fileResult.content.imports.push({
        source,
        imported: imported.trim(),
        line: lines.indexOf(line) + 1
      });
      
      fileResult.content.dependencies.push(source);
    }
  });
  
  // Export analysis
  const exportLines = lines.filter(line => 
    line.trim().startsWith('export ') || 
    line.trim().startsWith('module.exports')
  );
  exportLines.forEach(line => {
    let name = 'default';
    let isDefault = line.includes('export default');
    
    const namedExportMatch = line.match(/export\s+(?:const|let|var|function|class)\s+(\w+)/);
    if (namedExportMatch) {
      name = namedExportMatch[1];
    }
    
    fileResult.content.exports.push({
      name,
      isDefault,
      line: lines.indexOf(line) + 1
    });
  });
  
  // React hook usage
  const reactHooks = [
    'useState', 'useEffect', 'useContext', 'useReducer',
    'useCallback', 'useMemo', 'useRef', 'useImperativeHandle',
    'useLayoutEffect', 'useDebugValue', 'useSyncExternalStore'
  ];
  
  reactHooks.forEach(hook => {
    const hookRegex = new RegExp(`\\b${hook}\\s*\\(`, 'g');
    const matches = Array.from(content.matchAll(hookRegex));
    
    matches.forEach(match => {
      const pos = match.index;
      const lineNumber = content.substring(0, pos).split('\n').length;
      
      fileResult.content.hooks.push({
        name: hook,
        line: lineNumber,
        isBuiltIn: true
      });
    });
  });
  
  // Custom hooks
  const customHookRegex = /\buse[A-Z]\w*\s*\(/g;
  const customHookMatches = Array.from(content.matchAll(customHookRegex));
  
  customHookMatches.forEach(match => {
    const hookName = match[0].slice(0, -1).trim(); // Remove the trailing (
    if (!reactHooks.includes(hookName)) {
      const pos = match.index;
      const lineNumber = content.substring(0, pos).split('\n').length;
      
      fileResult.content.hooks.push({
        name: hookName,
        line: lineNumber,
        isCustom: true
      });
    }
  });
  
  // Component detection
  const componentPatterns = [
    /function\s+([A-Z]\w+)\s*\(/g,
    /const\s+([A-Z]\w+)\s*=\s*\(?/g,
    /class\s+([A-Z]\w+)\s+extends/g
  ];
  
  componentPatterns.forEach(pattern => {
    const matches = Array.from(content.matchAll(pattern));
    
    matches.forEach(match => {
      const componentName = match[1];
      const pos = match.index;
      const lineNumber = content.substring(0, pos).split('\n').length;
      
      fileResult.content.components[componentName] = {
        type: pattern.toString().includes('class') ? 'class' : 'function',
        line: lineNumber
      };
    });
  });
}

/**
 * Analyze component files (React, Vue, Svelte)
 * @param {object} fileResult - Result object to populate
 * @param {string} content - File content
 * @param {string} extension - File extension
 */
function analyzeComponentFile(fileResult, content, extension) {
  // Handle different component types based on extension
  if (extension === '.vue') {
    analyzeVueComponent(fileResult, content);
  } else if (extension === '.svelte') {
    analyzeSvelteComponent(fileResult, content);
  } else if (['.jsx', '.tsx'].includes(extension)) {
    // JSX/TSX files are already analyzed by the code analyzer
    // Here we can add additional React-specific component analysis
    analyzeReactComponent(fileResult, content);
  }
  
  // Detect component props
  detectComponentProps(fileResult, content, extension);
  
  // Detect component state
  detectComponentState(fileResult, content, extension);
}

/**
 * Analyze Vue component
 * @param {object} fileResult - Result object to populate
 * @param {string} content - File content
 */
function analyzeVueComponent(fileResult, content) {
  if (!parsers.vue) {
    console.log('⚠️ Vue template compiler not available for parsing Vue components');
    return;
  }
  
  try {
    const parsed = parsers.vue.parseComponent(content);
    
    // Extract script content
    if (parsed.script) {
      const scriptContent = parsed.script.content;
      
      // Look for component name
      const nameMatch = scriptContent.match(/name:\s*['"](.+?)['"]/);
      if (nameMatch) {
        const componentName = nameMatch[1];
        fileResult.content.components[componentName] = {
          type: 'vue-component',
          template: parsed.template ? true : false,
          style: parsed.styles && parsed.styles.length > 0
        };
      }
      
      // Look for props
      const propsMatch = scriptContent.match(/props:\s*{([^}]+)}/);
      if (propsMatch) {
        const propsContent = propsMatch[1];
        const propNames = propsContent.split(',').map(prop => {
          const match = prop.match(/(\w+):/);
          return match ? match[1].trim() : null;
        }).filter(Boolean);
        
        propNames.forEach(prop => {
          fileResult.content.components.props = fileResult.content.components.props || {};
          fileResult.content.components.props[prop] = { type: 'unknown', required: false };
        });
      }
      
      // Look for data
      const dataMatch = scriptContent.match(/data\s*\(\s*\)\s*{[^]*?return\s*{([^}]+)}/);
      if (dataMatch) {
        const dataContent = dataMatch[1];
        const dataProps = dataContent.split(',').map(prop => {
          const match = prop.match(/(\w+):/);
          return match ? match[1].trim() : null;
        }).filter(Boolean);
        
        dataProps.forEach(prop => {
          fileResult.content.state[prop] = { type: 'vue-data' };
        });
      }
    }
    
    // Extract template content
    if (parsed.template) {
      const templateContent = parsed.template.content;
      
      // Look for components used in template
      CONFIG.patterns.components.forEach(component => {
        const componentRegex = new RegExp(`<${component}[\\s>]`, 'g');
        const matches = templateContent.match(componentRegex);
        if (matches) {
          fileResult.content.components.used = fileResult.content.components.used || {};
          fileResult.content.components.used[component] = matches.length;
        }
      });
    }
    
    // Extract style content
    if (parsed.styles && parsed.styles.length > 0) {
      parsed.styles.forEach(style => {
        analyzeStyleContent(fileResult, style.content);
      });
    }
    
  } catch (error) {
    console.log(`⚠️ Error parsing Vue component ${fileResult.path}: ${error.message}`);
  }
}

/**
 * Analyze Svelte component
 * @param {object} fileResult - Result object to populate
 * @param {string} content - File content
 */
function analyzeSvelteComponent(fileResult, content) {
  if (!parsers.svelte) {
    console.log('⚠️ Svelte compiler not available for parsing Svelte components');
    return;
  }
  
  try {
    const parsed = parsers.svelte.parse(content);
    
    // Extract script content
    const scriptTag = parsed.instance;
    if (scriptTag) {
      const scriptContent = content.substring(scriptTag.start, scriptTag.end);
      
      // Look for exported variables (props)
      const exportMatches = scriptContent.match(/export\s+let\s+(\w+)(\s*=\s*[^;]+)?;/g);
      if (exportMatches) {
        exportMatches.forEach(match => {
          const propMatch = match.match(/export\s+let\s+(\w+)/);
          if (propMatch) {
            const propName = propMatch[1];
            fileResult.content.components.props = fileResult.content.components.props || {};
            fileResult.content.components.props[propName] = { type: 'svelte-prop' };
          }
        });
      }
      
      // Look for regular variables (state)
      const letMatches = scriptContent.match(/let\s+(\w+)(\s*=\s*[^;]+)?;/g);
      if (letMatches) {
        letMatches.forEach(match => {
          const varMatch = match.match(/let\s+(\w+)/);
          if (varMatch) {
            const varName = varMatch[1];
            fileResult.content.state[varName] = { type: 'svelte-state' };
          }
        });
      }
    }
    
    // Extract style content
    const styleTag = parsed.css;
    if (styleTag) {
      const styleContent = content.substring(styleTag.start, styleTag.end);
      analyzeStyleContent(fileResult, styleContent);
    }
    
  } catch (error) {
    console.log(`⚠️ Error parsing Svelte component ${fileResult.path}: ${error.message}`);
  }
}

/**
 * Analyze React component
 * @param {object} fileResult - Result object to populate
 * @param {string} content - File content
 */
function analyzeReactComponent(fileResult, content) {
  // Look for prop destructuring in function components
  const propDestructuringMatch = content.match(/function\s+\w+\s*\(\s*{\s*([^}]+)\s*}\s*\)/);
  if (propDestructuringMatch) {
    const props = propDestructuringMatch[1].split(',').map(prop => prop.trim());
    props.forEach(prop => {
      fileResult.content.components.props = fileResult.content.components.props || {};
      fileResult.content.components.props[prop] = { type: 'react-prop' };
    });
  }
  
  // Look for prop type definitions
  const propTypesMatch = content.match(/propTypes\s*=\s*{([^}]+)}/);
  if (propTypesMatch) {
    const propTypes = propTypesMatch[1].split(',').map(prop => {
      const match = prop.match(/(\w+):/);
      return match ? match[1].trim() : null;
    }).filter(Boolean);
    
    propTypes.forEach(prop => {
      fileResult.content.components.props = fileResult.content.components.props || {};
      fileResult.content.components.props[prop] = { type: 'prop-types', validation: true };
    });
  }
  
  // Look for TypeScript interface props
  const tsPropsMatch = content.match(/interface\s+\w+Props\s*{([^}]+)}/);
  if (tsPropsMatch) {
    const propsDef = tsPropsMatch[1];
    const propRegex = /(\w+)(\?)?:\s*([^;]+);/g;
    let match;
    
    while ((match = propRegex.exec(propsDef)) !== null) {
      const [, propName, optional, propType] = match;
      fileResult.content.components.props = fileResult.content.components.props || {};
      fileResult.content.components.props[propName] = { 
        type: propType.trim(), 
        required: !optional
      };
    }
  }
}

/**
 * Detect component props across frameworks
 * @param {object} fileResult - Result object to populate
 * @param {string} content - File content
 * @param {string} extension - File extension
 */
function detectComponentProps(fileResult, content, extension) {
  // This is a more general prop detection that works across frameworks
  const propPatterns = [
    { regex: /props\.\w+/g, framework: 'react' },
    { regex: /this\.props\.\w+/g, framework: 'react-class' },
    { regex: /\{[^}]*\bprops\.\w+/g, framework: 'react' }
  ];
  
  propPatterns.forEach(({ regex, framework }) => {
    const matches = Array.from(content.matchAll(regex));
    matches.forEach(match => {
      const propRef = match[0];
      const propName = propRef.split('.').pop();
      
      if (propName && propName !== 'props') {
        fileResult.content.components.props = fileResult.content.components.props || {};
        if (!fileResult.content.components.props[propName]) {
          fileResult.content.components.props[propName] = { type: framework };
        }
      }
    });
  });
}

/**
 * Detect component state across frameworks
 * @param {object} fileResult - Result object to populate
 * @param {string} content - File content
 * @param {string} extension - File extension
 */
function detectComponentState(fileResult, content, extension) {
  // State hooks in React
  const stateHookRegex = /const\s+\[(\w+),\s*set(\w+)\]\s*=\s*useState/g;
  let match;
  
  while ((match = stateHookRegex.exec(content)) !== null) {
    const [, stateName, setterSuffix] = match;
    const capitalizedStateName = stateName.charAt(0).toUpperCase() + stateName.slice(1);
    
    if (capitalizedStateName === setterSuffix) {
      fileResult.content.state[stateName] = { 
        type: 'react-state-hook',
        setter: `set${setterSuffix}`
      };
    }
  }
  
  // Class component state
  const classStateRegex = /this\.state\.(\w+)/g;
  const classStateMatches = Array.from(content.matchAll(classStateRegex));
  
  classStateMatches.forEach(match => {
    const stateName = match[1];
    fileResult.content.state[stateName] = { type: 'react-class-state' };
  });
  
  // State setters
  const setStateRegex = /this\.setState\(\s*{\s*([^}]+)\s*}\s*\)/g;
  const setStateMatches = Array.from(content.matchAll(setStateRegex));
  
  setStateMatches.forEach(match => {
    const stateUpdates = match[1].split(',').map(update => {
      const updateMatch = update.match(/(\w+):/);
      return updateMatch ? updateMatch[1].trim() : null;
    }).filter(Boolean);
    
    stateUpdates.forEach(stateName => {
      fileResult.content.state[stateName] = fileResult.content.state[stateName] || { 
        type: 'react-class-state' 
      };
    });
  });
}

/**
 * Analyze CSS and other style files
 * @param {object} fileResult - Result object to populate
 * @param {string} content - File content
 * @param {string} extension - File extension
 */
function analyzeStyleFile(fileResult, content, extension) {
  analyzeStyleContent(fileResult, content);
}

/**
 * Analyze CSS content regardless of source
 * @param {object} fileResult - Result object to populate
 * @param {string} content - Style content
 */
function analyzeStyleContent(fileResult, content) {
  // Look for CSS classes
  const classRegex = /\.([\w-]+)\s*[{:]/g;
  const classMatches = Array.from(content.matchAll(classRegex));
  
  classMatches.forEach(match => {
    const className = match[1];
    fileResult.content.styles.push({
      name: className,
      type: 'class'
    });
  });
  
  // Look for CSS variables
  const varRegex = /--[\w-]+:/g;
  const varMatches = Array.from(content.matchAll(varRegex));
  
  varMatches.forEach(match => {
    const varName = match[0].slice(0, -1); // Remove the colon
    fileResult.content.styles.push({
      name: varName,
      type: 'variable'
    });
  });
  
  // Look for media queries
  const mediaQueryRegex = /@media\s*([^{]+)/g;
  const mediaQueryMatches = Array.from(content.matchAll(mediaQueryRegex));
  
  mediaQueryMatches.forEach(match => {
    const query = match[1].trim();
    fileResult.content.styles.push({
      name: query,
      type: 'media-query'
    });
  });
  
  // Look for color values
  const colorRegex = /#[0-9a-f]{3,8}|rgba?\s*\([^)]+\)|hsla?\s*\([^)]+\)/gi;
  const colorMatches = Array.from(content.matchAll(colorRegex));
  
  const uniqueColors = new Set();
  colorMatches.forEach(match => {
    const color = match[0];
    uniqueColors.add(color);
  });
  
  if (uniqueColors.size > 0) {
    fileResult.content.styles.push({
      type: 'colors',
      values: Array.from(uniqueColors)
    });
    
    // If too many hardcoded colors, flag as an issue
    if (uniqueColors.size > 5) {
      fileResult.issues.push({
        severity: 'medium',
        type: 'style',
        message: `Contains ${uniqueColors.size} hardcoded color values`,
        recommendation: 'Use CSS variables or a theme system for colors'
      });
    }
  }
  
  // Look for !important declarations
  const importantRegex = /!important/g;
  const importantMatches = Array.from(content.matchAll(importantRegex));
  
  if (importantMatches.length > 0) {
    fileResult.content.styles.push({
      type: 'important',
      count: importantMatches.length
    });
    
    // If too many !important declarations, flag as an issue
    if (importantMatches.length > 3) {
      fileResult.issues.push({
        severity: 'medium',
        type: 'style',
        message: `Contains ${importantMatches.length} !important declarations`,
        recommendation: 'Avoid using !important by structuring CSS with better specificity'
      });
    }
  }
}

/**
 * Analyze HTML and template files
 * @param {object} fileResult - Result object to populate
 * @param {string} content - File content
 * @param {string} extension - File extension
 */
function analyzeTemplateFile(fileResult, content, extension) {
  if (!parsers.html) {
    console.log('⚠️ HTML parser not available for parsing template files');
    return;
  }
  
  try {
    const root = parsers.html.parse(content);
    
    // Count elements
    const elements = root.querySelectorAll('*');
    fileResult.content.template = {
      elementCount: elements.length
    };
    
    // Look for components
    CONFIG.patterns.components.forEach(component => {
      const componentElements = root.querySelectorAll(component);
      if (componentElements.length > 0) {
        fileResult.content.components.used = fileResult.content.components.used || {};
        fileResult.content.components.used[component] = componentElements.length;
      }
    });
    
    // Look for inline styles
    const inlineStyles = root.querySelectorAll('[style]');
    if (inlineStyles.length > 0) {
      fileResult.content.styles.push({
        type: 'inline-styles',
        count: inlineStyles.length
      });
      
      // Flag as an issue if there are too many
      if (inlineStyles.length > 2) {
        fileResult.issues.push({
          severity: 'medium',
          type: 'style',
          message: `Contains ${inlineStyles.length} inline style attributes`,
          recommendation: 'Use CSS classes instead of inline styles'
        });
      }
    }
    
    // Look for accessibility issues
    scanTemplateForA11yIssues(fileResult, root);
    
  } catch (error) {
    console.log(`⚠️ Error parsing HTML template ${fileResult.path}: ${error.message}`);
  }
}

/**
 * Scan file content for security issues
 * @param {object} fileResult - Result object to populate
 * @param {string} content - File content
 */
function scanForSecurityIssues(fileResult, content) {
  // Check for security issues based on patterns
  CONFIG.securityChecks.patterns.forEach(({ name, pattern }) => {
    const matches = Array.from(content.matchAll(pattern));
    
    if (matches.length > 0) {
      const lines = matches.map(match => {
        const pos = match.index;
        return content.substring(0, pos).split('\n').length;
      });
      
      fileResult.content.security.push({
        type: name,
        count: matches.length,
        lines
      });
      
      // Determine severity based on issue type
      let severity = 'medium';
      if (name.includes('API key') || name.includes('credential')) {
        severity = 'critical';
      } else if (name.includes('XSS') || name.includes('SQL Injection')) {
        severity = 'high';
      } else if (name.includes('Console statements')) {
        severity = 'low';
      }
      
      // Add to issues
      fileResult.issues.push({
        severity,
        type: 'security',
        message: `${name} found (${matches.length} occurrences)`,
        recommendation: getSecurityRecommendation(name),
        lines
      });
      
      // Add to global security issues tracker
      results.static.securityIssues.push({
        file: fileResult.path,
        issue: name,
        severity,
        count: matches.length,
        lines
      });
    }
  });
}

/**
 * Get security recommendation based on issue type
 * @param {string} issueName - Security issue name
 * @returns {string} - Recommendation
 */
function getSecurityRecommendation(issueName) {
  if (issueName.includes('API key')) {
    return 'Move API keys to environment variables or secure storage';
  } else if (issueName.includes('credential')) {
    return 'Remove hardcoded credentials and use secure storage';
  } else if (issueName.includes('randomness')) {
    return 'Use crypto.getRandomValues() for cryptographically secure randomness';
  } else if (issueName.includes('DOM')) {
    return 'Avoid using innerHTML or document.write to prevent XSS attacks';
  } else if (issueName.includes('XSS')) {
    return 'Sanitize content before rendering to prevent XSS attacks';
  } else if (issueName.includes('SQL')) {
    return 'Use parameterized queries or ORM to prevent SQL injection';
  } else if (issueName.includes('Console')) {
    return 'Remove console statements in production code';
  }
  return 'Follow security best practices';
}

/**
 * Scan for accessibility issues in file content
 * @param {object} fileResult - Result object to populate
 * @param {string} content - File content
 */
function scanForA11yIssues(fileResult, content) {
  // Look for common accessibility issues in code
  const a11yIssues = [
    {
      name: 'Missing alt attribute',
      pattern: /<img[^>]*(?!alt=)[^>]*>/g,
      severity: 'high',
      recommendation: 'Add alt attributes to all image elements'
    },
    {
      name: 'Non-semantic button',
      pattern: /<div[^>]*\s+onClick=/g,
      severity: 'medium',
      recommendation: 'Use <button> elements for interactive controls'
    },
    {
      name: 'Missing form labels',
      pattern: /<input[^>]*(?!id=|aria-label=|aria-labelledby=)[^>]*>/g,
      severity: 'high',
      recommendation: 'Add labels to all form controls'
    },
    {
      name: 'Hardcoded tabindex',
      pattern: /tabIndex=['"](\d{2,}|[^01])["']/g,
      severity: 'medium',
      recommendation: 'Avoid using tabIndex values greater than 1'
    }
  ];
  
  a11yIssues.forEach(({ name, pattern, severity, recommendation }) => {
    const matches = Array.from(content.matchAll(pattern));
    
    if (matches.length > 0) {
      const lines = matches.map(match => {
        const pos = match.index;
        return content.substring(0, pos).split('\n').length;
      });
      
      fileResult.content.accessibility.push({
        type: name,
        count: matches.length,
        lines
      });
      
      // Add to issues
      fileResult.issues.push({
        severity,
        type: 'accessibility',
        message: `${name} (${matches.length} occurrences)`,
        recommendation,
        lines
      });
      
      // Add to global accessibility issues tracker
      results.static.accessibilityIssues.push({
        file: fileResult.path,
        issue: name,
        severity,
        count: matches.length,
        lines
      });
    }
  });
}

/**
 * Scan HTML template for accessibility issues
 * @param {object} fileResult - Result object to populate
 * @param {object} root - Parsed HTML root node
 */
function scanTemplateForA11yIssues(fileResult, root) {
  // Check for images without alt attributes
  const imagesWithoutAlt = root.querySelectorAll('img:not([alt])');
  if (imagesWithoutAlt.length > 0) {
    fileResult.content.accessibility.push({
      type: 'Missing alt attribute',
      count: imagesWithoutAlt.length
    });
    
    fileResult.issues.push({
      severity: 'high',
      type: 'accessibility',
      message: `${imagesWithoutAlt.length} images missing alt attributes`,
      recommendation: 'Add descriptive alt attributes to all images'
    });
  }
  
  // Check for inputs without labels
  const inputsWithoutLabel = root.querySelectorAll('input:not([aria-label]):not([aria-labelledby])');
  let unlabeledInputs = 0;
  
  inputsWithoutLabel.forEach(input => {
    const id = input.getAttribute('id');
    if (!id || root.querySelector(`label[for="${id}"]`) === null) {
      unlabeledInputs++;
    }
  });
  
  if (unlabeledInputs > 0) {
    fileResult.content.accessibility.push({
      type: 'Input without label',
      count: unlabeledInputs
    });
    
    fileResult.issues.push({
      severity: 'high',
      type: 'accessibility',
      message: `${unlabeledInputs} inputs without associated labels`,
      recommendation: 'Add labels to all form controls using label elements or aria attributes'
    });
  }
  
  // Check for color contrast issues (simplified heuristic)
  const elementsWithInlineColor = root.querySelectorAll('[style*="color"]');
  let potentialContrastIssues = 0;
  
  elementsWithInlineColor.forEach(element => {
    const style = element.getAttribute('style');
    if (style && style.includes('color') && style.includes('background')) {
      potentialContrastIssues++;
    }
  });
  
  if (potentialContrastIssues > 0) {
    fileResult.content.accessibility.push({
      type: 'Potential contrast issues',
      count: potentialContrastIssues
    });
    
    fileResult.issues.push({
      severity: 'medium',
      type: 'accessibility',
      message: `${potentialContrastIssues} elements with potential color contrast issues`,
      recommendation: 'Ensure sufficient color contrast for text elements'
    });
  }
}

/**
 * Analyze generic file content
 * @param {object} fileResult - Result object to populate
 * @param {string} content - File content
 */
function analyzeFileContent(fileResult, content) {
  // Look for layout component usage
  CONFIG.patterns.components.forEach(component => {
    if (component.toLowerCase().includes('layout') ||
        component.toLowerCase().includes('container') ||
        component.toLowerCase().includes('header') ||
        component.toLowerCase().includes('footer')) {
      const componentRegex = new RegExp(`<${component}[\\s>]`, 'g');
      const matches = content.match(componentRegex);
      if (matches) {
        fileResult.content.components.layout = fileResult.content.components.layout || {};
        fileResult.content.components.layout[component] = matches.length;
      }
    }
  });
  
  // Look for component usage
  CONFIG.patterns.components.forEach(component => {
    const componentRegex = new RegExp(`<${component}[\\s>]`, 'g');
    const matches = content.match(componentRegex);
    if (matches) {
      fileResult.content.components.used = fileResult.content.components.used || {};
      fileResult.content.components.used[component] = matches.length;
    }
  });
  
  // Look for style patterns
  CONFIG.patterns.styles.forEach(pattern => {
    // Flexible pattern matching for different styling approaches
    const classNameRegex = new RegExp(`(className|class)=["'][^"']*${pattern}[^"']*["']`, 'g');
    const styledRegex = new RegExp(`\\b${pattern}\\b`, 'g');
    
    const classMatches = Array.from(content.matchAll(classNameRegex));
    const styledMatches = Array.from(content.matchAll(styledRegex));
    
    const totalMatches = classMatches.length + styledMatches.length;
    
    if (totalMatches > 0) {
      fileResult.content.styles.push({
        pattern,
        count: totalMatches
      });
    }
  });
  
  // Look for inline styles
  const inlineStyleRegex = /style=\{.*?\}/g;
  const inlineStyleMatches = Array.from(content.matchAll(inlineStyleRegex));
  
  if (inlineStyleMatches.length > 0) {
    fileResult.content.styles.push({
      type: 'inline-styles',
      count: inlineStyleMatches.length
    });
    
    // Add as an issue if there are many inline styles
    if (inlineStyleMatches.length > 3) {
      fileResult.issues.push({
        severity: 'medium',
        type: 'style',
        message: `Contains ${inlineStyleMatches.length} inline style declarations`,
        recommendation: 'Replace inline styles with CSS classes or styled components'
      });
    }
  }
  
  // Look for hardcoded colors
  const hexColorRegex = /#[0-9a-f]{3,8}/gi;
  const rgbColorRegex = /rgb\(.*?\)/g;
  const rgbaColorRegex = /rgba\(.*?\)/g;
  
  const hexMatches = content.match(hexColorRegex) || [];
  const rgbMatches = content.match(rgbColorRegex) || [];
  const rgbaMatches = content.match(rgbaColorRegex) || [];
  
  const allColors = [...hexMatches, ...rgbMatches, ...rgbaMatches];
  
  if (allColors.length > 0) {
    fileResult.content.styles.push({
      type: 'hardcoded-colors',
      values: allColors
    });
    
    // Add as an issue if there are many hardcoded colors
    if (allColors.length > 5) {
      fileResult.issues.push({
        severity: 'medium',
        type: 'style',
        message: `Contains ${allColors.length} hardcoded color values`,
        recommendation: 'Use theme variables or design tokens for colors'
      });
    }
  }
  
  // File-type specific issues
  
  // Issue: Pages should use layout components
  if (fileResult.type === 'page') {
    const hasLayout = fileResult.content.components.layout && 
      Object.values(fileResult.content.components.layout).some(count => count > 0);
    
    if (!hasLayout) {
      fileResult.issues.push({
        severity: 'high',
        type: 'layout',
        message: 'Page does not use any layout component',
        recommendation: 'Consider wrapping content with a layout component'
      });
      
      results.summary.inconsistencies = results.summary.inconsistencies || [];
      results.summary.inconsistencies.push({
        path: fileResult.path,
        type: 'missing-layout'
      });
    }
  }
}

/**
 * Calculate complexity metrics for a file
 * @param {object} fileResult - Result object to populate
 * @param {string} content - File content
 */
function calculateMetrics(fileResult, content) {
  // Calculate cyclomatic complexity
  const complexity = calculateComplexity(content);
  fileResult.metrics.complexity = complexity;
  
  // Calculate maintainability index (simplified)
  const halsteadVolume = calculateHalsteadVolume(content);
  const lineCount = content.split('\n').length;
  const commentCount = countComments(content);
  const commentRatio = commentCount / lineCount;
  
  // Simplified maintainability index formula (higher is better)
  const maintainability = Math.max(0, Math.min(100, 
    171 - 5.2 * Math.log(halsteadVolume) - 0.23 * complexity - 16.2 * Math.log(lineCount) + 50 * commentRatio
  ));
  fileResult.metrics.maintainability = Math.round(maintainability);
  
  // Set dependency count
  fileResult.metrics.dependencies = fileResult.content.dependencies.length;
  
  // Calculate nesting depth
  const depth = calculateNestingDepth(content);
  fileResult.metrics.depth = depth;
  
  // Add issues based on metrics
  if (complexity > 20) {
    fileResult.issues.push({
      severity: complexity > 30 ? 'high' : 'medium',
      type: 'complexity',
      message: `High cyclomatic complexity (${complexity})`,
      recommendation: 'Refactor code to reduce complexity, extract functions or components'
    });
  }
  
  if (depth > 4) {
    fileResult.issues.push({
      severity: depth > 6 ? 'high' : 'medium',
      type: 'complexity',
      message: `Deep nesting (depth ${depth})`,
      recommendation: 'Refactor code to reduce nesting, extract functions or components'
    });
  }
  
  if (maintainability < 65) {
    fileResult.issues.push({
      severity: maintainability < 50 ? 'high' : 'medium',
      type: 'maintainability',
      message: `Low maintainability index (${Math.round(maintainability)})`,
      recommendation: 'Improve code structure, add comments, reduce complexity'
    });
  }
  
  if (lineCount > 300) {
    fileResult.issues.push({
      severity: lineCount > 500 ? 'high' : 'medium',
      type: 'size',
      message: `File is too large (${lineCount} lines)`,
      recommendation: 'Split file into smaller modules'
    });
  }
  
  // Update global complexity data
  results.static.complexityData[fileResult.path] = {
    complexity,
    maintainability,
    lineCount,
    depth
  };
}

/**
 * Calculate cyclomatic complexity of code
 * @param {string} content - File content
 * @returns {number} - Complexity score
 */
function calculateComplexity(content) {
  // Base complexity is 1
  let complexity = 1;
  
  // Patterns that increase complexity
  const complexityPatterns = [
    /\bif\s*\(/g,           // if statements
    /\belse\b/g,            // else statements
    /\bswitch\s*\(/g,       // switch statements
    /\bcase\s+/g,           // case statements
    /\bfor\s*\(/g,          // for loops
    /\bwhile\s*\(/g,        // while loops
    /\bdo\s*{/g,            // do-while loops
    /\bcatch\s*\(/g,        // catch statements
    /\breturn\s+.+?\?/g,    // conditional returns
    /\?/g,                  // ternary operators
    /\|\|/g,                // logical OR
    /&&/g,                  // logical AND
    /\.(map|filter|reduce|forEach|some|every)\s*\(/g  // Array methods with callbacks
  ];
  
  // Count occurrences of each pattern
  complexityPatterns.forEach(pattern => {
    const matches = content.match(pattern);
    if (matches) {
      complexity += matches.length;
    }
  });
  
  return complexity;
}

/**
 * Calculate Halstead volume (simplified)
 * @param {string} content - File content
 * @returns {number} - Halstead volume
 */
function calculateHalsteadVolume(content) {
  // Extract operators and operands (simplified)
  const operators = new Set();
  const operands = new Set();
  
  // Common operators in JavaScript
  const operatorPatterns = [
    /[+\-*/%]=?/g,   // Arithmetic operators
    /[&|^]=?/g,      // Bitwise operators
    /[=!]==?/g,      // Equality operators
    /[<>]=?/g,       // Comparison operators
    /&&|\|\|/g,      // Logical operators
    /\?|:/g,         // Conditional operator
    /\bnew\b/g,      // new operator
    /\bdelete\b/g,   // delete operator
    /\btypeof\b/g,   // typeof operator
    /\binstanceof\b/g, // instanceof operator
    /\bin\b/g        // in operator
  ];
  
  // Extract operators
  operatorPatterns.forEach(pattern => {
    const matches = content.match(pattern);
    if (matches) {
      matches.forEach(match => operators.add(match));
    }
  });
  
  // Extract variable names and literals (simplified)
  const operandPatterns = [
    /\b[a-zA-Z_]\w*\b/g,  // Identifiers
    /"[^"]*"/g,           // String literals
    /'[^']*'/g,           // String literals
    /`[^`]*`/g,           // Template literals
    /\btrue\b|\bfalse\b/g, // Boolean literals
    /\bnull\b/g,          // Null literal
    /\bundefined\b/g,     // Undefined literal
    /\b\d+\b/g            // Number literals
  ];
  
  // Extract operands
  operandPatterns.forEach(pattern => {
    const matches = content.match(pattern);
    if (matches) {
      matches.forEach(match => operands.add(match));
    }
  });
  
  // Calculate Halstead metrics
  const n1 = operators.size; // Distinct operators
  const n2 = operands.size;  // Distinct operands
  const N1 = Array.from(content.matchAll(/[+\-*/%=&|^<>?:!~]|&&|\|\|/g)).length; // Total operators
  const N2 = Array.from(content.matchAll(/\b[a-zA-Z_]\w*\b|"[^"]*"|'[^']*'|`[^`]*`|\btrue\b|\bfalse\b|\bnull\b|\bundefined\b|\b\d+\b/g)).length; // Total operands
  
  // Calculate program vocabulary and length
  const vocabulary = n1 + n2;
  const length = N1 + N2;
  
  // Calculate volume
  return length * Math.log2(Math.max(vocabulary, 2));
}

/**
 * Count comments in code
 * @param {string} content - File content
 * @returns {number} - Comment count
 */
function countComments(content) {
  let count = 0;
  
  // Count single-line comments
  const singleLineComments = content.match(/\/\/.*/g);
  if (singleLineComments) {
    count += singleLineComments.length;
  }
  
  // Count multi-line comments
  const multiLineCommentMatches = content.match(/\/\*[\s\S]*?\*\//g);
  if (multiLineCommentMatches) {
    multiLineCommentMatches.forEach(comment => {
      count += comment.split('\n').length;
    });
  }
  
  // Count JSDoc comments
  const jsDocCommentMatches = content.match(/\/\*\*[\s\S]*?\*\//g);
  if (jsDocCommentMatches) {
    jsDocCommentMatches.forEach(comment => {
      count += comment.split('\n').length;
    });
  }
  
  return count;
}

/**
 * Calculate maximum nesting depth
 * @param {string} content - File content
 * @returns {number} - Maximum nesting depth
 */
function calculateNestingDepth(content) {
  let currentDepth = 0;
  let maxDepth = 0;
  const lines = content.split('\n');
  
  for (const line of lines) {
    // Count opening brackets/braces
    const openingCount = (line.match(/{|\(|\[/g) || []).length;
    
    // Count closing brackets/braces
    const closingCount = (line.match(/}|\)|\]/g) || []).length;
    
    // Update depth
    currentDepth += openingCount - closingCount;
    maxDepth = Math.max(maxDepth, currentDepth);
  }
  
  return maxDepth;
}

/**
 * Perform runtime analysis of the application
 * @param {string} baseUrl - Base URL of the application
 * @param {string[]} routes - Routes to analyze
 * @returns {Promise<object>} - Runtime analysis results
 */
async function performRuntimeAnalysis(baseUrl, routes) {
  console.log('🚀 Starting runtime analysis...');
  
  // Skip if puppeteer is not available
  if (!tools.puppeteer) {
    console.log('⚠️ Puppeteer not available. Runtime analysis disabled.');
    return null;
  }
  
  const runtimeResults = {
    performanceMetrics: {},
    a11yViolations: [],
    consoleMessages: [],
    resourceUsage: {},
    screenshots: {},
    errors: []
  };
  
  try {
    // Launch browser
    const browser = await tools.puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });
    
    let page = await browser.newPage();
    
    // Collect console messages
    page.on('console', message => {
      runtimeResults.consoleMessages.push({
        type: message.type(),
        text: message.text(),
        location: message.location()
      });
    });
    
    // Collect errors
    page.on('error', error => {
      runtimeResults.errors.push({
        message: error.message,
        stack: error.stack
      });
    });
    
    // Collect page errors
    page.on('pageerror', error => {
      runtimeResults.errors.push({
        message: error.message,
        type: 'pageerror'
      });
    });
    
    // Define the routes to analyze (default to home route if none provided)
    const routesToAnalyze = routes.length > 0 ? routes : ['/'];
    
    for (const route of routesToAnalyze) {
      const url = new URL(route, baseUrl).toString();
      console.log(`📊 Analyzing route: ${route}`);
      
      // Analyze each route with different screen sizes
      for (const screenSize of CONFIG.runtime.screenSizes) {
        console.log(`📱 Testing screen size: ${screenSize.name} (${screenSize.width}x${screenSize.height})`);
        
        // Set viewport size
        await page.setViewport({
          width: screenSize.width,
          height: screenSize.height
        });
        
        // Navigate to URL
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
        
        // Allow React/Vue/Angular to render
        await page.waitForTimeout(1000);
        
        // Take screenshot
        if (CONFIG.runtime.screenshots) {
          const screenshotPath = `${CONFIG.outputDir}/screenshots/${route.replace(/\//g, '_')}_${screenSize.name}.png`;
          // Ensure the directory exists
          const screenshotDir = path.dirname(screenshotPath);
          if (!fs.existsSync(screenshotDir)) {
            fs.mkdirSync(screenshotDir, { recursive: true });
          }
          
          await page.screenshot({ path: screenshotPath, fullPage: true });
          runtimeResults.screenshots[`${route}_${screenSize.name}`] = screenshotPath;
        }
        
        // Collect performance metrics
        const performanceMetrics = await page.evaluate(() => {
          const perfData = window.performance;
          const timing = perfData.timing;
          
          return {
            navigationStart: timing.navigationStart,
            redirectTime: timing.redirectEnd - timing.redirectStart,
            dnsTime: timing.domainLookupEnd - timing.domainLookupStart,
            connectTime: timing.connectEnd - timing.connectStart,
            sslTime: timing.connectEnd - timing.secureConnectionStart,
            ttfb: timing.responseStart - timing.requestStart,
            downloadTime: timing.responseEnd - timing.responseStart,
            domInteractive: timing.domInteractive - timing.navigationStart,
            domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
            domComplete: timing.domComplete - timing.navigationStart,
            loadTime: timing.loadEventEnd - timing.navigationStart,
            firstPaint: perfData.getEntriesByType('paint').find(entry => entry.name === 'first-paint')?.startTime,
            firstContentfulPaint: perfData.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint')?.startTime,
            largestContentfulPaint: perfData.getEntriesByName('largest-contentful-paint')?.startTime,
            resources: perfData.getEntriesByType('resource').length,
            javaScriptSize: perfData.getEntriesByType('resource')
              .filter(resource => resource.initiatorType === 'script')
              .reduce((total, script) => total + script.transferSize, 0),
            cssSize: perfData.getEntriesByType('resource')
              .filter(resource => resource.initiatorType === 'css')
              .reduce((total, css) => total + css.transferSize, 0),
            imageSize: perfData.getEntriesByType('resource')
              .filter(resource => resource.initiatorType === 'img')
              .reduce((total, img) => total + img.transferSize, 0)
          };
        });
        
        runtimeResults.performanceMetrics[`${route}_${screenSize.name}`] = performanceMetrics;
        
        // Get memory usage
        const jsHeapSize = await page.evaluate(() => 
          performance.memory ? performance.memory.usedJSHeapSize : null
        );
        
        if (jsHeapSize) {
          runtimeResults.resourceUsage[`${route}_${screenSize.name}`] = {
            jsHeapSize
          };
        }
        
        // Run accessibility tests with axe-core if available
        if (tools.axe && CONFIG.runtime.axe) {
          try {
            await tools.axe.inject(page);
            const axeResults = await page.evaluate(async () => {
              return await axe.run();
            });
            
            if (axeResults.violations.length > 0) {
              runtimeResults.a11yViolations.push({
                route,
                screenSize: screenSize.name,
                violations: axeResults.violations.map(violation => ({
                  id: violation.id,
                  impact: violation.impact,
                  description: violation.description,
                  help: violation.help,
                  helpUrl: violation.helpUrl,
                  nodes: violation.nodes.length
                }))
              });
              
              // Add to static results for reporting
              axeResults.violations.forEach(violation => {
                results.static.accessibilityIssues.push({
                  route,
                  screenSize: screenSize.name,
                  issue: violation.id,
                  impact: violation.impact,
                  description: violation.help,
                  url: violation.helpUrl
                });
              });
            }
          } catch (axeError) {
            console.log(`⚠️ Error running accessibility tests: ${axeError.message}`);
          }
        }
      }
      
      // Run Lighthouse audit if configured and available
      if (tools.lighthouse && CONFIG.runtime.lighthouse) {
        try {
          console.log(`🔆 Running Lighthouse audit for ${route}...`);
          
          // Close current page as Lighthouse needs to control its own
          await page.close();
          
          // Run Lighthouse
          const { lhr } = await tools.lighthouse(url, {
            port: (new URL(browser.wsEndpoint())).port,
            output: 'json',
            logLevel: 'error',
            onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo']
          });
          
          // Save Lighthouse results
          const lighthouseDir = `${CONFIG.outputDir}/lighthouse`;
          if (!fs.existsSync(lighthouseDir)) {
            fs.mkdirSync(lighthouseDir, { recursive: true });
          }
          
          const lighthousePath = `${lighthouseDir}/${route.replace(/\//g, '_')}.json`;
          fs.writeFileSync(lighthousePath, JSON.stringify(lhr, null, 2));
          
          // Extract scores and add to results
          runtimeResults.lighthouse = runtimeResults.lighthouse || {};
          runtimeResults.lighthouse[route] = {
            performance: lhr.categories.performance.score * 100,
            accessibility: lhr.categories.accessibility.score * 100,
            bestPractices: lhr.categories['best-practices'].score * 100,
            seo: lhr.categories.seo.score * 100,
            report: lighthousePath
          };
          
          // Create a new page for further testing
          page = await browser.newPage();
          
        } catch (lighthouseError) {
          console.log(`⚠️ Error running Lighthouse: ${lighthouseError.message}`);
        }
      }
    }
    
    // Close browser
    await browser.close();
    
    console.log('✅ Runtime analysis complete');
    return runtimeResults;
    
  } catch (error) {
    console.error(`❌ Runtime analysis failed: ${error.message}`);
    runtimeResults.errors.push({
      message: error.message,
      stack: error.stack,
      type: 'runtime-error'
    });
    return runtimeResults;
  }
}

/**
 * Generate HTML report from analysis results
 * @param {object} results - Analysis results
 * @returns {string} - Path to HTML report
 */
function generateReport(results) {
  console.log('📝 Generating report...');
  
  // Ensure output directory exists
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }
  
  // Define report paths
  const htmlReportPath = path.join(CONFIG.outputDir, 'audit-report.html');
  const jsonReportPath = path.join(CONFIG.outputDir, 'audit-data.json');
  
  // Save raw JSON data
  fs.writeFileSync(jsonReportPath, JSON.stringify(results, null, 2));
  
  // Generate HTML report
  let html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Frontend Audit Report</title>
  <style>
    :root {
      --primary: #4361ee;
      --secondary: #3f37c9;
      --success: #4cc9f0;
      --info: #4895ef;
      --warning: #f72585;
      --danger: #e63946;
      --light: #f8f9fa;
      --dark: #212529;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.5;
      color: var(--dark);
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem;
    }
    h1, h2, h3, h4 {
      color: var(--primary);
      margin-top: 2rem;
    }
    h1 {
      font-size: 2.5rem;
      text-align: center;
    }
    h2 {
      border-bottom: 2px solid var(--primary);
      padding-bottom: 0.5rem;
    }
    .summary {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 1rem;
      margin: 2rem 0;
    }
    .card {
      background: white;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      padding: 1.5rem;
      transition: transform 0.3s ease;
    }
    .card:hover {
      transform: translateY(-4px);
    }
    .metric {
      font-size: 2rem;
      font-weight: bold;
      margin: 0;
    }
    .label {
      color: #666;
      margin: 0;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 1rem 0;
    }
    th, td {
      text-align: left;
      padding: 0.75rem;
      border-bottom: 1px solid #ddd;
    }
    th {
      background-color: var(--light);
    }
    tr:hover {
      background-color: #f5f5f5;
    }
    .severity-critical {
      color: var(--danger);
      font-weight: bold;
    }
    .severity-high {
      color: var(--warning);
      font-weight: bold;
    }
    .severity-medium {
      color: var(--info);
    }
    .severity-low {
      color: var(--success);
    }
    .issues-container {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-top: 1rem;
    }
    .issue {
      border-left: 4px solid #ddd;
      padding: 0.75rem 1rem;
      background-color: #f9f9f9;
    }
    .issue.critical {
      border-left-color: var(--danger);
    }
    .issue.high {
      border-left-color: var(--warning);
    }
    .issue.medium {
      border-left-color: var(--info);
    }
    .issue.low {
      border-left-color: var(--success);
    }
    .tab-container {
      margin: 2rem 0;
    }
    .tabs {
      display: flex;
      border-bottom: 1px solid #ddd;
    }
    .tab {
      padding: 0.75rem 1rem;
      cursor: pointer;
      background: #f1f1f1;
      border: none;
      margin-right: 0.5rem;
    }
    .tab.active {
      background: white;
      border: 1px solid #ddd;
      border-bottom: none;
    }
    .tab-content {
      display: none;
      padding: 1rem;
      border: 1px solid #ddd;
      border-top: none;
    }
    .tab-content.active {
      display: block;
    }
    .chart-container {
      height: 300px;
      margin: 2rem 0;
    }
    code {
      font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      background-color: #f5f5f5;
      padding: 0.2rem 0.4rem;
      border-radius: 3px;
    }
    pre {
      background-color: #f5f5f5;
      padding: 1rem;
      border-radius: 5px;
      overflow-x: auto;
    }
    .framework-badge {
      display: inline-block;
      padding: 0.25rem 0.5rem;
      background-color: var(--primary);
      color: white;
      border-radius: 4px;
      font-weight: bold;
      margin-right: 0.5rem;
    }
    .recommendation {
      background-color: #f0f7ff;
      border-left: 4px solid var(--primary);
      padding: 1rem;
      margin: 1rem 0;
    }
    footer {
      text-align: center;
      margin-top: 3rem;
      padding: 1rem;
      border-top: 1px solid #ddd;
      color: #666;
    }
    @media (max-width: 768px) {
      .summary {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <h1>Frontend Code Audit Report</h1>
  <p class="timestamp">Generated on ${new Date().toLocaleString()}</p>
  
  ${results.summary.detectedFramework ? 
    `<p class="framework-detection">Detected framework: <span class="framework-badge">${results.summary.detectedFramework}</span></p>` : 
    ''}
  
  <div class="summary">
    <div class="card">
      <p class="metric">${results.summary.totalFiles}</p>
      <p class="label">Files Analyzed</p>
    </div>
    <div class="card">
      <p class="metric">${results.summary.totalLines.toLocaleString()}</p>
      <p class="label">Lines of Code</p>
    </div>
    <div class="card">
      <p class="metric">${results.summary.issues.critical + results.summary.issues.high + results.summary.issues.medium + results.summary.issues.low}</p>
      <p class="label">Total Issues</p>
    </div>
    <div class="card">
      <p class="metric">${results.summary.issues.critical}</p>
      <p class="label severity-critical">Critical Issues</p>
    </div>
    <div class="card">
      <p class="metric">${results.summary.issues.high}</p>
      <p class="label severity-high">High Issues</p>
    </div>
    <div class="card">
      <p class="metric">${results.summary.issues.medium}</p>
      <p class="label severity-medium">Medium Issues</p>
    </div>
  </div>

  <h2>Issues Summary</h2>
  
  <div class="tab-container">
    <div class="tabs">
      <button class="tab active" onclick="openTab(event, 'security-issues')">Security</button>
      <button class="tab" onclick="openTab(event, 'accessibility-issues')">Accessibility</button>
      <button class="tab" onclick="openTab(event, 'performance-issues')">Performance</button>
      <button class="tab" onclick="openTab(event, 'code-issues')">Code Quality</button>
    </div>
    
    <div id="security-issues" class="tab-content active">
      <div class="issues-container">
        ${generateIssuesHTML(results.static.securityIssues)}
      </div>
    </div>
    
    <div id="accessibility-issues" class="tab-content">
      <div class="issues-container">
        ${generateIssuesHTML(results.static.accessibilityIssues)}
      </div>
    </div>
    
    <div id="performance-issues" class="tab-content">
      <div class="issues-container">
        ${generateIssuesHTML(results.static.fileAnalysis
          .flatMap(file => file.issues.filter(issue => issue.type === 'complexity' || issue.type === 'performance'))
          .map(issue => ({
            file: file.path,
            issue: issue.message,
            severity: issue.severity,
            recommendation: issue.recommendation
          })))}
      </div>
    </div>
    
    <div id="code-issues" class="tab-content">
      <div class="issues-container">
        ${generateIssuesHTML(results.static.fileAnalysis
          .flatMap(file => file.issues.filter(issue => 
            issue.type !== 'security' && 
            issue.type !== 'accessibility' && 
            issue.type !== 'complexity' && 
            issue.type !== 'performance'))
          .map(issue => ({
            file: file.path,
            issue: issue.message,
            severity: issue.severity,
            recommendation: issue.recommendation
          })))}
      </div>
    </div>
  </div>
  
  <h2>File Type Breakdown</h2>
  <table>
    <thead>
      <tr>
        <th>File Type</th>
        <th>Count</th>
        <th>Percentage</th>
      </tr>
    </thead>
    <tbody>
      ${Object.entries(results.summary.fileTypes)
        .map(([type, count]) => {
          const percentage = ((count / results.summary.totalFiles) * 100).toFixed(1);
          return `<tr>
            <td>${type}</td>
            <td>${count}</td>
            <td>${percentage}%</td>
          </tr>`;
        }).join('')}
    </tbody>
  </table>
  
  <h2>Top Recommendations</h2>
  <div class="recommendations">
    ${generateRecommendations(results)}
  </div>
  
  ${results.runtime.performanceMetrics && Object.keys(results.runtime.performanceMetrics).length > 0 ? `
    <h2>Performance Metrics</h2>
    ${generatePerformanceSection(results.runtime)}
  ` : ''}
  
  <script>
    function openTab(evt, tabName) {
      var i, tabContent, tabLinks;
      
      tabContent = document.getElementsByClassName("tab-content");
      for (i = 0; i < tabContent.length; i++) {
        tabContent[i].className = tabContent[i].className.replace(" active", "");
      }
      
      tabLinks = document.getElementsByClassName("tab");
      for (i = 0; i < tabLinks.length; i++) {
        tabLinks[i].className = tabLinks[i].className.replace(" active", "");
      }
      
      document.getElementById(tabName).className += " active";
      evt.currentTarget.className += " active";
    }
  </script>
  
  <footer>
    <p>Generated by Universal Frontend Audit Tool</p>
  </footer>
</body>
</html>`;

  // Write HTML report to file
  fs.writeFileSync(htmlReportPath, html);
  
  console.log(`✅ Report saved to ${htmlReportPath}`);
  console.log(`✅ Raw data saved to ${jsonReportPath}`);
  
  return htmlReportPath;
}

/**
 * Generate HTML for issues section
 * @param {Array} issues - Array of issues
 * @returns {string} - HTML content
 */
function generateIssuesHTML(issues) {
  if (!issues || issues.length === 0) {
    return '<p>No issues detected.</p>';
  }
  
  return issues
    .sort((a, b) => {
      const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      return severityOrder[a.severity] - severityOrder[b.severity];
    })
    .map(issue => `
      <div class="issue ${issue.severity}">
        <h4>${issue.issue}</h4>
        <p><strong>File:</strong> ${issue.file}</p>
        <p><strong>Severity:</strong> <span class="severity-${issue.severity}">${issue.severity}</span></p>
        ${issue.recommendation ? `<p><strong>Recommendation:</strong> ${issue.recommendation}</p>` : ''}
      </div>
    `).join('');
}

/**
 * Generate recommendations section
 * @param {object} results - Analysis results
 * @returns {string} - HTML content
 */
function generateRecommendations(results) {
  // Collect all issues with recommendations
  const allIssues = [
    ...results.static.securityIssues,
    ...results.static.accessibilityIssues,
    ...results.static.fileAnalysis.flatMap(file => 
      file.issues.map(issue => ({
        ...issue,
        file: file.path
      }))
    )
  ];
  
  // Group by recommendation
  const recommendationGroups = {};
  
  allIssues.forEach(issue => {
    if (issue.recommendation) {
      if (!recommendationGroups[issue.recommendation]) {
        recommendationGroups[issue.recommendation] = {
          count: 0,
          severity: issue.severity,
          examples: []
        };
      }
      
      recommendationGroups[issue.recommendation].count++;
      
      // Keep track of the highest severity
      const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      if (severityOrder[issue.severity] < severityOrder[recommendationGroups[issue.recommendation].severity]) {
        recommendationGroups[issue.recommendation].severity = issue.severity;
      }
      
      // Add example if we don't have too many
      if (recommendationGroups[issue.recommendation].examples.length < 3) {
        recommendationGroups[issue.recommendation].examples.push({
          issue: issue.message || issue.issue,
          file: issue.file
        });
      }
    }
  });
  
  // Sort by count and severity
  const sortedRecommendations = Object.entries(recommendationGroups)
    .sort((a, b) => {
      // Sort by severity first
      const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      const severityDiff = severityOrder[a[1].severity] - severityOrder[b[1].severity];
      
      // If same severity, sort by count
      if (severityDiff === 0) {
        return b[1].count - a[1].count;
      }
      
      return severityDiff;
    })
    .slice(0, 10); // Top 10 recommendations
  
  if (sortedRecommendations.length === 0) {
    return '<p>No recommendations found.</p>';
  }
  
  return sortedRecommendations
    .map(([recommendation, { count, severity, examples }]) => `
      <div class="recommendation">
        <h3>${recommendation}</h3>
        <p><strong>Affected:</strong> ${count} ${count === 1 ? 'instance' : 'instances'}</p>
        <p><strong>Severity:</strong> <span class="severity-${severity}">${severity}</span></p>
        ${examples.length > 0 ? `
          <p><strong>Examples:</strong></p>
          <ul>
            ${examples.map(example => `<li>${example.issue} (in ${example.file})</li>`).join('')}
          </ul>
        ` : ''}
      </div>
    `).join('');
}

/**
 * Generate performance section HTML
 * @param {object} runtimeResults - Runtime analysis results
 * @returns {string} - HTML content
 */
function generatePerformanceSection(runtimeResults) {
  const { performanceMetrics } = runtimeResults;
  
  if (!performanceMetrics || Object.keys(performanceMetrics).length === 0) {
    return '<p>No performance metrics available.</p>';
  }
  
  const metrics = Object.entries(performanceMetrics)
    .map(([route, data]) => {
      if (!data) return '';
      
      return `
        <h3>${route}</h3>
        <table>
          <thead>
            <tr>
              <th>Metric</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Time to Interactive</td>
              <td>${Math.round(data.domInteractive)}ms</td>
            </tr>
            <tr>
              <td>First Paint</td>
              <td>${Math.round(data.firstPaint || 0)}ms</td>
            </tr>
            <tr>
              <td>First Contentful Paint</td>
              <td>${Math.round(data.firstContentfulPaint || 0)}ms</td>
            </tr>
            <tr>
              <td>DOM Content Loaded</td>
              <td>${Math.round(data.domContentLoaded)}ms</td>
            </tr>
            <tr>
              <td>Load Complete</td>
              <td>${Math.round(data.loadTime)}ms</td>
            </tr>
            <tr>
              <td>Resources Loaded</td>
              <td>${data.resources || 0}</td>
            </tr>
            <tr>
              <td>JavaScript Size</td>
              <td>${formatBytes(data.javaScriptSize || 0)}</td>
            </tr>
            <tr>
              <td>CSS Size</td>
              <td>${formatBytes(data.cssSize || 0)}</td>
            </tr>
            <tr>
              <td>Image Size</td>
              <td>${formatBytes(data.imageSize || 0)}</td>
            </tr>
          </tbody>
        </table>
      `;
    }).join('');
  
  return metrics;
}

/**
 * Format bytes to human-readable size
 * @param {number} bytes - Size in bytes
 * @returns {string} - Formatted size
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Main execution
async function runAudit() {
  try {
    console.log('🚀 Starting Universal Frontend Audit...');
    results.summary.startTime = performance.now();
    
    // Ensure output directory exists
    if (!fs.existsSync(CONFIG.outputDir)) {
      fs.mkdirSync(CONFIG.outputDir, { recursive: true });
    }
    
    // Find target files
    const targetFiles = findFiles(CONFIG.scanDirs);
    
    // Detect framework
    results.summary.detectedFramework = detectFramework(targetFiles);
    
    // Process files
    console.log(`Analyzing ${targetFiles.length} files...`);
    for (let i = 0; i < targetFiles.length; i++) {
      const file = targetFiles[i];
      await processFile(file);
      
      // Show progress
      if ((i + 1) % 10 === 0 || i + 1 === targetFiles.length) {
        console.log(`Progress: ${i + 1}/${targetFiles.length} files (${Math.round((i + 1) / targetFiles.length * 100)}%)`);
      }
    }
    
    // Calculate issue counts
    results.summary.issues = {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0
    };
    
    // Count issues by severity
    results.static.fileAnalysis.forEach(file => {
      file.issues.forEach(issue => {
        results.summary.issues[issue.severity] = (results.summary.issues[issue.severity] || 0) + 1;
      });
    });
    
    // Perform runtime analysis if enabled
    if (CONFIG.analysis.runtime) {
      results.runtime = await performRuntimeAnalysis(
        CONFIG.runtime.baseUrl,
        CONFIG.runtime.routes
      );
    }
    
    // End timing
    results.summary.endTime = performance.now();
    results.summary.duration = results.summary.endTime - results.summary.startTime;
    
    console.log(`✅ Analysis complete in ${(results.summary.duration / 1000).toFixed(2)} seconds`);
    
    // Generate reports
    const reportPath = generateReport(results);
    
    console.log('\n📊 Results Summary:');
    console.log(`- Files analyzed: ${results.summary.totalFiles}`);
    console.log(`- Total issues: ${results.summary.issues.critical + results.summary.issues.high + results.summary.issues.medium + results.summary.issues.low}`);
    console.log(`  - Critical: ${results.summary.issues.critical}`);
    console.log(`  - High: ${results.summary.issues.high}`);
    console.log(`  - Medium: ${results.summary.issues.medium}`);
    console.log(`  - Low: ${results.summary.issues.low}`);
    console.log(`- Runtime analysis: ${CONFIG.analysis.runtime ? 'Completed' : 'Skipped'}`);
    console.log(`- Report: ${reportPath}`);
    
    // Return success
    return 0;
  } catch (error) {
    console.error('❌ Audit failed:', error);
    console.error(error.stack);
    return 1;
  }
}

// Check if running as script or imported as module
if (require.main === module) {
  // Parse command line arguments
  const argv = require('minimist')(process.argv.slice(2));
  
  // Handle configuration from command line
  if (argv.dir) {
    CONFIG.scanDirs = Array.isArray(argv.dir) ? argv.dir : [argv.dir];
  }
  
  if (argv.output) {
    CONFIG.outputDir = argv.output;
  }
  
  if (argv.url) {
    CONFIG.runtime.baseUrl = argv.url;
  }
  
  if (argv.routes) {
    CONFIG.runtime.routes = Array.isArray(argv.routes) ? argv.routes : [argv.routes];
  }
  
  if (argv.help) {
    console.log(`
Universal Frontend Audit Tool
-----------------------------
A comprehensive static and runtime analysis tool for frontend codebases.

Usage:
  node universal-frontend-audit.js [options]

Options:
  --dir        Directory to scan (can be used multiple times)
  --output     Output directory for reports
  --url        Base URL for runtime analysis
  --routes     Routes to analyze (can be used multiple times)
  --no-runtime Skip runtime analysis
  --help       Show this help message
    `);
    process.exit(0);
  }
  
  // Disable runtime analysis if requested
  if (argv['no-runtime']) {
    CONFIG.analysis.runtime = false;
  }
  
  // Run audit
  runAudit().then(exitCode => {
    process.exit(exitCode);
  });
} else {
  // Export for use as a module
  module.exports = {
    runAudit,
    CONFIG,
  };
}