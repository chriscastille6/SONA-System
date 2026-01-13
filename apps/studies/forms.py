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
        ]
        # Note: 'use_ai_review' is not a model field, handled separately in view
