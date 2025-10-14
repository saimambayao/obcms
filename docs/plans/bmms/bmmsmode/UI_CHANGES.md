# User Interface Changes in BMMS Mode

## Overview

Switching from OBCMS to BMMS mode introduces significant changes to the user interface and navigation experience. This document details all UI modifications, new features, and visual differences users will encounter in BMMS mode.

## Navigation Structure Changes

### URL Structure Transformation

**OBCMS Mode Navigation:**
```
🏠 Dashboard                → /dashboard/
👥 Communities             → /communities/
📊 M&E Assessment          → /mana/
🤝 Partnerships            → /coordination/
📋 Projects                → /project-central/
📅 Calendar                → /calendar/
📈 Reports                 → /reports/
```

**BMMS Mode Navigation:**
```
🏠 Dashboard                → /moa/OOBC/dashboard/
👥 Communities             → /moa/OOBC/communities/
📊 M&E Assessment          → /moa/OOBC/mana/
🤝 Partnerships            → /moa/OOBC/coordination/
📋 Projects                → /moa/OOBC/project-central/
📅 Calendar                → /moa/OOBC/calendar/
📈 Reports                 → /moa/OOBC/reports/
```

### Organization Selector (New in BMMS)

**Location:** Top navigation bar, right side

**OBCMS Mode:** No organization selector present
**BMMS Mode:** Organization selector dropdown visible

```html
<!-- BMMS Mode Organization Selector -->
<div class="organization-selector">
    <label for="org-select">Current Organization:</label>
    <select id="org-select" class="form-select" onchange="switchOrganization(this.value)">
        <option value="/moa/OOBC/" selected>Office for Other Bangsamoro Communities (OOBC)</option>
        <option value="/moa/MOH/">Ministry of Health (MOH)</option>
        <option value="/moa/MENR/">Ministry of Environment (MENR)</option>
        <option value="/moa/MAFAR/">Ministry of Agriculture (MAFAR)</option>
    </select>
</div>
```

## Visual Interface Changes

### 1. Header and Branding

**OBCMS Mode Header:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🏛️ OBCMS                                                 👤 User │
│ Office for Other Bangsamoro Communities Management System    │
├─────────────────────────────────────────────────────────────┤
│ Dashboard Communities M&E Coordination Projects Calendar    │
└─────────────────────────────────────────────────────────────┘
```

**BMMS Mode Header:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🏛️ BMMS                            Organization: 👤 User  │
│ Bangsamoro Ministerial Management System              [OOBC ▼] │
├─────────────────────────────────────────────────────────────┤
│ Dashboard Communities M&E Coordination Projects Calendar    │
└─────────────────────────────────────────────────────────────┘
```

### 2. Sidebar Navigation

**OBCMS Mode Sidebar:**
```html
<nav class="sidebar">
    <div class="sidebar-header">
        <h4>OBCMS</h4>
        <p>Office for Other Bangsamoro Communities</p>
    </div>
    <ul class="nav-menu">
        <li><a href="/dashboard/">🏠 Dashboard</a></li>
        <li><a href="/communities/">👥 Communities</a></li>
        <li><a href="/mana/">📊 M&E Assessment</a></li>
        <li><a href="/coordination/">🤝 Partnerships</a></li>
        <li><a href="/project-central/">📋 Projects</a></li>
    </ul>
</nav>
```

**BMMS Mode Sidebar:**
```html
<nav class="sidebar">
    <div class="sidebar-header">
        <h4>BMMS</h4>
        <p>Bangsamoro Ministerial Management System</p>
        <div class="current-org">
            <span class="org-badge">OOBC</span>
            <span class="org-name">Office for Other Bangsamoro Communities</span>
        </div>
    </div>
    <ul class="nav-menu">
        <li><a href="{{ org_url_prefix }}/dashboard/">🏠 Dashboard</a></li>
        <li><a href="{{ org_url_prefix }}/communities/">👥 Communities</a></li>
        <li><a href="{{ org_url_prefix }}/mana/">📊 M&E Assessment</a></li>
        <li><a href="{{ org_url_prefix }}/coordination/">🤝 Partnerships</a></li>
        <li><a href="{{ org_url_prefix }}/project-central/">📋 Projects</a></li>
    </ul>
    <div class="org-switcher">
        <button class="btn btn-sm btn-outline-primary" onclick="showOrgSwitcher()">
            🔄 Switch Organization
        </button>
    </div>
</nav>
```

### 3. Dashboard Modifications

**OBCMS Mode Dashboard:**
```html
<div class="dashboard-header">
    <h1>Dashboard</h1>
    <p class="breadcrumb">Home / Dashboard</p>
</div>

<div class="stats-grid">
    <div class="stat-card">
        <h3>Total Communities</h3>
        <div class="stat-number">156</div>
    </div>
    <div class="stat-card">
        <h3>Active Assessments</h3>
        <div class="stat-number">23</div>
    </div>
    <div class="stat-card">
        <h3>Ongoing Projects</h3>
        <div class="stat-number">45</div>
    </div>
</div>
```

**BMMS Mode Dashboard:**
```html
<div class="dashboard-header">
    <h1>{{ organization_name }} Dashboard</h1>
    <p class="breadcrumb">
        Home / 
        <span class="org-breadcrumb">{{ organization_code }}</span> / 
        Dashboard
    </p>
</div>

<div class="org-info-bar">
    <div class="org-badge-large">{{ organization_code }}</div>
    <div class="org-details">
        <h2>{{ organization_name }}</h2>
        <p>Organization ID: {{ current_organization.id }}</p>
    </div>
    {% if is_ocm_user %}
    <div class="ocm-indicator">
        <span class="badge bg-info">OCM Read-Only Access</span>
    </div>
    {% endif %}
</div>

<div class="stats-grid">
    <div class="stat-card">
        <h3>Total Communities</h3>
        <div class="stat-number">{{ community_count }}</div>
        <small>{{ organization_code }} only</small>
    </div>
    <div class="stat-card">
        <h3>Active Assessments</h3>
        <div class="stat-number">{{ assessment_count }}</div>
        <small>{{ organization_code }} only</small>
    </div>
    <div class="stat-card">
        <h3>Ongoing Projects</h3>
        <div class="stat-number">{{ project_count }}</div>
        <small>{{ organization_code }} only</small>
    </div>
</div>
```

## Template Context Changes

### Available Template Variables

**OBCMS Mode Context:**
```python
{
    'user': <User object>,
    'request': <HttpRequest object>,
    'csrf_token': 'abc123',
    'DEBUG': True,
    'SITE_NAME': 'OBCMS',
}
```

**BMMS Mode Context:**
```python
{
    'user': <User object>,
    'request': <HttpRequest object>,
    'csrf_token': 'abc123',
    'DEBUG': False,
    'SITE_NAME': 'BMMS',
    
    # New BMMS-specific variables
    'current_organization': <Organization object>,
    'organization_code': 'OOBC',
    'organization_name': 'Office for Other Bangsamoro Communities',
    'org_url_prefix': '/moa/OOBC',
    'is_bmms_mode': True,
    'enabled_modules': ['communities', 'mana', 'coordination'],
    'user_organizations': [<Organization list>],
    'is_ocm_user': False,
    'can_switch_organization': True,
}
```

### Template Usage Examples

**URL Generation:**
```html
<!-- OBCMS Mode -->
<a href="{% url 'community_list' %}">Communities</a>
<a href="/communities/{{ community.id }}/">View Community</a>

<!-- BMMS Mode -->
<a href="{% url 'community_list' org_code=current_organization.code %}">Communities</a>
<a href="{{ org_url_prefix }}/communities/{{ community.id }}/">View Community</a>
```

**Organization Display:**
```html
<!-- BMMS Mode Only -->
{% if is_bmms_mode %}
<div class="organization-header">
    <span class="org-badge">{{ organization_code }}</span>
    <h3>{{ organization_name }}</h3>
    {% if is_ocm_user %}
        <p class="text-info">🔓 OCM Read-Only Access</p>
    {% endif %}
</div>
{% endif %}
```

## New UI Components

### 1. Organization Switcher Modal

```html
<!-- Organization Switcher Modal -->
<div class="modal fade" id="orgSwitcherModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Switch Organization</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p>Select an organization to switch to:</p>
                <div class="org-list">
                    {% for org in user_organizations %}
                    <div class="org-item {% if org.id == current_organization.id %}active{% endif %}">
                        <div class="org-info">
                            <span class="org-badge">{{ org.code }}</span>
                            <span class="org-name">{{ org.name }}</span>
                        </div>
                        <button class="btn btn-primary btn-sm" 
                                onclick="switchToOrganization({{ org.id }})"
                                {% if org.id == current_organization.id %}disabled{% endif %}>
                            {% if org.id == current_organization.id %}Current{% else %}Switch{% endif %}
                        </button>
                    </div>
                    {% endfor %}
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            </div>
        </div>
    </div>
</div>
```

### 2. Organization Context Bar

```html
<!-- Organization Context Bar (BMMS Mode) -->
{% if is_bmms_mode %}
<div class="org-context-bar bg-light border-bottom">
    <div class="container-fluid">
        <div class="row align-items-center">
            <div class="col-md-6">
                <div class="org-display">
                    <span class="badge bg-primary org-badge-large">{{ organization_code }}</span>
                    <span class="org-name ms-2">{{ organization_name }}</span>
                    {% if is_ocm_user %}
                        <span class="badge bg-warning ms-2">OCM Access</span>
                    {% endif %}
                </div>
            </div>
            <div class="col-md-6 text-end">
                {% if can_switch_organization %}
                <div class="org-actions">
                    <button class="btn btn-outline-primary btn-sm" 
                            onclick="showOrgSwitcher()">
                        🔄 Switch Organization
                    </button>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endif %}
```

### 3. Breadcrumb Navigation

```html
<!-- Enhanced Breadcrumb Navigation -->
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item">
            <a href="{{ org_url_prefix }}/dashboard/">🏠 Home</a>
        </li>
        
        {% if is_bmms_mode %}
        <li class="breadcrumb-item">
            <a href="{{ org_url_prefix }}/">{{ organization_code }}</a>
        </li>
        {% endif %}
        
        <li class="breadcrumb-item active" aria-current="page">
            {{ page_title }}
        </li>
    </ol>
</nav>
```

## JavaScript Enhancements

### 1. Organization Switching

```javascript
// Organization switching functionality
function switchOrganization(orgId) {
    fetch(`/switch-organization/${orgId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            showNotification('Organization switched successfully', 'success');
            // Reload page after short delay
            setTimeout(() => {
                window.location.href = data.redirect_url;
            }, 1000);
        } else {
            showNotification('Failed to switch organization', 'error');
        }
    })
    .catch(error => {
        console.error('Error switching organization:', error);
        showNotification('Error switching organization', 'error');
    });
}

// URL prefix helper for BMMS mode
function getOrgUrlPrefix() {
    return window.orgUrlPrefix || '';
}

// Generate organization-aware URLs
function orgUrl(path) {
    const prefix = getOrgUrlPrefix();
    return prefix + path;
}
```

### 2. Mode Detection

```javascript
// Detect current mode for UI adjustments
function isBmmsMode() {
    return window.isBmmsMode || false;
}

// Adjust UI based on mode
document.addEventListener('DOMContentLoaded', function() {
    if (isBmmsMode()) {
        // Show BMMS-specific UI elements
        document.querySelectorAll('.bmms-only').forEach(el => {
            el.style.display = 'block';
        });
        
        // Hide OBCMS-only elements
        document.querySelectorAll('.obcms-only').forEach(el => {
            el.style.display = 'none';
        });
        
        // Initialize organization switcher
        initializeOrgSwitcher();
    } else {
        // Show OBCMS-specific UI elements
        document.querySelectorAll('.obcms-only').forEach(el => {
            el.style.display = 'block';
        });
        
        // Hide BMMS-only elements
        document.querySelectorAll('.bmms-only').forEach(el => {
            el.style.display = 'none';
        });
    }
});
```

## Responsive Design Considerations

### Mobile Navigation

**OBCMS Mode Mobile:**
```
┌─────────────────────────┐
│ ☰ OBCMS              👤 │
│ Office for Other...      │
├─────────────────────────┤
│ 🏠 Dashboard           │
│ 👥 Communities        │
│ 📊 M&E Assessment     │
│ 🤝 Partnerships       │
│ 📋 Projects           │
└─────────────────────────┘
```

**BMMS Mode Mobile:**
```
┌─────────────────────────┐
│ ☰ BMMS            [OOBC▼]│
│ Bangsamoro Ministerial  │
├─────────────────────────┤
│ 🏠 Dashboard           │
│ 👥 Communities        │
│ 📊 M&E Assessment     │
│ 🤝 Partnerships       │
│ 📋 Projects           │
│ ───────────────────── │
│ 🔄 Switch Organization │
└─────────────────────────┘
```

### Tablet Navigation

**Tablet Organization Display:**
```css
@media (min-width: 768px) and (max-width: 1024px) {
    .org-context-bar {
        flex-direction: column;
        text-align: center;
    }
    
    .org-display {
        margin-bottom: 10px;
    }
    
    .org-actions {
        text-align: center;
    }
}
```

## Accessibility Improvements

### ARIA Labels and Roles

```html
<!-- Organization Selector with Accessibility -->
<div class="organization-selector" role="navigation" aria-label="Organization Selection">
    <label for="org-select" id="org-select-label">Current Organization:</label>
    <select id="org-select" 
            class="form-select" 
            aria-labelledby="org-select-label"
            aria-describedby="org-select-help"
            onchange="switchOrganization(this.value)">
        <option value="/moa/OOBC/" selected>Office for Other Bangsamoro Communities (OOBC)</option>
        <option value="/moa/MOH/">Ministry of Health (MOH)</option>
    </select>
    <div id="org-select-help" class="form-text">
        Select an organization to view its data and manage its resources
    </div>
</div>

<!-- Organization Badge with Screen Reader Support -->
<span class="org-badge" role="status" aria-live="polite">
    {{ organization_code }}
</span>
```

### Keyboard Navigation

```javascript
// Keyboard navigation for organization switching
document.addEventListener('keydown', function(e) {
    // Ctrl+Shift+O: Open organization switcher
    if (e.ctrlKey && e.shiftKey && e.key === 'O') {
        e.preventDefault();
        showOrgSwitcher();
    }
    
    // Escape: Close organization switcher
    if (e.key === 'Escape') {
        hideOrgSwitcher();
    }
});

// Focus management for modal
function showOrgSwitcher() {
    const modal = document.getElementById('orgSwitcherModal');
    modal.style.display = 'block';
    
    // Set focus to first organization option
    const firstOrgOption = modal.querySelector('.org-item button:not([disabled])');
    if (firstOrgOption) {
        firstOrgOption.focus();
    }
}
```

## CSS Styling Changes

### Organization-Specific Styling

```css
/* Organization Badge Styles */
.org-badge {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 0.8em;
}

.org-badge-large {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 1.1em;
}

/* Organization Context Bar */
.org-context-bar {
    background: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    padding: 10px 0;
}

.org-display {
    display: flex;
    align-items: center;
    gap: 10px;
}

.org-name {
    font-weight: 600;
    color: #495057;
}

/* OCM Access Indicator */
.ocm-indicator .badge {
    background: linear-gradient(135deg, #ffc107, #e0a800);
    color: #212529;
}

/* Organization Switcher Styles */
.org-list {
    max-height: 400px;
    overflow-y: auto;
}

.org-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    margin-bottom: 5px;
}

.org-item.active {
    background-color: #e7f3ff;
    border-color: #007bff;
}

.org-info {
    display: flex;
    align-items: center;
    gap: 10px;
}

/* BMMS Mode Specific Styles */
body.bmms-mode .sidebar-header {
    background: linear-gradient(135deg, #28a745, #1e7e34);
    color: white;
}

body.bmms-mode .nav-menu a:hover {
    background-color: rgba(40, 167, 69, 0.1);
}

/* OBCMS Mode Specific Styles */
body.obcms-mode .sidebar-header {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
}
```

## User Experience Improvements

### Loading States

```html
<!-- Organization Switching Loading State -->
<div id="org-switching-loading" class="loading-overlay" style="display: none;">
    <div class="loading-spinner">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Switching organization...</span>
        </div>
        <p class="mt-2">Switching to {{ target_org_name }}...</p>
    </div>
</div>
```

### Success/Error Messages

```javascript
// Notification system for organization switching
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}
```

---

**Related Documentation:**
- [Mode Switching Process](MODE_SWITCHING_PROCESS.md) - Step-by-step switching instructions
- [System Changes](SYSTEM_CHANGES.md) - Technical changes during mode switching
- [Security Implications](SECURITY_IMPLICATIONS.md) - Security-related UI changes

**Last Updated:** October 14, 2025  
**Implementation Status:** Complete  
**Testing Status:** Ready for staging validation