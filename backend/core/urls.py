"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from core import settings
from core.views import HealthCheckAPI

schema_view = get_schema_view(
    openapi.Info(
        title="Receipt Management API",
        default_version="v1",
        description="API for receipt upload, extraction, and management",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@receipts.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

api_urlpatterns = [
    path("auth/", include("apps.authentications.api.urls")),
    path("admin/", include("apps.users.api.urls")),
    path("jobs/", include("apps.jobs.api.urls")),
    path("receipts/", include("apps.receipts.api.urls")),  # Add this
]

urlpatterns = [
    path("healthcheck/", HealthCheckAPI.as_view(), name="healthcheck"),
    path("api/", include(api_urlpatterns)),
    path("admin/", admin.site.urls),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
