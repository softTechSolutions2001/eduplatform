/**
 * Common Components Index
 *
 * This file serves as a central export point for all common/reusable components.
 * This pattern provides several benefits:
 *
 * 1. Simplified Imports: Instead of importing each component individually from its own file,
 *    you can import multiple components from this single entry point:
 *    import { Button, Card, Badge } from '../components/common';
 *
 * 2. Better Organization: It makes the codebase more organized by providing a clear
 *    catalog of available reusable components.
 *
 * 3. Easier Maintenance: When components need to be renamed or restructured,
 *    you only need to update the exports here rather than throughout the codebase.
 *
 * 4. Discoverability: New team members can quickly see what components are available
 *    by looking at this file.
 */

// Layout Components
import Footer from './Footer';
import Header from './Header';
import MainLayout from './MainLayout';

// Export individual components
export {
  // UI Elements

  Footer,
  Header,
  MainLayout,
};

/**
 * Usage examples:
 *
 * 1. Import multiple components:
 *    import { Button, Card, Avatar } from '../components/common';
 *
 * 2. Import a specific component:
 *    import { Button } from '../components/common';
 *
 * 3. Import with alias:
 *    import { Button as CustomButton } from '../components/common';
 */
