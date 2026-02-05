"""
Management command to create the approved protocol submission record
for the Total Rewards Optimization (TRO) / Conjoint Analysis study.
"""
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import datetime
from apps.accounts.models import User, Profile
from apps.studies.models import Study, ProtocolSubmission, CollegeRepresentative


class Command(BaseCommand):
    help = 'Create approved protocol submission for TRO/Conjoint Analysis study'

    def handle(self, *args, **options):
        # Get the study
        try:
            study = Study.objects.get(slug='conjoint-analysis')
            self.stdout.write(self.style.SUCCESS(f'Found study: {study.title}'))
        except Study.DoesNotExist:
            self.stdout.write(self.style.ERROR('Study with slug "conjoint-analysis" not found'))
            return

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
            # Set department for college rep assignment
            profile, _ = Profile.objects.get_or_create(user=pi)
            profile.department = 'Business Administration'
            profile.save()
            self.stdout.write(self.style.SUCCESS(f'Created PI: {pi.get_full_name()}'))
        else:
            self.stdout.write(f'Found PI: {pi.get_full_name()}')

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
            self.stdout.write(self.style.SUCCESS(f'Created Co-I: {co_i.get_full_name()}'))
        else:
            self.stdout.write(f'Found Co-I: {co_i.get_full_name()}')

        # Get Jon Murphy (college rep)
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
                self.stdout.write(self.style.ERROR('Jon Murphy (college rep) not found'))
                return

        self.stdout.write(f'Found college rep: {jon_murphy.get_full_name()}')

        # Protocol number from Jon's letter
        protocol_number = 'IRBE20251031-005CBA'
        
        # Check if protocol submission already exists - use simple filter
        existing = ProtocolSubmission.objects.raw("""
            SELECT * FROM protocol_submissions 
            WHERE study_id = %s AND protocol_number = %s
        """, [str(study.id).replace('-', ''), protocol_number])
        
        existing_list = list(existing)
        if existing_list:
            existing = existing_list[0]
        else:
            existing = None

        if existing:
            self.stdout.write(self.style.SUCCESS(
                f'Protocol submission with number {protocol_number} already exists and is approved!'
            ))
            submission = existing
        else:
            # Create new protocol submission using raw SQL to avoid missing column errors
            from django.db import connection
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
            
            with connection.cursor() as cursor:
                # Insert using only columns that exist in the database
                cursor.execute("""
                    INSERT INTO protocol_submissions (
                        id, study_id, submission_number, version,
                        pi_suggested_review_type, review_type, college_rep_determination,
                        involves_deception, decision, protocol_number,
                        rejection_grounds, rnr_notes, approval_notes,
                        submitted_at, reviewed_at, decided_at,
                        college_rep_id, decided_by_id, submitted_by_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    submission_id, str(study.id).replace('-', ''), 'SUB-2025-001', 1,
                    'exempt', 'exempt', 'exempt',
                    0, 'approved', protocol_number,
                    '', '', approval_notes_text,
                    submitted_at_str, reviewed_at_str, decided_at_str,
                    str(jon_murphy.id).replace('-', ''), str(jon_murphy.id).replace('-', ''), str(pi.id).replace('-', '')
                ))
            
            # Get the created submission
            submission = ProtocolSubmission.objects.get(id=submission_id)
            self.stdout.write(self.style.SUCCESS('Created new protocol submission'))

        # Copy approval PDF to media directory
        base_dir = Path(__file__).parent.parent.parent.parent.parent  # Go up to project root
        approval_pdf_source = base_dir / 'apps' / 'studies' / 'assets' / 'irb' / 'conjoint-analysis' / 'meder_and_castille_approval.pdf'
        if approval_pdf_source.exists():
            media_dir = Path(settings.MEDIA_ROOT) / 'protocol_submissions' / 'approvals' / '2025' / '10'
            media_dir.mkdir(parents=True, exist_ok=True)
            approval_pdf_dest = media_dir / 'meder_and_castille_approval.pdf'
            shutil.copy2(approval_pdf_source, approval_pdf_dest)
            self.stdout.write(self.style.SUCCESS(
                f'Copied approval PDF to: {approval_pdf_dest.relative_to(settings.MEDIA_ROOT)}'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'Approval PDF not found at: {approval_pdf_source}'
            ))

        # Look for protocol PDF (IRB_Application_Consolidated_Agent_Protocol.pdf)
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
                f'Copied protocol PDF to: {protocol_pdf_dest.relative_to(settings.MEDIA_ROOT)}'
            ))
            
            # Store reference in approval notes or create a document link
            # You might want to add this to a ReviewDocument or similar model
        else:
            self.stdout.write(self.style.WARNING(
                'Protocol PDF (IRB_Application_Consolidated_Agent_Protocol.pdf) not found. '
                'Please ensure it exists in the TRO/conjoint-analysis folder.'
            ))

        # Update study IRB status
        study.irb_status = 'approved'
        study.irb_number = protocol_number  # Use exact number from Jon's letter
        study.irb_approved_by = jon_murphy
        study.irb_approved_at = timezone.make_aware(datetime(2025, 10, 31, 12, 0, 0))
        study.irb_approval_notes = submission.approval_notes
        study.save()

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Protocol submission created/updated:\n'
            f'   Submission Number: {submission.submission_number}\n'
            f'   Protocol Number: {submission.protocol_number}\n'
            f'   Study: {study.title}\n'
            f'   PI: {pi.get_full_name()}\n'
            f'   Co-I: {co_i.get_full_name()}\n'
            f'   Approved by: {jon_murphy.get_full_name()}\n'
            f'   Approval Date: October 31, 2025\n'
            f'   Review Type: Exempt\n'
        ))
