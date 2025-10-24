from django.contrib import admin
from .models import EmailMessage, Conversation, InternalMessage, MessageNotification

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

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['participants__username', 'participants__first_name', 'participants__last_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Conversation Details', {
            'fields': ('participants', 'related_job', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(InternalMessage)
class InternalMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'message_type', 'created_at', 'is_read']
    list_filter = ['message_type', 'created_at', 'read_at', 'is_deleted']
    search_fields = ['content', 'sender__username', 'recipient__username']
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Message Details', {
            'fields': ('conversation', 'sender', 'recipient', 'content', 'message_type')
        }),
        ('Attachments', {
            'fields': ('attachment_url', 'attachment_name'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_deleted', 'created_at', 'read_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MessageNotification)
class MessageNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'message__content']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
