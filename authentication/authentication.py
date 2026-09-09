from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from authentication.redis_client import is_token_blacklisted_in_redis

class RedisJWTAuthentication(JWTAuthentication):
    """
    Extends SimpleJWT's JWTAuthentication to verify whether the token's JTI
    has been revoked in Redis cache, enabling instantaneous revocation.
    """
    def get_validated_token(self, raw_token):
        validated_token = super().get_validated_token(raw_token)
        jti = validated_token.get('jti')
        if jti and is_token_blacklisted_in_redis(jti):
            raise InvalidToken({
                'detail': 'Token has been revoked in Redis blacklist.',
                'code': 'token_revoked'
            })
        return validated_token
