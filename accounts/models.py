from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
    USER_TYPE_CHOICES = (
        ('recruiter', 'Recruiter'),
        ('regular', 'Job Seeker'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='regular')
    # Candidate-specific fields (optional; used when user_type == 'regular')
    skills = models.TextField(blank=True, default='', help_text='Comma-separated list of skills')
    location = models.CharField(max_length=255, blank=True, default='', help_text='Candidate location')
    projects = models.TextField(blank=True, default='', help_text='Short description/list of projects')
    def __str__(self):
        return f'{self.user.username} Profile - {self.get_user_type_display()}'