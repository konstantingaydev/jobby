from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    """Form for job seekers to apply to jobs with a personalized note"""
    
    class Meta:
        model = Application
        fields = ['cover_note']
        widgets = {
            'cover_note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write a personalized note to make your application stand out (optional)...',
                'maxlength': 1000
            })
        }
        labels = {
            'cover_note': 'Cover Note'
        }
        help_texts = {
            'cover_note': 'Add a personal touch to your application. Mention why you\'re interested in this role and what makes you a great fit.'
        }

class ApplicationStatusUpdateForm(forms.ModelForm):
    """Form for recruiters to update application status"""
    
    class Meta:
        model = Application
        fields = ['status', 'recruiter_notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'recruiter_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add internal notes about this application...'
            })
        }
        labels = {
            'status': 'Application Status',
            'recruiter_notes': 'Internal Notes'
        }

class ApplicationFilterForm(forms.Form):
    """Form for filtering applications"""
    
    STATUS_CHOICES = [('', 'All Statuses')] + Application.STATUS_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Applied From'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Applied To'
    )
    
    company = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by company name...'
        }),
        label='Company'
    )
