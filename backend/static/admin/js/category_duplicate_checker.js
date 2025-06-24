// File Path: backend/static/admin/js/category_duplicate_checker.js
// Version: 1.0.0
// Date Created: 2025-06-15 06:16:48
// Date Revised: 2025-06-15 06:16:48
// Author: sujibeautysalon
// Last Modified By: sujibeautysalon
// Last Modified: 2025-06-15 06:16:48 UTC
// User: sujibeautysalon
//
// Frontend JavaScript: Real-time Category Duplicate Prevention

(function ($) {
    'use strict';

    /**
     * Real-time category duplicate checker for Django admin and forms
     *
     * FEATURES:
     * - Live duplicate checking as user types
     * - Name normalization preview
     * - Similar category suggestions
     * - Form submission prevention for duplicates
     */

    class CategoryDuplicateChecker {
        constructor() {
            this.checkTimeout = null;
            this.lastCheckedValue = '';
            this.isChecking = false;

            this.init();
        }

        init() {
            // Find category name input field
            this.nameInput = $('input[name="name"], input[data-duplicate-check="true"]');

            if (this.nameInput.length === 0) {
                return; // No category name field found
            }

            this.setupUI();
            this.bindEvents();
        }

        setupUI() {
            // Create status indicator
            this.statusDiv = $(`
                <div id="category-duplicate-status" class="duplicate-check-status" style="margin-top: 5px;">
                    <span class="status-text"></span>
                    <div class="suggestions" style="margin-top: 5px; display: none;"></div>
                </div>
            `);

            this.nameInput.after(this.statusDiv);

            // Add CSS styles
            if (!$('#duplicate-checker-styles').length) {
                $('head').append(`
                    <style id="duplicate-checker-styles">
                        .duplicate-check-status .status-text {
                            font-size: 12px;
                            padding: 3px 6px;
                            border-radius: 3px;
                            display: inline-block;
                        }
                        .status-checking { background: #ffc107; color: #856404; }
                        .status-available { background: #d4edda; color: #155724; }
                        .status-duplicate { background: #f8d7da; color: #721c24; }
                        .status-normalized { background: #d1ecf1; color: #0c5460; }
                        .suggestions {
                            font-size: 11px;
                            color: #6c757d;
                            background: #f8f9fa;
                            padding: 5px;
                            border-radius: 3px;
                            border-left: 3px solid #007bff;
                        }
                        .suggestion-item {
                            display: block;
                            margin: 2px 0;
                        }
                    </style>
                `);
            }
        }

        bindEvents() {
            // Real-time checking as user types
            this.nameInput.on('input', (e) => {
                this.scheduleCheck();
            });

            // Check on focus out
            this.nameInput.on('blur', (e) => {
                this.checkDuplicate();
            });

            // Prevent form submission if duplicate detected
            this.nameInput.closest('form').on('submit', (e) => {
                if (this.isDuplicateDetected) {
                    e.preventDefault();
                    alert('Cannot submit: A category with this name already exists.');
                    this.nameInput.focus();
                    return false;
                }
            });
        }

        scheduleCheck() {
            // Debounce the checking to avoid too many requests
            clearTimeout(this.checkTimeout);
            this.checkTimeout = setTimeout(() => {
                this.checkDuplicate();
            }, 500);
        }

        checkDuplicate() {
            const currentValue = this.nameInput.val().trim();

            // Don't check if value hasn't changed or is empty
            if (currentValue === this.lastCheckedValue || currentValue === '') {
                return;
            }

            if (this.isChecking) {
                return; // Already checking
            }

            this.lastCheckedValue = currentValue;
            this.isChecking = true;
            this.isDuplicateDetected = false;

            this.showStatus('Checking...', 'checking');

            // Get current category ID for updates (exclude from duplicate check)
            const excludeId = this.getExcludeId();

            $.ajax({
                url: '/courses/check-duplicate/',  // Update this URL to match your URL pattern
                method: 'GET',
                data: {
                    name: currentValue,
                    exclude_id: excludeId
                },
                success: (response) => {
                    this.handleCheckResponse(response);
                },
                error: (xhr, status, error) => {
                    console.error('Duplicate check failed:', error);
                    this.showStatus('Check failed', 'error');
                },
                complete: () => {
                    this.isChecking = false;
                }
            });
        }

        handleCheckResponse(response) {
            const { is_duplicate, normalized_name, suggestions, existing_category } = response;

            if (is_duplicate) {
                this.isDuplicateDetected = true;
                this.showStatus(
                    `Duplicate! "${existing_category}" already exists`,
                    'duplicate'
                );
            } else {
                this.isDuplicateDetected = false;

                // Show normalization info if name was changed
                if (normalized_name !== this.nameInput.val().trim()) {
                    this.showStatus(
                        `Available (will be saved as "${normalized_name}")`,
                        'normalized'
                    );
                } else {
                    this.showStatus('Available ✓', 'available');
                }
            }

            // Show suggestions if any
            if (suggestions && suggestions.length > 0) {
                this.showSuggestions(suggestions);
            } else {
                this.hideSuggestions();
            }
        }

        showStatus(message, type) {
            const statusText = this.statusDiv.find('.status-text');
            statusText.text(message);
            statusText.removeClass('status-checking status-available status-duplicate status-normalized status-error');
            statusText.addClass(`status-${type}`);
        }

        showSuggestions(suggestions) {
            const suggestionsDiv = this.statusDiv.find('.suggestions');

            if (suggestions.length === 0) {
                suggestionsDiv.hide();
                return;
            }

            const suggestionHtml = suggestions.map(name =>
                `<span class="suggestion-item">• ${name}</span>`
            ).join('');

            suggestionsDiv.html(`
                <strong>Similar categories:</strong><br>
                ${suggestionHtml}
            `).show();
        }

        hideSuggestions() {
            this.statusDiv.find('.suggestions').hide();
        }

        getExcludeId() {
            // Try to get category ID from URL (for edit forms)
            const urlMatch = window.location.pathname.match(/\/(\d+)\/change\//);
            if (urlMatch) {
                return urlMatch[1];
            }

            // Try to get from hidden form field
            const idField = $('input[name="id"], input[name="pk"]');
            if (idField.length > 0 && idField.val()) {
                return idField.val();
            }

            return null;
        }
    }

    // Initialize when DOM is ready
    $(document).ready(function () {
        new CategoryDuplicateChecker();
    });

})(django.jQuery || jQuery);
