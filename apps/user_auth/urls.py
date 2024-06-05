from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import AuthenticationViewSet, UserViewSet

urlpatterns = [
    path("auth/login", AuthenticationViewSet.as_view({"post": "login"}), name="login"),
    path(
        "auth/register",
        AuthenticationViewSet.as_view({"post": "register"}),
        name="register",
    ),
    path(
        "auth/logout", AuthenticationViewSet.as_view({"post": "logout"}, name="logout")
    ),
    path(
        "auth/user",
        UserViewSet.as_view({"get": "user_info"}),
        name="user-info",
    ),
    path(
        "auth/users",
        UserViewSet.as_view({"get": "list"}),
        name="user-list",
    ),
    path(
        "auth/users/history",
        UserViewSet.as_view({"get": "user_login_history_range"}),
        name="user-history-list",
    ),
    path(
        "auth/user/groups",
        AuthenticationViewSet.as_view({"get": "get_groups"}),
        name="role",
    ),
    path(
        "auth/token/verify",
        AuthenticationViewSet.as_view({"post": "verify_token"}),
        name="token_verify",
    ),
    path("auth/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "users/<int:pk>",
        UserViewSet.as_view({"delete": "destroy"}),
        name="user-detail",
    ),
]
