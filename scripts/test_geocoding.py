#!/usr/bin/env python
"""
Test script to debug geocoding issues
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobby.settings')
django.setup()

import urllib.request
import urllib.parse
import json

def test_geocode(location):
    """Test geocoding a location string"""
    print(f"\nTesting geocode for: '{location}'")
    print("="*60)
    
    if not location:
        print("ERROR: Location is empty")
        return None
    
    try:
        base = 'https://nominatim.openstreetmap.org/search?format=json&limit=1&q='
        url = base + urllib.parse.quote(location)
        print(f"URL: {url}")
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Jobby/1.0 (admin@jobby.example)'})
        print("Sending request...")
        
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read().decode('utf-8')
            print(f"Response received ({len(data)} bytes)")
            arr = json.loads(data)
            print(f"Parsed JSON: {json.dumps(arr, indent=2)}")
            
            if arr:
                lat = float(arr[0]['lat'])
                lon = float(arr[0]['lon'])
                print(f"\n✓ SUCCESS: Geocoded to ({lat}, {lon})")
                return (lat, lon)
            else:
                print("\n✗ FAILED: No results returned")
                return None
    except urllib.error.HTTPError as e:
        print(f"\n✗ HTTP ERROR: {e.code} - {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"\n✗ URL ERROR: {e.reason}")
        return None
    except Exception as e:
        print(f"\n✗ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    from jobs.models import Job
    
    # Test with the actual job location
    job = Job.objects.filter(is_remote=False).first()
    if job:
        print(f"Testing with job: {job.title}")
        print(f"Location from database: '{job.location}'")
        test_geocode(job.location)
        
        # Also test a few known locations
        print("\n" + "="*60)
        print("Testing other locations:")
        test_geocode("Atlanta, Georgia, USA")
        test_geocode("New York, NY")
        test_geocode("San Francisco, CA")
