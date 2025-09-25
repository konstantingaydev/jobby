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
    def __str__(self):
        return f'{self.user.username} Profile - {self.get_user_type_display()}'