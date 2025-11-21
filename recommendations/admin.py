from django.contrib import admin
from .models import CandidateRecommendation


@admin.register(CandidateRecommendation)
class CandidateRecommendationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'match_score', 'status', 'viewed_by_recruiter', 'is_favorite', 'recommended_at']
    list_filter = ['status', 'viewed_by_recruiter', 'is_favorite', 'recommended_at']
    search_fields = ['candidate__username', 'candidate__first_name', 'candidate__last_name', 'job__title', 'job__company_name']
    readonly_fields = ['recommended_at', 'last_updated']
    ordering = ['-match_score', '-recommended_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('job', 'candidate', 'candidate_profile')
        }),
        ('Match Scores', {
            'fields': ('match_score', 'skills_match_score', 'experience_match_score', 'location_match_score')
        }),
        ('Status & Interaction', {
            'fields': ('status', 'viewed_by_recruiter', 'viewed_at', 'is_favorite', 'recruiter_notes')
        }),
        ('Timestamps', {
            'fields': ('recommended_at', 'last_updated')
        }),
    )
