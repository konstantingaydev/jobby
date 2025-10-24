from django.contrib import admin
from .models import EmailMessage

@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'recipient', 'message_type', 'status', 'sent_at']
    list_filter = ['message_type', 'status', 'sent_at']
    search_fields = ['subject', 'message', 'sender__username', 'recipient__username']
    readonly_fields = ['sent_at', 'read_at', 'replied_at']
    date_hierarchy = 'sent_at'
    
    fieldsets = (
        ('Email Details', {
            'fields': ('sender', 'recipient', 'subject', 'message')
        }),
        ('Metadata', {
            'fields': ('message_type', 'status', 'related_job', 'parent_message')
        }),
        ('Timestamps', {
            'fields': ('sent_at', 'read_at', 'replied_at'),
            'classes': ('collapse',)
        }),
    )
