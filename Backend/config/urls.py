"""
URL configuration for NYAYASETU platform.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.cases.views import AdminStatsView


class PlatformHealthCheckView(APIView):
    """
    NYAYASETU Health Check & System Info Endpoint.
    """
    def get(self, request):
        return Response({
            "platform": "NYAYASETU",
            "tagline": "An AI-Assisted, Evidence-Oriented Judicial Information Platform",
            "status": "healthy",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/auth/",
                "cases": "/api/cases/cases/",
                "courts": "/api/courts/courts/",
                "legal": "/api/legal/acts/",
                "documents": "/api/documents/documents/",
                "services": "/api/services/services/",
                "laws": "/api/laws/categories/",
                "search": "/api/search/",
                "assistant": "/api/assistant/",
                "graph": "/api/graph/status/",
                "admin": "/admin/"
            }
        })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", PlatformHealthCheckView.as_view(), name="health_check"),
    path("api/admin/stats/", AdminStatsView.as_view(), name="admin_stats_root"),
    path("api/auth/", include("apps.users.urls")),
    path("api/sources/", include("apps.sources.urls")),
    path("api/courts/", include("apps.courts.urls")),
    path("api/cases/", include("apps.cases.urls")),
    path("api/legal/", include("apps.legal.urls")),
    path("api/laws/", include("apps.laws.urls")),
    path("api/documents/", include("apps.documents.urls")),
    path("api/services/", include("apps.services.urls")),
    path("api/search/", include("apps.search.urls")),
    path("api/assistant/", include("apps.assistant.urls")),
    path("api/graph/", include("apps.graph.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
