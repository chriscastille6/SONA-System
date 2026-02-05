"""
Management command to add the approved TRO study to the online database.
Safe to run on production server - only adds study data, no code changes needed.
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
    help = 'Add approved TRO/Conjoint Analysis study to online database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Adding TRO Study to Online Database...\n'))
        
        # Get or create the study
        study, study_created = Study.objects.get_or_create(
            slug='conjoint-analysis',
            defaults={
                'title': 'Teaching the Theory of Optimal Fringe Benefits Using Conjoint Analysis',
                'description': (
                    'Educational conjoint-analysis exercise for Labor Economics students. '
                    'Participants review consent materials, complete an intake survey, work '
                    'through eight job-package choice tasks, and collaborate on designing an '
                    'optimal fringe benefits package under budget constraints.'
                ),
                'mode': 'online',
                'credit_value': 0,
                'is_active': True,
                'is_approved': True,
                'irb_status': 'pending',  # Will be updated to approved below
            }
        )
        
        if study_created:
            # Need to set researcher - get or create PI first
            pi_temp, _ = User.objects.get_or_create(
                email='martin.meder@nicholls.edu',
                defaults={
                    'first_name': 'Martin',
                    'last_name': 'Meder',
                    'role': 'researcher',
                    'is_active': True,
                }
            )
            study.researcher = pi_temp
            study.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created study: {study.title}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Found study: {study.title}'))

        # Get or create PI (Dr. Martin Meder)
        pi, pi_created = User.objects.get_or_create(
            email='martin.meder@nicholls.edu',
            defaults={
                'first_name': 'Martin',
                'last_name': 'Meder',
                'role': 'researcher',
                'is_active': True,
            }
        )
        if pi_created:
            pi.set_password('temp_password_change_me')
            pi.save()
            profile, _ = Profile.objects.get_or_create(user=pi)
            profile.department = 'Business Administration'
            profile.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created PI: {pi.get_full_name()}'))
        else:
            self.stdout.write(f'✓ Found PI: {pi.get_full_name()}')

        # Get or create Co-Investigator (Dr. Christopher Castille)
        co_i, co_i_created = User.objects.get_or_create(
            email='christopher.castille@nicholls.edu',
            defaults={
                'first_name': 'Christopher',
                'last_name': 'Castille',
                'role': 'researcher',
                'is_active': True,
            }
        )
        if co_i_created:
            co_i.set_password('temp_password_change_me')
            co_i.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created Co-I: {co_i.get_full_name()}'))
        else:
            self.stdout.write(f'✓ Found Co-I: {co_i.get_full_name()}')

        # Get or create Jon Murphy (college rep)
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
                # Create Jon Murphy if he doesn't exist
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
                    # Create profile
                    profile, _ = Profile.objects.get_or_create(user=jon_murphy)
                    profile.department = 'Business Administration'
                    profile.save()
                    self.stdout.write(self.style.SUCCESS(f'✓ Created Jon Murphy: {jon_murphy.get_full_name()}'))
                
                # Assign as college rep
                college_rep, rep_created = CollegeRepresentative.objects.get_or_create(
                    college='business',
                    defaults={
                        'representative': jon_murphy,
                        'is_chair': False,
                        'active': True,
                    }
                )
                if rep_created:
                    self.stdout.write(self.style.SUCCESS('✓ Assigned Jon Murphy as College Representative for Business'))
                else:
                    college_rep.representative = jon_murphy
                    college_rep.active = True
                    college_rep.save()
                    self.stdout.write(self.style.SUCCESS('✓ Updated college representative assignment'))

        self.stdout.write(f'✓ Found college rep: {jon_murphy.get_full_name()}')

        # Protocol number from Jon's letter
        protocol_number = 'IRBE20251031-005CBA'
        
        # Check if protocol submission already exists using raw SQL
        existing = None
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM protocol_submissions 
                WHERE study_id = %s AND protocol_number = %s
            """, [str(study.id).replace('-', ''), protocol_number])
            row = cursor.fetchone()
            if row:
                existing_id = row[0]
                try:
                    existing = ProtocolSubmission.objects.raw(
                        "SELECT * FROM protocol_submissions WHERE id = %s",
                        [existing_id]
                    )
                    existing = list(existing)[0] if existing else None
                except:
                    pass

        if existing:
            self.stdout.write(self.style.SUCCESS(
                f'✓ Protocol submission with number {protocol_number} already exists!'
            ))
            submission = existing
        else:
            # Create new protocol submission using raw SQL
            import uuid
            submission_id = str(uuid.uuid4()).replace('-', '')
            approval_notes_text = (
                'Approved by Jonathan Murphy, PhD, HSIRB College of Business Admin Representative. '
                'Period of approval: October 31, 2025 - October 31, 2026. '
                'Exempt approval based on Category I (Educational settings), anonymous data collection, '
                'and benign behavioral interventions.'
            )
            submitted_at_str = timezone.make_aware(datetime(2025, 10, 15, 12, 0, 0)).isoformat()
            reviewed_at_str = timezone.make_aware(datetime(2025, 10, 31, 12, 0, 0)).isoformat()
            decided_at_str = timezone.make_aware(datetime(2025, 10, 31, 12, 0, 0)).isoformat()
            
            # Use Django ORM to handle all required fields automatically
            try:
                submission = ProtocolSubmission.objects.create(
                    id=submission_id,
                    study=study,
                    submission_number='SUB-2025-001',
                    version=1,
                    pi_suggested_review_type='exempt',
                    review_type='exempt',
                    college_rep_determination='exempt',
                    involves_deception=False,
                    decision='approved',
                    protocol_number=protocol_number,
                    rejection_grounds='',
                    rnr_notes='',
                    approval_notes=approval_notes_text,
                    submitted_at=timezone.make_aware(datetime(2025, 10, 15, 12, 0, 0)),
                    reviewed_at=timezone.make_aware(datetime(2025, 10, 31, 12, 0, 0)),
                    decided_at=timezone.make_aware(datetime(2025, 10, 31, 12, 0, 0)),
                    college_rep=jon_murphy,
                    decided_by=jon_murphy,
                    submitted_by=pi,
                    status='submitted',
                    # Set required text fields to empty strings
                    benefits_to_others='',
                    benefits_to_subjects='',
                    benefits_to_society='',
                )
                self.stdout.write(self.style.SUCCESS('✓ Created new protocol submission via ORM'))
            except Exception as e:
                # Fallback to raw SQL if ORM fails
                self.stdout.write(self.style.WARNING(f'ORM failed: {e}. Using raw SQL with all required fields...'))
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO protocol_submissions (
                            id, study_id, submission_number, version,
                            pi_suggested_review_type, review_type, college_rep_determination,
                            involves_deception, decision, protocol_number,
                            rejection_grounds, rnr_notes, approval_notes,
                            submitted_at, reviewed_at, decided_at,
                            college_rep_id, decided_by_id, submitted_by_id, status,
                            benefits_to_others, benefits_to_subjects, benefits_to_society
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::boolean, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        submission_id, str(study.id).replace('-', ''), 'SUB-2025-001', 1,
                        'exempt', 'exempt', 'exempt',
                        False, 'approved', protocol_number,
                        '', '', approval_notes_text,
                        submitted_at_str, reviewed_at_str, decided_at_str,
                        str(jon_murphy.id).replace('-', ''), str(jon_murphy.id).replace('-', ''), 
                        str(pi.id).replace('-', ''), 'submitted',
                        '', '', ''  # Required text fields
                    ))
                # Get the created submission
                submission = ProtocolSubmission.objects.raw(
                    "SELECT * FROM protocol_submissions WHERE id = %s",
                    [submission_id]
                )
                submission = list(submission)[0] if submission else None
            

        # Copy approval PDF to media directory
        base_dir = Path(settings.BASE_DIR)
        approval_pdf_source = base_dir / 'apps' / 'studies' / 'assets' / 'irb' / 'conjoint-analysis' / 'meder_and_castille_approval.pdf'
        
        if approval_pdf_source.exists():
            media_dir = Path(settings.MEDIA_ROOT) / 'protocol_submissions' / 'approvals' / '2025' / '10'
            media_dir.mkdir(parents=True, exist_ok=True)
            approval_pdf_dest = media_dir / 'meder_and_castille_approval.pdf'
            shutil.copy2(approval_pdf_source, approval_pdf_dest)
            self.stdout.write(self.style.SUCCESS(
                f'✓ Copied approval PDF to: {approval_pdf_dest.relative_to(settings.MEDIA_ROOT)}'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'⚠ Approval PDF not found at: {approval_pdf_source}'
            ))

        # Look for protocol PDF
        protocol_pdf_source = None
        possible_locations = [
            base_dir / 'apps' / 'studies' / 'assets' / 'irb' / 'conjoint-analysis' / 'IRB_Application_Consolidated_Agent_Protocol.pdf',
            base_dir / 'apps' / 'studies' / 'assets' / 'irb' / 'conjoint-analysis' / 'Conjoint_Analysis_NonExempt_IRB_Application.pdf',
            base_dir / 'protocol_templates' / 'IRB_Application_Consolidated_Agent_Protocol.pdf',
        ]
        
        for location in possible_locations:
            if location.exists():
                protocol_pdf_source = location
                break
        
        if protocol_pdf_source:
            media_dir = Path(settings.MEDIA_ROOT) / 'protocol_submissions' / 'protocols' / '2025' / '10'
            media_dir.mkdir(parents=True, exist_ok=True)
            protocol_pdf_dest = media_dir / 'IRB_Application_Consolidated_Agent_Protocol.pdf'
            shutil.copy2(protocol_pdf_source, protocol_pdf_dest)
            self.stdout.write(self.style.SUCCESS(
                f'✓ Copied protocol PDF to: {protocol_pdf_dest.relative_to(settings.MEDIA_ROOT)}'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                '⚠ Protocol PDF not found. Please ensure it exists in the TRO/conjoint-analysis folder.'
            ))

        # Update study IRB status using raw SQL to avoid missing column errors
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
                timezone.make_aware(datetime(2025, 10, 31, 12, 0, 0)).isoformat(),
                submission.approval_notes if hasattr(submission, 'approval_notes') else approval_notes_text,
                str(study.id).replace('-', '')
            ))

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ TRO Study Successfully Added to Online Database!\n'
            f'   Submission Number: SUB-2025-001\n'
            f'   Protocol Number: {protocol_number}\n'
            f'   Study: {study.title}\n'
            f'   PI: {pi.get_full_name()}\n'
            f'   Co-I: {co_i.get_full_name()}\n'
            f'   Approved by: {jon_murphy.get_full_name()}\n'
            f'   Approval Date: October 31, 2025\n'
            f'   Review Type: Exempt\n'
        ))
