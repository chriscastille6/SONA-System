"""
Data Security Agent for IRB Review

Focuses on data handling, storage, transmission, and security measures.
"""

from typing import Dict, Any
from .base import BaseAgent


class DataSecurityAgent(BaseAgent):
    """Agent specializing in data security and handling procedures."""
    
    def get_focus_area(self) -> str:
        return "data security, storage, transmission, and handling procedures"
    
    def _extract_relevant_criteria(self, all_criteria: Dict) -> Dict:
        """Extract data security-specific criteria."""
        return {
            "focus": "Data Security and Handling",
            "security_requirements": [
                "Encryption of data at rest and in transit",
                "Secure authentication and access controls",
                "Regular security audits and monitoring",
                "Backup and disaster recovery procedures",
                "Secure data transmission protocols (HTTPS, SFTP)",
                "Physical security of data storage",
                "Secure disposal of data",
                "Vendor/third-party security assessments"
            ],
            "data_handling_standards": [
                "Data minimization principle",
                "Purpose limitation and use restrictions",
                "Data quality and accuracy",
                "Storage limitation (retention policies)",
                "Integrity and confidentiality measures",
                "Accountability and governance",
                "Incident response and breach notification",
                "Audit trails and logging"
            ],
            "assessment_areas": [
                "How is data collected (methods, tools)?",
                "Where is data stored (servers, cloud, devices)?",
                "Who has access to raw vs. aggregated data?",
                "How is data transmitted between systems?",
                "What encryption is used (at rest, in transit)?",
                "How are backups secured?",
                "What is the data retention schedule?",
                "How is data destroyed at end of retention?",
                "Are there third-party vendors? How are they vetted?",
                "Is there a data breach response plan?"
            ],
            "security_risks": [
                "Unencrypted sensitive data",
                "Weak authentication (no 2FA, weak passwords)",
                "Data stored on unsecured devices or servers",
                "Unencrypted data transmission",
                "No access audit logs",
                "Undefined retention periods",
                "Insecure disposal methods",
                "Unvetted third-party services",
                "No breach notification plan",
                "Data on portable media without encryption",
                "Shared credentials or accounts",
                "Cloud storage without proper controls"
            ]
        }
    
    def _get_default_criteria(self) -> Dict:
        """Default data security criteria."""
        return self._extract_relevant_criteria({})
    
    def build_prompt(self, materials: Dict[str, Any]) -> str:
        """Build data security-focused prompt."""
        base_prompt = super().build_prompt(materials)
        
        security_specific = """

SPECIFIC DATA SECURITY FOCUS AREAS:

1. **Collection Security**:
   - Are data collection tools secure (HTTPS, encryption)?
   - Is data validated and sanitized on input?
   - Are there injection or XSS vulnerabilities?
   - Are sessions secure and properly managed?

2. **Storage Security**:
   - Where is data stored? Is it encrypted at rest?
   - Are databases secured and access-controlled?
   - Are there regular backups? How are they secured?
   - Physical security of storage location?
   - Is cloud storage HIPAA/FERPA compliant if needed?

3. **Transmission Security**:
   - Is HTTPS/TLS used for all data transmission?
   - Are API endpoints authenticated and authorized?
   - Is data encrypted during transmission?
   - Are there secure file transfer protocols?

4. **Access Controls**:
   - Role-based access control implemented?
   - Strong authentication (passwords, MFA)?
   - Are access credentials secured?
   - Is access logged and audited?
   - Principle of least privilege enforced?

5. **Data Lifecycle**:
   - Clear retention schedule defined?
   - Secure deletion/destruction procedures?
   - Data minimization practiced?
   - Regular security reviews conducted?

6. **Third-Party & Vendor Security**:
   - Are third-party services vetted for security?
   - Data processing agreements in place?
   - Compliance certifications verified?
   - Data residency requirements met?

7. **Incident Response**:
   - Is there a data breach response plan?
   - Are notification procedures defined?
   - Is there continuous monitoring for breaches?
   - Are security incidents logged?

Flag any unencrypted sensitive data, weak access controls, undefined retention policies,
or use of unsecured third-party services.
"""
        
        return base_prompt + security_specific








