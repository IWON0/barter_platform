from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from ads.views import logout_view

schema_view = get_schema_view(
    openapi.Info(
        title="Barter Platform API",
        default_version='v1',
        description="API для платформы обмена вещами",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ads.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema'),
]
