/**
 * File: src/utils/sanitizer.js
 * Version: 1.0.0
 * Date: 2025-05-13 18:04:20
 * Author: cadsanthanam
 *
 * HTML sanitization utility using DOMPurify
 */

import DOMPurify from 'dompurify';

// Configure DOMPurify globally once
DOMPurify.addHook('afterSanitizeAttributes', function (node) {
  // If element has href or src, add rel="noopener noreferrer"
  if ('href' in node) {
    node.setAttribute('target', '_blank');
    node.setAttribute('rel', 'noopener noreferrer');
  }

  // Add title attribute to iframes for accessibility
  if (node.nodeName === 'IFRAME' && !node.hasAttribute('title')) {
    node.setAttribute('title', 'Embedded content');
  }
});

/**
 * Sanitize HTML content to prevent XSS attacks
 *
 * @param {string} html - The HTML content to sanitize
 * @param {boolean} allowIframes - Whether to allow iframe elements (for video embeds)
 * @returns {string} - The sanitized HTML
 */
export const sanitizeHtml = (html = '', allowIframes = false) => {
  const config = {
    USE_PROFILES: { html: true },
    FORBID_TAGS: ['script', 'style', 'object', 'embed', 'form'],
    FORBID_ATTR: [
      'onerror',
      'onload',
      'onclick',
      'onmouseover',
      'oninput',
      'onchange',
    ],
  };

  // Conditionally allow iframes if needed for video embeds
  if (allowIframes) {
    config.ADD_TAGS = ['iframe'];
    config.ADD_ATTR = ['allow', 'allowfullscreen', 'frameborder', 'scrolling'];
  }

  return DOMPurify.sanitize(html, config);
};

export default sanitizeHtml;
