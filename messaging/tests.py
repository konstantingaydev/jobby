from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from .models import EmailMessage

class EmailMessagingTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.recruiter = User.objects.create_user(
            username='recruiter',
            email='recruiter@test.com',
            password='testpass123'
        )
        self.candidate = User.objects.create_user(
            username='candidate',
            email='candidate@test.com',
            password='testpass123'
        )
        
        # Create profiles
        from profiles.models import Profile
        Profile.objects.create(user=self.recruiter, user_type='recruiter')
        Profile.objects.create(user=self.candidate, user_type='regular')
        
        self.client = Client()
    
    def test_send_email_to_candidate(self):
        """Test that recruiters can send emails to candidates."""
        # Login as recruiter
        self.client.login(username='recruiter', password='testpass123')
        
        # Send email to candidate
        response = self.client.post(
            reverse('messaging:send_email', args=[self.candidate.id]),
            {
                'subject': 'Test Job Opportunity',
                'message': 'We have an exciting opportunity for you!',
                'message_type': 'initial_contact'
            }
        )
        
        # Check if email was created
        self.assertEqual(EmailMessage.objects.count(), 1)
        email = EmailMessage.objects.first()
        self.assertEqual(email.sender, self.recruiter)
        self.assertEqual(email.recipient, self.candidate)
        self.assertEqual(email.subject, 'Test Job Opportunity')
        
        # Check if email was sent (in development, it goes to console)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Job Opportunity')
        self.assertEqual(mail.outbox[0].to, ['candidate@test.com'])
    
    def test_email_inbox_access(self):
        """Test that users can access their email inbox."""
        # Login as recruiter
        self.client.login(username='recruiter', password='testpass123')
        
        # Create a test email
        EmailMessage.objects.create(
            sender=self.recruiter,
            recipient=self.candidate,
            subject='Test Email',
            message='Test message'
        )
        
        # Access inbox
        response = self.client.get(reverse('messaging:inbox'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Email')
    
    def test_candidate_cannot_send_email_to_recruiter(self):
        """Test that candidates cannot access the send email functionality."""
        # Login as candidate
        self.client.login(username='candidate', password='testpass123')
        
        # Try to send email (should redirect)
        response = self.client.get(
            reverse('messaging:send_email', args=[self.recruiter.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirected
    
    def test_email_thread_functionality(self):
        """Test email thread and reply functionality."""
        # Create initial email
        initial_email = EmailMessage.objects.create(
            sender=self.recruiter,
            recipient=self.candidate,
            subject='Initial Contact',
            message='Hello, I have a job opportunity for you.'
        )
        
        # Login as candidate and reply
        self.client.login(username='candidate', password='testpass123')
        
        response = self.client.post(
            reverse('messaging:email_detail', args=[initial_email.id]),
            {
                'message': 'Thank you for reaching out! I am interested.'
            }
        )
        
        # Check if reply was created
        self.assertEqual(EmailMessage.objects.count(), 2)
        reply = EmailMessage.objects.filter(parent_message=initial_email).first()
        self.assertIsNotNone(reply)
        self.assertEqual(reply.sender, self.candidate)
        self.assertEqual(reply.recipient, self.recruiter)
        self.assertTrue(reply.subject.startswith('Re: '))