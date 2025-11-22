from django.contrib import admin
from .models import Stage, CandidateCard, SavedSearch


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
	list_display = ('name', 'job', 'order')
	list_filter = ('job',)


@admin.register(CandidateCard)
class CandidateCardAdmin(admin.ModelAdmin):
	list_display = ('application', 'stage', 'order', 'added_at')
	list_filter = ('stage__job',)


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
	list_display = ('name', 'recruiter', 'created_at', 'updated_at')
	list_filter = ('recruiter', 'created_at')
	search_fields = ('name', 'skills', 'location', 'projects')
	readonly_fields = ('created_at', 'updated_at')
	fieldsets = (
		('Basic Information', {
			'fields': ('recruiter', 'name')
		}),
		('Search Criteria', {
			'fields': ('skills', 'location', 'projects', 'general_search')
		}),
		('Timestamps', {
			'fields': ('created_at', 'updated_at')
		}),
	)
