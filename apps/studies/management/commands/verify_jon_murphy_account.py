"""
Management command to verify Jon Murphy's account setup.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User, Profile
from apps.studies.models import CollegeRepresentative, ProtocolSubmission


class Command(BaseCommand):
    help = 'Verify Jon Murphy account setup and permissions'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Verifying Jon Murphy Account Setup...\n')
        
        # Find Jon Murphy
        jon_murphy = User.objects.filter(
            email__icontains='murphy'
        ).filter(role='irb_member').first()
        
        if not jon_murphy:
            # Try to get from college rep assignment
            college_rep = CollegeRepresentative.objects.filter(
                college='business',
                active=True
            ).first()
            if college_rep and college_rep.representative:
                jon_murphy = college_rep.representative
            else:
                self.stdout.write(self.style.ERROR('✗ Jon Murphy account not found'))
                self.stdout.write('\nTo create the account, run:')
                self.stdout.write('  python manage.py add_tro_study_online')
                return
        
        # Verify account details
        self.stdout.write(f'✓ Found account: {jon_murphy.get_full_name()}')
        self.stdout.write(f'  Email: {jon_murphy.email}')
        self.stdout.write(f'  Role: {jon_murphy.role}')
        self.stdout.write(f'  Active: {jon_murphy.is_active}')
        self.stdout.write(f'  Staff: {jon_murphy.is_staff}')
        
        # Check profile
        try:
            profile = jon_murphy.profile
            self.stdout.write(f'  Department: {profile.department or "Not set"}')
        except Profile.DoesNotExist:
            self.stdout.write(self.style.WARNING('  ⚠ Profile not found'))
        
        # Check college rep assignment
        college_rep = CollegeRepresentative.objects.filter(
            representative=jon_murphy
        ).first()
        
        if college_rep:
            self.stdout.write(f'  College Rep: {college_rep.get_college_display()}')
            self.stdout.write(f'  Active Rep: {college_rep.active}')
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Not assigned as college representative'))
        
        # Check assigned submissions
        submissions = ProtocolSubmission.objects.filter(college_rep=jon_murphy)
        self.stdout.write(f'\n  Assigned Protocol Submissions: {submissions.count()}')
        for sub in submissions:
            self.stdout.write(f'    - {sub.submission_number or "Draft"}: {sub.study.title}')
            self.stdout.write(f'      Status: {sub.get_status_display()}, Decision: {sub.get_decision_display()}')
        
        # Test password (can't verify without knowing it, but can check if it's set)
        self.stdout.write('\n📝 Login Information:')
        self.stdout.write(f'  Email: {jon_murphy.email}')
        self.stdout.write('  Password: temp_password_change_me (default)')
        self.stdout.write('  Login URL: /hsirb/accounts/login/')
        
        # Summary
        self.stdout.write('\n✅ Account Verification Summary:')
        checks = [
            (jon_murphy.is_active, 'Account is active'),
            (jon_murphy.role == 'irb_member', 'Role is IRB member'),
            (college_rep is not None, 'Assigned as college representative'),
        ]
        
        all_ok = True
        for check, message in checks:
            if check:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {message}'))
            else:
                self.stdout.write(self.style.ERROR(f'  ✗ {message}'))
                all_ok = False
        
        if all_ok:
            self.stdout.write(self.style.SUCCESS('\n✅ Jon Murphy account is properly configured!'))
        else:
            self.stdout.write(self.style.WARNING('\n⚠️ Some issues found. Review the output above.'))
