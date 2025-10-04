from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('profile/', views.profile_detail, name='profile_detail'),
    path('profile/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('skills/', views.manage_skills, name='manage_skills'),
    path('education/', views.manage_education, name='manage_education'),
    path('experience/', views.manage_experience, name='manage_experience'),
    path('projects/', views.manage_projects, name='manage_projects'),
    path('privacy/', views.privacy_settings, name='privacy_settings'),
]
