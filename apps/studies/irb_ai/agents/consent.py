"""
Consent Agent for IRB Review

Focuses on informed consent adequacy, comprehension, and voluntariness.
"""

from typing import Dict, Any
from .base import BaseAgent


class ConsentAgent(BaseAgent):
    """Agent specializing in informed consent processes and documentation."""
    
    def get_focus_area(self) -> str:
        return "informed consent adequacy, documentation, and process"
    
    def _extract_relevant_criteria(self, all_criteria: Dict) -> Dict:
        """Extract consent-specific criteria."""
        return {
            "focus": "Informed Consent",
            "required_elements": [
                "Research purpose and procedures",
                "Duration of participation",
                "Risks and discomforts",
                "Benefits to participant and others",
                "Alternative procedures or treatments",
                "Confidentiality protections",
                "Compensation (if any)",
                "Voluntary participation and right to withdraw",
                "Who to contact with questions",
                "Statement that participation is research"
            ],
            "additional_elements_when_appropriate": [
                "Unforeseeable risks",
                "Circumstances for termination by investigator",
                "Additional costs to participant",
                "Consequences of withdrawal",
                "Significant new findings disclosure",
                "Number of participants",
                "Commercial use of data or biological specimens"
            ],
            "process_requirements": [
                "Adequate time to consider participation",
                "Opportunity to ask questions",
                "No coercive or undue influence language",
                "Comprehension assessment when appropriate",
                "Documentation of consent (signed form or documented waiver)",
                "Language understandable to participants",
                "Reading level appropriate for population",
                "Translation for non-English speakers"
            ],
            "assessment_questions": [
                "Are all required elements present?",
                "Is language clear and jargon-free?",
                "Is reading level appropriate (8th grade or lower)?",
                "Is the process voluntary and free from coercion?",
                "Are risks and benefits accurately represented?",
                "Is the right to withdraw clearly stated?",
                "Are contact details provided?",
                "Is compensation described as non-coercive?",
                "Are there comprehension checks if needed?"
            ],
            "consent_red_flags": [
                "Missing required elements",
                "Exculpatory language (waiving legal rights)",
                "Coercive language or undue inducement",
                "Risks minimized or not disclosed",
                "Benefits overstated",
                "Complex language or jargon",
                "Reading level too high",
                "No opportunity for questions",
                "Pressure to consent",
                "Inadequate time to consider",
                "Consent coupled with unrelated activities",
                "No translation for non-English speakers",
                "Unclear withdrawal procedures"
            ]
        }
    
    def _get_default_criteria(self) -> Dict:
        """Default consent criteria."""
        return self._extract_relevant_criteria({})
    
    def build_prompt(self, materials: Dict[str, Any]) -> str:
        """Build consent-focused prompt."""
        base_prompt = super().build_prompt(materials)
        
        consent_specific = """

SPECIFIC CONSENT FOCUS AREAS:

1. **Required Elements Check**:
   Review consent form/process for ALL required elements:
   - Purpose and procedures clearly explained?
   - Duration stated?
   - Risks disclosed (physical, psychological, social, economic)?
   - Benefits described accurately (not overstated)?
   - Alternatives mentioned (if applicable)?
   - Confidentiality protections explained?
   - Compensation described (if any, ensure not coercive)?
   - Voluntary participation emphasized?
   - Right to withdraw stated clearly and without penalty?
   - Contact information provided?

2. **Language and Comprehension**:
   - Is language at 8th grade reading level or lower?
   - Is technical jargon avoided or explained?
   - Are sentences short and clear?
   - Is structure logical and easy to follow?
   - Are there comprehension checks if needed?
   - Is translation provided for non-English speakers?

3. **Voluntariness Assessment**:
   - Is participation clearly voluntary?
   - Are there coercive elements (excessive payment, course credit requirements)?
   - Is there undue influence (authority figures)?
   - Can participants withdraw without penalty?
   - Is withdrawal process clearly explained?

4. **Exculpatory Language Check**:
   - Does consent ask participants to waive legal rights?
   - Is there language releasing researchers from liability?
   - Are there inappropriate disclaimers?

5. **Process Adequacy**:
   - Is there adequate time to consider participation?
   - Is there opportunity to ask questions?
   - Is ongoing consent addressed (for longitudinal studies)?
   - Is re-consent planned for protocol changes?

Flag any missing required elements, exculpatory language, coercive elements, or 
language that is too complex or legalistic for participants to understand.
"""
        
        return base_prompt + consent_specific








