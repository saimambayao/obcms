/**
 * Query Builder Alpine.js Component
 * HTMX-powered step-by-step query builder for OBCMS Chat
 */

function queryBuilder() {
    return {
        // State
        open: false,
        step: 1,
        queryType: 'count',
        entityType: '',
        filters: {},
        selectedAggregate: '',
        previewText: '',
        availableEntities: [],
        filterConfig: {},
        aggregates: {},
        executing: false,

        // Initialize
        async init() {
            // Load available entities
            await this.loadAvailableEntities();

            // Listen for query builder open event
            window.addEventListener('open-query-builder', () => {
                this.open = true;
                this.reset();
            });

            // Listen for HTMX events
            document.addEventListener('htmx:afterSwap', (event) => {
                if (event.detail.target.id === 'filter-container') {
                    this.bindFilterInputs();
                }
            });
        },

        // Reset builder state
        reset() {
            this.step = 1;
            this.queryType = 'count';
            this.entityType = '';
            this.filters = {};
            this.selectedAggregate = '';
            this.previewText = '';
            this.filterConfig = {};
            this.aggregates = {};
            this.executing = false;
        },

        // Close builder
        close() {
            this.open = false;
        },

        // Navigation
        async nextStep() {
            if (!this.canProceed()) return;

            this.step++;

            // Load filters when entering step 3
            if (this.step === 3) {
                await this.loadFilters();
            }

            // Load preview when entering step 4
            if (this.step === 4) {
                await this.updatePreview();
            }
        },

        prevStep() {
            if (this.step > 1) {
                this.step--;
            }
        },

        canProceed() {
            switch (this.step) {
                case 1:
                    return this.queryType !== '';
                case 2:
                    return this.entityType !== '';
                case 3:
                    // For aggregate queries, must select an aggregate
                    if (this.queryType === 'aggregate') {
                        return this.selectedAggregate !== '';
                    }
                    return true;
                case 4:
                    return true;
                default:
                    return false;
            }
        },

        // Step 1: Select query type
        selectQueryType(type) {
            this.queryType = type;
            // Auto-advance to next step
            setTimeout(() => this.nextStep(), 300);
        },

        // Step 2: Select entity type
        async selectEntityType(type) {
            this.entityType = type;
            // Load config for this entity
            await this.loadEntityConfig(type);
            // Auto-advance to next step
            setTimeout(() => this.nextStep(), 300);
        },

        // Load available entities
        async loadAvailableEntities() {
            try {
                const response = await fetch('/api/query-builder/entities/', {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    this.availableEntities = data.entities;
                }
            } catch (error) {
                console.error('Failed to load entities:', error);
            }
        },

        // Load entity configuration
        async loadEntityConfig(entityType) {
            try {
                const response = await fetch(`/api/query-builder/config/${entityType}/`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    this.filterConfig = data.filters || {};
                    this.aggregates = data.aggregates || {};
                }
            } catch (error) {
                console.error('Failed to load entity config:', error);
            }
        },

        // Load filters HTML via HTMX
        async loadFilters() {
            const container = document.getElementById('filter-container');
            if (!container) return;

            // Show loading state
            container.innerHTML = `
                <div class="flex items-center justify-center py-8">
                    <div class="text-center">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mx-auto mb-2"></div>
                        <p class="text-sm text-gray-600">Loading filters...</p>
                    </div>
                </div>
            `;

            try {
                const response = await fetch(`/api/query-builder/filters/?entity=${this.entityType}`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                });

                if (response.ok) {
                    const html = await response.text();
                    container.innerHTML = html;
                    this.bindFilterInputs();
                }
            } catch (error) {
                console.error('Failed to load filters:', error);
                container.innerHTML = `
                    <div class="text-center py-4">
                        <p class="text-red-600">Failed to load filters</p>
                    </div>
                `;
            }
        },

        // Bind filter input changes
        bindFilterInputs() {
            const container = document.getElementById('filter-container');
            if (!container) return;

            const inputs = container.querySelectorAll('select, input');
            inputs.forEach(input => {
                input.addEventListener('change', (e) => {
                    const name = e.target.name;
                    const value = e.target.value;
                    this.filters[name] = value;
                });
            });
        },

        // Update preview
        async updatePreview() {
            const previewContainer = document.getElementById('preview-results');
            if (!previewContainer) return;

            // Build selections object
            const selections = {
                entity_type: this.entityType,
                query_type: this.queryType,
                filters: this.filters,
            };

            if (this.queryType === 'aggregate') {
                selections.aggregate = this.selectedAggregate;
            }

            try {
                const response = await fetch('/api/query-builder/preview/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken(),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify(selections),
                });

                if (response.ok) {
                    const data = await response.json();
                    this.previewText = data.query_text;

                    // Update preview results
                    previewContainer.innerHTML = `
                        <div class="space-y-4">
                            <div class="flex items-center justify-between">
                                <span class="text-sm font-medium text-gray-700">Result Type:</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                                    ${this.formatResultType(data.result_type)}
                                </span>
                            </div>
                            <div class="flex items-center justify-between">
                                <span class="text-sm font-medium text-gray-700">Estimated Count:</span>
                                <span class="text-2xl font-bold text-emerald-600">
                                    ${data.estimated_count.toLocaleString()}
                                </span>
                            </div>
                            ${this.queryType === 'aggregate' ? `
                                <div class="pt-4 border-t">
                                    <p class="text-sm text-gray-600">
                                        <i class="fas fa-info-circle mr-2"></i>
                                        This will calculate: <strong>${data.aggregate_label || this.selectedAggregate}</strong>
                                    </p>
                                </div>
                            ` : ''}
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Failed to load preview:', error);
                previewContainer.innerHTML = `
                    <div class="text-center py-4">
                        <p class="text-red-600">Failed to load preview</p>
                    </div>
                `;
            }
        },

        // Execute query
        async executeQuery() {
            if (this.executing) return;

            this.executing = true;

            // Build selections object
            const selections = {
                entity_type: this.entityType,
                query_type: this.queryType,
                filters: this.filters,
            };

            if (this.queryType === 'aggregate') {
                selections.aggregate = this.selectedAggregate;
            }

            try {
                const response = await fetch('/api/query-builder/execute/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken(),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify(selections),
                });

                if (response.ok) {
                    const data = await response.json();

                    if (data.success) {
                        // Inject results into chat
                        this.injectResultsIntoChat(data);

                        // Close builder
                        this.close();

                        // Show success toast
                        this.showToast('Query executed successfully!', 'success');
                    } else {
                        this.showToast(data.error || 'Query execution failed', 'error');
                    }
                } else {
                    this.showToast('Failed to execute query', 'error');
                }
            } catch (error) {
                console.error('Failed to execute query:', error);
                this.showToast('Failed to execute query', 'error');
            } finally {
                this.executing = false;
            }
        },

        // Inject results into chat
        injectResultsIntoChat(data) {
            // Get chat container
            const chatContainer = document.getElementById('chat-messages');
            if (!chatContainer) return;

            // Create message element
            const messageEl = document.createElement('div');
            messageEl.className = 'message assistant-message';

            let resultHtml = '';

            if (data.query_type === 'count') {
                resultHtml = `
                    <div class="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl p-6 border-2 border-emerald-200">
                        <div class="flex items-center space-x-4">
                            <div class="w-16 h-16 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-full flex items-center justify-center">
                                <i class="fas fa-calculator text-white text-2xl"></i>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600 mb-1">${data.query_text}</p>
                                <p class="text-4xl font-bold text-emerald-600">${data.data.toLocaleString()}</p>
                            </div>
                        </div>
                    </div>
                `;
            } else if (data.query_type === 'aggregate') {
                resultHtml = `
                    <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-200">
                        <div class="flex items-center space-x-4">
                            <div class="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full flex items-center justify-center">
                                <i class="fas fa-chart-bar text-white text-2xl"></i>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600 mb-1">${data.query_text}</p>
                                <p class="text-4xl font-bold text-blue-600">${this.formatNumber(data.data)}</p>
                            </div>
                        </div>
                    </div>
                `;
            } else if (data.query_type === 'list') {
                // For list queries, show a table or cards
                resultHtml = `
                    <div class="space-y-4">
                        <p class="font-medium text-gray-900">${data.query_text}</p>
                        <div class="bg-white rounded-xl border border-gray-200 p-4">
                            <p class="text-sm text-gray-600 mb-2">Found ${data.count} items</p>
                            <div class="text-sm text-gray-500">
                                (Results displayed in table format)
                            </div>
                        </div>
                    </div>
                `;
            }

            messageEl.innerHTML = resultHtml;
            chatContainer.appendChild(messageEl);

            // Scroll to bottom
            chatContainer.scrollTop = chatContainer.scrollHeight;
        },

        // Utility functions
        formatResultType(type) {
            const types = {
                count: 'Count',
                list: 'List',
                aggregate: 'Aggregate',
            };
            return types[type] || type;
        },

        formatNumber(num) {
            if (num === null || num === undefined) return 'N/A';
            return Number(num).toLocaleString(undefined, {
                maximumFractionDigits: 2,
            });
        },

        getCsrfToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        },

        showToast(message, type = 'info') {
            // Dispatch toast event
            window.dispatchEvent(new CustomEvent('show-toast', {
                detail: { message, type },
            }));
        },
    };
}

// Initialize query builder globally
document.addEventListener('DOMContentLoaded', () => {
    // Add global function to open query builder
    window.openQueryBuilder = () => {
        window.dispatchEvent(new CustomEvent('open-query-builder'));
    };
});
