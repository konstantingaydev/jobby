#!/usr/bin/env python
"""
Script to geocode existing jobs that don't have coordinates.
Run this after updating the job model to add geocoding functionality.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobby.settings')
django.setup()

from jobs.models import Job

def geocode_existing_jobs():
    """Geocode all non-remote jobs that don't have coordinates."""
    
    # Get all non-remote jobs without coordinates
    jobs_to_geocode = Job.objects.filter(
        is_remote=False,
        latitude__isnull=True
    ) | Job.objects.filter(
        is_remote=False,
        longitude__isnull=True
    )
    
    total = jobs_to_geocode.count()
    print(f"Found {total} non-remote jobs without coordinates")
    
    if total == 0:
        print("All non-remote jobs already have coordinates!")
        return
    
    success_count = 0
    fail_count = 0
    
    import time
    
    for i, job in enumerate(jobs_to_geocode, 1):
        print(f"\n[{i}/{total}] Processing: {job.title} at {job.company_name}")
        print(f"  Location: {job.location}")
        print(f"  Is Remote: {job.is_remote}")
        
        # Add delay to respect Nominatim usage policy (max 1 request per second)
        if i > 1:
            print("  Waiting 1 second...")
            time.sleep(1)
        
        # Save the job, which will trigger geocoding
        old_lat = job.latitude
        old_lon = job.longitude
        
        try:
            job.save()
            
            if job.latitude and job.longitude:
                print(f"  ✓ Geocoded to: ({job.latitude}, {job.longitude})")
                success_count += 1
            else:
                print(f"  ✗ Failed to geocode (no results from geocoding service)")
                # Try manual geocoding to debug
                print(f"  Attempting manual geocode test...")
                coords = job._geocode_location(job.location)
                if coords:
                    print(f"  Manual geocode returned: {coords}")
                    job.latitude, job.longitude = coords
                    job.save()
                    print(f"  ✓ Successfully geocoded on retry")
                    success_count += 1
                else:
                    print(f"  ✗ Manual geocode also failed")
                    fail_count += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1
    
    print(f"\n{'='*60}")
    print(f"Geocoding complete!")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {fail_count}")
    print(f"  Total processed: {total}")
    print(f"{'='*60}")
    
    # Show summary of all jobs
    all_jobs = Job.objects.filter(is_active=True)
    remote_jobs = all_jobs.filter(is_remote=True).count()
    non_remote_with_coords = all_jobs.filter(
        is_remote=False,
        latitude__isnull=False,
        longitude__isnull=False
    ).count()
    non_remote_without_coords = all_jobs.filter(
        is_remote=False
    ).filter(
        latitude__isnull=True
    ).count() + all_jobs.filter(
        is_remote=False
    ).filter(
        longitude__isnull=True
    ).count()
    
    print(f"\nCurrent database state:")
    print(f"  Total active jobs: {all_jobs.count()}")
    print(f"  Remote jobs (no map display): {remote_jobs}")
    print(f"  Non-remote jobs with coordinates (will show on map): {non_remote_with_coords}")
    print(f"  Non-remote jobs without coordinates (won't show on map): {non_remote_without_coords}")

if __name__ == '__main__':
    geocode_existing_jobs()
