"""
Management command to check what protocols Jon Murphy is assigned to review.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.studies.models import ProtocolSubmission, CollegeRepresentative


class Command(BaseCommand):
    help = 'Check what protocols Jon Murphy is assigned to and can approve'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Checking Jon Murphy Protocol Assignments...\n')
        
        # Find Jon Murphy
        jon_murphy = User.objects.filter(
            email__icontains='murphy'
        ).filter(role='irb_member').first()
        
        if not jon_murphy:
            self.stdout.write(self.style.ERROR('✗ Jon Murphy account not found'))
            return
        
        self.stdout.write(f'✓ Found: {jon_murphy.get_full_name()} ({jon_murphy.email})')
        
        # Check college rep assignment
        college_rep = CollegeRepresentative.objects.filter(
            representative=jon_murphy
        ).first()
        
        if college_rep:
            self.stdout.write(f'✓ College Representative for: {college_rep.get_college_display()}')
        else:
            self.stdout.write(self.style.WARNING('⚠ Not assigned as college representative'))
        
        # Get all protocol submissions
        self.stdout.write('\n' + '='*60)
        self.stdout.write('ALL PROTOCOL SUBMISSIONS IN SYSTEM:')
        self.stdout.write('='*60)
        
        all_submissions = ProtocolSubmission.objects.select_related(
            'study', 'study__researcher', 'college_rep'
        ).order_by('-submitted_at')
        
        if not all_submissions.exists():
            self.stdout.write(self.style.WARNING('No protocol submissions found in the system.'))
        else:
            for sub in all_submissions:
                self.stdout.write(f'\n📋 {sub.submission_number or "No number (draft?)"}')
                self.stdout.write(f'   Study: {sub.study.title}')
                self.stdout.write(f'   PI: {sub.study.researcher.get_full_name() if sub.study.researcher else "Unknown"}')
                self.stdout.write(f'   Status: {sub.get_status_display()}')
                self.stdout.write(f'   Decision: {sub.get_decision_display()}')
                self.stdout.write(f'   Review Type: {sub.get_review_type_display() if sub.review_type else "Not set"}')
                
                # College rep assignment
                if sub.college_rep:
                    if sub.college_rep == jon_murphy:
                        self.stdout.write(self.style.SUCCESS(f'   College Rep: {sub.college_rep.get_full_name()} ✓ (Jon Murphy)'))
                    else:
                        self.stdout.write(f'   College Rep: {sub.college_rep.get_full_name()}')
                else:
                    self.stdout.write(self.style.WARNING('   College Rep: Not assigned'))
                
                # Can Jon approve?
                can_approve = False
                reason = ""
                
                if sub.decision != 'pending':
                    reason = f"Already decided: {sub.get_decision_display()}"
                elif sub.college_rep != jon_murphy:
                    reason = "Jon is not the assigned college rep"
                elif sub.review_type == 'exempt':
                    can_approve = True
                    reason = "Exempt protocol - Jon can approve directly"
                elif sub.review_type == 'expedited':
                    can_approve = True
                    reason = "Expedited - Jon can approve or assign reviewers"
                elif sub.review_type == 'full':
                    reason = "Full board review - requires chair"
                else:
                    reason = "Review type not determined yet - Jon needs to make determination first"
                
                if can_approve:
                    self.stdout.write(self.style.SUCCESS(f'   Can Jon Approve? YES - {reason}'))
                else:
                    self.stdout.write(self.style.WARNING(f'   Can Jon Approve? NO - {reason}'))
        
        # Submissions specifically assigned to Jon
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SUBMISSIONS ASSIGNED TO JON MURPHY:')
        self.stdout.write('='*60)
        
        jon_submissions = ProtocolSubmission.objects.filter(
            college_rep=jon_murphy
        ).select_related('study', 'study__researcher')
        
        if not jon_submissions.exists():
            self.stdout.write(self.style.WARNING('\nNo submissions currently assigned to Jon Murphy.'))
            self.stdout.write('\nTo assign a submission to Jon, you need to:')
            self.stdout.write('1. Submit a protocol from the researcher dashboard')
            self.stdout.write('2. The system will auto-assign based on department')
            self.stdout.write('3. Or manually assign via admin')
        else:
            for sub in jon_submissions:
                self.stdout.write(f'\n✓ {sub.submission_number or "Draft"}: {sub.study.title}')
                self.stdout.write(f'  Decision: {sub.get_decision_display()}')
                self.stdout.write(f'  Review Type: {sub.get_review_type_display() if sub.review_type else "Not determined"}')
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SUMMARY:')
        self.stdout.write('='*60)
        self.stdout.write(f'Total submissions in system: {all_submissions.count()}')
        self.stdout.write(f'Assigned to Jon Murphy: {jon_submissions.count()}')
        pending_for_jon = jon_submissions.filter(decision='pending').count()
        self.stdout.write(f'Pending Jon\'s review: {pending_for_jon}')
