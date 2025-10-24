from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

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

class Conversation(models.Model):
    """Model to represent a conversation between two users."""
    
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Optional: Link to a specific job
    related_job = models.ForeignKey('jobs.Job', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        participant_names = [p.get_full_name() or p.username for p in self.participants.all()]
        return f"Conversation between {', '.join(participant_names)}"
    
    def get_other_participant(self, user):
        """Get the other participant in the conversation."""
        return self.participants.exclude(id=user.id).first()
    
    def get_latest_message(self):
        """Get the latest message in the conversation."""
        return self.messages.order_by('-created_at').first()
    
    def get_unread_count(self, user):
        """Get the number of unread messages for a user."""
        return self.messages.filter(
            sender__in=self.participants.exclude(id=user.id),
            read_at__isnull=True
        ).count()

class InternalMessage(models.Model):
    """Model to store internal platform messages between users."""
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text Message'),
        ('job_invite', 'Job Invitation'),
        ('interview_request', 'Interview Request'),
        ('offer', 'Job Offer'),
        ('follow_up', 'Follow Up'),
        ('general', 'General Message'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    
    # Message content
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    
    # Message metadata
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    # Optional attachments or links
    attachment_url = models.URLField(blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}: {self.content[:50]}..."
    
    def mark_as_read(self):
        """Mark the message as read."""
        if not self.read_at:
            self.read_at = timezone.now()
            self.save()
    
    @property
    def is_read(self):
        """Check if the message has been read."""
        return self.read_at is not None
    
    @property
    def time_since_sent(self):
        """Get human-readable time since message was sent."""
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"

class MessageNotification(models.Model):
    """Model to track message notifications for users."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_notifications')
    message = models.ForeignKey(InternalMessage, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'message']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message.content[:30]}..."
