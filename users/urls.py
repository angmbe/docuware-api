from django.urls import path
from .views import RegisterUserView, LoginUserView, UserListView, UpdatePasswordView

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('register/', RegisterUserView.as_view(), name='user-register'),
    path('login/', LoginUserView.as_view(), name='user-login'),
    path('update-password/', UpdatePasswordView.as_view(), name='user-update-password'),
]
