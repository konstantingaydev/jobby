from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'company_name', 'location', 'salary_min', 'salary_max',
            'employment_type', 'experience_level', 'description', 'requirements',
            'benefits', 'image', 'is_active'
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
                'placeholder': 'e.g., San Francisco, CA or Remote'
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
            'location': 'Location',
            'salary_min': 'Minimum Salary ($)',
            'salary_max': 'Maximum Salary ($)',
            'employment_type': 'Employment Type',
            'experience_level': 'Experience Level',
            'description': 'Job Description',
            'requirements': 'Requirements',
            'benefits': 'Benefits & Perks',
            'image': 'Company Logo/Image',
            'is_active': 'Active Job Posting'
        }
        help_texts = {
            'salary_min': 'Leave blank if not specified',
            'salary_max': 'Leave blank if not specified',
            'benefits': 'Optional - describe benefits and perks',
            'image': 'Optional - upload a company logo or relevant image',
            'is_active': 'Uncheck to temporarily hide this job posting'
        }

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError("Minimum salary cannot be greater than maximum salary.")
        
        return cleaned_data
