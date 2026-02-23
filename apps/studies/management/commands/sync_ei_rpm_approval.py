"""
Report and sync EI × RPM study approval from its protocol submission.

After Jon (or another IRB member) approves the EI × RPM protocol in the app,
the study is updated automatically. This command:
- Reports the current approval number and status for the EI × RPM study.
- If an approved submission exists but the study record is out of sync,
  updates the study to match the submission.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.studies.models import Study, ProtocolSubmission


class Command(BaseCommand):
    help = 'Report EI × RPM approval number and sync study from approved protocol submission'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sync',
            action='store_true',
            help='If approved submission exists but study is out of sync, update the study.',
        )

    def handle(self, *args, **options):
        try:
            study = Study.objects.get(slug='ei-rpm')
        except Study.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                'EI × RPM study (slug ei-rpm) not found.'
            ))
            return

        approved = (
            ProtocolSubmission.objects.filter(study=study, decision='approved')
            .order_by('-decided_at')
            .select_related('decided_by')
            .first()
        )

        self.stdout.write(f'Study: {study.title} (id={study.id})')
        self.stdout.write(f'  irb_status: {study.irb_status}')
        self.stdout.write(f'  irb_number: {study.irb_number or "(empty)"}')
        if study.irb_approved_at:
            self.stdout.write(f'  irb_approved_at: {study.irb_approved_at}')
        if study.irb_approved_by_id:
            self.stdout.write(f'  irb_approved_by: {study.irb_approved_by.get_full_name()}')

        if not approved:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(
                'No approved protocol submission found for this study. '
                'If Jon approved it in the app, the submission should have decision=approved and a protocol_number.'
            ))
            return

        protocol_number = approved.protocol_number or '(not set on submission)'
        self.stdout.write('')
        self.stdout.write('Approved protocol submission:')
        self.stdout.write(f'  submission id: {approved.id}')
        self.stdout.write(f'  protocol_number: {protocol_number}')
        self.stdout.write(f'  decided_at: {approved.decided_at}')
        if approved.decided_by_id:
            self.stdout.write(f'  decided_by: {approved.decided_by.get_full_name()}')

        needs_sync = (
            study.irb_status != 'approved'
            or (approved.protocol_number and study.irb_number != approved.protocol_number)
            or study.irb_approved_by_id != (approved.decided_by_id if approved.decided_by_id else None)
        )

        if not needs_sync:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Study record matches the approved submission.'))
            if approved.protocol_number:
                self.stdout.write(self.style.SUCCESS(f'EI × RPM approval number: {approved.protocol_number}'))
                self.stdout.write(
                    '  Participant consent page: set IRB_PROTOCOL_NUMBER in .env to show this number.'
                )
            return

        if not options['sync']:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(
                'Study record is out of sync with the approved submission. '
                'Run with --sync to update the study from the submission.'
            ))
            if approved.protocol_number:
                self.stdout.write(f'  Protocol number to set: {approved.protocol_number}')
            return

        study.irb_status = 'approved'
        if approved.protocol_number:
            study.irb_number = approved.protocol_number
        if approved.decided_by_id:
            study.irb_approved_by = approved.decided_by
        if approved.decided_at:
            study.irb_approved_at = approved.decided_at
        if getattr(approved, 'approval_notes', None):
            study.irb_approval_notes = approved.approval_notes
        study.save()
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Synced study from approved submission.'))
        self.stdout.write(self.style.SUCCESS(f'EI × RPM approval number: {study.irb_number}'))
        self.stdout.write('')
        self.stdout.write(
            'To show this number on the participant consent page, set in .env: '
            f'IRB_PROTOCOL_NUMBER={study.irb_number}'
        )
