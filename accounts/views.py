from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseForbidden

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
def search_candidates(request):
    # Only allow recruiters to use this view
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'recruiter':
        return HttpResponseForbidden('You are not authorized to view this page.')

    query_skills = request.GET.get('skills', '').strip()
    query_location = request.GET.get('location', '').strip()
    query_projects = request.GET.get('projects', '').strip()

    users = User.objects.filter(profile__user_type='regular')

    filters = Q()
    if query_location:
        filters &= Q(profile__location__icontains=query_location)

    # For skills and projects, we'll match any of the comma-separated tokens
    def token_q(field_name, query):
        qobj = Q()
        tokens = [t.strip() for t in query.split(',') if t.strip()]
        for t in tokens:
            qobj |= Q(**{f"{field_name}__icontains": t})
        return qobj

    if query_skills:
        filters &= token_q('profile__skills', query_skills)

    if query_projects:
        filters &= token_q('profile__projects', query_projects)

    results = users.filter(filters).select_related('profile')

    context = {
        'title': 'Search Candidates',
        'results': results,
        'query_skills': query_skills,
        'query_location': query_location,
        'query_projects': query_projects,
    }
    return render(request, 'accounts/search_candidates.html', context)