from rest_framework import permissions, viewsets, status
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from http import HTTPMethod
from utils.jwt import decode_jwt
from .helpers import get_user_from_jwt
from .serializers import LoginSerializer, UserSerializer, GroupSerializer
from .models import User
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class AuthenticationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(
        detail=False,
        methods=[HTTPMethod.POST],
        url_path="api/auth/login",
        permission_classes=[permissions.AllowAny],
    )
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=[HTTPMethod.POST],
        url_path="api/auth/logout",
        permission_classes=[permissions.IsAuthenticated],
    )
    def logout(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Soccessfully logout"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=[HTTPMethod.POST])
    def verify_token(self, request, *args, **kwargs):
        token = request.data.get("token")
        if not token:
            return Response(
                {"detail": "No token provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # This will verify the token's validity and check for expiration
            UntypedToken(token)

            # Check if the token is blacklisted
            outstanding_token = OutstandingToken.objects.get(token=token)
            token_id = outstanding_token.id
            if BlacklistedToken.objects.filter(token=token_id).exists():
                raise InvalidToken("Token is blacklisted")

            return Response({"detail": "Token is valid."})

        except TokenError as e:
            # Handles expired and invalid tokens
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=[HTTPMethod.GET])
    def get_groups(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if auth_header is not None:
            tokens = auth_header.split()[1]
            user = get_user_from_jwt(tokens)
            serialier = GroupSerializer(user.groups, many=True)
            return Response(serialier.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No Auth Token Found"}, status=status.HTTP_403_OK)

    @action(detail=False, methods=[HTTPMethod.GET])
    def user_info(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if auth_header is not None:
            tokens = auth_header.split()[1]
            user = get_user_from_jwt(tokens)

            groups = user.groups.all().values_list("name", flat=True)
            groups_list = list(groups)

            return Response(
                {"id": user.id, "name": user.name, "groups": groups_list},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("created_at")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
