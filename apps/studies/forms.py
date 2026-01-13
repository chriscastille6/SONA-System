"""
Forms for studies app.
"""
from django import forms
from .models import Study


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
