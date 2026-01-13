# Project Comparison Report
**Date**: October 22, 2025  
**Comparing**: SONA System vs Psychological Assessments (EI folder)

---

## 🎯 EXECUTIVE SUMMARY

### What's Different & Why It Matters

| Component | SONA System | Psych Assessments | Winner | Action Needed |
|-----------|-------------|-------------------|--------|---------------|
| **Consent Form** | ✅ Yes/No buttons (your request) | ❌ Checkbox only | **SONA** | Keep SONA version |
| **Demographics** | ✅ BLS/EEO categories (your request) | ❌ Basic ethnicity | **SONA** | Keep SONA version |
| **60-item Bank** | ✅ Identical | ✅ Identical | **Same** | No action |
| **Perception Items** | ⚠️ Different labels/images | ⚠️ Different labels/images | **Neither** | Decide which |
| **Perception Phase** | ❌ Structure only, not integrated | ✅ Fully integrated (Phase 4.5) | **Psych** | **MERGE NEEDED** |
| **Test Instructions** | ⚠️ Basic | ✅ Detailed 2-part explanation | **Psych** | **MERGE NEEDED** |
| **Django Integration** | ✅ Full SONA backend | ❌ Standalone HTML | **SONA** | Keep SONA |

---

## 📊 DETAILED FILE-BY-FILE COMPARISON

### 1. JavaScript: `sheldon_replication.js`

#### Key Differences:

| Feature | SONA System | Psychological Assessments | Status |
|---------|-------------|---------------------------|--------|
| **Total Phases** | 7 phases | 8 phases (includes perception phase 4.5) | ⚠️ **Psych has more** |
| **Consent Handling** | Yes/No buttons + redirect on "No" | Checkbox that enables button | ⚠️ **SONA better** |
| **Perception Phase** | Data structure exists, not fully wired | Fully integrated with phase navigation | ⚠️ **Psych better** |
| **Perception Loading** | `loadPerceptionItems()` exists but basic | Full `loadPerceptionItems()` + phase handlers | ⚠️ **Psych better** |
| **Demographics Capture** | Includes `ethnicity` field | Unknown (checking...) | ✅ **SONA has it** |
| **Item Bank Path** | `/static/projects/ei-dk/data/ei60_mixed_format.json` | `pilot_test/ei60_item_bank.json` | ⚠️ Different paths |

**Critical Missing in SONA**:
```javascript
// Psych Assessments has full perception phase setup:
'perception-phase',  // Phase 4.5 (after test, before feedback)

setupPerceptionHandlers() {
    // Full perception task logic
}

loadPerceptionQuestion() {
    // Displays perception items with timing
}
```

---

### 2. HTML Protocol: `protocol/index.html` vs `sheldon_replication.html`

#### Major Differences:

| Section | SONA System | Psychological Assessments | Winner |
|---------|-------------|---------------------------|--------|
| **Consent** | Two buttons: "No, I do not consent" / "Yes, I consent →" | Checkbox + single button | **SONA** ✅ |
| **Demographics - Ethnicity** | 7 BLS/EEO-1 categories | 2 options (Hispanic / Not Hispanic) | **SONA** ✅ |
| **Test Instructions** | Basic | **Detailed 2-part explanation with visual cards** | **Psych** ✅ |
| **Django Variables** | `{{ study.id }}`, `{{ study.slug }}` | None (standalone) | **SONA** ✅ |
| **Perception Phase HTML** | Missing | Full perception trial display | **Psych** ✅ |

**Psych Assessments has better instructional design**:
```html
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="bg-white rounded-lg p-4 border border-blue-200">
        <h4>Part 1: Typical Behavior</h4>
        <p>"What would you naturally do?"</p>
        ✓ Answer honestly about your usual responses
        ✓ No right or wrong answers
    </div>
    <div class="bg-white rounded-lg p-4 border border-green-200">
        <h4>Part 2: Best Practices</h4>
        <p>"What is most effective?"</p>
        ✓ Select the research-backed best answer
        ✓ Tests your knowledge of EI principles
    </div>
</div>
```

---

### 3. Item Banks

#### `ei60_mixed_format.json`
- **Status**: ✅ **IDENTICAL** (byte-for-byte match)
- **Both have**: 60 items (24 tendency + 36 ability)
- **No action needed**

#### `perception_items_page.json`
- **Status**: ⚠️ **DIFFERENT**
- **SONA System**: Named emotions (happiness.jpg, sadness.jpg, anger.jpg, fear.jpg)
- **Psych Assessments**: Numbered files (page-000.jpg, page-001.jpg, page-002.jpg)
- **Both have**: 15 items
- **Decision needed**: Which image naming convention is correct?

---

### 4. Videos

**SONA System**: `static/projects/ei-dk/videos/` (linked via dynamic URLs in items)  
**Psych Assessments**: `pilot_test/generated_videos_audio/` (actual video files)

**Question**: Are the actual video files in Psych Assessments that need to be copied to SONA?

---

## 🚨 CRITICAL FINDINGS

### What SONA System Has (Psych Assessments Doesn't):

1. ✅ **Yes/No consent buttons** (your request implemented)
2. ✅ **BLS/EEO ethnicity categories** (your request implemented)
3. ✅ **Django integration** (STUDY_ID, STUDY_SLUG variables)
4. ✅ **SONA platform context** (login, researcher dashboard, IRB review)

### What Psych Assessments Has (SONA System Doesn't):

1. ⚠️ **Full perception phase integration** (Phase 4.5 with handlers)
2. ⚠️ **Better instructional design** (2-part explanation with visual cards)
3. ⚠️ **Complete perception task display** (rapid presentation logic)
4. ⚠️ **8-phase workflow** (vs 7 in SONA)

---

## ✅ RECOMMENDED ACTION PLAN

### Priority 1: Merge Perception Phase from Psych → SONA
**Why**: Psych has full working perception integration, SONA only has structure

**Files to update in SONA**:
1. `static/projects/ei-dk/sheldon_replication.js`:
   - Add perception phase (4.5)
   - Copy `setupPerceptionHandlers()`
   - Copy `loadPerceptionQuestion()`
   - Update `totalPhases` to 8

2. `templates/projects/ei-dk/protocol/index.html`:
   - Add perception phase HTML section
   - Keep SONA's consent buttons ✅
   - Keep SONA's BLS ethnicity ✅

### Priority 2: Enhance Test Instructions (Optional)
**Why**: Psych has much better participant guidance

**Action**: Copy the 2-part instruction cards from Psych → SONA HTML

### Priority 3: Clarify Perception Images
**Decision needed**: Which image files are correct?
- SONA: `happiness.jpg, sadness.jpg, anger.jpg, fear.jpg`
- Psych: `page-000.jpg, page-001.jpg, page-002.jpg`

### Priority 4: Keep Everything Else in SONA
**Why**: Your requested changes (consent, demographics) are already there

---

## 🔧 DUPLICATION AUDIT

### What's NOT Duplicated (Good):

- ✅ Item banks are identical (no conflicting edits)
- ✅ Core study logic is similar (no major divergence)
- ✅ Both projects have clear purposes (SONA = deployment, Psych = development)

### What IS Being Duplicated (Needs Decision):

1. ⚠️ **Perception items** - different image naming
2. ⚠️ **Perception phase** - only complete in Psych
3. ⚠️ **Test instructions** - better in Psych

---

## 📝 YOUR DECISIONS NEEDED

### Question 1: Perception Images
Which image naming is correct?
- A) SONA's `happiness.jpg, sadness.jpg, anger.jpg, fear.jpg`
- B) Psych's `page-000.jpg, page-001.jpg`
- C) Something else entirely

### Question 2: Should I Merge Perception Phase?
Do you want me to:
- A) Copy full perception phase from Psych → SONA (recommended)
- B) Leave as-is and finish perception in SONA from scratch
- C) Abandon perception phase entirely

### Question 3: Enhanced Instructions?
Do you want the fancy 2-part instruction cards from Psych in SONA?
- A) Yes, copy them over (better UX)
- B) No, keep SONA simple

---

## 🎯 WORKFLOW RECOMMENDATION GOING FORWARD

### Clear Project Boundaries:

**Psychological Assessments** = R&D Lab
- Item generation
- Psychometric testing
- Prototype development
- Video creation
- **Do NOT edit for production deployment**

**SONA System** = Production Platform
- Final study hosting
- Participant management
- Data collection
- IRB integration
- **Only production-ready code here**

### One-Way Sync:
```
Psych Assessments (develop) → Test → Finalize → Copy to SONA (deploy)
```

**Never edit the same file in both projects simultaneously!**

---

## 🚀 NEXT IMMEDIATE STEPS

1. **You tell me**: Answer Questions 1-3 above
2. **I merge**: Perception phase + instructions if you want them
3. **You test**: Full run-through at http://localhost:8002/studies/ei-dk/run/
4. **You upload**: Pre-registration to OSF
5. **We review**: AI IRB Review with OSF link

**Ready to proceed?** Tell me your answers to the 3 questions!

