from django.urls import path
from . import views

app_name = 'recruiter'

urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='dashboard'),
    path('candidates/', views.candidate_search, name='candidate_search'),
    path('candidates/save/', views.save_search, name='save_search'),
    path('candidates/apply/<int:search_id>/', views.apply_saved_search, name='apply_saved_search'),
    path('candidates/delete/<int:search_id>/', views.delete_saved_search, name='delete_saved_search'),
    path('kanban/', views.kanban_board, name='kanban'),
    path('kanban/<int:job_id>/', views.kanban_board, name='kanban_job'),
    path('kanban/move_card/', views.move_card, name='kanban_move_card'),
]
