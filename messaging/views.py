from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import EmailMessage
from .forms import EmailCandidateForm, ReplyEmailForm, EmailSearchForm

@login_required
def send_email_to_candidate(request, candidate_id):
    """View for recruiters to send emails to candidates."""
    # Check if user is a recruiter
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        messages.error(request, 'Access denied. Recruiter account required.')
        return redirect('home.index')
    
    candidate = get_object_or_404(User, id=candidate_id)
    
    # Check if candidate has a profile and is a job seeker
    if not hasattr(candidate, 'profile') or candidate.profile.user_type != 'regular':
        messages.error(request, 'Invalid candidate.')
        return redirect('recruiter:candidate_search')
    
    if request.method == 'POST':
        form = EmailCandidateForm(request.POST, recruiter=request.user, candidate=candidate)
        if form.is_valid():
            email_message = form.save(commit=False)
            email_message.sender = request.user
            email_message.recipient = candidate
            email_message.save()
            
            # Send the actual email
            try:
                send_mail(
                    subject=email_message.subject,
                    message=email_message.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[candidate.email],
                    fail_silently=False,
                )
                messages.success(request, f'Email sent successfully to {candidate.get_full_name() or candidate.username}!')
                return redirect('messaging:email_sent', email_id=email_message.id)
            except Exception as e:
                email_message.status = 'failed'
                email_message.save()
                messages.error(request, f'Failed to send email: {str(e)}')
    else:
        form = EmailCandidateForm(recruiter=request.user, candidate=candidate)
    
    context = {
        'form': form,
        'candidate': candidate,
        'template_data': {'title': f'Send Email to {candidate.get_full_name() or candidate.username}'}
    }
    return render(request, 'messaging/send_email.html', context)

@login_required
def email_inbox(request):
    """View for users to see their email inbox."""
    search_form = EmailSearchForm(request.GET)
    
    # Get all emails for the current user
    emails = EmailMessage.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).select_related('sender', 'recipient', 'related_job').order_by('-sent_at')
    
    # Apply filters
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        message_type = search_form.cleaned_data.get('message_type')
        status = search_form.cleaned_data.get('status')
        message_filter = search_form.cleaned_data.get('message_filter')
        
        if search_query:
            emails = emails.filter(
                Q(subject__icontains=search_query) |
                Q(message__icontains=search_query) |
                Q(sender__username__icontains=search_query) |
                Q(recipient__username__icontains=search_query)
            )
        
        if message_type:
            emails = emails.filter(message_type=message_type)
        
        if status:
            emails = emails.filter(status=status)
        
        if message_filter:
            if message_filter == 'sent':
                emails = emails.filter(sender=request.user)
            elif message_filter == 'received':
                emails = emails.filter(recipient=request.user)
            elif message_filter == 'unread':
                emails = emails.filter(recipient=request.user, read_at__isnull=True)
    
    # Pagination
    paginator = Paginator(emails, 20)
    page_number = request.GET.get('page')
    emails_page = paginator.get_page(page_number)
    
    context = {
        'emails': emails_page,
        'search_form': search_form,
        'template_data': {'title': 'Email Inbox'}
    }
    return render(request, 'messaging/inbox.html', context)

@login_required
def email_detail(request, email_id):
    """View to display email details and allow replies."""
    email = get_object_or_404(EmailMessage, id=email_id)
    
    # Check if user has access to this email
    if email.sender != request.user and email.recipient != request.user:
        messages.error(request, 'Access denied.')
        return redirect('messaging:inbox')
    
    # Mark as read if user is the recipient
    if email.recipient == request.user and not email.is_read:
        email.mark_as_read()
    
    # Handle reply
    if request.method == 'POST':
        reply_form = ReplyEmailForm(request.POST, parent_message=email)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.sender = request.user
            reply.recipient = email.sender if request.user == email.recipient else email.recipient
            reply.subject = f"Re: {email.subject}"
            reply.parent_message = email
            reply.save()
            
            # Send the reply email
            try:
                send_mail(
                    subject=reply.subject,
                    message=reply.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reply.recipient.email],
                    fail_silently=False,
                )
                email.mark_as_replied()
                messages.success(request, 'Reply sent successfully!')
                return redirect('messaging:email_detail', email_id=email.id)
            except Exception as e:
                reply.status = 'failed'
                reply.save()
                messages.error(request, f'Failed to send reply: {str(e)}')
    else:
        reply_form = ReplyEmailForm(parent_message=email)
    
    # Get thread messages
    thread_messages = email.thread_messages
    
    context = {
        'email': email,
        'reply_form': reply_form,
        'thread_messages': thread_messages,
        'template_data': {'title': email.subject}
    }
    return render(request, 'messaging/email_detail.html', context)

@login_required
def email_sent(request, email_id):
    """View to show confirmation of sent email."""
    email = get_object_or_404(EmailMessage, id=email_id, sender=request.user)
    
    context = {
        'email': email,
        'template_data': {'title': 'Email Sent'}
    }
    return render(request, 'messaging/email_sent.html', context)

@login_required
def mark_email_read(request, email_id):
    """AJAX view to mark email as read."""
    if request.method == 'POST':
        email = get_object_or_404(EmailMessage, id=email_id, recipient=request.user)
        email.mark_as_read()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
