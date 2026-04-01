from django.contrib import admin
from django.urls import path, include
from api.views import CookieTokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/', include('gameplay.urls')),
    path('api/', include('django.contrib.auth.urls')),
    path('api/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
]