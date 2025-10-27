from django import forms
from django.contrib.auth.models import User
from .models import Profile, Skill, Education, WorkExperience, Project

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['headline', 'bio', 'phone', 'email', 'location', 'linkedin_url', 'github_url', 'portfolio_url']
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Software Engineer | Full Stack Developer'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell recruiters about yourself...'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, State'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/yourprofile'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/yourusername'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourportfolio.com'}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'proficiency_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Python, JavaScript, Project Management'}),
            'proficiency_level': forms.Select(attrs={'class': 'form-select'}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'gpa', 'description']
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'University Name'}),
            'degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bachelor of Science'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Computer Science'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '4.0', 'placeholder': '3.75'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Relevant coursework, achievements, etc.'}),
        }

class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ['company', 'position', 'location', 'start_date', 'end_date', 'is_current', 'description']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, State'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your responsibilities and achievements...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end_date'].required = False

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'technologies', 'start_date', 'end_date', 'project_url', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the project and your role...'}),
            'technologies': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, React, PostgreSQL, etc.'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'project_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/username/project'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end_date'].required = False

class PrivacySettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_visibility', 'show_contact_info', 'show_skills', 'show_education', 'show_experience', 'show_links']
        widgets = {
            'profile_visibility': forms.Select(attrs={'class': 'form-select'}),
            'show_contact_info': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_skills': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_education': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_experience': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_links': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'profile_visibility': 'Profile Visibility',
            'show_contact_info': 'Show Contact Information',
            'show_skills': 'Show Skills Section',
            'show_education': 'Show Education Section',
            'show_experience': 'Show Work Experience Section',
            'show_links': 'Show Social/Portfolio Links',
        }
