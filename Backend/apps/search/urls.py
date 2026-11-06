"""Search URL configuration."""
from django.urls import path
from apps.search.views import HybridSearchView, CaseTimelineView

urlpatterns = [
    path("", HybridSearchView.as_view(), name="hybrid_search"),
    path("cases/<int:case_id>/timeline/", CaseTimelineView.as_view(), name="case_timeline"),
]
