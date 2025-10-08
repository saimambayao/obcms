/**
 * Budget Distribution Modal - Alpine.js Component
 *
 * Manages three distribution methods:
 * - Equal: Split budget equally across all work items
 * - Weighted: Assign percentage weights (must sum to 100%)
 * - Manual: Manually set amounts (must match total budget)
 *
 * Features:
 * - Real-time validation
 * - Live preview calculations
 * - Currency formatting (₱ Philippine Peso)
 * - Smooth transitions
 * - Keyboard accessibility
 *
 * Usage:
 * Include in template: x-data="budgetDistributor({...})"
 */

function budgetDistributor(config) {
    return {
        // State
        totalBudget: config.totalBudget,
        workItems: config.workItems,
        entryId: config.entryId,
        method: null,
        distribution: {},
        isSubmitting: false,

        /**
         * Initialize distribution data structure
         */
        init() {
            this.workItems.forEach(item => {
                this.distribution[item.id] = {
                    weight: 0,           // Percentage weight (0-100)
                    amount: 0,           // Calculated amount
                    displayAmount: '0.00' // Formatted string for input
                };
            });
        },

        /**
         * Calculate distribution when method changes
         */
        calculateDistribution() {
            if (this.method === 'equal') {
                const equalAmount = this.totalBudget / this.workItems.length;
                this.workItems.forEach(item => {
                    this.distribution[item.id].amount = equalAmount;
                });
            } else if (this.method === 'weighted') {
                // Reset weights when switching
                this.workItems.forEach(item => {
                    this.distribution[item.id].weight = 0;
                    this.distribution[item.id].amount = 0;
                });
            } else if (this.method === 'manual') {
                // Reset amounts when switching
                this.workItems.forEach(item => {
                    this.distribution[item.id].amount = 0;
                    this.distribution[item.id].displayAmount = '0.00';
                });
            }
        },

        /**
         * Calculate amount from percentage weight
         */
        calculateWeightedAmount(itemId) {
            const weight = this.distribution[itemId].weight || 0;
            this.distribution[itemId].amount = (this.totalBudget * weight) / 100;
        },

        /**
         * Handle manual input with validation
         */
        handleManualInput(itemId, value) {
            // Remove non-numeric characters except decimal point
            const cleanValue = value.replace(/[^\d.]/g, '');
            const numericValue = parseFloat(cleanValue) || 0;
            this.distribution[itemId].amount = numericValue;
            this.distribution[itemId].displayAmount = cleanValue;
        },

        /**
         * Format manual input on blur
         */
        formatManualInput(itemId) {
            const amount = this.distribution[itemId].amount;
            this.distribution[itemId].displayAmount = this.formatNumber(amount);
        },

        /**
         * Calculate total weight (percentage)
         */
        totalWeight() {
            return this.workItems.reduce((sum, item) => {
                return sum + (this.distribution[item.id].weight || 0);
            }, 0);
        },

        /**
         * Calculate total allocated amount
         */
        totalAllocated() {
            return this.workItems.reduce((sum, item) => {
                return sum + (this.distribution[item.id].amount || 0);
            }, 0);
        },

        /**
         * Validate weighted distribution (must sum to 100%)
         */
        isWeightValid() {
            if (this.method !== 'weighted') return true;
            const total = this.totalWeight();
            return Math.abs(total - 100) < 0.01; // 0.01% tolerance
        },

        /**
         * Validate manual distribution (must equal total budget)
         */
        isManualValid() {
            if (this.method !== 'manual') return true;
            const variance = Math.abs(this.totalBudget - this.totalAllocated());
            return variance < 0.01; // ₱0.01 tolerance
        },

        /**
         * Overall validation check
         */
        isValid() {
            if (!this.method) return false;
            if (this.method === 'equal') return true;
            if (this.method === 'weighted') return this.isWeightValid();
            if (this.method === 'manual') return this.isManualValid();
            return false;
        },

        /**
         * Prepare distribution data for API submission
         */
        getDistributionData() {
            const data = {};
            this.workItems.forEach(item => {
                data[item.id] = this.distribution[item.id].amount;
            });
            return data;
        },

        /**
         * Format currency (₱ Philippine Peso)
         */
        formatCurrency(amount) {
            return '₱' + this.formatNumber(amount);
        },

        /**
         * Format number with thousands separator
         */
        formatNumber(num) {
            return new Intl.NumberFormat('en-PH', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(num || 0);
        },

        /**
         * Get badge color class for work type
         */
        getWorkTypeBadgeClass(workType) {
            const classes = {
                'staff_task': 'bg-blue-100 text-blue-800',
                'event': 'bg-purple-100 text-purple-800',
                'project_workflow': 'bg-emerald-100 text-emerald-800'
            };
            return classes[workType] || 'bg-gray-100 text-gray-800';
        },

        /**
         * Submit distribution to backend API
         */
        async submitDistribution() {
            if (!this.isValid() || this.isSubmitting) return;

            this.isSubmitting = true;

            try {
                const response = await fetch(`/monitoring/entries/${this.entryId}/distribute-budget/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken(),
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        method: this.method,
                        distribution: this.getDistributionData()
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Trigger custom event for parent page
                    window.dispatchEvent(new CustomEvent('budget-distributed', {
                        detail: data
                    }));

                    // Show success notification
                    this.showToast('Budget distributed successfully', 'success');

                    // Close modal
                    this.$el.dispatchEvent(new CustomEvent('close-modal'));

                    // Refresh stats using HTMX (if available)
                    if (window.htmx) {
                        window.htmx.trigger(document.body, 'refresh-stats');
                    }
                } else {
                    // Show error notification
                    this.showToast(data.error || 'Failed to distribute budget', 'error');
                }
            } catch (error) {
                console.error('Distribution error:', error);
                this.showToast('Network error. Please try again.', 'error');
            } finally {
                this.isSubmitting = false;
            }
        },

        /**
         * Get CSRF token from page
         */
        getCsrfToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]').value;
        },

        /**
         * Dispatch toast notification event
         */
        showToast(message, type) {
            window.dispatchEvent(new CustomEvent('show-toast', {
                detail: { message, type }
            }));
        }
    };
}

// Export for testing/module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { budgetDistributor };
}
