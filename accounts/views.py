from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from .forms import ProfileForm

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username = request.POST['username'], password = request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            user.profile.user_type = form.cleaned_data.get('user_type')
            user.profile.save()
            
            auth_login(request, user)
            return redirect('home.index') # Redirect to home
    else:
        form = CustomUserCreationForm()

    context = {
        'title': 'Sign Up',
        'form': form
    }
    return render(request, 'accounts/signup.html', context)


@login_required
def profile(request):
    # Simple profile landing that shows editable fields for candidate users
    # For now redirect to recruiter dashboard if recruiter
    try:
        p = request.user.profile
        if p.user_type == 'recruiter':
            return redirect('accounts.recruiter_dashboard')
    except Profile.DoesNotExist:
        # create via signal normally; redirect to signup for now
        return redirect('accounts.signup')

    template_data = {'title': 'My Profile', 'profile': request.user.profile}
    return render(request, 'accounts/profile.html', {'template_data': template_data})


@login_required
def profile_edit(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('home.index')

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('accounts.profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {'template_data': {'title': 'Edit Profile', 'form': form}})


@login_required
def recruiter_dashboard(request):
    """Recruiter dashboard: quick links and candidate search"""
    try:
        profile = request.user.profile
        if profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can access the recruiter dashboard.')
            return redirect('home.index')
    except Profile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts.signup')

    return render(request, 'accounts/recruiter_dashboard.html', {'template_data': {'title': 'Recruiter Dashboard'}})


@login_required
def candidate_search(request):
    """Search candidates by skills, location, and projects."""
    try:
        profile = request.user.profile
        if profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can search candidates.')
            return redirect('home.index')
    except Profile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts.signup')

    skills_q = request.GET.get('skills', '').strip()
    location_q = request.GET.get('location', '').strip()
    projects_q = request.GET.get('projects', '').strip()

    qs = Profile.objects.filter(user__is_active=True, user_type='regular')

    if skills_q:
        # simple comma/space separated search: check if any skill substring is in skills field
        for token in [t.strip() for t in skills_q.replace(',', ' ').split() if t.strip()]:
            qs = qs.filter(skills__icontains=token)
    if location_q:
        qs = qs.filter(location__icontains=location_q)
    if projects_q:
        qs = qs.filter(projects__icontains=projects_q)

    # Pagination
    paginator = Paginator(qs.order_by('user__username'), 12)
    page_number = request.GET.get('page')
    results = paginator.get_page(page_number)

    template_data = {
        'title': 'Candidate Search',
        'results': results,
        'search_terms': {'skills': skills_q, 'location': location_q, 'projects': projects_q}
    }
    return render(request, 'accounts/candidate_search.html', {'template_data': template_data})