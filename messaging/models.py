from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class EmailMessage(models.Model):
    """Model to store email communications between recruiters and candidates."""
    
    MESSAGE_TYPE_CHOICES = [
        ('initial_contact', 'Initial Contact'),
        ('follow_up', 'Follow Up'),
        ('interview_invite', 'Interview Invitation'),
        ('job_offer', 'Job Offer'),
        ('general', 'General Inquiry'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('failed', 'Failed'),
    ]
    
    # Sender and recipient
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_emails')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_emails')
    
    # Email content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='general')
    
    # Email metadata
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    
    # Related job (optional)
    related_job = models.ForeignKey('jobs.Job', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Thread tracking
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Email Message'
        verbose_name_plural = 'Email Messages'
    
    def __str__(self):
        return f"Email from {self.sender.username} to {self.recipient.username}: {self.subject}"
    
    def mark_as_read(self):
        """Mark the email as read."""
        if not self.read_at:
            self.read_at = timezone.now()
            self.status = 'read'
            self.save()
    
    def mark_as_replied(self):
        """Mark the email as replied."""
        if not self.replied_at:
            self.replied_at = timezone.now()
            self.status = 'replied'
            self.save()
    
    @property
    def is_read(self):
        """Check if the email has been read."""
        return self.read_at is not None
    
    @property
    def is_replied(self):
        """Check if the email has been replied to."""
        return self.replied_at is not None
    
    @property
    def thread_messages(self):
        """Get all messages in the same thread."""
        if self.parent_message:
            return EmailMessage.objects.filter(
                models.Q(id=self.parent_message.id) | 
                models.Q(parent_message=self.parent_message) |
                models.Q(parent_message__parent_message=self.parent_message)
            ).order_by('sent_at')
        else:
            return EmailMessage.objects.filter(
                models.Q(id=self.id) | 
                models.Q(parent_message=self)
            ).order_by('sent_at')
