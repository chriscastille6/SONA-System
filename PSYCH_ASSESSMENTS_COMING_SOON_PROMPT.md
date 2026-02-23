# Prompt for Psychological Assessments: "Coming Soon" Feature

## Request: Add "Coming Soon" Indicator for Assessments

I need to add a "Coming Soon" indicator/feature to the Psychological Assessment Library for assessments that are in development but not yet ready for use.

### Use Case

When an assessment is listed in the library but isn't fully implemented yet, users should see a clear "Coming Soon" indicator instead of being able to start the assessment (which would fail or show errors).

### Requirements

1. **Visual Indicator**: A badge or banner that says "Coming Soon" on assessments that aren't ready
2. **Disabled State**: The "Start Assessment" or similar button should be disabled/grayed out
3. **Clear Messaging**: Users should understand the assessment is in development
4. **Optional**: Estimated availability date or "Check back soon" message

### Where This Should Appear

- Assessment list/browse page
- Individual assessment detail page
- Any assessment cards or tiles

### Technical Implementation Options

1. **Database Flag**: Add a `is_coming_soon` or `status` field to assessments
2. **Configuration File**: List of assessment IDs/slugs that are "coming soon"
3. **Date-Based**: Show "Coming Soon" if `available_date` is in the future

### Example UI

```
┌─────────────────────────────────┐
│  Loss Aversion Inventory (LAI)  │
│  [Coming Soon] badge            │
│                                 │
│  [Start Assessment] (disabled)  │
│  "This assessment is currently  │
│   in development. Check back    │
│   soon!"                        │
└─────────────────────────────────┘
```

### Questions

1. What's the best way to mark assessments as "coming soon" in your system?
2. Should this be a database field, config file, or something else?
3. Do you want an estimated release date displayed?
4. Should there be a way for users to get notified when it's ready?

---

**Contact:** Christopher Castille (christopher.castille@nicholls.edu)
