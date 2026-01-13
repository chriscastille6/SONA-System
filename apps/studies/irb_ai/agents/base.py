"""
Base Agent for IRB Review

Provides common functionality for all specialized agents.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from django.conf import settings


class BaseAgent:
    """Base class for all IRB review agents."""
    
    def __init__(self):
        self.criteria = self.load_criteria()
        self.provider = getattr(settings, 'IRB_AI_PROVIDER', 'anthropic')  # 'anthropic' or 'openai'
        self.model = getattr(settings, 'IRB_AI_MODEL', 'claude-3-5-sonnet-20241022')
        self.agent_name = self.__class__.__name__
        self.client = self._initialize_client()
    
    def load_criteria(self) -> Dict[str, Any]:
        """
        Load IRB criteria from IRB_Automation_Toolkit.
        
        Returns:
            Dict containing IRB review criteria specific to this agent's focus area.
        """
        toolkit_path = Path(settings.BASE_DIR).parent / 'IRB_Automation_Toolkit' / 'configs' / 'nicholls_hsirb_settings.json'
        
        if toolkit_path.exists():
            try:
                with open(toolkit_path, 'r') as f:
                    all_criteria = json.load(f)
                return self._extract_relevant_criteria(all_criteria)
            except Exception as e:
                print(f"Warning: Could not load IRB criteria: {e}")
                return self._get_default_criteria()
        
        return self._get_default_criteria()
    
    def _extract_relevant_criteria(self, all_criteria: Dict) -> Dict:
        """
        Extract criteria relevant to this agent.
        Override in subclasses to filter specific sections.
        """
        return all_criteria
    
    def _get_default_criteria(self) -> Dict:
        """
        Get default criteria if toolkit is not available.
        Override in subclasses for agent-specific defaults.
        """
        return {
            "general_principles": [
                "Respect for persons",
                "Beneficence",
                "Justice"
            ]
        }
    
    async def analyze(self, materials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze study materials for ethical issues.
        
        Args:
            materials: Dict containing protocol documents, consent forms, etc.
        
        Returns:
            Dict with findings, severity levels, and recommendations.
        """
        if not self.client:
            return self._placeholder_analysis()
        
        prompt = self.build_prompt(materials)
        
        try:
            response = await self._call_ai_api(prompt)
            return self.parse_findings(response)
        except Exception as e:
            return {
                'error': str(e),
                'agent': self.agent_name,
                'findings': []
            }
    
    def build_prompt(self, materials: Dict[str, Any]) -> str:
        """
        Build the prompt for AI analysis.
        Override in subclasses for agent-specific prompts.
        
        Args:
            materials: Study materials to analyze
        
        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            f"You are an expert IRB reviewer specializing in {self.get_focus_area()}.",
            "\n\nIRB REVIEW CRITERIA:",
            json.dumps(self.criteria, indent=2),
            "\n\nSTUDY MATERIALS TO REVIEW:",
            self._format_materials(materials),
            "\n\nINSTRUCTIONS:",
            "1. Review the study materials against the IRB criteria",
            "2. Identify any ethical concerns or issues",
            "3. Categorize each issue by severity: critical, moderate, or minor",
            "4. Provide specific recommendations for addressing each issue",
            "5. Reference specific sections of the materials where issues were found",
            "\n\nProvide your analysis in JSON format with the following structure:",
            """{
  "findings": [
    {
      "issue_id": "unique_id",
      "severity": "critical|moderate|minor",
      "category": "category_name",
      "description": "detailed description",
      "recommendation": "specific recommendation",
      "affected_section": "document and section reference"
    }
  ],
  "summary": "overall summary of findings",
  "risk_assessment": "minimal|low|moderate|high"
}"""
        ]
        
        return "\n".join(prompt_parts)
    
    def _format_materials(self, materials: Dict[str, Any]) -> str:
        """Format study materials for inclusion in prompt."""
        formatted = []
        
        for material_type, content in materials.items():
            if isinstance(content, str):
                formatted.append(f"\n--- {material_type.upper()} ---\n{content}")
            elif isinstance(content, dict):
                formatted.append(f"\n--- {material_type.upper()} ---\n{json.dumps(content, indent=2)}")
        
        return "\n".join(formatted)
    
    def _initialize_client(self):
        """Initialize the appropriate AI client based on provider setting."""
        if self.provider == 'anthropic':
            api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
            if api_key:
                from anthropic import Anthropic
                return Anthropic(api_key=api_key)
        elif self.provider == 'openai':
            api_key = getattr(settings, 'OPENAI_API_KEY', '')
            if api_key:
                from openai import OpenAI
                return OpenAI(api_key=api_key)
        
        return None  # No API configured
    
    async def _call_ai_api(self, prompt: str) -> str:
        """
        Call the AI API with the constructed prompt.
        Supports both Anthropic and OpenAI.
        
        Args:
            prompt: The full prompt to send
        
        Returns:
            API response text
        """
        if not self.client:
            raise ValueError("AI client not initialized - check API key configuration")
        
        if self.provider == 'anthropic':
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return message.content[0].text
        
        elif self.provider == 'openai':
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.choices[0].message.content
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def parse_findings(self, response: str) -> Dict[str, Any]:
        """
        Parse AI response into structured findings.
        
        Args:
            response: Raw API response text
        
        Returns:
            Structured findings dict
        """
        try:
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                findings = json.loads(json_str)
            else:
                findings = json.loads(response)
            
            # Add agent metadata
            findings['agent'] = self.agent_name
            findings['model'] = self.model
            
            return findings
            
        except json.JSONDecodeError:
            # Fallback: structure as plain text findings
            return {
                'agent': self.agent_name,
                'model': self.model,
                'raw_response': response,
                'findings': [{
                    'issue_id': 'parse_error',
                    'severity': 'moderate',
                    'category': 'analysis_error',
                    'description': 'Could not parse AI response as JSON',
                    'recommendation': 'Manual review recommended',
                    'affected_section': 'N/A'
                }],
                'summary': 'Response parsing failed',
                'risk_assessment': 'unknown'
            }
    
    def get_focus_area(self) -> str:
        """
        Get the focus area for this agent.
        Override in subclasses.
        """
        return "general ethical review"
    
    def _placeholder_analysis(self) -> Dict[str, Any]:
        """Return placeholder analysis when AI is not configured."""
        return {
            'agent': self.agent_name,
            'model': 'placeholder',
            'findings': [{
                'issue_id': 'placeholder',
                'severity': 'minor',
                'category': 'configuration',
                'description': 'AI analysis not configured - placeholder results',
                'recommendation': 'Configure ANTHROPIC_API_KEY to enable AI analysis',
                'affected_section': 'N/A'
            }],
            'summary': f'{self.agent_name} analysis requires API configuration',
            'risk_assessment': 'unknown'
        }

