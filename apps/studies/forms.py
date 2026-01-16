"""
Forms for studies app.
"""
from django import forms
from .models import Study, ProtocolSubmission


class StudyForm(forms.ModelForm):
    """Form for creating/editing studies."""
    
    class Meta:
        model = Study
        fields = [
            'title',
            'description',
            'mode',
            'credit_value',
            'is_classroom_based',
            'consent_text',
            'involves_deception',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Emotional Intelligence and Fluid Intelligence Study'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what participants will do, time requirements, etc.'
            }),
            'mode': forms.Select(attrs={'class': 'form-select'}),
            'credit_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10',
                'step': '0.5',
                'placeholder': '1.0'
            }),
            'consent_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter the consent form text that participants must agree to...'
            }),
            'is_classroom_based': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'involves_deception': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Study Title',
            'description': 'Study Description',
            'mode': 'Study Type',
            'credit_value': 'Credits Offered',
            'consent_text': 'Consent Form Text',
            'is_classroom_based': 'Classroom-based study (not for general signup)',
            'involves_deception': 'Involves deception (requires IRB Chair review)',
            'is_active': 'Make study active (visible to participants)',
        }
        help_texts = {
            'is_classroom_based': 'Check if this study is only for students in a specific class',
            'involves_deception': 'Check if the study involves any form of deception',
        }


class ProtocolSubmissionForm(forms.ModelForm):
    """Comprehensive form for IRB protocol submission."""
    
    REVIEW_TYPE_CHOICES = [
        ('exempt', 'Exempt'),
        ('expedited', 'Expedited Review'),
        ('full', 'Full Board Review'),
    ]
    
    EXEMPTION_CATEGORIES = [
        ('', 'Not applicable'),
        ('A', 'Educational settings with normal educational practices'),
        ('B', 'Public officials or candidates'),
        ('C', 'Existing public data/documents'),
        ('D', 'Anonymous surveys/interviews'),
        ('E', 'Public behavior observation'),
    ]
    
    EXPEDITED_CATEGORIES = [
        ('', 'Not applicable'),
        ('4', 'Category (4) - Noninvasive data collection'),
        ('7', 'Category (7) - Research on individual/group characteristics'),
        ('8', 'Category (8) - Continuing review'),
    ]
    
    # Review type and basic info
    pi_suggested_review_type = forms.ChoiceField(
        choices=REVIEW_TYPE_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Review Type Suggestion',
        help_text='Based on your protocol, suggest which review type you believe is appropriate'
    )
    involves_deception = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='This protocol involves deception',
        help_text='Protocols involving deception automatically require full board review by the IRB Chair'
    )
    use_ai_review = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Run AI-assisted review before submission',
        help_text='AI review will analyze your protocol for potential ethical issues (optional)'
    )
    
    # Protocol Description
    protocol_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Protocol Description',
        help_text='Detailed description of the research project or proposal'
    )
    population_description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Population of Human Subjects',
        help_text='Describe the population for this study (e.g., undergraduate students, age requirements, etc.)'
    )
    research_procedures = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        label='Research Procedures and Data Collection',
        help_text='Step-by-step description of what participants will do, time required, and data collection methods'
    )
    research_objectives = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Research Objectives',
        help_text='Primary research objectives and goals'
    )
    research_questions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Research Questions or Hypotheses',
        help_text='Research questions or hypotheses (if applicable)'
    )
    educational_justification = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Educational Justification',
        help_text='If this is an educational exercise, explain why it is specifically designed for this educational context'
    )
    
    # Recruitment
    recruitment_method = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='How will you recruit subjects?',
        help_text='Describe your recruitment methods'
    )
    recruitment_script = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Recruitment Script',
        help_text='Exact script or materials used for recruitment'
    )
    inclusion_criteria = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Criteria for Including Subjects',
        help_text='Specific criteria for who can participate'
    )
    exclusion_criteria = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Criteria for Excluding Subjects',
        help_text='Specific criteria for who cannot participate'
    )
    
    # Benefits and Costs
    benefits_to_subjects = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Benefits to Human Subjects',
        help_text='Benefits to the human subjects involved in the research'
    )
    benefits_to_others = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Benefits to Others',
        help_text='Benefits to individuals who are not subjects but may have similar problems'
    )
    benefits_to_society = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Benefits to Society',
        help_text='Benefits to society in general'
    )
    payment_compensation = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Payment or Compensation',
        help_text='Describe any payment, compensation, or course credit provided to participants'
    )
    costs_to_subjects = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Costs to Subjects',
        help_text='Time required, any monetary costs, repeated testing, etc.'
    )
    
    # Review Type Justification
    review_type_justification = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Justification for Review Type',
        help_text='Explain why your protocol qualifies for the requested review type (exempt/expedited/full)'
    )
    exemption_category = forms.ChoiceField(
        choices=EXEMPTION_CATEGORIES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Exemption Category',
        help_text='If requesting exempt status, select the applicable exemption category'
    )
    expedited_category = forms.ChoiceField(
        choices=EXPEDITED_CATEGORIES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Expedited Review Category',
        help_text='If requesting expedited review, select the applicable category'
    )
    
    # Risks
    risk_statement = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Statement of Risk',
        help_text='Describe any physical, emotional, social, or legal risks to participants'
    )
    risk_mitigation = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Risk Mitigation Strategies',
        help_text='Describe protections and strategies to minimize risks'
    )
    
    # Data Handling
    data_collection_methods = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Data Collection Methods',
        help_text='Detailed description of data collection methods and instruments'
    )
    data_storage = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Data Storage',
        help_text='How data will be stored and secured'
    )
    confidentiality_procedures = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Confidentiality Procedures',
        help_text='Procedures for maintaining confidentiality or anonymity'
    )
    data_retention = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Data Retention Policy',
        help_text='How long data will be retained and when it will be destroyed'
    )
    data_access = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Data Access',
        help_text='Who will have access to the data'
    )
    
    # Consent Procedures
    consent_procedures = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Consent Procedures',
        help_text='How informed consent will be obtained from participants'
    )
    
    # Additional Information
    estimated_start_date = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Estimated Starting Date',
        help_text='e.g., Spring 2026'
    )
    estimated_completion_date = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Estimated Completion Date',
        help_text='e.g., Spring 2026'
    )
    funding_source = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Source of Project Funds',
        help_text='Describe funding source (e.g., no external funding, grant name, etc.)'
    )
    continuation_of_previous = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Is this a continuation of previously approved research?'
    )
    previous_protocol_number = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Previous HSIRB Protocol Number',
        help_text='If continuation, provide the previous protocol number'
    )
    
    # Investigator Information
    pi_name = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Primary Investigator Name',
        help_text='Full name of the Primary Investigator'
    )
    pi_title = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='PI Title/Position',
        help_text='PI academic title or position'
    )
    pi_department = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='PI Department',
        help_text='Department or college'
    )
    pi_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='PI Email',
        help_text='Primary Investigator email address'
    )
    pi_phone = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='PI Phone',
        help_text='Primary Investigator phone number'
    )
    co_investigators = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Co-Investigators',
        help_text='List all co-investigators (name, title, department, email)'
    )
    citi_training_completion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='CITI Training Completion',
        help_text='CITI training completion dates and certificate numbers for all investigators'
    )
    
    # Vulnerable Populations
    involves_vulnerable_populations = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Involves Vulnerable Populations',
        help_text='Check if this research involves vulnerable populations (children, prisoners, pregnant women, etc.)'
    )
    vulnerable_populations_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Vulnerable Populations Description',
        help_text='Describe which vulnerable populations are involved'
    )
    vulnerable_population_protections = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Vulnerable Population Protections',
        help_text='Specific protections and safeguards for vulnerable populations'
    )
    
    # International Research
    involves_international_research = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Involves International Research',
        help_text='Check if this research involves international participants or locations'
    )
    international_research_locations = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='International Research Locations',
        help_text='Geographic locations where research will be conducted'
    )
    cultural_considerations = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Cultural Considerations',
        help_text='Cultural considerations and adaptations for international research'
    )
    
    # Financial Interests
    financial_interest_disclosure = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Financial Interest Disclosure',
        help_text='Disclose any financial interests or conflicts of interest related to this research'
    )
    financial_interest_none = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='No Financial Interests',
        help_text='Check if there are no financial interests to disclose'
    )
    
    # Study Monitoring
    data_monitoring_plan = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Data Monitoring Plan',
        help_text='Plan for monitoring data collection and quality assurance'
    )
    oversight_procedures = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Oversight Procedures',
        help_text='Procedures for oversight and quality assurance'
    )
    
    # Publication and Dissemination
    publication_plan = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Publication Plan',
        help_text='Plan for publication and dissemination of results'
    )
    data_sharing_plan = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Data Sharing Plan',
        help_text='Plan for sharing data with other researchers or repositories'
    )
    participant_access_to_results = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Participant Access to Results',
        help_text='How participants can access study results (if applicable)'
    )
    
    # Appendices
    appendices_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Appendices Notes',
        help_text='Notes about supporting documents, instruments, or analysis plans (files can be uploaded separately)'
    )
    
    # Additional Contact Information
    study_contact_name = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Study Contact Name',
        help_text='Contact person name (if different from PI)'
    )
    study_contact_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='Study Contact Email',
        help_text='Study contact email address'
    )
    study_contact_phone = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Study Contact Phone',
        help_text='Study contact phone number'
    )
    irb_contact_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='IRB Contact Notes',
        help_text='Additional IRB contact information or notes'
    )
    
    # PI's reviewer suggestions
    suggested_reviewers = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Suggested Reviewers (Optional)',
        help_text='You may suggest reviewers for your protocol. The college representative will make the final assignment, but your suggestions will be considered. Example: "I recommend Jon Murphy (CBA rep) and Julianne Allen as reviewers."'
    )
    
    class Meta:
        model = ProtocolSubmission
        fields = [
            'pi_suggested_review_type',
            'involves_deception',
            'protocol_description',
            'population_description',
            'research_procedures',
            'research_objectives',
            'research_questions',
            'educational_justification',
            'recruitment_method',
            'recruitment_script',
            'inclusion_criteria',
            'exclusion_criteria',
            'benefits_to_subjects',
            'benefits_to_others',
            'benefits_to_society',
            'payment_compensation',
            'costs_to_subjects',
            'review_type_justification',
            'exemption_category',
            'expedited_category',
            'risk_statement',
            'risk_mitigation',
            'data_collection_methods',
            'data_storage',
            'confidentiality_procedures',
            'data_retention',
            'data_access',
            'consent_procedures',
            'estimated_start_date',
            'estimated_completion_date',
            'funding_source',
            'continuation_of_previous',
            'previous_protocol_number',
            # Investigator Information
            'pi_name',
            'pi_title',
            'pi_department',
            'pi_email',
            'pi_phone',
            'co_investigators',
            'citi_training_completion',
            # Vulnerable Populations
            'involves_vulnerable_populations',
            'vulnerable_populations_description',
            'vulnerable_population_protections',
            # International Research
            'involves_international_research',
            'international_research_locations',
            'cultural_considerations',
            # Financial Interests
            'financial_interest_disclosure',
            'financial_interest_none',
            # Study Monitoring
            'data_monitoring_plan',
            'oversight_procedures',
            # Publication and Dissemination
            'publication_plan',
            'data_sharing_plan',
            'participant_access_to_results',
            # Appendices
            'appendices_notes',
            # Additional Contact Information
            'study_contact_name',
            'study_contact_email',
            'study_contact_phone',
            'irb_contact_notes',
            'suggested_reviewers',
        ]
        # Note: 'use_ai_review' is not a model field, handled separately in view
