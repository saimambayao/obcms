/**
 * Work Item Tree Component JavaScript
 *
 * Features:
 * - Expand/collapse with state persistence (localStorage)
 * - Keyboard navigation (Arrow keys, Space, Enter)
 * - HTMX lazy loading integration
 * - Accessibility (ARIA attributes, focus management)
 * - Smooth animations
 *
 * Dependencies:
 * - HTMX (for lazy loading)
 *
 * Usage:
 *   Include this script after HTMX is loaded.
 *   Tree nodes are automatically initialized on page load.
 */

(function() {
    'use strict';

    // ========== Constants ==========
    const STORAGE_KEY = 'obcms_work_item_tree_state';
    const ANIMATION_DURATION = 300; // milliseconds

    // ========== State Management ==========

    /**
     * Get expanded state from localStorage
     * @returns {Object} Map of work item IDs to expanded state
     */
    function getExpandedState() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            return stored ? JSON.parse(stored) : {};
        } catch (error) {
            console.warn('Failed to load tree state from localStorage:', error);
            return {};
        }
    }

    /**
     * Save expanded state to localStorage
     * @param {string} workItemId - Work item ID
     * @param {boolean} isExpanded - Expanded state
     */
    function saveExpandedState(workItemId, isExpanded) {
        try {
            const state = getExpandedState();
            if (isExpanded) {
                state[workItemId] = true;
            } else {
                delete state[workItemId];
            }
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        } catch (error) {
            console.warn('Failed to save tree state to localStorage:', error);
        }
    }

    /**
     * Check if a work item should be expanded based on saved state
     * @param {string} workItemId - Work item ID
     * @returns {boolean}
     */
    function shouldBeExpanded(workItemId) {
        const state = getExpandedState();
        return state[workItemId] === true;
    }

    // ========== Expand/Collapse Logic ==========

    /**
     * Toggle expand/collapse state of a work item node
     * @param {HTMLElement} button - The expand toggle button
     * @param {string} workItemId - Work item ID
     */
    window.toggleWorkItemNode = function(button, workItemId) {
        const node = document.getElementById(`node-${workItemId}`);
        const childrenContainer = document.getElementById(`children-${workItemId}`);
        const icon = document.getElementById(`toggle-icon-${workItemId}`);

        if (!node || !childrenContainer) {
            console.warn(`Node or children container not found for work item ${workItemId}`);
            return;
        }

        const isExpanded = button.getAttribute('aria-expanded') === 'true';
        const newExpandedState = !isExpanded;

        // Update ARIA attributes
        button.setAttribute('aria-expanded', newExpandedState);
        node.setAttribute('aria-expanded', newExpandedState);

        // Rotate icon
        if (icon) {
            if (newExpandedState) {
                icon.style.transform = 'rotate(90deg)';
            } else {
                icon.style.transform = 'rotate(0deg)';
            }
        }

        // Toggle children container
        if (newExpandedState) {
            // Expand
            childrenContainer.classList.remove('hidden');
            // Force reflow for animation
            void childrenContainer.offsetHeight;
            childrenContainer.classList.add('expanded');
        } else {
            // Collapse
            childrenContainer.classList.remove('expanded');
            setTimeout(() => {
                if (!childrenContainer.classList.contains('expanded')) {
                    childrenContainer.classList.add('hidden');
                }
            }, ANIMATION_DURATION);
        }

        // Save state to localStorage
        saveExpandedState(workItemId, newExpandedState);

        // Announce state change to screen readers
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.className = 'sr-only';
        announcement.textContent = newExpandedState
            ? `Expanded ${button.getAttribute('aria-label') || 'sub-items'}`
            : 'Collapsed sub-items';
        document.body.appendChild(announcement);
        setTimeout(() => announcement.remove(), 1000);
    };

    // ========== Keyboard Navigation ==========

    /**
     * Initialize keyboard navigation for tree nodes
     */
    function initKeyboardNavigation() {
        document.addEventListener('keydown', function(event) {
            const activeNode = document.activeElement.closest('.tree-node');
            if (!activeNode) return;

            const nodeId = activeNode.dataset.nodeId;
            const depth = parseInt(activeNode.dataset.depth, 10);

            switch (event.key) {
                case 'ArrowRight':
                    // Expand if has children and is collapsed
                    handleArrowRight(activeNode, nodeId);
                    event.preventDefault();
                    break;

                case 'ArrowLeft':
                    // Collapse if expanded, or move to parent
                    handleArrowLeft(activeNode, nodeId, depth);
                    event.preventDefault();
                    break;

                case 'ArrowDown':
                    // Move to next sibling or first child if expanded
                    handleArrowDown(activeNode);
                    event.preventDefault();
                    break;

                case 'ArrowUp':
                    // Move to previous sibling or parent
                    handleArrowUp(activeNode);
                    event.preventDefault();
                    break;

                case ' ':
                case 'Enter':
                    // Toggle expand/collapse
                    const toggleButton = activeNode.querySelector('.expand-toggle');
                    if (toggleButton) {
                        toggleButton.click();
                        event.preventDefault();
                    }
                    break;

                case 'Home':
                    // Move to first root node
                    focusFirstNode();
                    event.preventDefault();
                    break;

                case 'End':
                    // Move to last visible node
                    focusLastNode();
                    event.preventDefault();
                    break;
            }
        });
    }

    function handleArrowRight(activeNode, nodeId) {
        const toggleButton = activeNode.querySelector('.expand-toggle');
        if (!toggleButton) return;

        const isExpanded = toggleButton.getAttribute('aria-expanded') === 'true';
        if (!isExpanded) {
            // Expand the node
            toggleButton.click();
        } else {
            // Already expanded, move to first child
            const firstChild = document.querySelector(`#children-${nodeId} > .tree-node`);
            if (firstChild) {
                firstChild.focus();
                firstChild.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            }
        }
    }

    function handleArrowLeft(activeNode, nodeId, depth) {
        const toggleButton = activeNode.querySelector('.expand-toggle');
        if (toggleButton && toggleButton.getAttribute('aria-expanded') === 'true') {
            // Collapse the node
            toggleButton.click();
        } else if (depth > 0) {
            // Move to parent node
            const parentNode = activeNode.closest('[data-depth="' + (depth - 1) + '"]');
            if (parentNode) {
                parentNode.focus();
                parentNode.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            }
        }
    }

    function handleArrowDown(activeNode) {
        // Try to find next visible node (sibling or nested child)
        let nextNode = findNextVisibleNode(activeNode);
        if (nextNode) {
            nextNode.focus();
            nextNode.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    function handleArrowUp(activeNode) {
        // Try to find previous visible node
        let prevNode = findPreviousVisibleNode(activeNode);
        if (prevNode) {
            prevNode.focus();
            prevNode.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    function findNextVisibleNode(node) {
        // If expanded, go to first child
        const nodeId = node.dataset.nodeId;
        const toggleButton = node.querySelector('.expand-toggle');
        if (toggleButton && toggleButton.getAttribute('aria-expanded') === 'true') {
            const firstChild = document.querySelector(`#children-${nodeId} > .tree-node`);
            if (firstChild) return firstChild;
        }

        // Otherwise, go to next sibling
        let nextSibling = node.nextElementSibling;
        while (nextSibling && !nextSibling.classList.contains('tree-node')) {
            nextSibling = nextSibling.nextElementSibling;
        }
        if (nextSibling) return nextSibling;

        // If no sibling, go to parent's next sibling
        const parentContainer = node.closest('.children-container');
        if (parentContainer) {
            const parentNode = parentContainer.previousElementSibling;
            if (parentNode && parentNode.classList.contains('tree-node')) {
                return findNextVisibleNode(parentNode);
            }
        }

        return null;
    }

    function findPreviousVisibleNode(node) {
        // Go to previous sibling's last visible descendant, or previous sibling, or parent
        let prevSibling = node.previousElementSibling;
        while (prevSibling && !prevSibling.classList.contains('tree-node')) {
            prevSibling = prevSibling.previousElementSibling;
        }

        if (prevSibling) {
            // Find the last visible descendant of previous sibling
            return findLastVisibleDescendant(prevSibling);
        }

        // No previous sibling, go to parent
        const parentContainer = node.closest('.children-container');
        if (parentContainer) {
            const parentNode = parentContainer.previousElementSibling;
            if (parentNode && parentNode.classList.contains('tree-node')) {
                return parentNode;
            }
        }

        return null;
    }

    function findLastVisibleDescendant(node) {
        const nodeId = node.dataset.nodeId;
        const toggleButton = node.querySelector('.expand-toggle');
        if (toggleButton && toggleButton.getAttribute('aria-expanded') === 'true') {
            const childrenContainer = document.getElementById(`children-${nodeId}`);
            if (childrenContainer) {
                const children = childrenContainer.querySelectorAll(':scope > .tree-node');
                if (children.length > 0) {
                    return findLastVisibleDescendant(children[children.length - 1]);
                }
            }
        }
        return node;
    }

    function focusFirstNode() {
        const firstNode = document.querySelector('.tree-node[data-depth="0"]');
        if (firstNode) {
            firstNode.focus();
            firstNode.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    function focusLastNode() {
        const rootNodes = document.querySelectorAll('.tree-node[data-depth="0"]');
        if (rootNodes.length > 0) {
            const lastRoot = rootNodes[rootNodes.length - 1];
            const lastVisible = findLastVisibleDescendant(lastRoot);
            if (lastVisible) {
                lastVisible.focus();
                lastVisible.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            }
        }
    }

    // ========== HTMX Integration ==========

    /**
     * Initialize HTMX event listeners for tree updates
     */
    function initHTMXListeners() {
        // After HTMX loads children, restore expanded state
        document.body.addEventListener('htmx:afterSwap', function(event) {
            const target = event.detail.target;
            if (target && target.id && target.id.startsWith('children-')) {
                const workItemId = target.id.replace('children-', '');

                // Initialize newly loaded child nodes
                const childNodes = target.querySelectorAll('.tree-node');
                childNodes.forEach(function(childNode) {
                    const childId = childNode.dataset.nodeId;
                    if (shouldBeExpanded(childId)) {
                        const toggleButton = childNode.querySelector('.expand-toggle');
                        if (toggleButton && toggleButton.getAttribute('aria-expanded') !== 'true') {
                            // Trigger expansion for persisted state
                            toggleButton.click();
                        }
                    }
                });

                // Announce to screen readers
                announceChildrenLoaded(childNodes.length);
            }
        });

        // Handle HTMX request errors
        document.body.addEventListener('htmx:responseError', function(event) {
            const target = event.detail.target;
            if (target && target.id && target.id.startsWith('children-')) {
                const workItemId = target.id.replace('children-', '');
                const node = document.getElementById(`node-${workItemId}`);
                const toggleButton = node?.querySelector('.expand-toggle');

                // Reset to collapsed state on error
                if (toggleButton) {
                    toggleButton.setAttribute('aria-expanded', 'false');
                    const icon = document.getElementById(`toggle-icon-${workItemId}`);
                    if (icon) {
                        icon.style.transform = 'rotate(0deg)';
                    }
                }

                // Show error message
                target.innerHTML = `
                    <div class="p-4 text-center text-red-600">
                        <i class="fas fa-exclamation-triangle mb-2"></i>
                        <p class="text-sm">Failed to load sub-items. Please try again.</p>
                    </div>
                `;
            }
        });
    }

    function announceChildrenLoaded(count) {
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.className = 'sr-only';
        announcement.textContent = `Loaded ${count} sub-item${count !== 1 ? 's' : ''}`;
        document.body.appendChild(announcement);
        setTimeout(() => announcement.remove(), 1000);
    }

    // ========== Restore State on Load ==========

    /**
     * Restore expanded state from localStorage on page load
     */
    function restoreExpandedState() {
        const expandedState = getExpandedState();
        Object.keys(expandedState).forEach(function(workItemId) {
            const node = document.getElementById(`node-${workItemId}`);
            if (!node) return;

            const toggleButton = node.querySelector('.expand-toggle');
            if (toggleButton && toggleButton.getAttribute('aria-expanded') !== 'true') {
                // Trigger expansion
                setTimeout(() => toggleButton.click(), 100);
            }
        });
    }

    // ========== Initialization ==========

    /**
     * Initialize the work item tree component
     */
    function init() {
        console.log('[WorkItemTree] Initializing...');

        // Initialize keyboard navigation
        initKeyboardNavigation();

        // Initialize HTMX listeners
        initHTMXListeners();

        // Restore expanded state
        restoreExpandedState();

        console.log('[WorkItemTree] Initialized successfully');
    }

    // Run initialization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // ========== Public API ==========

    window.WorkItemTree = {
        getExpandedState: getExpandedState,
        saveExpandedState: saveExpandedState,
        clearState: function() {
            try {
                localStorage.removeItem(STORAGE_KEY);
                console.log('[WorkItemTree] State cleared');
            } catch (error) {
                console.warn('Failed to clear tree state:', error);
            }
        },
        expandAll: function() {
            document.querySelectorAll('.expand-toggle[aria-expanded="false"]').forEach(function(button) {
                button.click();
            });
        },
        collapseAll: function() {
            document.querySelectorAll('.expand-toggle[aria-expanded="true"]').forEach(function(button) {
                button.click();
            });
        }
    };

})();
