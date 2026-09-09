from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from authentication.redis_client import is_token_blacklisted_in_redis
from drf_spectacular.extensions import OpenApiAuthenticationExtension

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

class RedisJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    OpenAPI 3.0 security scheme definition for RedisJWTAuthentication.
    Renders the Bearer JWT authorization lock in Swagger UI.
    """
    target_class = 'authentication.authentication.RedisJWTAuthentication'
    name = 'jwtAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'Enter JWT Bearer token obtained from /api/auth/login/ or /api/auth/register/'
        }
