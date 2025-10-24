from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Email functionality
    path('inbox/', views.email_inbox, name='inbox'),
    path('send/<int:candidate_id>/', views.send_email_to_candidate, name='send_email'),
    path('email/<int:email_id>/', views.email_detail, name='email_detail'),
    path('sent/<int:email_id>/', views.email_sent, name='email_sent'),
    path('mark-read/<int:email_id>/', views.mark_email_read, name='mark_read'),
    
    # Internal messaging functionality
    path('messages/', views.internal_messages, name='internal_messages'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start-conversation/', views.start_conversation, name='start_conversation'),
    path('start-conversation/<int:user_id>/', views.start_conversation, name='start_conversation_with_user'),
    path('mark-message-read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
    path('unread-count/', views.get_unread_count, name='get_unread_count'),
    path('delete-conversation/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
]
