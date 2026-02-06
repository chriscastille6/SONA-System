# Protocol Submission Flow Diagram

## Mermaid Diagram: What Happens When a PI Submits a Protocol

```mermaid
flowchart TD
    A[PI Clicks 'Submit for Review'] --> B[protocol_submit view]
    B --> C[Mark draft status='submitted']
    C --> D[assign_college_rep function]
    
    D --> E{Get researcher from<br/>submission.submitted_by<br/>or study.researcher}
    E --> F{Get researcher's<br/>profile.department}
    F --> G[get_college_from_department]
    
    G --> H{Department contains?}
    H -->|business, accounting, finance,<br/>marketing, management, economics| I[college='business']
    H -->|education, psychology,<br/>counseling, behavioral| J[college='education']
    H -->|liberal arts, english,<br/>history, philosophy| K[college='liberal_arts']
    H -->|science, technology,<br/>computer, engineering| L[college='sciences']
    H -->|nursing| M[college='nursing']
    H -->|none| N[college_rep = None]
    
    I --> O[Find CollegeRepresentative<br/>college='business'<br/>active=True]
    J --> P[Find CollegeRepresentative<br/>college='education'<br/>active=True]
    K --> Q[Find CollegeRepresentative<br/>college='liberal_arts'<br/>active=True]
    L --> R[Find CollegeRepresentative<br/>college='sciences'<br/>active=True]
    M --> S[Find CollegeRepresentative<br/>college='nursing'<br/>active=True]
    
    O --> T[submission.college_rep =<br/>CollegeRep.representative<br/>e.g., Jon Murphy for Business]
    P --> U[submission.college_rep =<br/>CollegeRep.representative<br/>e.g., Grant Gautreaux for Education]
    Q --> V[submission.college_rep =<br/>CollegeRep.representative]
    R --> W[submission.college_rep =<br/>CollegeRep.representative]
    S --> X[submission.college_rep =<br/>CollegeRep.representative]
    N --> Y[No college rep assigned]
    
    T --> Z[route_submission function]
    U --> Z
    V --> Z
    W --> Z
    X --> Z
    Y --> Z
    
    Z --> AA{submission.involves_deception?}
    AA -->|Yes| AB[Set chair_reviewer = IRB Chair<br/>review_type = 'full']
    AA -->|No| AC[review_type =<br/>pi_suggested_review_type]
    
    AC --> AD{Review Type?}
    AD -->|exempt| AE[College rep can approve directly]
    AD -->|expedited| AF[Need 2 reviewers assigned]
    AD -->|full| AG[Route to chair_reviewer]
    
    AB --> AH[Save submission]
    AE --> AH
    AF --> AH
    AG --> AH
    
    AH --> AI[Send email to college_rep]
    AI --> AJ[Redirect to submission detail]
    
    AJ --> AK{Who can approve?}
    AK -->|exempt| AL[Only college_rep<br/>can approve]
    AK -->|expedited| AM[college_rep OR<br/>assigned reviewers<br/>can approve]
    AK -->|full| AN[Only chair_reviewer<br/>can approve]
    
    style T fill:#ffd700
    style U fill:#ff6b6b
    style AL fill:#90ee90
    style AM fill:#87ceeb
    style AN fill:#dda0dd
```

## Why Jon Murphy Cannot Approve the EI Protocol

**The Problem:**

Jon Murphy is the **College of Business Administration** representative. The EI (Emotional Intelligence) protocol is likely assigned to a **different college rep** because:

1. **Department Mapping**: The `assign_college_rep` function maps the PI's department to a college:
   - If the PI's department contains "psychology", "education", "counseling", or "behavioral" → maps to **College of Education**
   - If the PI's department contains "business", "management", "economics" → maps to **College of Business**

2. **EI Study PI**: The Emotional Intelligence study PI likely has a department that maps to **Education** (e.g., Psychology), not Business.

3. **College Rep Assignment**: The EI protocol gets assigned to the **Education college rep** (e.g., Grant Gautreaux), not Jon Murphy (Business).

4. **Approval Permissions**: 
   - For **exempt** protocols: Only the assigned `college_rep` can approve
   - For **expedited**: `college_rep` OR assigned reviewers can approve
   - For **full**: Only `chair_reviewer` can approve

**Solution:**

To allow Jon Murphy to approve the EI protocol, you need to either:

1. **Reassign the college rep** (if appropriate): Change `submission.college_rep` to Jon Murphy in the database or admin
2. **Change the PI's department**: Update the PI's profile department to something that maps to Business
3. **Assign Jon as a reviewer**: For expedited reviews, assign Jon Murphy as one of the reviewers
4. **Override in code**: Add logic to allow cross-college approvals for specific cases
