# UI Testing Checklist
**Date:** January 16, 2026  
**Version:** Usability Improvements v1.0

## Pre-Deployment Testing

### ✅ Code Quality Checks
- [x] No linter errors
- [x] All JavaScript has null checks
- [x] All HTML elements have proper IDs
- [x] CSS selectors match HTML elements
- [x] Form structure is valid

### 🔍 Functional Testing

#### 1. Auto-Fill PI Information
- [ ] Navigate to protocol submission form
- [ ] Verify PI name field is pre-filled with user's full name
- [ ] Verify PI email field is pre-filled with user's email
- [ ] Verify PI department field is pre-filled (if user has profile with department)
- [ ] Verify all fields are still editable after auto-fill
- [ ] Test with user who has no profile (should still fill name/email)

#### 2. Progress Indicator
- [ ] Verify progress bar appears at top of form
- [ ] Verify progress bar shows "Section 1 of 16" initially
- [ ] Scroll down through form
- [ ] Verify progress bar updates as sections come into view
- [ ] Verify progress bar percentage increases correctly
- [ ] Verify progress bar text updates (e.g., "Section 5 of 16")
- [ ] Test on mobile - verify progress bar is hidden on very small screens

#### 3. Section Navigation Sidebar
- [ ] Verify sidebar appears on desktop (lg screens and above)
- [ ] Verify sidebar is hidden on mobile/tablet
- [ ] Click on each section link in sidebar
- [ ] Verify smooth scroll to correct section
- [ ] Verify current section is highlighted as you scroll
- [ ] Verify sidebar scrolls independently if content is long
- [ ] Test all 16 section links

#### 4. Success Messages
- [ ] Create a new study
- [ ] Verify success message appears with links
- [ ] Click "Submit for IRB review" link - verify it works
- [ ] Click "dashboard" link - verify it works
- [ ] Submit a protocol
- [ ] Verify success message shows submission number
- [ ] Verify success message has links to submission details and dashboard
- [ ] Verify links in success messages are clickable

#### 5. Loading States
- [ ] Fill out protocol form
- [ ] Click "Submit Protocol" button
- [ ] Verify button shows spinner and "Submitting..." text
- [ ] Verify button is disabled during submission
- [ ] Verify loading overlay appears
- [ ] Verify cancel button is disabled during submission
- [ ] Verify form cannot be submitted twice

#### 6. Conditional Fields
- [ ] Check "Involves Vulnerable Populations" checkbox
- [ ] Verify vulnerable population fields appear
- [ ] Uncheck - verify fields hide
- [ ] Check "Involves International Research" checkbox
- [ ] Verify international research fields appear
- [ ] Check "No Financial Interests" checkbox
- [ ] Verify financial disclosure field hides
- [ ] Check "Continuation of Previous" checkbox
- [ ] Verify previous protocol number field appears

#### 7. Form Validation
- [ ] Try to submit form with required fields empty
- [ ] Verify error messages appear
- [ ] Verify error messages are clear and helpful
- [ ] Fill in required fields
- [ ] Verify form submits successfully

### 📱 Mobile Responsiveness Testing

#### Desktop (1920x1080, 1366x768)
- [ ] Verify sidebar navigation is visible
- [ ] Verify progress bar is visible
- [ ] Verify form layout is readable
- [ ] Verify all buttons are accessible

#### Tablet (768px - 991px)
- [ ] Verify sidebar is hidden
- [ ] Verify progress bar is visible
- [ ] Verify form fields are properly sized
- [ ] Verify buttons are tappable

#### Mobile (320px - 767px)
- [ ] Verify sidebar is hidden
- [ ] Verify progress bar is hidden on very small screens
- [ ] Verify form fields are at least 44px tall
- [ ] Verify buttons stack vertically
- [ ] Verify all text is readable
- [ ] Verify form is scrollable
- [ ] Test on actual mobile device (iOS Safari, Android Chrome)

### 🎨 Visual Design Testing

#### Branding
- [ ] Verify Nicholls red (#A6192E) is used for primary actions
- [ ] Verify Nicholls gray (#7C858E) is used for secondary elements
- [ ] Verify progress bar uses brand colors
- [ ] Verify sidebar header uses brand red

#### Layout
- [ ] Verify form sections are properly spaced
- [ ] Verify cards have proper shadows and borders
- [ ] Verify text is readable (proper contrast)
- [ ] Verify buttons have proper hover states

#### Accessibility
- [ ] Verify all form fields have labels
- [ ] Verify required fields are marked with asterisks
- [ ] Verify error messages are associated with fields
- [ ] Test keyboard navigation (Tab through form)
- [ ] Verify focus states are visible

### 🐛 Edge Cases

#### Empty States
- [ ] Test with user who has no profile
- [ ] Test with user who has partial profile data
- [ ] Test form with no existing submissions

#### Browser Compatibility
- [ ] Test in Chrome (latest)
- [ ] Test in Firefox (latest)
- [ ] Test in Safari (latest)
- [ ] Test in Edge (latest)

#### Performance
- [ ] Verify page loads quickly
- [ ] Verify JavaScript doesn't cause lag when scrolling
- [ ] Verify form submission is responsive

### 🔄 Integration Testing

#### Workflow
- [ ] Create study → Submit protocol → Verify success
- [ ] Edit study → Submit protocol → Verify success
- [ ] Submit protocol → View submission → Verify details

#### Data Persistence
- [ ] Fill out form partially
- [ ] Refresh page (should lose data - expected)
- [ ] Submit form → Verify data is saved correctly
- [ ] Verify auto-filled data is saved

## Known Issues / Notes

### Fixed Issues
- ✅ Sidebar moved outside column structure for proper positioning
- ✅ Added null checks to all JavaScript
- ✅ Fixed form structure (removed duplicate closing tags)

### Potential Issues to Monitor
- Sidebar positioning on very wide screens (>1920px)
- Progress bar calculation on very long sections
- Mobile performance with many sections

## Testing Results

**Tested By:** _______________  
**Date:** _______________  
**Status:** Ready for Deployment / Needs Fixes

### Critical Issues Found:
1. 
2. 
3. 

### Minor Issues Found:
1. 
2. 
3. 

---

## Quick Test Script

1. **Login** to system
2. **Create a study** - verify success message with links
3. **Click "Submit Protocol"** - verify form loads
4. **Check PI fields** - verify auto-filled
5. **Scroll through form** - verify progress bar updates
6. **Click sidebar links** - verify smooth scroll
7. **Fill out form** - verify conditional fields work
8. **Submit form** - verify loading states
9. **Check success message** - verify links work
10. **Test on mobile** - verify responsive design

---

## Deployment Readiness

- [ ] All critical tests passed
- [ ] No blocking issues found
- [ ] Mobile testing completed
- [ ] Browser compatibility verified
- [ ] Performance acceptable
- [ ] **READY TO DEPLOY** ✅
