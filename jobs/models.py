from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import urllib.request
import urllib.parse
import json

class Job(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
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
    # Optional geographic coordinates (populated later via geocoding)
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude of job location")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude of job location")
    salary_min = models.IntegerField(null=True, blank=True, help_text="Minimum salary")
    salary_max = models.IntegerField(null=True, blank=True, help_text="Maximum salary")
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full-time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='entry')
    description = models.TextField(help_text="Job description and requirements", default="")
    requirements = models.TextField(help_text="Required skills and qualifications", default="")
    benefits = models.TextField(blank=True, help_text="Benefits and perks")
    image = models.ImageField(upload_to='job_images/', null=True, blank=True)
    
    # Enhanced search fields
    skills_required = models.TextField(blank=True, help_text="Required skills (comma-separated)")
    is_remote = models.BooleanField(default=False, help_text="Is this a remote position?")
    visa_sponsorship = models.BooleanField(default=False, help_text="Does this job offer visa sponsorship?")
    
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
    
    @property
    def skills_list(self):
        """Return skills as a list"""
        if self.skills_required:
            return [skill.strip() for skill in self.skills_required.split(',') if skill.strip()]
        return []

    def _geocode_location(self, location):
        """Try to geocode a free-text location using Nominatim.

        Returns (lat, lon) or None on failure. This is best-effort and
        failures are silently ignored to avoid blocking saves.
        """
        if not location:
            return None
        try:
            base = 'https://nominatim.openstreetmap.org/search?format=json&limit=1&q='
            url = base + urllib.parse.quote(location)
            req = urllib.request.Request(url, headers={'User-Agent': 'Jobby/1.0 (admin@jobby.example)'} )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read().decode('utf-8')
                arr = json.loads(data)
                if arr:
                    return float(arr[0]['lat']), float(arr[0]['lon'])
        except Exception:
            # Network errors, rate-limiting, or parsing issues are ignored.
            return None
        return None

    def save(self, *args, **kwargs):
        """Override save to attempt geocoding when location changes or coords are missing."""
        try:
            old_location = None
            if self.pk:
                try:
                    old_location = Job.objects.values_list('location', flat=True).get(pk=self.pk)
                except Job.DoesNotExist:
                    old_location = None

            need_geocode = False
            if not self.pk:
                # new object
                need_geocode = True
            else:
                if (self.latitude is None or self.longitude is None):
                    need_geocode = True
                if old_location is not None and old_location != (self.location or ''):
                    need_geocode = True

            if need_geocode and (self.location or '').strip():
                coords = self._geocode_location(self.location)
                if coords:
                    self.latitude, self.longitude = coords
        except Exception:
            # Ensure save proceeds even if geocoding fails
            pass

        super().save(*args, **kwargs)