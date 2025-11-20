from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'company_name', 'location', 'salary_min', 'salary_max',
            'employment_type', 'experience_level', 'description', 'requirements',
            'benefits', 'is_remote', 'visa_sponsorship', 
            'image', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Software Engineer'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Tech Corp Inc.'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 123 Main St, San Francisco, CA or just San Francisco, CA'
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 80000'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 120000'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe the role, responsibilities, and what the candidate will be working on...'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List required skills, qualifications, and experience...'
            }),
            'benefits': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List benefits, perks, and what makes this opportunity attractive...'
            }),
            'is_remote': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'visa_sponsorship': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Job Title',
            'company_name': 'Company Name',
            'location': 'Job Location',
            'salary_min': 'Minimum Salary ($)',
            'salary_max': 'Maximum Salary ($)',
            'employment_type': 'Employment Type',
            'experience_level': 'Experience Level',
            'description': 'Job Description',
            'requirements': 'Requirements',
            'benefits': 'Benefits & Perks',
            'is_remote': 'Remote Position',
            'visa_sponsorship': 'Visa Sponsorship Available',
            'image': 'Company Logo/Image',
            'is_active': 'Active Job Posting'
        }
        help_texts = {
            'salary_min': 'Leave blank if not specified',
            'salary_max': 'Leave blank if not specified',
            'benefits': 'Optional - describe benefits and perks',
            'is_remote': 'Check if this is a remote position',
            'visa_sponsorship': 'Check if visa sponsorship is available',
            'image': 'Optional - upload a company logo or relevant image',
            'location': 'Enter full address (recommended) or city name. The map will display this location accurately. For remote positions, check the "Remote Position" box below.',
            'is_active': 'Uncheck to temporarily hide this job posting'
        }

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError("Minimum salary cannot be greater than maximum salary.")
        
        return cleaned_data


class JobSearchForm(forms.Form):
    """Advanced search form for job seekers"""
    
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Job title, company, or keywords...'
        }),
        label='Search'
    )
    
    skills = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Python, JavaScript, React, etc.'
        }),
        label='Skills',
        help_text='Comma-separated skills'
    )
    
    location = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, State, or "Remote"'
        }),
        label='Location'
    )
    
    employment_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Job.EMPLOYMENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Employment Type'
    )
    
    experience_level = forms.ChoiceField(
        choices=[('', 'All Levels')] + Job.EXPERIENCE_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Experience Level'
    )
    
    salary_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 50000'
        }),
        label='Minimum Salary ($)',
        min_value=0
    )
    
    salary_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 100000'
        }),
        label='Maximum Salary ($)',
        min_value=0
    )
    
    is_remote = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Remote work only'
    )
    
    visa_sponsorship = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Visa sponsorship available'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError("Minimum salary cannot be greater than maximum salary.")
        
        return cleaned_data
