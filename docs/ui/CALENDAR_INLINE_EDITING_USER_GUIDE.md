# Calendar Inline Editing - User Guide

**Feature**: Quick edit work items directly from the calendar sidebar
**Available In**: OOBC Advanced Modern Calendar
**Access**: OOBC Management → Calendar → Advanced

---

## Quick Start

### How to Edit a Work Item from the Calendar

1. **Click on any event** in the calendar to open the detail panel
2. **Click the "Edit" button** in the detail panel (blue gradient button)
3. **Make your changes** in the edit form
4. **Click "Save Changes"** or **"Cancel"** to return without saving

The calendar will automatically refresh to show your updates!

---

## What You Can Edit

The inline editing form includes these fields:

| Field | Description | Required |
|-------|-------------|----------|
| **Title** | Work item name | ✅ Yes |
| **Status** | Not Started, In Progress, At Risk, Blocked, Completed, Cancelled | No |
| **Priority** | Low, Medium, High, Urgent, Critical | No |
| **Start Date** | When work begins | No |
| **Due Date** | When work should be completed (must be after start date) | No |
| **Progress** | Completion percentage (0-100%) | No |
| **Description** | Detailed information about the work item | No |
| **Assign To** | Users assigned to this work item (Ctrl/Cmd + Click for multiple) | No |

---

## Tips & Tricks

### Selecting Multiple Assignees

**Windows/Linux**: Hold `Ctrl` and click each user
**Mac**: Hold `Cmd` and click each user

### Date Selection

- Click the calendar icon in the date field to open a date picker
- Manually type dates in `YYYY-MM-DD` format (e.g., `2025-10-15`)
- **Validation**: Due date cannot be before start date

### Progress Slider

- Use the number input to set progress
- Default step: 5% increments
- Range: 0% to 100%

### Keyboard Shortcuts

- **Tab**: Navigate between form fields
- **Enter**: Submit form (when focused on input field)
- **Esc**: Close detail panel (when in view mode)

---

## Visual Guide

### Step 1: Click Event
![Click Event](../assets/calendar-click-event.png)
*Click any calendar event to open the detail panel on the right*

### Step 2: View Details
![View Details](../assets/calendar-view-details.png)
*Review work item information and click "Edit" button*

### Step 3: Edit Form
![Edit Form](../assets/calendar-edit-form.png)
*Make changes in the inline form*

### Step 4: Save Changes
![Save Success](../assets/calendar-save-success.png)
*Click "Save Changes" to update the work item*

### Step 5: Updated View
![Updated View](../assets/calendar-updated-view.png)
*Calendar refreshes automatically, detail panel shows updated information*

---

## Permissions

### Who Can Edit?

You can edit a work item if **any** of these conditions are true:

- ✅ You created the work item
- ✅ You are assigned to the work item
- ✅ You have the "Change Work Item" permission
- ✅ You are a superuser

### Who Can Delete?

You can delete a work item if **any** of these conditions are true:

- ✅ You created the work item
- ✅ You have the "Delete Work Item" permission
- ✅ You are a superuser

**Note**: If you don't have permission, the Edit and Delete buttons will not appear.

---

## Common Scenarios

### Updating Task Status

**Scenario**: Mark a task as completed

1. Click the task in the calendar
2. Click "Edit"
3. Change **Status** dropdown to "Completed"
4. Set **Progress** to 100%
5. Click "Save Changes"

**Result**: Task is marked as completed, calendar shows updated status color

---

### Changing Dates

**Scenario**: Push back a deadline by one week

1. Click the event in the calendar
2. Click "Edit"
3. Update the **Due Date** field
4. Click "Save Changes"

**Result**: Event moves to new date on calendar

---

### Reassigning Work

**Scenario**: Add a team member to help with a task

1. Click the task in the calendar
2. Click "Edit"
3. Hold `Ctrl/Cmd` and click additional users in **Assign To** field
4. Click "Save Changes"

**Result**: New assignees see the task in their assigned work items

---

### Updating Progress

**Scenario**: Update a project's completion percentage

1. Click the project in the calendar
2. Click "Edit"
3. Update **Progress** field (e.g., change from 50% to 75%)
4. Click "Save Changes"

**Result**: Progress bar updates in detail view

---

## Troubleshooting

### Edit Button Not Showing

**Cause**: You don't have permission to edit this work item

**Solution**:
- Check if you created the work item or are assigned to it
- Contact your administrator to request edit permissions

---

### "Due date must be after start date" Error

**Cause**: You set a due date that's earlier than the start date

**Solution**:
- Change the due date to be after the start date
- Or change the start date to be before the due date

---

### Changes Not Saving

**Cause**: Validation errors in the form

**Solution**:
- Look for red error messages under each field
- Fix any validation errors
- Click "Save Changes" again

---

### Calendar Not Refreshing

**Cause**: Browser issue or network connectivity

**Solution**:
1. Wait a few seconds and check if calendar updates
2. Click outside the detail panel and re-open the event
3. Refresh the page (Ctrl+R or Cmd+R)

---

## Best Practices

### When to Use Inline Editing

✅ **Use inline editing when:**
- Making quick updates to status or priority
- Adjusting dates by a few days
- Updating progress percentage
- Adding/removing assignees
- Adding brief notes to description

❌ **Use full edit page when:**
- Changing work type (Project → Activity)
- Moving work item to different parent
- Changing teams assigned
- Updating complex project data (budget, workflow stage)
- Need to see full hierarchy while editing

---

### Workflow Recommendations

**Daily Standup Updates**:
1. Open calendar to today's view
2. Click each assigned task
3. Update status and progress inline
4. Add brief notes to description if needed

**Weekly Planning**:
1. Switch calendar to week view
2. Review upcoming deadlines
3. Adjust dates for tasks running behind
4. Reassign work if team members are overloaded

**End of Day**:
1. Review completed tasks for the day
2. Mark as "Completed" and set progress to 100%
3. Add completion notes to description

---

## Accessibility

### Screen Reader Support

- Form labels are properly announced
- Validation errors are read aloud
- Button purposes are clearly stated

### Keyboard Navigation

- Use `Tab` to move between form fields
- Use arrow keys in dropdown menus
- Use `Space` to select checkboxes
- Use `Enter` to submit form

### High Contrast Mode

- Form fields have clear borders
- Error messages use red color with icon
- Success messages use green color with icon

---

## Mobile Usage

The inline editing feature works on mobile devices with these adaptations:

- **Sidebar becomes full-screen modal** on mobile
- **Touch-friendly button sizes** (minimum 44x44px)
- **Date pickers use native mobile date selectors**
- **Assignee multi-select optimized for touch**

---

## Frequently Asked Questions

### Q: Can I edit multiple work items at once?

**A**: Not currently. You must edit each work item individually. Bulk editing is planned for a future release.

---

### Q: What happens if I click Cancel?

**A**: All changes are discarded and you return to the detail view. Nothing is saved to the database.

---

### Q: Will my changes affect parent/child work items?

**A**: If the parent has "Auto-calculate progress" enabled, updating a child's status to "Completed" will automatically update the parent's progress percentage.

---

### Q: Can I undo changes after saving?

**A**: Not directly. You'll need to click Edit again and manually revert the changes. An audit log tracks all changes for review.

---

### Q: Does inline editing work in the basic calendar view?

**A**: Currently, inline editing is only available in the **Advanced Modern Calendar** view. The basic calendar still navigates to the full edit page.

---

### Q: How do I know my changes were saved?

**A**: You'll see:
1. A green success toast notification in the top-right corner
2. The detail panel returns to view mode with updated information
3. The calendar automatically refreshes to show the changes

---

## Getting Help

### Additional Resources

- **Full Documentation**: [CALENDAR_INLINE_EDITING_IMPLEMENTATION.md](../improvements/UI/CALENDAR_INLINE_EDITING_IMPLEMENTATION.md)
- **Calendar User Guide**: [CALENDAR_VISUAL_GUIDE.md](CALENDAR_VISUAL_GUIDE.md)
- **UI Standards**: [OBCMS_UI_COMPONENTS_STANDARDS.md](OBCMS_UI_COMPONENTS_STANDARDS.md)

### Contact Support

If you encounter issues or have questions:

1. **Check the Troubleshooting section** above
2. **Contact your system administrator**
3. **Submit a support ticket** via OOBC Management → Help

---

**Last Updated**: 2025-10-06
**Feature Version**: 1.0
**Applicable To**: OOBC Advanced Modern Calendar
