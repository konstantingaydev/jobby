from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.db import models
from .forms import CustomUserCreationForm, CustomErrorList, ProfileForm, SkillForm, EducationForm, WorkExperienceForm, PrivacySettingsForm
from .models import Profile, Skill, Education, WorkExperience

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
def profile_detail(request, pk=None):
    """View a user's profile (own or others)"""
    if pk:
        profile = get_object_or_404(Profile, pk=pk)
    else:
        profile = request.user.profile
    
    # Check if viewer can see this profile
    if not can_view_profile(request.user, profile):
        messages.error(request, 'You do not have permission to view this profile.')
        return redirect('home.index')
    
    context = {
        'template_data': {'title': f'{profile.user.username}\'s Profile'},
        'profile': profile,
        'is_own_profile': profile.user == request.user,
        'can_view_contact': profile.show_contact_info or profile.user == request.user,
        'can_view_skills': profile.show_skills or profile.user == request.user,
        'can_view_education': profile.show_education or profile.user == request.user,
        'can_view_experience': profile.show_experience or profile.user == request.user,
        'can_view_links': profile.show_links or profile.user == request.user,
    }
    return render(request, 'accounts/profile_detail.html', context)

@login_required
def profile_edit(request):
    """Edit the current user's profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts.profile_detail')
    else:
        form = ProfileForm(instance=profile)
    
    context = {
        'template_data': {'title': 'Edit Profile'},
        'form': form,
        'profile': profile,
    }
    return render(request, 'accounts/profile_edit.html', context)

@login_required
def manage_skills(request):
    """Manage user's skills"""
    profile = request.user.profile
    SkillFormSet = modelformset_factory(Skill, form=SkillForm, extra=1, can_delete=True)
    
    if request.method == 'POST':
        formset = SkillFormSet(request.POST, queryset=profile.skills.all())
        if formset.is_valid():
            skills = formset.save(commit=False)
            for skill in skills:
                skill.profile = profile
                skill.save()
            for skill in formset.deleted_objects:
                skill.delete()
            messages.success(request, 'Skills updated successfully!')
            return redirect('accounts.profile_detail')
    else:
        formset = SkillFormSet(queryset=profile.skills.all())
    
    context = {
        'template_data': {'title': 'Manage Skills'},
        'formset': formset,
        'profile': profile,
    }
    return render(request, 'accounts/manage_skills.html', context)

@login_required
def manage_education(request):
    """Manage user's education"""
    profile = request.user.profile
    EducationFormSet = modelformset_factory(Education, form=EducationForm, extra=1, can_delete=True)
    
    if request.method == 'POST':
        formset = EducationFormSet(request.POST, queryset=profile.education.all())
        if formset.is_valid():
            educations = formset.save(commit=False)
            for education in educations:
                education.profile = profile
                education.save()
            for education in formset.deleted_objects:
                education.delete()
            messages.success(request, 'Education updated successfully!')
            return redirect('accounts.profile_detail')
    else:
        formset = EducationFormSet(queryset=profile.education.all())
    
    context = {
        'template_data': {'title': 'Manage Education'},
        'formset': formset,
        'profile': profile,
    }
    return render(request, 'accounts/manage_education.html', context)

@login_required
def manage_experience(request):
    """Manage user's work experience"""
    profile = request.user.profile
    ExperienceFormSet = modelformset_factory(WorkExperience, form=WorkExperienceForm, extra=1, can_delete=True)
    
    if request.method == 'POST':
        formset = ExperienceFormSet(request.POST, queryset=profile.work_experience.all())
        if formset.is_valid():
            experiences = formset.save(commit=False)
            for experience in experiences:
                experience.profile = profile
                experience.save()
            for experience in formset.deleted_objects:
                experience.delete()
            messages.success(request, 'Work experience updated successfully!')
            return redirect('accounts.profile_detail')
    else:
        formset = ExperienceFormSet(queryset=profile.work_experience.all())
    
    context = {
        'template_data': {'title': 'Manage Work Experience'},
        'formset': formset,
        'profile': profile,
    }
    return render(request, 'accounts/manage_experience.html', context)

def can_view_profile(viewer_user, profile_owner):
    """Check if viewer can see the profile based on privacy settings"""
    # Profile owner can always see their own profile
    if viewer_user == profile_owner.user:
        return True
    
    # Check profile visibility setting
    if profile_owner.profile_visibility == 'private':
        return False
    elif profile_owner.profile_visibility == 'public':
        return True
    elif profile_owner.profile_visibility == 'recruiters':
        # Only recruiters and admins can see
        if viewer_user.is_authenticated:
            return (viewer_user.profile.user_type == 'recruiter' or 
                   viewer_user.profile.user_type == 'admin' or 
                   viewer_user.is_staff)
        return False
    
    return False

@login_required
def privacy_settings(request):
    """Manage user's privacy settings"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = PrivacySettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Privacy settings updated successfully!')
            return redirect('accounts.profile_detail')
    else:
        form = PrivacySettingsForm(instance=profile)
    
    context = {
        'template_data': {'title': 'Privacy Settings'},
        'form': form,
        'profile': profile,
    }
    return render(request, 'accounts/privacy_settings.html', context)


# Recruiter Dashboard Functions (from job-posting branch)
@login_required
def recruiter_dashboard(request):
    """Dashboard view for recruiters."""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        messages.error(request, 'Access denied. Recruiter account required.')
        return redirect('home.index')
    
    template_data = {'title': 'Recruiter Dashboard'}
    return render(request, 'accounts/recruiter_dashboard.html', {'template_data': template_data})


@login_required  
def candidate_search(request):
    """Search view for recruiters to find candidates."""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        messages.error(request, 'Access denied. Recruiter account required.')
        return redirect('home.index')
        
    # Get all job seeker profiles
    candidates = Profile.objects.filter(user_type='regular')
    
    # Filter by search query if provided
    search_query = request.GET.get('search', '')
    if search_query:
        candidates = candidates.filter(
            models.Q(skills_text__icontains=search_query) |
            models.Q(location__icontains=search_query) |
            models.Q(projects__icontains=search_query) |
            models.Q(user__first_name__icontains=search_query) |
            models.Q(user__last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(candidates, 10)  # Show 10 candidates per page
    page_number = request.GET.get('page')
    candidates = paginator.get_page(page_number)
    
    context = {
        'template_data': {'title': 'Search Candidates'},
        'candidates': candidates,
        'search_query': search_query,
    }
    return render(request, 'accounts/candidate_search.html', context)
