// Created on 2025-07-25
// Basic Pagination component for the EduPlatform

import React from 'react';

/**
 * A reusable pagination component
 * @param {Object} props
 * @param {Number} props.currentPage - Current page number (1-based)
 * @param {Number} props.totalPages - Total number of pages
 * @param {Function} props.onPageChange - Function to call when page changes
 * @param {Number} props.siblingCount - Number of sibling pages to show on each side
 * @param {String} props.className - Additional classes for styling
 */
const Pagination = ({
  currentPage = 1,
  totalPages = 1,
  onPageChange,
  siblingCount = 1,
  className = '',
}) => {
  // Don't render pagination if there's only one page
  if (totalPages <= 1) return null;

  // Ensure current page is within valid range
  const validCurrentPage = Math.max(1, Math.min(currentPage, totalPages));

  // Generate page numbers to show
  const getPageNumbers = () => {
    // Calculate range of pages to show
    const leftSiblingIndex = Math.max(1, validCurrentPage - siblingCount);
    const rightSiblingIndex = Math.min(
      totalPages,
      validCurrentPage + siblingCount
    );

    const pages = [];

    // Always include first page
    if (leftSiblingIndex > 1) {
      pages.push(1);
      // Add ellipsis if there's a gap
      if (leftSiblingIndex > 2) {
        pages.push('...');
      }
    }

    // Add pages in the middle range
    for (let i = leftSiblingIndex; i <= rightSiblingIndex; i++) {
      pages.push(i);
    }

    // Always include last page
    if (rightSiblingIndex < totalPages) {
      // Add ellipsis if there's a gap
      if (rightSiblingIndex < totalPages - 1) {
        pages.push('...');
      }
      pages.push(totalPages);
    }

    return pages;
  };

  // Handle page change
  const handlePageChange = page => {
    if (
      page !== validCurrentPage &&
      page >= 1 &&
      page <= totalPages &&
      onPageChange
    ) {
      onPageChange(page);
    }
  };

  const pageNumbers = getPageNumbers();

  return (
    <nav className={`flex justify-center items-center space-x-1 ${className}`}>
      {/* Previous button */}
      <button
        onClick={() => handlePageChange(validCurrentPage - 1)}
        disabled={validCurrentPage === 1}
        className={`px-3 py-2 rounded-md ${
          validCurrentPage === 1
            ? 'text-gray-300 cursor-not-allowed'
            : 'text-gray-700 hover:bg-gray-100'
        }`}
        aria-label="Previous page"
      >
        <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      {/* Page numbers */}
      {pageNumbers.map((page, index) => (
        <React.Fragment key={index}>
          {page === '...' ? (
            <span className="px-3 py-2">...</span>
          ) : (
            <button
              onClick={() => handlePageChange(page)}
              className={`px-3 py-2 rounded-md ${
                page === validCurrentPage
                  ? 'bg-primary-500 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
              aria-current={page === validCurrentPage ? 'page' : undefined}
              aria-label={`Page ${page}`}
            >
              {page}
            </button>
          )}
        </React.Fragment>
      ))}

      {/* Next button */}
      <button
        onClick={() => handlePageChange(validCurrentPage + 1)}
        disabled={validCurrentPage === totalPages}
        className={`px-3 py-2 rounded-md ${
          validCurrentPage === totalPages
            ? 'text-gray-300 cursor-not-allowed'
            : 'text-gray-700 hover:bg-gray-100'
        }`}
        aria-label="Next page"
      >
        <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
            clipRule="evenodd"
          />
        </svg>
      </button>
    </nav>
  );
};

export default Pagination;
