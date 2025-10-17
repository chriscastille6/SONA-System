"""
Django management command to populate the database with demo/template data.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import random

from apps.accounts.models import User, Profile
from apps.courses.models import Course, Enrollment
from apps.studies.models import Study, Timeslot, Signup, Response
from apps.credits.models import CreditTransaction


class Command(BaseCommand):
    help = 'Creates template study with hypothetical participants, signups, and data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating demo data for SONA System...'))
        
        # Create admin user
        admin = self.create_admin()
        
        # Create users
        researcher = self.create_researcher()
        instructor = self.create_instructor()
        participants = self.create_participants()
        
        # Create course
        course = self.create_course(instructor)
        
        # Enroll participants
        enrollments = self.create_enrollments(course, participants)
        
        # Create study
        study = self.create_study(researcher)
        
        # Create timeslots
        timeslots = self.create_timeslots(study)
        
        # Create signups
        signups = self.create_signups(timeslots, participants)
        
        # Create credit transactions
        self.create_credit_transactions(signups, course)
        
        # Create some protocol responses
        self.create_responses(study)
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✓ Demo data created successfully!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'  • Administrator: {admin.email} (password: admin123)')
        self.stdout.write(f'  • Researcher: {researcher.email} (password: demo123)')
        self.stdout.write(f'  • Instructor: {instructor.email} (password: demo123)')
        self.stdout.write(f'  • Participants: {len(participants)} students')
        self.stdout.write(f'  • Course: {course.code} - {course.name}')
        self.stdout.write(f'  • Study: {study.title}')
        self.stdout.write(f'  • Timeslots: {len(timeslots)} sessions')
        self.stdout.write(f'  • Signups: {len(signups)} total')
        self.stdout.write(f'  • Protocol Responses: 12')
        self.stdout.write('\n🌐 Access the system at http://localhost:8000')
        self.stdout.write(f'🔐 Admin panel at http://localhost:8000/admin/')
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

    def create_admin(self):
        """Create administrator/superuser account."""
        email = 'admin@nicholls.edu'
        
        # Only create if doesn't exist (don't delete existing admin)
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            self.stdout.write(f'  ✓ Administrator already exists: {user.get_full_name()}')
        else:
            user = User.objects.create_superuser(
                email=email,
                password='admin123',
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            self.stdout.write(f'  ✓ Created administrator: {user.get_full_name()}')
        
        return user

    def create_researcher(self):
        """Create a researcher user."""
        email = 'researcher@nicholls.edu'
        
        # Delete if exists
        User.objects.filter(email=email).delete()
        
        user = User.objects.create_user(
            email=email,
            password='demo123',
            first_name='Dr. Sarah',
            last_name='Martinez',
            role='researcher',
            email_verified_at=timezone.now()
        )
        
        # Update the auto-created profile
        profile = user.profile
        profile.department = 'Psychology'
        profile.lab_name = 'Cognitive Neuroscience Lab'
        profile.phone = '985-448-4567'
        profile.save()
        
        self.stdout.write(f'  ✓ Created researcher: {user.get_full_name()}')
        return user

    def create_instructor(self):
        """Create an instructor user."""
        email = 'instructor@nicholls.edu'
        
        # Delete if exists
        User.objects.filter(email=email).delete()
        
        user = User.objects.create_user(
            email=email,
            password='demo123',
            first_name='Dr. James',
            last_name='Thompson',
            role='instructor',
            email_verified_at=timezone.now()
        )
        
        # Update the auto-created profile
        profile = user.profile
        profile.department = 'Psychology'
        profile.phone = '985-448-4568'
        profile.save()
        
        self.stdout.write(f'  ✓ Created instructor: {user.get_full_name()}')
        return user

    def create_participants(self):
        """Create multiple participant users."""
        participants_data = [
            ('Emily', 'Johnson', 'emily.johnson@my.nicholls.edu', '2003-05-15', 'F'),
            ('Michael', 'Brown', 'michael.brown@my.nicholls.edu', '2002-08-22', 'M'),
            ('Sophia', 'Davis', 'sophia.davis@my.nicholls.edu', '2003-01-10', 'F'),
            ('James', 'Wilson', 'james.wilson@my.nicholls.edu', '2002-11-30', 'M'),
            ('Olivia', 'Garcia', 'olivia.garcia@my.nicholls.edu', '2003-03-18', 'F'),
            ('William', 'Martinez', 'william.martinez@my.nicholls.edu', '2002-07-25', 'M'),
            ('Ava', 'Rodriguez', 'ava.rodriguez@my.nicholls.edu', '2003-09-12', 'F'),
            ('Alexander', 'Lee', 'alexander.lee@my.nicholls.edu', '2002-04-08', 'M'),
            ('Isabella', 'Walker', 'isabella.walker@my.nicholls.edu', '2003-06-20', 'F'),
            ('Ethan', 'Hall', 'ethan.hall@my.nicholls.edu', '2002-12-05', 'M'),
            ('Mia', 'Young', 'mia.young@my.nicholls.edu', '2003-02-14', 'F'),
            ('Daniel', 'King', 'daniel.king@my.nicholls.edu', '2002-10-28', 'M'),
        ]
        
        participants = []
        
        for first, last, email, dob, gender in participants_data:
            # Delete if exists
            User.objects.filter(email=email).delete()
            
            user = User.objects.create_user(
                email=email,
                password='demo123',
                first_name=first,
                last_name=last,
                role='participant',
                email_verified_at=timezone.now()
            )
            
            # Update the auto-created profile
            profile = user.profile
            profile.student_id = f'N{random.randint(10000000, 99999999)}'
            profile.date_of_birth = date.fromisoformat(dob)
            profile.gender = gender
            profile.languages = ['en']
            profile.no_show_count = 0
            profile.save()
            
            participants.append(user)
        
        self.stdout.write(f'  ✓ Created {len(participants)} participants')
        return participants

    def create_course(self, instructor):
        """Create a course."""
        # Delete if exists
        Course.objects.filter(code='PSYC-101', term='2025-Fall').delete()
        
        course = Course.objects.create(
            code='PSYC-101',
            name='Introduction to Psychology',
            term='2025-Fall',
            section='01',
            instructor=instructor,
            credits_required=Decimal('3.0'),
            is_active=True
        )
        
        self.stdout.write(f'  ✓ Created course: {course}')
        return course

    def create_enrollments(self, course, participants):
        """Enroll participants in the course."""
        enrollments = []
        for participant in participants:
            enrollment = Enrollment.objects.create(
                course=course,
                participant=participant
            )
            enrollments.append(enrollment)
        
        self.stdout.write(f'  ✓ Enrolled {len(enrollments)} students in {course.code}')
        return enrollments

    def create_study(self, researcher):
        """Create a comprehensive study."""
        # Delete if exists
        Study.objects.filter(title='Decision Making Under Uncertainty').delete()
        
        study = Study.objects.create(
            title='Decision Making Under Uncertainty',
            description="""
**Study Overview:**
This study investigates how people make decisions when facing uncertain outcomes. You will be presented with a series of choices between different options, each with varying probabilities of success.

**What You'll Do:**
- Complete a brief demographic questionnaire (2 minutes)
- Make decisions in 30 hypothetical scenarios (20 minutes)
- Answer questions about your decision-making strategy (3 minutes)

**Duration:** Approximately 25-30 minutes

**Location:** Psychology Building, Room 215

**What to Expect:**
The study will be conducted on a computer. You'll read scenarios and make choices by clicking buttons. There are no right or wrong answers—we're interested in your natural decision-making process.

**Eligibility:**
- Must be 18 years or older
- Must be enrolled in PSYC-101
- Normal or corrected-to-normal vision

**Compensation:**
You will receive 0.5 research credits upon completion of the study.

**Privacy:**
All responses are confidential and will be stored securely. Your data will be identified only by a participant code, not your name.
            """.strip(),
            mode='lab',
            researcher=researcher,
            credit_value=Decimal('0.5'),
            is_active=True,
            is_approved=True,
            eligibility={
                'age_min': 18,
                'courses': ['PSYC-101'],
            },
            consent_text="""
**CONSENT TO PARTICIPATE IN RESEARCH**

**Study Title:** Decision Making Under Uncertainty

**Principal Investigator:** Dr. Sarah Martinez, Psychology Department

**Purpose:**
You are invited to participate in a research study examining how people make decisions when outcomes are uncertain.

**Procedures:**
If you agree to participate, you will:
1. Complete a brief demographic questionnaire
2. Make choices in 30 hypothetical decision scenarios
3. Answer questions about your decision-making process

The entire study takes approximately 25-30 minutes.

**Risks and Benefits:**
There are no foreseeable risks beyond those encountered in daily life. You may gain insight into your own decision-making style. Your participation contributes to scientific understanding of human cognition.

**Confidentiality:**
Your responses will be kept confidential. Data will be stored securely and identified only by participant codes. Only the research team will have access to the data.

**Voluntary Participation:**
Your participation is completely voluntary. You may withdraw at any time without penalty. Your decision will not affect your course grade or standing at the university.

**Questions:**
If you have questions about this study, contact Dr. Sarah Martinez at sarah.martinez@nicholls.edu or 985-448-4567.

**Consent:**
By clicking "I Agree" below, you indicate that:
- You have read and understood this consent form
- You are 18 years or older
- You voluntarily agree to participate in this study
            """.strip(),
            external_link='',
            irb_status='approved',
            irb_number='IRB-2025-089',
            irb_expiration=date(2026, 10, 15),
            osf_enabled=True,
            osf_project_id='8xk2d',
            osf_link='https://osf.io/8xk2d/',
            min_sample_size=30,
            bf_threshold=10.0,
            monitoring_enabled=True,
            monitoring_notified=False,
            duration_minutes=30,
            max_participants=50
        )
        
        self.stdout.write(f'  ✓ Created study: {study.title}')
        return study

    def create_timeslots(self, study):
        """Create multiple timeslots for the study."""
        timeslots = []
        base_date = timezone.now().date()
        
        # Create timeslots for next 3 weeks (past and future)
        # Week 1 (past week - for demo of completed sessions)
        for day_offset in [-7, -6, -5, -4, -3]:
            for hour in [10, 14, 16]:
                start = timezone.make_aware(
                    timezone.datetime.combine(
                        base_date + timedelta(days=day_offset),
                        timezone.datetime.min.time().replace(hour=hour)
                    )
                )
                end = start + timedelta(minutes=30)
                
                timeslot = Timeslot.objects.create(
                    study=study,
                    starts_at=start,
                    ends_at=end,
                    capacity=2,
                    location='Psychology Building, Room 215',
                    notes='Standard session'
                )
                timeslots.append(timeslot)
        
        # Week 2-3 (upcoming sessions)
        for day_offset in [1, 2, 3, 4, 5, 8, 9, 10, 11, 12]:
            for hour in [10, 14, 16]:
                start = timezone.make_aware(
                    timezone.datetime.combine(
                        base_date + timedelta(days=day_offset),
                        timezone.datetime.min.time().replace(hour=hour)
                    )
                )
                end = start + timedelta(minutes=30)
                
                timeslot = Timeslot.objects.create(
                    study=study,
                    starts_at=start,
                    ends_at=end,
                    capacity=2,
                    location='Psychology Building, Room 215',
                    notes='Standard session'
                )
                timeslots.append(timeslot)
        
        self.stdout.write(f'  ✓ Created {len(timeslots)} timeslots')
        return timeslots

    def create_signups(self, timeslots, participants):
        """Create signups with various statuses."""
        signups = []
        
        # Past timeslots - create attended/no-show signups
        past_timeslots = [ts for ts in timeslots if ts.is_past]
        random.shuffle(past_timeslots)
        
        for i, timeslot in enumerate(past_timeslots[:15]):  # First 15 past slots
            participant = participants[i % len(participants)]
            
            # 80% attended, 15% no-show, 5% cancelled
            rand = random.random()
            if rand < 0.80:
                status = 'attended'
            elif rand < 0.95:
                status = 'no_show'
            else:
                status = 'cancelled'
            
            signup = Signup.objects.create(
                timeslot=timeslot,
                participant=participant,
                status=status,
                consent_text_version=timeslot.study.consent_text,
                booked_at=timeslot.starts_at - timedelta(days=random.randint(3, 10)),
            )
            
            if status == 'attended':
                signup.attended_at = timeslot.ends_at + timedelta(minutes=5)
                signup.save()
            elif status == 'cancelled':
                signup.cancelled_at = timeslot.starts_at - timedelta(days=2)
                signup.save()
            
            signups.append(signup)
        
        # Future timeslots - create booked signups
        future_timeslots = [ts for ts in timeslots if not ts.is_past]
        random.shuffle(future_timeslots)
        
        for i, timeslot in enumerate(future_timeslots[:8]):  # Book 8 future slots
            participant = participants[(i + 15) % len(participants)]
            
            signup = Signup.objects.create(
                timeslot=timeslot,
                participant=participant,
                status='booked',
                consent_text_version=timeslot.study.consent_text,
                booked_at=timezone.now() - timedelta(days=random.randint(0, 5)),
                participant_notes=random.choice([
                    '',
                    'Looking forward to participating!',
                    'Is parking available nearby?',
                    ''
                ])
            )
            signups.append(signup)
        
        self.stdout.write(f'  ✓ Created {len(signups)} signups')
        return signups

    def create_credit_transactions(self, signups, course):
        """Create credit transactions for attended signups."""
        transactions = []
        
        attended_signups = [s for s in signups if s.status == 'attended']
        
        for signup in attended_signups:
            transaction = CreditTransaction.objects.create(
                participant=signup.participant,
                study=signup.timeslot.study,
                course=course,
                amount=signup.timeslot.study.credit_value,
                reason=f'Completed study: {signup.timeslot.study.title}',
                created_by=signup.timeslot.study.researcher,
                created_at=signup.attended_at + timedelta(hours=1)
            )
            transactions.append(transaction)
        
        self.stdout.write(f'  ✓ Created {len(transactions)} credit transactions')
        return transactions

    def create_responses(self, study):
        """Create sample protocol responses."""
        responses = []
        
        # Create 12 sample responses with realistic decision-making data
        for i in range(12):
            response_data = {
                'participant_id': f'P{str(i+1).zfill(3)}',
                'demographics': {
                    'age': random.randint(18, 23),
                    'gender': random.choice(['M', 'F', 'Other']),
                    'major': random.choice(['Psychology', 'Biology', 'Business', 'Education', 'Other'])
                },
                'trials': []
            }
            
            # Generate 30 trial responses
            for trial_num in range(1, 31):
                trial_data = {
                    'trial_number': trial_num,
                    'scenario': f'Scenario {trial_num}',
                    'option_a_prob': random.randint(30, 70),
                    'option_a_value': random.randint(50, 200),
                    'option_b_prob': random.randint(30, 70),
                    'option_b_value': random.randint(50, 200),
                    'choice': random.choice(['A', 'B']),
                    'reaction_time_ms': random.randint(1500, 8000),
                    'confidence': random.randint(1, 7)
                }
                response_data['trials'].append(trial_data)
            
            # Add strategy questionnaire
            response_data['strategy'] = {
                'risk_preference': random.randint(1, 7),
                'calculation_method': random.choice(['gut_feeling', 'mental_math', 'comparison']),
                'confidence_overall': random.randint(1, 7)
            }
            
            response = Response.objects.create(
                study=study,
                payload=response_data,
                created_at=timezone.now() - timedelta(days=random.randint(1, 7)),
                ip_address=f'192.168.1.{random.randint(1, 254)}',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            responses.append(response)
        
        self.stdout.write(f'  ✓ Created {len(responses)} protocol responses')
        return responses

