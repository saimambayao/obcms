# Django Admin Navbar Visual Guide

## Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 🛡️ OBC Management System - Admin            👤 John Doe  [User Menu ▼]  ☰    │
│                                               Superuser                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 🏠 Dashboard │ 👥 OBC Data ▼ │ 🗺️ MANA ▼ │ 🤝 Coordination ▼ │ ⚖️ Recs ▼ │...│
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Dropdown Example (OBC Data)

```
┌────────────────────────────────────────┐
│  📍 Communities                        │
│     Manage OBC community profiles      │
├────────────────────────────────────────┤
│  🏙️ Municipal Profiles                 │
│     Municipal coverage and statistics  │
└────────────────────────────────────────┘
```

### User Menu Dropdown

```
┌──────────────────────────┐
│  👤 John Doe             │
│     Superuser            │
├──────────────────────────┤
│  🔗 View site            │
│  📖 Documentation        │
│  🔑 Change password      │
├──────────────────────────┤
│  🚪 Log out              │
└──────────────────────────┘
```

## Mobile Layout

```
┌──────────────────────────────────┐
│ 🛡️ OBC Admin  [👤]  [☰]         │
└──────────────────────────────────┘
```

**Expanded Mobile Menu:**

```
┌──────────────────────────────────┐
│ 🛡️ OBC Admin  [👤]  [✕]         │
├──────────────────────────────────┤
│ 🏠 Dashboard                     │
│ ───────────────────────────────  │
│ 👥 OBC Data              [▼]     │
│   📍 Communities                 │
│   🏙️ Municipal Profiles          │
│ ───────────────────────────────  │
│ 🗺️ MANA                  [▼]     │
│   📋 Assessments                 │
│   🗺️ Geographic Data             │
│ ───────────────────────────────  │
│ ...                              │
└──────────────────────────────────┘
```

## Color Scheme

### Gradient Background
```
┌────────────────────────────────────┐
│ Blue-800 ──────► Emerald-600       │
│ #1e40af         #059669            │
└────────────────────────────────────┘
```

### Icon Colors (Semantic)
- 📍 **Blue-500** (`#3b82f6`) - Communities
- 🏙️ **Indigo-500** (`#6366f1`) - Municipal
- 📋 **Sky-500** (`#0ea5e9`) - Assessments
- 🗺️ **Purple-500** (`#a855f7`) - Geographic
- 🏢 **Cyan-500** (`#06b6d4`) - Organizations
- 📄 **Amber-500** (`#f59e0b`) - Partnerships
- 📅 **Lime-500** (`#84cc16`) - Events
- ⚖️ **Orange-500** (`#f97316`) - Policies
- 📊 **Emerald-500** (`#10b981`) - Projects

## Interaction States

### Normal
```css
background: transparent
color: white/90 (rgba(255,255,255,0.9))
```

### Hover
```css
background: white/10 (rgba(255,255,255,0.1))
color: white (#ffffff)
```

### Active (Current Page)
```css
background: white/15 (rgba(255,255,255,0.15))
border-bottom: 2px solid white
```

### Focus (Keyboard)
```css
outline: 2px solid emerald-300
outline-offset: 2px
```

## Dropdown Animations

### Desktop
```
Initial State:
- opacity: 0
- transform: translateY(-10px)

On Hover:
- opacity: 1
- transform: translateY(0)
- transition: 200ms ease
```

### Mobile
```
Closed:
- max-height: 0
- overflow: hidden

Open:
- max-height: 500px
- transition: 300ms ease
```

### Chevron Rotation
```
Normal:  ▼ (0deg)
Hover:   ▲ (180deg)
transition: 200ms ease
```

## Navigation Item Structure

### Desktop Dropdown Button
```html
<button class="admin-nav-item">
  <i class="fas fa-icon"></i>
  <span>Section Name</span>
  <i class="fas fa-chevron-down"></i>
</button>
```

### Desktop Dropdown Menu
```html
<div class="admin-dropdown-menu">
  <a href="...">
    <i class="fas fa-icon color-class"></i>
    <span>
      <span class="block font-semibold">Title</span>
      <span class="block text-xs">Description</span>
    </span>
  </a>
</div>
```

### Mobile Toggle
```html
<button class="admin-mobile-toggle"
        data-target="admin-mobile-section-id">
  <span>
    <i class="fas fa-icon"></i>
    <span>Section Name</span>
  </span>
  <i class="fas fa-chevron-down"></i>
</button>
```

## Responsive Breakpoints

| Breakpoint | Width    | Layout                    |
|------------|----------|---------------------------|
| Mobile     | < 768px  | Hamburger menu only       |
| Tablet     | 768-1023 | Hamburger + user info     |
| Desktop    | ≥ 1024px | Full horizontal nav       |

## Accessibility Features

### ARIA Attributes
```html
<!-- Dropdown Button -->
<button aria-haspopup="true"
        aria-expanded="false"
        aria-label="OBC Data menu">
  ...
</button>

<!-- Dropdown Menu -->
<div role="menu"
     aria-label="OBC Data Submodules">
  <a role="menuitem" href="...">...</a>
</div>
```

### Keyboard Navigation Flow
```
Tab → Dashboard → OBC Data ▼ → MANA ▼ → ...
      ↓
      Enter/Space opens dropdown
      ↓
      Tab → First menu item → Second menu item → ...
      ↓
      Escape closes dropdown, returns to button
```

## Z-Index Hierarchy

```
50  - Sticky header (#header)
50  - Dropdown menus (.admin-dropdown-menu)
50  - User dropdown menu (.admin-user-dropdown-menu)
50  - Mobile menu (#adminMobileMenu)
```

## Touch Targets

### Minimum Sizes (Mobile)
- Buttons: **48px height**
- Menu items: **48px height**
- User dropdown: **36px circle** (adequate for thumb)

### Spacing
- Between buttons: **4px** (space-x-1)
- Menu items: **2px** (space-y-2)
- Dropdown items: **12px padding** (py-3)

## Print Styles

When printing:
- ❌ Hide navigation bar
- ❌ Hide user dropdown
- ❌ Hide mobile menu
- ✅ Show only content area
- ✅ Static header (no sticky)

## Performance Metrics

- **Initial Load**: < 50ms (CSS + JS)
- **Dropdown Open**: 200ms animation
- **Mobile Menu**: 300ms slide-down
- **Scroll Listener**: Debounced 250ms
- **Resize Listener**: Debounced 250ms

## Browser Support

| Feature           | Chrome | Firefox | Safari | Edge | Mobile |
|-------------------|--------|---------|--------|------|--------|
| Flexbox           | ✅     | ✅      | ✅     | ✅   | ✅     |
| Transitions       | ✅     | ✅      | ✅     | ✅   | ✅     |
| Transform         | ✅     | ✅      | ✅     | ✅   | ✅     |
| Hover (Desktop)   | ✅     | ✅      | ✅     | ✅   | N/A    |
| Click (Mobile)    | ✅     | ✅      | ✅     | ✅   | ✅     |
| ARIA Support      | ✅     | ✅      | ✅     | ✅   | ✅     |

---

**Last Updated:** 2025-10-13
**Document Version:** 1.0
