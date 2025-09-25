from django.urls import path
from . import views
urlpatterns = [
    path('signup', views.signup, name='accounts.signup'),
    path('login/', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    # Recruiter routes
    path('recruiter/dashboard/', views.recruiter_dashboard, name='accounts.recruiter_dashboard'),
    path('recruiter/search/', views.candidate_search, name='accounts.candidate_search'),
    path('profile/', views.profile, name='accounts.profile'),
    path('profile/edit/', views.profile_edit, name='accounts.profile_edit'),
]