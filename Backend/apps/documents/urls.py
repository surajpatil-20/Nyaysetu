from rest_framework.routers import DefaultRouter
from .views import (
    DocumentViewSet, DocumentChunkViewSet,
    UploadedDocumentViewSet, UploadedDocumentChunkViewSet
)

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'document-chunks', DocumentChunkViewSet, basename='document-chunk')
router.register(r'user-documents', UploadedDocumentViewSet, basename='user-document')
router.register(r'user-chunks', UploadedDocumentChunkViewSet, basename='user-chunk')

urlpatterns = router.urls

