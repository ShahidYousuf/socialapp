from django.urls import path, include
from rest_framework import routers
from .views import SignUpView
from .views import LoginView
from .views import FriendListAPIView, UserAPIView, UserListAPIView, APIBaseView
#
# router = routers.DefaultRouter()
# router.register(r'', FriendsAPIView)

urlpatterns = [
    path('register/', SignUpView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', APIBaseView.as_view(), name='root'),
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserAPIView.as_view(), name='user-detail'),
    path('users/<int:pk>/friends/', FriendListAPIView.as_view(), name='friend-list'),
]