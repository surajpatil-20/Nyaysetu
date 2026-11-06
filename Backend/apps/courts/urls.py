from rest_framework.routers import DefaultRouter
from .views import CourtViewSet, JudgeViewSet, JudgeCourtHistoryViewSet

router = DefaultRouter()
router.register(r'courts', CourtViewSet, basename='court')
router.register(r'judges', JudgeViewSet, basename='judge')
router.register(r'judge-history', JudgeCourtHistoryViewSet, basename='judge-history')

urlpatterns = router.urls

