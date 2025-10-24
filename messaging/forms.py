from django import forms
from django.contrib.auth.models import User
from .models import EmailMessage

class EmailCandidateForm(forms.ModelForm):
    """Form for recruiters to send emails to candidates."""
    
    class Meta:
        model = EmailMessage
        fields = ['subject', 'message', 'message_type', 'related_job']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Write your message to the candidate...'
            }),
            'message_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'related_job': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.recruiter = kwargs.pop('recruiter', None)
        self.candidate = kwargs.pop('candidate', None)
        super().__init__(*args, **kwargs)
        
        # Filter related jobs to only show jobs posted by the recruiter
        if self.recruiter:
            self.fields['related_job'].queryset = self.recruiter.job_set.all()
            self.fields['related_job'].required = False
        
        # Set default subject based on message type
        if not self.instance.pk:  # Only for new messages
            self.fields['subject'].initial = f"Opportunity from {self.recruiter.get_full_name() or self.recruiter.username}"
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if not message or len(message.strip()) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long.")
        return message
    
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if not subject or len(subject.strip()) < 5:
            raise forms.ValidationError("Subject must be at least 5 characters long.")
        return subject

class ReplyEmailForm(forms.ModelForm):
    """Form for replying to emails."""
    
    class Meta:
        model = EmailMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Write your reply...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.parent_message = kwargs.pop('parent_message', None)
        super().__init__(*args, **kwargs)
        
        if self.parent_message:
            self.fields['message'].initial = f"\n\n--- Original Message ---\n{self.parent_message.message}"
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if not message or len(message.strip()) < 10:
            raise forms.ValidationError("Reply must be at least 10 characters long.")
        return message

class EmailSearchForm(forms.Form):
    """Form for searching email messages."""
    
    SEARCH_CHOICES = [
        ('all', 'All Messages'),
        ('sent', 'Sent Messages'),
        ('received', 'Received Messages'),
        ('unread', 'Unread Messages'),
    ]
    
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search messages...'
        })
    )
    
    message_type = forms.ChoiceField(
        choices=[('', 'All Types')] + EmailMessage.MESSAGE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + EmailMessage.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    message_filter = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
