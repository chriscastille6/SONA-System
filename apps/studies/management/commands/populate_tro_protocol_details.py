"""
Management command to populate TRO protocol submission with full details from the
IRB_Application_Consolidated_Agent_Protocol.pdf and create the Loss Aversion amendment.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User
from apps.studies.models import Study, ProtocolSubmission, ProtocolAmendment


class Command(BaseCommand):
    help = 'Populate TRO protocol with details from PDF and create Loss Aversion amendment'

    def handle(self, *args, **options):
        self.stdout.write('📋 Populating TRO Protocol Details...\n')

        # Find the study
        study = Study.objects.filter(slug='conjoint-analysis').first()
        if not study:
            self.stdout.write(self.style.ERROR('✗ TRO study not found'))
            return

        self.stdout.write(f'✓ Found study: {study.title}')

        # Find the protocol submission
        submission = ProtocolSubmission.objects.filter(study=study).order_by('-version').first()
        if not submission:
            self.stdout.write(self.style.ERROR('✗ No protocol submission found for this study'))
            return

        self.stdout.write(f'✓ Found submission: {submission.submission_number} (v{submission.version})')

        # Find Jon Murphy (prefer active account with real email)
        jon_murphy = User.objects.filter(
            email='jonathan.murphy@nicholls.edu', role='irb_member', is_active=True
        ).first()
        if not jon_murphy:
            jon_murphy = User.objects.filter(
                email__icontains='murphy', role='irb_member', is_active=True
            ).first()
        if not jon_murphy:
            # Try college rep
            from apps.studies.models import CollegeRepresentative
            rep = CollegeRepresentative.objects.filter(college='business', active=True).first()
            if rep and rep.representative:
                jon_murphy = rep.representative

        # Find PI (Meder) and Co-I (Castille)
        pi = User.objects.filter(email__icontains='meder').first()
        co_i = User.objects.filter(email__icontains='castille').first()

        # ================================================================
        # POPULATE PROTOCOL DETAILS FROM PDF
        # ================================================================
        self.stdout.write('\n📝 Populating protocol fields...')

        # 1. Protocol Description (Section 1)
        submission.protocol_description = (
            "This is an educational classroom exercise designed to teach students about conjoint "
            "analysis and total rewards optimization within the context of Dr. Meder's Labor "
            "Economics course at Nicholls State University. The exercise uses conjoint analysis "
            "and total rewards optimization to teach students about the application of the theory "
            "of optimal fringe benefits. Dr. Christopher Castille is supporting Dr. Meder in the "
            "implementation and analysis of this exercise, which has been designed as a pedagogical "
            "tool to help undergraduate business students learn skills in economic decision-making "
            "and preference analysis. The exercise design has been developed via Dr. Meder building "
            "off established conjoint analysis methodologies published in the labor economics and "
            "management literature."
        )

        submission.population_description = (
            "The population for this study consists exclusively of undergraduate students enrolled "
            "in Dr. Martin Meder's Labor Economics course at Nicholls State University. "
            "Participation is VOLUNTARY and students must be 18 or older. This exercise is only "
            "available to students in this specific course who have received the necessary "
            "background instruction in labor economics concepts."
        )

        submission.research_procedures = (
            "1. Introduction and Consent: Students receive a brief introduction explaining they are "
            "participating in a Total Rewards Optimization project as part of their Labor Economics coursework.\n\n"
            "2. Role-Playing Scenario: Students imagine they are employees at 'Firm Co.' participating in a "
            "Total Rewards Optimization project to identify new employee rewards.\n\n"
            "3. Choice Tasks: Students complete 8 choice tasks selecting between pairs of job scenarios. Each "
            "scenario presents changes from a $64K baseline compensation package. All options represent a $5K "
            "reduction to $59K total compensation, with different allocations across four attributes:\n"
            "   - Salary: $37.5K to $42.5K (compared to $45K baseline)\n"
            "   - Training Budget: $1K to $5K per employee (compared to $2.5K baseline)\n"
            "   - Manager Quality: Average vs Good\n"
            "   - Work Flexibility: Onsite, Hybrid, Remote\n\n"
            "4. Turnover Probability Assessment: Students report probability (0-100%) of staying with the "
            "company for four different packages.\n\n"
            "5. Wait Page and Group Work: Students work in small groups to design a new benefit package "
            "considering the $59K cost constraint.\n\n"
            "6. Final Choice Round: Students choose between baseline, preferred choice, and focus group packages.\n\n"
            "7. Loss Aversion Assessment: Students complete a validated 7-item loss aversion scale (Li, Chai, "
            "Nordstrom, Tangpong, & Hung, 2021) measuring individual differences in decision-making preferences. "
            "Items are rated on a 1-7 Likert scale.\n\n"
            "8. Exercise Evaluation: Students rate the exercise on interest, usefulness, recommendation, "
            "understanding of economic concepts, business relevance, discussion value, and cross-teaching value "
            "(adapted from Moryl, 2013).\n\n"
            "9. Results Discussion: Students view class-wide results showing preference patterns and business "
            "impact calculations."
        )

        submission.research_objectives = (
            "To teach undergraduate business students about the theory of optimal fringe benefits through "
            "hands-on application of conjoint analysis and total rewards optimization techniques in Dr. Meder's "
            "Labor Economics course. The exercise reinforces theoretical concepts through practical "
            "decision-making experience."
        )

        submission.research_questions = (
            "1. How do students allocate preferences across compensation components (salary, training, "
            "manager quality, work flexibility) under budget constraints?\n"
            "2. How does loss aversion influence compensation package preferences?\n"
            "3. What is the educational value of conjoint analysis as a teaching tool for labor economics concepts?\n"
            "4. How does cross-teaching (participation of a Management professor) enhance understanding of "
            "labor economics integration in business education?"
        )

        submission.educational_justification = (
            "This exercise is conducted as part of Dr. Martin Meder's Labor Economics course. It is designed "
            "as a pedagogical tool to help undergraduate business students learn skills in economic "
            "decision-making and preference analysis using established conjoint analysis methodologies "
            "from the labor economics and management literature."
        )

        # 2. Recruitment (Section 3)
        submission.recruitment_method = (
            "Students enrolled in Dr. Martin Meder's Labor Economics course at Nicholls State University "
            "will be invited to participate as part of their educational experience. The exercise is "
            "integrated into the regular course curriculum. Participation is VOLUNTARY."
        )

        submission.inclusion_criteria = (
            "- Undergraduate students enrolled in Dr. Meder's Labor Economics course at Nicholls State University\n"
            "- Must be 18 years of age or older\n"
            "- Must have received the necessary background instruction in labor economics concepts"
        )

        submission.exclusion_criteria = (
            "- Students under 18 years of age\n"
            "- Students not enrolled in the Labor Economics course"
        )

        submission.recruitment_script = (
            "This exercise is part of your Labor Economics course. Your participation is voluntary. "
            "You may withdraw at any time without penalty. All responses are anonymous."
        )

        # 3. Benefits and Costs (Section 4)
        submission.benefits_to_subjects = (
            "Students will gain hands-on experience with conjoint analysis methodology, which is widely "
            "used in marketing research, human resource management, and economic decision-making. "
            "The exercise directly reinforces labor economics concepts covered in the course."
        )

        submission.benefits_to_others = (
            "Other educators may benefit from this pedagogical approach to teaching labor economics "
            "concepts through interactive conjoint analysis exercises."
        )

        submission.benefits_to_society = (
            "This research contributes to understanding effective pedagogical approaches for teaching "
            "economic concepts and may inform better compensation design practices in organizations."
        )

        submission.payment_compensation = (
            "No monetary compensation. This is an educational classroom exercise conducted as part of "
            "normal course activities."
        )

        submission.costs_to_subjects = (
            "Approximately 5-10 minutes of class time to complete the online survey and choice tasks. "
            "No financial costs to participants."
        )

        # 4. Review Type Justification (Section 5)
        submission.review_type_justification = (
            "This research qualifies for exempt review as it involves normal educational practices "
            "conducted in established educational settings (Dr. Meder's Labor Economics course at "
            "Nicholls State University). The exercise is designed as a pedagogical tool that uses "
            "commonly accepted educational practices. Participation is voluntary and poses no more "
            "than minimal risk to participants."
        )

        submission.exemption_category = "Category 1 (A): Research conducted in established or commonly accepted educational settings"
        submission.expedited_category = ""

        # 5. Risks (Section 6)
        submission.risk_statement = (
            "This study poses minimal risk to participants. The exercise involves making hypothetical "
            "choices about compensation packages in a simulated scenario. There are no physical, emotional, "
            "social, or legal risks beyond those encountered in normal daily life or routine educational activities."
        )

        submission.risk_mitigation = (
            "- Participation is completely voluntary\n"
            "- Students may withdraw at any time without penalty to course grade\n"
            "- No personal identifying information is collected\n"
            "- All responses are anonymous\n"
            "- Data is stored locally in browser only with no external data transmission"
        )

        # 6. Data Handling (Section 7)
        submission.data_collection_methods = (
            "Online survey administered through a static HTML/CSS/JavaScript application "
            "(student_survey.html, Version: September 2025). Mobile-responsive design for "
            "smartphone and tablet use. Platform: Local server or web hosting. Data includes "
            "conjoint choice task selections, turnover probability estimates, loss aversion scale "
            "responses (7-item scale), and exercise evaluation ratings."
        )

        submission.data_storage = (
            "Anonymous responses stored locally in browser. No external data transmission. "
            "No personal identifying information collected. Data stored locally in browser only."
        )

        submission.confidentiality_procedures = (
            "- No personal identifying information collected (no names, email addresses, or student IDs)\n"
            "- Data stored locally in browser only\n"
            "- No external data transmission\n"
            "- Completely anonymous participation\n"
            "- All data is aggregated for class-wide analysis"
        )

        submission.data_retention = (
            "Data will be retained for the duration of the academic semester and any subsequent "
            "analysis period. Anonymous aggregate data may be retained indefinitely for research "
            "and publication purposes."
        )

        submission.data_access = (
            "Dr. Martin Meder (PI) and Dr. Christopher Castille (Co-Investigator) will have "
            "access to the anonymous aggregate data. No individual-level identifying data is collected."
        )

        # 7. Consent Procedures (Section 8)
        submission.consent_procedures = (
            "Students will receive written informed consent information at the beginning of the exercise. "
            "The consent form includes:\n"
            "- Purpose of the exercise\n"
            "- Description of procedures\n"
            "- Voluntary participation statement\n"
            "- Right to withdraw without penalty\n"
            "- Anonymity assurance\n"
            "- Contact information for PIs and HSIRB\n\n"
            "By participating in the exercise, students indicate their consent to participate. "
            "Students who do not wish to participate may complete an alternative assignment."
        )

        # Additional Information
        submission.estimated_start_date = "Spring 2026"
        submission.estimated_completion_date = "Spring 2026"
        submission.funding_source = "No external funding; educational exercise conducted as part of normal course activities"
        submission.continuation_of_previous = False

        # Investigator Information (Section 9)
        submission.pi_name = "Dr. Martin Meder"
        submission.pi_title = "Associate Professor"
        submission.pi_department = "Business Administration"
        submission.pi_email = "martin.meder@nicholls.edu"
        submission.pi_phone = "985-448-4237"
        submission.co_investigators = (
            "Dr. Christopher Castille, christopher.castille@nicholls.edu, 985-449-7015\n"
            "Department of Management, Nicholls State University"
        )

        # CITI Training (Section 9) – certificate can be linked via protocol form upload or link_tro_citi_certificate
        submission.citi_training_completion = (
            "Dr. Martin Meder (PI) and Dr. Christopher Castille (Co-I) have completed CITI Program training "
            "in Human Research (Social-Behavioral-Educational). Completion certificates are on file and "
            "linked to this submission."
        )

        # Vulnerable Populations (Section 10)
        submission.involves_vulnerable_populations = False
        submission.vulnerable_populations_description = ""
        submission.vulnerable_population_protections = ""

        # International Research (Section 11)
        submission.involves_international_research = False
        submission.international_research_locations = ""
        submission.cultural_considerations = ""

        # Financial Interests (Section 12)
        submission.financial_interest_none = True
        submission.financial_interest_disclosure = ""

        # Study Monitoring (Section 13)
        submission.data_monitoring_plan = (
            "Real-time visualization of aggregated class data using Chart.js library. "
            "Conjoint analysis: preference pattern visualization. "
            "Turnover cost calculations based on student retention predictions. "
            "ROI analysis: cost-benefit analysis of different benefit packages."
        )

        submission.oversight_procedures = (
            "The PI (Dr. Martin Meder) and Co-I (Dr. Christopher Castille) will oversee data collection "
            "and quality. The exercise is conducted within normal educational settings with no external "
            "data transmission; all responses are anonymous and stored locally."
        )

        # Publication and Dissemination (Section 14)
        submission.publication_plan = (
            "Results may be submitted for publication in academic journals related to "
            "economics education, labor economics, or management pedagogy. All published "
            "data will be aggregated and anonymous."
        )

        submission.data_sharing_plan = (
            "Anonymous aggregate data may be shared via OSF (Open Science Framework) repository "
            "for research transparency and replication purposes."
        )

        submission.participant_access_to_results = (
            "Aggregated class results are displayed during the exercise. Participants may request "
            "a summary of study findings from the PI once analysis is complete."
        )

        # Appendices (Section 15)
        submission.appendices_notes = (
            "Appendix A: Informed Consent Form\n"
            "Appendix B: Data Collection Instruments (Choice Task Example, Retention Questions, "
            "Assessment Questions)\n"
            "Appendix C: Technical Implementation (Static HTML/CSS/JavaScript Application)\n"
            "Appendix D: Enhanced Assessment Items (adapted from Moryl, 2013)\n"
            "Appendix E: Application Screenshots\n\n"
            "Loss Aversion Scale Reference: Li, J., Chai, L., Nordstrom, O., Tangpong, C., & "
            "Hung, K. (2021). Development of a Loss Aversion Scale. Journal of Managerial Issues, "
            "33(1), 69-89."
        )

        # Contact Information (Section 16)
        submission.study_contact_name = "Dr. Martin Meder"
        submission.study_contact_email = "martin.meder@nicholls.edu"
        submission.study_contact_phone = "985-448-4237"
        submission.irb_contact_notes = (
            "Alternative contact: Dr. Christopher Castille, christopher.castille@nicholls.edu, 985-449-7015\n\n"
            "This research is valid for a 12-month period from the date of approval. "
            "Data collection may begin only after this form has received committee approval "
            "and has been properly filed with the HSIRB."
        )

        # Save all updates
        submission.save()

        self.stdout.write(self.style.SUCCESS('✓ Protocol details populated from PDF'))

        # ================================================================
        # CREATE LOSS AVERSION AMENDMENT
        # ================================================================
        self.stdout.write('\n📋 Creating Loss Aversion Amendment...')

        # Check if amendment already exists
        existing = ProtocolAmendment.objects.filter(
            protocol_submission=submission,
            title__icontains='Loss Aversion'
        ).first()

        if existing:
            self.stdout.write(f'✓ Amendment already exists: {existing.amendment_number}')
            amendment = existing
        else:
            submitter = co_i or pi  # Castille submits, falls back to Meder

            amendment = ProtocolAmendment.objects.create(
                protocol_submission=submission,
                title='Addition of Loss Aversion Inventory and Correlate Measures from the Psychological Assessment Library',
                amendment_type='minor',
                description=(
                    "This amendment proposes the addition of supplementary measures from the "
                    "Psychological Assessment Library to the approved conjoint analysis protocol. "
                    "Specifically, we request approval to administer the full Loss Aversion Inventory (LAI) "
                    "and related correlate measures (including the Endowment Effect scale) that are "
                    "implemented in the library's loss aversion measurement process.\n\n"
                    "The currently approved protocol includes a 7-item Loss Aversion Scale (Li, Chai, "
                    "Nordstrom, Tangpong, & Hung, 2021). This amendment expands the measurement to include "
                    "additional validated items and correlate measures that:\n\n"
                    "1. Measure the endowment effect — the tendency to overvalue items one already possesses\n"
                    "2. Assess related decision-making constructs that co-occur with loss aversion\n"
                    "3. Provide a more comprehensive profile of participants' loss aversion tendencies\n\n"
                    "The assessment is delivered through the Psychological Assessment Library platform and "
                    "takes approximately 5-10 additional minutes to complete."
                ),
                justification=(
                    "The addition of these measures serves two important research purposes:\n\n"
                    "1. Gather more comprehensive data on the loss aversion construct and its correlates: "
                    "The original 7-item scale provides a useful but limited measure of loss aversion. "
                    "By adding the endowment effect scale and other correlate measures, we can develop a "
                    "richer understanding of how various facets of loss aversion influence compensation "
                    "package preferences in the conjoint analysis task.\n\n"
                    "2. Replicate the original Li et al. (2021) findings: The original Development of a "
                    "Loss Aversion Scale (Journal of Managerial Issues, 33(1), 69-89) reported specific "
                    "psychometric properties and correlations. By administering the full inventory, we can "
                    "contribute to the replication literature and assess whether the scale's properties "
                    "hold in our specific educational context with undergraduate business students.\n\n"
                    "This addition directly supports the pedagogical and research goals of the original "
                    "protocol by providing deeper insight into the psychological mechanisms underlying "
                    "students' economic decision-making in the conjoint analysis exercise."
                ),
                impact_on_risk=(
                    "No change to the risk level. The additional measures are survey-based self-report "
                    "items similar to those already approved in the protocol. They involve no deception, "
                    "no sensitive personal information, and pose no additional risk beyond what participants "
                    "experience in the approved exercise."
                ),
                impact_on_consent=(
                    "The consent form should be updated to include a brief mention of the additional "
                    "psychological assessment measures and the estimated increase in completion time "
                    "(approximately 5-10 additional minutes). The voluntary nature of participation "
                    "remains unchanged."
                ),
                new_instruments=(
                    "Loss Aversion Inventory (LAI) — Full version available through the Psychological "
                    "Assessment Library, including:\n\n"
                    "1. Loss Aversion Scale (Li et al., 2021): 7 items measuring loss aversion tendencies "
                    "on a 1-7 Likert scale. Items assess cognitive focus on losses vs. gains, monetary "
                    "loss sensitivity, emotional responses to potential losses, memory persistence of "
                    "losses, and fear of failure vs. hope for success.\n\n"
                    "2. Endowment Effect Measure: Items assessing the tendency to overvalue items one "
                    "already possesses, which is a closely related construct to loss aversion in "
                    "behavioral economics.\n\n"
                    "3. Additional correlate measures implemented in the library's loss aversion "
                    "measurement process for comprehensive construct assessment.\n\n"
                    "All instruments are delivered via the Psychological Assessment Library platform "
                    "at the URL provided. Responses are anonymous and collected electronically."
                ),
                instrument_url='https://bayoupal.nicholls.edu/platform/assessment-flow.html?assessment=lai',
                submitted_by=submitter,
                reviewer=jon_murphy,
            )

            self.stdout.write(self.style.SUCCESS(
                f'✓ Created amendment: {amendment.amendment_number}'
            ))

        # ================================================================
        # SUMMARY
        # ================================================================
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ TRO Protocol Update Complete'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'Study: {study.title}')
        self.stdout.write(f'Protocol: {submission.protocol_number}')
        self.stdout.write(f'Decision: {submission.get_decision_display()}')
        self.stdout.write(f'\nAmendment: {amendment.amendment_number}')
        self.stdout.write(f'Title: {amendment.title}')
        self.stdout.write(f'Status: {amendment.get_decision_display()}')
        if amendment.reviewer:
            self.stdout.write(f'Assigned to: {amendment.reviewer.get_full_name()} ({amendment.reviewer.email})')
        self.stdout.write('')
