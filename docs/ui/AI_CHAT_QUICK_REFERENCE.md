# AI Chat Widget - Quick Reference Guide

**For**: OBCMS Users and Administrators
**Last Updated**: 2025-10-06

---

## What is the AI Chat Widget?

The AI Chat Widget is an intelligent assistant powered by Google Gemini AI that helps you:
- Find data quickly (communities, assessments, partnerships, etc.)
- Navigate the OBCMS system
- Get analytical insights
- Learn how to use OBCMS features

---

## How to Use

### Opening the Chat

1. Look for the **green circular button** at the bottom-right of any OBCMS page
2. Click the button to open the chat panel
3. The chat will slide up from the bottom

**Mobile**: Chat opens as a full-width panel from the bottom

**Desktop**: Chat opens as a floating panel (400px wide)

### Asking Questions

Simply type your question naturally, as if talking to a colleague:

**Examples**:
- "How many communities are in Region IX?"
- "Show me recent MANA assessments"
- "List all active partnerships"
- "What is the OBC population in Zamboanga del Sur?"
- "Help me create a new workshop"

**Tips**:
- Be specific (mention region, province, or module)
- Use natural language (no special syntax needed)
- Ask follow-up questions (the AI remembers context)

### Understanding Responses

The AI will provide:
1. **Direct answer** to your question
2. **Structured data** (if available) - numbers, lists, statistics
3. **Follow-up suggestions** - related questions you might ask next
4. **Intent badge** - shows what type of question was detected

### Closing the Chat

- Click the **X button** in the chat header
- Click outside the chat panel (mobile only)
- Press **Esc key** on your keyboard

---

## What Can the AI Do?

### 1. Data Queries

**Ask for specific information from OBCMS**:
- "How many communities in Region IX?"
- "List all workshops in Zamboanga del Sur"
- "Show me active policy recommendations"
- "Count organizations in the coordination network"

**The AI can access**:
- Communities (OBC profiles, demographics)
- MANA (assessments, workshops, needs)
- Coordination (organizations, partnerships, activities)
- Policies (recommendations, implementation status)
- Projects (PPAs, budgets, timelines)

### 2. Analysis

**Get insights and patterns**:
- "What are the top needs in coastal communities?"
- "Analyze MANA assessment trends"
- "Compare project completion rates by region"
- "Show me the most common ethnolinguistic groups"

### 3. Navigation

**Find your way around OBCMS**:
- "Take me to the dashboard"
- "Open the MANA module"
- "Go to coordination page"
- "Where do I create a new assessment?"

### 4. Help & Instructions

**Learn how to use features**:
- "How do I create a new workshop?"
- "What is a policy recommendation?"
- "Help me search for communities"
- "How do I export data?"

### 5. General Conversation

**Greetings and casual questions**:
- "Hello!"
- "Thank you"
- "What can you help me with?"
- "Tell me about OBCMS"

---

## Example Conversations

### Scenario 1: Community Data Query

**You**: "How many communities are in Zamboanga del Sur?"

**AI**: "Based on the latest data, there are 23 Bangsamoro communities in Zamboanga del Sur province across 15 municipalities."

**Follow-up suggestions**:
- "Show me details about these communities"
- "What are the primary ethnolinguistic groups?"
- "How many OBC residents in total?"

---

### Scenario 2: Assessment Status Check

**You**: "Show me recent MANA assessments"

**AI**: "Here are the 5 most recent MANA assessments:
1. Community Assessment - Barangay X (Draft, Sep 2025)
2. Needs Survey - Municipality Y (Under Review, Aug 2025)
3. Livelihood Assessment - Province Z (Approved, Aug 2025)
..."

**Follow-up suggestions**:
- "Which assessments need approval?"
- "Show me assessment details for Barangay X"
- "How many assessments completed this year?"

---

### Scenario 3: Navigation Help

**You**: "Where do I create a new partnership?"

**AI**: "To create a new partnership:
1. Go to the Coordination module
2. Click 'Partnerships' in the sidebar
3. Click the 'Add Partnership' button
4. Fill in the partnership details form

Would you like me to take you there?"

**Follow-up suggestions**:
- "What information do I need for a partnership?"
- "How do I add partner organizations?"
- "Show me existing partnerships"

---

## Chat Features

### Multi-Turn Conversations

The AI remembers your recent questions (up to 10 messages):

**You**: "How many communities in Region IX?"
**AI**: "There are 47 communities in Region IX."

**You**: "What about Region X?"
**AI**: "Region X has 38 communities." *(understands you're still asking about community count)*

### Context Awareness

The AI understands:
- Previous questions in the conversation
- What page you're currently viewing
- Your role/permissions in OBCMS

### Follow-Up Suggestions

After each response, the AI suggests 2-3 related questions you might want to ask next. Just click a suggestion to ask it instantly.

### Instant Updates

Messages appear immediately (no page reload). You'll see:
- ✅ Your message (blue bubble, right side)
- ⏳ "Thinking..." spinner while AI processes
- 🤖 AI response (white card, left side with robot icon)

---

## Accessibility

The chat widget is fully accessible:

**Keyboard Navigation**:
- `Tab` - Move between chat button and form fields
- `Enter` - Send message
- `Esc` - Close chat

**Screen Readers**:
- All elements have proper ARIA labels
- New messages announced via `aria-live` regions
- Focus management for smooth navigation

**Visual**:
- High contrast text and backgrounds
- Large touch targets (48px minimum)
- Clear focus indicators

---

## Privacy & Data

### What's Stored

- Your chat messages (user and AI responses)
- Timestamp of each message
- Intent classification (what type of question)
- Topic of conversation

### What's NOT Stored

- No voice recordings (text only)
- No sensitive personal information
- No data from external sources

### How Long Data is Kept

- **Conversation history**: Stored in database indefinitely
- **Context cache**: 1 hour (Redis cache)
- **API responses**: 1 hour cache (for common queries)

### Clearing Your History

Administrators can clear chat history via:
```bash
DELETE /chat/clear/
```

This removes all messages and clears your conversation context.

---

## Troubleshooting

### Chat button not visible
- Check if you're logged in
- Clear browser cache and reload
- Check if JavaScript is enabled

### Messages not sending
- Check internet connection
- Verify you're logged in
- Try refreshing the page

### "Error" message appears
- API might be temporarily unavailable
- Try again in a few moments
- Contact admin if issue persists

### AI gives incorrect information
- AI responses are based on OBCMS data
- Data might be outdated - check with admin
- Report persistent issues to support

### Slow responses
- First query may take 2-3 seconds
- Subsequent queries should be faster (cached)
- Network speed affects response time

---

## Tips for Best Results

**DO**:
- ✅ Be specific ("Region IX" not just "region")
- ✅ Use natural language
- ✅ Ask follow-up questions
- ✅ Try suggested questions
- ✅ Report issues to admin

**DON'T**:
- ❌ Use technical syntax (no SQL, code)
- ❌ Ask about non-OBCMS data
- ❌ Expect real-time data (some caching)
- ❌ Share sensitive information

---

## Technical Details

**Powered by**: Google Gemini Flash (AI model)
**Response time**: 1-3 seconds average
**Context window**: 10 recent messages
**Cache duration**: 1 hour
**Authentication**: Required (must be logged in)

---

## Support

**Questions**: Contact your OBCMS administrator
**Technical issues**: Check system logs or report to IT
**Feature requests**: Submit via feedback form

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Esc` | Close chat panel |
| `Tab` | Navigate between fields |
| `Enter` | Send message |

---

## Mobile Experience

On mobile devices (< 640px width):
- Chat opens as **full-width bottom sheet** (80% screen height)
- Tap **X** or tap **outside** to close
- Optimized for touch (larger buttons, easier scrolling)

---

## Coming Soon

Future enhancements planned:
- Voice input/output
- File attachments
- Rich visualizations (charts, maps)
- Multi-language support
- Export conversation history

---

**Need help?** Just ask the AI: *"What can you help me with?"*

**Happy chatting!** 🤖💬
