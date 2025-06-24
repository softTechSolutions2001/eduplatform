/**
 * Direction Context
 * Provides an easy way to manage and access the current text direction (LTR or RTL)
 * throughout the application.
 */

import { createContext, useEffect, useState } from 'react';

export const DirectionContext = createContext({
  direction: 'ltr',
  setDirection: () => {},
  toggleDirection: () => {},
});

export const DirectionProvider = ({ children }) => {
  const [direction, setDirection] = useState('ltr');

  // Load direction from localStorage on initial load
  useEffect(() => {
    const savedDirection = localStorage.getItem('app-direction') || 'ltr';
    setDirection(savedDirection);
    document.documentElement.dir = savedDirection;
  }, []);

  // Update HTML dir attribute whenever direction changes
  useEffect(() => {
    document.documentElement.dir = direction;
    localStorage.setItem('app-direction', direction);
  }, [direction]);

  const toggleDirection = () => {
    setDirection(prev => (prev === 'ltr' ? 'rtl' : 'ltr'));
  };

  return (
    <DirectionContext.Provider
      value={{ direction, setDirection, toggleDirection }}
    >
      {children}
    </DirectionContext.Provider>
  );
};

export default DirectionProvider;
