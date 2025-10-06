# AI Chat Widget - Sample Test Questions

**Purpose:** Test questions for manual testing of the AI chat widget
**Usage:** Copy and paste these questions into the chat widget to verify responses
**Expected:** AI should provide relevant, accurate responses with follow-up suggestions

---

## Data Query Questions

### Communities Module

**Question 1: Basic Count**
```
How many communities are in Region IX?
```
Expected Response: Specific count of OBC communities in Region IX
Follow-up Suggestions: Related geographic queries

**Question 2: Province-Specific**
```
Show me communities in Zamboanga del Sur
```
Expected Response: List or count of communities in that province
Follow-up: "Show details", "Which municipalities?"

**Question 3: Ethnolinguistic Groups**
```
How many Maranao communities are there?
```
Expected Response: Count of Maranao communities
Follow-up: "Where are they located?", "Other ethnic groups"

**Question 4: Regional Distribution**
```
Which region has the most OBC communities?
```
Expected Response: Region with highest count
Follow-up: "Show breakdown by province", "What about Region X?"

---

### MANA (Mapping and Needs Assessment)

**Question 5: Recent Assessments**
```
Show me recent MANA assessments
```
Expected Response: List of recent assessments (Draft, Approved, Published)
Follow-up: "Filter by region", "Show approved only"

**Question 6: Assessment Status**
```
How many assessments are approved?
```
Expected Response: Count of assessments in "Approved" status
Follow-up: "Show draft assessments", "Which communities assessed?"

**Question 7: Priority Needs**
```
What are the top needs identified in assessments?
```
Expected Response: Summary of priority needs (Health, Education, Infrastructure, etc.)
Follow-up: "Health needs only", "By region"

**Question 8: MANA Explanation**
```
What is MANA?
```
Expected Response: Explanation of Mapping and Needs Assessment module
Follow-up: "How to create assessment", "Assessment workflow"

---

### Coordination Module

**Question 9: Workshops**
```
How many workshops have been conducted?
```
Expected Response: Total workshop count
Follow-up: "Show recent workshops", "By topic"

**Question 10: Partnerships**
```
List all coordination partnerships
```
Expected Response: List of NGOs, LGUs, national agencies
Follow-up: "Show active partnerships", "Filter by type"

**Question 11: Recent Activities**
```
What coordination activities are happening this month?
```
Expected Response: Current month's workshops, meetings, activities
Follow-up: "Next month's schedule", "Past events"

**Question 12: Stakeholder Types**
```
How many NGO partners do we have?
```
Expected Response: Count of NGO stakeholders
Follow-up: "List LGU partners", "Show national agencies"

---

### Policy Recommendations

**Question 13: Policy Count**
```
How many policy recommendations have been submitted?
```
Expected Response: Total policy recommendation count
Follow-up: "Show approved policies", "By status"

**Question 14: Policy Status**
```
Show me implemented policies
```
Expected Response: List of policies in "Implemented" status
Follow-up: "Pending policies", "Under review"

**Question 15: Policy Topics**
```
What policy areas are covered?
```
Expected Response: Summary of policy categories (Education, Health, Livelihood, etc.)
Follow-up: "Education policies only", "Recent submissions"

---

### Project Management (Project Central)

**Question 16: Active Projects**
```
How many active projects are there?
```
Expected Response: Count of projects in active status
Follow-up: "Show project details", "By MOA"

**Question 17: Budget Information**
```
What is the total project budget?
```
Expected Response: Sum of all project budgets
Follow-up: "Budget by ministry", "Top projects by budget"

**Question 18: MOA Projects**
```
List all projects from Ministry of Health
```
Expected Response: Projects filtered by MOA
Follow-up: "Other ministries", "Project timelines"

---

## Help and Navigation Questions

**Question 19: General Help**
```
What can you help me with?
```
Expected Response: Overview of AI assistant capabilities
Suggestions: Example queries for each module

**Question 20: Navigation**
```
Take me to the dashboard
```
Expected Response: "I'll take you to the dashboard" + redirect data
Suggestions: Other navigation options

**Question 21: Feature Explanation**
```
How do I create a new workshop?
```
Expected Response: Step-by-step instructions or link to guide
Suggestions: Related help topics

**Question 22: Module Overview**
```
Tell me about the Coordination module
```
Expected Response: Explanation of Coordination module features
Suggestions: "Create partnership", "View workshops"

---

## Conversational Questions

**Question 23: Greeting**
```
Hello
```
Expected Response: Friendly greeting + capabilities overview
Suggestions: Common queries to get started

**Question 24: Thanks**
```
Thank you
```
Expected Response: "You're welcome! Anything else I can help with?"
Suggestions: Related queries

**Question 25: About OBCMS**
```
What is OBCMS?
```
Expected Response: Explanation of Office for Other Bangsamoro Communities Management System
Suggestions: "Main features", "Who uses OBCMS"

**Question 26: Bangsamoro Context**
```
Tell me about OBC communities
```
Expected Response: Context about Other Bangsamoro Communities outside BARMM
Suggestions: "Community distribution", "Ethnic groups"

---

## Analysis Questions (Advanced)

**Question 27: Trends**
```
What are the trends in community needs?
```
Expected Response: Analysis of needs across assessments
Suggestions: "By region", "By sector"

**Question 28: Comparison**
```
Compare communities in Region IX vs Region X
```
Expected Response: Comparative data between regions
Suggestions: "Add Region XI", "Show differences"

**Question 29: Distribution**
```
Show me the geographic distribution of communities
```
Expected Response: Breakdown by region/province
Suggestions: "Visualize on map", "Export data"

**Question 30: Impact Assessment**
```
What is the impact of completed projects?
```
Expected Response: Summary of project outcomes (if available)
Suggestions: "By sector", "Success metrics"

---

## Edge Cases and Error Handling

**Question 31: Ambiguous Query**
```
Show me stuff
```
Expected Response: Request for clarification
Suggestions: Specific examples of what can be shown

**Question 32: Out of Scope**
```
What's the weather today?
```
Expected Response: Polite explanation that this is outside OBCMS scope
Suggestions: OBCMS-related queries

**Question 33: Complex Multi-Part**
```
How many communities are in Region IX and what are their primary needs and which ones have workshops scheduled?
```
Expected Response: Answer to multi-part query OR break down into separate questions
Suggestions: Focus on one aspect

**Question 34: Data Not Available**
```
How many communities on Mars?
```
Expected Response: "I don't have data about that"
Suggestions: Valid geographic queries

**Question 35: Follow-up Context**
```
First: "How many communities are there?"
Then: "Where are they located?"
```
Expected Response: Should understand "they" refers to communities from previous question
Suggestions: More specific location queries

---

## Performance Test Questions

**Question 36: Quick Response**
```
Count communities
```
Expected Response: Fast count result (<2 seconds)

**Question 37: Simple Lookup**
```
Region IX count
```
Expected Response: Quick region-specific count

**Question 38: Multiple Queries in Sequence**
Send 5 questions rapidly:
1. "How many communities?"
2. "How many workshops?"
3. "How many policies?"
4. "How many projects?"
5. "How many assessments?"

Expected: All responses arrive in order, no errors

---

## Accessibility Test Questions

**Question 39: Keyboard Navigation Test**
Use only keyboard:
- Tab to chat button
- Enter to open
- Tab to input
- Type question
- Enter to send

Expected: Fully keyboard accessible

**Question 40: Screen Reader Test**
Enable screen reader (NVDA/JAWS):
- Verify announcements
- Check ARIA labels
- Confirm role attributes

Expected: All elements properly announced

---

## Testing Checklist

When testing each question, verify:

- [ ] Response is relevant and accurate
- [ ] Response time is acceptable (<3 seconds)
- [ ] Follow-up suggestions are provided (2-3 suggestions)
- [ ] Suggestions are contextually relevant
- [ ] No error messages appear
- [ ] Chat scrolls to show new messages
- [ ] User message and bot response are visually distinct
- [ ] Timestamps are shown (if implemented)
- [ ] Conversation history is maintained
- [ ] Input clears after sending
- [ ] Loading indicator appears during processing

---

## Sample Conversation Flows

### Flow 1: Community Research

```
User: How many communities are in Region IX?
AI: [Response with count]

User: Where are they located?
AI: [Response with province distribution]

User: Show me Zamboanga del Sur communities
AI: [Response with specific communities]

User: What are their primary needs?
AI: [Response with needs assessment data]
```

### Flow 2: MANA Workflow

```
User: What is MANA?
AI: [Explanation of MANA module]

User: How do I create an assessment?
AI: [Step-by-step instructions]

User: Show me recent assessments
AI: [List of assessments]

User: How many are approved?
AI: [Count of approved assessments]
```

### Flow 3: Project Tracking

```
User: How many active projects?
AI: [Count of active projects]

User: Show me health projects
AI: [Filtered list]

User: What's the total budget?
AI: [Budget sum]

User: Which MOA has the most projects?
AI: [Top MOA by project count]
```

---

## Expected Response Format

All responses should include:

1. **Direct Answer:** Clear, concise response to the question
2. **Context:** Brief explanation if needed
3. **Data:** Specific numbers, lists, or information
4. **Cultural Sensitivity:** Respect for Bangsamoro context
5. **Suggestions:** 2-3 relevant follow-up questions

**Example:**
```
User: How many communities are in Region IX?

AI Response:
"There are 47 OBC (Other Bangsamoro Communities) identified in Region IX
(Zamboanga Peninsula). These communities are spread across Zamboanga del
Norte, Zamboanga del Sur, and Zamboanga Sibugay provinces.

SUGGESTIONS:
- Show me communities in Zamboanga del Sur
- What are the primary needs in Region IX?
- Which ethnic groups are represented?"
```

---

## Notes for Testers

1. **Vary Your Questions:** Don't use exact phrasing from this list
2. **Test Follow-ups:** Click on suggested questions to test flow
3. **Report Issues:** Document any unexpected responses
4. **Check Performance:** Note any slow responses (>3 seconds)
5. **Mobile Testing:** Test on actual mobile devices
6. **Browser Testing:** Test on Chrome, Firefox, Safari
7. **Accessibility:** Test with screen readers and keyboard only

---

**Document Status:** ✅ Ready for Testing
**Last Updated:** 2025-10-06
**Related Docs:**
- [AI_CHAT_WIDGET_TEST_REPORT.md](AI_CHAT_WIDGET_TEST_REPORT.md) - Complete test plan
- [AI_CHAT_TEST_EXECUTION_SUMMARY.md](AI_CHAT_TEST_EXECUTION_SUMMARY.md) - Test results
