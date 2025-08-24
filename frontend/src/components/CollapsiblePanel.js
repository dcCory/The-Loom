// src/components/CollapsiblePanel.js
import React, { useState } from 'react';

const CollapsiblePanel = ({ title, children, defaultOpen = true, position = 'left' }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const togglePanel = () => {
    setIsOpen(!isOpen);
  };

  // Determines alignment for the title and button based on position
  const titleAlignmentClass = position === 'left' ? 'justify-between' : 'justify-between flex-row-reverse';
  const chevronIcon = isOpen ? '▼' : '▶'; // Basic text icons

  return (
    <div className={`
      bg-gray-800 p-4 border border-gray-700 rounded-lg shadow-lg
      ${isOpen ? 'w-64' : 'w-12'}
      transition-all duration-300 ease-in-out overflow-hidden flex-shrink-0
      ${position === 'left' ? 'mr-4' : 'ml-4'}
    `}>
      <div className={`flex items-center cursor-pointer ${titleAlignmentClass}`} onClick={togglePanel}>
        {/* Only shows full title if panel is open, otherwise just a hint */}
        {isOpen ? (
          <h3 className="text-lg font-semibold text-gray-200 whitespace-nowrap">{title}</h3>
        ) : (
          <h3 className="text-lg font-semibold text-gray-200 writing-mode-vertical-rl rotate-180 whitespace-nowrap">
            {title.split('').join('\n')} {/* Stacks letters vertically */}
          </h3>
        )}
        <button
          className="p-1 text-gray-400 hover:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
          aria-expanded={isOpen}
          aria-controls={`panel-content-${title.replace(/\s/g, '-')}`}
        >
          {chevronIcon}
        </button>
      </div>
      <div
        id={`panel-content-${title.replace(/\s/g, '-')}`}
        className={`mt-4 ${isOpen ? 'block' : 'hidden'}`}
      >
        {children}
      </div>
    </div>
  );
};

export default CollapsiblePanel;