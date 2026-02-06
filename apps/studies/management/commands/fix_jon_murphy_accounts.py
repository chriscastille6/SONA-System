"""
Management command to fix Jon Murphy accounts - merge test account into real account.
Ensures one canonical account (jonathan.murphy@nicholls.edu) and that it is the College of Business rep.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.studies.models import ProtocolSubmission, CollegeRepresentative


class Command(BaseCommand):
    help = 'Merge Jon Murphy test account into real jonathan.murphy@nicholls.edu and set as College of Business rep'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Fixing Jon Murphy Accounts...\n')
        
        canonical_email = 'jonathan.murphy@nicholls.edu'
        real_jon = User.objects.filter(email=canonical_email).first()
        
        # If no canonical account but e.g. jon.murphy@nicholls.edu exists, convert it
        if not real_jon:
            other = User.objects.filter(email__icontains='murphy').first()
            if other:
                self.stdout.write(
                    self.style.WARNING(
                        f'✗ No account {canonical_email}; converting {other.email} to canonical.'
                    )
                )
                other.email = canonical_email
                other.save(update_fields=['email'])
                real_jon = other
                self.stdout.write(f'✓ Renamed to {canonical_email}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ No Murphy account found. Create {canonical_email} or run setup_college_reps --create-users.')
                )
                return
        else:
            self.stdout.write(f'✓ Found real account: {real_jon.email}')
        
        self.stdout.write(f'  Name: {real_jon.get_full_name()}')
        self.stdout.write(f'  Role: {real_jon.role}')
        
        # Find test accounts (any murphy that is not the canonical)
        test_jons = User.objects.filter(
            email__icontains='murphy'
        ).exclude(email=canonical_email)
        
        if test_jons.exists():
            for test_jon in test_jons:
                self.stdout.write(f'\n📋 Merging test account: {test_jon.email}')
                reps = CollegeRepresentative.objects.filter(representative=test_jon)
                for rep in reps:
                    self.stdout.write(f'  → Transferring College Rep: {rep.get_college_display()}')
                    rep.representative = real_jon
                    rep.save()
                subs = ProtocolSubmission.objects.filter(college_rep=test_jon)
                count = subs.count()
                if count > 0:
                    self.stdout.write(f'  → Transferring {count} protocol submission(s)')
                    subs.update(college_rep=real_jon)
                decided = ProtocolSubmission.objects.filter(decided_by=test_jon)
                count = decided.count()
                if count > 0:
                    self.stdout.write(f'  → Transferring {count} decision(s)')
                    decided.update(decided_by=real_jon)
                chair = ProtocolSubmission.objects.filter(chair_reviewer=test_jon)
                count = chair.count()
                if count > 0:
                    self.stdout.write(f'  → Transferring {count} chair assignment(s)')
                    chair.update(chair_reviewer=real_jon)
                from apps.studies.models import IRBReviewerAssignment
                assignments = IRBReviewerAssignment.objects.filter(reviewer=test_jon)
                count = assignments.count()
                if count > 0:
                    self.stdout.write(f'  → Transferring {count} reviewer assignment(s)')
                    assignments.update(reviewer=real_jon)
                test_jon.is_active = False
                test_jon.save()
                self.stdout.write(f'  → Deactivated test account: {test_jon.email}')
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ No other Murphy accounts to merge'))

        # Ensure real account has correct settings
        real_jon.role = 'irb_member'
        real_jon.is_staff = True
        real_jon.is_active = True
        real_jon.save()

        # Ensure this account is the College of Business representative
        biz_rep, created = CollegeRepresentative.objects.get_or_create(
            college='business',
            defaults={'representative': real_jon, 'is_chair': False, 'active': True},
        )
        if not created and biz_rep.representative != real_jon:
            biz_rep.representative = real_jon
            biz_rep.active = True
            biz_rep.save()
            self.stdout.write(self.style.WARNING('  → Set College of Business rep to jonathan.murphy@nicholls.edu'))
        elif created:
            self.stdout.write(self.style.SUCCESS('  → Assigned as College of Business representative'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Jon Murphy accounts consolidated successfully!'))
        self.stdout.write(f'\nCanonical account (login):')
        self.stdout.write(f'  Email: jonathan.murphy@nicholls.edu')
        self.stdout.write(f'  (Set password in Admin or use password reset if needed.)')
        
        # Show final state
        self.stdout.write('\n📊 Final State:')
        rep = CollegeRepresentative.objects.filter(representative=real_jon).first()
        if rep:
            self.stdout.write(f'  College Rep: {rep.get_college_display()} ✓')
        
        subs = ProtocolSubmission.objects.filter(college_rep=real_jon)
        self.stdout.write(f'  Protocol Assignments: {subs.count()}')
        for sub in subs:
            self.stdout.write(f'    - {sub.submission_number or "Draft"}: {sub.study.title} ({sub.get_decision_display()})')
