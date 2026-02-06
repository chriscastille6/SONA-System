"""
Utility functions for IRB protocol submission workflow.
"""
from django.conf import settings
from apps.studies.models import CollegeRepresentative, ProtocolSubmission, Study


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
    
    Args:
        submission: ProtocolSubmission instance
        
    Returns:
        CollegeRepresentative instance or None
    """
    # Get researcher's department
    researcher = submission.submitted_by or submission.study.researcher
    if not researcher:
        return None
    
    profile = getattr(researcher, 'profile', None)
    if not profile:
        return None
    
    department_name = getattr(profile, 'department', None)
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
