from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from .views import (
    BookViewSet,
    UploadPDFView,
    UploadZIPView,
    AIChatView,
)

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/upload-pdf/', UploadPDFView.as_view(), name='upload-pdf'),
    path('api/upload-zip/', UploadZIPView.as_view(), name='upload-zip'),
    path('api/chat/', AIChatView.as_view(), name='ai-chat'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)