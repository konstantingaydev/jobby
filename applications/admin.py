from django.contrib import admin
from .models import Application, ApplicationStatusHistory

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'applied_at', 'viewed_by_recruiter', 'days_since_applied']
    list_filter = ['status', 'applied_at', 'viewed_by_recruiter', 'job__company_name']
    search_fields = ['applicant__username', 'applicant__email', 'job__title', 'job__company_name']
    readonly_fields = ['applied_at', 'updated_at', 'days_since_applied']
    
    fieldsets = (
        ('Application Details', {
            'fields': ('applicant', 'job', 'status', 'cover_note')
        }),
        ('Tracking', {
            'fields': ('viewed_by_recruiter', 'recruiter_notes')
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def days_since_applied(self, obj):
        return obj.days_since_applied
    days_since_applied.short_description = 'Days Since Applied'
    
    def save_model(self, request, obj, form, change):
        # Track status changes
        if change and 'status' in form.changed_data:
            old_status = Application.objects.get(pk=obj.pk).status
            super().save_model(request, obj, form, change)
            
            # Create status history entry
            ApplicationStatusHistory.objects.create(
                application=obj,
                old_status=old_status,
                new_status=obj.status,
                changed_by=request.user,
                notes=f"Status changed via admin by {request.user.username}"
            )
        else:
            super().save_model(request, obj, form, change)

@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['application', 'old_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['old_status', 'new_status', 'changed_at']
    search_fields = ['application__applicant__username', 'application__job__title']
    readonly_fields = ['changed_at']
    
    def has_add_permission(self, request):
        # Prevent manual creation of status history entries
        return False
