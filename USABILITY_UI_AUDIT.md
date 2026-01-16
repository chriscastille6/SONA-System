# Usability & UI Audit Report
**PRAMS (Participant Recruitment and Management System)**  
**Date:** January 16, 2026  
**Auditor:** AI Assistant

---

## 🎯 Navigation & User Flow

### **Where to Go: Protocol Submission**

**Primary Path:**
1. **Login** → `https://bayoupal.nicholls.edu/hsirb/`
2. **Click "My Studies"** in navigation (or go to `/studies/researcher/`)
3. **Click "Create New Study"** button (or go to `/studies/researcher/create/`)
4. **Fill out study form** → Click "Create Study"
5. **Return to dashboard** → Find your study card
6. **Click "Submit Protocol"** button on study card
7. **Fill out comprehensive IRB form** (16 sections)
8. **Submit Protocol**

**Direct URLs:**
- Create Study: `https://bayoupal.nicholls.edu/hsirb/studies/researcher/create/`
- Researcher Dashboard: `https://bayoupal.nicholls.edu/hsirb/studies/researcher/`
- Submit Protocol: `https://bayoupal.nicholls.edu/hsirb/studies/<study_id>/protocol/submit/`

---

## ✅ STRENGTHS

### 1. **Visual Design**
- ✅ **Consistent Branding**: Nicholls State University colors (red #A6192E, gray #7C858E) applied throughout
- ✅ **Clear Visual Hierarchy**: Card-based layout with distinct sections
- ✅ **Professional Appearance**: Clean, modern Bootstrap-based design
- ✅ **Color-Coded Sections**: Different header colors for different form sections

### 2. **Information Architecture**
- ✅ **Logical Flow**: Create study → Submit protocol → Wait for review
- ✅ **Clear Section Headers**: Numbered sections (1-16) in protocol form
- ✅ **Breadcrumb Navigation**: Present on protocol submission page
- ✅ **Contextual Help Text**: Most fields have helpful descriptions

### 3. **Functionality**
- ✅ **Conditional Fields**: JavaScript shows/hides fields based on checkboxes
- ✅ **Form Validation**: Required fields marked with red asterisks
- ✅ **Error Display**: Field-level error messages shown
- ✅ **Success Feedback**: Django messages framework for user feedback

---

## ⚠️ USABILITY ISSUES & RECOMMENDATIONS

### 🔴 **CRITICAL ISSUES**

#### 1. **Navigation Clarity - Missing "Submit Protocol" Link After Study Creation**
**Issue:** After creating a study, user is redirected to dashboard but may not immediately see how to submit protocol.

**Current Flow:**
- Create study → Redirect to dashboard → User must find their study card → Click "Submit Protocol"

**Recommendation:**
- Add a prominent call-to-action after study creation: "Submit Protocol for IRB Review" button
- Or redirect directly to protocol submission page after study creation
- Add a success message with next steps: "Study created! Click here to submit for IRB review"

**Priority:** HIGH

#### 2. **Protocol Form Length - No Progress Indicator**
**Issue:** The protocol submission form has 16 sections but no progress indicator or save-as-draft functionality.

**Recommendation:**
- Add a progress bar showing "Section X of 16"
- Add "Save Draft" functionality
- Add section navigation (jump to section)
- Consider accordion-style sections that can be collapsed

**Priority:** HIGH

#### 3. **Missing Auto-Fill for Investigator Information**
**Issue:** PI information fields (name, email, department) are empty even though user is logged in.

**Recommendation:**
- Auto-populate PI fields from logged-in user's profile
- Pre-fill: `pi_name`, `pi_email`, `pi_department` from user account
- Make these fields editable but pre-filled

**Priority:** MEDIUM-HIGH

---

### 🟡 **MODERATE ISSUES**

#### 4. **Study Dashboard - Information Overload**
**Issue:** Study cards show many badges and statistics that may be overwhelming.

**Current Display:**
- Multiple badges (Active/Inactive, IRB status, AI Review status, Monitoring, OSF)
- Multiple statistics (Total Signups, Available Slots, Protocol Responses, BF)
- Multiple button groups

**Recommendation:**
- Use collapsible sections or tabs
- Group related information
- Use tooltips for less critical information
- Consider a "Summary" vs "Details" view toggle

**Priority:** MEDIUM

#### 5. **Form Field Organization - Some Sections Too Long**
**Issue:** Some sections (like "Description of Project") have many text areas in sequence.

**Recommendation:**
- Add visual separators between major fields
- Use consistent field heights
- Consider grouping related fields in sub-sections
- Add "Character count" indicators for long text fields

**Priority:** MEDIUM

#### 6. **Missing "Back" Navigation in Protocol Form**
**Issue:** No easy way to go back to previous sections without scrolling.

**Recommendation:**
- Add a sticky navigation sidebar with section links
- Add "Previous Section" / "Next Section" buttons
- Add section completion indicators (✓ for completed sections)

**Priority:** MEDIUM

#### 7. **Mobile Responsiveness - Long Forms**
**Issue:** 16-section form may be difficult to navigate on mobile devices.

**Recommendation:**
- Test on mobile devices
- Consider mobile-specific layout (single column, larger touch targets)
- Add mobile-friendly section navigation
- Ensure all form fields are easily accessible

**Priority:** MEDIUM

---

### 🟢 **MINOR IMPROVEMENTS**

#### 8. **Visual Feedback - Loading States**
**Issue:** No loading indicators when submitting long forms.

**Recommendation:**
- Add loading spinner on form submission
- Disable submit button during submission
- Show "Submitting..." message

**Priority:** LOW

#### 9. **Help Text Consistency**
**Issue:** Some fields have help text, others don't. Formatting varies.

**Recommendation:**
- Standardize help text format
- Use consistent styling (small, muted text)
- Add help icons (?) for complex fields
- Consider expandable "More information" sections

**Priority:** LOW

#### 10. **Success Messages - Next Steps**
**Issue:** After protocol submission, success message doesn't clearly indicate what happens next.

**Recommendation:**
- Enhance success message with timeline: "Your submission will be reviewed within X days"
- Add link to view submission status
- Send email confirmation with submission details

**Priority:** LOW

#### 11. **Form Validation - Real-time Feedback**
**Issue:** Validation only occurs on submit, not as user types.

**Recommendation:**
- Add real-time validation for email fields
- Add character count for text areas
- Validate date formats as user types
- Show field completion status

**Priority:** LOW

#### 12. **Accessibility - Screen Reader Support**
**Issue:** Some form fields may not have proper ARIA labels.

**Recommendation:**
- Add `aria-label` attributes to all form fields
- Ensure all buttons have descriptive text
- Test with screen readers
- Add skip-to-content links

**Priority:** LOW

---

## 📱 MOBILE-SPECIFIC CONCERNS

### Issues:
1. **Long Form Scrolling**: 16 sections require significant scrolling
2. **Button Groups**: Multiple button groups may be cramped on small screens
3. **Card Layout**: Study cards may be too wide for mobile
4. **Table Views**: Any tables (rosters, submissions) may not be responsive

### Recommendations:
- Test all pages on mobile devices
- Consider mobile-first design for forms
- Use collapsible sections on mobile
- Implement swipe gestures for navigation

---

## 🎨 VISUAL DESIGN RECOMMENDATIONS

### 1. **Protocol Form Sections**
- ✅ Good: Color-coded headers (red for section 1, gray for others)
- ⚠️ Consider: More visual distinction between sections (borders, spacing)
- ⚠️ Consider: Icons for each section type

### 2. **Button Styling**
- ✅ Good: Consistent use of Nicholls red for primary actions
- ⚠️ Consider: Larger touch targets (minimum 44x44px)
- ⚠️ Consider: More visual distinction between primary/secondary buttons

### 3. **Form Fields**
- ✅ Good: Consistent Bootstrap styling
- ⚠️ Consider: Larger text areas for long responses
- ⚠️ Consider: Better visual grouping of related fields

### 4. **Dashboard Cards**
- ✅ Good: Clear card-based layout
- ⚠️ Consider: Hover effects for better interactivity
- ⚠️ Consider: Visual indicators for study status

---

## 🔍 SPECIFIC PAGE AUDITS

### **Researcher Dashboard** (`/studies/researcher/`)
**Strengths:**
- Clear "Create New Study" button
- Study cards show key information
- Multiple action buttons available

**Issues:**
- Information density may be high
- "Submit Protocol" button may not be immediately obvious
- No filtering or sorting options

**Recommendations:**
- Add search/filter functionality
- Add sorting options (by date, status, etc.)
- Make "Submit Protocol" button more prominent
- Add empty state with helpful guidance

### **Create Study Page** (`/studies/researcher/create/`)
**Strengths:**
- Clear form layout
- Helpful "What happens next?" section
- Good field organization

**Issues:**
- No direct link to protocol submission after creation
- No indication of required vs optional fields (except asterisks)

**Recommendations:**
- Add "Submit Protocol" button after successful creation
- Add field requirement summary at top
- Add character limits where applicable

### **Protocol Submission Page** (`/studies/<id>/protocol/submit/`)
**Strengths:**
- Comprehensive 16-section form
- Conditional field display
- Clear section headers
- Breadcrumb navigation

**Issues:**
- No progress indicator
- No save-as-draft
- No section navigation
- Long scrolling required
- PI fields not auto-filled

**Recommendations:**
- Add progress bar
- Add section navigation sidebar
- Auto-fill PI information
- Add "Save Draft" functionality
- Add section completion indicators

---

## 🚀 QUICK WINS (Easy to Implement)

1. **Auto-fill PI Information** - Use logged-in user's profile data
2. **Add Progress Bar** - Simple JavaScript counter (Section X of 16)
3. **Enhance Success Messages** - Add next steps and links
4. **Add Loading States** - Disable submit button during submission
5. **Improve Mobile Buttons** - Larger touch targets
6. **Add Section Navigation** - Sticky sidebar with section links
7. **Add "Submit Protocol" CTA** - After study creation

---

## 📊 PRIORITY MATRIX

| Priority | Issue | Impact | Effort | Recommendation |
|----------|-------|--------|--------|---------------|
| HIGH | Missing protocol link after study creation | High | Low | Add CTA button |
| HIGH | No progress indicator | High | Medium | Add progress bar |
| HIGH | PI fields not auto-filled | High | Low | Auto-populate from user |
| MEDIUM | Information overload on dashboard | Medium | Medium | Add filtering/collapse |
| MEDIUM | No section navigation | Medium | Medium | Add sticky sidebar |
| MEDIUM | Mobile responsiveness | Medium | High | Test and optimize |
| LOW | Loading states | Low | Low | Add spinners |
| LOW | Help text consistency | Low | Low | Standardize format |

---

## 🎯 RECOMMENDED IMPLEMENTATION ORDER

### Phase 1 (Immediate - High Impact, Low Effort):
1. Auto-fill PI information from user profile
2. Add "Submit Protocol" CTA after study creation
3. Add progress indicator to protocol form
4. Enhance success messages with next steps

### Phase 2 (Short-term - Medium Impact, Medium Effort):
5. Add section navigation sidebar
6. Add "Save Draft" functionality
7. Improve mobile responsiveness
8. Add loading states

### Phase 3 (Long-term - Medium Impact, High Effort):
9. Redesign dashboard with filtering/sorting
10. Add accordion-style form sections
11. Implement real-time validation
12. Comprehensive accessibility audit

---

## 📝 SUMMARY

**Overall Assessment:** The system has a solid foundation with good visual design and comprehensive functionality. The main usability issues are:

1. **Navigation clarity** - Users may not immediately know how to proceed after creating a study
2. **Form length** - 16-section protocol form needs better navigation and progress tracking
3. **Auto-fill** - PI information should be pre-populated from user account
4. **Mobile experience** - Needs testing and optimization

**User Experience Score:** 7/10
- **Strengths:** Visual design, comprehensive features, clear information architecture
- **Weaknesses:** Navigation flow, form length management, mobile optimization

**Recommendation:** Focus on Phase 1 improvements first (auto-fill, progress indicator, CTA buttons) as they provide high impact with low effort.
