/\*\*

- Common Component Export Documentation
- Version: 1.0.0
- Date: 2025-06-02
-
- This document outlines the standardized export pattern for common components
- in the EduPlatform frontend application.
-
- # Export Pattern
-
- All components in the /components/common directory should follow this pattern:
-
- 1.  Export the component as a named export:
- ```jsx

  ```

- export const Button = ({ ...props }) => { ... }
- ```

  ```

-
- 2.  Also include a default export for backward compatibility:
- ```jsx

  ```

- export default Button;
- ```

  ```

-
- # Import Pattern
-
- Components should be imported using named imports:
- ```jsx

  ```

- import { Button, Card, Badge } from '../components/common';
- ```

  ```

-
- Or directly from their component files:
- ```jsx

  ```

- import { Button } from '../components/common/Button';
- ```

  ```

-
- # Common Components
-
- The following components follow this export pattern:
- - Button
- - Card
- - Badge
- - Alert
- - FormInput
- - Tabs
- - Modal
- - Seo
- - Skeleton
-
- # Migration
-
- When updating older components, ensure both export methods are maintained
- to avoid breaking existing code. \*/
