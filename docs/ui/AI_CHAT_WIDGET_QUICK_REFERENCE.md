# AI Chat Widget - Quick Reference

**Component:** `components/ai_chat_widget.html`
**Status:** ✅ Production Ready
**Version:** 1.0

---

## Usage

### Include in Template

```django
{% if user.is_authenticated %}
{% include 'components/ai_chat_widget.html' %}
{% endif %}
```

**Note:** Already included in `base.html` - no action needed for most pages.

---

## JavaScript API

### Toggle Function

```javascript
// Open or close chat
window.toggleAIChat();
```

### Programmatic Control

```javascript
// Check if chat is open
const panel = document.getElementById('ai-chat-panel');
const isOpen = panel.classList.contains('chat-open');

// Force open
if (!isOpen) {
    window.toggleAIChat();
}

// Force close
if (isOpen) {
    window.toggleAIChat();
}
```

### Event Listeners

```javascript
// Listen for chat state changes
const chatPanel = document.getElementById('ai-chat-panel');
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.attributeName === 'class') {
            const isOpen = chatPanel.classList.contains('chat-open');
            console.log('Chat state changed:', isOpen ? 'open' : 'closed');
        }
    });
});
observer.observe(chatPanel, { attributes: true });
```

---

## DOM Elements

### Key IDs

| Element ID | Purpose |
|------------|---------|
| `ai-chat-widget` | Container wrapper |
| `ai-chat-toggle-btn` | Toggle button |
| `ai-chat-icon` | Button icon (changes state) |
| `ai-chat-panel` | Chat panel container |
| `ai-chat-messages` | Message scroll container |
| `ai-chat-backdrop` | Mobile backdrop overlay |

### Classes

| Class | State | Purpose |
|-------|-------|---------|
| `.chat-open` | Panel | Panel is visible |
| `.chat-active` | Button | Chat is open |
| `.ai-chat-button` | Button | Base button styles |
| `.ai-chat-panel` | Panel | Base panel styles |

---

## Styling

### CSS Variables

```css
/* Emerald gradient (primary) */
--emerald-500: #10b981;
--teal-600: #0d9488;

/* Panel dimensions */
--panel-width: 384px;        /* 24rem */
--panel-height: 500px;
--panel-mobile-height: 80vh;
```

### Custom Animations

```css
/* Pulse ring on button */
@keyframes pulse-ring {
    0%, 100% { opacity: 0; transform: scale(1); }
    50% { opacity: 0.3; transform: scale(1.15); }
}

/* Panel fade-in */
@keyframes slideUpFadeIn {
    from { opacity: 0; transform: translateY(10px) scale(0.95); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}
```

---

## Customization

### Change Button Color

```css
/* Override in your custom CSS */
#ai-chat-toggle-btn {
    background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
    /* Blue gradient instead of emerald */
}
```

### Change Panel Size

```css
/* Desktop */
#ai-chat-panel {
    width: 32rem;  /* Default: 24rem (384px) */
    height: 600px; /* Default: 500px */
}

/* Mobile */
@media (max-width: 640px) {
    #ai-chat-panel {
        height: 90vh; /* Default: 80vh */
    }
}
```

### Change Animation Duration

```css
.ai-chat-panel {
    transition: all 0.5s ease; /* Default: 0.3s */
}
```

---

## HTMX Integration

### Auto-scroll on Message Swap

**Already implemented:**
```javascript
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'ai-chat-messages') {
        event.detail.target.scrollTop = event.detail.target.scrollHeight;
    }
});
```

### Add New Message

```django
<!-- In your Django template -->
<div hx-post="{% url 'common:ai_chat_send' %}"
     hx-target="#ai-chat-messages"
     hx-swap="beforeend">
    <!-- Message form here -->
</div>
```

### Message HTML Template

```html
<!-- User message -->
<div class="flex justify-end">
    <div class="bg-emerald-500 text-white rounded-lg p-3 max-w-[80%]">
        <p class="text-sm">User message text</p>
        <span class="text-xs opacity-75">12:34 PM</span>
    </div>
</div>

<!-- Bot message -->
<div class="flex justify-start">
    <div class="bg-white border border-gray-200 rounded-lg p-3 max-w-[80%]">
        <div class="flex items-start gap-2">
            <div class="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full flex items-center justify-center flex-shrink-0">
                <i class="fas fa-robot text-white text-sm"></i>
            </div>
            <div class="flex-1">
                <p class="text-sm text-gray-700">Bot response text</p>
                <span class="text-xs text-gray-500">12:35 PM</span>
            </div>
        </div>
    </div>
</div>
```

---

## Accessibility

### ARIA Attributes (Auto-managed)

| Element | Attribute | Value (Closed) | Value (Open) |
|---------|-----------|----------------|--------------|
| Toggle Button | `aria-expanded` | `"false"` | `"true"` |
| Toggle Button | `aria-label` | `"Toggle AI Assistant Chat"` | (same) |
| Chat Panel | `aria-hidden` | `"true"` | `"false"` |
| Chat Panel | `role` | `"dialog"` | (same) |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Focus toggle button |
| `Enter` / `Space` | Toggle chat (when focused) |
| `Escape` | Close chat |

### Screen Reader Support

**Announcements:**
- "AI chat opened" (when opening)
- "AI chat closed" (when closing)

**Implementation:**
```javascript
function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    document.body.appendChild(announcement);
    setTimeout(() => document.body.removeChild(announcement), 1000);
}
```

---

## Mobile Behavior

### Breakpoint: 640px

**Desktop (≥ 640px):**
- Panel: 384px × 500px
- Position: Bottom-right, above button
- Backdrop: None

**Mobile (< 640px):**
- Panel: Full-width × 80vh
- Position: Bottom sheet (bottom: 0)
- Backdrop: Black overlay with blur
- Close: Tap backdrop or X button

---

## Troubleshooting

### Chat Won't Open

**Check:**
1. Is user authenticated? (widget only shows for logged-in users)
2. Console errors? (Press F12, check Console tab)
3. Component file exists? (`ls src/templates/components/ai_chat_widget.html`)

**Debug:**
```javascript
// Check if elements exist
console.log('Button:', document.getElementById('ai-chat-toggle-btn'));
console.log('Panel:', document.getElementById('ai-chat-panel'));
console.log('Function:', typeof window.toggleAIChat);
```

---

### Animation Glitches

**Check:**
1. CSS transitions not disabled in browser
2. GPU acceleration available
3. No conflicting CSS from other stylesheets

**Debug:**
```javascript
// Check computed styles
const panel = document.getElementById('ai-chat-panel');
const styles = window.getComputedStyle(panel);
console.log('Transition:', styles.transition);
console.log('Transform:', styles.transform);
```

---

### Z-Index Issues

**Check:**
1. Other elements with `z-index > 9999`
2. Parent containers creating stacking contexts

**Fix:**
```css
/* Increase z-index if needed */
#ai-chat-widget {
    z-index: 10000; /* Default: 9999 */
}
```

---

### Mobile Backdrop Not Showing

**Check:**
1. Screen width < 640px
2. Backdrop element exists
3. No CSS hiding backdrop

**Debug:**
```javascript
// Check backdrop state
const backdrop = document.getElementById('ai-chat-backdrop');
console.log('Backdrop exists:', !!backdrop);
console.log('Backdrop classes:', backdrop.className);
console.log('Window width:', window.innerWidth);
```

---

## Performance Tips

### Reduce Animation Duration

For slower devices:
```css
.ai-chat-panel {
    transition: all 0.2s ease; /* Faster = less GPU work */
}
```

### Disable Backdrop Blur

If performance issues on mobile:
```css
#ai-chat-backdrop {
    backdrop-filter: none; /* Remove blur */
    -webkit-backdrop-filter: none;
}
```

### Lazy Load Messages

For long chat histories:
```javascript
// Implement virtual scrolling or pagination
// Load only recent messages initially
// Load older messages on scroll to top
```

---

## Future Backend Integration

### Required Django View

```python
# src/common/views/chat.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def ai_chat_send(request):
    user_message = request.POST.get('message')

    # TODO: Send to AI service (Gemini)
    # bot_response = ai_service.generate_response(user_message)

    return render(request, 'common/partials/chat_message.html', {
        'message': user_message,
        'response': 'Response coming soon...',
        'timestamp': timezone.now()
    })
```

### Required URL Pattern

```python
# src/common/urls.py
from django.urls import path
from .views import chat

urlpatterns = [
    # ... existing patterns ...
    path('ai-chat/send/', chat.ai_chat_send, name='ai_chat_send'),
]
```

### Message Template

```django
<!-- src/templates/common/partials/chat_message.html -->
<!-- User message -->
<div class="flex justify-end animate-fade-in">
    <div class="bg-emerald-500 text-white rounded-lg p-3 max-w-[80%]">
        <p class="text-sm">{{ message }}</p>
        <span class="text-xs opacity-75">{{ timestamp|time:"g:i A" }}</span>
    </div>
</div>

<!-- Bot response -->
<div class="flex justify-start animate-fade-in">
    <div class="bg-white border border-gray-200 rounded-lg p-3 max-w-[80%]">
        <div class="flex items-start gap-2">
            <div class="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full flex items-center justify-center flex-shrink-0">
                <i class="fas fa-robot text-white text-sm"></i>
            </div>
            <div class="flex-1">
                <p class="text-sm text-gray-700">{{ response }}</p>
                <span class="text-xs text-gray-500">{{ timestamp|time:"g:i A" }}</span>
            </div>
        </div>
    </div>
</div>
```

---

## Related Documentation

- [AI Chat Widget Fix Summary](./AI_CHAT_WIDGET_FIX_SUMMARY.md)
- [AI Chat Widget Testing Guide](../testing/AI_CHAT_WIDGET_TESTING_GUIDE.md)
- [OBCMS UI Components Standards](./OBCMS_UI_COMPONENTS_STANDARDS.md)
- [Accessibility Guidelines](../guidelines/ACCESSIBILITY.md)

---

## Component File Location

```
src/templates/components/ai_chat_widget.html
```

**Lines of Code:** ~450 lines (HTML + CSS + JavaScript)

**Last Updated:** 2025-10-06
**Maintainer:** OBCMS Development Team

---

## Quick Links

- [View Component Source](../../templates/components/ai_chat_widget.html)
- [Report Bug](https://github.com/tech-bangsamoro/obcms/issues)
- [Request Feature](https://github.com/tech-bangsamoro/obcms/issues)

---

**Pro Tip:** Press `Ctrl + Shift + C` in browser to inspect the chat widget and see live CSS changes!
