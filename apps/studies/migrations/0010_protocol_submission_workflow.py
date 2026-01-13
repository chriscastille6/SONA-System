import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('studies', '0009_add_paper_copy_asset'),
    ]

    operations = [
        # Add deception flag to Study
        migrations.AddField(
            model_name='study',
            name='involves_deception',
            field=models.BooleanField(default=False, help_text='Protocol involves deception (requires chair review)'),
        ),
        
        # Create CollegeRepresentative model
        migrations.CreateModel(
            name='CollegeRepresentative',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('college', models.CharField(choices=[('business', 'College of Business Administration'), ('education', 'College of Education and Behavioral Sciences'), ('liberal_arts', 'College of Liberal Arts'), ('sciences', 'College of Sciences & Technology'), ('nursing', 'Department of Nursing')], max_length=50, unique=True)),
                ('is_chair', models.BooleanField(default=False, help_text='This representative is the IRB Chair')),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('representative', models.ForeignKey(help_text='IRB member serving as college representative', limit_choices_to={'role': 'irb_member'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='college_representative_assignments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'College Representative',
                'verbose_name_plural': 'College Representatives',
                'db_table': 'college_representatives',
                'ordering': ['college'],
            },
        ),
        
        # Create ProtocolSubmission model
        migrations.CreateModel(
            name='ProtocolSubmission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('submission_number', models.CharField(db_index=True, help_text='Auto-generated submission number', max_length=50, unique=True)),
                ('version', models.IntegerField(default=1, help_text='Submission version number')),
                ('pi_suggested_review_type', models.CharField(choices=[('exempt', 'Exempt'), ('expedited', 'Expedited Review'), ('full', 'Full Board Review')], help_text='Review type suggested by Primary Investigator', max_length=20)),
                ('college_rep_determination', models.CharField(blank=True, choices=[('exempt', 'Exempt'), ('expedited', 'Expedited Review'), ('full', 'Full Board Review')], help_text="College rep's determination of review type", max_length=20)),
                ('involves_deception', models.BooleanField(default=False, help_text='Protocol involves deception (requires chair review)')),
                ('review_type', models.CharField(choices=[('exempt', 'Exempt'), ('expedited', 'Expedited Review'), ('full', 'Full Board Review')], help_text='Actual review type (may differ from PI suggestion)', max_length=20)),
                ('decision', models.CharField(choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('revise_resubmit', 'Revise & Resubmit'), ('rejected', 'Rejected')], db_index=True, default='pending', help_text='Current decision status', max_length=20)),
                ('protocol_number', models.CharField(blank=True, db_index=True, help_text='IRB protocol number (issued upon approval)', max_length=100)),
                ('rejection_grounds', models.TextField(blank=True, help_text='Grounds for rejection (if rejected)')),
                ('rnr_notes', models.TextField(blank=True, help_text='Revise & resubmit notes and required changes')),
                ('approval_notes', models.TextField(blank=True, help_text='Approval notes and conditions')),
                ('submitted_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('decided_at', models.DateTimeField(blank=True, null=True)),
                ('ai_review', models.ForeignKey(blank=True, help_text='Optional AI-assisted review', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='protocol_submission', to='studies.irbreview')),
                ('chair_reviewer', models.ForeignKey(blank=True, help_text='IRB Chair reviewing this submission', limit_choices_to={'role': 'irb_member'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chair_reviews', to=settings.AUTH_USER_MODEL)),
                ('college_rep', models.ForeignKey(blank=True, help_text='College representative assigned to this submission', limit_choices_to={'role': 'irb_member'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_submissions', to=settings.AUTH_USER_MODEL)),
                ('decided_by', models.ForeignKey(blank=True, help_text='IRB member who made the decision', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='decided_protocols', to=settings.AUTH_USER_MODEL)),
                ('reviewers', models.ManyToManyField(blank=True, help_text='IRB members assigned to review (for expedited reviews)', limit_choices_to={'role': 'irb_member'}, related_name='protocol_reviews', to=settings.AUTH_USER_MODEL)),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='protocol_submissions', to='studies.study')),
                ('submitted_by', models.ForeignKey(help_text='Primary Investigator who submitted', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submitted_protocols', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Protocol Submission',
                'verbose_name_plural': 'Protocol Submissions',
                'db_table': 'protocol_submissions',
                'ordering': ['-submitted_at'],
                'unique_together': {('study', 'version')},
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='protocolsubmission',
            index=models.Index(fields=['study', 'version'], name='protocol_s_study_version_idx'),
        ),
        migrations.AddIndex(
            model_name='protocolsubmission',
            index=models.Index(fields=['decision', 'submitted_at'], name='protocol_s_decision_submitted_idx'),
        ),
        migrations.AddIndex(
            model_name='protocolsubmission',
            index=models.Index(fields=['review_type', 'decision'], name='protocol_s_review_type_decision_idx'),
        ),
        migrations.AddIndex(
            model_name='protocolsubmission',
            index=models.Index(fields=['college_rep', 'decision'], name='protocol_s_college_rep_decision_idx'),
        ),
    ]
