import json
from django.core.management.base import BaseCommand
from apps.studies.models import Study, ProtocolSubmission

class Command(BaseCommand):
    help = 'Dump protocol submission fields for a specific study ID to a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('study_id', type=str, nargs='?', default='8dc48b39-b789-4d52-b11b-366472911e7e')

    def handle(self, *args, **options):
        study_id = options['study_id']
        self.stdout.write(f"Searching for study ID: {study_id}...")
        
        try:
            study = Study.objects.get(id=study_id)
            self.stdout.write(self.style.SUCCESS(f"Found study: '{study.title}' (Slug: {getattr(study, 'slug', 'None')})"))
            
            data = {
                'study': {
                    'id': str(study.id),
                    'title': study.title,
                    'slug': getattr(study, 'slug', 'None'),
                    'description': study.description,
                    'consent_text': study.consent_text,
                    'credit_value': float(study.credit_value) if study.credit_value is not None else 0.0,
                    'mode': study.mode,
                    'is_active': study.is_active,
                }
            }
            
            try:
                sub = ProtocolSubmission.objects.get(study=study)
                data['protocol'] = {
                    'pi_name': sub.pi_name,
                    'pi_title': sub.pi_title,
                    'pi_department': sub.pi_department,
                    'pi_email': sub.pi_email,
                    'pi_phone': sub.pi_phone,
                    'co_investigators': sub.co_investigators,
                    'citi_training_completion': sub.citi_training_completion,
                    'review_type_justification': sub.review_type_justification,
                    'protocol_description': sub.protocol_description,
                    'population_description': sub.population_description,
                    'research_procedures': sub.research_procedures,
                    'research_objectives': sub.research_objectives,
                    'research_questions': sub.research_questions,
                    'educational_justification': sub.educational_justification,
                    'recruitment_method': sub.recruitment_method,
                    'recruitment_script': sub.recruitment_script,
                    'inclusion_criteria': sub.inclusion_criteria,
                    'exclusion_criteria': sub.exclusion_criteria,
                    'benefits_to_subjects': sub.benefits_to_subjects,
                    'benefits_to_others': sub.benefits_to_others,
                    'benefits_to_society': sub.benefits_to_society,
                    'payment_compensation': sub.payment_compensation,
                    'costs_to_subjects': sub.costs_to_subjects,
                    'risk_statement': sub.risk_statement,
                    'risk_mitigation': sub.risk_mitigation,
                    'data_collection_methods': sub.data_collection_methods,
                    'data_storage': sub.data_storage,
                    'confidentiality_procedures': sub.confidentiality_procedures,
                    'data_retention': sub.data_retention,
                    'data_access': sub.data_access,
                    'consent_procedures': sub.consent_procedures,
                    'data_monitoring_plan': sub.data_monitoring_plan,
                    'oversight_procedures': sub.oversight_procedures,
                }
                self.style.SUCCESS(f"Found protocol submission details.")
            except ProtocolSubmission.DoesNotExist:
                self.stdout.write(self.style.WARNING("No protocol submission found for this study."))
                data['protocol'] = None

            output_path = 'tmp/live_protocol_dump.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.stdout.write(self.style.SUCCESS(f"Successfully dumped protocol data to: {output_path}"))
            
        except Study.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Study with ID {study_id} does not exist."))
