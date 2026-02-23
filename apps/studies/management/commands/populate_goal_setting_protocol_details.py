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
            "(same goal + $2 per round met), and (iv) personal goal (mere goal without 'prior students' "
            "reference). Participants have the opportunity to overstate performance and (in reward goal) "
            "take unearned cash. Sponsored by ARIM (Advancement of Replications Initiative in Management)."
        )

        submission.population_description = (
            "Undergraduate students and working professionals. Multi-site study across universities "
            "(e.g., Nicholls State University, University of Waterloo, Otto Beisheim School of Management, "
            "UC Louvain, Florida Atlantic University). At Nicholls: students from BSAD 101 (Powell 140). "
            "All participants must be 18 or older. Participation is voluntary."
        )

        submission.research_procedures = (
            "1. Consent: Participants read and sign informed consent. Materials assigned randomly for double-blind.\n\n"
            "2. Participant ID: Participants generate unique ID via https://chriscastille6.github.io/CANDIDATE-ID-GENERATOR/\n\n"
            "3. Practice Rounds: Two 1-minute anagram rounds (create words from 7 letters).\n\n"
            "4. Condition Assignment: Random assignment to do your best, mere goal, reward goal, or personal goal. "
            "Goal conditions receive 90th percentile target from pilot (e.g., 9 words).\n\n"
            "5. Performance Rounds: Eight 1-minute anagram rounds. Round 8 uses unique anagram for data linking.\n\n"
            "6. Self-Payment: Experimenters leave room. Participants check work, complete Productivity Report, "
            "pay themselves ($10 for do your best/mere/personal; $2/round for reward goal), seal envelope.\n\n"
            "7. Follow-Up Survey: Manipulation checks (goal recall, commitment), attention check, "
            "open-ended (exclude data? study purpose?). Optional: HEXACO-60, Moral Identity, Need for Achievement.\n\n"
            "8. Debriefing: Immediate debriefing (minimize diffusion); full debrief via email after data collection."
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
            "ARIM initiative uses replication-focused research to help doctoral students learn "
            "scientific research skills. Dr. Castille (PI) and Dr. Ann-Marie Castille support "
            "junior scholars (Adrien Maught, Kaitlin Gravois). Design builds on Schweitzer et al. (2004)."
        )

        submission.recruitment_method = (
            "Classroom visits with flyer (Appendix F). Instructors may offer bonus points or course credit. "
            "Flyer mentions up to $14 cash reward. Participants bring cell phone for ID generator."
        )

        submission.inclusion_criteria = (
            "- Undergraduate students or working professionals\n"
            "- 18 years of age or older\n"
            "- Must have cell phone for participant ID generator (if used)"
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
            "Do your best, mere goal, personal goal: $10 flat. Reward goal: $2 per round met (max $14). "
            "All participants receive $16 envelope at start; unearned money returned in sealed envelope."
        )

        submission.costs_to_subjects = (
            "Approximately 1 hour. No monetary cost (participants receive compensation)."
        )

        submission.review_type_justification = (
            "Exempt under Category D: data obtained through educational tests (cognitive/anagram task) "
            "and recorded so subjects cannot be identified. Anonymous participation; unique anagram "
            "allows measurement of overstating without identifying individuals. Minimal risk. "
            "Mild deception (participants told 'decision making' study) disclosed in debrief."
        )

        submission.exemption_category = "Category D: Educational tests, anonymous data"
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
            "- Debriefing after data collection\n"
            "- Counseling resources provided"
        )

        submission.data_collection_methods = (
            "Paper workbooks (anagram responses, goal commitment), productivity report (self-rated "
            "performance), follow-up survey (manipulation checks, HEXACO-60, Moral Identity, Need for "
            "Achievement). Optional participant ID generator. Data coded by researchers A/B; Researcher C "
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
            "PI (Dr. Christopher Castille), Co-Is (Adrien Maught, Kaitlin Gravois, Dr. Ann-Marie "
            "Castille), and authorized ARIM collaborators. Anonymized data shared publicly via OSF."
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
        submission.pi_title = "Assistant Professor"
        submission.pi_department = "Management and Marketing"
        submission.pi_email = "christopher.castille@nicholls.edu"
        submission.pi_phone = "985-449-7015"
        submission.co_investigators = (
            "Mr. Adrien Maught, adrien.maught@nicholls.edu, 985-448-4194\n"
            "Mrs. Kaitlin Gravois, kaitlin.gravois@nicholls.edu, 985-448-4187\n"
            "Dr. Ann-Marie R. Castille, ann-marie.castille@nicholls.edu, 985-448-4738"
        )

        submission.citi_training_completion = (
            "All investigators have completed CITI Program training. Dr. Christopher Castille "
            "(Faculty Researchers), Dr. Ann-Marie Castille, Kaitlin Gravois (Faculty Researchers), "
            "Adrien Maught (Social/Behavioral RCR). Certificates on file."
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
            "Appendix A: Detailed study goals and hypotheses\n"
            "Appendix B: Anagram materials, goal commitment, demographics, answer sheet\n"
            "Appendix C: Procedure details\n"
            "Appendix D: Debriefing materials\n"
            "Appendix E: Informed consent form\n"
            "Appendix F: Recruitment flyer\n"
            "Addendum 1: Procedural modifications (H4, H5, follow-up survey, 4th condition, "
            "personality measures, experimenter script, course credit)"
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
