from django.urls import path
from authentication.views import (
    HealthCheckView,
    RegisterView,
    UserProfileView,
    RedisRevokeTokenView,
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/profile/', UserProfileView.as_view(), name='auth_profile'),
    path('auth/redis-revoke/', RedisRevokeTokenView.as_view(), name='auth_redis_revoke'),
]
