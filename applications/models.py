from django.db import models
from django.contrib.auth.models import User
from jobs.models import Job
from django.utils import timezone

class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('review', 'Under Review'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('closed', 'Closed'),
    ]
    
    # Core relationships
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    
    # Application details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    cover_note = models.TextField(blank=True, help_text="Personalized note from the applicant")
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional tracking fields
    viewed_by_recruiter = models.BooleanField(default=False)
    recruiter_notes = models.TextField(blank=True, help_text="Internal notes from recruiter")
    
    class Meta:
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title} at {self.job.company_name} ({self.get_status_display()})"
    
    @property
    def status_display(self):
        return self.get_status_display()
    
    @property
    def days_since_applied(self):
        """Calculate days since application was submitted"""
        return (timezone.now() - self.applied_at).days
    
    def can_withdraw(self):
        """Check if application can be withdrawn by applicant"""
        return self.status in ['applied', 'review']
    
    def get_status_color(self):
        """Return CSS class for status color coding"""
        status_colors = {
            'applied': 'text-primary',
            'review': 'text-warning',
            'interview': 'text-info',
            'offer': 'text-success',
            'closed': 'text-secondary',
        }
        return status_colors.get(self.status, 'text-secondary')
    
    @classmethod
    def get_active_application(cls, user, job):
        """Get active application for a user and job (excludes closed applications)"""
        return cls.objects.filter(
            applicant=user, 
            job=job
        ).exclude(status='closed').first()
    
    @classmethod
    def has_active_application(cls, user, job):
        """Check if user has an active application for this job"""
        return cls.get_active_application(user, job) is not None

class ApplicationStatusHistory(models.Model):
    """Track status changes for applications"""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = "Application status histories"
    
    def __str__(self):
        return f"{self.application} - {self.old_status} → {self.new_status}"
