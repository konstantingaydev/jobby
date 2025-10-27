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
from django.db import transaction
from .models import EmailMessage, Conversation, InternalMessage, MessageNotification
from .forms import EmailCandidateForm, ReplyEmailForm, EmailSearchForm, InternalMessageForm, ConversationSearchForm, StartConversationForm

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
    
    # Check if candidate has an email address
    if not candidate.email:
        messages.error(request, f'{candidate.get_full_name() or candidate.username} does not have an email address on file. Please use the messaging system instead.')
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

# Internal Messaging Views

@login_required
def internal_messages(request):
    """View for internal messaging inbox."""
    search_form = ConversationSearchForm(request.GET)
    
    # Get conversations for the current user (only active ones)
    conversations = Conversation.objects.filter(
        participants=request.user,
        is_active=True
    ).prefetch_related('participants', 'messages').order_by('-updated_at')
    
    # Apply search filters
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        message_type = search_form.cleaned_data.get('message_type')
        unread_only = search_form.cleaned_data.get('unread_only')
        
        if search_query:
            conversations = conversations.filter(
                Q(participants__username__icontains=search_query) |
                Q(participants__first_name__icontains=search_query) |
                Q(participants__last_name__icontains=search_query) |
                Q(messages__content__icontains=search_query)
            ).distinct()
        
        if message_type:
            conversations = conversations.filter(
                messages__message_type=message_type
            ).distinct()
        
        if unread_only:
            # Get conversations with unread messages for the current user
            unread_conversation_ids = InternalMessage.objects.filter(
                recipient=request.user,
                read_at__isnull=True,
                is_deleted=False
            ).values_list('conversation_id', flat=True).distinct()
            conversations = conversations.filter(id__in=unread_conversation_ids)
    
    # Add unread counts and latest messages
    conversation_list = []
    for conversation in conversations:
        conversation.unread_count = conversation.get_unread_count(request.user)
        conversation.latest_message = conversation.get_latest_message()
        conversation.other_participant = conversation.get_other_participant(request.user)
        # Only include conversations that have messages
        if conversation.latest_message:
            conversation_list.append(conversation)
    
    context = {
        'conversations': conversation_list,
        'search_form': search_form,
        'template_data': {'title': 'Messages'}
    }
    return render(request, 'messaging/internal_messages.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """View for a specific conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user, is_active=True)
    other_participant = conversation.get_other_participant(request.user)
    
    # Mark all messages in this conversation as read
    InternalMessage.objects.filter(
        conversation=conversation,
        recipient=request.user,
        read_at__isnull=True
    ).update(read_at=timezone.now())
    
    # Get messages for this conversation
    conversation_messages = conversation.messages.filter(is_deleted=False).order_by('created_at')
    
    # Handle new message
    if request.method == 'POST':
        form = InternalMessageForm(request.POST, sender=request.user, recipient=other_participant)
        if form.is_valid():
            try:
                with transaction.atomic():
                    message = form.save(commit=False)
                    message.conversation = conversation
                    message.sender = request.user
                    message.recipient = other_participant
                    message.save()
                    
                    # Update conversation timestamp
                    conversation.updated_at = timezone.now()
                    conversation.save()
                    
                    # Create notification for recipient
                    MessageNotification.objects.create(
                        user=other_participant,
                        message=message
                    )
                
                messages.success(request, 'Message sent successfully!')
                return redirect('messaging:conversation_detail', conversation_id=conversation.id)
            except Exception as e:
                messages.error(request, f'Failed to send message: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InternalMessageForm(sender=request.user, recipient=other_participant)
    
    context = {
        'conversation': conversation,
        'other_participant': other_participant,
        'messages': conversation_messages,
        'form': form,
        'template_data': {'title': f'Conversation with {other_participant.get_full_name() or other_participant.username}'}
    }
    return render(request, 'messaging/conversation_detail.html', context)

@login_required
def start_conversation(request, user_id=None):
    """View for starting a new conversation."""
    if user_id:
        recipient = get_object_or_404(User, id=user_id)
        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            participants__in=[request.user, recipient],
            is_active=True
        ).filter(participants=request.user).filter(participants=recipient).first()
        
        if existing_conversation:
            return redirect('messaging:conversation_detail', conversation_id=existing_conversation.id)
    else:
        recipient = None
    
    if request.method == 'POST':
        form = StartConversationForm(request.POST, sender=request.user)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            initial_message = form.cleaned_data['initial_message']
            message_type = form.cleaned_data['message_type']
            related_job = form.cleaned_data.get('related_job')
            
            # Check if conversation already exists
            existing_conversation = Conversation.objects.filter(
                participants__in=[request.user, recipient],
                is_active=True
            ).filter(participants=request.user).filter(participants=recipient).first()
            
            if existing_conversation:
                conversation = existing_conversation
            else:
                # Create new conversation
                conversation = Conversation.objects.create(
                    related_job=related_job,
                    is_active=True
                )
                conversation.participants.add(request.user, recipient)
            
            # Create initial message
            with transaction.atomic():
                message = InternalMessage.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    recipient=recipient,
                    content=initial_message,
                    message_type=message_type,
                    attachment_url=form.cleaned_data.get('attachment_url', ''),
                    attachment_name=form.cleaned_data.get('attachment_name', '')
                )
                
                # Create notification
                MessageNotification.objects.create(
                    user=recipient,
                    message=message
                )
            
            messages.success(request, f'Conversation started with {recipient.get_full_name() or recipient.username}!')
            return redirect('messaging:conversation_detail', conversation_id=conversation.id)
    else:
        form = StartConversationForm(sender=request.user)
        if recipient:
            form.fields['recipient'].initial = recipient
    
    context = {
        'form': form,
        'recipient': recipient,
        'template_data': {'title': 'Start New Conversation'}
    }
    return render(request, 'messaging/start_conversation.html', context)

@login_required
def mark_message_read(request, message_id):
    """AJAX view to mark a message as read."""
    if request.method == 'POST':
        message = get_object_or_404(InternalMessage, id=message_id, recipient=request.user)
        message.mark_as_read()
        
        # Mark notification as read
        MessageNotification.objects.filter(
            user=request.user,
            message=message
        ).update(is_read=True)
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_unread_count(request):
    """AJAX view to get unread message count."""
    unread_count = MessageNotification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'unread_count': unread_count})

@login_required
def delete_conversation(request, conversation_id):
    """View to delete/deactivate a conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user, is_active=True)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Mark conversation as inactive
                conversation.is_active = False
                conversation.save()
                
                # Mark all messages in this conversation as deleted for this user
                InternalMessage.objects.filter(
                    Q(conversation=conversation) & (Q(sender=request.user) | Q(recipient=request.user))
                ).update(is_deleted=True)
                
                # Mark all notifications as read for this user
                MessageNotification.objects.filter(
                    user=request.user,
                    message__conversation=conversation
                ).update(is_read=True)
            
            messages.success(request, 'Conversation deleted successfully.')
        except Exception as e:
            messages.error(request, f'Failed to delete conversation: {str(e)}')
        
        return redirect('messaging:internal_messages')
    
    context = {
        'conversation': conversation,
        'template_data': {'title': 'Delete Conversation'}
    }
    return render(request, 'messaging/delete_conversation.html', context)
