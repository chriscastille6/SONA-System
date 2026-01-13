"""
Privacy Agent for IRB Review

Focuses on privacy protection, confidentiality, and data anonymization.
"""

from typing import Dict, Any
from .base import BaseAgent


class PrivacyAgent(BaseAgent):
    """Agent specializing in privacy and confidentiality."""
    
    def get_focus_area(self) -> str:
        return "privacy protection, confidentiality, and data anonymization"
    
    def _extract_relevant_criteria(self, all_criteria: Dict) -> Dict:
        """Extract privacy-specific criteria."""
        return {
            "focus": "Privacy and Confidentiality",
            "key_requirements": [
                "Personally identifiable information (PII) protection",
                "Data anonymization or pseudonymization",
                "Confidentiality safeguards",
                "Limits on data collection (minimize PII)",
                "Secure data storage and transmission",
                "Access controls and authentication",
                "Data retention and destruction policies"
            ],
            "assessment_areas": [
                "What personal data is collected?",
                "How is data anonymized or de-identified?",
                "Who has access to identifiable data?",
                "How long is data retained?",
                "Are there adequate security measures?",
                "Is there a data breach response plan?",
                "Are participants informed about privacy protections?",
                "Does the study comply with privacy regulations (FERPA, etc.)?"
            ],
            "privacy_risks": [
                "Collecting unnecessary PII",
                "Inadequate de-identification",
                "Weak access controls",
                "Insecure data transmission",
                "Excessive data retention",
                "Re-identification risks",
                "Third-party data sharing without consent",
                "Inadequate privacy disclosures"
            ]
        }
    
    def _get_default_criteria(self) -> Dict:
        """Default privacy criteria."""
        return self._extract_relevant_criteria({})
    
    def build_prompt(self, materials: Dict[str, Any]) -> str:
        """Build privacy-focused prompt."""
        base_prompt = super().build_prompt(materials)
        
        privacy_specific = """

SPECIFIC PRIVACY FOCUS AREAS:

1. **Data Collection**:
   - Is PII collection minimized?
   - Is all collected data necessary for the research?
   - Are indirect identifiers controlled?
   - Are recordings (audio/video) justified?

2. **De-identification & Anonymization**:
   - Are identifiers removed or encrypted?
   - Is there a code key? If so, how is it protected?
   - Are there re-identification risks?
   - Is data aggregation/generalization used appropriately?

3. **Access Controls**:
   - Who has access to identifiable data?
   - Are there role-based access controls?
   - Is access logged and audited?
   - How are access credentials managed?

4. **Data Lifecycle**:
   - How is data stored (encryption, secure servers)?
   - How is data transmitted (SSL/TLS, encrypted channels)?
   - How long is data retained?
   - How is data destroyed at end of retention?

5. **Disclosure & Transparency**:
   - Are privacy practices clearly disclosed to participants?
   - Is there a privacy policy or data use statement?
   - Are data sharing practices disclosed?
   - Are participants' privacy rights explained?

Flag any collection of sensitive data (health, financial, biometric), inadequate security 
measures, or privacy disclosures that are unclear or incomplete.
"""
        
        return base_prompt + privacy_specific








