import os
import sys
import django
import json

# Ensure project root is on sys.path so Django settings module can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobby.settings')
django.setup()

from jobs.models import Job
from django.urls import reverse

jobs = Job.objects.filter(is_active=True)
out = []
for job in jobs:
    out.append({
        'id': job.id,
        'title': job.title,
        'company_name': job.company_name,
        'location': job.location,
        'url': reverse('jobs.show', args=[job.id])
    })
print(json.dumps({'jobs': out}, indent=2))
