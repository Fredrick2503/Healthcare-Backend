import time
from django.db import connection
from django.contrib.auth import get_user_model
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from authentication.serializers import (
    UserSerializer,
    RegisterSerializer,
    RegisterResponseSerializer,
    LoginSerializer,
    LoginResponseSerializer,
    RedisRevokeTokenSerializer,
)
from authentication.redis_client import (
    blacklist_token_in_redis,
    check_redis_health,
)

User = get_user_model()

class HealthCheckView(APIView):
    """
    Check the health status of the Django application, Database, and Redis cache.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['System'],
        summary="Service Health Check",
        description="Returns current availability and connectivity status for PostgreSQL/SQLite and Redis.",
        responses={
            200: OpenApiResponse(description="Health status report (healthy or degraded).")
        }
    )
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
    Register a new user account with name, email, and password.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        tags=['Authentication'],
        summary="User Registration",
        description="Creates a new user profile with name, email, and password, and issues initial JWT access/refresh tokens.",
        request=RegisterSerializer,
        responses={
            201: RegisterResponseSerializer,
            400: OpenApiResponse(description="Validation error (e.g. duplicate email, invalid password).")
        },
        examples=[
            OpenApiExample(
                "Registration Example",
                value={
                    "name": "Dr. Meredith Grey",
                    "email": "meredith@grey.com",
                    "password": "Password123!"
                },
                request_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for immediate access
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "User registered successfully.",
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """
    Authenticate an existing user using email and password, returning JWT access and refresh tokens.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        tags=['Authentication'],
        summary="User Login",
        description="Authenticates user credentials and returns signed JWT access and refresh tokens.",
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
            400: OpenApiResponse(description="Invalid credentials or disabled account.")
        },
        examples=[
            OpenApiExample(
                "Login Example",
                value={
                    "email": "dr.meredith@seattlegrace.com",
                    "password": "Password123!"
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = validated_data['user']

        return Response({
            "message": "Login successful.",
            "user": UserSerializer(user).data,
            "access": validated_data['access'],
            "refresh": validated_data['refresh'],
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the currently authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(
        tags=['Authentication'],
        summary="Get / Update User Profile",
        description="Returns profile details for the currently authenticated user identified by the Bearer access token."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Authentication'],
        summary="Update User Profile",
        description="Update profile details (name, email) for the authenticated user."
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=['Authentication'],
        summary="Partial Update User Profile",
        description="Partially update profile details for the authenticated user."
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

class RedisRevokeTokenView(APIView):
    """
    Revoke a JWT token instantaneously via Redis cache.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RedisRevokeTokenSerializer

    @extend_schema(
        tags=['Authentication'],
        summary="Instant Token Revocation (Redis)",
        description="Stores the token's JTI claim in Redis with auto-expiring TTL matching the token lifespan, instantly rejecting any subsequent requests.",
        request=RedisRevokeTokenSerializer,
        responses={
            200: OpenApiResponse(description="Token successfully revoked in Redis."),
            400: OpenApiResponse(description="Invalid token format or missing JTI claim."),
            500: OpenApiResponse(description="Redis is disabled or connection failed.")
        }
    )
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
