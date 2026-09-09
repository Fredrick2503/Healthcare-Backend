from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import UntypedToken, RefreshToken
import jwt
from django.conf import settings

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Full name of the user (e.g. Dr. Meredith Grey)"
    )
    email = serializers.EmailField(
        required=True,
        help_text="Valid and unique email address (e.g. user@example.com)"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        help_text="Password with at least 8 characters"
    )

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user

class RegisterResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="User registered successfully.")
    user = UserSerializer()
    token = serializers.CharField(help_text="JWT Access Token")

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="Registered email address (e.g. dr.meredith@seattlegrace.com)"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Account password"
    )

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        password = attrs.get('password')

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "User account is disabled."})

        refresh = RefreshToken.for_user(user)
        attrs['user'] = user
        attrs['token'] = str(refresh.access_token)
        return attrs

class LoginResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Login successful.")
    user = UserSerializer()
    token = serializers.CharField(help_text="JWT Access Token")

class RedisRevokeTokenSerializer(serializers.Serializer):
    token = serializers.CharField(
        required=True,
        help_text="JWT access or refresh token string to revoke immediately in Redis"
    )

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
