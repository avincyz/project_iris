from django.urls import path
from . import views

urlpatterns = [
    path('sessions/', views.list_active_sessions, name = 'sessions-list'),
    path('session/start/', views.session_start_view, name = 'session-start'),
    path('generate/<int:session_id>/', views.generate_questions_view, name = 'generate-questions'),
    path('answer/<int:session_id>/', views.answer_question_view, name = 'answer-question'),
    path('debrief/<int:session_id>/', views.generate_debrief_view, name = 'debrief'),
    path('pause/<int:session_id>/', views.pause_session, name = 'pause'),
    path('resume/<int:session_id>/', views.resume_session, name = 'resume'),
    path('abandon/<int:session_id>/', views.abandon_session, name = 'abandon'),
]