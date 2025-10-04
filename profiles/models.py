from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Profile(models.Model):
    USER_TYPE_CHOICES = (
        ('recruiter', 'Recruiter'),
        ('regular', 'Job Seeker'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='regular')
    
    # Job Seeker Profile Fields
    headline = models.CharField(max_length=200, blank=True, help_text="Professional headline or title")
    bio = models.TextField(blank=True, help_text="Brief professional summary")
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=255, blank=True, help_text='Candidate location')
    
    # Links
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn profile URL")
    github_url = models.URLField(blank=True, help_text="GitHub profile URL")
    portfolio_url = models.URLField(blank=True, help_text="Personal website or portfolio URL")
    
    # Candidate-specific fields from job-posting branch
    skills_text = models.TextField(blank=True, default='', help_text='Comma-separated list of skills (simple version)')
    projects_text = models.TextField(blank=True, default='', help_text='Short description/list of projects')
    
    # Profile completion tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Privacy Settings
    PRIVACY_CHOICES = [
        ('public', 'Public - Visible to everyone'),
        ('recruiters', 'Recruiters Only - Visible to recruiters and admins'),
        ('private', 'Private - Only visible to me'),
    ]
    
    profile_visibility = models.CharField(
        max_length=20, 
        choices=PRIVACY_CHOICES, 
        default='recruiters',
        help_text="Control who can see your profile"
    )
    
    # Individual section privacy controls
    show_contact_info = models.BooleanField(default=True, help_text="Show phone and email to viewers")
    show_skills = models.BooleanField(default=True, help_text="Show skills section")
    show_education = models.BooleanField(default=True, help_text="Show education section")
    show_experience = models.BooleanField(default=True, help_text="Show work experience section")
    show_links = models.BooleanField(default=True, help_text="Show social/portfolio links")
    
    def __str__(self):
        return f'{self.user.username} Profile - {self.get_user_type_display()}'
    
    def get_absolute_url(self):
        return reverse('profiles:profile_detail', kwargs={'pk': self.pk})

class Skill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    proficiency_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], default='intermediate')
    
    class Meta:
        unique_together = ('profile', 'name')
    
    def __str__(self):
        return f"{self.name} ({self.get_proficiency_level_display()})"

class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank if currently studying")
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.degree} at {self.institution}"

class WorkExperience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='work_experience')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank if currently working")
    description = models.TextField(blank=True, help_text="Describe your responsibilities and achievements")
    is_current = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.position} at {self.company}"

class Project(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Describe the project and your role")
    technologies = models.CharField(max_length=500, blank=True, help_text="Technologies used (comma-separated)")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank if ongoing")
    project_url = models.URLField(blank=True, help_text="Link to project (GitHub, live demo, etc.)")
    is_featured = models.BooleanField(default=False, help_text="Feature this project on profile")
    
    class Meta:
        ordering = ['-is_featured', '-end_date', '-start_date']
    
    def __str__(self):
        return self.title
    
    @property
    def technologies_list(self):
        """Return technologies as a list"""
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]
        return []
