from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from profiles.models import Profile

@login_required
def recruiter_dashboard(request):
    """Dashboard view for recruiters."""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        messages.error(request, 'Access denied. Recruiter account required.')
        return redirect('home.index')
    
    template_data = {'title': 'Recruiter Dashboard'}
    return render(request, 'recruiter/dashboard.html', {'template_data': template_data})


@login_required  
def candidate_search(request):
    """Search view for recruiters to find candidates."""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        messages.error(request, 'Access denied. Recruiter account required.')
        return redirect('home.index')
        
    # Get all job seeker profiles that are visible to recruiters
    candidates = Profile.objects.filter(
        user_type='regular'
    ).filter(
        models.Q(profile_visibility='public') | 
        models.Q(profile_visibility='recruiters')
    ).select_related('user').prefetch_related('skills', 'projects')
    
    # Get search parameters
    skills_query = request.GET.get('skills', '')
    location_query = request.GET.get('location', '')
    projects_query = request.GET.get('projects', '')
    search_query = request.GET.get('search', '')  # Keep for general search
    
    # Apply filters
    if skills_query:
        # Search in both the skills model and the legacy skills_text field
        skill_terms = [term.strip() for term in skills_query.split(',') if term.strip()]
        skill_q = models.Q()
        for term in skill_terms:
            skill_q |= models.Q(skills__name__icontains=term) | models.Q(skills_text__icontains=term)
        candidates = candidates.filter(skill_q).distinct()
    
    if location_query:
        candidates = candidates.filter(location__icontains=location_query)
    
    if projects_query:
        # Search in both the projects model and the legacy projects_text field
        candidates = candidates.filter(
            models.Q(projects__title__icontains=projects_query) |
            models.Q(projects__description__icontains=projects_query) |
            models.Q(projects__technologies__icontains=projects_query) |
            models.Q(projects_text__icontains=projects_query)
        ).distinct()
    
    # Filter by general search query if provided
    if search_query:
        candidates = candidates.filter(
            models.Q(skills__name__icontains=search_query) |
            models.Q(skills_text__icontains=search_query) |
            models.Q(location__icontains=search_query) |
            models.Q(projects__title__icontains=search_query) |
            models.Q(projects__description__icontains=search_query) |
            models.Q(projects_text__icontains=search_query) |
            models.Q(user__first_name__icontains=search_query) |
            models.Q(user__last_name__icontains=search_query) |
            models.Q(headline__icontains=search_query) |
            models.Q(bio__icontains=search_query)
        ).distinct()
    
    # Pagination
    paginator = Paginator(candidates, 10)  # Show 10 candidates per page
    page_number = request.GET.get('page')
    candidates_page = paginator.get_page(page_number)
    
    # Structure data as expected by template
    template_data = {
        'title': 'Search Candidates',
        'results': candidates_page,
        'search_terms': {
            'skills': skills_query,
            'location': location_query,
            'projects': projects_query,
        }
    }
    
    context = {
        'template_data': template_data,
        'candidates': candidates_page,  # Keep for backward compatibility
        'search_query': search_query,   # Keep for backward compatibility
    }
    return render(request, 'recruiter/candidate_search.html', context)
