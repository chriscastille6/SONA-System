"""
Populate Goal Setting protocol submission with full details from the IRB application
and Addendum 1 (Procedural Modifications).
Protocol: IRB 2024-07-30-001 CBA
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.studies.models import Study, ProtocolSubmission
from apps.studies.goal_setting_study import GOAL_SETTING_STUDY_SLUG


class Command(BaseCommand):
    help = 'Populate Goal Setting protocol with full IRB details'

    def handle(self, *args, **options):
        self.stdout.write('📋 Populating Goal Setting Protocol Details...\n')

        study = Study.objects.filter(slug=GOAL_SETTING_STUDY_SLUG).first()
        if not study:
            self.stdout.write(self.style.ERROR('✗ Goal Setting study not found'))
            return

        self.stdout.write(f'✓ Found study: {study.title}')

        submission = ProtocolSubmission.objects.filter(
            study=study,
            protocol_number='IRB 2024-07-30-001 CBA'
        ).first()
        if not submission:
            self.stdout.write(self.style.ERROR('✗ No protocol submission found for IRB 2024-07-30-001 CBA'))
            return

        self.stdout.write(f'✓ Found submission: {submission.protocol_number}')

        # ================================================================
        # PROTOCOL DETAILS FROM IRB APPLICATION + ADDENDUM 1 (HUMANIZED)
        # ================================================================
        self.stdout.write('\n📝 Populating protocol fields...')

        submission.protocol_description = (
            "This study is a local replication of the foundational Schweitzer, Ordóñez, and Douma (2004) "
            "experiment examining whether performance goals drive unethical behavior. Participants complete "
            "anagram puzzles under one of four conditions: do-your-best, mere goal, reward goal, or "
            "personal goal. This design directly addresses several methodological limitations of the "
            "original 2004 study, tests key boundary conditions—specifically trait loss aversion and "
            "goal proximity—and contributes to a multi-site global replication project."
        )

        submission.population_description = (
            "Undergraduate students enrolled in Business Administration courses (specifically BSAD 101, "
            "meeting in Powell 140) at Nicholls State University, as well as working professionals. "
            "All participants must be 18 years of age or older."
        )

        submission.research_procedures = (
            "Data collection occurs in two phases: (1) a pilot session to calibrate materials and "
            "administration procedures, and (2) a main study session for hypothesis testing. Both pilot "
            "and main materials are supplied for HSIRB review; participants receive only the materials "
            "appropriate to their session.\n\n"
            "Pilot session procedures:\n"
            "1. Consent: Participants enter the lab in groups of up to 20, review and sign the pilot "
            "informed consent form (Appendix B), which is collected separately to preserve anonymity.\n"
            "2. Practice: Participants complete two 1-minute practice rounds to learn the anagram task.\n"
            "3. Performance: Participants complete several timed anagram rounds under do-your-best "
            "instructions to establish site-calibrated performance benchmarks.\n"
            "4. Productivity report: Participants complete an anonymous productivity report; there is "
            "no cash self-payment step in the pilot session. Participants may use a phone to access "
            "an online Scrabble dictionary via a QR code on the report.\n"
            "5. Demographics and traits: Participants complete brief questionnaires.\n"
            "6. Debriefing: The researcher hands each participant the pilot appreciation letter.\n\n"
            "Main study procedures:\n"
            "1. Consent: Participants review and sign the main study informed consent form (Appendix B2), "
            "collected separately to preserve anonymity.\n"
            "2. Practice: Participants complete two 1-minute practice rounds.\n"
            "3. Condition assignment: Participants are randomly assigned to one of four conditions: "
            "'do your best', 'mere goal', 'personal goal', or 'reward goal'. Goal conditions receive "
            "the site-calibrated target from the pilot phase.\n"
            "4. Performance rounds: Participants complete seven 1-minute anagram rounds in paper workbooks.\n"
            "5. Anonymized linking: In an eighth round, participants solve a unique anagram that serves "
            "as a double-blind identifier to match workbook scores with self-reported productivity.\n"
            "6. Demographics and traits: While the researcher is present, participants complete "
            "questionnaires covering demographics, manipulation checks, and individual difference scales "
            "(trait loss aversion, HEXACO-60, moral identity).\n"
            "7. Private self-payment: The researcher leaves the room. Participants use a phone only "
            "to access an online Scrabble dictionary via a QR code on the productivity report, check "
            "their work, complete an anonymous productivity report for rounds 1–7 (round 8 does not "
            "count toward payment), take cash from a $14 envelope per the report instructions, seal "
            "the productivity report and cash envelope in a large envelope, and deposit the large "
            "envelope and workbook folder in separate designated boxes.\n"
            "8. Debriefing: The researcher hands each participant the main study debriefing "
            "sheet explaining the study's scientific purpose and replication goals.\n\n"
            "Students who participated in the pilot may also participate in the main study. Because all "
            "data are anonymous, the research team cannot monitor repeat participation without "
            "compromising anonymity."
        )

        submission.research_objectives = (
            "Our primary objective is to conduct a constructive replication of the foundational "
            "Schweitzer et al. (2004) study, correcting its methodological limitations while maintaining "
            "its core strengths. Second, we aim to investigate when and for whom performance goals lead "
            "to unethical behavior. By testing how trait loss aversion and goal proximity influence "
            "overstatement, we provide a direct empirical test of the loss aversion mechanism "
            "theorized by Ordóñez and Wu (2013). These findings will help strengthen the empirical basis "
            "of the goal-setting literature and offer new theoretical insights for behavioral ethics."
        )

        submission.research_questions = (
            "H1. People with specific challenging goals (i.e., personal, mere, or reward goals) are more "
            "likely to overstate their performance than people without specific challenging goals "
            "(i.e., do-your-best condition).\n"
            "H2. Challenging goal type is related to overstating performance. People with reward goals "
            "are more likely to overstate their performance than those with mere goals, who in turn "
            "are more likely to overstate their performance than those with personal goals.\n"
            "H3a. People who fail to reach their goal by a smaller margin are more likely to overstate "
            "their performance than if they were to fail to reach their goal by a larger margin.\n"
            "H3b. People who reach their goal are less likely to overstate their performance than if "
            "they failed to reach the goal.\n"
            "H4. People with greater trait loss aversion are more likely to overstate their performance.\n"
            "H5. The relationship between trait loss aversion and overstating behavior is amplified in "
            "trials where people failed their goal by a smaller margin than when they failed by a larger margin."
        )

        submission.educational_justification = (
            "This project is part of a global multi-site initiative designed to train student researchers "
            "and junior faculty in rigorous, open-science replication methodologies. By engaging with "
            "a conditionally accepted Registered Report, local co-investigators and research assistants "
            "gain firsthand experience in pre-registration, double-blind administration, and collaborative "
            "behavioral science research."
        )

        submission.recruitment_method = (
            "Recruitment will occur via classroom visits using approved informational flyers. "
            "Two flyer versions are included in the HSIRB packet (Appendix A for pilot sessions, "
            "Appendix A2 for main study); only the version matching the session is shown to "
            "participants. Instructors may offer course credit or bonus points for participation. "
            "The main-study flyer mentions a small cash reward of at least $7.00 with opportunity for "
            "up to $14.00; the pilot flyer does not."
        )

        submission.inclusion_criteria = (
            "- Undergraduate students or working professionals\n"
            "- 18 years of age or older"
        )

        submission.exclusion_criteria = (
            "- Individuals under 18 years of age"
        )

        submission.recruitment_script = (
            "Pilot session script: You are invited to participate in a pilot session for a research study "
            "examining how individuals make decisions during cognitive tasks. This session takes approximately "
            "one hour, has received ethics clearance from the Institutional Review Board, and helps the team "
            "refine procedures before main data collection. There is no cash compensation for the pilot "
            "session. Depending on your instructor's policy, you may receive course credit or bonus points. "
            "Participation is completely voluntary, and all data collected are anonymous.\n\n"
            "Main study script: You are invited to participate in a research study examining how individuals "
            "make decisions during cognitive tasks. This study takes approximately one hour and has received "
            "ethics clearance from the Institutional Review Board. Depending on your instructor's policy, you "
            "may receive course credit, bonus points, or a small cash reward of at least $7.00 with an "
            "opportunity to receive up to $14.00 total. Participation is completely voluntary, and all data collected are "
            "anonymous."
        )

        submission.benefits_to_subjects = (
            "Pilot session participants receive no cash compensation. They may receive course credit or "
            "bonus points at their instructor's discretion and receive a written appreciation letter "
            "explaining how pilot data support calibration for the main study.\n\n"
            "Main study participants receive direct financial compensation through the self-payment "
            "procedure, keeping at least $7.00 and up to $14.00 depending on their assigned "
            "instructions and performance (averaging about $10.00). They also receive a detailed debriefing sheet explaining the "
            "logic and value of open-science replication research."
        )

        submission.benefits_to_others = (
            "Providing managers and organizations with empirically validated insights into when and for "
            "whom specific performance goals prompt unethical behavior, helping design more ethical "
            "incentive systems."
        )

        submission.benefits_to_society = (
            "Strengthening the empirical foundation of the dark-side of goal setting literature, "
            "generating a shared understanding between goal setting and behavioral ethics scholars, "
            "and developing novel theoretical insights to guide organizational practices."
        )

        submission.payment_compensation = (
            "Pilot session: No cash compensation is provided.\n\n"
            "Main study only: Participants receive an envelope containing $14.00 at the start of the "
            "session. Payment amounts are stated on each participant's productivity report during the "
            "private self-payment step. Those in the 'do your best', 'mere goal', and 'personal goal' "
            "conditions are instructed to keep $10.00. Those in the 'reward goal' condition are "
            "instructed to keep $7.00 plus an additional $1.00 for each scored round (rounds 1–7) in "
            "which they met the site-calibrated goal (on average, they receive approximately $10.00). "
            "Unearned cash is returned in the cash envelope, sealed with the productivity report in a "
            "large envelope, and deposited while the researcher is out of the room. Participant-facing "
            "materials describe a small cash reward of at least $7.00 with opportunity for up to $14.00."
        )

        submission.costs_to_subjects = (
            "Participation requires approximately one hour of time. There are no financial costs to "
            "the subjects."
        )

        submission.review_type_justification = (
            "The study qualifies for exempt review under Category 2 of the revised Common Rule "
            "(45 CFR 46.104(d)(2)). Data are collected via behavioral tests (an anagram task) and "
            "survey procedures. No participant names, IDs, or other identifying information are "
            "recorded on any data collection sheets, ensuring participants cannot be identified, "
            "directly or through linked identifiers. While we correlate task performance with "
            "self-reported productivity reports using a unique eighth-round anagram, this linking "
            "mechanism is entirely anonymous and never associated with any student identity."
        )

        submission.exemption_category = "Exempt Category 2 (45 CFR 46.104(d)(2))"
        submission.expedited_category = ""

        submission.risk_statement = (
            "The study presents minimal risk. The anagram task may cause mild frustration or "
            "performance anxiety, but no more than everyday schoolwork or standard puzzles. While "
            "participants have an opportunity to over-report performance or keep unearned money, "
            "all data are completely anonymous and cannot be linked to individual identities."
        )

        submission.risk_mitigation = (
            "To protect participants, the design is double-blind, and no names or student IDs are ever "
            "written on the study workbooks or productivity reports. Signed consent forms are collected "
            "and stored separately. The researcher leaves the room during grading, self-payment, and "
            "report submission. A unique eighth-round anagram is used for anonymous data linking. "
            "Finally, participants receive a detailed debriefing, and contact information for the "
            "Nicholls Counseling Center is provided."
        )

        submission.data_collection_methods = (
            "Data collection uses paper-and-pencil materials, including a task workbook (practice and "
            "performance anagram rounds, goal commitment, trait loss aversion, and demographics), "
            "a separate productivity report for self-reported performance (rounds 1–7), and a follow-up "
            "survey for manipulation and data quality checks. Participants may use a phone only to "
            "access an online Scrabble dictionary via a QR code during the private checking step. Hard "
            "copies are deposited in separate designated boxes (workbook folder and sealed large envelope)."
        )

        submission.data_storage = (
            "Hard-copy workbooks and productivity reports are stored in a locked office in the "
            "Department of Management and Marketing at Nicholls State University. De-identified, "
            "anonymized electronic datasets are maintained on secure, password-protected computers "
            "and shared publicly on the Open Science Framework (OSF) to facilitate open-science collaboration."
        )

        submission.confidentiality_procedures = (
            "Participants remain completely anonymous. No names, email addresses, or student IDs are "
            "written on the workbooks, productivity reports, or survey forms. Signed consent forms are "
            "stored in a separate locked cabinet from the raw data sheets. Anonymized data are linked via "
            "a unique eighth-round anagram rather than any personal identifier, and the de-identified "
            "spreadsheet is shared publicly on the OSF."
        )

        submission.data_retention = (
            "Paper materials will be retained in a locked office for five to seven years in accordance "
            "with APA guidelines, after which they will be shredded. The anonymized electronic dataset "
            "will be preserved indefinitely on the OSF for replication and meta-analysis."
        )

        submission.data_access = (
            "The principal investigator and local co-investigators have access to the raw paper materials. "
            "De-identified, anonymous data are shared with our research collaborators across the multi-site "
            "initiative and made publicly available on the Open Science Framework (OSF)."
        )

        submission.consent_procedures = (
            "Two written informed consent forms are included for HSIRB review: Appendix B (pilot session) "
            "and Appendix B2 (main study). Only the form matching the session is shown to participants. "
            "Each form details the study's purpose, procedures, risks, and benefits, emphasizing that "
            "participation is entirely voluntary and that participants may withdraw at any time without "
            "penalty. The main-study form describes cash compensation; the pilot form states that no cash "
            "compensation is provided. Students who choose not to participate are offered an equivalent "
            "alternative assignment for equal course credit. Students who participated in the pilot may "
            "also participate in the main study; because all data are anonymous, repeat participation "
            "cannot be monitored without compromising anonymity."
        )

        submission.estimated_start_date = "Fall 2024"
        submission.estimated_completion_date = "Spring 2027"
        submission.funding_source = "Nicholls State University Research Council"
        submission.continuation_of_previous = False

        submission.pi_name = "Dr. Christopher Castille"
        submission.pi_title = "Associate Professor of Management"
        submission.pi_department = "Management and Marketing"
        submission.pi_email = "christopher.castille@nicholls.edu"
        submission.pi_phone = "985-449-7015"
        submission.co_investigators = (
            "Dr. Ann-Marie R. Castille (Associate Professor of Management), ann-marie.castille@nicholls.edu, 985-448-4738\n"
            "Dr. Samantha Falgout (Assistant Professor of Accounting), samantha.falgout@nicholls.edu, 985-448-4193\n"
            "Dr. Kaitlin Gravois (Assistant Professor of Marketing), kaitlin.gravois@nicholls.edu, 985-448-4187\n"
            "Dr. Adrien Maught (Assistant Professor of Marketing), adrien.maught@nicholls.edu, 985-448-4194"
        )

        submission.citi_training_completion = (
            "All investigators have completed CITI Program training. Dr. Christopher Castille "
            "(Faculty Researchers), Dr. Ann-Marie R. Castille (Faculty Researchers), "
            "Dr. Samantha Falgout (Faculty Researchers), Dr. Kaitlin Gravois (Faculty Researchers), "
            "Dr. Adrien Maught (Social/Behavioral RCR). Certificates are pending / to be submitted upon request."
        )

        submission.involves_vulnerable_populations = False
        submission.vulnerable_populations_description = ""
        submission.vulnerable_population_protections = ""

        submission.involves_international_research = True
        submission.international_research_locations = (
            "Multi-site: Nicholls State University, University of Waterloo, Otto Beisheim School of "
            "Management, UC Louvain, Florida Atlantic University, Radboud University, Durham University, "
            "and other ARIM partner institutions."
        )
        submission.cultural_considerations = (
            "Each international site secures local ethics clearance and provides site-specific consent "
            "documents and student support resources. Surveys are adjusted for local language proficiency "
            "where applicable."
        )

        submission.financial_interest_none = True
        submission.financial_interest_disclosure = ""

        submission.data_monitoring_plan = (
            "To maintain strict anonymity, data entry is split among three researchers. One researcher "
            "codes the performance workbooks, a second researcher codes the productivity reports and "
            "self-payment sheets, and a third researcher (the PI) merges the electronic files using "
            "the unique eighth-round anagram. This workflow ensures that no single researcher can connect "
            "a participant's actual performance with their self-payment and self-reported productivity."
        )

        submission.oversight_procedures = (
            "The PI oversees local data collection and compliance. Multi-site coordination is "
            "managed through the ARIM consortium, and each collaborating university obtains local "
            "ethics approval for its respective participants."
        )

        submission.publication_plan = (
            "The study results will be submitted to peer-reviewed academic journals, specifically "
            "Psychological Science, as part of the multi-site Registered Report. All findings will be "
            "presented in aggregate form, ensuring individual responses remain anonymous."
        )

        submission.data_sharing_plan = (
            "Anonymized electronic datasets will be posted on the Open Science Framework (OSF) to "
            "permit verification, comparison across sites, and future meta-analyses, with no "
            "identifying information shared."
        )

        submission.participant_access_to_results = (
            "A written debriefing sheet is provided at the end of the session. Participants may also "
            "request a summary of the aggregated findings from the research team by emailing the "
            "principal investigator."
        )

        submission.appendices_notes = (
            "Appendix A: Pilot Recruitment Flyer (no cash compensation language; used for pilot sessions only)\n"
            "Appendix A2: Main Study Recruitment Flyer (small cash reward of at least $7.00 with "
            "opportunity for up to $14.00; used for main data collection)\n"
            "Internal IRB note: Both pilot and main study recruitment materials are submitted for HSIRB "
            "review. Participants see only the flyer that matches their session (pilot or main study).\n"
            "Appendix B: Pilot Informed Consent Statement (no cash compensation)\n"
            "Appendix B2: Main Study Informed Consent Statement (describes self-payment compensation)\n"
            "Internal IRB note: Both consent forms are submitted for HSIRB review. Only the form matching "
            "the session is shown to participants.\n"
            "Repeat participation: Students who participated in the pilot may also participate in the main "
            "study. Because all data are anonymous, the research team cannot monitor repeat participation "
            "without compromising anonymity.\n"
            "Appendix C: Anagram Task Workbook (Study Instrument)\n"
            "Appendix D: Participant Productivity Report (main study; condition-specific pay instructions "
            "on form; reward-condition variant uses $7 base plus $1 per scored round at goal)\n"
            "Appendix E: Pilot Study Appreciation Letter\n"
            "Appendix E2: Main Study Debriefing & Appreciation Letter\n"
            "Appendix F: Approved UWaterloo Master Protocol\n"
            "Appendix G: Psychological Science Registered Report Manuscript\n"
            "Appendix H: Psychological Science Stage 1 In-Principle Acceptance Letter\n"
            "Addendum 1: Procedural modifications (H4, H5, follow-up survey, 4th condition, "
            "experimenter script, course credit)"
        )

        submission.study_contact_name = "Dr. Christopher Castille"
        submission.study_contact_email = "christopher.castille@nicholls.edu"
        submission.study_contact_phone = "985-449-7015"
        submission.irb_contact_notes = (
            "This study is part of a multi-site global replication under the Advancement of Replications "
            "Initiative in Management (ARIM). The protocol and Addendum 1 (procedural modifications) have "
            "been approved and align with the master protocol."
        )

        submission.save()

        self.stdout.write(self.style.SUCCESS('\n✅ Goal Setting Protocol Details Populated'))
        self.stdout.write(f'   Protocol: {submission.protocol_number}')
        self.stdout.write(f'   Study: {study.title}')
        self.stdout.write(f'   Exemption: {submission.exemption_category}')
