// src/declarations.d.ts
declare module '*.jsx' {
  import React from 'react';
  const component: React.ComponentType<any>;
  export default component;
}

// If you need to handle JS files as well
declare module '*.js' {
  const content: any;
  export default content;
}
