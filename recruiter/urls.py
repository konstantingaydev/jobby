from django.urls import path
from . import views

app_name = 'recruiter'

urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='dashboard'),
    path('candidates/', views.candidate_search, name='candidate_search'),
]
