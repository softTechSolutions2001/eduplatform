import React, { useState } from 'react';
import PropTypes from 'prop-types';

const AccordionItem = ({
  title,
  children,
  isOpen,
  toggleItem,
  index,
  borderless = false,
  className = '',
}) => {
  const borderClasses = borderless ? '' : 'border border-gray-200';

  return (
    <div
      className={`rounded-lg overflow-hidden mb-3 ${borderClasses} ${className}`}
    >
      <button
        className="w-full flex items-center justify-between p-4 text-left bg-white hover:bg-gray-50 transition-colors"
        onClick={() => toggleItem(index)}
      >
        <h3 className="font-medium text-gray-900">{title}</h3>
        <i
          className={`fas ${isOpen ? 'fa-chevron-up' : 'fa-chevron-down'} text-gray-500 transition-transform`}
        ></i>
      </button>

      <div
        className={`bg-gray-50 transition-all overflow-hidden ${isOpen ? 'max-h-96 p-4' : 'max-h-0'}`}
      >
        {children}
      </div>
    </div>
  );
};

const Accordion = ({
  items = [], // Provide default empty array
  defaultOpenIndex = null,
  allowMultiple = false,
  borderless = false,
  className = '',
}) => {
  const [openIndexes, setOpenIndexes] = useState(
    defaultOpenIndex !== null ? [defaultOpenIndex] : []
  );

  const toggleItem = index => {
    setOpenIndexes(prev => {
      if (prev.includes(index)) {
        return prev.filter(i => i !== index);
      } else {
        return allowMultiple ? [...prev, index] : [index];
      }
    });
  };

  // Check if items is valid before mapping
  if (!items || !Array.isArray(items) || items.length === 0) {
    return <div className="text-gray-500">No accordion items provided</div>;
  }

  return (
    <div className={className}>
      {items.map((item, index) => (
        <AccordionItem
          key={index}
          title={item.title}
          isOpen={openIndexes.includes(index)}
          toggleItem={toggleItem}
          index={index}
          borderless={borderless}
          className={item.className || ''}
        >
          {item.content}
        </AccordionItem>
      ))}
    </div>
  );
};

Accordion.propTypes = {
  items: PropTypes.arrayOf(
    PropTypes.shape({
      title: PropTypes.node.isRequired,
      content: PropTypes.node.isRequired,
      className: PropTypes.string,
    })
  ),
  defaultOpenIndex: PropTypes.number,
  allowMultiple: PropTypes.bool,
  borderless: PropTypes.bool,
  className: PropTypes.string,
};

// Add named export
export { Accordion };

// Keep default export
export default Accordion;
