from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from profiles.models import Profile
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST, require_http_methods
from django.db import transaction
from applications.models import Application
from .models import Stage, CandidateCard, SavedSearch
from jobs.models import Job
from django.core.serializers.json import DjangoJSONEncoder
import json

@login_required
def recruiter_dashboard(request):
    """Dashboard view for recruiters."""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        messages.error(request, 'Access denied. Recruiter account required.')
        return redirect('home.index')
    
    template_data = {'title': 'Recruiter Dashboard'}
    return render(request, 'recruiter/recruiter_dashboard.html', {'template_data': template_data})


def apply_candidate_filters(candidates, skills_query=None, location_query=None, projects_query=None, search_query=None):
    """Apply search filters to a candidate queryset. Used by both search and saved searches."""
    # Apply skills filter
    if skills_query:
        skill_terms = [term.strip() for term in skills_query.split(',') if term.strip()]
        skill_q = models.Q()
        for term in skill_terms:
            skill_q |= models.Q(skills__name__icontains=term) | models.Q(skills_text__icontains=term)
        candidates = candidates.filter(skill_q).distinct()
    
    # Apply location filter
    if location_query:
        candidates = candidates.filter(location__icontains=location_query)
    
    # Apply projects filter
    if projects_query:
        candidates = candidates.filter(
            models.Q(projects__title__icontains=projects_query) |
            models.Q(projects__description__icontains=projects_query) |
            models.Q(projects__technologies__icontains=projects_query) |
            models.Q(projects_text__icontains=projects_query)
        ).distinct()
    
    # Apply general search filter
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
    
    return candidates


def get_candidates_for_search(saved_search, limit=None):
    """Get matching candidates for a saved search using the same filtering as the main search."""
    candidates = Profile.objects.filter(
        user_type='regular'
    ).filter(
        models.Q(profile_visibility='public') | 
        models.Q(profile_visibility='recruiters')
    ).select_related('user').prefetch_related('skills', 'projects')
    
    # Apply the same filters as the main search view
    candidates = apply_candidate_filters(
        candidates,
        skills_query=saved_search.skills,
        location_query=saved_search.location,
        projects_query=saved_search.projects,
        search_query=saved_search.general_search
    )
    
    if limit:
        return candidates[:limit]
    return candidates


@login_required  
def candidate_search(request):
    """Search view for recruiters to find candidates."""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        messages.error(request, 'Access denied. Recruiter account required.')
        return redirect('home.index')
    
    # Get recruiter's saved searches with preview candidates
    saved_searches = SavedSearch.objects.filter(recruiter=request.user)
    
    # Attach preview candidates to each saved search
    saved_searches_with_previews = []
    for search in saved_searches:
        search.preview_candidates = get_candidates_for_search(search, limit=3)
        saved_searches_with_previews.append(search)
        
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
    
    # Apply filters using the shared function
    candidates = apply_candidate_filters(
        candidates,
        skills_query=skills_query,
        location_query=location_query,
        projects_query=projects_query,
        search_query=search_query
    )
    
    # Pagination
    paginator = Paginator(candidates, 10)  # Show 10 candidates per page
    page_number = request.GET.get('page')
    candidates_page = paginator.get_page(page_number)
    
    # Check if there are active filters
    has_filters = any([skills_query, location_query, projects_query, search_query])
    
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
        'saved_searches': saved_searches_with_previews,
        'has_filters': has_filters,
    }
    return render(request, 'recruiter/candidate_search.html', context)


@login_required
def kanban_board(request, job_id=None):
    """Render the kanban board for a recruiter's job. If no job_id provided, use first posted job."""
    # Basic recruiter check
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        messages.error(request, 'Access denied. Recruiter account required.')
        return redirect('home.index')

    # determine job
    if job_id:
        job = get_object_or_404(Job, id=job_id)
    else:
        job = request.user.posted_jobs.first()
        if not job:
            messages.info(request, 'You have no jobs posted. Create a job to manage applicants.')
            return redirect('jobs.create')

    if job.posted_by != request.user:
        messages.error(request, 'Access denied. You do not own this job.')
        return redirect('recruiter:dashboard')

    # Ensure stages exist for this job. If none, create sensible defaults.
    stages = list(Stage.objects.filter(job=job).order_by('order'))
    if not stages:
        default = ['Applied', 'Phone Screen', 'Interview', 'Offer', 'Hired']
        for idx, name in enumerate(default):
            Stage.objects.create(job=job, name=name, order=idx)
        stages = list(Stage.objects.filter(job=job).order_by('order'))

    # Ensure each application has a CandidateCard. If not, place by application.status mapping.
    apps = Application.objects.filter(job=job).select_related('applicant')
    # mapping from application.status to stage name heuristically
    status_map = {
        'applied': 'Applied',
        'review': 'Phone Screen',
        'interview': 'Interview',
        'offer': 'Offer',
        'closed': 'Hired',
    }

    stage_by_name = {s.name: s for s in stages}
    for app in apps:
        if not hasattr(app, 'kanban_card'):
            stage_name = status_map.get(app.status, 'Applied')
            stage = stage_by_name.get(stage_name, stages[0])
            # determine next order
            next_order = (CandidateCard.objects.filter(stage=stage).aggregate(models.Max('order'))['order__max'] or 0) + 1
            CandidateCard.objects.create(application=app, stage=stage, order=next_order)

    # Reload stages with cards
    stages = Stage.objects.filter(job=job).order_by('order').prefetch_related('cards__application__applicant')

    context = {
        'job': job,
        'stages': stages,
        'template_data': {'title': f'Pipeline — {job.title}'},
    }
    return render(request, 'recruiter/kanban_board.html', context)

@login_required
@require_POST
def move_card(request):
    """AJAX endpoint to move a card to another stage/order.

    Expects JSON: { card_id: int, to_stage: int, to_order: int }
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    card_id = payload.get('card_id')
    to_stage_id = payload.get('to_stage')
    to_order = payload.get('to_order')
    if card_id is None or to_stage_id is None or to_order is None:
        return JsonResponse({'error': 'Missing params'}, status=400)

    card = get_object_or_404(CandidateCard, id=card_id)
    stage = get_object_or_404(Stage, id=to_stage_id)

    # permission: recruiter must own the job
    if stage.job.posted_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # perform move and reorder atomically
    with transaction.atomic():
        # Shift down other cards in destination to make room
        CandidateCard.objects.filter(stage=stage, order__gte=to_order).update(order=models.F('order')+1)

        # Remove the card from its current stage slots
        old_stage = card.stage
        old_order = card.order
        card.stage = stage
        card.order = to_order
        card.save()

        # Close gap in old stage
        CandidateCard.objects.filter(stage=old_stage, order__gt=old_order).update(order=models.F('order')-1)

        # Optionally update the underlying application.status by heuristics
        name = stage.name.lower()
        app = card.application
        if 'appl' in name:
            app.status = 'applied'
        elif 'phone' in name or 'screen' in name:
            app.status = 'review'
        elif 'interview' in name:
            app.status = 'interview'
        elif 'offer' in name:
            app.status = 'offer'
        elif 'hire' in name or 'closed' in name:
            app.status = 'closed'
        app.save()

    return JsonResponse({'ok': True})


@login_required
@require_POST
def save_search(request):
    """Save current search criteria with a name."""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'error': 'Search name is required'}, status=400)
    
    # Get search criteria from POST
    skills = request.POST.get('skills', '')
    location = request.POST.get('location', '')
    projects = request.POST.get('projects', '')
    general_search = request.POST.get('search', '')
    
    # Check if at least one criteria is provided
    if not any([skills, location, projects, general_search]):
        return JsonResponse({'error': 'At least one search criteria is required'}, status=400)
    
    try:
        # Create or update saved search
        saved_search, created = SavedSearch.objects.update_or_create(
            recruiter=request.user,
            name=name,
            defaults={
                'skills': skills,
                'location': location,
                'projects': projects,
                'general_search': general_search,
            }
        )
        
        action = 'created' if created else 'updated'
        messages.success(request, f'Search "{name}" {action} successfully!')
        return JsonResponse({
            'success': True,
            'message': f'Search "{name}" {action} successfully!',
            'search_id': saved_search.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def apply_saved_search(request, search_id):
    """Apply a saved search by redirecting with its parameters."""
    saved_search = get_object_or_404(SavedSearch, id=search_id, recruiter=request.user)
    
    # Build query string from saved parameters
    params = saved_search.get_search_params()
    from urllib.parse import urlencode
    query_string = urlencode(params)
    
    messages.info(request, f'Applied saved search: {saved_search.name}')
    return redirect(f"{request.path.replace(f'/apply/{search_id}/', '')}?{query_string}")


@login_required
@require_http_methods(["DELETE", "POST"])
def delete_saved_search(request, search_id):
    """Delete a saved search."""
    saved_search = get_object_or_404(SavedSearch, id=search_id, recruiter=request.user)
    name = saved_search.name
    saved_search.delete()
    
    messages.success(request, f'Saved search "{name}" deleted successfully!')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f'Search "{name}" deleted'})
    
    return redirect('recruiter:candidate_search')

@login_required
def candidate_map(request):
    """Render the map view for recruiters."""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        messages.error(request, 'Access denied.')
        return redirect('home.index')
        
    context = {
        'template_data': {'title': 'Candidate Map'}
    }
    return render(request, 'recruiter/candidate_map.html', context)

@login_required
def candidate_map_data(request):
    """Return JSON data of candidate locations."""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        return JsonResponse({'error': 'Access denied'}, status=403)

    # Get candidates with valid coordinates
    candidates = Profile.objects.filter(
        user_type='regular',
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('user')

    # Optional: Filter by skills if query param exists
    skill_query = request.GET.get('skill')
    if skill_query:
        candidates = candidates.filter(skills_text__icontains=skill_query)

    data = []
    for profile in candidates:
        data.append({
            'id': profile.id,
            'name': profile.user.get_full_name() or profile.user.username,
            'headline': profile.headline,
            'lat': profile.latitude,
            'lng': profile.longitude,
            'url': f"/profiles/profile/{profile.id}/" # Hardcoded based on urls.py
        })

    return JsonResponse({'candidates': data}, encoder=DjangoJSONEncoder)

@login_required
def job_applicant_map(request, job_id):
    """Render the map view for a specific job's applicants."""
    # FIX: Changed 'user' to 'posted_by'
    job = get_object_or_404(Job, pk=job_id, posted_by=request.user)
    
    context = {
        'template_data': {'title': f'Map: {job.title}'},
        'job': job
    }
    return render(request, 'recruiter/job_applicant_map.html', context)

@login_required
def job_applicant_map_data(request, job_id):
    """Return JSON data of applicants for a specific job using an optimized query."""
    # 1. Get the job (Security check)
    job = get_object_or_404(Job, pk=job_id, posted_by=request.user)

    # 2. OPTIMIZED QUERY: Get Profiles directly
    applicants = Profile.objects.filter(
        user__job_applications__job=job,
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('user').distinct()

    # Debug print to server console
    print(f"Map Data for '{job.title}': Found {applicants.count()} valid profiles.")

    data = []
    for profile in applicants:
        # Get the specific application date for this job
        app = profile.user.job_applications.filter(job=job).first()
        
        # FIX: Changed 'created_at' to 'applied_at' to match your Application model
        applied_date = app.applied_at.strftime('%Y-%m-%d') if app else "Unknown"

        data.append({
            'id': profile.id,
            'name': profile.user.get_full_name() or profile.user.username,
            'headline': profile.headline,
            'lat': profile.latitude,
            'lng': profile.longitude,
            'url': f"/profiles/profile/{profile.id}/",
            'applied_at': applied_date
        })
    
    return JsonResponse({'applicants': data})