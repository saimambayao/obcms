/**
 * HTMX Focus Management
 * Handles focus management for HTMX swaps to improve accessibility
 * Ensures keyboard users don't lose focus context after dynamic updates
 */

(function() {
    'use strict';

    // Store the last focused element before HTMX request
    let lastFocusedElement = null;
    let focusTrapActive = false;
    let focusableElements = [];

    /**
     * Get all focusable elements within a container
     */
    function getFocusableElements(container) {
        if (!container) return [];

        const selector = 'a[href], button:not([disabled]), textarea:not([disabled]), ' +
                        'input:not([disabled]), select:not([disabled]), ' +
                        '[tabindex]:not([tabindex="-1"])';

        return Array.from(container.querySelectorAll(selector))
            .filter(el => {
                // Filter out hidden elements
                const style = window.getComputedStyle(el);
                return style.display !== 'none' && style.visibility !== 'hidden';
            });
    }

    /**
     * Trap focus within a modal or container
     */
    function trapFocus(container) {
        if (!container) return;

        focusableElements = getFocusableElements(container);
        if (focusableElements.length === 0) return;

        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];

        // Set initial focus
        setTimeout(() => {
            firstFocusable.focus();
        }, 100);

        // Handle Tab key to trap focus
        container.addEventListener('keydown', handleFocusTrap);
        focusTrapActive = true;

        function handleFocusTrap(e) {
            if (e.key !== 'Tab') return;

            if (e.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstFocusable) {
                    e.preventDefault();
                    lastFocusable.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastFocusable) {
                    e.preventDefault();
                    firstFocusable.focus();
                }
            }
        }
    }

    /**
     * Release focus trap
     */
    function releaseFocusTrap() {
        focusTrapActive = false;
        focusableElements = [];
    }

    /**
     * Restore focus to the element that triggered the action
     */
    function restoreFocus() {
        if (lastFocusedElement && document.body.contains(lastFocusedElement)) {
            const elementToFocus = lastFocusedElement;
            setTimeout(() => {
                if (elementToFocus && document.body.contains(elementToFocus)) {
                    elementToFocus.focus();
                }
            }, 100);
        }
        lastFocusedElement = null;
    }

    // HTMX Event Handlers

    // Before request: Store the currently focused element
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        lastFocusedElement = document.activeElement;
    });

    // After swap: Manage focus based on context
    document.body.addEventListener('htmx:afterSwap', function(event) {
        const target = event.target;

        // Handle modal focus
        if (target && target.id === 'taskModalContent') {
            const modal = document.getElementById('taskModal');
            if (modal && !modal.classList.contains('hidden')) {
                trapFocus(modal);
                return;
            }
        }

        // Handle board/table swaps: Focus first interactive element
        if (target && (target.matches('[data-board-container]') ||
                      target.matches('[data-notion-table-container]'))) {
            const firstInteractive = getFocusableElements(target)[0];
            if (firstInteractive) {
                setTimeout(() => {
                    firstInteractive.focus();
                }, 100);
            }
            return;
        }

        // Default: Restore focus to triggering element
        restoreFocus();
    });

    // After settle: Announce changes to screen readers
    document.body.addEventListener('htmx:afterSettle', function(event) {
        const target = event.target;

        // Announce content updates to screen readers
        if (target) {
            announceToScreenReader('Content updated');
        }
    });

    // Modal Management

    // When modal opens
    document.body.addEventListener('click', function(event) {
        const modalLink = event.target.closest('[data-modal-link]');
        if (modalLink) {
            lastFocusedElement = modalLink;
        }

        // When modal closes
        if (event.target.closest('[data-close-modal]') ||
            event.target.matches('[data-modal-backdrop]')) {
            releaseFocusTrap();
            setTimeout(restoreFocus, 150);
        }
    });

    // Escape key to close modal
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const modal = document.getElementById('taskModal');
            if (modal && !modal.classList.contains('hidden')) {
                releaseFocusTrap();
                const closeButton = modal.querySelector('[data-close-modal]');
                if (closeButton) {
                    closeButton.click();
                }
            }
        }
    });

    /**
     * Screen Reader Announcements
     */
    function announceToScreenReader(message) {
        let announcer = document.getElementById('sr-announcer');

        if (!announcer) {
            announcer = document.createElement('div');
            announcer.id = 'sr-announcer';
            announcer.className = 'sr-only';
            announcer.setAttribute('role', 'status');
            announcer.setAttribute('aria-live', 'polite');
            announcer.setAttribute('aria-atomic', 'true');
            document.body.appendChild(announcer);
        }

        // Clear and set new message
        announcer.textContent = '';
        setTimeout(() => {
            announcer.textContent = message;
        }, 100);
    }

    // Expose utility functions globally
    window.focusManagement = {
        trapFocus: trapFocus,
        releaseFocusTrap: releaseFocusTrap,
        restoreFocus: restoreFocus,
        announceToScreenReader: announceToScreenReader
    };

    console.log('HTMX Focus Management initialized');
})();
