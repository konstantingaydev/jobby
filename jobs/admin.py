from django.contrib import admin
from .models import Job

class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'location', 'latitude', 'longitude', 'employment_type', 'experience_level', 'is_active', 'created_at']
    list_filter = ['employment_type', 'experience_level', 'is_active', 'created_at']
    search_fields = ['title', 'company_name', 'location', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'posted_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company_name', 'location', 'latitude', 'longitude', 'image')
        }),
        ('Job Details', {
            'fields': ('employment_type', 'experience_level', 'salary_min', 'salary_max')
        }),
        ('Content', {
            'fields': ('description', 'requirements', 'benefits')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('posted_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.posted_by = request.user
        # Let model.save handle geocoding if coords are missing or location changed
        super().save_model(request, obj, form, change)

admin.site.register(Job, JobAdmin)