"""
Management command to add the approved Goal Setting study to the online database.
Safe to run on production server - only adds study data, no code changes needed.

Protocol: IRB 2024-07-30-001 CBA (A Study in Decision Making)
PI: Dr. Christopher Castille
"""
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.db import connection
from datetime import datetime
from apps.accounts.models import User, Profile
from apps.studies.models import Study, ProtocolSubmission, CollegeRepresentative


class Command(BaseCommand):
    help = 'Add approved Goal Setting study (A Study in Decision Making) to online database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Adding Goal Setting Study to Online Database...\n'))

        # Get or create the study
        study, study_created = Study.objects.get_or_create(
            slug='goal-setting',
            defaults={
                'title': 'A Study in Decision Making',
                'description': (
                    'Replication of Schweitzer, Ordóñez, and Douma (2004) examining whether goal setting '
                    'motivates unethical behavior. Participants complete anagram tasks under different goal '
                    'conditions (do your best, mere goal, reward goal, personal goal) and have the opportunity '
                    'to overstate performance. Sponsored by ARIM (Advancement of Replications Initiative in Management).'
                ),
                'mode': 'lab',
                'credit_value': 0,
                'is_active': True,
                'is_approved': True,
                'irb_status': 'pending',  # Will be updated to approved below
                'osf_enabled': True,
                'osf_project_id': 'f5u39',
                'osf_link': 'https://osf.io/f5u39/',
            }
        )

        # Update OSF fields if study already exists
        if not study_created:
            if not study.osf_enabled or study.osf_link != 'https://osf.io/f5u39/':
                study.osf_enabled = True
                study.osf_project_id = 'f5u39'
                study.osf_link = 'https://osf.io/f5u39/'
                study.save(update_fields=['osf_enabled', 'osf_project_id', 'osf_link'])
                self.stdout.write(self.style.SUCCESS('✓ Updated OSF link: https://osf.io/f5u39/'))

        # PI: Dr. Christopher Castille
        pi, pi_created = User.objects.get_or_create(
            email='christopher.castille@nicholls.edu',
            defaults={
                'first_name': 'Christopher',
                'last_name': 'Castille',
                'role': 'researcher',
                'is_active': True,
            }
        )
        if pi_created:
            pi.set_password('temp_password_change_me')
            pi.save()
            profile, _ = Profile.objects.get_or_create(user=pi)
            profile.department = 'Management and Marketing'
            profile.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created PI: {pi.get_full_name()}'))
        else:
            self.stdout.write(f'✓ Found PI: {pi.get_full_name()}')

        if study_created:
            study.researcher = pi
            study.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created study: {study.title}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Found study: {study.title}'))
            if not study.researcher or study.researcher.email != 'christopher.castille@nicholls.edu':
                study.researcher = pi
                study.save()
                self.stdout.write(self.style.SUCCESS(f'  Updated researcher (PI) to: {pi.get_full_name()}'))

        # Co-investigators (for co_investigators field)
        co_i_emails = [
            'adrien.maught@nicholls.edu',
            'kaitlin.gravois@nicholls.edu',
            'ann-marie.castille@nicholls.edu',
        ]
        co_i_str = 'Mr. Adrien Maught, Mrs. Kaitlin Gravois, Dr. Ann-Marie R. Castille'

        # Get or create college rep (Business - Jon Murphy)
        jon_murphy = User.objects.filter(
            email__icontains='murphy'
        ).filter(role='irb_member').first()

        if not jon_murphy:
            college_rep = CollegeRepresentative.objects.filter(
                college='business',
                active=True
            ).first()
            if college_rep and college_rep.representative:
                jon_murphy = college_rep.representative
            else:
                self.stdout.write(self.style.WARNING('⚠ Jon Murphy not found, creating...'))
                jon_murphy, created = User.objects.get_or_create(
                    email='jon.murphy@nicholls.edu',
                    defaults={
                        'first_name': 'Jon',
                        'last_name': 'Murphy',
                        'role': 'irb_member',
                        'is_active': True,
                        'is_staff': True,
                    }
                )
                if created:
                    jon_murphy.set_password('temp_password_change_me')
                    jon_murphy.save()
                    profile, _ = Profile.objects.get_or_create(user=jon_murphy)
                    profile.department = 'Business Administration'
                    profile.save()
                college_rep, _ = CollegeRepresentative.objects.get_or_create(
                    college='business',
                    defaults={'representative': jon_murphy, 'is_chair': False, 'active': True}
                )
                if not college_rep.representative_id:
                    college_rep.representative = jon_murphy
                    college_rep.save()

        self.stdout.write(f'✓ Found college rep: {jon_murphy.get_full_name()}')

        protocol_number = 'IRB 2024-07-30-001 CBA'

        # Check if protocol submission already exists
        existing = ProtocolSubmission.objects.filter(
            study=study,
            protocol_number=protocol_number
        ).first()

        if existing:
            self.stdout.write(self.style.SUCCESS(
                f'✓ Protocol submission with number {protocol_number} already exists!'
            ))
            submission = existing
        else:
            approval_notes_text = (
                'Approved by HSIRB College of Business Administration Representative. '
                'Exempt under Category D (educational tests, anonymous data). '
                'Original approval July 2024. Addendum 1 (Procedural Modifications) approved.'
            )

            submission = ProtocolSubmission.objects.create(
                study=study,
                submission_number='SUB-2024-GS001',
                version=1,
                pi_suggested_review_type='exempt',
                review_type='exempt',
                college_rep_determination='exempt',
                involves_deception=True,  # Study involves mild deception (performance overstatement)
                decision='approved',
                protocol_number=protocol_number,
                rejection_grounds='',
                rnr_notes='',
                approval_notes=approval_notes_text,
                submitted_at=timezone.make_aware(datetime(2024, 7, 16, 12, 0, 0)),
                reviewed_at=timezone.make_aware(datetime(2024, 7, 30, 12, 0, 0)),
                decided_at=timezone.make_aware(datetime(2024, 7, 30, 12, 0, 0)),
                college_rep=jon_murphy,
                decided_by=jon_murphy,
                submitted_by=pi,
                status='submitted',
                benefits_to_others='',
                benefits_to_subjects='',
                benefits_to_society='',
                co_investigators=co_i_str,
            )
            self.stdout.write(self.style.SUCCESS('✓ Created new protocol submission'))

        # Copy approval PDF to media directory
        base_dir = Path(settings.BASE_DIR)
        approval_sources = [
            base_dir / 'apps' / 'studies' / 'assets' / 'irb' / 'goal-setting' / 'chris_castille_irb_approval_july_2024.pdf',
            base_dir / 'apps' / 'studies' / 'assets' / 'irb' / 'goal-setting' / 'Chris Castille IRB Approval letter July 2024.pdf',
        ]
        approval_pdf_source = None
        for p in approval_sources:
            if p.exists():
                approval_pdf_source = p
                break

        if approval_pdf_source:
            media_dir = Path(settings.MEDIA_ROOT) / 'protocol_submissions' / 'approvals' / '2024' / '07'
            media_dir.mkdir(parents=True, exist_ok=True)
            approval_pdf_dest = media_dir / 'chris_castille_goal_setting_approval_july_2024.pdf'
            shutil.copy2(approval_pdf_source, approval_pdf_dest)
            self.stdout.write(self.style.SUCCESS(
                f'✓ Copied approval PDF to: {approval_pdf_dest.relative_to(settings.MEDIA_ROOT)}'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                '⚠ Approval PDF not found. Copy to apps/studies/assets/irb/goal-setting/'
            ))

        # Copy addendum PDF if present
        addendum_source = base_dir / 'apps' / 'studies' / 'assets' / 'irb' / 'goal-setting' / 'addendum_1_procedural_modifications.pdf'
        if addendum_source.exists():
            media_dir = Path(settings.MEDIA_ROOT) / 'protocol_submissions' / 'amendments' / '2024' / '07'
            media_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(addendum_source, media_dir / 'addendum_1_procedural_modifications.pdf')
            self.stdout.write(self.style.SUCCESS('✓ Copied Addendum 1 PDF'))

        # Update study IRB status
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE studies
                SET irb_status = %s,
                    irb_number = %s,
                    irb_approved_by_id = %s,
                    irb_approved_at = %s,
                    irb_approval_notes = %s
                WHERE id = %s
            """, (
                'approved',
                protocol_number,
                str(jon_murphy.id).replace('-', ''),
                timezone.make_aware(datetime(2024, 7, 30, 12, 0, 0)).isoformat(),
                submission.approval_notes if hasattr(submission, 'approval_notes') else '',
                str(study.id).replace('-', '')
            ))

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Goal Setting Study Successfully Added to Online Database!\n'
            f'   Protocol Number: {protocol_number}\n'
            f'   Study: {study.title}\n'
            f'   PI: {pi.get_full_name()}\n'
            f'   Co-Is: {co_i_str}\n'
            f'   Approved by: {jon_murphy.get_full_name()}\n'
            f'   Approval Date: July 30, 2024\n'
            f'   Review Type: Exempt\n'
        ))
