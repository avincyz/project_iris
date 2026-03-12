# api\urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('home/', views.home, name = 'home'),
    path('signup/', views.signup, name = 'signup'),
    path('login/', views.CookieTokenObtainPairView.as_view(), name = 'login'),
    path('login/refresh/', views.CookieTokenRefreshView.as_view(), name = 'login_refresh'),
    path('google-login/', views.google_login, name = 'google-login'),
    path('password-change/', views.password_change, name = 'password-change'),
    path('password-reset-request/', views.password_reset_request, name = 'password-reset-request'),
    path('password-reset/<str:uidb64>/<str:token>/', views.password_reset_confirm, name = 'password-reset-confirm' ),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name = 'verify-email'),
    path('logout/', views.logout, name = 'logout'),
]