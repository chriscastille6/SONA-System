"""
Utility functions for IRB protocol submission workflow.
"""
import json
from pathlib import Path
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from apps.studies.models import CollegeRepresentative, ProtocolSubmission, Study

# ProtocolSubmission text/char fields that can be loaded from protocol.json
PROTOCOL_JSON_FIELDS = [
    'protocol_description', 'population_description', 'research_procedures',
    'research_objectives', 'research_questions', 'educational_justification',
    'recruitment_method', 'recruitment_script', 'inclusion_criteria', 'exclusion_criteria',
    'benefits_to_subjects', 'benefits_to_others', 'benefits_to_society',
    'payment_compensation', 'costs_to_subjects',
    'review_type_justification', 'exemption_category', 'expedited_category',
    'risk_statement', 'risk_mitigation',
    'data_collection_methods', 'data_storage', 'confidentiality_procedures',
    'data_retention', 'data_access',
    'consent_procedures',
    'estimated_start_date', 'estimated_completion_date', 'funding_source',
    'pi_name', 'pi_title', 'pi_department', 'pi_email', 'pi_phone',
    'co_investigators', 'citi_training_completion', 'previous_protocol_number',
    'data_monitoring_plan', 'oversight_procedures',
    'publication_plan', 'data_sharing_plan', 'participant_access_to_results',
    'appendices_notes', 'study_contact_name', 'study_contact_email', 'study_contact_phone',
    'irb_contact_notes', 'suggested_reviewers',
]


def create_or_update_protocol_from_json(study, protocol_path, researcher):
    """
    Create or update a draft ProtocolSubmission from a protocol.json file.
    Used by add_*_study_online commands so protocol details are visible for review.

    Args:
        study: Study instance
        protocol_path: Path to protocol.json (or protocol config dict)
        researcher: User who is the PI/submitted_by

    Returns:
        ProtocolSubmission (draft) or None if protocol_path missing/invalid
    """
    if isinstance(protocol_path, dict):
        data = protocol_path
    else:
        path = Path(protocol_path)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

    draft = ProtocolSubmission.objects.filter(
        study=study, status='draft'
    ).order_by('-version').first()

    if draft:
        submission = draft
    else:
        submission = ProtocolSubmission.objects.create(
            study=study,
            status='draft',
            submitted_by=researcher,
            pi_suggested_review_type=data.get('pi_suggested_review_type', 'exempt'),
            review_type=data.get('review_type', 'exempt'),
        )

    # Required/standard fields
    submission.pi_suggested_review_type = data.get('pi_suggested_review_type', 'exempt')
    submission.review_type = data.get('review_type', 'exempt')
    submission.exemption_category = data.get('exemption_category', 'D')
    submission.involves_deception = data.get('involves_deception', False)
    submission.funding_source = data.get('funding_source', 'No external funding. Internal research project.')
    submission.continuation_of_previous = data.get('continuation_of_previous', False)
    submission.involves_vulnerable_populations = data.get('involves_vulnerable_populations', False)
    submission.involves_international_research = data.get('involves_international_research', False)
    submission.financial_interest_none = data.get('financial_interest_none', True)

    # Dates (use strings or compute from today)
    today = timezone.now().date()
    if data.get('estimated_start_date'):
        submission.estimated_start_date = data['estimated_start_date']
    else:
        submission.estimated_start_date = str((today + timedelta(days=14)).strftime('%Y-%m-%d'))
    if data.get('estimated_completion_date'):
        submission.estimated_completion_date = data['estimated_completion_date']
    else:
        submission.estimated_completion_date = str((today + timedelta(days=180)).strftime('%Y-%m-%d'))

    # PI info from researcher if not in JSON
    submission.pi_name = data.get('pi_name') or (researcher.get_full_name() or researcher.email)
    submission.pi_email = data.get('pi_email') or researcher.email
    submission.pi_title = data.get('pi_title', '')
    submission.pi_department = data.get('pi_department', '')
    submission.pi_phone = data.get('pi_phone', '')
    submission.co_investigators = data.get('co_investigators', 'None')
    submission.citi_training_completion = data.get(
        'citi_training_completion',
        'Principal Investigator has completed CITI training in Human Subjects Research (Social/Behavioral Research).'
    )

    # Copy all text fields from JSON (allow empty strings)
    for field in PROTOCOL_JSON_FIELDS:
        if field in data and hasattr(submission, field):
            val = data[field]
            if val is not None:
                setattr(submission, field, val if isinstance(val, str) else str(val))

    submission.save()

    # Assign college rep so IRB reviewers (e.g. Jon Murphy) can see the protocol
    assign_college_rep(submission)

    return submission


def get_college_from_department(department):
    """
    Map department name to college code.
    
    Args:
        department: Department name from user profile
        
    Returns:
        College code or None
    """
    if not department:
        return None
    
    department_lower = department.lower()
    
    # College of Business Administration
    # Includes: Business, Accounting, Finance, Marketing, Management (including "Management and Marketing")
    if any(term in department_lower for term in ['business', 'accounting', 'finance', 'marketing', 'management', 'economics']):
        return 'business'
    
    # College of Education and Behavioral Sciences
    if any(term in department_lower for term in ['education', 'psychology', 'counseling', 'behavioral']):
        return 'education'
    
    # College of Liberal Arts
    if any(term in department_lower for term in ['liberal arts', 'english', 'history', 'philosophy', 'sociology', 'political science']):
        return 'liberal_arts'
    
    # College of Sciences & Technology
    if any(term in department_lower for term in ['science', 'technology', 'computer', 'engineering', 'biology', 'chemistry', 'physics', 'mathematics', 'math']):
        return 'sciences'
    
    # Department of Nursing
    if 'nursing' in department_lower:
        return 'nursing'
    
    return None


def assign_college_rep(submission):
    """
    Assign college representative based on researcher's department.
    Uses researcher profile first; falls back to submission.pi_department (from protocol JSON).

    Args:
        submission: ProtocolSubmission instance

    Returns:
        CollegeRepresentative instance or None
    """
    department_name = None
    researcher = submission.submitted_by
    if not researcher and submission.study_id:
        try:
            researcher = submission.study.researcher
        except Exception:
            pass
    if researcher:
        profile = getattr(researcher, 'profile', None)
        if profile:
            department_name = getattr(profile, 'department', None)
    # Fallback: use pi_department from protocol (e.g. protocols loaded from JSON)
    if not department_name and getattr(submission, 'pi_department', None):
        department_name = submission.pi_department
    if not department_name:
        return None
    
    # Get college code
    college_code = get_college_from_department(department_name)
    if not college_code:
        return None
    
    # Find college representative
    college_rep = CollegeRepresentative.objects.filter(
        college=college_code,
        active=True
    ).first()
    
    if college_rep and college_rep.representative:
        submission.college_rep = college_rep.representative
        submission.save(update_fields=['college_rep'])
        return college_rep
    
    return None


def route_submission(submission):
    """
    Route submission based on review type and deception flag.
    
    Args:
        submission: ProtocolSubmission instance
        
    Returns:
        Updated submission
    """
    # If deception involved, route to chair
    if submission.involves_deception:
        chair = CollegeRepresentative.objects.filter(is_chair=True, active=True).first()
        if chair and chair.representative:
            submission.chair_reviewer = chair.representative
            submission.review_type = 'full'  # Deception always requires full review
            submission.save(update_fields=['chair_reviewer', 'review_type'])
        return submission
    
    # Set initial review type from PI suggestion
    submission.review_type = submission.pi_suggested_review_type
    
    # Route based on review type
    if submission.review_type == 'exempt':
        # Exempt can be approved by college rep
        # Already assigned above
        pass
    
    elif submission.review_type == 'expedited':
        # Expedited needs 2 reviewers + college rep
        # Reviewers will be assigned by college rep
        pass
    
    elif submission.review_type == 'full':
        # Full review goes to chair
        chair = CollegeRepresentative.objects.filter(is_chair=True, active=True).first()
        if chair and chair.representative:
            submission.chair_reviewer = chair.representative
            submission.save(update_fields=['chair_reviewer'])
    
    submission.save()
    return submission


def get_irb_chair():
    """Get the IRB Chair."""
    chair = CollegeRepresentative.objects.filter(is_chair=True, active=True).first()
    return chair.representative if chair else None
