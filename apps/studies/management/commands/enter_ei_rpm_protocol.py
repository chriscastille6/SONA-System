"""
Management command to enter comprehensive protocol details for EI × RPM study.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.studies.models import Study, ProtocolSubmission, CollegeRepresentative

User = get_user_model()


class Command(BaseCommand):
    help = 'Enter comprehensive protocol details for EI × RPM study'

    def handle(self, *args, **options):
        # Find the EI × RPM study
        try:
            study = Study.objects.get(slug='ei-rpm')
        except Study.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                'EI × RPM study (ei-rpm) does not exist. Create it first.'
            ))
            return
        
        # Get the researcher (study owner)
        researcher = study.researcher
        if not researcher:
            self.stdout.write(self.style.ERROR(
                'Study has no researcher assigned.'
            ))
            return
        
        # Check if draft already exists
        existing_draft = ProtocolSubmission.objects.filter(
            study=study,
            status='draft'
        ).first()
        
        if existing_draft:
            self.stdout.write(self.style.WARNING(
                f'Draft protocol already exists (ID: {existing_draft.id}). Updating...'
            ))
            submission = existing_draft
        else:
            # Create new draft submission
            submission = ProtocolSubmission.objects.create(
                study=study,
                status='draft',
                submitted_by=researcher,
            )
            self.stdout.write(self.style.SUCCESS(
                'Created new draft protocol submission.'
            ))
        
        # Set estimated dates (start in 2 weeks, complete in 6 months)
        today = timezone.now().date()
        submission.estimated_start_date = today + timedelta(days=14)
        submission.estimated_completion_date = today + timedelta(days=180)
        
        # Review type recommendation: EXEMPT
        submission.pi_suggested_review_type = 'exempt'
        submission.review_type = 'exempt'  # Initial
        submission.exemption_category = 'D'  # Anonymous surveys/interviews
        
        # Basic information
        submission.funding_source = 'No external funding. Internal research project.'
        submission.continuation_of_previous = False
        submission.involves_deception = False
        
        # Protocol Description
        submission.protocol_description = '''
This study examines the relationship between emotional intelligence (EI) and fluid intelligence 
as measured by Raven's Progressive Matrices (RPM), and also explores the Dunning-Kruger effect 
in self-assessment of EI abilities. We are testing whether there is a fluid emotional intelligence 
that is separate and distinct from crystallized IQ, and how individuals' self-perceptions of EI 
align with their actual performance.
        '''.strip()
        
        submission.population_description = '''
Participants will be undergraduate students enrolled in psychology and business courses at 
Nicholls State University. Participants must be at least 18 years of age. There are no 
specific exclusion criteria beyond age requirements. Participants will be recruited through 
the SONA system and will receive course credit for participation.
        '''.strip()
        
        submission.research_procedures = '''
The study involves the following procedures:

1. **Informed Consent**: Participants will read and provide electronic consent before beginning the study.

2. **Demographics and Background**: Participants will provide basic demographic information (age, gender, 
   academic status, major) and background questions about their experience with emotional intelligence 
   assessments.

3. **Self-Estimate Assessment**: Participants will be asked to estimate their emotional intelligence 
   abilities across multiple domains (self-awareness, self-management, social awareness, relationship 
   management) by providing percentile estimates of their performance relative to others.

4. **Emotional Intelligence Assessment**: Participants will complete a video-based emotional intelligence 
   assessment. They will watch workplace scenarios and answer questions about emotional recognition, 
   regulation, and appropriate responses. This assessment includes approximately 36 items across 
   3 different video scenarios.

5. **Raven's Progressive Matrices (RPM)**: Participants will complete a fluid intelligence test using 
   Raven's Progressive Matrices, which measures abstract reasoning and pattern recognition abilities.

6. **Feedback and Comparison**: Participants will receive immediate feedback comparing their self-estimates 
   with their actual performance on the EI assessment, allowing for examination of the Dunning-Kruger effect.

7. **Debriefing**: Participants will receive a comprehensive debriefing explaining the study's purpose, 
   the Dunning-Kruger effect, and resources for further learning about emotional intelligence.

All data collection will occur online through the SONA system. The entire procedure takes approximately 
30-40 minutes to complete.
        '''.strip()
        
        submission.research_objectives = '''
The primary objectives of this research are:

1. To determine whether emotional intelligence represents a distinct form of fluid intelligence 
   separate from crystallized IQ, as measured by the relationship between EI performance and 
   Raven's Progressive Matrices scores.

2. To examine the Dunning-Kruger effect in emotional intelligence self-assessment by comparing 
   participants' self-estimates of EI abilities with their actual performance on the EI assessment.

3. To understand the relationship between self-assessed EI abilities and actual EI performance, 
   including identifying factors that predict accurate vs. inaccurate self-assessment.

4. To contribute to the theoretical understanding of emotional intelligence as either a fluid 
   cognitive ability or a crystallized knowledge-based skill.
        '''.strip()
        
        submission.research_questions = '''
1. Is there a significant positive correlation between emotional intelligence (EI) performance 
   and fluid intelligence (RPM scores), suggesting EI as a fluid cognitive ability?

2. Do individuals with lower actual EI performance overestimate their EI abilities (Dunning-Kruger effect)?

3. Do individuals with higher actual EI performance accurately estimate or underestimate their abilities?

4. What demographic or background factors predict accurate vs. inaccurate self-assessment of EI abilities?

5. Is emotional intelligence better conceptualized as a fluid intelligence (correlated with RPM) 
   or as crystallized knowledge (independent of RPM)?
        '''.strip()
        
        submission.educational_justification = '''
This research serves educational purposes by:
- Providing students with hands-on experience in psychological research
- Teaching students about emotional intelligence and its measurement
- Demonstrating research methodology and data collection procedures
- Contributing to students' understanding of cognitive abilities and self-assessment
        '''.strip()
        
        # Recruitment
        submission.recruitment_method = '''
Participants will be recruited through the SONA (System for Online Research) platform. 
Students enrolled in psychology and business courses that offer research participation credit 
will be able to view and sign up for this study through the SONA system. Recruitment materials 
will be posted on the SONA system with a clear description of the study requirements, duration, 
and credit value.
        '''.strip()
        
        submission.recruitment_script = '''
Study Title: Emotional Intelligence and Fluid Intelligence Study

Description: This study examines the relationship between emotional intelligence and cognitive abilities. 
You will complete assessments of emotional intelligence and fluid intelligence, and receive feedback 
on your performance.

Duration: Approximately 30-40 minutes
Credit Value: 1.0 credit
Mode: Online (complete at your own pace)

Requirements: Must be 18 years of age or older
        '''.strip()
        
        submission.inclusion_criteria = '''
- Must be at least 18 years of age
- Must be currently enrolled as a student at Nicholls State University
- Must be enrolled in a course that offers research participation credit through SONA
- Must have access to a computer or device with internet connection
- Must be able to view video content and complete online assessments
        '''.strip()
        
        submission.exclusion_criteria = '''
- Under 18 years of age
- Not currently enrolled at Nicholls State University
- Unable to complete online assessments due to technical limitations
- Previously participated in this study (to avoid duplicate responses)
        '''.strip()
        
        # Benefits and Costs
        submission.benefits_to_subjects = '''
Participants will benefit from:
- Receiving course credit for participation (1.0 credit)
- Gaining insight into their own emotional intelligence abilities through immediate feedback
- Learning about emotional intelligence and the Dunning-Kruger effect through the debriefing
- Contributing to scientific understanding of emotional intelligence
        '''.strip()
        
        submission.benefits_to_others = '''
This research may benefit:
- Other students and researchers interested in emotional intelligence
- Educators developing EI training programs
- Organizations seeking to understand EI assessment and self-awareness
        '''.strip()
        
        submission.benefits_to_society = '''
This research contributes to:
- Scientific understanding of emotional intelligence as a cognitive ability
- Understanding of the Dunning-Kruger effect in emotional intelligence
- Development of better EI assessment and training methods
- Educational practices related to emotional intelligence development
        '''.strip()
        
        submission.payment_compensation = '''
Participants will receive 1.0 course credit through the SONA system for their participation. 
No monetary compensation will be provided.
        '''.strip()
        
        submission.costs_to_subjects = '''
The only cost to participants is their time (approximately 30-40 minutes). There are no 
financial costs, physical risks, or other burdens associated with participation.
        '''.strip()
        
        # Review Type Justification
        submission.review_type_justification = '''
This study qualifies for exempt status under Category D (Educational settings, anonymous surveys/interviews) 
because:

1. The study involves minimal risk to participants (online surveys and assessments)
2. All data collection is anonymous - participants are identified only by SONA ID numbers
3. The study involves standard educational and psychological assessment procedures
4. No sensitive topics or vulnerable populations are involved
5. Participants are adults (18+) who can provide informed consent
6. The study does not involve deception, physical procedures, or collection of sensitive information
7. All procedures are standard in educational research settings

The study involves only anonymous data collection through online assessments, with no collection 
of identifying information beyond SONA ID numbers (which are already anonymized in the system).
        '''.strip()
        
        # Risks
        submission.risk_statement = '''
This study involves minimal risk to participants. The primary potential risks are:

1. **Psychological discomfort**: Some participants may experience mild discomfort when receiving 
   feedback that their self-estimates differ from their actual performance. However, all feedback 
   is provided in a supportive, educational context with emphasis on learning and growth.

2. **Time commitment**: Participants invest approximately 30-40 minutes of their time, but this 
   is compensated with course credit.

3. **Privacy concerns**: While all data is anonymized, there is a minimal risk of data breach. 
   However, no personally identifying information is collected beyond SONA ID numbers.

The risks in this study are no greater than those encountered in normal daily activities or 
routine educational assessments.
        '''.strip()
        
        submission.risk_mitigation = '''
Risks are mitigated through:

1. **Comprehensive debriefing**: All participants receive detailed debriefing explaining the study 
   purpose, their performance, and the Dunning-Kruger effect in a supportive, educational context.

2. **Anonymization**: All data is collected with SONA ID numbers only - no names, email addresses, 
   or other identifying information is collected.

3. **Voluntary participation**: Participants can withdraw at any time without penalty.

4. **Secure data storage**: All data is stored securely on password-protected servers with access 
   limited to the research team.

5. **Support resources**: Participants are provided with resources for further learning about 
   emotional intelligence if they are interested.
        '''.strip()
        
        # Data Handling
        submission.data_collection_methods = '''
Data will be collected through the SONA online platform using the following methods:

1. **Demographic and background information**: Collected through online forms
2. **Self-estimate assessments**: Collected through online rating scales and percentile estimates
3. **Emotional intelligence assessment**: Collected through video-based scenario questions (36 items)
4. **Raven's Progressive Matrices**: Collected through online pattern recognition test
5. **Feedback responses**: Collected through online forms after performance feedback

All data collection occurs through secure, encrypted online forms. Data is automatically stored 
in the SONA database system with SONA ID numbers as the only identifier.
        '''.strip()
        
        submission.data_storage = '''
All data will be stored securely on password-protected servers maintained by Nicholls State University. 
Data will be stored in the SONA system database, which uses industry-standard encryption and security 
measures. Access to data is restricted to the principal investigator and authorized research team members.

Data will be stored with SONA ID numbers only - no personally identifying information (names, 
email addresses, etc.) will be stored with the research data.
        '''.strip()
        
        submission.confidentiality_procedures = '''
Confidentiality is maintained through:

1. **Anonymization**: Participants are identified only by SONA ID numbers, which are already 
   anonymized in the SONA system. No names, email addresses, or other identifying information 
   is collected or stored with research data.

2. **Secure access**: Only the principal investigator and authorized research team members have 
   access to the data, and all access is logged and monitored.

3. **Data encryption**: All data is stored using industry-standard encryption methods.

4. **Limited data sharing**: Data will only be shared in aggregated, anonymized form for 
   publication purposes. Individual participant data will never be shared.

5. **IRB compliance**: All procedures follow IRB guidelines for data confidentiality and security.
        '''.strip()
        
        submission.data_retention = '''
Research data will be retained for a minimum of 5 years after study completion, as required by 
IRB regulations. After this period, data may be retained longer for potential follow-up analyses 
or publication purposes, but will continue to be stored securely and confidentially. Data will be 
destroyed in accordance with university data retention policies and IRB requirements.
        '''.strip()
        
        submission.data_access = '''
Access to research data is restricted to:
- Principal Investigator (Dr. Chris Castille)
- Authorized research team members (if any)
- IRB members for review purposes (if requested)

Data will be accessed only for research analysis, publication preparation, and IRB compliance. 
All data access is logged and monitored.
        '''.strip()
        
        # Consent Procedures
        submission.consent_procedures = '''
Informed consent will be obtained electronically through the SONA system before participants 
begin the study. The consent process includes:

1. **Consent form display**: Participants will see a comprehensive consent form explaining the 
   study purpose, procedures, risks, benefits, and their rights as participants.

2. **Consent questions**: Participants must answer questions confirming they understand the study 
   and their rights before proceeding.

3. **Electronic consent**: Participants provide consent by clicking "Yes, I consent to participate" 
   after reading the consent form.

4. **Right to withdraw**: The consent form clearly states that participants can withdraw at any 
   time without penalty.

5. **Contact information**: The consent form includes contact information for the principal 
   investigator and IRB for questions or concerns.

The consent form is stored electronically in the SONA system as part of the research record.
        '''.strip()
        
        # Investigator Information
        submission.pi_name = researcher.get_full_name() or researcher.username
        submission.pi_email = researcher.email
        if hasattr(researcher, 'profile') and researcher.profile:
            submission.pi_department = getattr(researcher.profile, 'department', 'Psychology')
        else:
            submission.pi_department = 'Psychology'
        submission.pi_title = 'Assistant Professor'  # Update if needed
        submission.pi_phone = ''  # Add if available
        
        submission.co_investigators = 'None'
        submission.citi_training_completion = 'Principal Investigator has completed CITI training in Human Subjects Research (Social/Behavioral Research).'
        
        # Vulnerable Populations
        submission.involves_vulnerable_populations = False
        
        # International Research
        submission.involves_international_research = False
        
        # Financial Interests
        submission.financial_interest_none = True
        submission.financial_interest_disclosure = ''
        
        # Study Monitoring
        submission.data_monitoring_plan = '''
Data will be monitored throughout the study period to ensure:
- Data quality and completeness
- Appropriate participant recruitment
- System functionality and data collection accuracy
- Compliance with IRB protocols

The principal investigator will review data collection progress weekly and address any issues 
that arise.
        '''.strip()
        
        submission.oversight_procedures = '''
Study oversight will be provided by:
- Principal Investigator: Daily monitoring of data collection and system functionality
- IRB: Annual review and compliance monitoring
- College Representative: Initial review and determination of exempt status

Any adverse events or protocol deviations will be reported to the IRB immediately.
        '''.strip()
        
        # Publication and Dissemination
        submission.publication_plan = '''
Results from this study will be prepared for publication in peer-reviewed psychology journals, 
with a focus on journals related to emotional intelligence, cognitive abilities, and individual 
differences. Findings may also be presented at academic conferences.

All publications will use aggregated, anonymized data only. No individual participant data 
will be published or shared.
        '''.strip()
        
        submission.data_sharing_plan = '''
Aggregated, anonymized data may be shared with other researchers through:
- Publication in peer-reviewed journals (with data availability statements)
- Academic conference presentations
- Open science repositories (if appropriate and with IRB approval)

Individual participant data will never be shared. All shared data will be fully anonymized 
and aggregated.
        '''.strip()
        
        submission.participant_access_to_results = '''
Participants who are interested in learning about the study results can:
- Contact the principal investigator to request a summary of findings
- Access published results through academic journals (when published)
- Receive information about publications through the SONA system (if they opt in)

A summary of findings will be prepared and made available to participants upon request after 
data analysis is complete.
        '''.strip()
        
        # Appendices
        submission.appendices_notes = '''
Supporting documents include:
- Consent form (stored in SONA system)
- Emotional Intelligence Assessment items and scenarios
- Raven's Progressive Matrices test materials
- Debriefing materials and resources
- Recruitment materials posted on SONA system

All materials are available for IRB review upon request.
        '''.strip()
        
        # Contact Information
        submission.study_contact_name = submission.pi_name
        submission.study_contact_email = submission.pi_email
        submission.study_contact_phone = submission.pi_phone
        
        submission.irb_contact_notes = '''
For questions or concerns about this research, participants can contact:
- Principal Investigator: [Contact information in consent form]
- IRB Office: [IRB contact information]

All contact information is provided in the consent form and study materials.
        '''.strip()
        
        # Save the submission
        submission.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'✅ Protocol details entered for: {study.title}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   Submission ID: {submission.id}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   Status: {submission.get_status_display()}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   Recommended Review Type: {submission.get_pi_suggested_review_type_display()}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   Exemption Category: {submission.exemption_category} (Anonymous surveys/interviews)'
        ))
        self.stdout.write(self.style.WARNING(
            '\n⚠️  Notes:'
        ))
        self.stdout.write(
            '   - Recommended reviewers: Jon Murphy (CBA rep) and Julianne Allen'
        )
        self.stdout.write(
            '   - Reviewers will be assigned by the college representative during the review process'
        )
        self.stdout.write(
            '   - You can view and edit the protocol at:'
        )
        self.stdout.write(
            f'     https://bayoupal.nicholls.edu/hsirb/studies/{study.id}/protocol/enter/'
        )
        self.stdout.write(self.style.SUCCESS(
            '\n✅ Protocol draft is ready for review and submission!'
        ))
