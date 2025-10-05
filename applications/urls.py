from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    # Job seeker application URLs
    path('apply/<int:job_id>/', views.apply_to_job, name='apply_to_job'),
    path('quick-apply/<int:job_id>/', views.quick_apply, name='quick_apply'),
    path('apply-with-note/<int:job_id>/', views.apply_with_note, name='apply_with_note'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
    path('withdraw/<int:application_id>/', views.withdraw_application, name='withdraw_application'),
    
    # Recruiter application management URLs
    path('recruiter/applications/', views.recruiter_applications, name='recruiter_applications'),
    path('recruiter/update-status/<int:application_id>/', views.update_application_status, name='update_application_status'),
]
