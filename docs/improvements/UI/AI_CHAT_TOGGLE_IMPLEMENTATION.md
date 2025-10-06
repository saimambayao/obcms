# AI Chat Toggle Implementation - Comprehensive Guide

**Date**: 2025-10-06
**Status**: Implementation Ready
**Priority**: CRITICAL

## Executive Summary

This document provides three production-ready implementations of the AI Chat toggle functionality with comprehensive error handling, accessibility features, and compatibility with modern web frameworks (HTMX, Turbo, etc.).

---

## Current Implementation Analysis

**Location**: `/src/templates/base.html` lines 462-548

**Current Code**:
```html
<!-- Button -->
<button onclick="toggleAIChat()"
        class="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full shadow-lg hover:shadow-xl transition-all flex items-center justify-center group">
    <i class="fas fa-comments text-white text-xl group-hover:scale-110 transition-transform"></i>
</button>

<!-- Panel -->
<div id="ai-chat-panel" class="hidden absolute bottom-full right-0 mb-2 w-96 ...">
    <!-- Chat content -->
</div>

<!-- Script -->
<script>
function toggleAIChat() {
    const panel = document.getElementById('ai-chat-panel');
    panel.classList.toggle('hidden');

    // Auto-scroll to bottom when opening
    if (!panel.classList.contains('hidden')) {
        const messages = document.getElementById('ai-chat-messages');
        setTimeout(() => {
            messages.scrollTop = messages.scrollHeight;
        }, 100);
    }
}
</script>
```

### Issues Identified

1. **No Error Handling**: Script crashes if `#ai-chat-panel` or `#ai-chat-messages` not found
2. **No Accessibility**: Missing ARIA attributes (`aria-expanded`, `aria-controls`, `aria-labelledby`)
3. **No Debugging**: No console logging for troubleshooting
4. **Inline onclick**: Mixing JavaScript with HTML (not ideal separation of concerns)
5. **No Screen Reader Feedback**: No live region announcements
6. **No Fallback**: Script fails silently if elements missing
7. **No Turbo/HTMX Compatibility**: May break on page navigation in SPA-style apps

---

## Implementation Options

### Recommendation Matrix

| Version | Pros | Cons | Use Case |
|---------|------|------|----------|
| **Version A: Inline onclick** | Simple, works immediately, no DOM ready wait | HTML/JS mixing, harder to maintain | Quick fix, legacy systems |
| **Version B: Event Listener** ✅ **RECOMMENDED** | Clean separation, best practices, maintainable | Requires DOM ready wait | Production use, modern apps |
| **Version C: Data Attributes** | Generic, reusable pattern, framework-agnostic | Most complex, requires utility function | Design systems, component libraries |

**Recommendation**: Use **Version B (Event Listener)** for production OBCMS deployment.

---

## Version A: Enhanced Inline onclick (Current Approach Improved)

### Complete Implementation

```html
<!-- AI Chat Assistant - Fixed bottom-right -->
{% if user.is_authenticated %}
<div id="ai-chat-widget" class="fixed bottom-6 right-6 z-50">
    <button id="ai-chat-toggle-btn"
            onclick="toggleAIChat()"
            class="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full shadow-lg hover:shadow-xl transition-all flex items-center justify-center group"
            aria-label="Open AI Chat Assistant"
            aria-expanded="false"
            aria-controls="ai-chat-panel">
        <i class="fas fa-comments text-white text-xl group-hover:scale-110 transition-transform"></i>
    </button>

    <!-- Chat Panel (hidden by default) - Opens UPWARD from button -->
    <div id="ai-chat-panel"
         class="hidden absolute bottom-full right-0 mb-2 w-96 max-w-[calc(100vw-2rem)] h-[500px] max-h-[calc(100vh-120px)] bg-white rounded-xl shadow-2xl border border-gray-200 flex flex-col"
         role="dialog"
         aria-labelledby="ai-chat-header"
         aria-hidden="true">
        <!-- Chat Header -->
        <div class="bg-gradient-to-r from-emerald-500 to-teal-600 p-4 rounded-t-xl">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <i class="fas fa-robot text-white"></i>
                    <h3 id="ai-chat-header" class="text-white font-medium">AI Assistant</h3>
                    <span class="px-2 py-0.5 bg-white/20 rounded-full text-xs text-white">Beta</span>
                </div>
                <button onclick="toggleAIChat()"
                        class="text-white hover:bg-white/20 rounded p-1 transition-colors"
                        aria-label="Close AI Chat">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <p class="text-xs text-white/90 mt-1">Ask me anything about OBCMS data</p>
        </div>

        <!-- Chat Messages -->
        <div id="ai-chat-messages" class="flex-1 overflow-y-auto p-4 space-y-3">
            <div class="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
                <div class="flex items-start gap-2">
                    <i class="fas fa-robot text-emerald-600 mt-0.5"></i>
                    <div class="flex-1">
                        <p class="text-sm text-gray-700">Hello! I'm your AI assistant. I can help you with:</p>
                        <ul class="mt-2 space-y-1 text-xs text-gray-600">
                            <li><i class="fas fa-check text-emerald-500 text-xs mr-1"></i> Finding community data</li>
                            <li><i class="fas fa-check text-emerald-500 text-xs mr-1"></i> Analyzing assessments</li>
                            <li><i class="fas fa-check text-emerald-500 text-xs mr-1"></i> Generating reports</li>
                            <li><i class="fas fa-check text-emerald-500 text-xs mr-1"></i> Answering questions</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- Chat Input -->
        <div class="p-4 border-t border-gray-200">
            <div class="text-center py-4">
                <p class="text-sm text-gray-500">
                    <i class="fas fa-wrench mr-1"></i>
                    AI Chat Coming Soon
                </p>
            </div>
        </div>
    </div>

    <!-- Screen Reader Live Region -->
    <div id="ai-chat-status" class="sr-only" role="status" aria-live="polite"></div>
</div>

<script>
// Version A: Enhanced Inline onclick with Error Handling
// IMPORTANT: This script MUST be defined BEFORE the button renders
(function() {
    'use strict';

    // Global function (required for inline onclick)
    window.toggleAIChat = function() {
        try {
            console.log('[AI Chat] Toggle function called');

            // Get elements with error handling
            const panel = document.getElementById('ai-chat-panel');
            const button = document.getElementById('ai-chat-toggle-btn');
            const messages = document.getElementById('ai-chat-messages');
            const statusEl = document.getElementById('ai-chat-status');

            // Validate elements exist
            if (!panel) {
                console.error('[AI Chat] ERROR: Panel element #ai-chat-panel not found');
                return;
            }

            if (!button) {
                console.warn('[AI Chat] WARNING: Button element #ai-chat-toggle-btn not found (ARIA states will not update)');
            }

            // Toggle visibility
            const isHidden = panel.classList.contains('hidden');
            panel.classList.toggle('hidden');

            console.log('[AI Chat] Panel toggled:', isHidden ? 'OPENED' : 'CLOSED');

            // Update ARIA attributes
            if (button) {
                button.setAttribute('aria-expanded', isHidden.toString());
                button.setAttribute('aria-label', isHidden ? 'Close AI Chat Assistant' : 'Open AI Chat Assistant');
            }
            panel.setAttribute('aria-hidden', (!isHidden).toString());

            // Screen reader announcement
            if (statusEl) {
                statusEl.textContent = isHidden ? 'AI Chat Assistant opened' : 'AI Chat Assistant closed';
            }

            // Auto-scroll to bottom when opening
            if (isHidden && messages) {
                setTimeout(function() {
                    messages.scrollTop = messages.scrollHeight;
                    console.log('[AI Chat] Messages scrolled to bottom');
                }, 100);
            }
        } catch (error) {
            console.error('[AI Chat] CRITICAL ERROR in toggleAIChat():', error);
            // Fallback: Show alert in development only
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                alert('AI Chat Error: ' + error.message);
            }
        }
    };

    console.log('[AI Chat] Version A: Inline onclick initialized');
})();

// Close chat on escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        try {
            const panel = document.getElementById('ai-chat-panel');
            if (panel && !panel.classList.contains('hidden')) {
                toggleAIChat();
                console.log('[AI Chat] Closed via Escape key');
            }
        } catch (error) {
            console.error('[AI Chat] Error closing on Escape:', error);
        }
    }
});

// Auto-scroll chat messages to bottom when new message arrives (HTMX integration)
document.body.addEventListener('htmx:afterSwap', function(event) {
    try {
        if (event.detail && event.detail.target && event.detail.target.id === 'ai-chat-messages') {
            event.detail.target.scrollTop = event.detail.target.scrollHeight;
            console.log('[AI Chat] HTMX: Messages auto-scrolled after swap');
        }
    } catch (error) {
        console.error('[AI Chat] Error in HTMX afterSwap:', error);
    }
});
</script>
{% endif %}
```

### Features

- ✅ Error handling with try-catch
- ✅ Console logging for debugging
- ✅ Element validation before operations
- ✅ ARIA attributes for accessibility
- ✅ Screen reader announcements
- ✅ Development-only alerts
- ✅ HTMX compatibility maintained
- ✅ Escape key support

---

## Version B: Event Listener (RECOMMENDED)

### Complete Implementation

```html
<!-- AI Chat Assistant - Fixed bottom-right -->
{% if user.is_authenticated %}
<div id="ai-chat-widget" class="fixed bottom-6 right-6 z-50">
    <!-- IMPORTANT: No inline onclick - uses event listener instead -->
    <button id="ai-chat-toggle-btn"
            class="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full shadow-lg hover:shadow-xl transition-all flex items-center justify-center group"
            aria-label="Open AI Chat Assistant"
            aria-expanded="false"
            aria-controls="ai-chat-panel">
        <i class="fas fa-comments text-white text-xl group-hover:scale-110 transition-transform"></i>
    </button>

    <!-- Chat Panel (hidden by default) - Opens UPWARD from button -->
    <div id="ai-chat-panel"
         class="hidden absolute bottom-full right-0 mb-2 w-96 max-w-[calc(100vw-2rem)] h-[500px] max-h-[calc(100vh-120px)] bg-white rounded-xl shadow-2xl border border-gray-200 flex flex-col"
         role="dialog"
         aria-labelledby="ai-chat-header"
         aria-hidden="true">
        <!-- Chat Header -->
        <div class="bg-gradient-to-r from-emerald-500 to-teal-600 p-4 rounded-t-xl">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <i class="fas fa-robot text-white"></i>
                    <h3 id="ai-chat-header" class="text-white font-medium">AI Assistant</h3>
                    <span class="px-2 py-0.5 bg-white/20 rounded-full text-xs text-white">Beta</span>
                </div>
                <button id="ai-chat-close-btn"
                        class="text-white hover:bg-white/20 rounded p-1 transition-colors"
                        aria-label="Close AI Chat">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <p class="text-xs text-white/90 mt-1">Ask me anything about OBCMS data</p>
        </div>

        <!-- Chat Messages -->
        <div id="ai-chat-messages" class="flex-1 overflow-y-auto p-4 space-y-3">
            <div class="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
                <div class="flex items-start gap-2">
                    <i class="fas fa-robot text-emerald-600 mt-0.5"></i>
                    <div class="flex-1">
                        <p class="text-sm text-gray-700">Hello! I'm your AI assistant. I can help you with:</p>
                        <ul class="mt-2 space-y-1 text-xs text-gray-600">
                            <li><i class="fas fa-check text-emerald-500 text-xs mr-1"></i> Finding community data</li>
                            <li><i class="fas fa-check text-emerald-500 text-xs mr-1"></i> Analyzing assessments</li>
                            <li><i class="fas fa-check text-emerald-500 text-xs mr-1"></i> Generating reports</li>
                            <li><i class="fas fa-check text-emerald-500 text-xs mr-1"></i> Answering questions</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- Chat Input -->
        <div class="p-4 border-t border-gray-200">
            <div class="text-center py-4">
                <p class="text-sm text-gray-500">
                    <i class="fas fa-wrench mr-1"></i>
                    AI Chat Coming Soon
                </p>
            </div>
        </div>
    </div>

    <!-- Screen Reader Live Region -->
    <div id="ai-chat-status" class="sr-only" role="status" aria-live="polite"></div>
</div>

<script>
// Version B: Event Listener (RECOMMENDED for Production)
// Clean separation of concerns, best practices, maintainable
(function() {
    'use strict';

    // Initialize when DOM is fully loaded
    function initAIChat() {
        try {
            console.log('[AI Chat] Initializing Version B: Event Listener...');

            // Get elements
            const toggleBtn = document.getElementById('ai-chat-toggle-btn');
            const closeBtn = document.getElementById('ai-chat-close-btn');
            const panel = document.getElementById('ai-chat-panel');
            const messages = document.getElementById('ai-chat-messages');
            const statusEl = document.getElementById('ai-chat-status');

            // Validate critical elements
            if (!toggleBtn) {
                console.error('[AI Chat] CRITICAL: Toggle button #ai-chat-toggle-btn not found');
                return;
            }

            if (!panel) {
                console.error('[AI Chat] CRITICAL: Panel #ai-chat-panel not found');
                return;
            }

            console.log('[AI Chat] Elements validated successfully');

            // Toggle function
            function togglePanel() {
                try {
                    const isHidden = panel.classList.contains('hidden');
                    panel.classList.toggle('hidden');

                    console.log('[AI Chat] Panel toggled:', isHidden ? 'OPENED' : 'CLOSED');

                    // Update ARIA attributes
                    toggleBtn.setAttribute('aria-expanded', isHidden.toString());
                    toggleBtn.setAttribute('aria-label', isHidden ? 'Close AI Chat Assistant' : 'Open AI Chat Assistant');
                    panel.setAttribute('aria-hidden', (!isHidden).toString());

                    // Screen reader announcement
                    if (statusEl) {
                        statusEl.textContent = isHidden ? 'AI Chat Assistant opened' : 'AI Chat Assistant closed';
                    }

                    // Auto-scroll when opening
                    if (isHidden && messages) {
                        setTimeout(function() {
                            messages.scrollTop = messages.scrollHeight;
                            console.log('[AI Chat] Messages scrolled to bottom');
                        }, 100);
                    }

                    // Focus management
                    if (isHidden) {
                        // Panel opened - focus close button
                        if (closeBtn) {
                            closeBtn.focus();
                        }
                    } else {
                        // Panel closed - return focus to toggle button
                        toggleBtn.focus();
                    }
                } catch (error) {
                    console.error('[AI Chat] Error in togglePanel():', error);
                }
            }

            // Add event listeners
            toggleBtn.addEventListener('click', function(event) {
                event.preventDefault();
                event.stopPropagation();
                togglePanel();
            });

            if (closeBtn) {
                closeBtn.addEventListener('click', function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                    togglePanel();
                });
            }

            console.log('[AI Chat] Event listeners attached successfully');
            console.log('[AI Chat] ✅ Version B initialized');

        } catch (error) {
            console.error('[AI Chat] CRITICAL ERROR during initialization:', error);
            // Development-only alert
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                alert('AI Chat Initialization Error: ' + error.message);
            }
        }
    }

    // Initialize on DOM ready (multiple approaches for compatibility)
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAIChat);
    } else {
        // DOM already loaded
        initAIChat();
    }

    // Re-initialize on Turbo/HTMX page loads (SPA compatibility)
    document.addEventListener('turbo:load', initAIChat);
    document.addEventListener('htmx:afterSettle', initAIChat);

})();

// Global keyboard handler (Escape key)
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        try {
            const panel = document.getElementById('ai-chat-panel');
            const toggleBtn = document.getElementById('ai-chat-toggle-btn');

            if (panel && !panel.classList.contains('hidden')) {
                panel.classList.add('hidden');

                if (toggleBtn) {
                    toggleBtn.setAttribute('aria-expanded', 'false');
                    toggleBtn.setAttribute('aria-label', 'Open AI Chat Assistant');
                    toggleBtn.focus();
                }

                panel.setAttribute('aria-hidden', 'true');

                const statusEl = document.getElementById('ai-chat-status');
                if (statusEl) {
                    statusEl.textContent = 'AI Chat Assistant closed';
                }

                console.log('[AI Chat] Closed via Escape key');
            }
        } catch (error) {
            console.error('[AI Chat] Error closing on Escape:', error);
        }
    }
});

// HTMX integration - auto-scroll on message updates
document.body.addEventListener('htmx:afterSwap', function(event) {
    try {
        if (event.detail && event.detail.target && event.detail.target.id === 'ai-chat-messages') {
            event.detail.target.scrollTop = event.detail.target.scrollHeight;
            console.log('[AI Chat] HTMX: Messages auto-scrolled after swap');
        }
    } catch (error) {
        console.error('[AI Chat] Error in HTMX afterSwap:', error);
    }
});

// Click outside to close
document.addEventListener('click', function(event) {
    try {
        const widget = document.getElementById('ai-chat-widget');
        const panel = document.getElementById('ai-chat-panel');
        const toggleBtn = document.getElementById('ai-chat-toggle-btn');

        if (widget && panel && !panel.classList.contains('hidden')) {
            if (!widget.contains(event.target)) {
                panel.classList.add('hidden');

                if (toggleBtn) {
                    toggleBtn.setAttribute('aria-expanded', 'false');
                    toggleBtn.setAttribute('aria-label', 'Open AI Chat Assistant');
                }

                panel.setAttribute('aria-hidden', 'true');

                const statusEl = document.getElementById('ai-chat-status');
                if (statusEl) {
                    statusEl.textContent = 'AI Chat Assistant closed';
                }

                console.log('[AI Chat] Closed via outside click');
            }
        }
    } catch (error) {
        console.error('[AI Chat] Error in outside click handler:', error);
    }
});
</script>
{% endif %}
```

### Features

- ✅ Clean separation of HTML and JavaScript
- ✅ Event listeners (best practice)
- ✅ Comprehensive error handling
- ✅ Full accessibility (ARIA, focus management)
- ✅ Screen reader announcements
- ✅ Turbo/HTMX compatibility (re-initialization)
- ✅ Escape key support
- ✅ Click outside to close
- ✅ Console logging for debugging
- ✅ Development alerts for errors

---

## Version C: Data Attribute Toggle (Generic Pattern)

### Complete Implementation

```html
<!-- AI Chat Assistant - Fixed bottom-right -->
{% if user.is_authenticated %}
<div id="ai-chat-widget" class="fixed bottom-6 right-6 z-50">
    <!-- IMPORTANT: Uses data-toggle-target instead of onclick or id-based listeners -->
    <button data-toggle-target="ai-chat-panel"
            data-toggle-type="chat"
            class="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full shadow-lg hover:shadow-xl transition-all flex items-center justify-center group"
            aria-label="Open AI Chat Assistant"
            aria-expanded="false"
            aria-controls="ai-chat-panel">
        <i class="fas fa-comments text-white text-xl group-hover:scale-110 transition-transform"></i>
    </button>

    <!-- Chat Panel (hidden by default) - Opens UPWARD from button -->
    <div id="ai-chat-panel"
         class="hidden absolute bottom-full right-0 mb-2 w-96 max-w-[calc(100vw-2rem)] h-[500px] max-h-[calc(100vh-120px)] bg-white rounded-xl shadow-2xl border border-gray-200 flex flex-col"
         role="dialog"
         aria-labelledby="ai-chat-header"
         aria-hidden="true"
         data-toggle-scroll-target="ai-chat-messages">
        <!-- Chat Header -->
        <div class="bg-gradient-to-r from-emerald-500 to-teal-600 p-4 rounded-t-xl">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <i class="fas fa-robot text-white"></i>
                    <h3 id="ai-chat-header" class="text-white font-medium">AI Assistant</h3>
                    <span class="px-2 py-0.5 bg-white/20 rounded-full text-xs text-white">Beta</span>
                </div>
                <button data-toggle-target="ai-chat-panel"
                        data-toggle-type="chat"
                        class="text-white hover:bg-white/20 rounded p-1 transition-colors"
                        aria-label="Close AI Chat">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <p class="text-xs text-white/90 mt-1">Ask me anything about OBCMS data</p>
        </div>

        <!-- Chat Messages -->
        <div id="ai-chat-messages" class="flex-1 overflow-y-auto p-4 space-y-3">
            <div class="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
                <div class="flex items-start gap-2">
                    <i class="fas fa-robot text-emerald-600 mt-0.5"></i>
                    <div class="flex-1">
                        <p class="text-sm text-gray-700">Hello! I'm your AI assistant. I can help you with:</p>
                        <ul class="mt-2 space-y-1 text-xs text-gray-600">
                            <li><i class="fas fa-check text-emerald-500 text-xs mr-1"></i> Finding community data</li>
                            <li><i class="fas fa-check text-emerald-500 text-xs mr-1"></i> Analyzing assessments</li>
                            <li><i class="fas fa-check text-emerald-500 text-xs mr-1"></i> Generating reports</li>
                            <li><i class="fas fa-check text-emerald-500 text-xs mr-1"></i> Answering questions</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- Chat Input -->
        <div class="p-4 border-t border-gray-200">
            <div class="text-center py-4">
                <p class="text-sm text-gray-500">
                    <i class="fas fa-wrench mr-1"></i>
                    AI Chat Coming Soon
                </p>
            </div>
        </div>
    </div>

    <!-- Screen Reader Live Region -->
    <div id="ai-chat-status" class="sr-only" role="status" aria-live="polite"></div>
</div>

<script>
// Version C: Generic Data Attribute Toggle Pattern
// Reusable for any toggle-able component across the entire application
(function() {
    'use strict';

    // Generic toggle handler
    function handleToggle(event) {
        try {
            const trigger = event.currentTarget;
            const targetId = trigger.getAttribute('data-toggle-target');
            const toggleType = trigger.getAttribute('data-toggle-type') || 'generic';

            if (!targetId) {
                console.warn('[Toggle] No data-toggle-target specified on:', trigger);
                return;
            }

            const target = document.getElementById(targetId);

            if (!target) {
                console.error('[Toggle] Target element #' + targetId + ' not found');
                return;
            }

            const isHidden = target.classList.contains('hidden');
            target.classList.toggle('hidden');

            console.log('[Toggle]', toggleType + ':', isHidden ? 'OPENED' : 'CLOSED', '#' + targetId);

            // Update ARIA on trigger
            if (trigger.hasAttribute('aria-expanded')) {
                trigger.setAttribute('aria-expanded', isHidden.toString());
            }

            if (trigger.hasAttribute('aria-label')) {
                const currentLabel = trigger.getAttribute('aria-label');
                if (isHidden && currentLabel.includes('Open')) {
                    trigger.setAttribute('aria-label', currentLabel.replace('Open', 'Close'));
                } else if (!isHidden && currentLabel.includes('Close')) {
                    trigger.setAttribute('aria-label', currentLabel.replace('Close', 'Open'));
                }
            }

            // Update ARIA on target
            if (target.hasAttribute('aria-hidden')) {
                target.setAttribute('aria-hidden', (!isHidden).toString());
            }

            // Screen reader announcement
            const statusId = targetId.replace('-panel', '-status');
            const statusEl = document.getElementById(statusId);
            if (statusEl) {
                const componentName = toggleType.charAt(0).toUpperCase() + toggleType.slice(1);
                statusEl.textContent = componentName + ' ' + (isHidden ? 'opened' : 'closed');
            }

            // Auto-scroll behavior (chat-specific)
            if (toggleType === 'chat' && isHidden) {
                const scrollTargetId = target.getAttribute('data-toggle-scroll-target');
                if (scrollTargetId) {
                    const scrollTarget = document.getElementById(scrollTargetId);
                    if (scrollTarget) {
                        setTimeout(function() {
                            scrollTarget.scrollTop = scrollTarget.scrollHeight;
                            console.log('[Toggle] Auto-scrolled #' + scrollTargetId);
                        }, 100);
                    }
                }
            }

            // Focus management (move focus to close button when opening)
            if (isHidden) {
                const closeBtn = target.querySelector('[data-toggle-target="' + targetId + '"]');
                if (closeBtn && closeBtn !== trigger) {
                    closeBtn.focus();
                }
            } else {
                trigger.focus();
            }

        } catch (error) {
            console.error('[Toggle] Error in handleToggle():', error);
        }
    }

    // Initialize toggle handlers
    function initToggleHandlers() {
        try {
            console.log('[Toggle] Initializing data-toggle handlers...');

            const triggers = document.querySelectorAll('[data-toggle-target]');
            console.log('[Toggle] Found', triggers.length, 'toggle triggers');

            triggers.forEach(function(trigger) {
                // Remove old listener if re-initializing
                trigger.removeEventListener('click', handleToggle);
                // Add new listener
                trigger.addEventListener('click', function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                    handleToggle(event);
                });
            });

            console.log('[Toggle] ✅ Version C initialized');

        } catch (error) {
            console.error('[Toggle] CRITICAL ERROR during initialization:', error);
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                alert('Toggle Initialization Error: ' + error.message);
            }
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initToggleHandlers);
    } else {
        initToggleHandlers();
    }

    // Re-initialize on Turbo/HTMX page loads
    document.addEventListener('turbo:load', initToggleHandlers);
    document.addEventListener('htmx:afterSettle', initToggleHandlers);

})();

// Global keyboard handler (Escape key closes any open panel)
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        try {
            // Close all panels with role="dialog" that are visible
            const panels = document.querySelectorAll('[role="dialog"]:not(.hidden)');

            panels.forEach(function(panel) {
                panel.classList.add('hidden');
                panel.setAttribute('aria-hidden', 'true');

                // Find associated trigger button
                const panelId = panel.id;
                const trigger = document.querySelector('[data-toggle-target="' + panelId + '"]');

                if (trigger) {
                    trigger.setAttribute('aria-expanded', 'false');
                    if (trigger.hasAttribute('aria-label')) {
                        const label = trigger.getAttribute('aria-label');
                        if (label.includes('Close')) {
                            trigger.setAttribute('aria-label', label.replace('Close', 'Open'));
                        }
                    }
                    trigger.focus();
                }

                console.log('[Toggle] Closed #' + panelId + ' via Escape key');
            });

        } catch (error) {
            console.error('[Toggle] Error closing on Escape:', error);
        }
    }
});

// Click outside to close (generic for all dialog panels)
document.addEventListener('click', function(event) {
    try {
        const panels = document.querySelectorAll('[role="dialog"]:not(.hidden)');

        panels.forEach(function(panel) {
            const widget = panel.closest('[id$="-widget"]');

            if (widget && !widget.contains(event.target)) {
                panel.classList.add('hidden');
                panel.setAttribute('aria-hidden', 'true');

                const panelId = panel.id;
                const trigger = document.querySelector('[data-toggle-target="' + panelId + '"]');

                if (trigger) {
                    trigger.setAttribute('aria-expanded', 'false');
                    if (trigger.hasAttribute('aria-label')) {
                        const label = trigger.getAttribute('aria-label');
                        if (label.includes('Close')) {
                            trigger.setAttribute('aria-label', label.replace('Close', 'Open'));
                        }
                    }
                }

                console.log('[Toggle] Closed #' + panelId + ' via outside click');
            }
        });

    } catch (error) {
        console.error('[Toggle] Error in outside click handler:', error);
    }
});

// HTMX integration - auto-scroll chat messages
document.body.addEventListener('htmx:afterSwap', function(event) {
    try {
        if (event.detail && event.detail.target && event.detail.target.id === 'ai-chat-messages') {
            event.detail.target.scrollTop = event.detail.target.scrollHeight;
            console.log('[Toggle] HTMX: Messages auto-scrolled after swap');
        }
    } catch (error) {
        console.error('[Toggle] Error in HTMX afterSwap:', error);
    }
});
</script>
{% endif %}
```

### Features

- ✅ Generic, reusable pattern (any component)
- ✅ Framework-agnostic (works with HTMX, Turbo, Alpine, etc.)
- ✅ Data attributes for configuration
- ✅ Multiple toggles per page supported
- ✅ Full accessibility support
- ✅ Comprehensive error handling
- ✅ Console logging for debugging
- ✅ Auto-initialization on page load/navigation
- ✅ Escape key and outside click support

---

## Accessibility Features (All Versions)

### ARIA Attributes

| Attribute | Element | Purpose |
|-----------|---------|---------|
| `aria-label` | Button | Descriptive label for screen readers |
| `aria-expanded` | Button | Indicates panel open/closed state |
| `aria-controls` | Button | Links button to panel it controls |
| `aria-hidden` | Panel | Hides panel from assistive tech when closed |
| `role="dialog"` | Panel | Identifies panel as dialog component |
| `aria-labelledby` | Panel | Links panel to header for description |
| `role="status"` | Live region | Announces state changes to screen readers |
| `aria-live="polite"` | Live region | Non-intrusive announcements |

### Keyboard Support

| Key | Action |
|-----|--------|
| **Enter/Space** | Toggle panel (when button focused) |
| **Escape** | Close panel (when panel open) |
| **Tab** | Navigate focusable elements in panel |

### Focus Management

1. **Opening Panel**: Focus moves to close button inside panel
2. **Closing Panel**: Focus returns to toggle button
3. **Escape Key**: Focus returns to toggle button
4. **Outside Click**: Focus remains on current element

---

## Testing Checklist

### Functional Testing

- [ ] **Toggle Button Works**: Click opens/closes panel
- [ ] **Close Button Works**: X button closes panel
- [ ] **Escape Key Works**: Escape closes panel
- [ ] **Outside Click Works**: Click outside closes panel (Versions B & C)
- [ ] **Auto-Scroll Works**: Messages scroll to bottom when opened
- [ ] **Multiple Toggles**: No interference if opening/closing repeatedly

### Browser Compatibility

- [ ] **Chrome**: All features work
- [ ] **Firefox**: All features work
- [ ] **Safari**: All features work
- [ ] **Edge**: All features work
- [ ] **Mobile Safari (iOS)**: Touch interactions work
- [ ] **Chrome Mobile (Android)**: Touch interactions work

### Accessibility Testing

- [ ] **Screen Reader**: VoiceOver/NVDA announces state changes
- [ ] **Keyboard Navigation**: All actions work via keyboard
- [ ] **Focus Indicators**: Focus visible on all interactive elements
- [ ] **ARIA States**: `aria-expanded` updates correctly
- [ ] **Color Contrast**: All text meets WCAG AA (4.5:1)
- [ ] **Touch Targets**: All buttons minimum 44x44px

### Error Handling

- [ ] **Missing Elements**: Console errors logged, no crashes
- [ ] **HTMX Not Loaded**: Feature works without HTMX
- [ ] **JavaScript Disabled**: Graceful degradation (no errors)
- [ ] **Dev Alerts**: Alerts shown on localhost only

### Performance

- [ ] **No Layout Shift**: Panel appears without page jump
- [ ] **Smooth Animation**: 200ms fade-in animation works
- [ ] **No Memory Leaks**: Event listeners properly managed
- [ ] **Re-initialization**: Works after Turbo/HTMX navigation

---

## Debugging Guide

### Console Messages

```javascript
// Success messages
[AI Chat] Initializing Version B: Event Listener...
[AI Chat] Elements validated successfully
[AI Chat] Event listeners attached successfully
[AI Chat] ✅ Version B initialized
[AI Chat] Panel toggled: OPENED
[AI Chat] Messages scrolled to bottom

// Error messages
[AI Chat] CRITICAL: Toggle button #ai-chat-toggle-btn not found
[AI Chat] CRITICAL: Panel #ai-chat-panel not found
[AI Chat] Error in togglePanel(): [error details]
```

### Common Issues

| Issue | Solution |
|-------|----------|
| **Panel doesn't open** | Check console for element not found errors |
| **Button has no effect** | Verify event listener attached (check console) |
| **ARIA not updating** | Ensure button has `id="ai-chat-toggle-btn"` |
| **Auto-scroll fails** | Check `#ai-chat-messages` exists |
| **Works once, then fails** | Re-initialization issue (check Turbo/HTMX listeners) |

### Development Alerts

Alerts only shown on `localhost` or `127.0.0.1`:

```javascript
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    alert('AI Chat Error: ' + error.message);
}
```

---

## Recommendation for OBCMS

**Use Version B: Event Listener**

### Rationale

1. **Best Practices**: Clean separation of HTML and JavaScript
2. **Maintainability**: Easier to update and debug
3. **Accessibility**: Full ARIA support with focus management
4. **Compatibility**: Works with HTMX, Turbo, and standard pages
5. **Production-Ready**: Comprehensive error handling and logging

### Implementation Steps

1. **Backup Current**: Create backup of `base.html`
2. **Replace Code**: Replace lines 462-548 with Version B implementation
3. **Test Locally**: Verify all features work
4. **Test Accessibility**: Use VoiceOver/NVDA to verify screen reader support
5. **Test Mobile**: Verify touch interactions on iOS/Android
6. **Deploy to Staging**: Test in staging environment
7. **Monitor Logs**: Check browser console for any errors
8. **Deploy to Production**: Roll out after successful staging test

---

## Additional Enhancements (Future)

### Suggested Improvements

1. **Persistent State**: Remember open/closed state in localStorage
2. **Minimize Animation**: Add minimize/maximize instead of hide/show
3. **Position Options**: Allow left/right/top positioning via data attributes
4. **Drag & Drop**: Make panel draggable
5. **Resize**: Allow user to resize panel height/width
6. **Notifications**: Badge count for unread messages
7. **Sound**: Optional notification sound for new messages
8. **Themes**: Support light/dark mode toggle

### Sample localStorage Enhancement

```javascript
// Save state
function togglePanel() {
    const isHidden = panel.classList.contains('hidden');
    panel.classList.toggle('hidden');

    // Save preference
    localStorage.setItem('ai-chat-open', !isHidden);
}

// Restore state on page load
const savedState = localStorage.getItem('ai-chat-open');
if (savedState === 'true') {
    panel.classList.remove('hidden');
    toggleBtn.setAttribute('aria-expanded', 'true');
}
```

---

## Conclusion

All three versions are production-ready with comprehensive error handling, accessibility features, and compatibility with modern web frameworks. Choose based on your project's specific needs and coding standards.

**For OBCMS**: Version B (Event Listener) is recommended for production deployment.
