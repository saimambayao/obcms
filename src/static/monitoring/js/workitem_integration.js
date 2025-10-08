/**
 * WorkItem Integration JavaScript
 * Handles interactions for MOA PPA - WorkItem tracking
 *
 * @requires HTMX
 * @author OBCMS Development Team
 * @version 1.0.0
 */

(function() {
    'use strict';

    /**
     * Toggle work item children visibility
     * @param {string} workItemId - ID of the work item
     */
    window.toggleWorkItemChildren = function(workItemId) {
        const childrenContainer = document.getElementById(`children-${workItemId}`);
        const toggleIcon = document.getElementById(`toggle-icon-${workItemId}`);

        if (!childrenContainer || !toggleIcon) {
            console.warn(`Work item ${workItemId} children or toggle icon not found`);
            return;
        }

        // Toggle collapsed/expanded classes
        if (childrenContainer.classList.contains('collapsed')) {
            childrenContainer.classList.remove('collapsed');
            childrenContainer.classList.add('expanded');
            toggleIcon.style.transform = 'rotate(0deg)';
        } else {
            childrenContainer.classList.remove('expanded');
            childrenContainer.classList.add('collapsed');
            toggleIcon.style.transform = 'rotate(-90deg)';
        }

        // Save state to localStorage
        const expandedState = JSON.parse(localStorage.getItem('workItemExpandedState') || '{}');
        expandedState[workItemId] = !childrenContainer.classList.contains('collapsed');
        localStorage.setItem('workItemExpandedState', JSON.stringify(expandedState));
    };

    /**
     * Budget Distribution Validation Module
     * Handles weighted, manual, and equal distribution validation
     */
    const BudgetDistribution = {
        totalBudget: 0,
        tolerance: 0.01,
        currentMethod: 'equal',

        /**
         * Initialize budget distribution validator
         * @param {number} totalBudget - Total budget to distribute
         */
        init(totalBudget) {
            this.totalBudget = parseFloat(totalBudget);
            this.attachValidators();
        },

        /**
         * Attach validators to distribution method inputs
         */
        attachValidators() {
            // Weighted distribution inputs
            const weightInputs = document.querySelectorAll('.weight-input');
            weightInputs.forEach(input => {
                input.addEventListener('input', () => this.validateWeighted());
                input.addEventListener('blur', () => this.formatWeightInput(input));
            });

            // Manual budget inputs
            const manualInputs = document.querySelectorAll('.manual-budget-input');
            manualInputs.forEach(input => {
                input.addEventListener('input', () => this.validateManual());
                input.addEventListener('blur', () => this.formatInputOnBlur(input));
            });

            // Distribution method radio buttons
            const methodRadios = document.querySelectorAll('input[name="distribution_method"]');
            methodRadios.forEach(radio => {
                radio.addEventListener('change', (e) => this.switchMethod(e.target.value));
            });
        },

        /**
         * Switch distribution method and validate
         * @param {string} method - Distribution method (equal, weighted, manual)
         */
        switchMethod(method) {
            this.currentMethod = method;

            // Hide all method sections
            document.querySelectorAll('.distribution-method-section').forEach(section => {
                section.classList.add('hidden');
            });

            // Show selected method section
            const selectedSection = document.getElementById(`${method}-distribution-section`);
            if (selectedSection) {
                selectedSection.classList.remove('hidden');
            }

            // Validate based on method
            if (method === 'weighted') {
                this.validateWeighted();
            } else if (method === 'manual') {
                this.validateManual();
            } else if (method === 'equal') {
                this.previewEqual();
            }
        },

        /**
         * Validate weighted distribution (must sum to 100%)
         * @returns {boolean} True if valid
         */
        validateWeighted() {
            const inputs = document.querySelectorAll('.weight-input');
            let totalWeight = 0;

            inputs.forEach(input => {
                const value = parseFloat(input.value) || 0;
                totalWeight += value;

                // Highlight invalid inputs
                if (value < 0 || value > 100) {
                    input.classList.add('border-red-500');
                } else {
                    input.classList.remove('border-red-500');
                }
            });

            const isValid = Math.abs(totalWeight - 100) < 0.01;
            const remaining = 100 - totalWeight;
            this.updateValidationUI('weighted', isValid, remaining, '%');
            return isValid;
        },

        /**
         * Validate manual distribution (must sum to total budget)
         * @returns {boolean} True if valid
         */
        validateManual() {
            const inputs = document.querySelectorAll('.manual-budget-input');
            let totalAllocated = 0;

            inputs.forEach(input => {
                const value = this.parseCurrency(input.value);
                totalAllocated += value;

                // Highlight over-budget inputs
                if (value > this.totalBudget) {
                    input.classList.add('border-red-500');
                } else {
                    input.classList.remove('border-red-500');
                }
            });

            const isValid = Math.abs(totalAllocated - this.totalBudget) < this.tolerance;
            const remaining = this.totalBudget - totalAllocated;
            this.updateValidationUI('manual', isValid, remaining, 'currency');
            return isValid;
        },

        /**
         * Preview equal distribution
         */
        previewEqual() {
            const count = document.querySelectorAll('[data-work-item-id]').length;
            if (count === 0) return;

            const perItem = this.totalBudget / count;
            const preview = document.getElementById('equal-distribution-preview');

            if (preview) {
                preview.innerHTML = `
                    <div class="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                        <div class="flex items-center gap-3">
                            <i class="fas fa-calculator text-emerald-600 text-xl"></i>
                            <div>
                                <p class="text-sm text-gray-600">Each work item will receive:</p>
                                <p class="text-2xl font-bold text-emerald-600">${this.formatCurrency(perItem)}</p>
                            </div>
                        </div>
                    </div>
                `;
            }

            // Enable submit button for equal distribution
            const submitBtn = document.getElementById('distribute-submit');
            if (submitBtn) {
                submitBtn.disabled = false;
            }
        },

        /**
         * Update validation UI indicators
         * @param {string} method - Distribution method
         * @param {boolean} isValid - Whether distribution is valid
         * @param {number} remaining - Remaining amount
         * @param {string} format - Format type (currency or %)
         */
        updateValidationUI(method, isValid, remaining, format) {
            const indicator = document.getElementById(`${method}-validation`);
            const submitBtn = document.getElementById('distribute-submit');

            if (!indicator) return;

            if (isValid) {
                indicator.innerHTML = `
                    <div class="flex items-center gap-2 text-emerald-600">
                        <i class="fas fa-check-circle"></i>
                        <span class="font-medium">Valid distribution</span>
                    </div>
                `;
                if (submitBtn) submitBtn.disabled = false;
            } else {
                const formatted = format === 'currency'
                    ? this.formatCurrency(remaining)
                    : `${remaining.toFixed(2)}%`;

                const message = remaining > 0 ? 'Remaining' : 'Over by';
                const absFormatted = format === 'currency'
                    ? this.formatCurrency(Math.abs(remaining))
                    : `${Math.abs(remaining).toFixed(2)}%`;

                indicator.innerHTML = `
                    <div class="flex items-center gap-2 text-red-600">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span class="font-medium">${message}: ${absFormatted}</span>
                    </div>
                `;
                if (submitBtn) submitBtn.disabled = true;
            }
        },

        /**
         * Format currency with Philippine Peso symbol
         * @param {number} amount - Amount to format
         * @returns {string} Formatted currency
         */
        formatCurrency(amount) {
            return '₱' + amount.toLocaleString('en-PH', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        },

        /**
         * Parse currency input removing ₱ and commas
         * @param {string} value - Currency string
         * @returns {number} Parsed amount
         */
        parseCurrency(value) {
            if (typeof value === 'number') return value;
            return parseFloat(value.replace(/[₱,]/g, '')) || 0;
        },

        /**
         * Format currency input on blur
         * @param {HTMLInputElement} input - Input element
         */
        formatInputOnBlur(input) {
            const value = this.parseCurrency(input.value);
            input.value = this.formatCurrency(value);
        },

        /**
         * Format weight input on blur
         * @param {HTMLInputElement} input - Input element
         */
        formatWeightInput(input) {
            const value = parseFloat(input.value) || 0;
            input.value = value.toFixed(2);
        }
    };

    /**
     * Modal Management Module
     * Handles modal open/close with focus trapping and keyboard navigation
     */
    const ModalManager = {
        /**
         * Open modal with focus trap
         * @param {string} modalId - Modal element ID
         */
        openModal(modalId) {
            const modal = document.getElementById(modalId);
            if (!modal) {
                console.error(`Modal ${modalId} not found`);
                return;
            }

            modal.classList.remove('hidden');
            modal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';

            // Focus trap
            const focusableElements = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            if (firstElement) {
                setTimeout(() => firstElement.focus(), 100);
            }

            // Keyboard navigation
            const handleKeyDown = (e) => {
                // Escape key closes modal
                if (e.key === 'Escape') {
                    this.closeModal(modalId);
                }

                // Tab trap
                if (e.key === 'Tab') {
                    if (e.shiftKey && document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    } else if (!e.shiftKey && document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            };

            modal.addEventListener('keydown', handleKeyDown);
            modal.dataset.keydownHandler = 'attached';
        },

        /**
         * Close modal and restore focus
         * @param {string} modalId - Modal element ID
         */
        closeModal(modalId) {
            const modal = document.getElementById(modalId);
            if (!modal) return;

            modal.classList.add('hidden');
            modal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';

            // Clean up event listeners
            if (modal.dataset.keydownHandler === 'attached') {
                modal.removeEventListener('keydown', () => {});
                delete modal.dataset.keydownHandler;
            }
        }
    };

    /**
     * Open budget distribution modal (public API)
     */
    window.openBudgetDistributionModal = function() {
        const modal = document.getElementById('budgetDistributionModal');
        const modalContent = document.getElementById('budgetDistributionModalContent');

        if (!modal || !modalContent) {
            console.error('Budget distribution modal not found');
            return;
        }

        // Load modal content via HTMX
        const ppaId = getPPAIdFromURL();
        if (ppaId) {
            htmx.ajax('GET', `/monitoring/moa-ppas/${ppaId}/budget-distribution-modal/`, {
                target: '#budgetDistributionModalContent',
                swap: 'innerHTML'
            }).then(() => {
                // Initialize budget distribution after modal content loads
                const totalBudget = modal.querySelector('[data-total-budget]')?.dataset.totalBudget;
                if (totalBudget) {
                    BudgetDistribution.init(parseFloat(totalBudget));
                }
            });
        }

        ModalManager.openModal('budgetDistributionModal');
    };

    /**
     * Close budget distribution modal (public API)
     */
    window.closeBudgetDistributionModal = function() {
        ModalManager.closeModal('budgetDistributionModal');
    };

    /**
     * Get PPA ID from current URL
     * @returns {string|null} PPA ID
     */
    function getPPAIdFromURL() {
        const match = window.location.pathname.match(/\/monitoring\/entry\/(\d+)\//);
        return match ? match[1] : null;
    }

    /**
     * Restore expanded state from localStorage
     */
    function restoreExpandedState() {
        const expandedState = JSON.parse(localStorage.getItem('workItemExpandedState') || '{}');

        Object.keys(expandedState).forEach(workItemId => {
            if (expandedState[workItemId]) {
                const childrenContainer = document.getElementById(`children-${workItemId}`);
                const toggleIcon = document.getElementById(`toggle-icon-${workItemId}`);

                if (childrenContainer && toggleIcon) {
                    childrenContainer.classList.remove('collapsed');
                    childrenContainer.classList.add('expanded');
                    toggleIcon.style.transform = 'rotate(0deg)';
                }
            }
        });
    }

    /**
     * Enhanced HTMX Event Handlers
     * Provides instant UI updates, loading states, and error handling
     */

    /**
     * After HTMX swaps content into the DOM
     */
    document.addEventListener('htmx:afterSwap', function(event) {
        // Restore expanded state after HTMX updates
        if (event.detail.target.id === 'work-items-tree' ||
            event.detail.target.id === 'work-items-tab-content') {
            restoreExpandedState();
        }

        // Handle budget distribution modal content load
        if (event.detail.target.id === 'budgetDistributionModalContent') {
            const totalBudget = event.detail.target.querySelector('[data-total-budget]')?.dataset.totalBudget;
            if (totalBudget) {
                BudgetDistribution.init(parseFloat(totalBudget));
            }
        }

        // Show success toast if work item was created/updated
        if (event.detail.target.id === 'workItemModal') {
            const responseHTML = event.detail.xhr.responseText;
            if (responseHTML.includes('work-item-created') || responseHTML.includes('work-item-updated')) {
                showToast('Work item saved successfully', 'success');

                // Refresh work items tree
                setTimeout(() => {
                    refreshWorkItemsTree();
                }, 500);
            }
        }

        // Handle HX-Trigger custom events
        const trigger = event.detail.xhr.getResponseHeader('HX-Trigger');
        if (trigger) {
            try {
                const triggers = JSON.parse(trigger);

                // Show toast notification
                if (triggers['show-toast']) {
                    const toast = triggers['show-toast'];
                    if (typeof toast === 'string') {
                        showToast(toast, 'success');
                    } else {
                        showToast(toast.message, toast.type || 'success');
                    }
                }

                // Refresh counters
                if (triggers['refresh-counters']) {
                    refreshWorkItemCounters();
                }

                // Refresh progress bars
                if (triggers['refresh-progress']) {
                    refreshProgressBars();
                }

                // Close modal
                if (triggers['close-modal']) {
                    ModalManager.closeModal(triggers['close-modal']);
                }
            } catch (e) {
                console.warn('Failed to parse HX-Trigger header:', e);
            }
        }
    });

    /**
     * Before HTMX sends request - show loading states
     */
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        const target = event.detail.target;

        // Show loading indicator for tree updates
        if (target.id === 'work-items-tree' || target.id === 'work-items-tab-content') {
            target.style.opacity = '0.6';
            target.style.pointerEvents = 'none';

            // Add loading spinner
            const spinner = document.createElement('div');
            spinner.id = 'htmx-loading-spinner';
            spinner.className = 'absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10';
            spinner.innerHTML = `
                <div class="flex items-center gap-3">
                    <i class="fas fa-spinner fa-spin text-blue-500 text-2xl"></i>
                    <span class="text-gray-600 font-medium">Loading...</span>
                </div>
            `;
            target.style.position = 'relative';
            target.appendChild(spinner);
        }

        // Disable submit buttons during form submission
        if (event.detail.elt.tagName === 'FORM') {
            const submitBtns = event.detail.elt.querySelectorAll('button[type="submit"]');
            submitBtns.forEach(btn => {
                btn.disabled = true;
                btn.dataset.originalText = btn.textContent;
                btn.innerHTML = `
                    <i class="fas fa-spinner fa-spin mr-2"></i>
                    Processing...
                `;
            });
        }
    });

    /**
     * After HTMX completes request - hide loading states
     */
    document.body.addEventListener('htmx:afterRequest', function(event) {
        const target = event.detail.target;

        // Remove loading indicator
        if (target.id === 'work-items-tree' || target.id === 'work-items-tab-content') {
            target.style.opacity = '1';
            target.style.pointerEvents = 'auto';

            const spinner = document.getElementById('htmx-loading-spinner');
            if (spinner) {
                spinner.remove();
            }
        }

        // Re-enable submit buttons
        if (event.detail.elt.tagName === 'FORM') {
            const submitBtns = event.detail.elt.querySelectorAll('button[type="submit"]');
            submitBtns.forEach(btn => {
                btn.disabled = false;
                if (btn.dataset.originalText) {
                    btn.textContent = btn.dataset.originalText;
                    delete btn.dataset.originalText;
                }
            });
        }
    });

    /**
     * Handle HTMX errors gracefully
     */
    document.body.addEventListener('htmx:responseError', function(event) {
        const status = event.detail.xhr.status;
        let message = 'An error occurred. Please try again.';

        if (status === 403) {
            message = 'Permission denied. You do not have access to this resource.';
        } else if (status === 404) {
            message = 'Resource not found.';
        } else if (status === 500) {
            message = 'Server error. Please contact support if this persists.';
        }

        showToast(message, 'error');
        console.error('HTMX error:', event.detail);
    });

    /**
     * Handle HTMX network errors
     */
    document.body.addEventListener('htmx:sendError', function(event) {
        showToast('Network error. Please check your connection.', 'error');
        console.error('HTMX network error:', event.detail);
    });

    /**
     * Refresh work item counters after updates
     */
    function refreshWorkItemCounters() {
        const counters = document.querySelectorAll('[data-counter-type]');
        counters.forEach(counter => {
            const type = counter.dataset.counterType;
            const ppaId = getPPAIdFromURL();

            if (ppaId) {
                htmx.ajax('GET', `/monitoring/moa-ppas/${ppaId}/counters/${type}/`, {
                    target: counter,
                    swap: 'innerHTML'
                });
            }
        });
    }

    /**
     * Refresh progress bars after work item updates
     */
    function refreshProgressBars() {
        const progressBars = document.querySelectorAll('[data-progress-bar]');
        progressBars.forEach(bar => {
            const workItemId = bar.dataset.workItemId;
            const ppaId = getPPAIdFromURL();

            if (ppaId && workItemId) {
                htmx.ajax('GET', `/monitoring/moa-ppas/${ppaId}/work-items/${workItemId}/progress/`, {
                    target: bar,
                    swap: 'innerHTML'
                });
            }
        });
    }

    /**
     * Refresh work items tree via HTMX
     */
    function refreshWorkItemsTree() {
        const ppaId = getPPAIdFromURL();
        if (ppaId) {
            htmx.ajax('GET', `/monitoring/moa-ppas/${ppaId}/work-items-tab/`, {
                target: '#work-items-tab-content',
                swap: 'innerHTML'
            });
        }
    }

    /**
     * Show toast notification
     * @param {string} message - Toast message
     * @param {string} type - Toast type (success, error, warning, info)
     */
    function showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-xl shadow-lg transition-all duration-300 transform translate-x-full`;

        // Set colors based on type
        const colors = {
            success: 'bg-emerald-500 text-white',
            error: 'bg-red-500 text-white',
            warning: 'bg-amber-500 text-white',
            info: 'bg-blue-500 text-white'
        };
        toast.className += ` ${colors[type] || colors.info}`;

        // Set icon based on type
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        const icon = icons[type] || icons.info;

        toast.innerHTML = `
            <div class="flex items-center gap-3">
                <i class="fas ${icon} text-xl"></i>
                <span class="font-medium">${message}</span>
            </div>
        `;

        document.body.appendChild(toast);

        // Slide in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);

        // Slide out after 3 seconds
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    /**
     * Handle keyboard shortcuts
     */
    document.addEventListener('keydown', function(event) {
        // Close modals on Escape key
        if (event.key === 'Escape') {
            closeBudgetDistributionModal();

            const workItemModal = document.getElementById('workItemModal');
            if (workItemModal && !workItemModal.classList.contains('hidden')) {
                workItemModal.classList.add('hidden');
            }
        }

        // Expand all work items (Ctrl+E)
        if (event.ctrlKey && event.key === 'e') {
            event.preventDefault();
            expandAllWorkItems();
        }

        // Collapse all work items (Ctrl+C)
        if (event.ctrlKey && event.key === 'c') {
            event.preventDefault();
            collapseAllWorkItems();
        }
    });

    /**
     * Expand all work items
     */
    function expandAllWorkItems() {
        const childrenContainers = document.querySelectorAll('.work-item-children');
        const expandedState = {};

        childrenContainers.forEach(container => {
            const workItemId = container.id.replace('children-', '');
            container.classList.remove('collapsed');
            container.classList.add('expanded');

            const toggleIcon = document.getElementById(`toggle-icon-${workItemId}`);
            if (toggleIcon) {
                toggleIcon.style.transform = 'rotate(0deg)';
            }

            expandedState[workItemId] = true;
        });

        localStorage.setItem('workItemExpandedState', JSON.stringify(expandedState));
        showToast('All work items expanded', 'info');
    }

    /**
     * Collapse all work items
     */
    function collapseAllWorkItems() {
        const childrenContainers = document.querySelectorAll('.work-item-children');
        const expandedState = {};

        childrenContainers.forEach(container => {
            const workItemId = container.id.replace('children-', '');
            container.classList.remove('expanded');
            container.classList.add('collapsed');

            const toggleIcon = document.getElementById(`toggle-icon-${workItemId}`);
            if (toggleIcon) {
                toggleIcon.style.transform = 'rotate(-90deg)';
            }

            expandedState[workItemId] = false;
        });

        localStorage.setItem('workItemExpandedState', JSON.stringify(expandedState));
        showToast('All work items collapsed', 'info');
    }

    /**
     * Calculate budget variance
     * @param {number} allocated - Allocated budget
     * @param {number} actual - Actual spending
     * @returns {object} Variance details
     */
    function calculateBudgetVariance(allocated, actual) {
        const variance = actual - allocated;
        const percentage = allocated > 0 ? (variance / allocated) * 100 : 0;

        return {
            amount: variance,
            percentage: percentage,
            status: variance > 0 ? 'over' : variance < 0 ? 'under' : 'on-budget'
        };
    }

    /**
     * Update progress bars with animation
     * @param {string} workItemId - Work item ID
     * @param {number} progress - Progress percentage (0-100)
     */
    window.updateWorkItemProgress = function(workItemId, progress) {
        const progressBar = document.querySelector(`[data-work-item-id="${workItemId}"] .progress-bar-fill`);

        if (progressBar) {
            progressBar.style.width = `${progress}%`;

            // Add completed class if 100%
            if (progress >= 100) {
                progressBar.classList.add('completed');
            } else {
                progressBar.classList.remove('completed');
            }
        }
    };

    /**
     * Initialize on DOM ready
     */
    document.addEventListener('DOMContentLoaded', function() {
        console.log('WorkItem Integration initialized');

        // Restore expanded state
        restoreExpandedState();

        // Initialize all children containers as collapsed by default
        document.querySelectorAll('.work-item-children').forEach(container => {
            if (!container.classList.contains('expanded')) {
                container.classList.add('collapsed');
            }
        });

        // Add HTMX event listeners for better UX
        document.body.addEventListener('htmx:beforeRequest', function(event) {
            // Show loading indicator
            if (event.detail.target.id === 'work-items-tree' ||
                event.detail.target.id === 'work-items-tab-content') {
                const target = document.getElementById(event.detail.target.id);
                if (target) {
                    target.style.opacity = '0.6';
                    target.style.pointerEvents = 'none';
                }
            }
        });

        document.body.addEventListener('htmx:afterRequest', function(event) {
            // Remove loading indicator
            if (event.detail.target.id === 'work-items-tree' ||
                event.detail.target.id === 'work-items-tab-content') {
                const target = document.getElementById(event.detail.target.id);
                if (target) {
                    target.style.opacity = '1';
                    target.style.pointerEvents = 'auto';
                }
            }
        });

        // Handle HTMX errors
        document.body.addEventListener('htmx:responseError', function(event) {
            showToast('An error occurred. Please try again.', 'error');
            console.error('HTMX error:', event.detail);
        });
    });

    // Export functions for testing
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = {
            toggleWorkItemChildren: window.toggleWorkItemChildren,
            openBudgetDistributionModal: window.openBudgetDistributionModal,
            closeBudgetDistributionModal: window.closeBudgetDistributionModal,
            calculateBudgetVariance: calculateBudgetVariance
        };
    }
})();
