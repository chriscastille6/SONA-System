"""
IRB Analyzer - Orchestrates Multi-Agent Review

Coordinates multiple AI agents to perform comprehensive IRB review.
"""

import asyncio
import time
from typing import Dict, List, Any
from django.utils import timezone
from apps.studies.models import IRBReview, ReviewDocument, Study
from .agents import (
    EthicsAgent,
    PrivacyAgent,
    VulnerabilityAgent,
    DataSecurityAgent,
    ConsentAgent
)


class IRBAnalyzer:
    """Orchestrates multi-agent IRB review."""
    
    def __init__(self, review_id: str):
        """
        Initialize analyzer with review ID.
        
        Args:
            review_id: UUID of the IRBReview record
        """
        self.review = IRBReview.objects.get(id=review_id)
        self.agents = {
            'ethics': EthicsAgent(),
            'privacy': PrivacyAgent(),
            'vulnerability': VulnerabilityAgent(),
            'data_security': DataSecurityAgent(),
            'consent': ConsentAgent()
        }
        self.materials = {}
        self.start_time = None
    
    async def run_review(self) -> Dict[str, Any]:
        """
        Execute complete IRB review workflow.
        
        Returns:
            Dict containing summary of review results
        """
        self.start_time = time.time()
        
        try:
            # Update status
            self.review.status = 'in_progress'
            self.review.save(update_fields=['status'])
            
            # Step 1: Gather materials
            print(f"[{self.review.study.slug}] Gathering materials...")
            self.materials = await self.gather_materials()
            
            # Step 2: Run all agents in parallel
            print(f"[{self.review.study.slug}] Running {len(self.agents)} AI agents...")
            agent_results = await self._run_agents()
            
            # Step 3: Aggregate and categorize findings
            print(f"[{self.review.study.slug}] Aggregating findings...")
            self._categorize_findings(agent_results)
            
            # Step 4: Generate recommendations
            print(f"[{self.review.study.slug}] Generating recommendations...")
            self._generate_recommendations()
            
            # Step 5: Assess overall risk
            print(f"[{self.review.study.slug}] Assessing overall risk...")
            self._assess_overall_risk()
            
            # Step 6: Save results
            print(f"[{self.review.study.slug}] Saving results...")
            self._save_results()
            
            # Mark complete
            elapsed = int(time.time() - self.start_time)
            self.review.status = 'completed'
            self.review.completed_at = timezone.now()
            self.review.processing_time_seconds = elapsed
            self.review.save(update_fields=['status', 'completed_at', 'processing_time_seconds'])
            
            return {
                'success': True,
                'review_id': str(self.review.id),
                'version': self.review.version,
                'risk_level': self.review.overall_risk_level,
                'critical_issues': len(self.review.critical_issues),
                'moderate_issues': len(self.review.moderate_issues),
                'minor_issues': len(self.review.minor_issues),
                'processing_time': elapsed
            }
            
        except Exception as e:
            # Mark as failed
            self.review.status = 'failed'
            self.review.completed_at = timezone.now()
            self.review.save(update_fields=['status', 'completed_at'])
            
            return {
                'success': False,
                'error': str(e),
                'review_id': str(self.review.id)
            }
    
    async def gather_materials(self) -> Dict[str, Any]:
        """
        Gather study materials from uploads or OSF.
        
        Returns:
            Dict with extracted text from all materials
        """
        materials = {
            'study_info': {
                'title': self.review.study.title,
                'description': self.review.study.description,
                'mode': self.review.study.get_mode_display(),
                'duration_minutes': self.review.study.duration_minutes,
                'credit_value': str(self.review.study.credit_value),
            }
        }
        
        # Extract text from uploaded documents
        for doc in self.review.documents.all():
            content = self._extract_document_text(doc)
            materials[f'{doc.file_type}_document'] = content
        
        # If OSF repo URL provided, fetch materials
        if self.review.osf_repo_url:
            from .osf_client import OSFClient
            osf = OSFClient()
            osf_materials = await osf.fetch_repo_files(self.review.osf_repo_url)
            materials['osf_materials'] = osf_materials
        
        # Check if study has a protocol template (HTML)
        if self.review.study.slug:
            protocol_path = f'templates/projects/{self.review.study.slug}/protocol/index.html'
            from pathlib import Path
            from django.conf import settings
            full_path = Path(settings.BASE_DIR) / protocol_path
            if full_path.exists():
                with open(full_path, 'r') as f:
                    materials['protocol_html'] = f.read()
        
        return materials
    
    def _extract_document_text(self, doc: ReviewDocument) -> str:
        """
        Extract text from uploaded document.
        
        Args:
            doc: ReviewDocument instance
        
        Returns:
            Extracted text content
        """
        try:
            if doc.filename.endswith('.txt'):
                with open(doc.file.path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif doc.filename.endswith('.pdf'):
                # Use PyPDF2 for PDF extraction
                import PyPDF2
                with open(doc.file.path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = []
                    for page in reader.pages:
                        text.append(page.extract_text())
                    return '\n\n'.join(text)
            
            elif doc.filename.endswith(('.doc', '.docx')):
                # For Word documents, try python-docx
                try:
                    from docx import Document
                    doc_obj = Document(doc.file.path)
                    return '\n\n'.join([para.text for para in doc_obj.paragraphs])
                except ImportError:
                    return f"[Word document: {doc.filename} - install python-docx to extract]"
            
            elif doc.filename.endswith(('.html', '.htm')):
                with open(doc.file.path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            else:
                return f"[Unsupported file type: {doc.filename}]"
                
        except Exception as e:
            return f"[Error extracting {doc.filename}: {e}]"
    
    async def _run_agents(self) -> Dict[str, Dict]:
        """
        Run all agents in parallel.
        
        Returns:
            Dict mapping agent names to their results
        """
        # Create tasks for all agents
        tasks = {
            name: agent.analyze(self.materials)
            for name, agent in self.agents.items()
        }
        
        # Run concurrently
        results = {}
        for name, task in tasks.items():
            try:
                results[name] = await task
            except Exception as e:
                results[name] = {
                    'error': str(e),
                    'agent': name,
                    'findings': []
                }
        
        return results
    
    def _categorize_findings(self, agent_results: Dict[str, Dict]):
        """
        Categorize all findings by severity.
        
        Args:
            agent_results: Results from all agents
        """
        self.review.critical_issues = []
        self.review.moderate_issues = []
        self.review.minor_issues = []
        
        for agent_name, result in agent_results.items():
            # Store agent-specific analysis
            setattr(self.review, f'{agent_name}_analysis', result)
            
            # Categorize findings
            for finding in result.get('findings', []):
                issue = {
                    'agent': agent_name,
                    'issue_id': finding.get('issue_id', f'{agent_name}_{len(self.review.critical_issues)}'),
                    'category': finding.get('category', 'general'),
                    'description': finding.get('description', ''),
                    'recommendation': finding.get('recommendation', ''),
                    'affected_section': finding.get('affected_section', ''),
                }
                
                severity = finding.get('severity', 'minor').lower()
                if severity == 'critical':
                    self.review.critical_issues.append(issue)
                elif severity == 'moderate':
                    self.review.moderate_issues.append(issue)
                else:
                    self.review.minor_issues.append(issue)
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on all findings."""
        recommendations = []
        
        # Aggregate from all findings
        all_issues = (
            self.review.critical_issues +
            self.review.moderate_issues +
            self.review.minor_issues
        )
        
        # Group by category
        by_category = {}
        for issue in all_issues:
            category = issue.get('category', 'general')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(issue)
        
        # Generate category-level recommendations
        for category, issues in by_category.items():
            if len(issues) > 1:
                recommendations.append({
                    'category': category,
                    'recommendation': f'Address {len(issues)} issues in {category}',
                    'issue_ids': [i.get('issue_id') for i in issues],
                    'priority': 'high' if any(i in self.review.critical_issues for i in issues) else 'medium'
                })
        
        # Add specific recommendations from critical issues
        for issue in self.review.critical_issues:
            recommendations.append({
                'category': issue.get('category'),
                'recommendation': issue.get('recommendation'),
                'issue_ids': [issue.get('issue_id')],
                'priority': 'critical'
            })
        
        self.review.recommendations = recommendations
    
    def _assess_overall_risk(self):
        """Determine overall risk level based on aggregated findings."""
        if self.review.critical_issues:
            self.review.overall_risk_level = 'high'
        elif len(self.review.moderate_issues) >= 5:
            self.review.overall_risk_level = 'moderate'
        elif self.review.moderate_issues:
            self.review.overall_risk_level = 'low'
        else:
            self.review.overall_risk_level = 'minimal'
        
        # Check agent-specific risk assessments
        risk_levels = []
        for agent_name in self.agents.keys():
            analysis = getattr(self.review, f'{agent_name}_analysis', {})
            if analysis and 'risk_assessment' in analysis:
                risk_levels.append(analysis['risk_assessment'])
        
        # If any agent says 'high', overall is high
        if 'high' in risk_levels:
            self.review.overall_risk_level = 'high'
        elif 'moderate' in risk_levels and self.review.overall_risk_level == 'low':
            self.review.overall_risk_level = 'moderate'
    
    def _save_results(self):
        """Save all analysis results and metadata."""
        # Record AI model versions
        self.review.ai_model_versions = {
            agent_name: agent.model
            for agent_name, agent in self.agents.items()
        }
        
        # Save all fields
        self.review.save()








