from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import UntypedToken
import jwt
from django.conf import settings

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class RedisRevokeTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, help_text="JWT access or refresh token string to revoke in Redis")

    def validate_token(self, value):
        try:
            UntypedToken(value)
            decoded = jwt.decode(
                value,
                settings.SECRET_KEY,
                algorithms=[settings.SIMPLE_JWT.get('ALGORITHM', 'HS256')],
                options={"verify_exp": False}
            )
            return decoded
        except Exception as e:
            raise serializers.ValidationError(f"Invalid token format or signature: {str(e)}")
