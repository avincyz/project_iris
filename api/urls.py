# api\urls.py
from django.urls import path
from django.views.generic import TemplateView

from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('home/', views.home, name = 'home'),
    path('token/', views.CookieTokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name = 'token_refresh'),
    path('google-login/', views.google_login, name = 'google-login'),
    path('signup/', views.SignUpView.as_view(), name = 'signup'),
    path('logout/', views.logout, name = 'logout'),
]