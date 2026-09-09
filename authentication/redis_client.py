"""
Redis helper module for token caching, blacklisting, and connectivity verification.
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)

REDIS_TOKEN_KEY_PREFIX = "jwt:revoked:"

def get_redis_client():
    """
    Returns the redis client instance using django-redis or direct redis.
    """
    try:
        from django_redis import get_redis_connection
        return get_redis_connection("default")
    except Exception as e:
        logger.warning(f"Could not obtain django-redis connection: {e}")
        try:
            import redis
            return redis.from_url(getattr(settings, 'REDIS_URL', 'redis://redis:6379/1'))
        except Exception as err:
            logger.error(f"Failed to connect directly to Redis: {err}")
            return None

def blacklist_token_in_redis(jti: str, ttl_seconds: int = 3600) -> bool:
    """
    Stores revoked JWT JTI in Redis with a time-to-live (TTL) equal to token lifetime.
    """
    if not getattr(settings, 'USE_REDIS_FOR_JWT', True):
        return False

    client = get_redis_client()
    if not client:
        return False

    try:
        key = f"{REDIS_TOKEN_KEY_PREFIX}{jti}"
        # Set with expiration
        client.setex(key, int(ttl_seconds), "revoked")
        return True
    except Exception as e:
        logger.error(f"Error saving revoked token {jti} to Redis: {e}")
        return False

def is_token_blacklisted_in_redis(jti: str) -> bool:
    """
    Checks if a given JWT JTI is present in Redis blacklist.
    """
    if not getattr(settings, 'USE_REDIS_FOR_JWT', True):
        return False

    client = get_redis_client()
    if not client:
        return False

    try:
        key = f"{REDIS_TOKEN_KEY_PREFIX}{jti}"
        return client.exists(key) > 0
    except Exception as e:
        logger.error(f"Error querying token {jti} in Redis: {e}")
        return False

def check_redis_health() -> dict:
    """
    Performs a ping to check Redis health status.
    """
    client = get_redis_client()
    if not client:
        return {"status": "unavailable", "message": "Redis client initialization failed"}

    try:
        pong = client.ping()
        if pong:
            return {"status": "healthy", "message": "Redis responded to PING"}
        return {"status": "unhealthy", "message": "Redis did not return PONG"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
