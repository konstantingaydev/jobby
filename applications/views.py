from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.db.models import Q
from jobs.models import Job
from .models import Application, ApplicationStatusHistory
from .forms import ApplicationForm, ApplicationFilterForm, ApplicationStatusUpdateForm
from profiles.models import Profile

@login_required
@require_POST
def apply_to_job(request, job_id):
    """One-click apply to a job with optional personalized note"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if user is a job seeker
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.user_type != 'regular':
            messages.error(request, "Only job seekers can apply to jobs.")
            return redirect('jobs:show', job_id=job.id)
    except Profile.DoesNotExist:
        messages.error(request, "Please complete your profile before applying to jobs.")
        return redirect('profiles:profile_edit')
    
    # Check if already applied (only active applications)
    existing_application = Application.get_active_application(request.user, job)
    if existing_application:
        messages.warning(request, f"You have already applied to this job. Status: {existing_application.get_status_display()}")
        return redirect('jobs.show', job_id=job.id)
    
    # Handle form submission
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.applicant = request.user
                application.job = job
                application.save()
                
                messages.success(request, f"Successfully applied to {job.title} at {job.company_name}!")
                return redirect('applications:my_applications')
            except IntegrityError:
                messages.error(request, "You have already applied to this job.")
                return redirect('jobs:show', job_id=job.id)
        else:
            messages.error(request, "There was an error with your application. Please try again.")
    
    return redirect('jobs:show', job_id=job.id)

@login_required
def quick_apply(request, job_id):
    """Quick apply without cover note"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if user is a job seeker
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.user_type != 'regular':
            return JsonResponse({'success': False, 'message': 'Only job seekers can apply to jobs.'})
    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Please complete your profile before applying.'})
    
    # Check if already applied (only active applications)
    if Application.has_active_application(request.user, job):
        return JsonResponse({'success': False, 'message': 'You have already applied to this job.'})
    
    try:
        application = Application.objects.create(
            applicant=request.user,
            job=job,
            cover_note=""
        )
        return JsonResponse({
            'success': True, 
            'message': f'Successfully applied to {job.title}!',
            'application_id': application.id
        })
    except IntegrityError:
        return JsonResponse({'success': False, 'message': 'You have already applied to this job.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})

@login_required
def apply_with_note(request, job_id):
    """Apply to job with personalized note"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if user is a job seeker
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.user_type != 'regular':
            messages.error(request, "Only job seekers can apply to jobs.")
            return redirect('jobs:show', job_id=job.id)
    except Profile.DoesNotExist:
        messages.error(request, "Please complete your profile before applying to jobs.")
        return redirect('profiles:profile_edit')
    
    # Check if already applied (only active applications)
    existing_application = Application.get_active_application(request.user, job)
    if existing_application:
        messages.warning(request, f"You have already applied to this job. Status: {existing_application.get_status_display()}")
        return redirect('jobs.show', job_id=job.id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.applicant = request.user
                application.job = job
                application.save()
                
                messages.success(request, f"Successfully applied to {job.title} at {job.company_name}!")
                return redirect('applications:my_applications')
            except IntegrityError:
                messages.error(request, "You have already applied to this job.")
                return redirect('jobs:show', job_id=job.id)
    else:
        form = ApplicationForm()
    
    context = {
        'job': job,
        'form': form,
    }
    return render(request, 'applications/apply_with_note.html', context)

@login_required
def my_applications(request):
    """View user's job applications with filtering and status tracking"""
    # Ensure user is a job seeker
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.user_type != 'regular':
            messages.error(request, "This page is only available to job seekers.")
            return redirect('home:index')
    except Profile.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('profiles:profile_edit')
    
    applications = Application.objects.filter(applicant=request.user).select_related('job')
    
    # Handle filtering
    filter_form = ApplicationFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data['status']:
            applications = applications.filter(status=filter_form.cleaned_data['status'])
        if filter_form.cleaned_data['date_from']:
            applications = applications.filter(applied_at__date__gte=filter_form.cleaned_data['date_from'])
        if filter_form.cleaned_data['date_to']:
            applications = applications.filter(applied_at__date__lte=filter_form.cleaned_data['date_to'])
        if filter_form.cleaned_data['company']:
            applications = applications.filter(job__company_name__icontains=filter_form.cleaned_data['company'])
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total': applications.count(),
        'applied': applications.filter(status='applied').count(),
        'review': applications.filter(status='review').count(),
        'interview': applications.filter(status='interview').count(),
        'offer': applications.filter(status='offer').count(),
        'closed': applications.filter(status='closed').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'stats': stats,
    }
    return render(request, 'applications/my_applications.html', context)

@login_required
def application_detail(request, application_id):
    """View detailed application information"""
    application = get_object_or_404(Application, id=application_id)
    
    # Check permissions
    if application.applicant != request.user and not (hasattr(request.user, 'profile') and request.user.profile.user_type in ['recruiter', 'admin']):
        messages.error(request, "You don't have permission to view this application.")
        return redirect('applications:my_applications')
    
    # Get status history
    status_history = application.status_history.all()
    
    context = {
        'application': application,
        'status_history': status_history,
    }
    return render(request, 'applications/application_detail.html', context)

@login_required
def withdraw_application(request, application_id):
    """Allow job seekers to withdraw their applications"""
    application = get_object_or_404(Application, id=application_id, applicant=request.user)
    
    if not application.can_withdraw():
        messages.error(request, "This application cannot be withdrawn at this stage.")
        return redirect('applications:my_applications')
    
    if request.method == 'POST':
        # Create status history entry
        ApplicationStatusHistory.objects.create(
            application=application,
            old_status=application.status,
            new_status='closed',
            changed_by=request.user,
            notes="Application withdrawn by applicant"
        )
        
        application.status = 'closed'
        application.save()
        
        messages.success(request, f"Successfully withdrew application for {application.job.title}")
        return redirect('applications:my_applications')
    
    context = {'application': application}
    return render(request, 'applications/withdraw_application.html', context)

# Recruiter views
@login_required
def recruiter_applications(request):
    """View applications for recruiter's job postings"""
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.user_type != 'recruiter':
            messages.error(request, "This page is only available to recruiters.")
            return redirect('home:index')
    except Profile.DoesNotExist:
        messages.error(request, "Access denied.")
        return redirect('home:index')
    
    # Get applications for jobs posted by this recruiter
    applications = Application.objects.filter(
        job__posted_by=request.user
    ).select_related('job', 'applicant').order_by('-applied_at')
    
    # Handle filtering
    filter_form = ApplicationFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data['status']:
            applications = applications.filter(status=filter_form.cleaned_data['status'])
        if filter_form.cleaned_data['date_from']:
            applications = applications.filter(applied_at__date__gte=filter_form.cleaned_data['date_from'])
        if filter_form.cleaned_data['date_to']:
            applications = applications.filter(applied_at__date__lte=filter_form.cleaned_data['date_to'])
    
    # Pagination
    paginator = Paginator(applications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
    }
    return render(request, 'applications/recruiter_applications.html', context)

@login_required
def update_application_status(request, application_id):
    """Allow recruiters to update application status"""
    application = get_object_or_404(Application, id=application_id)
    
    # Check if user is the recruiter who posted the job
    if application.job.posted_by != request.user:
        messages.error(request, "You don't have permission to update this application.")
        return redirect('applications:recruiter_applications')
    
    if request.method == 'POST':
        form = ApplicationStatusUpdateForm(request.POST, instance=application)
        if form.is_valid():
            old_status = application.status
            application = form.save()
            
            # Create status history entry if status changed
            if old_status != application.status:
                ApplicationStatusHistory.objects.create(
                    application=application,
                    old_status=old_status,
                    new_status=application.status,
                    changed_by=request.user,
                    notes=f"Status updated by recruiter"
                )
            
            # Mark as viewed by recruiter
            application.viewed_by_recruiter = True
            application.save()
            
            messages.success(request, f"Application status updated to {application.get_status_display()}")
            return redirect('applications:recruiter_applications')
    else:
        form = ApplicationStatusUpdateForm(instance=application)
    
    context = {
        'application': application,
        'form': form,
    }
    return render(request, 'applications/update_status.html', context)
