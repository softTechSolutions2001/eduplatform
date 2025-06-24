/**
 * File: frontend-analyzer.js
 * Purpose: Analyze a React frontend application and generate comprehensive documentation
 * 
 * How to use:
 * 1. Save this script to the root of your React project
 * 2. Run: node frontend-analyzer.js
 * 3. Documentation will be generated in the 'docs' folder
 * 
 * Configuration variables:
 * - SRC_DIR: Source directory of your React app (default: 'src')
 * - OUTPUT_FILE: Output markdown file path (default: 'docs/frontend-documentation.md')
 * - COMPONENT_PATTERNS: File patterns for React components
 * - IGNORED_DIRECTORIES: Directories to ignore during scan
 * - LAYOUT_COMPONENTS: Names of components that represent layouts (for consistency checking)
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generate = require('@babel/generator').default;
const reactDocs = require('react-docgen');
const mkdirp = require('mkdirp');
const chalk = require('chalk');

// Configuration
const CONFIG = {
  SRC_DIR: 'src',
  OUTPUT_FILE: 'docs/frontend-documentation.md',
  COMPONENT_PATTERNS: ['**/*.jsx', '**/*.tsx', '**/*.js', '**/*.ts'],
  IGNORED_DIRECTORIES: ['node_modules', 'build', 'dist', 'coverage'],
  LAYOUT_COMPONENTS: ['Layout', 'MainLayout', 'DefaultLayout', 'AuthLayout', 'Header', 'Footer'],
  API_PATTERNS: ['api', 'fetch', 'axios', '.get(', '.post(', '.put(', '.delete(', '.patch('],
  STATE_PATTERNS: ['useState', 'useReducer', 'useContext', 'connect('],
};

// Data structures to store analysis
const analysis = {
  components: {},
  pages: {},
  routes: [],
  layouts: {},
  apiEndpoints: {},
  consistencyMetrics: {
    layoutUsage: {},
    headerUsage: 0,
    footerUsage: 0,
    totalPages: 0,
  },
};

// Utility functions
function isPage(filePath) {
  return filePath.includes('/pages/') || filePath.includes('/views/');
}

function isComponent(filePath) {
  return filePath.includes('/components/');
}

function isLayout(componentName) {
  return CONFIG.LAYOUT_COMPONENTS.some(layout => 
    componentName.toLowerCase().includes(layout.toLowerCase())
  );
}

function extractComponentName(filePath) {
  const basename = path.basename(filePath, path.extname(filePath));
  // Convert to PascalCase if it's not already
  return basename.charAt(0).toUpperCase() + basename.slice(1);
}

function getRelativePath(filePath) {
  return path.relative(process.cwd(), filePath);
}

function findApiCalls(code) {
  const apiCalls = [];
  try {
    const ast = parser.parse(code, {
      sourceType: 'module',
      plugins: ['jsx', 'typescript'],
    });

    traverse(ast, {
      CallExpression(path) {
        // Check for API calls
        const callee = path.node.callee;
        const calleeCode = generate(callee).code;
        
        if (CONFIG.API_PATTERNS.some(pattern => calleeCode.includes(pattern))) {
          let endpoint = '';
          
          // Try to extract endpoint string from arguments
          if (path.node.arguments.length > 0 && 
              path.node.arguments[0].type === 'StringLiteral') {
            endpoint = path.node.arguments[0].value;
          }
          
          apiCalls.push({
            type: calleeCode,
            endpoint: endpoint,
          });
        }
      }
    });
  } catch (e) {
    console.error('Error parsing code for API calls:', e);
  }
  
  return apiCalls;
}

function findStateUsage(code) {
  const stateUsage = [];
  try {
    const ast = parser.parse(code, {
      sourceType: 'module',
      plugins: ['jsx', 'typescript'],
    });

    traverse(ast, {
      CallExpression(path) {
        if (
          path.node.callee.type === 'Identifier' && 
          CONFIG.STATE_PATTERNS.some(pattern => path.node.callee.name.includes(pattern))
        ) {
          stateUsage.push({
            type: path.node.callee.name,
            variable: generate(path.node.arguments[0]).code,
          });
        }
      }
    });
  } catch (e) {
    console.error('Error parsing code for state usage:', e);
  }
  
  return stateUsage;
}

function findImports(code) {
  const imports = [];
  try {
    const ast = parser.parse(code, {
      sourceType: 'module',
      plugins: ['jsx', 'typescript'],
    });

    traverse(ast, {
      ImportDeclaration(path) {
        imports.push({
          source: path.node.source.value,
          specifiers: path.node.specifiers.map(specifier => {
            if (specifier.type === 'ImportDefaultSpecifier') {
              return {
                name: specifier.local.name,
                type: 'default',
              };
            }
            return {
              name: specifier.local.name,
              imported: specifier.imported ? specifier.imported.name : null,
              type: 'named',
            };
          }),
        });
      }
    });
  } catch (e) {
    console.error('Error parsing code for imports:', e);
  }
  
  return imports;
}

function findRoutes(code) {
  const routes = [];
  try {
    const ast = parser.parse(code, {
      sourceType: 'module',
      plugins: ['jsx', 'typescript'],
    });

    // Look for Route components
    traverse(ast, {
      JSXElement(path) {
        const openingElement = path.node.openingElement;
        if (openingElement.name.name === 'Route') {
          const props = {};
          openingElement.attributes.forEach(attr => {
            if (attr.type === 'JSXAttribute') {
              const name = attr.name.name;
              if (attr.value.type === 'StringLiteral') {
                props[name] = attr.value.value;
              } else if (attr.value.type === 'JSXExpressionContainer') {
                props[name] = generate(attr.value.expression).code;
              }
            }
          });
          
          if (props.path || props.element) {
            routes.push(props);
          }
        }
      }
    });
  } catch (e) {
    console.error('Error parsing code for routes:', e);
  }
  
  return routes;
}

function analyzeComponent(filePath) {
  try {
    const code = fs.readFileSync(filePath, 'utf8');
    const componentName = extractComponentName(filePath);
    
    let info = {
      name: componentName,
      path: getRelativePath(filePath),
      isPage: isPage(filePath),
      isLayout: isLayout(componentName),
      apiCalls: findApiCalls(code),
      stateUsage: findStateUsage(code),
      imports: findImports(code),
      routes: findRoutes(code),
    };
    
    // Try to extract documentation using react-docgen
    try {
      const docInfo = reactDocs.parse(code);
      info = {
        ...info,
        description: docInfo.description,
        props: docInfo.props,
        methods: docInfo.methods,
      };
    } catch (e) {
      // react-docgen may fail for some components, which is OK
    }
    
    if (info.isLayout) {
      analysis.layouts[componentName] = info;
    }
    
    if (info.isPage) {
      analysis.pages[componentName] = info;
      analysis.consistencyMetrics.totalPages++;
      
      // Check for layout components
      const hasLayout = info.imports.some(imp => 
        imp.specifiers.some(spec => isLayout(spec.name))
      );
      
      if (hasLayout) {
        const layoutName = info.imports
          .flatMap(imp => imp.specifiers)
          .find(spec => isLayout(spec.name))?.name;
        
        analysis.consistencyMetrics.layoutUsage[layoutName] = 
          (analysis.consistencyMetrics.layoutUsage[layoutName] || 0) + 1;
      }
      
      // Check for header/footer usage
      const code = fs.readFileSync(filePath, 'utf8');
      if (code.includes('Header') || code.includes('header')) {
        analysis.consistencyMetrics.headerUsage++;
      }
      
      if (code.includes('Footer') || code.includes('footer')) {
        analysis.consistencyMetrics.footerUsage++;
      }
    } else {
      analysis.components[componentName] = info;
    }
    
    // Extract API endpoints
    info.apiCalls.forEach(call => {
      if (call.endpoint && !call.endpoint.includes('{')) {
        analysis.apiEndpoints[call.endpoint] = analysis.apiEndpoints[call.endpoint] || [];
        analysis.apiEndpoints[call.endpoint].push(componentName);
      }
    });
    
    // Extract routes
    if (info.routes.length > 0) {
      analysis.routes.push(...info.routes.map(route => ({
        ...route,
        definedIn: componentName,
      })));
    }
    
    return info;
  } catch (e) {
    console.error(`Error analyzing component ${filePath}:`, e);
    return null;
  }
}

function formatApiCalls(apiCalls) {
  if (!apiCalls || apiCalls.length === 0) return 'None';
  
  return apiCalls.map(call => 
    call.endpoint ? `${call.type} -> ${call.endpoint}` : call.type
  ).join('\n- ');
}

function formatStateUsage(stateUsage) {
  if (!stateUsage || stateUsage.length === 0) return 'None';
  
  return stateUsage.map(state => 
    `${state.type}${state.variable ? `: ${state.variable}` : ''}`
  ).join('\n- ');
}

function generateMarkdown() {
  const timestamp = new Date().toISOString();
  
  let markdown = `# Frontend Application Documentation
Generated on: ${timestamp}

## Table of Contents
1. [Application Overview](#application-overview)
2. [Layout Components](#layout-components)
3. [Pages](#pages)
4. [Components](#components)
5. [Routes](#routes)
6. [API Endpoints](#api-endpoints)
7. [Consistency Analysis](#consistency-analysis)

## Application Overview

- **Total Pages:** ${analysis.consistencyMetrics.totalPages}
- **Total Components:** ${Object.keys(analysis.components).length}
- **Layout Components:** ${Object.keys(analysis.layouts).length}
- **Routes Defined:** ${analysis.routes.length}
- **API Endpoints Used:** ${Object.keys(analysis.apiEndpoints).length}

## Layout Components

`;

  // Layout Components Section
  if (Object.keys(analysis.layouts).length === 0) {
    markdown += 'No layout components found.\n\n';
  } else {
    for (const [name, layout] of Object.entries(analysis.layouts)) {
      markdown += `### ${name}\n\n`;
      markdown += `- **Path:** ${layout.path}\n`;
      markdown += `- **Description:** ${layout.description || 'No description available'}\n`;
      markdown += `- **Imported By:** ${
        [...Object.entries(analysis.pages), ...Object.entries(analysis.components)]
          .filter(([_, comp]) => comp.imports.some(imp => 
            imp.specifiers.some(spec => spec.name === name)
          ))
          .map(([compName, _]) => compName)
          .join(', ') || 'Not imported by any component'
      }\n\n`;
    }
  }

  // Pages Section
  markdown += '## Pages\n\n';
  for (const [name, page] of Object.entries(analysis.pages)) {
    markdown += `### ${name}\n\n`;
    markdown += `- **Path:** ${page.path}\n`;
    markdown += `- **Description:** ${page.description || 'No description available'}\n`;
    
    // Check for layout usage
    const usedLayouts = page.imports
      .flatMap(imp => imp.specifiers)
      .filter(spec => isLayout(spec.name))
      .map(spec => spec.name);
    
    markdown += `- **Uses Layout:** ${usedLayouts.length > 0 ? usedLayouts.join(', ') : 'No'}\n`;
    markdown += `- **Has Header:** ${page.path.includes('Header') || page.imports.some(imp => 
      imp.specifiers.some(spec => spec.name.includes('Header'))
    ) ? 'Yes' : 'No'}\n`;
    markdown += `- **Has Footer:** ${page.path.includes('Footer') || page.imports.some(imp => 
      imp.specifiers.some(spec => spec.name.includes('Footer'))
    ) ? 'Yes' : 'No'}\n`;
    
    // API calls
    markdown += `- **API Endpoints:** \n- ${formatApiCalls(page.apiCalls)}\n`;
    
    // State management
    markdown += `- **State Management:** \n- ${formatStateUsage(page.stateUsage)}\n`;
    
    // Routes defined
    if (page.routes && page.routes.length > 0) {
      markdown += `- **Defines Routes:** \n`;
      page.routes.forEach(route => {
        markdown += `  - ${route.path || 'unknown'} -> ${route.element || route.component || 'unknown component'}\n`;
      });
    }
    
    markdown += `\n`;
  }

  // Components Section (abbreviated to avoid too much detail)
  markdown += '## Components\n\n';
  markdown += `This application contains ${Object.keys(analysis.components).length} components. Key components:\n\n`;
  
  const keyComponents = Object.entries(analysis.components)
    .sort((a, b) => {
      const aImports = Object.values(analysis.pages).filter(page => 
        page.imports.some(imp => 
          imp.specifiers.some(spec => spec.name === a[0])
        )
      ).length;
      
      const bImports = Object.values(analysis.pages).filter(page => 
        page.imports.some(imp => 
          imp.specifiers.some(spec => spec.name === b[0])
        )
      ).length;
      
      return bImports - aImports; // Sort by most used first
    })
    .slice(0, 10); // Top 10 most used components
  
  for (const [name, component] of keyComponents) {
    markdown += `### ${name}\n\n`;
    markdown += `- **Path:** ${component.path}\n`;
    markdown += `- **Description:** ${component.description || 'No description available'}\n`;
    
    const usedByPages = Object.entries(analysis.pages)
      .filter(([_, page]) => page.imports.some(imp => 
        imp.specifiers.some(spec => spec.name === name)
      ))
      .map(([pageName, _]) => pageName);
    
    markdown += `- **Used By Pages:** ${usedByPages.join(', ') || 'Not used by any page'}\n\n`;
  }

  // Routes Section
  markdown += '## Routes\n\n';
  if (analysis.routes.length === 0) {
    markdown += 'No routes found in the codebase.\n\n';
  } else {
    markdown += '| Path | Component | Defined In |\n';
    markdown += '|------|-----------|------------|\n';
    analysis.routes.forEach(route => {
      markdown += `| ${route.path || 'unknown'} | ${route.element || route.component || 'unknown'} | ${route.definedIn} |\n`;
    });
    markdown += '\n';
  }

  // API Endpoints Section
  markdown += '## API Endpoints\n\n';
  if (Object.keys(analysis.apiEndpoints).length === 0) {
    markdown += 'No API endpoints detected.\n\n';
  } else {
    markdown += '| Endpoint | Used By |\n';
    markdown += '|----------|--------|\n';
    for (const [endpoint, components] of Object.entries(analysis.apiEndpoints)) {
      markdown += `| ${endpoint} | ${components.join(', ')} |\n`;
    }
    markdown += '\n';
  }

  // Consistency Analysis
  markdown += '## Consistency Analysis\n\n';
  markdown += `- **Pages Using Layouts:** ${
    Object.values(analysis.consistencyMetrics.layoutUsage).reduce((sum, count) => sum + count, 0)
  }/${analysis.consistencyMetrics.totalPages} (${
    Math.round(Object.values(analysis.consistencyMetrics.layoutUsage).reduce((sum, count) => sum + count, 0) / 
      (analysis.consistencyMetrics.totalPages || 1) * 100)
  }%)\n`;
  markdown += `- **Pages With Headers:** ${analysis.consistencyMetrics.headerUsage}/${analysis.consistencyMetrics.totalPages} (${
    Math.round(analysis.consistencyMetrics.headerUsage / 
      (analysis.consistencyMetrics.totalPages || 1) * 100)
  }%)\n`;
  markdown += `- **Pages With Footers:** ${analysis.consistencyMetrics.footerUsage}/${analysis.consistencyMetrics.totalPages} (${
    Math.round(analysis.consistencyMetrics.footerUsage / 
      (analysis.consistencyMetrics.totalPages || 1) * 100)
  }%)\n\n`;
  
  markdown += '### Layout Usage Breakdown\n\n';
  markdown += '| Layout Component | Used By Pages | Percentage |\n';
  markdown += '|------------------|---------------|------------|\n';
  for (const [layout, count] of Object.entries(analysis.consistencyMetrics.layoutUsage)) {
    markdown += `| ${layout} | ${count} | ${
      Math.round(count / (analysis.consistencyMetrics.totalPages || 1) * 100)
    }% |\n`;
  }
  markdown += '\n';

  // Recommendations based on analysis
  markdown += '## Recommendations\n\n';
  
  if (
    Object.values(analysis.consistencyMetrics.layoutUsage).reduce((sum, count) => sum + count, 0) < 
    analysis.consistencyMetrics.totalPages * 0.8
  ) {
    markdown += '- **Improve Layout Usage:** Consider implementing a consistent layout system. ' +
      'Only ' + Math.round(Object.values(analysis.consistencyMetrics.layoutUsage).reduce((sum, count) => sum + count, 0) / 
      (analysis.consistencyMetrics.totalPages || 1) * 100) + '% of pages are using layout components.\n';
  }
  
  if (analysis.consistencyMetrics.headerUsage < analysis.consistencyMetrics.totalPages * 0.8) {
    markdown += '- **Add Headers Consistently:** ' + 
      (analysis.consistencyMetrics.totalPages - analysis.consistencyMetrics.headerUsage) + 
      ' pages are missing header components.\n';
  }
  
  if (analysis.consistencyMetrics.footerUsage < analysis.consistencyMetrics.totalPages * 0.8) {
    markdown += '- **Add Footers Consistently:** ' + 
      (analysis.consistencyMetrics.totalPages - analysis.consistencyMetrics.footerUsage) + 
      ' pages are missing footer components.\n';
  }
  
  return markdown;
}

// Main execution function
async function analyzeApplication() {
  try {
    console.log(chalk.blue('🔍 Starting frontend application analysis...'));
    
    // Create output directory
    const outputDir = path.dirname(CONFIG.OUTPUT_FILE);
    await mkdirp(outputDir);
    
    // Find all component files
    let files = [];
    for (const pattern of CONFIG.COMPONENT_PATTERNS) {
      const matches = glob.sync(path.join(CONFIG.SRC_DIR, pattern), {
        ignore: CONFIG.IGNORED_DIRECTORIES.map(dir => `**/${dir}/**`),
      });
      files = [...files, ...matches];
    }
    
    console.log(chalk.green(`Found ${files.length} files to analyze.`));
    
    // Analyze each component
    let analyzed = 0;
    for (const file of files) {
      const result = analyzeComponent(file);
      if (result) analyzed++;
      
      // Progress indicator
      if (analyzed % 10 === 0) {
        console.log(chalk.yellow(`Analyzed ${analyzed}/${files.length} files...`));
      }
    }
    
    // Generate markdown
    const markdown = generateMarkdown();
    fs.writeFileSync(CONFIG.OUTPUT_FILE, markdown);
    
    console.log(chalk.green(`✅ Analysis complete! Documentation generated at ${CONFIG.OUTPUT_FILE}`));
    console.log(chalk.blue(`📊 Summary:`));
    console.log(`   - Pages: ${analysis.consistencyMetrics.totalPages}`);
    console.log(`   - Components: ${Object.keys(analysis.components).length}`);
    console.log(`   - Layout components: ${Object.keys(analysis.layouts).length}`);
    console.log(`   - API endpoints: ${Object.keys(analysis.apiEndpoints).length}`);
    
    // Layout consistency
    const layoutUsage = Object.values(analysis.consistencyMetrics.layoutUsage)
      .reduce((sum, count) => sum + count, 0);
    const layoutPercentage = Math.round(layoutUsage / (analysis.consistencyMetrics.totalPages || 1) * 100);
    
    console.log(`   - Layout consistency: ${layoutPercentage}%`);
    console.log(`   - Header usage: ${Math.round(analysis.consistencyMetrics.headerUsage / 
      (analysis.consistencyMetrics.totalPages || 1) * 100)}%`);
    console.log(`   - Footer usage: ${Math.round(analysis.consistencyMetrics.footerUsage / 
      (analysis.consistencyMetrics.totalPages || 1) * 100)}%`);
    
  } catch (e) {
    console.error(chalk.red('Error during application analysis:'), e);
  }
}

analyzeApplication();