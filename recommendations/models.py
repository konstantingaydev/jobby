from django.db import models
from django.contrib.auth.models import User
from jobs.models import Job
from profiles.models import Profile


class CandidateRecommendation(models.Model):
    """Model to store candidate recommendations for job postings."""
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='recommendations')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_recommendations')
    candidate_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='recommendations')
    
    # Recommendation scoring
    match_score = models.FloatField(default=0.0, help_text="Overall match score (0-100)")
    skills_match_score = models.FloatField(default=0.0, help_text="Skills match percentage")
    experience_match_score = models.FloatField(default=0.0, help_text="Experience level match")
    location_match_score = models.FloatField(default=0.0, help_text="Location match score")
    
    # Recommendation metadata
    recommended_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Recruiter interaction
    viewed_by_recruiter = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    is_favorite = models.BooleanField(default=False, help_text="Marked as favorite by recruiter")
    recruiter_notes = models.TextField(blank=True, help_text="Recruiter's notes about this candidate")
    
    # Status tracking
    STATUS_CHOICES = [
        ('new', 'New Recommendation'),
        ('viewed', 'Viewed'),
        ('contacted', 'Contacted'),
        ('applied', 'Applied'),
        ('dismissed', 'Dismissed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    class Meta:
        ordering = ['-match_score', '-recommended_at']
        unique_together = ['job', 'candidate']
        indexes = [
            models.Index(fields=['job', '-match_score']),
            models.Index(fields=['job', 'status']),
        ]
    
    def __str__(self):
        return f"{self.candidate.username} recommended for {self.job.title} (Score: {self.match_score:.1f}%)"
    
    def mark_as_viewed(self):
        """Mark this recommendation as viewed by the recruiter."""
        from django.utils import timezone
        self.viewed_by_recruiter = True
        self.viewed_at = timezone.now()
        if self.status == 'new':
            self.status = 'viewed'
        self.save()
    
    @property
    def match_percentage(self):
        """Return match score as percentage."""
        return f"{self.match_score:.1f}%"
    
    @property
    def days_since_recommended(self):
        """Calculate days since recommendation was created."""
        from django.utils import timezone
        return (timezone.now() - self.recommended_at).days
