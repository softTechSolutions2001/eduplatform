/**
 * Seo Component - Provides consistent SEO management
 *
 * This component uses react-helmet-async to manage document head tags
 * for SEO optimization and social media sharing.
 *
 * Features:
 * - Consistent title format with brand name
 * - Meta description for search engines
 * - Social media meta tags (Open Graph and Twitter)
 * - Canonical URL support
 * - Default values with customization options
 *
 * @version 1.0.0
 * @author GitHub Copilot
 * @date June 2, 2025
 */

import React from 'react';
import PropTypes from 'prop-types';
import { Helmet } from 'react-helmet-async';

// Site constants
const SITE_NAME = 'SoftTech Solutions';
const DEFAULT_DESCRIPTION =
  'Learn programming skills with our interactive courses. Master web development, data science, AI and more.';
const DEFAULT_IMAGE = '/images/site/og-image.jpg';
const SITE_URL = 'https://edu-platform.com';

const Seo = ({
  title,
  description = DEFAULT_DESCRIPTION,
  image = DEFAULT_IMAGE,
  url,
  article = false,
  jsonLd = null,
  noIndex = false,
  canonicalUrl,
  children,
}) => {
  // Format the title to include site name
  const formattedTitle = `${title} | ${SITE_NAME}`;

  // Create canonical URL
  const canonical = canonicalUrl || url || window.location.href;

  return (
    <Helmet>
      {/* Standard meta tags */}
      <title>{formattedTitle}</title>
      <meta name="description" content={description} />
      {canonical && <link rel="canonical" href={canonical} />}

      {/* Open Graph tags */}
      <meta property="og:site_name" content={SITE_NAME} />
      <meta property="og:title" content={formattedTitle} />
      <meta property="og:description" content={description} />
      <meta
        property="og:image"
        content={image.startsWith('http') ? image : `${SITE_URL}${image}`}
      />
      <meta property="og:url" content={url || canonical} />
      <meta property="og:type" content={article ? 'article' : 'website'} />

      {/* Twitter tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={formattedTitle} />
      <meta name="twitter:description" content={description} />
      <meta
        name="twitter:image"
        content={image.startsWith('http') ? image : `${SITE_URL}${image}`}
      />

      {/* No index directive if specified */}
      {noIndex && <meta name="robots" content="noindex,nofollow" />}

      {/* Optional structured data */}
      {jsonLd && (
        <script type="application/ld+json">{JSON.stringify(jsonLd)}</script>
      )}

      {/* Additional elements */}
      {children}
    </Helmet>
  );
};

Seo.propTypes = {
  title: PropTypes.string.isRequired,
  description: PropTypes.string,
  image: PropTypes.string,
  url: PropTypes.string,
  article: PropTypes.bool,
  jsonLd: PropTypes.object,
  noIndex: PropTypes.bool,
  canonicalUrl: PropTypes.string,
  children: PropTypes.node,
};

export default Seo;
