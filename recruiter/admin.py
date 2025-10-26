from django.contrib import admin
from .models import Stage, CandidateCard


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
	list_display = ('name', 'job', 'order')
	list_filter = ('job',)


@admin.register(CandidateCard)
class CandidateCardAdmin(admin.ModelAdmin):
	list_display = ('application', 'stage', 'order', 'added_at')
	list_filter = ('stage__job',)
