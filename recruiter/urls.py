from django.urls import path
from . import views

app_name = 'recruiter'

urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='dashboard'),
    path('candidates/', views.candidate_search, name='candidate_search'),
    path('kanban/', views.kanban_board, name='kanban'),
    path('kanban/<int:job_id>/', views.kanban_board, name='kanban_job'),
    path('kanban/move_card/', views.move_card, name='kanban_move_card'),
]
