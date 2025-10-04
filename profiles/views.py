from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory
from .models import Profile, Skill, Education, WorkExperience, Project
from .forms import ProfileForm, SkillForm, EducationForm, WorkExperienceForm, PrivacySettingsForm, ProjectForm

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
    return render(request, 'profiles/profile_detail.html', context)

@login_required
def profile_edit(request):
    """Edit the current user's profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profiles:profile_detail')
    else:
        form = ProfileForm(instance=profile)
    
    context = {
        'template_data': {'title': 'Edit Profile'},
        'form': form,
        'profile': profile,
    }
    return render(request, 'profiles/profile_edit.html', context)

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
            return redirect('profiles:profile_detail')
    else:
        formset = SkillFormSet(queryset=profile.skills.all())
    
    context = {
        'template_data': {'title': 'Manage Skills'},
        'formset': formset,
        'profile': profile,
    }
    return render(request, 'profiles/manage_skills.html', context)

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
            return redirect('profiles:profile_detail')
    else:
        formset = EducationFormSet(queryset=profile.education.all())
    
    context = {
        'template_data': {'title': 'Manage Education'},
        'formset': formset,
        'profile': profile,
    }
    return render(request, 'profiles/manage_education.html', context)

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
            return redirect('profiles:profile_detail')
    else:
        formset = ExperienceFormSet(queryset=profile.work_experience.all())
    
    context = {
        'template_data': {'title': 'Manage Work Experience'},
        'formset': formset,
        'profile': profile,
    }
    return render(request, 'profiles/manage_experience.html', context)

@login_required
def manage_projects(request):
    """Manage user's projects"""
    profile = request.user.profile
    ProjectFormSet = modelformset_factory(Project, form=ProjectForm, extra=1, can_delete=True)
    
    if request.method == 'POST':
        formset = ProjectFormSet(request.POST, queryset=profile.projects.all())
        if formset.is_valid():
            projects = formset.save(commit=False)
            for project in projects:
                project.profile = profile
                project.save()
            for project in formset.deleted_objects:
                project.delete()
            messages.success(request, 'Projects updated successfully!')
            return redirect('profiles:profile_detail')
    else:
        formset = ProjectFormSet(queryset=profile.projects.all())
    
    context = {
        'template_data': {'title': 'Manage Projects'},
        'formset': formset,
        'profile': profile,
    }
    return render(request, 'profiles/manage_projects.html', context)

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
            return redirect('profiles:profile_detail')
    else:
        form = PrivacySettingsForm(instance=profile)
    
    context = {
        'template_data': {'title': 'Privacy Settings'},
        'form': form,
        'profile': profile,
    }
    return render(request, 'profiles/privacy_settings.html', context)
