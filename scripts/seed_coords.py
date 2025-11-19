import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobby.settings')
import django
django.setup()

from jobs.models import Job

# Simple mapping for common city names to coordinates
CITY_COORDS = {
    'dallas, tx': (32.7767, -96.7970),
    'atlanta, ga': (33.7490, -84.3880),
    'new york, ny': (40.7128, -74.0060),
    'san francisco, ca': (37.7749, -122.4194),
}

updated = 0
for job in Job.objects.filter(is_active=True):
    loc_key = (job.location or '').strip().lower()
    if loc_key in CITY_COORDS:
        lat, lon = CITY_COORDS[loc_key]
        job.latitude = lat
        job.longitude = lon
        job.save()
        print('Set coords for', job.id, job.title, '->', (lat, lon))
        updated += 1

print('Done. Updated', updated, 'jobs.')
