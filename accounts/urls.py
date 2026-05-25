from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, MobileTokenView, LogoutView, ProfileView, ChangePasswordView, UsersListView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("token/", MobileTokenView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("change-password/", ChangePasswordView.as_view()),
    path("users/", UsersListView.as_view()),
]
