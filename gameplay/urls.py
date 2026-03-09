from django.urls import path
from . import views

urlpatterns = [
    path('sessions/', views.list_active_sessions, name = 'sessions-list'),
    path('session/start/', views.session_start_view, name = 'session-start'),
    path('stage/<str:stage_name>/generate/', views.generate_questions_view, name = 'generate-questions'),
    path('question/<int:question_id>/answer/', views.answer_question_view, name = 'answer-question'),
    path('session/<int:session_id>/debrief/', views.generate_debrief_view, name = 'debrief'),
    path('session/<int:session_id>/pause/', views.pause_session, name = 'pause'),
    path('session/<int:session_id>/resume/', views.resume_session, name = 'resume'),
    path('session/<int:session_id>/abandon/', views.abandon_session, name = 'abandon'),
]