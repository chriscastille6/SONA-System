"""
Populate Goal Setting protocol submission with full details from the IRB application
and Addendum 1 (Procedural Modifications).
Protocol: IRB 2024-07-30-001 CBA
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.studies.models import Study, ProtocolSubmission


class Command(BaseCommand):
    help = 'Populate Goal Setting protocol with full IRB details'

    def handle(self, *args, **options):
        self.stdout.write('📋 Populating Goal Setting Protocol Details...\n')

        study = Study.objects.filter(slug='goal-setting').first()
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
            "1. Consent: Participants enter the lab in groups of up to 20, review and sign the informed "
            "consent form, which is collected separately to preserve anonymity.\n\n"
            "2. Practice: Participants complete two 1-minute practice rounds to learn the rules of the "
            "anagram task.\n\n"
            "3. Condition assignment: Participants are randomly assigned to one of four conditions: "
            "'do your best', 'mere goal', 'personal goal', or 'reward goal'. Goal conditions receive the "
            "site-calibrated target.\n\n"
            "4. Performance rounds: Participants complete seven 1-minute anagram rounds, solving word "
            "puzzles in their paper workbooks.\n\n"
            "5. Anonymized linking: In an eighth round, participants solve a unique anagram. This unique "
            "word serves as a double-blind identifier to match actual workbook scores with their self-reported "
            "productivity report without collecting names.\n\n"
            "6. Private self-payment: The researcher leaves the room. Participants grade their own work, "
            "fill out an anonymous productivity report, pay themselves from a cash envelope ($14 total starting "
            "balance), and deposit the report and any unearned cash into a secure box.\n\n"
            "7. Demographics and traits: Participants complete a brief questionnaire covering demographics, "
            "manipulation checks, and individual difference scales (including trait loss aversion, "
            "HEXACO-60, and moral identity).\n\n"
            "8. Debriefing: The researcher returns and hands each participant a written debriefing sheet "
            "explaining the study's scientific purpose and replication goals."
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
            "Recruitment will occur via classroom visits using an approved informational flyer. "
            "Instructors may offer course credit or bonus points for participation, and the flyer "
            "mentions a cash reward of up to $14.00."
        )

        submission.inclusion_criteria = (
            "- Undergraduate students or working professionals\n"
            "- 18 years of age or older"
        )

        submission.exclusion_criteria = (
            "- Individuals under 18 years of age"
        )

        submission.recruitment_script = (
            "You are invited to participate in a research study examining how individuals make decisions "
            "during cognitive tasks. This study takes approximately one hour and has received ethics "
            "clearance from the Institutional Review Board. Depending on your instructor's policy, you "
            "may receive course credit, bonus points, or earn up to $14.00 in cash. Participation is "
            "completely voluntary, and all data collected are anonymous."
        )

        submission.benefits_to_subjects = (
            "Participants receive direct financial compensation through the self-payment procedure, "
            "keeping at least $7.00 and up to $14.00 (averaging about $10.00) depending on their experimental "
            "condition. They also receive a detailed debriefing sheet explaining the logic and value of "
            "open-science replication research."
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
            "All participants receive an envelope containing $14.00 at the start of the session. "
            "Those in the 'do your best', 'mere goal', and 'personal goal' conditions are instructed to "
            "keep $10.00. Those in the 'reward goal' condition are instructed to keep $7.00 plus an "
            "additional $1.00 for each round they met their goal (on average, they receive approximately $10.00). "
            "All participants return any unearned cash in a sealed envelope placed in a secure collection "
            "box while the researcher is out of the room. This process ensures complete privacy and guarantees "
            "every participant receives at least $7.00."
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
            "a separate productivity report for self-reported performance, and a follow-up survey for "
            "manipulation and data quality checks. Hard copies are collected in a secure box."
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
            "Participants provide written informed consent before beginning the session. The consent form "
            "details the study's purpose, procedures, risks, and benefits, emphasizing that participation "
            "is entirely voluntary and that they may withdraw at any time without penalty. Students who "
            "choose not to participate are offered an equivalent alternative assignment for equal course credit."
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
            "Dr. Kaitlin Gravois (Instructor of Management), kaitlin.gravois@nicholls.edu, 985-448-4187\n"
            "Dr. Adrien Maught (Instructor of Management), adrien.maught@nicholls.edu, 985-448-4194"
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
            "Appendix A: Recruitment Flyer / Announcement\n"
            "Appendix B: Informed Consent Statement\n"
            "Appendix C: Anagram Task Workbook (Study Instrument)\n"
            "Appendix D: Participant Productivity Report\n"
            "Appendix E: Debriefing & Appreciation Letter (to be distributed at study conclusion)\n"
            "Appendix F: Approved UWaterloo Master Protocol\n"
            "Appendix G: Psychological Science Registered Report Manuscript\n"
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
