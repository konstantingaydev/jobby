import os
import sys
import time
import json
import urllib.request
import urllib.parse
import ssl
import django

# 1. Setup Django environment
# Adds the project root to python path so we can import settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobby.settings')
django.setup()

from profiles.models import Profile

def direct_geocode(location):
    """Geocode function defined directly in the script to ensure it runs."""
    print(f"  > Querying Nominatim for: '{location}'")
    if not location:
        return None
        
    try:
        base = 'https://nominatim.openstreetmap.org/search?format=json&limit=1&q='
        url = base + urllib.parse.quote(location)
        # Use a descriptive User-Agent
        headers = {'User-Agent': 'Jobby/1.0 (admin@jobby.example)'} 
        req = urllib.request.Request(url, headers=headers)
        
        # Ignore SSL certificate errors for development
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            raw_data = resp.read().decode('utf-8')
            # Print the raw response to debug API issues
            print(f"  > API Response: {raw_data[:100]}...") 
            
            data = json.loads(raw_data)
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
            else:
                print("  > API returned no results (empty list).")
    except Exception as e:
        print(f"  > Error during request: {e}")
    return None

def run():
    # Find profiles that have a location written down
    profiles = Profile.objects.filter(location__isnull=False).exclude(location='')
    print(f"Found {profiles.count()} profiles with locations.")
    
    for p in profiles:
        # Only process if coordinates are missing
        if not p.latitude or not p.longitude:
            print(f"\nProcessing: {p.user.username} ({p.location})")
            
            coords = direct_geocode(p.location)
            
            if coords:
                lat, lon = coords
                print(f"  > Success! Saving {lat}, {lon}")
                # Update using .update() to bypass model.save() logic completely
                Profile.objects.filter(pk=p.pk).update(latitude=lat, longitude=lon)
            else:
                print("  > Failed to resolve coordinates.")
            
            # Sleep to be nice to the API
            time.sleep(1.5)
        else:
            print(f"Skipping {p.user.username} (already has coordinates)")

if __name__ == '__main__':
    run()