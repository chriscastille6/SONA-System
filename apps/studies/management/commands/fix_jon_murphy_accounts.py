"""
Management command to fix Jon Murphy accounts - merge test account into real account.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.studies.models import ProtocolSubmission, CollegeRepresentative


class Command(BaseCommand):
    help = 'Merge Jon Murphy test account into real jonathan.murphy@nicholls.edu account'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Fixing Jon Murphy Accounts...\n')
        
        # Find the real account
        real_jon = User.objects.filter(email='jonathan.murphy@nicholls.edu').first()
        
        # Find test accounts
        test_jons = User.objects.filter(
            email__icontains='murphy'
        ).exclude(email='jonathan.murphy@nicholls.edu')
        
        if not real_jon:
            self.stdout.write(self.style.ERROR('✗ Real account (jonathan.murphy@nicholls.edu) not found'))
            return
        
        self.stdout.write(f'✓ Found real account: {real_jon.email}')
        self.stdout.write(f'  Name: {real_jon.get_full_name()}')
        self.stdout.write(f'  Role: {real_jon.role}')
        
        if not test_jons.exists():
            self.stdout.write(self.style.SUCCESS('\n✓ No test accounts to merge'))
            return
        
        for test_jon in test_jons:
            self.stdout.write(f'\n📋 Merging test account: {test_jon.email}')
            
            # Transfer college rep assignment
            reps = CollegeRepresentative.objects.filter(representative=test_jon)
            for rep in reps:
                self.stdout.write(f'  → Transferring College Rep: {rep.get_college_display()}')
                rep.representative = real_jon
                rep.save()
            
            # Transfer protocol submissions (as college_rep)
            subs = ProtocolSubmission.objects.filter(college_rep=test_jon)
            count = subs.count()
            if count > 0:
                self.stdout.write(f'  → Transferring {count} protocol submission(s)')
                subs.update(college_rep=real_jon)
            
            # Transfer protocol submissions (as decided_by)
            decided = ProtocolSubmission.objects.filter(decided_by=test_jon)
            count = decided.count()
            if count > 0:
                self.stdout.write(f'  → Transferring {count} decision(s)')
                decided.update(decided_by=real_jon)
            
            # Transfer protocol submissions (as chair_reviewer)
            chair = ProtocolSubmission.objects.filter(chair_reviewer=test_jon)
            count = chair.count()
            if count > 0:
                self.stdout.write(f'  → Transferring {count} chair assignment(s)')
                chair.update(chair_reviewer=real_jon)
            
            # Transfer reviewer assignments
            from apps.studies.models import IRBReviewerAssignment
            assignments = IRBReviewerAssignment.objects.filter(reviewer=test_jon)
            count = assignments.count()
            if count > 0:
                self.stdout.write(f'  → Transferring {count} reviewer assignment(s)')
                assignments.update(reviewer=real_jon)
            
            # Deactivate test account (don't delete to preserve any audit trail)
            test_jon.is_active = False
            test_jon.save()
            self.stdout.write(f'  → Deactivated test account: {test_jon.email}')
        
        # Ensure real account has correct settings
        real_jon.role = 'irb_member'
        real_jon.is_staff = True
        real_jon.is_active = True
        real_jon.save()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Jon Murphy accounts merged successfully!'))
        self.stdout.write(f'\nJon Murphy can now log in with:')
        self.stdout.write(f'  Email: jonathan.murphy@nicholls.edu')
        self.stdout.write(f'  Password: temp_password_change_me')
        
        # Show final state
        self.stdout.write('\n📊 Final State:')
        rep = CollegeRepresentative.objects.filter(representative=real_jon).first()
        if rep:
            self.stdout.write(f'  College Rep: {rep.get_college_display()}')
        
        subs = ProtocolSubmission.objects.filter(college_rep=real_jon)
        self.stdout.write(f'  Protocol Assignments: {subs.count()}')
        for sub in subs:
            self.stdout.write(f'    - {sub.submission_number or "Draft"}: {sub.study.title} ({sub.get_decision_display()})')
