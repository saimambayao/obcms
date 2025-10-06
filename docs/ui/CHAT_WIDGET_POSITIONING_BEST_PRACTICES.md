# Chat Widget Positioning Best Practices

**Date:** 2025-10-06
**Status:** Research Complete
**Purpose:** Document best practices for chat widget positioning to ensure visibility and accessibility

---

## Executive Summary

This document provides comprehensive research on chat widget positioning patterns, based on industry standards from Intercom, Zendesk, Drift, and accessibility guidelines. The research covers positioning strategies, viewport constraints, mobile patterns, z-index management, and accessibility requirements.

**Key Findings:**
- **Use `position: fixed`** for chat widgets (not absolute)
- **Bottom-right corner** is industry standard (aligns with reading patterns)
- **Mobile requires different approach** (bottom sheets or fullscreen)
- **z-index range:** 1000-9999 depending on context
- **WCAG 2.2 AA compliance** required for accessibility

---

## 1. Fixed vs Absolute Positioning

### Recommendation: Use `position: fixed`

**Fixed Positioning:**
- Positioned relative to the **viewport/browser window**
- Stays visible when user scrolls
- Industry standard for chat widgets
- Ensures constant visibility "above the fold"

**Absolute Positioning:**
- Positioned relative to closest positioned ancestor
- Scrolls with page content
- **NOT recommended** for chat widgets
- Only use for in-content elements

### Implementation Pattern

```css
/* ✅ CORRECT: Fixed positioning for chat widgets */
.chat-widget {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
}

/* ❌ WRONG: Absolute positioning */
.chat-widget {
    position: absolute; /* Will scroll away from view */
    bottom: 20px;
    right: 20px;
}
```

---

## 2. Bottom-Right Corner Placement

### Why Bottom-Right?

**User Experience Research:**
- Aligns with natural reading patterns (left-to-right languages)
- Users end page scan in bottom-right area
- Area typically devoid of content
- Minimizes disruption to browsing experience
- Decades of design conventions condition users to look here

**Industry Standard:**
- Intercom: Default bottom-right
- Zendesk: Bottom-right preferred
- Drift: Bottom-right standard
- HubSpot: Bottom-right default

### Alternative: Bottom-Left

Use bottom-left only when:
- Right side has persistent elements (e.g., "Back to Top" button)
- Regional reading patterns (right-to-left languages)
- Specific brand requirements

**Implementation:**

```css
/* Bottom-right (standard) */
.chat-widget {
    position: fixed;
    bottom: 20px;
    right: 20px;
}

/* Bottom-left (alternative) */
.chat-widget {
    position: fixed;
    bottom: 20px;
    left: 20px;
}
```

---

## 3. Viewport-Aware Positioning

### The Mobile 100vh Problem

**Issue:** On mobile browsers, `100vh` includes browser UI (address bar), causing content to be pushed off-screen.

**Solutions:**

#### A. Modern CSS: Dynamic Viewport Units (Preferred)

```css
/* ✅ BEST: Dynamic viewport height (2023+ browsers) */
.chat-panel {
    max-height: calc(100dvh - 100px); /* dvh = dynamic viewport height */
    overflow-y: auto;
}

/* Alternative: Small viewport height */
.chat-panel {
    max-height: calc(100svh - 100px); /* svh excludes browser UI */
}
```

#### B. JavaScript Custom Property (Broader Support)

```javascript
// Set custom --vh property
function setVhProperty() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
}

// Call on load and resize
window.addEventListener('resize', setVhProperty);
setVhProperty();
```

```css
/* Use custom property */
.chat-panel {
    max-height: calc(var(--vh, 1vh) * 100 - 100px);
}
```

#### C. Webkit Fill Available (iOS Fallback)

```css
.chat-panel {
    min-height: -webkit-fill-available;
    max-height: -webkit-fill-available;
}
```

### Recommended Approach

```css
.chat-panel {
    /* Fallback for older browsers */
    max-height: calc(100vh - 100px);

    /* Modern browsers with dynamic viewport */
    max-height: calc(100dvh - 100px);

    /* Constrain with min() for safety */
    max-height: min(600px, calc(100dvh - 100px));

    overflow-y: auto;
    overflow-x: hidden;
}
```

### Preventing Off-Screen Issues

```css
/* Ensure panel never exceeds viewport */
.chat-panel {
    position: fixed;
    bottom: 80px; /* Above chat button */
    right: 20px;

    /* Constrain dimensions */
    max-width: min(400px, calc(100vw - 40px));
    max-height: min(600px, calc(100dvh - 120px));

    /* Handle overflow */
    overflow-y: auto;
    overflow-x: hidden;
}
```

---

## 4. Z-Index Best Practices

### Standard Z-Index Scale

Based on Bootstrap and Material UI frameworks:

```css
/* Component z-index hierarchy */
.dropdown { z-index: 1000; }
.sticky-header { z-index: 1020; }
.fixed-navbar { z-index: 1030; }
.modal-backdrop { z-index: 1040; }
.modal { z-index: 1050; }
.popover { z-index: 1060; }
.tooltip { z-index: 1070; }

/* Chat widget placement */
.chat-button { z-index: 1080; }     /* Above tooltips */
.chat-panel { z-index: 1090; }      /* Above chat button */
.chat-modal { z-index: 1100; }      /* Above everything */
```

### Why High Values (9999)?

**Use Cases:**
- Fail-safe to ensure visibility over all elements
- Third-party integrations with unknown z-indexes
- Legacy codebases with inconsistent stacking

**Caution:**
- Creates z-index inflation
- Harder to maintain
- Can conflict with other "fail-safe" components

**Recommended Approach:**

```css
/* ✅ GOOD: Structured z-index scale */
:root {
    --z-dropdown: 1000;
    --z-sticky: 1020;
    --z-fixed: 1030;
    --z-modal-backdrop: 1040;
    --z-modal: 1050;
    --z-chat-button: 1080;
    --z-chat-panel: 1090;
}

.chat-button { z-index: var(--z-chat-button); }
.chat-panel { z-index: var(--z-chat-panel); }

/* ❌ AVOID: Arbitrary high values */
.chat-button { z-index: 9999; }
.chat-panel { z-index: 99999; }
```

### Resolving Z-Index Conflicts

**Common Issues:**

1. **Stacking Context Limitations**
   - Parent element creates new stacking context
   - Child z-index only applies within parent context

   ```css
   /* ❌ Problem: z-index doesn't work */
   .parent {
       position: relative; /* Creates stacking context */
       z-index: 1;
   }
   .child {
       position: absolute;
       z-index: 9999; /* Only applies within parent context */
   }

   /* ✅ Solution: Place at document root */
   body > .chat-widget {
       position: fixed;
       z-index: 1080;
   }
   ```

2. **Modal Conflicts**
   - Chat widget obscures modals
   - Solution: Ensure modals have higher z-index OR hide chat when modal opens

   ```javascript
   // Hide chat when modal opens
   document.addEventListener('modal-open', () => {
       document.querySelector('.chat-widget').style.display = 'none';
   });

   document.addEventListener('modal-close', () => {
       document.querySelector('.chat-widget').style.display = 'block';
   });
   ```

### Vendor-Specific Z-Index

**Intercom:**
```javascript
window.intercomSettings = {
    app_id: 'abc123',
    z_index: 1080 // Custom z-index
};
```

**Zendesk:**
```javascript
zE('webWidget', 'updateSettings', {
    webWidget: {
        zIndex: 1080
    }
});
```

---

## 5. Mobile Considerations

### Bottom Sheet Pattern (Recommended for Mobile)

**What is a Bottom Sheet?**
- UI pattern anchored to bottom of screen
- Slides up from bottom edge
- Can be modal (dimmed background) or non-modal
- Supports partial/full expansion

**Types:**

1. **Standard Bottom Sheet** (Non-modal)
   - Persistent, collapsible
   - Allows interaction with background
   - Good for contextual info

2. **Modal Bottom Sheet**
   - Blocks interaction with background
   - Full-width in portrait/landscape
   - Requires dismissal to continue

**Implementation:**

```css
/* Mobile: Bottom sheet pattern */
@media (max-width: 768px) {
    .chat-panel {
        /* Reset desktop positioning */
        right: 0;
        bottom: 0;
        left: 0;

        /* Full width */
        width: 100%;
        max-width: 100%;

        /* Partial height initially */
        height: 60vh;
        max-height: none;

        /* Rounded top corners */
        border-radius: 16px 16px 0 0;

        /* Shadow for elevation */
        box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.15);
    }

    /* Expanded state */
    .chat-panel.expanded {
        height: 100vh;
        border-radius: 0;
    }
}
```

### Fullscreen Mobile Chat

```css
/* Small viewports: Fullscreen chat */
@media (max-height: 600px), (max-width: 480px) {
    .chat-panel {
        position: fixed;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 100%;
        max-width: none;
        max-height: none;
        border-radius: 0;
    }

    /* Hide chat button when panel open */
    .chat-panel.open ~ .chat-button {
        display: none;
    }
}
```

### Touch-Friendly Positioning

```css
.chat-button {
    /* Minimum touch target: 48x48px (WCAG 2.5.5) */
    min-width: 48px;
    min-height: 48px;

    /* Adequate spacing from edges */
    bottom: 20px;
    right: 20px;

    /* Prevent accidental touches */
    padding: 12px;
}

/* Tablet adjustments */
@media (min-width: 768px) and (max-width: 1024px) {
    .chat-panel {
        max-width: 400px;
        right: 20px;
        bottom: 80px;
    }
}
```

### Progressive Enhancement Strategy

```css
/* Base: Mobile-first (bottom sheet) */
.chat-panel {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: 60vh;
    border-radius: 16px 16px 0 0;
}

/* Tablet: Positioned panel */
@media (min-width: 768px) {
    .chat-panel {
        width: 360px;
        height: auto;
        max-height: 500px;
        right: 20px;
        left: auto;
        border-radius: 12px;
    }
}

/* Desktop: Larger panel */
@media (min-width: 1024px) {
    .chat-panel {
        width: 400px;
        max-height: 600px;
    }
}
```

---

## 6. Accessibility Requirements

### WCAG 2.2 AA Compliance

**Critical Requirements:**

1. **Keyboard Navigation** (WCAG 2.1.1)
   - All interactive elements accessible via keyboard
   - Logical tab order
   - Visible focus indicators

2. **Color Contrast** (WCAG 1.4.3)
   - Minimum 4.5:1 for normal text
   - Minimum 3:1 for large text (18pt+)

3. **Touch Targets** (WCAG 2.5.5)
   - Minimum 44x44px (preferably 48x48px)

4. **Screen Reader Support** (WCAG 4.1.2)
   - Proper ARIA labels
   - Semantic HTML
   - Live regions for messages

### Keyboard Navigation Implementation

```html
<!-- Chat button with keyboard support -->
<button
    class="chat-button"
    aria-label="Open chat widget"
    aria-expanded="false"
    aria-controls="chat-panel"
>
    <i class="fas fa-comments" aria-hidden="true"></i>
    <span class="sr-only">Chat with us</span>
</button>

<!-- Chat panel with proper ARIA -->
<div
    id="chat-panel"
    class="chat-panel"
    role="dialog"
    aria-labelledby="chat-title"
    aria-modal="true"
    hidden
>
    <div class="chat-header">
        <h2 id="chat-title">Chat Support</h2>
        <button
            class="close-button"
            aria-label="Close chat"
            type="button"
        >
            <i class="fas fa-times" aria-hidden="true"></i>
        </button>
    </div>

    <!-- Messages container with live region -->
    <div
        class="chat-messages"
        role="log"
        aria-live="polite"
        aria-atomic="false"
    >
        <!-- Messages appear here -->
    </div>

    <form class="chat-input" role="form">
        <label for="message-input" class="sr-only">Type your message</label>
        <input
            id="message-input"
            type="text"
            placeholder="Type a message..."
            aria-required="true"
        />
        <button type="submit" aria-label="Send message">
            <i class="fas fa-paper-plane" aria-hidden="true"></i>
        </button>
    </form>
</div>
```

### CSS for Accessibility

```css
/* Visible focus indicators */
.chat-button:focus,
.chat-panel button:focus,
.chat-panel input:focus {
    outline: 2px solid #0066CC;
    outline-offset: 2px;
}

/* High contrast focus (Windows High Contrast Mode) */
@media (prefers-contrast: high) {
    .chat-button:focus,
    .chat-panel button:focus {
        outline: 3px solid currentColor;
    }
}

/* Screen reader only text */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}

/* Minimum touch targets */
.chat-button,
.chat-panel button {
    min-width: 48px;
    min-height: 48px;
    padding: 12px;
}

/* Ensure sufficient color contrast */
.chat-button {
    background-color: #0066CC; /* Blue */
    color: #FFFFFF; /* White */
    /* Contrast ratio: 7.9:1 (exceeds 4.5:1 minimum) */
}
```

### JavaScript for Accessibility

```javascript
// Focus management
function openChat() {
    const panel = document.getElementById('chat-panel');
    const firstFocusable = panel.querySelector('button, input');

    // Show panel
    panel.removeAttribute('hidden');

    // Update ARIA
    document.querySelector('.chat-button').setAttribute('aria-expanded', 'true');

    // Trap focus within panel
    trapFocus(panel);

    // Move focus to first element
    firstFocusable?.focus();
}

function closeChat() {
    const panel = document.getElementById('chat-panel');
    const button = document.querySelector('.chat-button');

    // Hide panel
    panel.setAttribute('hidden', '');

    // Update ARIA
    button.setAttribute('aria-expanded', 'false');

    // Return focus to button
    button.focus();
}

// Trap focus within panel (prevent tabbing to background)
function trapFocus(element) {
    const focusableElements = element.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];

    element.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            if (e.shiftKey) {
                if (document.activeElement === firstFocusable) {
                    lastFocusable.focus();
                    e.preventDefault();
                }
            } else {
                if (document.activeElement === lastFocusable) {
                    firstFocusable.focus();
                    e.preventDefault();
                }
            }
        }

        // Close on Escape
        if (e.key === 'Escape') {
            closeChat();
        }
    });
}
```

### Preventing Content Blockage

```css
/* Ensure panel doesn't block important content */
.chat-panel {
    /* Position with safe margins */
    bottom: 80px; /* Above chat button */
    right: 20px;

    /* Add backdrop for modal behavior */
    &::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: -1;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s;
    }

    &[aria-modal="true"]::before {
        opacity: 1;
        pointer-events: auto;
    }
}

/* Responsive padding to prevent content overlap */
@media (max-width: 768px) {
    body.chat-open {
        padding-bottom: 60vh; /* Match chat panel height */
    }
}
```

---

## 7. Complete Implementation Examples

### Example 1: Standard Chat Widget (Desktop)

```html
<div class="chat-widget">
    <button class="chat-button" aria-label="Open chat" aria-expanded="false">
        <i class="fas fa-comments"></i>
    </button>

    <div class="chat-panel" hidden>
        <div class="chat-header">
            <h2>Chat Support</h2>
            <button class="close-btn" aria-label="Close chat">×</button>
        </div>

        <div class="chat-messages" role="log" aria-live="polite">
            <!-- Messages -->
        </div>

        <form class="chat-input">
            <input type="text" placeholder="Type a message..." aria-label="Message" />
            <button type="submit" aria-label="Send">
                <i class="fas fa-paper-plane"></i>
            </button>
        </form>
    </div>
</div>
```

```css
/* Chat button */
.chat-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    cursor: pointer;
    z-index: 1080;
    transition: transform 0.2s, box-shadow 0.2s;
}

.chat-button:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.chat-button:focus {
    outline: 2px solid #0066CC;
    outline-offset: 2px;
}

/* Chat panel */
.chat-panel {
    position: fixed;
    bottom: 90px;
    right: 20px;
    width: 380px;
    max-height: min(600px, calc(100dvh - 120px));
    background: white;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    z-index: 1090;
    overflow: hidden;
}

.chat-panel[hidden] {
    display: none;
}

/* Chat header */
.chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.chat-header h2 {
    font-size: 18px;
    font-weight: 600;
    margin: 0;
}

.close-btn {
    background: none;
    border: none;
    color: white;
    font-size: 24px;
    cursor: pointer;
    padding: 4px 8px;
    line-height: 1;
    min-width: 32px;
    min-height: 32px;
}

/* Messages area */
.chat-messages {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 20px;
    background: #f5f5f5;
}

/* Input area */
.chat-input {
    display: flex;
    gap: 8px;
    padding: 16px;
    background: white;
    border-top: 1px solid #e0e0e0;
}

.chat-input input {
    flex: 1;
    padding: 12px 16px;
    border: 1px solid #e0e0e0;
    border-radius: 24px;
    font-size: 14px;
    outline: none;
}

.chat-input input:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.chat-input button {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    cursor: pointer;
    transition: transform 0.2s;
}

.chat-input button:hover {
    transform: scale(1.05);
}
```

### Example 2: Mobile-Responsive Bottom Sheet

```css
/* Base styles (mobile-first) */
.chat-panel {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: 60vh;
    background: white;
    border-radius: 16px 16px 0 0;
    box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    z-index: 1090;
    transform: translateY(100%);
    transition: transform 0.3s ease-out;
}

.chat-panel.open {
    transform: translateY(0);
}

/* Drag handle for bottom sheet */
.chat-panel::before {
    content: '';
    position: absolute;
    top: 8px;
    left: 50%;
    transform: translateX(-50%);
    width: 40px;
    height: 4px;
    background: #ccc;
    border-radius: 2px;
}

/* Expanded state */
.chat-panel.expanded {
    height: 100vh;
    border-radius: 0;
}

/* Tablet: Positioned panel */
@media (min-width: 768px) {
    .chat-panel {
        bottom: 90px;
        right: 20px;
        left: auto;
        width: 380px;
        height: auto;
        max-height: min(600px, calc(100dvh - 120px));
        border-radius: 12px;
        transform: scale(0.8) translateY(20px);
        opacity: 0;
    }

    .chat-panel.open {
        transform: scale(1) translateY(0);
        opacity: 1;
    }

    .chat-panel::before {
        display: none; /* Hide drag handle on desktop */
    }
}

/* Desktop: Larger panel */
@media (min-width: 1024px) {
    .chat-panel {
        width: 420px;
        max-height: min(680px, calc(100dvh - 120px));
    }
}

/* Small height viewports: Fullscreen */
@media (max-height: 600px) {
    .chat-panel {
        height: 100vh;
        border-radius: 0;
    }
}
```

### Example 3: Advanced Features

```javascript
class ChatWidget {
    constructor() {
        this.button = document.querySelector('.chat-button');
        this.panel = document.querySelector('.chat-panel');
        this.closeBtn = document.querySelector('.close-btn');
        this.messagesContainer = document.querySelector('.chat-messages');
        this.isOpen = false;

        this.init();
    }

    init() {
        // Event listeners
        this.button.addEventListener('click', () => this.toggle());
        this.closeBtn.addEventListener('click', () => this.close());

        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });

        // Auto-scroll to bottom on new message
        this.observeMessages();

        // Set viewport height custom property
        this.updateVh();
        window.addEventListener('resize', () => this.updateVh());
    }

    toggle() {
        this.isOpen ? this.close() : this.open();
    }

    open() {
        this.panel.removeAttribute('hidden');
        this.panel.classList.add('open');
        this.button.setAttribute('aria-expanded', 'true');
        this.isOpen = true;

        // Focus first input
        const input = this.panel.querySelector('input');
        setTimeout(() => input?.focus(), 300);

        // Announce to screen readers
        this.announce('Chat panel opened');
    }

    close() {
        this.panel.classList.remove('open');
        this.button.setAttribute('aria-expanded', 'false');

        // Wait for animation before hiding
        setTimeout(() => {
            this.panel.setAttribute('hidden', '');
            this.isOpen = false;
        }, 300);

        // Return focus to button
        this.button.focus();

        // Announce to screen readers
        this.announce('Chat panel closed');
    }

    observeMessages() {
        const observer = new MutationObserver(() => {
            this.scrollToBottom();
        });

        observer.observe(this.messagesContainer, {
            childList: true,
            subtree: true
        });
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    updateVh() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    announce(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        document.body.appendChild(announcement);
        setTimeout(() => announcement.remove(), 1000);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    new ChatWidget();
});
```

---

## 8. Key Recommendations Summary

### Positioning
- **Use `position: fixed`** for chat widgets
- **Bottom-right corner** as default (20px from edges)
- **Adjust for mobile** using bottom sheet pattern

### Viewport Constraints
- **Use `calc(100dvh - offset)`** for height calculations
- **Fallback to JavaScript** for older browsers
- **Constrain with `min()`** to prevent overflow

### Z-Index
- **Use structured scale** (1000-1100 range)
- **Chat button: 1080**, **Chat panel: 1090**
- **Avoid arbitrary high values** unless necessary

### Mobile
- **Bottom sheet pattern** for tablets/phones
- **Fullscreen on small viewports** (< 600px height)
- **Touch targets: 48x48px minimum**

### Accessibility
- **WCAG 2.2 AA compliance** required
- **Keyboard navigation** with visible focus
- **Screen reader support** with ARIA
- **Color contrast: 4.5:1 minimum**

### Performance
- **CSS transitions** for smooth animations
- **Auto-scroll to bottom** on new messages
- **Viewport height updates** on resize

---

## 9. Testing Checklist

### Desktop Testing
- [ ] Widget visible on all screen sizes (1024px+)
- [ ] Panel doesn't exceed viewport height
- [ ] Z-index higher than other elements (modals, dropdowns)
- [ ] Smooth open/close animations
- [ ] Keyboard navigation works (Tab, Shift+Tab, Escape)
- [ ] Focus indicators visible

### Mobile Testing
- [ ] Bottom sheet displays correctly (portrait/landscape)
- [ ] Touch targets are 48x48px minimum
- [ ] Panel doesn't exceed viewport (100dvh works)
- [ ] Swipe gestures work (if implemented)
- [ ] Fullscreen on small viewports (< 600px)
- [ ] Virtual keyboard doesn't obscure input

### Tablet Testing
- [ ] Positioned panel (not fullscreen)
- [ ] Responsive dimensions (360-400px width)
- [ ] Landscape mode works correctly

### Accessibility Testing
- [ ] Screen reader announces panel state
- [ ] All interactive elements keyboard accessible
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Focus trap works when panel open
- [ ] ARIA attributes correct
- [ ] Live region announces new messages

### Cross-Browser Testing
- [ ] Chrome (desktop & mobile)
- [ ] Firefox (desktop & mobile)
- [ ] Safari (desktop & iOS)
- [ ] Edge
- [ ] Samsung Internet (Android)

---

## 10. References

### Industry Examples
- **Intercom:** https://www.intercom.com (bottom-right, fixed)
- **Zendesk:** https://www.zendesk.com (bottom-right, customizable)
- **Drift:** https://www.drift.com (bottom-right, animated)
- **HubSpot:** https://www.hubspot.com (bottom-right, adaptive)

### Documentation
- **Zendesk Widget API:** https://support.zendesk.com/hc/en-us/articles/4408820711322
- **Intercom Customization:** https://developers.intercom.com/installing-intercom/web/customization
- **Material Design Bottom Sheets:** https://m3.material.io/components/bottom-sheets/guidelines

### Accessibility Guidelines
- **WCAG 2.2:** https://www.w3.org/WAI/WCAG22/quickref/
- **Keyboard Accessibility:** https://webaim.org/techniques/keyboard/
- **ARIA Authoring Practices:** https://www.w3.org/WAI/ARIA/apg/

### Technical Resources
- **CSS Position:** https://developer.mozilla.org/en-US/docs/Web/CSS/position
- **Viewport Units:** https://developer.mozilla.org/en-US/docs/Web/CSS/Viewport_concepts
- **Z-Index:** https://developer.mozilla.org/en-US/docs/Web/CSS/z-index

---

## Conclusion

Chat widget positioning requires balancing visibility, accessibility, and user experience across devices. The key principles are:

1. **Fixed positioning** ensures constant visibility
2. **Bottom-right placement** aligns with user expectations
3. **Viewport-aware constraints** prevent off-screen issues
4. **Mobile-specific patterns** (bottom sheets) improve usability
5. **Structured z-index** prevents conflicts
6. **WCAG compliance** ensures accessibility for all users

By following these best practices, chat widgets remain visible, accessible, and unobtrusive across all devices and screen sizes.
