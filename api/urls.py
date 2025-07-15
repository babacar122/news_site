from django.urls import path
from .views import AuthView, UserListView, ArticleListView, CategoryArticleView

urlpatterns = [
    path('auth/', AuthView.as_view(), name='api-auth'),
    path('users/', UserListView.as_view(), name='api-users'),
    path('articles/', ArticleListView.as_view(), name='api-articles'),
    path('articles/category/<int:category_id>/', CategoryArticleView.as_view(), name='api-category-articles'),
]