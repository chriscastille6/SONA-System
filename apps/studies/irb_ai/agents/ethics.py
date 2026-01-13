"""
Ethics Agent for IRB Review

Focuses on core ethical principles: respect for persons, beneficence, and justice.
"""

from typing import Dict, Any
from .base import BaseAgent


class EthicsAgent(BaseAgent):
    """Agent specializing in ethical principles and research ethics."""
    
    def get_focus_area(self) -> str:
        return "research ethics and ethical principles (Belmont Report principles)"
    
    def _extract_relevant_criteria(self, all_criteria: Dict) -> Dict:
        """Extract ethics-specific criteria."""
        return {
            "focus": "Research Ethics",
            "principles": [
                "Respect for Persons - Autonomy and informed consent",
                "Beneficence - Maximize benefits, minimize harms",
                "Justice - Fair distribution of research burdens and benefits"
            ],
            "key_considerations": [
                "Are participants treated with respect and dignity?",
                "Is there a favorable risk-benefit ratio?",
                "Is participant selection fair and equitable?",
                "Are there adequate protections for participants?",
                "Is there potential for coercion or undue influence?",
                "Are there conflicts of interest?",
                "Is the research scientifically sound?",
                "Is there appropriate scientific justification for the study?"
            ],
            "red_flags": [
                "Deception without justification",
                "Inadequate risk mitigation",
                "Unfair participant selection",
                "Lack of scientific merit",
                "Conflicts of interest not disclosed",
                "Coercive recruitment practices"
            ]
        }
    
    def _get_default_criteria(self) -> Dict:
        """Default ethics criteria if toolkit not available."""
        return self._extract_relevant_criteria({})
    
    def build_prompt(self, materials: Dict[str, Any]) -> str:
        """Build ethics-focused prompt."""
        base_prompt = super().build_prompt(materials)
        
        ethics_specific = """

SPECIFIC ETHICS FOCUS AREAS:

1. **Respect for Persons**:
   - Adequate informed consent process
   - Voluntariness and freedom to withdraw
   - Special protections for vulnerable populations
   - Privacy and confidentiality

2. **Beneficence**:
   - Risks are minimized and reasonable
   - Benefits justify risks
   - Research has potential value
   - Participant welfare is prioritized

3. **Justice**:
   - Fair participant selection
   - Equitable distribution of benefits/burdens
   - No exploitation of vulnerable groups
   - Appropriate inclusion/exclusion criteria

4. **Additional Ethical Considerations**:
   - Scientific validity and design
   - Researcher qualifications
   - Conflicts of interest
   - Data integrity and honesty
   - Cultural sensitivity

Pay special attention to any deception, risks (physical/psychological), vulnerable populations, 
coercion, and conflicts of interest.
"""
        
        return base_prompt + ethics_specific








