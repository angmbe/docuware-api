from django.urls import path
from .views import RegisterUserView, LoginUserView, UserListView

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('register/', RegisterUserView.as_view(), name='user-register'),
    path('login/', LoginUserView.as_view(), name='user-login'),
]
