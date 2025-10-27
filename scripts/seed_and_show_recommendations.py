# This script is intended to be run with: python manage.py shell < scripts/seed_and_show_recommendations.py
from django.contrib.auth.models import User
from accounts.models import Profile
from jobs.models import Job
from django.test import Client
from django.utils import timezone

# Helper to create user if not exists
def get_or_create_user(username, email, password, user_type='regular'):
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    if created:
        user.set_password(password)
        user.save()
    # Ensure profile exists
    profile = user.profile
    profile.user_type = user_type
    profile.save()
    return user

print('Creating users...')
recruiter = get_or_create_user('rec1', 'rec1@example.com', 'password', user_type='recruiter')
seeker = get_or_create_user('alice', 'alice@example.com', 'password', user_type='regular')

# Give the seeker some skills (profiles app uses skills_text and projects_text)
seeker.profile.skills_text = 'Python, Django, REST'
seeker.profile.location = 'Atlanta'
seeker.profile.projects_text = 'portfolio, blog'
seeker.profile.save()

print('Creating jobs...')
# Create two jobs
job1, created = Job.objects.get_or_create(title='Backend Engineer', defaults={
    'company_name':'Acme Corp', 'location':'Atlanta', 'description':'Work on backend services',
    'requirements':'Python, Django, REST, APIs', 'skills_required':'Python, Django, REST',
    'posted_by': recruiter, 'is_active': True
})
job2, created = Job.objects.get_or_create(title='Frontend Engineer', defaults={
    'company_name':'Beta Inc', 'location':'Remote', 'description':'Frontend with React',
    'requirements':'React, JavaScript, CSS', 'skills_required':'React, JavaScript',
    'posted_by': recruiter, 'is_active': True
})

print('Using test client to fetch recommendations for alice...')
client = Client()
logged_in = client.login(username='alice', password='password')
print('Logged in:', logged_in)
response = client.get('/jobs/recommendations/')
print('Status code:', response.status_code)
html = response.content.decode('utf-8')
# Save to file for easy viewing
out_path = 'scripts/recommendations_preview.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved rendered HTML to', out_path)
print('\n--- HTML preview (first 2000 chars) ---\n')
print(html[:2000])
print('\n--- end preview ---')
