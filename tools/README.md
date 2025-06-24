# Universal Frontend Audit Tool

A comprehensive static and runtime analysis tool for frontend codebases that can:

- Analyze any JavaScript/TypeScript frontend project
- Automatically detect React, Vue, Angular, and Svelte frameworks
- Perform both static code analysis and runtime performance evaluation
- Analyze code structure, component usage, and patterns
- Identify security vulnerabilities and accessibility issues
- Generate detailed HTML reports with recommendations

## Features

- **Framework-agnostic**: Works with any frontend framework (React, Vue, Angular, Svelte, etc.)
- **Static analysis**: Examines code without running it
  - Code structure and metrics
  - Component identification and usage
  - API calls and data flow
  - Security vulnerability detection
  - Accessibility compliance
  - Best practices enforcement
- **Runtime analysis**: Evaluates performance in the browser
  - Performance metrics (load times, paint events)
  - Lighthouse audits
  - Accessibility testing with Axe
  - Responsive testing across multiple screen sizes
  - Console error monitoring
- **Comprehensive reports**: Beautiful HTML reports with actionable insights

## Installation

```bash
# Install globally
npm install -g universal-frontend-audit

# Or use without installing
npx universal-frontend-audit
```

For full functionality, you may want to install the optional dependencies:

```bash
npm install -g puppeteer lighthouse @axe-core/puppeteer
```

## Usage

Basic usage:

```bash
# Analyze the current directory
frontend-audit

# Analyze a specific directory
frontend-audit --dir ./src

# Analyze multiple directories
frontend-audit --dir ./src --dir ./components
```

With runtime analysis:

```bash
# Analyze with runtime tests (requires a running dev server)
frontend-audit --url http://localhost:3000

# Analyze specific routes
frontend-audit --url http://localhost:3000 --routes / --routes /about --routes /dashboard
```

Output options:

```bash
# Specify output directory
frontend-audit --output ./audit-results
```

Additional options:

```bash
# Show all available options
frontend-audit --help
```

## Configuration

You can customize the tool through command-line arguments or by creating a `.frontend-audit.js` file in your project root with the following structure:

```javascript
module.exports = {
  scanDirs: ['./src'],
  outputDir: './audit-results',
  analysis: {
    static: true,
    runtime: true,
    // ...other options
  },
  runtime: {
    baseUrl: 'http://localhost:3000',
    routes: ['/'],
    // ...other options
  }
};
```

## Report

The tool generates a comprehensive HTML report with:

- Summary of findings
- Issue list categorized by severity and type
- File type breakdown
- Component and pattern usage statistics
- Security and accessibility issues
- Performance metrics
- Recommendations for improvement

## Requirements

- Node.js 14 or higher
- For runtime analysis:
  - A running development server
  - Puppeteer (installed automatically as a peer dependency)

## Optional Dependencies

The tool will work with basic functionality out of the box, but for enhanced capabilities:

- **Static Analysis**:
  - `@babel/parser`: For advanced JavaScript parsing
  - `@typescript/parser`: For TypeScript support
  - `vue-template-compiler`: For Vue component analysis
  - `svelte`: For Svelte component analysis
  - `node-html-parser`: For HTML analysis
  - `css-tree`: For CSS analysis

- **Runtime Analysis**:
  - `puppeteer`: For browser automation
  - `lighthouse`: For performance audits
  - `@axe-core/puppeteer`: For accessibility testing

## License

MIT 