# Prompt for Psychological Assessments Project

## Request: Loss Aversion Inventory (LAI) Integration

I need to add the **Loss Aversion Inventory (LAI)** and related correlate measures from the Psychological Assessment Library to the TRO (Total Rewards Optimization) study protocol.

### Context

The TRO study currently includes a **7-item Loss Aversion Scale** based on Li, Chai, Nordstrom, Tangpong, & Hung (2021) from the *Journal of Managerial Issues*. This is implemented directly in the study protocol.

### What I Need

I need to add the **full Loss Aversion Inventory** that's available through the Psychological Assessment Library, which includes:

1. **Loss Aversion Scale** (Li et al., 2021): The 7-item validated scale we already have
2. **Endowment Effect Measure**: Items assessing the tendency to overvalue items one already possesses
3. **Additional correlate measures**: Any other measures implemented in the library's loss aversion measurement process

### Purpose

This addition serves two research goals:

1. **Gather more comprehensive data on the loss aversion construct and its correlates**: The original 7-item scale is useful but limited. Adding the endowment effect scale and other correlate measures will provide a richer understanding of how various facets of loss aversion influence compensation package preferences in the conjoint analysis task.

2. **Replicate the original Li et al. (2021) findings**: The original study reported specific psychometric properties and correlations. By administering the full inventory, we can contribute to the replication literature and assess whether the scale's properties hold in our specific educational context with undergraduate business students.

### Technical Requirements

- The assessment should be accessible via: `https://bayoupal.nicholls.edu/platform/assessment-flow.html?assessment=lai`
- Should take approximately 5-10 additional minutes to complete
- Must be compatible with the existing TRO study protocol (which is an online survey)
- Should collect anonymous responses (no personal identifying information)
- Data should be exportable/accessible for analysis

### Current Implementation

The TRO study protocol is at:
- Study slug: `conjoint-analysis`
- Protocol: Static HTML/CSS/JavaScript application
- Current loss aversion measure: 7-item scale embedded in the protocol

### Questions

1. Is the Loss Aversion Inventory (LAI) already implemented in the Psychological Assessment Library?
2. If yes, what is the exact URL/endpoint to access it?
3. What additional measures (endowment effect, etc.) are included in the library's loss aversion assessment?
4. How do I integrate this into the TRO study protocol?
5. What data format does it return? (JSON, CSV, etc.)
6. Can it be embedded in an iframe, or does it need to be a separate page/redirect?

### Reference

**Loss Aversion Scale Reference:**
Li, J., Chai, L., Nordstrom, O., Tangpong, C., & Hung, K. (2021). Development of a Loss Aversion Scale. *Journal of Managerial Issues*, 33(1), 69-89.

---

**Contact:** Christopher Castille (christopher.castille@nicholls.edu)  
**Study:** Theory of Optimal Fringe Benefits Using Conjoint Analysis  
**IRB Protocol:** IRBE20251031-005CBA  
**Amendment:** IRBE20251031-005CBA-AMD-01 (pending approval)
