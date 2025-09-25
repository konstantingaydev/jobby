from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Job(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]
    
    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive'),
    ]
    
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, help_text="Job title", default="")
    company_name = models.CharField(max_length=255, help_text="Company name", default="")
    location = models.CharField(max_length=255, help_text="Job location", default="")
    salary_min = models.IntegerField(null=True, blank=True, help_text="Minimum salary")
    salary_max = models.IntegerField(null=True, blank=True, help_text="Maximum salary")
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full-time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='entry')
    description = models.TextField(help_text="Job description and requirements", default="")
    requirements = models.TextField(help_text="Required skills and qualifications", default="")
    benefits = models.TextField(blank=True, help_text="Benefits and perks")
    image = models.ImageField(upload_to='job_images/', null=True, blank=True)
    
    # Recruiter information
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Whether the job posting is active")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company_name}"
    
    @property
    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} - ${self.salary_max:,}"
        elif self.salary_min:
            return f"${self.salary_min:,}+"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,}"
        return "Salary not specified"