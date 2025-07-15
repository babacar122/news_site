from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (UserCreateView, UserUpdateView, UserListView, login_view, logout_view)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/new/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
]