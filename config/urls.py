from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from swagger import schema_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("auth/", include("accounts.urls")),
    path("", include("storage.urls")),
    path("activity-logs/", include("activity_logs.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
