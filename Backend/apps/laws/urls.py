from rest_framework.routers import DefaultRouter
from .views import (
    LawCategoryViewSet,
    LawActViewSet,
    LawSectionViewSet,
    LegalScenarioViewSet,
)

router = DefaultRouter()
router.register(r'categories', LawCategoryViewSet, basename='law-category')
router.register(r'acts', LawActViewSet, basename='law-act')
router.register(r'sections', LawSectionViewSet, basename='law-section')
router.register(r'scenarios', LegalScenarioViewSet, basename='legal-scenario')

urlpatterns = router.urls
