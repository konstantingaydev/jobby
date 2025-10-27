from django import forms
from django.contrib.auth.models import User
from .models import EmailMessage, InternalMessage, Conversation

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
            from jobs.models import Job
            self.fields['related_job'].queryset = Job.objects.filter(posted_by=self.recruiter)
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

class InternalMessageForm(forms.ModelForm):
    """Form for sending internal messages."""
    
    class Meta:
        model = InternalMessage
        fields = ['content', 'message_type', 'attachment_url', 'attachment_name']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Type your message...',
                'id': 'message-content'
            }),
            'message_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'attachment_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional: Link to document or resource'
            }),
            'attachment_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Attachment name (if URL provided)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        self.recipient = kwargs.pop('recipient', None)
        super().__init__(*args, **kwargs)
        
        # Set default message type based on user type
        if self.sender and hasattr(self.sender, 'profile') and self.sender.profile:
            if self.sender.profile.user_type == 'recruiter':
                self.fields['message_type'].initial = 'job_invite'
            else:
                self.fields['message_type'].initial = 'general'
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) < 1:
            raise forms.ValidationError("Message cannot be empty.")
        if len(content) > 2000:
            raise forms.ValidationError("Message is too long. Please keep it under 2000 characters.")
        return content

class ConversationSearchForm(forms.Form):
    """Form for searching conversations."""
    
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search conversations...'
        })
    )
    
    message_type = forms.ChoiceField(
        choices=[('', 'All Types')] + InternalMessage.MESSAGE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    unread_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class StartConversationForm(forms.Form):
    """Form for starting a new conversation."""
    
    recipient = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    initial_message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Write your initial message...'
        })
    )
    
    message_type = forms.ChoiceField(
        choices=InternalMessage.MESSAGE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    related_job = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    attachment_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional: Link to document or resource'
        })
    )
    
    attachment_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Attachment name (if URL provided)'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        
        if self.sender:
            # Filter recipients based on sender type
            try:
                if hasattr(self.sender, 'profile') and self.sender.profile and self.sender.profile.user_type == 'recruiter':
                    # Recruiters can message job seekers
                    self.fields['recipient'].queryset = User.objects.filter(
                        profile__user_type='regular'
                    ).exclude(id=self.sender.id).select_related('profile')
                    
                    # Show recruiter's jobs
                    from jobs.models import Job
                    self.fields['related_job'].queryset = Job.objects.filter(posted_by=self.sender)
                else:
                    # Job seekers can message recruiters
                    self.fields['recipient'].queryset = User.objects.filter(
                        profile__user_type='recruiter'
                    ).exclude(id=self.sender.id).select_related('profile')
                    self.fields['related_job'].queryset = None
                    self.fields['related_job'].widget = forms.HiddenInput()
            except Exception:
                # Fallback: show all users except sender
                self.fields['recipient'].queryset = User.objects.exclude(id=self.sender.id)
        else:
            # If no sender, show all users
            self.fields['recipient'].queryset = User.objects.all()
    
    def clean_initial_message(self):
        message = self.cleaned_data.get('initial_message')
        if not message or len(message.strip()) < 1:
            raise forms.ValidationError("Initial message cannot be empty.")
        return message
