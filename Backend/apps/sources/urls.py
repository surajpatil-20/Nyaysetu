from rest_framework.routers import DefaultRouter
from .views import SourceViewSet

router = DefaultRouter()
router.register(r'sources', SourceViewSet, basename='source')

urlpatterns = router.urls

