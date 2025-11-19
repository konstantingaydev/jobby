from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='jobs.index'),
    path('<int:id>/', views.show, name='jobs.show'),
    path('my-jobs/', views.my_jobs, name='jobs.my_jobs'),
    path('create/', views.create_job, name='jobs.create'),
    path('recommendations/', views.recommendations, name='jobs.recommendations'),
    path('<int:id>/edit/', views.edit_job, name='jobs.edit'),
    path('<int:id>/delete/', views.delete_job, name='jobs.delete'),
    path('map/', views.map_view, name='jobs.map'),
    path('api/geo-jobs/', views.jobs_geo_json, name='jobs.geo_json'),
]