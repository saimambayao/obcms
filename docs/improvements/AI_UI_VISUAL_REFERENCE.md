# AI UI Visual Reference Guide

**Visual examples of all AI components integrated into OBCMS**

---

## 1. AI Chat Widget (Base Template)

### Location
Fixed bottom-right corner on all authenticated pages

### Visual Design
```
┌─────────────────────────────────────────────────────┐
│                                            [Widget]  │
│                                              ┌───┐  │
│                                              │ 💬 │  │ ← Floating button
│                                              └───┘  │   (emerald/teal gradient)
└─────────────────────────────────────────────────────┘
```

### Expanded State
```
┌───────────────────────────────────────────────────────────────┐
│                                                     ┌────────┐│
│                                                     │        ││
│  ┌──────────────────────────────────────────────┐  │        ││
│  │ 🤖 AI Assistant [Beta]                    ✕ │  │        ││ ← Header
│  │ Ask me anything about OBCMS data             │  │        ││   (emerald/teal)
│  ├──────────────────────────────────────────────┤  │        ││
│  │                                              │  │        ││
│  │ 🤖 Hello! I can help you with:              │  │        ││
│  │    ✓ Finding community data                 │  │        ││ ← Welcome msg
│  │    ✓ Analyzing assessments                  │  │        ││
│  │    ✓ Generating reports                     │  │        ││
│  │    ✓ Answering questions                    │  │        ││
│  │                                              │  │        ││
│  │                                              │  │ Chat   ││
│  │ [User messages and AI responses here]       │  │ Area   ││
│  │                                              │  │        ││
│  ├──────────────────────────────────────────────┤  │        ││
│  │ [Type your question...          ] [➤]       │  │        ││ ← Input
│  └──────────────────────────────────────────────┘  └────────┘│
└───────────────────────────────────────────────────────────────┘
```

### Color Scheme
- **Header:** `bg-gradient-to-r from-emerald-500 to-teal-600`
- **Button:** `bg-gradient-to-br from-emerald-500 to-teal-600`
- **User Messages:** `bg-blue-100`
- **AI Messages:** `bg-emerald-50 border border-emerald-200`

---

## 2. Dashboard AI Showcase

### Location
Between hero section and system overview on main dashboard

### Visual Design
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🤖 AI-Powered Insights                                        [NEW] │
│ Intelligent analysis across all modules                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│ │ 👥 Communities │  │ 📋 MANA AI    │  │ 🤝 Coordination│        │
│ │ AI             │  │               │  │ AI             │        │
│ │                │  │ Response      │  │                │        │
│ │ Similar        │  │ analysis,     │  │ Stakeholder    │        │
│ │ communities,   │  │ report        │  │ matching,      │        │
│ │ needs...       │  │ generation... │  │ partnerships...│        │
│ │                │  │               │  │                │        │
│ │ Explore →      │  │ Explore →     │  │ Explore →      │        │
│ └────────────────┘  └────────────────┘  └────────────────┘        │
│                                                                      │
│ ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│ │ ⚖️ Policy AI   │  │ 📊 M&E AI     │  │ 🔍 Semantic    │        │
│ │                │  │               │  │ Search         │        │
│ │ Evidence       │  │ Anomaly       │  │                │        │
│ │ gathering,     │  │ detection,    │  │ Natural        │        │
│ │ compliance...  │  │ forecasting...│  │ language...    │        │
│ │                │  │               │  │                │        │
│ │ Explore →      │  │ Explore →     │  │ Try AI Chat →  │        │
│ └────────────────┘  └────────────────┘  └────────────────┘        │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│ ℹ️ AI features are available across all detail pages               │
│                                           [Open AI Chat Button]     │
└─────────────────────────────────────────────────────────────────────┘
```

### Hover State
- **Border:** Changes from `border-gray-200` to `border-emerald-300`
- **Shadow:** Adds `shadow-md`
- **Arrow:** Slides right with `transform translate-x-1`

---

## 3. Module AI Insights Panel (Generic)

### Location
Bottom of detail pages (after main content)

### Visual Design
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🧠 AI Insights for This [Object]                  [Powered by AI]   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌─────────────────────────────┐  ┌─────────────────────────────┐  │
│ │ 💬 Feature 1                │  │ 🏷️ Feature 2               │  │
│ ├─────────────────────────────┤  ├─────────────────────────────┤  │
│ │                             │  │                             │  │
│ │ [AI Analysis Results]       │  │ [AI Analysis Results]       │  │
│ │                             │  │                             │  │
│ │ Confidence: 85%             │  │ Key Themes:                 │  │
│ │ ████████████░░░░             │  │ • Theme 1 • Theme 2         │  │
│ │                             │  │                             │  │
│ └─────────────────────────────┘  └─────────────────────────────┘  │
│                                                                      │
│ ┌─────────────────────────────┐  ┌─────────────────────────────┐  │
│ │ 🕌 Feature 3                │  │ 🔗 Feature 4                │  │
│ ├─────────────────────────────┤  ├─────────────────────────────┤  │
│ │ [AI Analysis Results]       │  │ [AI Analysis Results]       │  │
│ └─────────────────────────────┘  └─────────────────────────────┘  │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│          [📄 Generate Comprehensive AI Report Button]               │
└─────────────────────────────────────────────────────────────────────┘
```

### Loading State
```
┌─────────────────────────────────────────────────────────────────────┐
│ 💬 Feature Name                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                          ⟳ Loading AI insights...                   │ ← Spinner
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Report Success State
```
┌─────────────────────────────────────────────────────────────────────┐
│ ✓ Report generated successfully!                                    │
│   📥 Download Report                                                │
└─────────────────────────────────────────────────────────────────────┘
```

### Error State
```
┌─────────────────────────────────────────────────────────────────────┐
│ ⚠️ AI service temporarily unavailable. Please try again later.     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. MANA Module AI Features

### Specific Features
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🧠 AI Insights for This Assessment              [Powered by AI]     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌─────────────────────────────┐  ┌─────────────────────────────┐  │
│ │ 💬 Response Analysis        │  │ 🏷️ Key Themes              │  │
│ ├─────────────────────────────┤  ├─────────────────────────────┤  │
│ │ Sentiment Score: 0.75       │  │ Infrastructure, Education,  │  │
│ │ ███████████████░░            │  │ Healthcare, Agriculture     │  │
│ │                             │  │                             │  │
│ │ 45 Positive  23 Neutral     │  │ Frequency:                  │  │
│ │ 12 Negative                 │  │ • Infra (34) • Edu (28)     │  │
│ └─────────────────────────────┘  └─────────────────────────────┘  │
│                                                                      │
│ ┌─────────────────────────────┐  ┌─────────────────────────────┐  │
│ │ 🕌 Cultural Validation      │  │ 🔗 Similar Assessments      │  │
│ ├─────────────────────────────┤  ├─────────────────────────────┤  │
│ │ ✓ Culturally appropriate    │  │ • Assessment A (92% match)  │  │
│ │ ✓ Language sensitivity OK   │  │ • Assessment B (87% match)  │  │
│ │ ⚠️ Consider local customs   │  │ • Assessment C (81% match)  │  │
│ └─────────────────────────────┘  └─────────────────────────────┘  │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│    [📄 Generate Comprehensive AI Assessment Report]                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Communities Module AI Features

### Specific Features
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🧠 AI Community Insights                         [Powered by AI]    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌─────────────────────────────┐  ┌─────────────────────────────┐  │
│ │ 👥 Similar Communities      │  │ 📋 Needs Classification     │  │
│ ├─────────────────────────────┤  ├─────────────────────────────┤  │
│ │ • Community A (94% match)   │  │ Primary: Infrastructure     │  │
│ │   Zamboanga Peninsula       │  │ Secondary: Education        │  │
│ │                             │  │ Urgent: Healthcare          │  │
│ │ • Community B (89% match)   │  │                             │  │
│ │   Northern Mindanao         │  │ Confidence: 87%             │  │
│ └─────────────────────────────┘  └─────────────────────────────┘  │
│                                                                      │
│ ┌─────────────────────────────┐  ┌─────────────────────────────┐  │
│ │ ✓ Data Quality Score        │  │ 💡 Quick Insights           │  │
│ ├─────────────────────────────┤  ├─────────────────────────────┤  │
│ │ Overall: 92/100             │  │ • Growing population        │  │
│ │ ████████████████████░        │  │ • Infrastructure gaps       │  │
│ │                             │  │ • Strong community ties     │  │
│ │ ✓ Complete   ⚠️ Missing:    │  │ • Youth engagement needed   │  │
│ │   Contact info              │  │                             │  │
│ └─────────────────────────────┘  └─────────────────────────────┘  │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│         [📄 Generate AI Community Profile Report]                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Coordination Module AI Features

### Specific Features
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🧠 AI Coordination Insights                      [Powered by AI]    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌─────────────────────────────┐  ┌─────────────────────────────┐  │
│ │ 👥 Recommended Stakeholders │  │ 🤝 Partnership Opportunities │  │
│ ├─────────────────────────────┤  ├─────────────────────────────┤  │
│ │ • DSWD Region IX            │  │ • MOA Partnership (High)    │  │
│ │   Match: 94%                │  │   Shared goals: Education   │  │
│ │   Reason: Education focus   │  │                             │  │
│ │                             │  │ • LGU Partnership (Med)     │  │
│ │ • NGO Mindanao              │  │   Shared goals: Livelihood  │  │
│ │   Match: 87%                │  │                             │  │
│ └─────────────────────────────┘  └─────────────────────────────┘  │
│                                                                      │
│ ┌─────────────────────────────┐  ┌─────────────────────────────┐  │
│ │ 📅 Meeting Intelligence     │  │ 📊 Resource Recommendations │  │
│ ├─────────────────────────────┤  ├─────────────────────────────┤  │
│ │ Last 5 meetings:            │  │ Optimal allocation:         │  │
│ │ • 80% attendance rate       │  │ • Personnel: 3 staff        │  │
│ │ • Avg duration: 2.5 hrs     │  │ • Budget: ₱150,000         │  │
│ │ • Action items: 85% done    │  │ • Timeline: 3 months        │  │
│ └─────────────────────────────┘  └─────────────────────────────┘  │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│        [📄 Generate Coordination Strategy Report]                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 7. Policy Module AI Features

### Specific Features
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🧠 AI Policy Insights                            [Powered by AI]    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌─────────────────────────────┐  ┌─────────────────────────────┐  │
│ │ 🔍 Supporting Evidence      │  │ ✍️ Policy Enhancements      │  │
│ ├─────────────────────────────┤  ├─────────────────────────────┤  │
│ │ Found 12 relevant sources:  │  │ Suggested improvements:     │  │
│ │ • RA 11054 (BARMM Organic   │  │ • Clarify implementation    │  │
│ │   Law) - 5 citations        │  │   timeline                  │  │
│ │ • EO 120 - 3 citations      │  │ • Add success metrics       │  │
│ │ • Related policies - 4      │  │ • Strengthen monitoring     │  │
│ └─────────────────────────────┘  └─────────────────────────────┘  │
│                                                                      │
│ ┌─────────────────────────────┐  ┌─────────────────────────────┐  │
│ │ 📊 Predicted Impact         │  │ 🛡️ Compliance Check         │  │
│ ├─────────────────────────────┤  ├─────────────────────────────┤  │
│ │ Expected outcomes:          │  │ ✓ Aligns with BARMM mandate │  │
│ │ • Reach: 15,000 families    │  │ ✓ Budget allocation valid   │  │
│ │ • Timeline: 12-18 months    │  │ ⚠️ Review environmental     │  │
│ │ • Success probability: 78%  │  │   compliance requirements   │  │
│ └─────────────────────────────┘  └─────────────────────────────┘  │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│              [📄 Generate AI Policy Brief]                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 8. Project Central (M&E) AI Features

### Specific Features
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🧠 AI Project Intelligence                       [Powered by AI]    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌─────────────────────────────┐  ┌─────────────────────────────┐  │
│ │ ⚠️ Anomaly Detection        │  │ 📈 Performance Forecast     │  │
│ ├─────────────────────────────┤  ├─────────────────────────────┤  │
│ │ ⚠️ 2 anomalies detected:    │  │ Projected completion:       │  │
│ │                             │  │ • Date: March 2026          │  │
│ │ • Budget variance: +15%     │  │ • Confidence: 82%           │  │
│ │   Action: Review expenses   │  │ • On track ✓                │  │
│ │                             │  │                             │  │
│ │ • Timeline delay: +2 weeks  │  │ Key milestones:             │  │
│ │   Action: Resource realloc  │  │ ████████████░░ (75%)        │  │
│ └─────────────────────────────┘  └─────────────────────────────┘  │
│                                                                      │
│ ┌─────────────────────────────┐  ┌─────────────────────────────┐  │
│ │ 🛡️ Risk Analysis            │  │ 📊 Resource Optimization    │  │
│ ├─────────────────────────────┤  ├─────────────────────────────┤  │
│ │ Identified risks:           │  │ Current efficiency: 78%     │  │
│ │                             │  │                             │  │
│ │ • Medium: Weather delays    │  │ Recommendations:            │  │
│ │   Mitigation: Covered area  │  │ • Reallocate 2 staff to     │  │
│ │                             │  │   Activity B                │  │
│ │ • Low: Supply chain issues  │  │ • Budget shift: ₱50k to    │  │
│ │   Mitigation: Backup vendor │  │   procurement               │  │
│ └─────────────────────────────┘  └─────────────────────────────┘  │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│          [📄 Generate AI Progress Report]                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Color Palette Reference

### Primary AI Colors
- **Emerald/Teal Gradient:** `from-emerald-500 to-teal-600`
- **Background:** `from-emerald-50 to-teal-50`
- **Border:** `border-emerald-200`
- **Text:** `text-emerald-600`, `text-emerald-700`

### Status Colors
- **Success:** `text-emerald-600`, `bg-emerald-50`, `border-emerald-200`
- **Warning:** `text-amber-600`, `bg-amber-50`, `border-amber-200`
- **Error:** `text-red-600`, `bg-red-50`, `border-red-200`
- **Info:** `text-blue-600`, `bg-blue-50`, `border-blue-200`

### Interactive States
- **Hover:** `hover:border-emerald-300`, `hover:shadow-md`
- **Active:** `bg-emerald-600 text-white`
- **Disabled:** `opacity-50 cursor-not-allowed`

---

## Icon Usage

### AI Feature Icons (FontAwesome)
- **Similar Items:** `fa-users`, `fa-project-diagram`
- **Analysis:** `fa-comments`, `fa-chart-bar`
- **Classification:** `fa-clipboard-list`, `fa-tags`
- **Validation:** `fa-check-circle`, `fa-shield-alt`
- **Insights:** `fa-lightbulb`, `fa-brain`
- **Matching:** `fa-users-cog`, `fa-handshake`
- **Forecasting:** `fa-chart-line`, `fa-chart-area`
- **Risk:** `fa-exclamation-triangle`, `fa-shield-alt`
- **Reports:** `fa-file-alt`, `fa-download`
- **Chat:** `fa-robot`, `fa-comments`, `fa-paper-plane`

---

## Responsive Breakpoints

### Grid Layout Changes
- **Mobile (< 768px):** 1 column
- **Tablet (768px - 1024px):** 2 columns
- **Desktop (> 1024px):** 3 columns

### Chat Widget
- **Mobile:** `max-w-[calc(100vw-2rem)]` (fits screen with margin)
- **Desktop:** `w-96` (fixed width)

---

## Animation Timings

### Standard Transitions
- **Default:** `transition-all duration-200`
- **Hover Effects:** `transition-transform`
- **Loading Spinners:** `animate-spin`

### HTMX Swaps
- **Swap Duration:** `swap:300ms` (for smooth transitions)
- **Delete Duration:** `swap:200ms` (for removals)

---

## Accessibility Features

### Keyboard Navigation
- **Tab:** Navigate between interactive elements
- **Enter:** Activate buttons and links
- **Escape:** Close chat panel

### Screen Reader Support
- Semantic HTML structure
- ARIA labels for dynamic content
- Live regions for HTMX updates

### Color Contrast
- **Text on backgrounds:** Minimum 4.5:1 ratio
- **Interactive elements:** Clear focus indicators
- **Status indicators:** Color + icon (not color alone)

---

## Implementation Notes

1. **All templates use emerald/teal gradient for AI elements**
2. **Loading states show spinner + descriptive text**
3. **Error states use red color scheme with clear messages**
4. **Success states use emerald color scheme with icons**
5. **All components are mobile-responsive**
6. **HTMX handles dynamic loading without page reloads**
7. **Consistent spacing and typography throughout**

---

**For complete technical implementation details, see:**
- `/docs/improvements/AI_TEMPLATE_INTEGRATION_SUMMARY.md`
- `/docs/improvements/AI_INTEGRATION_QUICK_START.md`
