import React, { useState } from 'react';

/**
 * Tabs component for creating tabbed interfaces
 * @param {Object} props - Component props
 * @param {Array} props.tabs - Array of tab objects with label and content properties
 * @param {number} props.defaultActiveTab - Index of the default active tab
 * @param {string} props.className - Additional CSS classes for the tabs container
 * @param {function} props.onChange - Callback when active tab changes
 */
const Tabs = ({
  tabs = [],
  defaultActiveTab = 0,
  className = '',
  onChange = () => {},
}) => {
  const [activeTabIndex, setActiveTabIndex] = useState(defaultActiveTab);

  // Ensure the activeTabIndex is valid
  const safeActiveTabIndex = Math.min(
    Math.max(0, activeTabIndex),
    tabs.length - 1
  );

  const handleTabClick = index => {
    setActiveTabIndex(index);
    onChange(index);
  };

  if (!tabs || tabs.length === 0) {
    return <div className="text-gray-500">No tabs provided</div>;
  }

  return (
    <div className={`w-full ${className}`}>
      {/* Tab headers */}
      <div className="flex border-b border-gray-200">
        {tabs.map((tab, index) => (
          <button
            key={index}
            className={`px-4 py-2 text-sm font-medium focus:outline-none ${
              index === safeActiveTabIndex
                ? 'text-blue-600 border-b-2 border-blue-600 -mb-px'
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => handleTabClick(index)}
            role="tab"
            aria-selected={index === safeActiveTabIndex}
            aria-controls={`tab-panel-${index}`}
            id={`tab-${index}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="p-4">
        {tabs.map((tab, index) => (
          <div
            key={index}
            role="tabpanel"
            aria-labelledby={`tab-${index}`}
            id={`tab-panel-${index}`}
            className={index === safeActiveTabIndex ? 'block' : 'hidden'}
          >
            {tab.content}
          </div>
        ))}
      </div>
    </div>
  );
};

// Named export
export { Tabs };

// Default export
export default Tabs;
