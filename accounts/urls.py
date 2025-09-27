from django.urls import path
from . import views
urlpatterns = [
    path('signup', views.signup, name='accounts.signup'),
    path('login/', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    
    # Recruiter routes (from job-posting branch)
    path('recruiter/dashboard/', views.recruiter_dashboard, name='accounts.recruiter_dashboard'),
    path('recruiter/search/', views.candidate_search, name='accounts.candidate_search'),
    
    # Profile URLs (detailed version from main)
    path('profile/', views.profile_detail, name='accounts.profile_detail'),
    path('profile/<int:pk>/', views.profile_detail, name='accounts.profile_detail'),
    path('profile/edit/', views.profile_edit, name='accounts.profile_edit'),
    path('profile/skills/', views.manage_skills, name='accounts.manage_skills'),
    path('profile/education/', views.manage_education, name='accounts.manage_education'),
    path('profile/experience/', views.manage_experience, name='accounts.manage_experience'),
    path('profile/privacy/', views.privacy_settings, name='accounts.privacy_settings'),
]
