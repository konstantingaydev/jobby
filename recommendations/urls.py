from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('', views.all_recommendations, name='all_recommendations'),
    path('job/<int:job_id>/', views.job_recommendations, name='job_recommendations'),
    path('job/<int:job_id>/refresh/', views.refresh_recommendations, name='refresh_recommendations'),
    path('<int:recommendation_id>/viewed/', views.mark_recommendation_viewed, name='mark_viewed'),
    path('<int:recommendation_id>/status/', views.update_recommendation_status, name='update_status'),
    path('<int:recommendation_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
]
