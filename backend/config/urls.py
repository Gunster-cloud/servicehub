"""
URL configuration for ServiceHub project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from servicehub.apps.users.views import (
    AuthLoginView, AuthRegisterView, AuthLogoutView, AuthMeView
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/login/', AuthLoginView.as_view(), name='auth_login'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='auth_refresh'),
    path('api/v1/auth/logout/', AuthLogoutView.as_view(), name='auth_logout'),
    path('api/v1/auth/me/', AuthMeView.as_view(), name='auth_me'),
    path('api/v1/auth/register/', AuthRegisterView.as_view(), name='auth_register'),
    
    # API Routes
    path('api/v1/users/', include('servicehub.apps.users.urls')),
    path('api/v1/clients/', include('servicehub.apps.clients.urls')),
    path('api/v1/quotes/', include('servicehub.apps.quotes.urls')),
    path('api/v1/services/', include('servicehub.apps.services.urls')),
    path('api/v1/analytics/', include('servicehub.apps.analytics.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

