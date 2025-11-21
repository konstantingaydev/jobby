from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from jobs.models import Job
from .models import CandidateRecommendation
from .utils import generate_recommendations_for_job, refresh_recommendations_for_job


@login_required
def job_recommendations(request, job_id):
    """View to show candidate recommendations for a specific job."""
    # Check if user is a recruiter
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        messages.error(request, 'Access denied. Recruiter account required.')
        return redirect('home.index')
    
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    # Get recommendations for this job
    recommendations = CandidateRecommendation.objects.filter(
        job=job
    ).select_related('candidate', 'candidate_profile').order_by('-match_score', '-recommended_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        recommendations = recommendations.filter(status=status_filter)
    
    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        recommendations = recommendations.filter(
            Q(candidate__username__icontains=search_query) |
            Q(candidate__first_name__icontains=search_query) |
            Q(candidate__last_name__icontains=search_query) |
            Q(candidate_profile__headline__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(recommendations, 10)
    page_number = request.GET.get('page')
    recommendations_page = paginator.get_page(page_number)
    
    context = {
        'job': job,
        'recommendations': recommendations_page,
        'status_filter': status_filter,
        'search_query': search_query,
        'template_data': {'title': f'Candidate Recommendations - {job.title}'}
    }
    return render(request, 'recommendations/job_recommendations.html', context)


@login_required
def all_recommendations(request):
    """View to show all candidate recommendations across all jobs for the recruiter."""
    # Check if user is a recruiter
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        messages.error(request, 'Access denied. Recruiter account required.')
        return redirect('home.index')
    
    # Get all recommendations for jobs posted by this recruiter
    recommendations = CandidateRecommendation.objects.filter(
        job__posted_by=request.user
    ).select_related('job', 'candidate', 'candidate_profile').order_by('-match_score', '-recommended_at')
    
    # Filter by job if provided
    job_filter = request.GET.get('job', '')
    if job_filter:
        recommendations = recommendations.filter(job_id=job_filter)
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        recommendations = recommendations.filter(status=status_filter)
    
    # Show only unviewed
    unviewed_only = request.GET.get('unviewed', '')
    if unviewed_only:
        recommendations = recommendations.filter(viewed_by_recruiter=False)
    
    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        recommendations = recommendations.filter(
            Q(candidate__username__icontains=search_query) |
            Q(candidate__first_name__icontains=search_query) |
            Q(candidate__last_name__icontains=search_query) |
            Q(candidate_profile__headline__icontains=search_query) |
            Q(job__title__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(recommendations, 15)
    page_number = request.GET.get('page')
    recommendations_page = paginator.get_page(page_number)
    
    # Get all jobs for filter dropdown
    jobs = Job.objects.filter(posted_by=request.user, is_active=True).order_by('-created_at')
    
    context = {
        'recommendations': recommendations_page,
        'jobs': jobs,
        'job_filter': job_filter,
        'status_filter': status_filter,
        'unviewed_only': unviewed_only,
        'search_query': search_query,
        'template_data': {'title': 'Candidate Recommendations'}
    }
    return render(request, 'recommendations/all_recommendations.html', context)


@login_required
@require_POST
def refresh_recommendations(request, job_id):
    """Refresh recommendations for a specific job."""
    # Check if user is a recruiter
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    try:
        recommendations = refresh_recommendations_for_job(job)
        messages.success(request, f'Generated {len(recommendations)} new candidate recommendations!')
        return redirect('recommendations:job_recommendations', job_id=job_id)
    except Exception as e:
        messages.error(request, f'Failed to refresh recommendations: {str(e)}')
        return redirect('recommendations:job_recommendations', job_id=job_id)


@login_required
@require_POST
def mark_recommendation_viewed(request, recommendation_id):
    """Mark a recommendation as viewed."""
    # Check if user is a recruiter
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    recommendation = get_object_or_404(
        CandidateRecommendation,
        id=recommendation_id,
        job__posted_by=request.user
    )
    
    recommendation.mark_as_viewed()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('recommendations:job_recommendations', job_id=recommendation.job.id)


@login_required
@require_POST
def update_recommendation_status(request, recommendation_id):
    """Update the status of a recommendation."""
    # Check if user is a recruiter
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    recommendation = get_object_or_404(
        CandidateRecommendation,
        id=recommendation_id,
        job__posted_by=request.user
    )
    
    new_status = request.POST.get('status')
    if new_status in dict(CandidateRecommendation.STATUS_CHOICES).keys():
        recommendation.status = new_status
        if new_status == 'viewed' and not recommendation.viewed_by_recruiter:
            recommendation.mark_as_viewed()
        recommendation.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'new_status': new_status})
        
        messages.success(request, 'Recommendation status updated.')
    
    return redirect('recommendations:job_recommendations', job_id=recommendation.job.id)


@login_required
@require_POST
def toggle_favorite(request, recommendation_id):
    """Toggle favorite status of a recommendation."""
    # Check if user is a recruiter
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    recommendation = get_object_or_404(
        CandidateRecommendation,
        id=recommendation_id,
        job__posted_by=request.user
    )
    
    recommendation.is_favorite = not recommendation.is_favorite
    recommendation.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_favorite': recommendation.is_favorite
        })
    
    messages.success(request, 'Favorite status updated.')
    return redirect('recommendations:job_recommendations', job_id=recommendation.job.id)
