from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CaseViewSet, PartyViewSet, CasePartyViewSet,
    CaseJudgeViewSet, CaseEventViewSet, CaseCitationViewSet,
    RelatedCasesView, AdminStatsView
)

router = DefaultRouter()
router.register(r'cases', CaseViewSet, basename='case')
router.register(r'parties', PartyViewSet, basename='party')
router.register(r'case-parties', CasePartyViewSet, basename='case-party')
router.register(r'case-judges', CaseJudgeViewSet, basename='case-judge')
router.register(r'case-events', CaseEventViewSet, basename='case-event')
router.register(r'case-citations', CaseCitationViewSet, basename='case-citation')

urlpatterns = [
    path('cases/<int:case_id>/related/', RelatedCasesView.as_view(), name='related-cases-nested'),
    path('<int:case_id>/related/', RelatedCasesView.as_view(), name='related-cases'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
] + router.urls

