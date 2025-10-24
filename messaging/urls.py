from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.email_inbox, name='inbox'),
    path('send/<int:candidate_id>/', views.send_email_to_candidate, name='send_email'),
    path('email/<int:email_id>/', views.email_detail, name='email_detail'),
    path('sent/<int:email_id>/', views.email_sent, name='email_sent'),
    path('mark-read/<int:email_id>/', views.mark_email_read, name='mark_read'),
]
