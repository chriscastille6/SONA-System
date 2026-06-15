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
        # PROTOCOL DETAILS FROM IRB APPLICATION + ADDENDUM 1
        # ================================================================
        self.stdout.write('\n📝 Populating protocol fields...')

        submission.protocol_description = (
            "Replication of Schweitzer, Ordóñez, and Douma (2004) examining whether goal setting "
            "motivates unethical behavior. Participants complete anagram tasks under four experimental "
            "conditions: (i) do your best, (ii) mere goal (90th percentile from pilot), (iii) reward goal "
            "(same goal + $7 base + $1 per round met), and (iv) personal goal (mere goal without 'prior students' "
            "reference). Participants have the opportunity to overstate performance and (in reward goal) "
            "take unearned cash. Sponsored by ARIM (Advancement of Replications Initiative in Management) "
            "and aligned with the master multi-site global research project."
        )

        submission.population_description = (
            "Undergraduate students and working professionals. Multi-site study across universities "
            "(e.g., Nicholls State University, University of Waterloo, Otto Beisheim School of Management, "
            "UC Louvain, Florida Atlantic University). At Nicholls: students from BSAD 101 (Powell 140). "
            "All participants must be 18 or older. Participation is voluntary."
        )

        submission.research_procedures = (
            "1. Consent: Participants read and sign informed consent. Materials are assigned randomly for a double-blind design.\n\n"
            "2. Practice Rounds: Two 1-minute anagram rounds (create words from 7 letters) to familiarize with the task rules.\n\n"
            "3. Condition Assignment: Random assignment to do your best, mere goal, reward goal, or personal goal. "
            "Goal conditions receive the site-calibrated 90th percentile target from pilot (e.g., 9 words).\n\n"
            "4. Performance Rounds: Seven 1-minute anagram rounds where participants solve word puzzles.\n\n"
            "5. Anagram Pilot / Linking Round: An 8th round is completed (presented as an anagram pilot round) "
            "using an anagram unique to each participant. This unique anagram acts as a secure, double-blind "
            "linking key to correlate the workbook with the anonymous self-reported Productivity Report.\n\n"
            "6. Self-Payment: Experimenters leave the room. Participants check their work, complete the anonymous "
            "Productivity Report, pay themselves from their $14 envelope ($10 flat for do-your-best/mere/personal; "
            "$7 base + $1 per round met for reward goal), and place their reports in a sealed envelope.\n\n"
            "7. Follow-Up Survey: Manipulation checks (goal recall, goal type), attention check, "
            "and an open-ended data quality check (whether to use their data).\n\n"
            "8. Debriefing: Full debrief sheet/letter will be distributed to participants via email after data collection has fully concluded to prevent information diffusion across classes."
        )

        submission.research_objectives = (
            "To replicate Schweitzer et al. (2004) findings on goal setting and unethical behavior: "
            "(1) People with specific unmet goals overstate more than do-your-best; (2) Reward goals "
            "increase overstating vs. mere goals; (3) Proximity to goal (just shy) increases overstating; "
            "(4) Personal goals reduce overstating vs. mere/reward; (5) Proximity × goal commitment "
            "moderates overstating."
        )

        submission.research_questions = (
            "H1: People with specific, unmet goals overstate performance more than do-your-best.\n"
            "H2: Unmet reward goals increase overstating vs. unmet mere goals.\n"
            "H3: People just shy of goal overstate more than those far from goal.\n"
            "H4: Personal goals (unmet) reduce overstating vs. mere (H4a) or reward (H4b) goals.\n"
            "H5: Proximity × goal commitment: most overstating when just shy + highly committed."
        )

        submission.educational_justification = (
            "ARIM initiative uses replication-focused research to help students and faculty learn "
            "scientific research skills. Dr. Christopher Castille (PI) and Dr. Ann-Marie R. Castille support "
            "junior scholars and co-investigators (Dr. Adrien Maught, Dr. Kaitlin Gravois, Dr. Samantha Falgout). "
            "Design builds on Schweitzer et al. (2004)."
        )

        submission.recruitment_method = (
            "Classroom visits with flyer (Appendix F). Instructors may offer bonus points or course credit. "
            "Flyer mentions up to $14 cash reward."
        )

        submission.inclusion_criteria = (
            "- Undergraduate students or working professionals\n"
            "- 18 years of age or older"
        )

        submission.exclusion_criteria = (
            "- Under 18\n"
            "- Children and other criteria per IRB guidelines"
        )

        submission.recruitment_script = (
            "You are invited to participate in a research study on decision making. This study has "
            "received ethics clearance from the IRB at Nicholls State University. You may receive "
            "bonus points, course credit, or cash (up to $14) depending on your instructor. "
            "Participation takes ~1 hour. All data are anonymous."
        )

        submission.benefits_to_subjects = (
            "Small cash reward (~$10 for do your best/mere/personal; up to $14 for reward goal). "
            "Bonus points or course credit if instructor approves."
        )

        submission.benefits_to_others = (
            "Knowledge about whether goal setting practices drive unethical behavior; insights "
            "for managers and employees."
        )

        submission.benefits_to_society = (
            "Understanding how goal setting influences ethical decision-making; informing practices "
            "to mitigate unethical behavior while preserving performance benefits."
        )

        submission.payment_compensation = (
            "Participants receive an envelope containing $14 at the start of the study. "
            "Those in the do-your-best, mere goal, and personal goal conditions are instructed to keep a flat $10. "
            "Those in the reward goal condition are instructed to keep a base of $7 plus $1 for each round in "
            "which they met their goal (maximum $14). All participants return any unearned cash in a sealed "
            "envelope placed in a secure collection box, completely privately."
        )

        submission.costs_to_subjects = (
            "Approximately 1 hour. No monetary cost (participants receive compensation)."
        )

        submission.review_type_justification = (
            "Exempt under Category 2 of the revised Common Rule (45 CFR 46.104(d)(2)): "
            "Data are obtained through educational tests (cognitive/anagram task) and standard survey "
            "procedures. Information is recorded in such a manner that the identity of the human "
            "subjects cannot be readily ascertained, directly or through identifiers linked to the "
            "subjects. The double-blind design ensures anonymous participation, where a unique 8th-round "
            "anagram safely correlates performance to reports without ever identifying individual students. Minimal risk."
        )

        submission.exemption_category = "Exempt Category 2 (45 CFR 46.104(d)(2))"
        submission.expedited_category = ""

        submission.risk_statement = (
            "Minimal risk. Task may be mildly upsetting but no more than everyday work life. "
            "Participants may overstate performance or take unearned money; data are anonymous. "
            "Psychological support available (Nicholls Counseling Center)."
        )

        submission.risk_mitigation = (
            "- Double-blind: experimenters do not know condition\n"
            "- Anonymous: no names on materials; materials randomly assigned\n"
            "- Self-payment in private; experimenters leave room\n"
            "- Unique anagram links data without identifying participants\n"
            "- Delayed debriefing via email at study conclusion\n"
            "- Counseling resources provided"
        )

        submission.data_collection_methods = (
            "Paper workbooks (anagram responses, goal commitment, trait loss aversion), productivity report (self-rated "
            "performance), follow-up survey (manipulation checks). Data coded by researchers A/B; Researcher C "
            "(Castille) links via unique anagram and replaces with new ID. Stored on OSF."
        )

        submission.data_storage = (
            "Open Science Framework (https://osf.io/f5u39/). Encrypted, access controls. "
            "Anonymous data; no identifiers. Paper copies retained 5-7 years per APA guidelines."
        )

        submission.confidentiality_procedures = (
            "- No names or identifying info on workbooks\n"
            "- Unique anagram links data but not to person\n"
            "- Researcher C replaces anagram with new ID before analysis\n"
            "- Anonymized dataset shared for replication"
        )

        submission.data_retention = (
            "Paper files 5-7 years per APA guidelines. Anonymized dataset shared via OSF for "
            "replication and meta-analysis."
        )

        submission.data_access = (
            "PI (Dr. Christopher Castille), Co-Is (Dr. Ann-Marie R. Castille, Dr. Samantha Falgout, "
            "Dr. Kaitlin Gravois, Dr. Adrien Maught), and authorized ARIM collaborators. "
            "Anonymized data shared publicly via OSF."
        )

        submission.consent_procedures = (
            "Written informed consent at start. Consent form includes purpose, procedures, risks, "
            "benefits, voluntary participation, right to withdraw, anonymity, contact info. "
            "Participation indicates consent. Students may decline and complete alternative assignment."
        )

        submission.estimated_start_date = "Fall 2024"
        submission.estimated_completion_date = "Spring 2025"
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
            "Site-specific consent and counseling resources. Demographics include ethnic origin and "
            "English proficiency for non-English sites."
        )

        submission.financial_interest_none = True
        submission.financial_interest_disclosure = ""

        submission.data_monitoring_plan = (
            "Three researchers code data separately. Researcher A: workbooks (performance, commitment, "
            "demographics). Researcher B: productivity report and payment. Researcher C: links via "
            "unique anagram, replaces with new ID. Prevents any single researcher from identifying participants."
        )

        submission.oversight_procedures = (
            "PI (Dr. Christopher Castille) oversees data collection. Multi-site IRBs oversee local "
            "sites. ARIM consortium coordination. Data coding split to prevent identification."
        )

        submission.publication_plan = (
            "Results submitted to peer-reviewed journals (e.g., Academy of Management Journal). "
            "All data aggregated and anonymous. OSF pre-registration for replication."
        )

        submission.data_sharing_plan = (
            "Anonymized dataset shared via Open Science Framework (osf.io/f5u39/) for replication "
            "and meta-analysis. No identifying information."
        )

        submission.participant_access_to_results = (
            "Debriefing email sent after data collection. Participants may request summary from "
            "research team (kaitlin.gravois@nicholls.edu)."
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
            "ARIM initiative: arimweb.org. This study is part of a multi-site replication. "
            "Protocol valid per IRB approval. Addendum 1 (Procedural Modifications) approved."
        )

        submission.save()

        self.stdout.write(self.style.SUCCESS('\n✅ Goal Setting Protocol Details Populated'))
        self.stdout.write(f'   Protocol: {submission.protocol_number}')
        self.stdout.write(f'   Study: {study.title}')
        self.stdout.write(f'   Exemption: {submission.exemption_category}')
