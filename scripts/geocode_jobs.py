import os
import sys
import time
import urllib.request
import urllib.parse
import json

# Bootstrap Django
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobby.settings')
import django
django.setup()

from jobs.models import Job

NOMINATIM = 'https://nominatim.openstreetmap.org/search?format=json&limit=1&q='

def geocode_location(location):
    if not location:
        return None
    url = NOMINATIM + urllib.parse.quote(location)
    headers = { 'User-Agent': 'JobbyGeocoder/1.0 (your-email@example.com)' }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode('utf-8')
            arr = json.loads(data)
            if arr:
                return float(arr[0]['lat']), float(arr[0]['lon'])
    except Exception as e:
        print('Geocode error for', location, ':', e)
    return None


def main():
    jobs = Job.objects.filter(is_active=True)
    updated = 0
    for job in jobs:
        if job.latitude is not None and job.longitude is not None:
            continue
        loc = job.location
        print('Geocoding:', job.id, job.title, '->', repr(loc))
        coords = geocode_location(loc)
        if coords:
            job.latitude, job.longitude = coords
            job.save()
            updated += 1
            print('  Saved coords:', coords)
        else:
            print('  No coords found')
        # Be polite to Nominatim: 1 second between requests
        time.sleep(1)
    print('Done. Updated', updated, 'jobs.')

if __name__ == '__main__':
    main()
