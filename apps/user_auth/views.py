from django.utils import timezone
from django.db.models import Max, Case, When, BooleanField, Value, Count, Q
from django.db.models.functions import TruncDay
from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework import filters
from rest_framework_simplejwt.tokens import RefreshToken
from http import HTTPMethod
from .helpers import get_user_from_jwt
from .serializers import LoginSerializer, UserSerializer, GroupSerializer
from .models import User
from django.contrib.auth.models import Group
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from utils.format import str_to_bool
from api.pagination import PagePagination
from datetime import datetime, timedelta


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
        url_path="api/auth/register",
        permission_classes=[permissions.AllowAny],
    )
    def register(self, request):
        data = request.data

        if not User.objects.filter(email=data["email"]).exists():
            new_user = User.objects.create_user(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                phone_number=data["phone_number"],
                password=data["password"],
                position=data["position"],
                is_active=True,
            )
            # Adding group to user
            group = Group.objects.get(name="Employee")
            new_user.groups.add(group)

            return Response(
                {"detail": "Successfully Registered"}, status=status.HTTP_200_OK
            )

        else:
            return Response(
                {"detail": "Email already registered"},
                status=status.HTTP_409_CONFLICT,
            )

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

        return Response({"detail": "Successfully logout"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=[HTTPMethod.POST])
    def verify_token(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "No token provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # This will verify the token's validity and check for expiration
            UntypedToken(refresh_token)

            # Check if the token is blacklisted
            outstanding_token = OutstandingToken.objects.get(token=refresh_token)
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("created_at")
    serializer_class = UserSerializer
    pagination_class = PagePagination
    # permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=[HTTPMethod.GET])
    def list(self, request):
        is_online = request.GET.get("isOnline")
        today = request.GET.get("today")
        search_query = request.GET.get("q")
        query = self.queryset
        now = timezone.now()

        if today:
            if str_to_bool(today):
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                today_end = today_start + timezone.timedelta(days=1)
                query = query.filter(last_login__range=(today_start, today_end))

        latest_token = (
            OutstandingToken.objects.all()
            .values("user_id")
            .annotate(latest_expires_at=Max("expires_at"))
            .filter(expires_at__gt=now)
        )
        # Manual serialization to a list of dictionaries
        latest_users_token = []
        for token in latest_token:
            latest_token = OutstandingToken.objects.filter(
                user_id=token["user_id"], expires_at=token["latest_expires_at"]
            ).first()  # Getting the first token that matches (there should be only one)

            if latest_token:
                latest_users_token.append(
                    {
                        "id": latest_token.id,
                        "user_id": latest_token.user_id,
                    }
                )

        online_users_id = []
        for users_token in latest_users_token:
            offline = BlacklistedToken.objects.filter(token_id=users_token["id"])
            if not offline:
                online_users_id.append(users_token["user_id"])

        query = query.annotate(
            is_online=Case(
                When(id__in=online_users_id, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )

        if is_online:
            is_online_bool = str_to_bool(is_online)
            if is_online_bool:
                query = query.filter(is_online=True)
            else:
                query = query.filter(is_online=False)

        # Apply search functionality
        if search_query:
            query = query.filter(
                Q(email__icontains=search_query)
                | Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(position__icontains=search_query)
            )

        page = self.paginate_queryset(query)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=[HTTPMethod.GET])
    def user_login_history_range(self, request):
        start_date = request.GET.get("startDate")
        end_date = request.GET.get("endDate")

        # Validate and convert the date strings to datetime objects
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure the dates are timezone-aware
        start_date = timezone.make_aware(start_date, timezone.get_current_timezone())
        end_date = timezone.make_aware(end_date, timezone.get_current_timezone())
        end_date = end_date + timedelta(days=1) - timedelta(seconds=1)

        # Filter the queryset based on the provided dates
        login_counts_per_day = (
            OutstandingToken.objects.filter(
                created_at__gte=start_date, created_at__lte=end_date
            )
            .annotate(date=TruncDay("created_at"))  # Truncate the created_at to date
            .values("date")  # Group by date
            .annotate(
                value=Count("user_id", distinct=True)
            )  # Count distinct user_ids for each date
            .order_by("date")  # Order results by date
        )

        # Convert query results to a list of dictionaries (optional, depends on needs)
        login_counts = list(login_counts_per_day)

        return Response(login_counts, status=status.HTTP_200_OK)

    @action(detail=False, methods=[HTTPMethod.GET])
    def user_info(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if auth_header is not None:
            tokens = auth_header.split()[1]
            user = get_user_from_jwt(tokens)

            groups = user.groups.all().values_list("name", flat=True)
            groups_list = list(groups)

            return Response(
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "position": user.position,
                    "groups": groups_list,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserSearchView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["email", "first_name", "last_name", "position"]
