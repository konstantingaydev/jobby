from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden

from .models import Job
from .forms import JobForm
from accounts.models import Profile

def index(request):
    """Display all job postings with filtering capabilities"""
    jobs = Job.objects.filter(is_active=True)
    
    # Get filter parameters
    search_term = request.GET.get('search', '')
    employment_type = request.GET.get('employment_type', '')
    experience_level = request.GET.get('experience_level', '')
    
    # Apply search filter
    if search_term:
        jobs = jobs.filter(
            Q(title__icontains=search_term) |
            Q(company_name__icontains=search_term) |
            Q(description__icontains=search_term)
        )
    
    # Apply employment type filter
    if employment_type:
        jobs = jobs.filter(employment_type=employment_type)
    
    # Apply experience level filter
    if experience_level:
        jobs = jobs.filter(experience_level=experience_level)
    
    # Order by most recent
    jobs = jobs.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(jobs, 9)  # 9 jobs per page (3x3 grid)
    page_number = request.GET.get('page')
    jobs_page = paginator.get_page(page_number)
    
    # Structure data as expected by template
    template_data = {
        'jobs': jobs_page,
        'current_search': search_term,
        'current_employment_type': employment_type,
        'current_experience_level': experience_level,
        'employment_types': Job.EMPLOYMENT_TYPE_CHOICES,
        'experience_levels': Job.EXPERIENCE_LEVEL_CHOICES,
    }
    
    context = {
        'template_data': template_data
    }
    
    return render(request, 'jobs/index.html', context)

def show(request, id):
    job = get_object_or_404(Job, id=id, is_active=True)
    template_data = {
        'title': job.title,
        'job': job
    }
    return render(request, 'jobs/show.html', {'template_data': template_data})

@login_required
def my_jobs(request):
    """View for recruiters to see their posted jobs"""
    try:
        profile = request.user.profile
        if profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can access this page.')
            return redirect('jobs.index')
    except Profile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')
    
    jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
    
    template_data = {
        'title': 'My Job Postings',
        'jobs': jobs
    }
    return render(request, 'jobs/my_jobs.html', {'template_data': template_data})

@login_required
def create_job(request):
    """View for recruiters to create new job postings"""
    try:
        profile = request.user.profile
        if profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can post jobs.')
            return redirect('jobs.index')
    except Profile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, f'Job "{job.title}" has been posted successfully!')
            return redirect('jobs.my_jobs')
    else:
        form = JobForm()
    
    template_data = {
        'title': 'Post a New Job',
        'form': form
    }
    return render(request, 'jobs/create_job.html', {'template_data': template_data})

@login_required
def edit_job(request, id):
    """View for recruiters to edit their job postings"""
    job = get_object_or_404(Job, id=id, posted_by=request.user)
    
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f'Job "{job.title}" has been updated successfully!')
            return redirect('jobs.my_jobs')
    else:
        form = JobForm(instance=job)
    
    template_data = {
        'title': f'Edit Job: {job.title}',
        'form': form,
        'job': job
    }
    return render(request, 'jobs/edit_job.html', {'template_data': template_data})

@login_required
def delete_job(request, id):
    """View for recruiters to delete their job postings"""
    job = get_object_or_404(Job, id=id, posted_by=request.user)
    
    if request.method == 'POST':
        job_title = job.title
        job.delete()
        messages.success(request, f'Job "{job_title}" has been deleted successfully!')
        return redirect('jobs.my_jobs')
    
    template_data = {
        'title': f'Delete Job: {job.title}',
        'job': job
    }
    return render(request, 'jobs/delete_job.html', {'template_data': template_data})