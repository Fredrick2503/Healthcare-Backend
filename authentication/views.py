import time
from django.db import connection
from django.contrib.auth import get_user_model
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    RedisRevokeTokenSerializer,
)
from authentication.redis_client import (
    blacklist_token_in_redis,
    check_redis_health,
)

User = get_user_model()

class HealthCheckView(APIView):
    """
    Health check endpoint returning the status of Django, Database, and Redis.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        health_report = {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {}
        }

        # 1. Database Check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
            health_report["services"]["database"] = {
                "status": "healthy",
                "engine": connection.settings_dict.get('ENGINE', 'unknown')
            }
        except Exception as e:
            health_report["status"] = "degraded"
            health_report["services"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # 2. Redis Check
        redis_status = check_redis_health()
        health_report["services"]["redis"] = redis_status
        if redis_status.get("status") not in ("healthy", "disabled"):
            health_report["status"] = "degraded"

        response_status = status.HTTP_200_OK if health_report["status"] == "healthy" else status.HTTP_200_OK
        return Response(health_report, status=response_status)

class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Register a new user with name, email, and password.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for immediate access
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "User registered successfully.",
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """
    POST /api/auth/login/
    Log in a user with email and password, returning JWT access & refresh tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = validated_data['user']
        tokens = validated_data['tokens']

        return Response({
            "message": "Login successful.",
            "user": UserSerializer(user).data,
            "access": tokens['access'],
            "refresh": tokens['refresh'],
            "tokens": tokens
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/auth/profile/
    Retrieve or update currently authenticated user profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class RedisRevokeTokenView(APIView):
    """
    POST /api/auth/redis-revoke/
    Revokes a JWT token directly in Redis cache for instantaneous invalidation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RedisRevokeTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data['token']

        jti = payload.get('jti')
        exp = payload.get('exp')

        if not jti:
            return Response(
                {"error": "Token does not contain a 'jti' claim."},
                status=status.HTTP_400_BAD_REQUEST
            )

        ttl = 3600
        if exp:
            current_timestamp = int(time.time())
            ttl = max(1, exp - current_timestamp)

        success = blacklist_token_in_redis(jti=jti, ttl_seconds=ttl)
        if success:
            return Response({
                "message": f"Token with JTI '{jti}' successfully added to Redis blacklist.",
                "ttl_seconds": ttl
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Failed to store token in Redis or Redis is disabled."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
