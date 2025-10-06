# Fast Tree UI Patterns: Best Practices for Hierarchical Interactions

**Research Summary: Creating Instant, Smooth Tree UI Experiences**

*Priority: HIGH | Complexity: Moderate | Prerequisites: HTMX, Django ORM optimization*

---

## Executive Summary

This document consolidates research on creating fast, smooth hierarchical tree UI interactions based on modern web performance best practices, HTMX patterns, and user experience research. The key finding: **perceived performance matters more than actual performance** - users judge speed by how responsive the UI feels, not by actual load times.

### Core Principles

1. **Sub-100ms feels instant** - Aim for <50ms UI response to user interactions
2. **100-300ms feels fast** - Acceptable for visual transitions and animations
3. **>300ms needs feedback** - Show skeleton screens or loading indicators
4. **Optimistic UI is king** - Update UI immediately, handle server response later

---

## 1. Performance Timing Benchmarks

### User Perception Thresholds

Based on extensive UX research, here are the critical timing thresholds:

| Timing | User Perception | UI Strategy |
|--------|----------------|-------------|
| **0-50ms** | Instantaneous - feels like direct manipulation | Ideal target for UI feedback |
| **50-100ms** | Instant - no perceptible delay | Optimistic UI updates |
| **100-200ms** | Fast - slight pause but acceptable | Smooth transitions, no spinner needed |
| **200-300ms** | Noticeable - user starts to feel the delay | Consider loading indicators |
| **300-1000ms** | Slow - requires feedback | Show skeleton screens or spinners |
| **>1000ms** | Very slow - attention wanders | Progress indicators essential |

### Key Research Findings

**From Nielsen Norman Group:**
> "Operations that are completed in 100ms or fewer will feel instantaneous to the user, which is the gold standard to aim for when optimizing websites."

**From MDN Performance Guide:**
> "When users interact with content, it's important to provide feedback and acknowledge the user's response or interaction within 100ms, preferably within 50ms. 50ms feels immediate."

**The 300ms Mobile Problem:**
> "Traditionally mobile browsers have waited 300ms after a user touches a button to see if the user will make a double tap, which already blows the ideal 100ms response time by 300 percent before even starting to execute an operation."

### Applying to Tree UI

For hierarchical tree expand/collapse interactions:

- **Target: <50ms** - Click to visual feedback (chevron rotation, highlight)
- **Target: 100-200ms** - Expand/collapse animation duration
- **Target: <300ms** - Server response for lazy-loaded children
- **Fallback: Skeleton screen** - If server response >300ms

---

## 2. Loading States & Perceived Performance

### Skeleton Screens vs Spinners

**Research shows skeleton screens improve perceived performance by 20-30%:**

| Metric | Skeleton Screens | Spinners |
|--------|-----------------|----------|
| Perceived speed | **30% faster** | Baseline |
| User engagement | High - shows content structure | Low - generic indicator |
| Wait time perception | Feels 20% shorter | Feels longer (passive waiting) |
| Context provided | Yes - previews layout | No - abstract indicator |
| Best for | >300ms loads | Quick operations <1s |

### Why Skeleton Screens Win

**Active vs Passive Waiting:**
> "According to research on time perception, active waiting periods are perceived as faster than passive waiting phases. With a progress bar or spinner, the entire waiting period is passive: there's nothing to do but watch this spinner that has absolutely nothing to do with the content we're about to see."

**Mental Model Building:**
> "The skeleton screen helps users build a mental model of what will be on the page and even gives some clues as to the underlying information hierarchy. Skeleton screens are great at creating the illusion of progress and making users feel like the site is loading faster."

### When to Skip Loading Indicators

**Critical guideline:**
> "If a page takes less than 1 second to load, skeleton screens or spinners aren't necessary, as they likely won't make a difference to the users' experience."

### Tree UI Application

For hierarchical tree loading:

```html
<!-- Good: Skeleton for lazy-loaded children -->
<div class="tree-children-skeleton">
    <div class="skeleton-item animate-pulse">
        <div class="h-4 bg-gray-200 rounded w-3/4"></div>
    </div>
    <div class="skeleton-item animate-pulse">
        <div class="h-4 bg-gray-200 rounded w-2/3"></div>
    </div>
</div>

<!-- Bad: Generic spinner -->
<div class="spinner"></div>
```

**Implementation pattern:**
1. Click expand → Instant chevron rotation (optimistic UI)
2. If load <300ms → Direct content swap
3. If load >300ms → Show skeleton screen matching tree structure
4. Content arrives → Smooth transition from skeleton to real content

---

## 3. Optimistic UI Updates

### What is Optimistic UI?

**Definition:**
> "Optimistic UI is a technique that makes apps feel more responsive by updating the UI before receiving a server response. This design and development approach means changes made by a user are immediately reflected in the user interface, even before those changes are confirmed by the server."

### Key Benefits

1. **Improved Perceived Performance:**
   - Interactions feel instant (sub-50ms response)
   - Eliminates waiting for server confirmation
   - 30%+ improvement in perceived speed

2. **Better User Experience:**
   > "Users can interact with the app continuously without interruptions from loading spinners or waiting screens, enhancing overall responsiveness."

3. **Works Offline:**
   > "It can work well in scenarios with intermittent or low connectivity, allowing users to continue interacting even when temporarily disconnected."

### Error Handling

**Critical requirement:**
> "If the server returns an error (e.g., a network issue or validation failure), the app must handle it by removing the cached data or reverting to the previous state. If the operation fails, the UI state reverts to its previous state and an error is displayed."

### Tree UI Implementation

**Pattern for expand/collapse:**

```javascript
// 1. Optimistic UI update (instant)
treeNode.classList.add('expanded');
chevron.style.transform = 'rotate(90deg)';
childrenContainer.style.display = 'block';

// 2. HTMX request in background
htmx.ajax('GET', `/tree/${nodeId}/children/`, {
    target: '#children-' + nodeId,
    swap: 'innerHTML'
});

// 3. Error handling
htmx.on('htmx:responseError', function(evt) {
    // Revert optimistic changes
    treeNode.classList.remove('expanded');
    chevron.style.transform = 'rotate(0deg)';
    childrenContainer.style.display = 'none';

    // Show error message
    showToast('Failed to load children', 'error');
});
```

**HTMX-specific pattern:**

```html
<!-- Optimistic expand with error recovery -->
<div
    class="tree-node"
    hx-get="/tree/{{ node.id }}/children/"
    hx-target="#children-{{ node.id }}"
    hx-swap="innerHTML show:none"
    hx-indicator="#loading-{{ node.id }}"
    data-optimistic="expand"
    onclick="this.querySelector('.chevron').style.transform='rotate(90deg)'"
>
    <i class="chevron fa fa-chevron-right transition-transform duration-200"></i>
    <span>{{ node.name }}</span>

    <div id="children-{{ node.id }}" class="tree-children"></div>
    <div id="loading-{{ node.id }}" class="htmx-indicator">
        <!-- Skeleton screen -->
    </div>
</div>
```

---

## 4. Animation & Visual Feedback

### Animation Duration Guidelines

**From UX Research:**
> "The speed of an animation is hugely important for usability — too fast, and it's hard to see or dizzying; too slow, and it becomes intrusive and feels like a delay to the user. In animation, tiny details matter, because a tenth of a second will make a big difference to the user experience."

**Recommended Durations:**

| Interaction Type | Duration | CSS Example |
|-----------------|----------|-------------|
| Microinteractions (chevron, highlight) | 100-150ms | `transition: transform 0.1s ease` |
| Expand/collapse animation | 200-300ms | `transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1)` |
| Fade in/out | 150-200ms | `transition: opacity 0.15s ease` |
| Skeleton to content | 200ms | `transition: opacity 0.2s ease` |

### CSS Animation Performance

**Critical Performance Rule:**
> "Animating properties like height triggers layout or paint, while transform and opacity don't. Animating width and height requires calculating layout and painting the results on every frame, which is very expensive and typically causes frame drops."

**Performance Comparison:**

| Property | Performance | Triggers | Recommendation |
|----------|------------|----------|----------------|
| `transform` | ✅ Excellent - GPU accelerated | Composite only | **Use for animations** |
| `opacity` | ✅ Excellent - GPU accelerated | Composite only | **Use for animations** |
| `height` | ❌ Poor - CPU intensive | Layout + Paint + Composite | Avoid animating |
| `width` | ❌ Poor - CPU intensive | Layout + Paint + Composite | Avoid animating |
| `margin`/`padding` | ❌ Poor - CPU intensive | Layout + Paint + Composite | Avoid animating |

### Solution: Transform-Based Expand/Collapse

**Problem:** Animating `height: 0` to `height: auto` is not performant.

**Solution:** Use `transform: scaleY()` with counter-transforms:

```css
/* Performant expand/collapse */
.tree-children {
    transform-origin: top;
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.tree-children.collapsed {
    transform: scaleY(0);
}

.tree-children.expanded {
    transform: scaleY(1);
}

/* Counter-transform to prevent child squishing */
.tree-children.collapsed > .tree-node {
    transform: scaleY(0); /* Inverse of parent */
}

.tree-children.expanded > .tree-node {
    transform: scaleY(1);
}
```

**Alternative: Modern CSS (Chrome 129+):**

```css
/* New CSS feature - limited browser support */
.tree-children {
    height: 0;
    transition: height 0.25s ease;
    interpolate-size: allow-keywords; /* Enable height: auto animation */
}

.tree-children.expanded {
    height: auto;
}
```

### Visual Feedback Patterns

**Chevron Rotation (Microinteraction):**
```css
.chevron {
    transition: transform 0.1s ease;
}

.tree-node.expanded .chevron {
    transform: rotate(90deg);
}
```

**Highlight on Hover/Click:**
```css
.tree-node {
    transition: background-color 0.15s ease;
}

.tree-node:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

.tree-node:active {
    background-color: rgba(0, 0, 0, 0.1);
}
```

---

## 5. Technical Approaches: HTMX vs JavaScript

### When to Use HTMX

**Best for:**
- ✅ Lazy loading tree children from server
- ✅ Progressive disclosure (load on demand)
- ✅ Server-driven tree updates
- ✅ Out-of-band swaps (update multiple tree sections)
- ✅ SEO-friendly initial tree structure

**HTMX Advantages:**
> "HTMX's lightweight nature results in more rapid page loads, with users benefiting from faster interactions and lower latency since they do not have to load large JavaScript libraries or frameworks."

**Lazy Loading Pattern:**

```html
<!-- HTMX lazy load on expand -->
<div class="tree-node">
    <button
        hx-get="/api/tree/{{ node.id }}/children/"
        hx-trigger="click once"
        hx-target="#children-{{ node.id }}"
        hx-swap="innerHTML show:none"
        hx-indicator=".skeleton-{{ node.id }}"
    >
        <i class="chevron fa fa-chevron-right"></i>
        {{ node.name }}
    </button>

    <div id="children-{{ node.id }}" class="tree-children">
        <!-- Loaded on first expand -->
    </div>

    <div class="skeleton-{{ node.id }} htmx-indicator">
        <!-- Skeleton screen while loading -->
    </div>
</div>
```

### When to Use Pure JavaScript

**Best for:**
- ✅ Instant expand/collapse of already-loaded nodes
- ✅ Client-side filtering/searching
- ✅ Drag-and-drop tree reorganization
- ✅ Complex animation sequences
- ✅ Keyboard navigation

**JavaScript Advantages:**
- Zero network latency
- Full control over animations
- Can implement virtual scrolling
- Better for offline functionality

### Hybrid Approach (Recommended)

**Combine both for optimal UX:**

```html
<!-- 1. Server-rendered initial tree (SEO + fast first paint) -->
<div class="tree" id="main-tree">
    {% for node in root_nodes %}
        <div class="tree-node" data-node-id="{{ node.id }}">
            {% if node.has_children %}
                <!-- 2. HTMX for lazy loading deep children -->
                <button
                    class="expand-btn"
                    hx-get="/tree/{{ node.id }}/children/"
                    hx-trigger="click once"
                    hx-target="#children-{{ node.id }}"
                    onclick="toggleChevron(this)"
                >
                    <i class="chevron fa fa-chevron-right"></i>
                    {{ node.name }}
                </button>
            {% endif %}

            <div id="children-{{ node.id }}" class="tree-children collapsed">
                <!-- Lazy loaded via HTMX -->
            </div>
        </div>
    {% endfor %}
</div>

<script>
// 3. JavaScript for instant visual feedback
function toggleChevron(btn) {
    const chevron = btn.querySelector('.chevron');
    const children = btn.nextElementSibling;

    // Instant optimistic UI
    if (children.classList.contains('collapsed')) {
        chevron.style.transform = 'rotate(90deg)';
        children.classList.remove('collapsed');
        children.classList.add('expanded');
    } else {
        chevron.style.transform = 'rotate(0deg)';
        children.classList.add('collapsed');
        children.classList.remove('expanded');
    }
}
</script>
```

---

## 6. Database Query Optimization

### The N+1 Query Problem

**Problem:**
> "The N+1 query problem occurs when code loops over a list of results from one query, and then performs another query per result. This can become a performance problem because each query involves the overhead of communicating with the database server, so the total runtime can be high."

### Django Solutions

#### 1. `select_related()` - For Foreign Keys

```python
# ❌ Bad: N+1 queries
nodes = TreeNode.objects.all()
for node in nodes:
    print(node.parent.name)  # Extra query per node!

# ✅ Good: 1 query with JOIN
nodes = TreeNode.objects.select_related('parent').all()
for node in nodes:
    print(node.parent.name)  # No extra queries
```

#### 2. `prefetch_related()` - For Many-to-Many/Reverse FK

```python
# ❌ Bad: N+1 queries
nodes = TreeNode.objects.all()
for node in nodes:
    children = node.children.all()  # Extra query per node!

# ✅ Good: 2 queries total
nodes = TreeNode.objects.prefetch_related('children').all()
for node in nodes:
    children = node.children.all()  # No extra queries
```

#### 3. Recursive Queries (PostgreSQL/SQLite)

**For deep tree traversal:**

```python
from django.db.models import Q, F

# Get entire subtree efficiently
def get_subtree(root_id):
    return TreeNode.objects.raw("""
        WITH RECURSIVE tree_cte AS (
            -- Base case: root node
            SELECT id, parent_id, name, level = 0
            FROM tree_node
            WHERE id = %s

            UNION ALL

            -- Recursive case: children
            SELECT n.id, n.parent_id, n.name, level = t.level + 1
            FROM tree_node n
            INNER JOIN tree_cte t ON n.parent_id = t.id
        )
        SELECT * FROM tree_cte ORDER BY level, name
    """, [root_id])
```

#### 4. Specialized Libraries

**Django-MPTT (Modified Preorder Tree Traversal):**

```python
from mptt.models import MPTTModel

class TreeNode(MPTTModel):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['name']

# Efficient queries
root.get_descendants()  # All descendants in 1 query
root.get_children()     # Direct children in 1 query
node.get_ancestors()    # Path to root in 1 query
```

**Django-tree-queries (Recursive CTE):**

```python
from tree_queries.models import TreeNode

class Category(TreeNode):
    name = models.CharField(max_length=200)

# Automatic recursive queries
Category.objects.with_tree_fields()  # Adds tree metadata
```

### View Optimization

**Lazy loading endpoint:**

```python
from django.views.generic import ListView
from django.db.models import Prefetch

class TreeChildrenView(ListView):
    model = TreeNode
    template_name = 'tree_children.html'

    def get_queryset(self):
        parent_id = self.kwargs['parent_id']

        return TreeNode.objects.filter(
            parent_id=parent_id
        ).select_related(
            'parent'
        ).prefetch_related(
            Prefetch(
                'children',
                queryset=TreeNode.objects.filter(has_children=True)
            )
        ).annotate(
            child_count=Count('children')
        )
```

### Performance Checklist

- [ ] Use `select_related()` for FK relationships
- [ ] Use `prefetch_related()` for reverse FK/M2M
- [ ] Consider django-mptt for complex tree operations
- [ ] Use recursive CTEs for deep tree traversal
- [ ] Annotate `child_count` to avoid extra queries
- [ ] Index `parent_id` column
- [ ] Add `has_children` boolean field for UI optimization

---

## 7. Caching Strategies

### HTMX Caching

#### 1. Client-Side Caching

```html
<!-- Cache HTMX responses -->
<div
    hx-get="/tree/{{ node.id }}/children/"
    hx-cache="true"
    hx-trigger="click once"
>
    {{ node.name }}
</div>
```

**Benefits:**
> "The hx-cache attribute allows you to cache the response of an HTMX request on the client-side, and when set to 'true', HTMX stores the response in memory and reuses it for the same requests."

#### 2. HTTP Caching

**Server-side caching headers:**

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(60 * 15), name='dispatch')  # 15 minutes
class TreeChildrenView(View):
    def get(self, request, node_id):
        # ...
        response = render(request, 'tree_children.html', context)
        response['Last-Modified'] = node.modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
        response['ETag'] = f'"{node.id}-{node.modified.timestamp()}"'
        return response
```

**HTMX automatically handles:**
> "When your server includes the Last-Modified HTTP response header for a specific URL, the browser will automatically add the If-Modified-Since request header to future requests for that URL, allowing the server to send a 304 Not Modified response if the content hasn't changed."

#### 3. History Caching

**HTMX history caching:**
> "HTMX automatically caches pages in the browser's history, enabling instant back and forward navigation without extra server requests, which you can manage with the hx-history attribute."

```html
<!-- Enable history caching -->
<div hx-boost="true" hx-history="true">
    <!-- Tree navigation cached in history -->
</div>
```

### Django Template Fragment Caching

**Cache static tree sections:**

```django
{% load cache %}

{% cache 3600 tree_static_nodes request.user.id %}
    <div class="tree-static-section">
        {% for node in static_nodes %}
            <!-- Cached for 1 hour per user -->
            <div class="tree-node">{{ node.name }}</div>
        {% endfor %}
    </div>
{% endcache %}
```

**Benefits:**
> "By caching, you avoid unnecessary database queries and template rendering for content that doesn't change frequently. Caching can significantly boost performance by reducing database queries, network round trips, and overall processing time."

### Caching Strategy Matrix

| Data Type | Caching Method | Duration | Key |
|-----------|---------------|----------|-----|
| Static tree structure | Template fragment | 1 hour | `tree_static_{user_id}` |
| User-specific nodes | Template fragment | 15 min | `tree_user_{user_id}` |
| Dynamic children | HTTP cache | 5 min | `tree_children_{node_id}` |
| Expanded state | LocalStorage | Session | `tree_expanded_nodes` |
| Search results | HTMX client cache | 1 min | Auto (URL-based) |

### LocalStorage for UI State

**Persist expanded/collapsed state:**

```javascript
// Save expanded state
function saveTreeState() {
    const expanded = Array.from(
        document.querySelectorAll('.tree-node.expanded')
    ).map(node => node.dataset.nodeId);

    localStorage.setItem('tree_expanded_nodes', JSON.stringify(expanded));
}

// Restore on page load
function restoreTreeState() {
    const expanded = JSON.parse(
        localStorage.getItem('tree_expanded_nodes') || '[]'
    );

    expanded.forEach(nodeId => {
        const node = document.querySelector(`[data-node-id="${nodeId}"]`);
        if (node) {
            node.classList.add('expanded');
            // Trigger HTMX load if needed
            htmx.trigger(node, 'click');
        }
    });
}

// Save on expand/collapse
document.addEventListener('htmx:afterSwap', saveTreeState);
```

---

## 8. Virtual Scrolling for Large Trees

### When to Use Virtual Scrolling

**Indicators you need it:**
- Tree has >1000 visible nodes
- Deep nesting (10+ levels)
- Performance issues with rendering
- Slow scroll performance

### How Virtual Scrolling Works

**Concept:**
> "Virtual scrolling is a technique that only renders the visible items in a list at any given time, rather than rendering the entire list. When users scroll, the visible items are dynamically replaced with new ones, maintaining a small, constant DOM size regardless of the list's actual length."

### Performance Benefits

**Dramatic improvements:**
> "In one project, initial render time was reduced from over 5 seconds to under 100ms for a list with 10,000 items, while maintaining smooth 60fps scrolling."

> "By only rendering a subset of items at a time, the browser has to handle fewer DOM elements, which can greatly reduce the memory and CPU usage of your application."

### Implementation Options

#### 1. Tanstack Virtual (Recommended)

```javascript
import { useVirtualizer } from '@tanstack/react-virtual'

function TreeView({ nodes }) {
    const parentRef = useRef()

    const virtualizer = useVirtualizer({
        count: nodes.length,
        getScrollElement: () => parentRef.current,
        estimateSize: () => 35, // Tree node height
        overscan: 10, // Render 10 extra items
    })

    return (
        <div ref={parentRef} style={{ height: '500px', overflow: 'auto' }}>
            <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
                {virtualizer.getVirtualItems().map(virtualRow => (
                    <div
                        key={virtualRow.key}
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            transform: `translateY(${virtualRow.start}px)`,
                        }}
                    >
                        <TreeNode node={nodes[virtualRow.index]} />
                    </div>
                ))}
            </div>
        </div>
    )
}
```

#### 2. Vanilla JavaScript Virtual Scroll

```javascript
class VirtualTreeScroller {
    constructor(container, items, rowHeight = 35) {
        this.container = container;
        this.items = items;
        this.rowHeight = rowHeight;
        this.visibleStart = 0;
        this.visibleEnd = 0;

        this.init();
    }

    init() {
        // Create scroll container
        this.viewport = this.container.offsetHeight;
        this.visibleCount = Math.ceil(this.viewport / this.rowHeight);

        // Set total height
        this.container.style.height = `${this.items.length * this.rowHeight}px`;

        // Listen to scroll
        this.container.addEventListener('scroll', () => this.render());

        // Initial render
        this.render();
    }

    render() {
        const scrollTop = this.container.scrollTop;
        const start = Math.floor(scrollTop / this.rowHeight);
        const end = start + this.visibleCount + 5; // 5 item buffer

        if (start === this.visibleStart && end === this.visibleEnd) {
            return; // No change
        }

        this.visibleStart = start;
        this.visibleEnd = end;

        // Render only visible items
        const fragment = document.createDocumentFragment();

        for (let i = start; i < end && i < this.items.length; i++) {
            const item = this.items[i];
            const node = this.createTreeNode(item);
            node.style.transform = `translateY(${i * this.rowHeight}px)`;
            fragment.appendChild(node);
        }

        // Clear and append
        this.container.innerHTML = '';
        this.container.appendChild(fragment);
    }

    createTreeNode(item) {
        const div = document.createElement('div');
        div.className = 'tree-node';
        div.innerHTML = `
            <i class="chevron fa fa-chevron-right"></i>
            ${item.name}
        `;
        return div;
    }
}
```

### HTMX + Virtual Scrolling

**Hybrid approach:**

```html
<!-- Initial paginated load -->
<div
    id="tree-container"
    hx-get="/tree/nodes/?page=1"
    hx-trigger="load"
    hx-swap="innerHTML"
>
    Loading...
</div>

<!-- Infinite scroll -->
<div
    hx-get="/tree/nodes/?page=2"
    hx-trigger="intersect once"
    hx-swap="beforeend"
    hx-target="#tree-container"
>
</div>

<script>
// Convert to virtual scroll once loaded
htmx.on('htmx:afterSettle', function() {
    const items = Array.from(document.querySelectorAll('.tree-node'));
    if (items.length > 1000) {
        new VirtualTreeScroller(
            document.getElementById('tree-container'),
            items
        );
    }
});
</script>
```

---

## 9. Progressive Disclosure Patterns

### Definition

**Progressive Disclosure:**
> "Progressive Disclosure defers advanced or rarely used features to a secondary screen, reducing cognitive load on the current task at hand. Progressive disclosure is a technique UX designers use to reduce cognitive load by gradually revealing more complex information or features as the user progresses through a user interface."

### Tree Hierarchy and Progressive Disclosure

**Natural fit:**
> "Tree diagrams help designers visualize the content of their products and ensure one path to each piece of information or setting. Progressive disclosure supports hierarchical organization—information architecture often involves creating a hierarchical information structure, from general to specific, and progressive disclosure aligns with this."

### Common UI Patterns

#### 1. Accordion-Style Expansion

```html
<!-- Progressive disclosure via accordion -->
<div class="tree-accordion">
    <button class="tree-header" onclick="toggleSection(this)">
        <i class="chevron fa fa-chevron-right"></i>
        Projects (12)
    </button>

    <div class="tree-content collapsed">
        <!-- Revealed on click -->
        <div class="tree-node">Project A</div>
        <div class="tree-node">Project B</div>
    </div>
</div>
```

#### 2. Lazy Loading as Progressive Disclosure

**Pattern:**
> "Lazy loading is an extremely useful technique when you have a lot of information to display and want to reduce interaction cost. Scrolling provides a more comfortable experience than clicking—all the user needs to do to get new content is simply scroll down."

```html
<!-- Load more on scroll -->
<div
    class="tree-section"
    hx-get="/tree/more/?level=2"
    hx-trigger="intersect once threshold:0.5"
    hx-swap="afterend"
>
    <div class="tree-node">...</div>
</div>

<!-- Placeholder for next batch -->
<div class="load-more-indicator">
    <i class="fa fa-spinner fa-spin"></i> Loading more...
</div>
```

#### 3. Depth-Based Progressive Loading

**Strategy: Load only 2-3 levels initially**

```python
# View: Progressive depth loading
def get_tree_nodes(request):
    max_depth = int(request.GET.get('max_depth', 2))

    nodes = TreeNode.objects.filter(
        level__lte=max_depth
    ).select_related('parent').prefetch_related(
        Prefetch(
            'children',
            queryset=TreeNode.objects.filter(level__lte=max_depth + 1)
        )
    )

    return render(request, 'tree_progressive.html', {
        'nodes': nodes,
        'max_depth': max_depth
    })
```

```django
<!-- Template: Progressive depth -->
{% for node in nodes %}
    <div class="tree-node" data-level="{{ node.level }}">
        {{ node.name }}

        {% if node.level < max_depth %}
            <!-- Children visible -->
            <div class="tree-children">
                {% for child in node.children.all %}
                    <!-- Recursive include -->
                {% endfor %}
            </div>
        {% else %}
            <!-- Load on demand -->
            <button
                hx-get="/tree/{{ node.id }}/children/?max_depth={{ max_depth|add:1 }}"
                hx-target="next .tree-children"
            >
                <i class="fa fa-plus"></i> Load more
            </button>
            <div class="tree-children"></div>
        {% endif %}
    </div>
{% endfor %}
```

### Benefits

1. **Reduced Initial Load:** Only essential data loaded first
2. **Lower Cognitive Load:** Users see manageable information chunks
3. **Better Performance:** Fewer DOM nodes, faster rendering
4. **Improved Usability:** Users discover content at their own pace

---

## 10. HTMX-Specific Optimizations

### Out-of-Band Swaps

**Update multiple tree sections with one request:**

**Scenario:** Updating a node affects counters, breadcrumbs, and sibling nodes

```python
# Django view
def update_tree_node(request, node_id):
    node = TreeNode.objects.get(id=node_id)
    node.name = request.POST.get('name')
    node.save()

    # Update parent's child count
    parent = node.parent
    parent.child_count = parent.children.count()

    return render(request, 'tree_update.html', {
        'node': node,
        'parent': parent,
        'siblings': node.parent.children.all() if parent else []
    })
```

```django
<!-- Template: Multiple updates -->
<!-- Main target: Updated node -->
<div id="node-{{ node.id }}" class="tree-node">
    {{ node.name }}
</div>

<!-- Out-of-band: Update parent counter -->
<div
    id="parent-count-{{ parent.id }}"
    hx-swap-oob="true"
    class="child-count"
>
    {{ parent.child_count }} children
</div>

<!-- Out-of-band: Update breadcrumb -->
<div
    id="breadcrumb"
    hx-swap-oob="true"
>
    {% for ancestor in node.get_ancestors %}
        {{ ancestor.name }} /
    {% endfor %}
    {{ node.name }}
</div>
```

**Benefits:**
> "While using events works fine, two requests are done to the server, but using out of band swaps, you can return both HTML snippets using the same call and have htmx update both divs at the client."

**Trade-offs:**
> "OOB swaps can be tricky to debug, so it's recommended to start with hidden listeners and graduate to this when you need the performance boost."

### Trigger Optimization

**Debounce search/filter:**

```html
<!-- Search with debounce -->
<input
    type="text"
    name="search"
    hx-get="/tree/search/"
    hx-trigger="keyup changed delay:300ms"
    hx-target="#tree-results"
    placeholder="Search tree..."
/>
```

**Load once pattern:**

```html
<!-- Load children only once -->
<button
    hx-get="/tree/{{ node.id }}/children/"
    hx-trigger="click once"
    hx-target="#children-{{ node.id }}"
>
    Expand
</button>
```

**Intersect for lazy loading:**

```html
<!-- Load when scrolled into view -->
<div
    hx-get="/tree/{{ node.id }}/children/"
    hx-trigger="intersect once threshold:0.5"
    hx-target="this"
    hx-swap="outerHTML"
>
    <div class="skeleton">Loading...</div>
</div>
```

### Request Queuing

**Prevent race conditions:**

```html
<!-- Queue requests (process sequentially) -->
<div
    hx-get="/tree/update/"
    hx-sync="this:queue"
>
    <!-- Requests queued, not parallel -->
</div>

<!-- Replace previous (cancel pending) -->
<div
    hx-get="/tree/search/"
    hx-sync="this:replace"
>
    <!-- Only latest request executes -->
</div>
```

### Indicator Strategy

**Targeted loading indicators:**

```html
<div class="tree-node">
    <button
        hx-get="/tree/{{ node.id }}/children/"
        hx-indicator="#loading-{{ node.id }}"
    >
        {{ node.name }}
    </button>

    <!-- Custom indicator -->
    <div id="loading-{{ node.id }}" class="htmx-indicator">
        <div class="skeleton-tree-item"></div>
        <div class="skeleton-tree-item"></div>
    </div>

    <div id="children-{{ node.id }}"></div>
</div>
```

---

## 11. Implementation Patterns

### Pattern 1: Optimistic Expand with Lazy Load

**Best for: Large trees with unknown children**

```html
<div class="tree-node" data-node-id="{{ node.id }}">
    <button
        class="expand-btn"
        hx-get="/tree/{{ node.id }}/children/"
        hx-trigger="click once"
        hx-target="#children-{{ node.id }}"
        hx-swap="innerHTML show:none swap:200ms"
        hx-indicator="#skeleton-{{ node.id }}"
        onclick="optimisticExpand(this)"
    >
        <i class="chevron fa fa-chevron-right transition-transform duration-150"></i>
        <span>{{ node.name }}</span>
    </button>

    <!-- Skeleton (shows if load >300ms) -->
    <div id="skeleton-{{ node.id }}" class="htmx-indicator">
        <div class="skeleton-item"></div>
    </div>

    <!-- Children container -->
    <div id="children-{{ node.id }}" class="tree-children collapsed"></div>
</div>

<script>
function optimisticExpand(btn) {
    const chevron = btn.querySelector('.chevron');
    const children = btn.parentElement.querySelector('.tree-children');

    // Instant visual feedback (<50ms)
    chevron.style.transform = 'rotate(90deg)';
    children.classList.remove('collapsed');
    children.classList.add('expanding');

    // Error handling
    btn.addEventListener('htmx:responseError', function() {
        // Revert optimistic changes
        chevron.style.transform = 'rotate(0deg)';
        children.classList.add('collapsed');
        children.classList.remove('expanding');
    }, { once: true });
}
</script>

<style>
.tree-children.collapsed {
    display: none;
}

.tree-children.expanding {
    display: block;
    opacity: 0;
    animation: fadeIn 200ms ease forwards;
}

@keyframes fadeIn {
    to { opacity: 1; }
}

.skeleton-item {
    height: 32px;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
</style>
```

### Pattern 2: Progressive Depth Loading

**Best for: Known tree structure, controlled depth**

```python
# views.py
class TreeView(View):
    def get(self, request):
        max_depth = int(request.GET.get('depth', 2))

        nodes = TreeNode.objects.filter(
            level__lte=max_depth
        ).select_related('parent').prefetch_related(
            Prefetch(
                'children',
                queryset=TreeNode.objects.filter(level__lte=max_depth)
            )
        )

        return render(request, 'tree.html', {
            'nodes': nodes,
            'max_depth': max_depth
        })
```

```django
<!-- tree.html -->
{% load tree_tags %}

{% for node in root_nodes %}
    {% tree_node node max_depth %}
{% endfor %}

<!-- tree_node.html template tag -->
<div class="tree-node" data-level="{{ node.level }}">
    {% if node.children.exists %}
        <button onclick="toggleNode(this)">
            <i class="chevron fa fa-chevron-right"></i>
            {{ node.name }}
        </button>

        <div class="tree-children">
            {% if node.level < max_depth %}
                <!-- Render children -->
                {% for child in node.children.all %}
                    {% tree_node child max_depth %}
                {% endfor %}
            {% else %}
                <!-- Lazy load deeper levels -->
                <button
                    hx-get="{% url 'tree:children' node.id %}?depth={{ max_depth|add:2 }}"
                    hx-target="closest .tree-children"
                    hx-swap="innerHTML"
                    class="load-more-btn"
                >
                    <i class="fa fa-ellipsis-h"></i> Load more
                </button>
            {% endif %}
        </div>
    {% else %}
        <div class="tree-leaf">{{ node.name }}</div>
    {% endif %}
</div>
```

### Pattern 3: Search with Highlighting

**Best for: Searchable trees**

```html
<!-- Search input -->
<div class="tree-search">
    <input
        type="text"
        name="q"
        hx-get="/tree/search/"
        hx-trigger="keyup changed delay:300ms"
        hx-target="#tree-results"
        hx-indicator="#search-spinner"
        hx-sync="this:replace"
        placeholder="Search tree..."
    />
    <i id="search-spinner" class="fa fa-spinner fa-spin htmx-indicator"></i>
</div>

<!-- Results -->
<div id="tree-results">
    <!-- Search results loaded here -->
</div>
```

```python
# views.py
def tree_search(request):
    query = request.GET.get('q', '')

    if len(query) < 2:
        return HttpResponse('')  # Empty response

    # Search with path
    results = TreeNode.objects.filter(
        name__icontains=query
    ).select_related('parent').prefetch_related(
        'children'
    ).annotate(
        path=StringAgg('ancestors__name', delimiter=' > ')
    )[:20]  # Limit results

    return render(request, 'tree_search_results.html', {
        'results': results,
        'query': query
    })
```

```django
<!-- tree_search_results.html -->
{% for result in results %}
    <div class="search-result">
        <!-- Breadcrumb path -->
        <div class="result-path text-sm text-gray-500">
            {{ result.path }}
        </div>

        <!-- Highlighted result -->
        <div class="result-name">
            {{ result.name|highlight:query }}
        </div>

        <!-- Quick expand -->
        <button
            hx-get="/tree/{{ result.id }}/expand/"
            hx-target="#tree-container"
            hx-swap="innerHTML"
            class="btn-expand"
        >
            Show in tree
        </button>
    </div>
{% empty %}
    <div class="no-results">No results found</div>
{% endfor %}
```

### Pattern 4: Drag & Drop Reordering

**Best for: Reorganizable trees**

```html
<div class="tree-node draggable" draggable="true" data-node-id="{{ node.id }}">
    <div
        class="drop-zone"
        ondragover="allowDrop(event)"
        ondrop="handleDrop(event, {{ node.id }})"
    >
        <i class="drag-handle fa fa-grip-vertical"></i>
        {{ node.name }}
    </div>
</div>

<script>
function allowDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}

function handleDrop(event, targetId) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');

    const sourceId = event.dataTransfer.getData('nodeId');

    // Optimistic UI: Move immediately
    const sourceNode = document.querySelector(`[data-node-id="${sourceId}"]`);
    const targetNode = event.currentTarget.closest('.tree-node');
    targetNode.querySelector('.tree-children').appendChild(sourceNode);

    // HTMX update
    htmx.ajax('POST', '/tree/move/', {
        values: { source: sourceId, target: targetId },
        swap: 'none'
    }).then(response => {
        // Success
        showToast('Node moved successfully');
    }).catch(error => {
        // Revert on error
        location.reload();  // Or implement proper revert
    });
}

document.querySelectorAll('.draggable').forEach(node => {
    node.addEventListener('dragstart', function(e) {
        e.dataTransfer.setData('nodeId', this.dataset.nodeId);
        this.classList.add('dragging');
    });

    node.addEventListener('dragend', function(e) {
        this.classList.remove('dragging');
        document.querySelectorAll('.drag-over').forEach(el => {
            el.classList.remove('drag-over');
        });
    });
});
</script>
```

---

## 12. Trade-offs & Decision Matrix

### Loading Strategy Trade-offs

| Strategy | Pros | Cons | Best For |
|----------|------|------|----------|
| **Server-render all** | SEO friendly, fast first paint | Slow for large trees, large HTML | Small trees (<100 nodes) |
| **Lazy load all** | Fast initial load, scalable | SEO challenges, multiple requests | Large trees (>1000 nodes) |
| **Progressive depth** | Balanced, predictable | Complex logic | Medium trees (100-1000 nodes) |
| **Virtual scrolling** | Handles any size, consistent performance | Complex implementation, no SEO | Very large trees (>5000 nodes) |
| **Hybrid** | Best of all worlds | Most complex | Production applications |

### Animation Trade-offs

| Approach | Performance | Browser Support | Complexity | Recommendation |
|----------|------------|----------------|------------|----------------|
| `transform: scaleY()` | ✅ Excellent | ✅ Universal | ⚠️ Medium (counter-transform) | **Recommended** |
| `height: auto` animation | ❌ Poor (triggers layout) | ⚠️ Limited (Chrome 129+) | ✅ Simple | Avoid (unless modern browsers only) |
| `max-height` hack | ⚠️ OK | ✅ Universal | ✅ Simple | Quick prototype only |
| JavaScript animation | ✅ Good (requestAnimationFrame) | ✅ Universal | ⚠️ Medium | When you need fine control |

### Caching Trade-offs

| Strategy | Performance Gain | Complexity | Invalidation | Use Case |
|----------|-----------------|------------|--------------|----------|
| **HTMX client cache** | High (instant repeat requests) | Low | Simple (time-based) | Static content |
| **HTTP cache (304)** | Medium (reduced bandwidth) | Low | Conditional (Last-Modified) | Semi-static content |
| **Template fragment** | High (no DB queries) | Medium | Manual | User-specific trees |
| **LocalStorage state** | Very High (instant restore) | Medium | Manual | UI state only |
| **Redis cache** | Very High (shared cache) | High | Complex (events) | Production systems |

### HTMX vs JavaScript Decision Matrix

| Scenario | Use HTMX | Use JavaScript | Hybrid |
|----------|----------|---------------|--------|
| Lazy load children from server | ✅ | ❌ | ✅ (HTMX load, JS animation) |
| Expand/collapse already loaded | ❌ | ✅ | ❌ |
| Search/filter server-side | ✅ | ❌ | ✅ (HTMX search, JS highlight) |
| Search/filter client-side | ❌ | ✅ | ❌ |
| Drag & drop | ❌ | ✅ | ✅ (JS interaction, HTMX save) |
| Keyboard navigation | ❌ | ✅ | ❌ |
| Update multiple sections | ✅ (OOB swaps) | ⚠️ | ✅ |
| Offline functionality | ❌ | ✅ | ⚠️ |

---

## 13. Recommended Implementation Checklist

### Phase 1: Foundation (CRITICAL)

- [ ] **Optimize database queries**
  - [ ] Add `select_related()` for parent FK
  - [ ] Add `prefetch_related()` for children
  - [ ] Index `parent_id` column
  - [ ] Annotate `child_count` to avoid N+1

- [ ] **Implement optimistic UI**
  - [ ] Instant chevron rotation (<50ms)
  - [ ] Instant expand/collapse visual feedback
  - [ ] Error handling with rollback

- [ ] **Add loading states**
  - [ ] Skeleton screens for >300ms loads
  - [ ] Custom indicators per node
  - [ ] Smooth transitions (200-300ms)

### Phase 2: Performance (HIGH)

- [ ] **Lazy loading**
  - [ ] HTMX `hx-trigger="click once"` for children
  - [ ] Progressive depth loading (2-3 levels initial)
  - [ ] Intersection observer for viewport loading

- [ ] **Caching strategy**
  - [ ] HTTP cache headers (Last-Modified, ETag)
  - [ ] Template fragment caching for static sections
  - [ ] LocalStorage for expanded state persistence

- [ ] **Animation optimization**
  - [ ] Use `transform: scaleY()` (not `height`)
  - [ ] 100-150ms for microinteractions
  - [ ] 200-300ms for expand/collapse

### Phase 3: Enhancement (MEDIUM)

- [ ] **Search & filter**
  - [ ] Debounced search (300ms delay)
  - [ ] Client-side highlight
  - [ ] Path breadcrumbs in results

- [ ] **Progressive disclosure**
  - [ ] "Load more" for deep levels
  - [ ] Expand/collapse all controls
  - [ ] Depth limit configuration

- [ ] **State management**
  - [ ] Save expanded nodes to LocalStorage
  - [ ] Restore state on page load
  - [ ] Sync state across tabs (BroadcastChannel)

### Phase 4: Advanced (LOW)

- [ ] **Virtual scrolling** (only if >1000 nodes)
  - [ ] Implement virtual scroller
  - [ ] Dynamic row heights
  - [ ] Keyboard navigation

- [ ] **Drag & drop** (if needed)
  - [ ] Optimistic reorder
  - [ ] HTMX save
  - [ ] Validation & rollback

- [ ] **Real-time updates** (if needed)
  - [ ] WebSocket connection
  - [ ] Out-of-band swaps for live updates
  - [ ] Conflict resolution

---

## 14. Key Takeaways

### 1. Perceived Performance > Actual Performance

**Most Important Finding:**
> "Under 100ms, users don't notice the wait; over 200ms, they start to feel it. Users perceive sites with skeleton screens as 30% faster than identical sites with spinners, despite identical actual loading times."

**Action:** Prioritize instant UI feedback (<50ms) and skeleton screens over actual load time optimization.

### 2. Optimistic UI is Non-Negotiable

**Critical Pattern:**
- Update UI immediately on user interaction
- Handle server response in background
- Revert only on error
- Users expect modern app behavior

### 3. Database Optimization is Foundation

**N+1 queries kill performance:**
- Always use `select_related()` and `prefetch_related()`
- Consider django-mptt for complex trees
- Index properly (`parent_id`, `level`)
- Annotate counts to avoid extra queries

### 4. HTMX + JavaScript Hybrid is Best

**Don't choose one:**
- HTMX for server interactions (lazy load, search)
- JavaScript for instant UI (expand/collapse, animations)
- Combine both for optimal UX

### 5. Animation Performance Matters

**Use GPU-accelerated properties:**
- ✅ `transform` and `opacity`
- ❌ `height`, `width`, `margin`, `padding`
- Use `transform: scaleY()` with counter-transforms
- Duration: 100-150ms (micro), 200-300ms (transitions)

### 6. Progressive Disclosure is Natural for Trees

**Load what's needed, when needed:**
- Initial: 2-3 levels max
- On demand: Lazy load deeper levels
- On scroll: Infinite scroll for large lists
- On search: Show relevant paths only

### 7. Caching is Multi-Layered

**Implement caching at every level:**
1. Browser cache (HTTP headers)
2. HTMX client cache (repeat requests)
3. Django template fragments (static sections)
4. LocalStorage (UI state)
5. Redis/Memcached (server-side)

### 8. Virtual Scrolling Only When Needed

**Don't over-engineer:**
- <1000 nodes: Regular rendering is fine
- 1000-5000 nodes: Consider virtual scrolling
- >5000 nodes: Virtual scrolling essential
- Adds complexity, use only when necessary

### 9. Error Handling is Critical

**Optimistic UI requires robust error handling:**
- Always implement rollback mechanism
- Show clear error messages
- Provide recovery options
- Log errors for debugging

### 10. Test on Real Devices

**Performance feels different on mobile:**
- Test on actual mobile devices, not just Chrome DevTools
- Consider slow 3G/4G networks
- Account for 300ms tap delay on mobile
- Ensure touch targets are adequate (48px minimum)

---

## 15. Code Examples Summary

### Complete HTMX Tree Implementation

```python
# models.py
from django.db import models
from django.db.models import Count

class TreeNode(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    level = models.IntegerField(default=0)
    has_children = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['parent', 'level']),
        ]

    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
        super().save(*args, **kwargs)

        # Update parent's has_children
        if self.parent:
            self.parent.has_children = True
            self.parent.save(update_fields=['has_children'])
```

```python
# views.py
from django.views.generic import ListView, View
from django.shortcuts import render
from django.db.models import Prefetch

class TreeView(ListView):
    model = TreeNode
    template_name = 'tree/index.html'
    context_object_name = 'nodes'

    def get_queryset(self):
        max_depth = 2  # Load 2 levels initially

        return TreeNode.objects.filter(
            parent__isnull=True  # Root nodes
        ).select_related('parent').prefetch_related(
            Prefetch(
                'children',
                queryset=TreeNode.objects.filter(
                    level__lte=max_depth
                ).select_related('parent')
            )
        ).annotate(
            child_count=Count('children')
        )

class TreeChildrenView(View):
    def get(self, request, node_id):
        node = TreeNode.objects.get(id=node_id)

        children = node.children.select_related(
            'parent'
        ).prefetch_related('children').annotate(
            child_count=Count('children')
        )

        return render(request, 'tree/children.html', {
            'children': children
        })
```

```django
<!-- tree/index.html -->
{% load static %}

<div class="tree-container">
    {% for node in nodes %}
        {% include 'tree/node.html' with node=node %}
    {% endfor %}
</div>

<!-- tree/node.html -->
<div class="tree-node" data-node-id="{{ node.id }}">
    {% if node.has_children %}
        <button
            class="expand-btn"
            hx-get="{% url 'tree:children' node.id %}"
            hx-trigger="click once"
            hx-target="#children-{{ node.id }}"
            hx-swap="innerHTML show:none swap:200ms"
            hx-indicator="#skeleton-{{ node.id }}"
            onclick="optimisticExpand(this)"
        >
            <i class="chevron fa fa-chevron-right"></i>
            {{ node.name }}
            {% if node.child_count %}
                <span class="count">({{ node.child_count }})</span>
            {% endif %}
        </button>

        <div id="skeleton-{{ node.id }}" class="htmx-indicator">
            <div class="skeleton-item"></div>
        </div>

        <div id="children-{{ node.id }}" class="tree-children collapsed"></div>
    {% else %}
        <div class="tree-leaf">
            <i class="fa fa-file"></i>
            {{ node.name }}
        </div>
    {% endif %}
</div>

<!-- tree/children.html -->
{% for child in children %}
    {% include 'tree/node.html' with node=child %}
{% endfor %}
```

```javascript
// tree.js - Optimistic UI
function optimisticExpand(btn) {
    const chevron = btn.querySelector('.chevron');
    const nodeDiv = btn.closest('.tree-node');
    const children = nodeDiv.querySelector('.tree-children');

    // Check if already expanded
    if (nodeDiv.classList.contains('expanded')) {
        // Collapse
        chevron.style.transform = 'rotate(0deg)';
        children.classList.add('collapsed');
        nodeDiv.classList.remove('expanded');
        return;
    }

    // Expand (optimistic)
    chevron.style.transform = 'rotate(90deg)';
    children.classList.remove('collapsed');
    nodeDiv.classList.add('expanded');

    // Error handling
    btn.addEventListener('htmx:responseError', function() {
        chevron.style.transform = 'rotate(0deg)';
        children.classList.add('collapsed');
        nodeDiv.classList.remove('expanded');
        alert('Failed to load children');
    }, { once: true });
}

// Save/restore state
function saveTreeState() {
    const expanded = Array.from(
        document.querySelectorAll('.tree-node.expanded')
    ).map(node => node.dataset.nodeId);

    localStorage.setItem('tree_expanded', JSON.stringify(expanded));
}

function restoreTreeState() {
    const expanded = JSON.parse(
        localStorage.getItem('tree_expanded') || '[]'
    );

    expanded.forEach(nodeId => {
        const node = document.querySelector(`[data-node-id="${nodeId}"]`);
        if (node) {
            const btn = node.querySelector('.expand-btn');
            if (btn) btn.click();
        }
    });
}

// Auto-save on changes
document.addEventListener('htmx:afterSwap', saveTreeState);

// Restore on load
document.addEventListener('DOMContentLoaded', restoreTreeState);
```

```css
/* tree.css - Performant animations */
.chevron {
    transition: transform 0.15s ease;
}

.tree-node.expanded .chevron {
    transform: rotate(90deg);
}

.tree-children {
    transform-origin: top;
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1),
                opacity 0.25s ease;
}

.tree-children.collapsed {
    transform: scaleY(0);
    opacity: 0;
    height: 0;
    overflow: hidden;
}

.tree-children.expanded {
    transform: scaleY(1);
    opacity: 1;
}

/* Skeleton screen */
.skeleton-item {
    height: 32px;
    margin: 4px 0;
    background: linear-gradient(
        90deg,
        #f0f0f0 25%,
        #e0e0e0 50%,
        #f0f0f0 75%
    );
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
    border-radius: 4px;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* HTMX indicator */
.htmx-indicator {
    display: none;
}

.htmx-request .htmx-indicator {
    display: block;
}

/* Hover effects */
.tree-node {
    transition: background-color 0.15s ease;
}

.tree-node:hover {
    background-color: rgba(0, 0, 0, 0.05);
}

.expand-btn {
    cursor: pointer;
    background: none;
    border: none;
    padding: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    text-align: left;
}

.expand-btn:active {
    background-color: rgba(0, 0, 0, 0.1);
}
```

---

## 16. Additional Resources

### Documentation
- [HTMX Official Docs](https://htmx.org/docs/)
- [Django Query Optimization](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
- [Web Performance MDN](https://developer.mozilla.org/en-US/docs/Web/Performance)
- [Nielsen Norman Group - Response Times](https://www.nngroup.com/articles/response-times-3-important-limits/)

### Libraries
- **django-mptt**: Modified Preorder Tree Traversal for Django
- **django-tree-queries**: Recursive CTE for adjacency-list trees
- **Tanstack Virtual**: Virtual scrolling for large lists
- **HTMX**: High-power tools for HTML

### Tools
- **Django Debug Toolbar**: SQL query analysis
- **Chrome DevTools**: Performance profiling
- **Lighthouse**: Web performance auditing
- **WebPageTest**: Real-world performance testing

---

## Conclusion

Creating fast, smooth tree UI interactions is about **perceived performance**, not just actual speed. The research shows that:

1. **Sub-100ms feels instant** - This is your target for UI feedback
2. **Skeleton screens beat spinners** by 20-30% in perceived performance
3. **Optimistic UI is essential** for modern web apps
4. **Database optimization is the foundation** - Fix N+1 queries first
5. **HTMX + JavaScript hybrid** provides the best user experience
6. **Animation performance matters** - Use GPU-accelerated properties
7. **Progressive disclosure is natural** for hierarchical data

**Start simple, measure, then optimize.** Don't implement virtual scrolling if you have 50 nodes. Don't use complex caching if your tree loads in 50ms. But do implement optimistic UI, skeleton screens, and proper database queries from day one.

The goal: **Users should feel like they're manipulating a local application, not waiting for a server.**

---

*Research compiled: 2025-10-06*
*Based on: Nielsen Norman Group, MDN Web Docs, HTMX documentation, and modern web performance best practices*
