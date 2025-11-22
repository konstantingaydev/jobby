from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
import urllib.request
import urllib.parse
import json
import ssl

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
    email = models.EmailField(blank=True, help_text="Email address for recruiters to contact you")
    location = models.CharField(max_length=255, blank=True, help_text='Candidate location')
    
    # Coordinates
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Links
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn profile URL")
    github_url = models.URLField(blank=True, help_text="GitHub profile URL")
    portfolio_url = models.URLField(blank=True, help_text="Personal website or portfolio URL")
    
    # Candidate-specific fields
    skills_text = models.TextField(blank=True, default='', help_text='Comma-separated list of skills (simple version)')
    projects_text = models.TextField(blank=True, default='', help_text='Short description/list of projects')
    
    # Tracking
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
    
    show_contact_info = models.BooleanField(default=True, help_text="Show phone and email to viewers")
    show_skills = models.BooleanField(default=True, help_text="Show skills section")
    show_education = models.BooleanField(default=True, help_text="Show education section")
    show_experience = models.BooleanField(default=True, help_text="Show work experience section")
    show_links = models.BooleanField(default=True, help_text="Show social/portfolio links")
    
    def __str__(self):
        return f'{self.user.username} Profile - {self.get_user_type_display()}'
    
    def get_absolute_url(self):
        return reverse('profiles:profile_detail', kwargs={'pk': self.pk})

    # --- MOVED THESE METHODS INSIDE THE CLASS ---
    def _geocode_location(self, location):
        """
        Geocodes the location string to lat/long. 
        Uses the specific User-Agent that we confirmed works in the script.
        """
        if not location:
            return None
        try:
            base = 'https://nominatim.openstreetmap.org/search?format=json&limit=1&q='
            url = base + urllib.parse.quote(location)
            
            headers = {'User-Agent': 'Jobby/1.0 (admin@jobby.example)'} 
            req = urllib.request.Request(url, headers=headers)
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
                data = resp.read().decode('utf-8')
                arr = json.loads(data)
                if arr:
                    return float(arr[0]['lat']), float(arr[0]['lon'])
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None
        return None

    def save(self, *args, **kwargs):
        """
        Automatic trigger: If location changes, fetch new coordinates.
        """
        if self.location:
            old_location = None
            if self.pk:
                try:
                    old_profile = Profile.objects.get(pk=self.pk)
                    old_location = old_profile.location
                except Profile.DoesNotExist:
                    pass
            
            if (self.location != old_location) or (self.latitude is None):
                print(f"Auto-geocoding location for {self.user.username}...")
                coords = self._geocode_location(self.location)
                if coords:
                    self.latitude, self.longitude = coords
                    print(f"  > Saved coordinates: {self.latitude}, {self.longitude}")
                else:
                    print("  > Could not geocode location.")
                    
        super().save(*args, **kwargs)
    # --- END OF PROFILE CLASS ---

# Other models stay below Profile
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