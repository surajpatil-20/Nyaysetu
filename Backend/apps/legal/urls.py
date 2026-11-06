from rest_framework.routers import DefaultRouter
from .views import ActViewSet, SectionViewSet, CaseSectionViewSet

router = DefaultRouter()
router.register(r'acts', ActViewSet, basename='act')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'case-sections', CaseSectionViewSet, basename='case-section')

urlpatterns = router.urls

