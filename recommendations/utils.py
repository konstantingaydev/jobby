"""
Utility functions for candidate recommendation algorithm.
"""
from django.db.models import Q
from profiles.models import Profile, Skill, WorkExperience, Education, Project
from jobs.models import Job
from applications.models import Application
import re


def normalize_skill(skill):
    """Normalize skill name for comparison."""
    return skill.strip().lower()


def extract_skills_from_text(text):
    """Extract skills from text (comma-separated or space-separated)."""
    if not text:
        return []
    
    # Split by comma or newline
    skills = re.split(r'[,;\n]', text)
    # Clean and normalize
    skills = [normalize_skill(s) for s in skills if s.strip()]
    return skills


def get_candidate_skills(candidate_profile):
    """Get all skills from a candidate profile."""
    skills = set()
    
    # From Skill model
    for skill in candidate_profile.skills.all():
        skills.add(normalize_skill(skill.name))
    
    # From skills_text field
    if candidate_profile.skills_text:
        text_skills = extract_skills_from_text(candidate_profile.skills_text)
        skills.update(text_skills)
    
    # From projects
    for project in candidate_profile.projects.all():
        if project.technologies:
            tech_skills = extract_skills_from_text(project.technologies)
            skills.update(tech_skills)
    
    # From work experience descriptions
    for exp in candidate_profile.work_experience.all():
        if exp.description:
            # Try to extract common tech terms
            desc_skills = extract_skills_from_text(exp.description)
            skills.update(desc_skills)
    
    return skills


def calculate_skills_match(job, candidate_profile):
    """Calculate skills match score between job and candidate."""
    job_skills = set()
    
    # Get required skills from job
    if job.skills_required:
        job_skills = set(extract_skills_from_text(job.skills_required))
    
    # Also extract from requirements and description
    if job.requirements:
        req_skills = extract_skills_from_text(job.requirements)
        job_skills.update(req_skills)
    
    if job.description:
        desc_skills = extract_skills_from_text(job.description)
        job_skills.update(desc_skills)
    
    if not job_skills:
        return 0.0
    
    candidate_skills = get_candidate_skills(candidate_profile)
    
    if not candidate_skills:
        return 0.0
    
    # Calculate match
    matched_skills = job_skills.intersection(candidate_skills)
    match_percentage = (len(matched_skills) / len(job_skills)) * 100
    
    return min(match_percentage, 100.0)


def calculate_experience_match(job, candidate_profile):
    """Calculate experience level match."""
    # Map experience levels to numeric values
    experience_map = {
        'entry': 1,
        'mid': 2,
        'senior': 3,
        'executive': 4,
    }
    
    job_level = experience_map.get(job.experience_level, 2)
    
    # Calculate candidate experience based on work experience
    total_years = 0
    for exp in candidate_profile.work_experience.all():
        from datetime import date
        start = exp.start_date
        end = exp.end_date if exp.end_date else date.today()
        years = (end - start).days / 365.25
        total_years += years
    
    # Map years to experience level
    if total_years < 2:
        candidate_level = 1  # entry
    elif total_years < 5:
        candidate_level = 2  # mid
    elif total_years < 10:
        candidate_level = 3  # senior
    else:
        candidate_level = 4  # executive
    
    # Calculate match score
    level_diff = abs(job_level - candidate_level)
    if level_diff == 0:
        return 100.0
    elif level_diff == 1:
        return 75.0
    elif level_diff == 2:
        return 50.0
    else:
        return 25.0


def calculate_location_match(job, candidate_profile):
    """Calculate location match score."""
    # If job is remote, location doesn't matter
    if job.is_remote:
        return 100.0
    
    if not job.location or not candidate_profile.location:
        return 50.0  # Neutral score if location info missing
    
    job_loc = job.location.lower().strip()
    candidate_loc = candidate_profile.location.lower().strip()
    
    # Exact match
    if job_loc == candidate_loc:
        return 100.0
    
    # Check if same city or state
    job_parts = job_loc.split(',')
    candidate_parts = candidate_loc.split(',')
    
    # City match
    if len(job_parts) > 0 and len(candidate_parts) > 0:
        if job_parts[0].strip() == candidate_parts[0].strip():
            return 80.0
    
    # State/region match
    if len(job_parts) > 1 and len(candidate_parts) > 1:
        if job_parts[1].strip() == candidate_parts[1].strip():
            return 60.0
    
    # Check for "remote" in candidate location
    if 'remote' in candidate_loc:
        return 70.0
    
    return 30.0  # Low match for different locations


def calculate_overall_match_score(job, candidate_profile):
    """Calculate overall match score with weighted components."""
    skills_score = calculate_skills_match(job, candidate_profile)
    experience_score = calculate_experience_match(job, candidate_profile)
    location_score = calculate_location_match(job, candidate_profile)
    
    # Weighted average
    # Skills: 50%, Experience: 30%, Location: 20%
    overall_score = (
        skills_score * 0.5 +
        experience_score * 0.3 +
        location_score * 0.2
    )
    
    return round(overall_score, 2)


def generate_recommendations_for_job(job, limit=20, exclude_applied=True):
    """
    Generate candidate recommendations for a job.
    
    Args:
        job: Job instance
        limit: Maximum number of recommendations to return
        exclude_applied: Whether to exclude candidates who already applied
    
    Returns:
        List of CandidateRecommendation objects
    """
    from .models import CandidateRecommendation
    from django.utils import timezone
    
    # Get all job seeker profiles that are visible to recruiters
    candidate_profiles = Profile.objects.filter(
        user_type='regular'
    ).filter(
        Q(profile_visibility='public') | Q(profile_visibility='recruiters')
    ).select_related('user').prefetch_related('skills', 'work_experience', 'education', 'projects')
    
    # Exclude candidates who already applied
    if exclude_applied:
        applied_candidate_ids = Application.objects.filter(
            job=job
        ).values_list('applicant_id', flat=True)
        candidate_profiles = candidate_profiles.exclude(user_id__in=applied_candidate_ids)
    
    # Calculate match scores for each candidate
    recommendations = []
    for profile in candidate_profiles:
        # Skip if no skills or experience
        if not profile.skills.exists() and not profile.skills_text:
            continue
        
        # Calculate scores
        skills_score = calculate_skills_match(job, profile)
        experience_score = calculate_experience_match(job, profile)
        location_score = calculate_location_match(job, profile)
        overall_score = calculate_overall_match_score(job, profile)
        
        # Only recommend if match score is above threshold (e.g., 30%)
        if overall_score < 30:
            continue
        
        # Get or create recommendation
        recommendation, created = CandidateRecommendation.objects.get_or_create(
            job=job,
            candidate=profile.user,
            defaults={
                'candidate_profile': profile,
                'match_score': overall_score,
                'skills_match_score': skills_score,
                'experience_match_score': experience_score,
                'location_match_score': location_score,
                'status': 'new',
            }
        )
        
        # Update if not new
        if not created:
            recommendation.match_score = overall_score
            recommendation.skills_match_score = skills_score
            recommendation.experience_match_score = experience_score
            recommendation.location_match_score = location_score
            recommendation.last_updated = timezone.now()
            recommendation.save()
        
        recommendations.append(recommendation)
    
    # Sort by match score and return top candidates
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    return recommendations[:limit]


def refresh_recommendations_for_job(job):
    """Refresh recommendations for a specific job."""
    return generate_recommendations_for_job(job, limit=50)

