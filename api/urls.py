from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, UserViewSet, AuthenticateView

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('authenticate/', AuthenticateView.as_view(), name='authenticate'),
]