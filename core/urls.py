from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    index_view,
    EmailTokenObtainView,
    RegisterView,
    UserMeView,
    BookViewSet,
    UploadPDFView,
    UploadZIPView,
    AIChatView,
)

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('', index_view, name='index'),
    path('api/auth/login/', EmailTokenObtainView.as_view(), name='token_obtain_pair'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/me/', UserMeView.as_view(), name='user-me'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/upload-pdf/', UploadPDFView.as_view(), name='upload-pdf'),
    path('api/upload-zip/', UploadZIPView.as_view(), name='upload-zip'),
    path('api/chat/', AIChatView.as_view(), name='ai-chat'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)