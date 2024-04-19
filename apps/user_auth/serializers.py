from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group
from django.utils import timezone
from .models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data["email"]
        password = data["password"]
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid login credentials")

        # Update last_login manually
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        # Generate Token
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class UserSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "position",
            "phone_number",
            "last_login",
            "is_online",
        ]
        
    def get_is_online(self, obj):
        # The 'is_online' attribute is expected to be annotated to the queryset.
        # Default to False if it's somehow not present.
        return getattr(obj, 'is_online', False)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name"]
