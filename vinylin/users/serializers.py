from rest_framework import serializers

from users.models import User, Profile
from users.services import UserService


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('user',)


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        exclude = (
            'date_joined', 'is_active', 'is_staff',
            'is_superuser', 'last_login', 'password'
        )


class RegistrationSerializer(UserSerializer):
    @property
    def service(self) -> UserService:
        return self.context.get('service')

    def validate_password(self, value):
        self.service.validate_password(value)
        return value

    def create(self, validated_data):
        return self.service.register(validated_data)

    class Meta:
        model = User
        exclude = (
            'date_joined', 'is_active', 'is_staff',
            'is_superuser', 'last_login', 'is_email_verified'
        )


class EmailChangeSerializer(UserSerializer):
    def update(self, instance, validated_data):
        service = UserService(user=instance)
        service.change_email(validated_data)
        return service.user

    class Meta:
        model = User
        fields = ('email',)


class EmailConfirmSerializer(UserSerializer):
    """Checks token validity and confirm email verification"""
    token = serializers.CharField(required=True)

    @property
    def service(self) -> UserService:
        return self.context.get('service')

    def validate_token(self, value):
        if not self.service.is_token_valid(value):
            raise serializers.ValidationError(
                {'errors': ['Token is invalid or expired.']}
            )
        return value

    def update(self, instance, validated_data):
        self.service.confirm_email()
        return self.service.user

    class Meta:
        model = User
        fields = ('token',)


class PasswordChangeSerializer(UserSerializer):
    password2 = serializers.CharField(required=True)

    @property
    def service(self) -> UserService:
        return self.context.get('service')

    def validate_password(self, value):
        """Old password validation"""
        if not self.instance.check_password(value):
            raise serializers.ValidationError(
                {'errors': ['Old password is incorrect.']}
            )
        return value

    def validate_password2(self, value):
        """New password validation"""
        self.service.validate_password(value)
        return value

    def update(self, instance: User, validated_data):
        self.service.set_password(validated_data.get('password'))
        return self.service.user

    class Meta:
        model = User
        fields = ('password', 'password2')


class PasswordResetSerializer(UserSerializer):
    email = serializers.EmailField(required=True)

    @property
    def service(self) -> UserService:
        return self.context.get('service')

    def validate_email(self, value):
        self.service.email = value
        if not self.service.user:
            raise serializers.ValidationError(
                {'errors': ['User with this e-mail does not exist.']}
            )

        if not self.service.user.is_email_verified:
            raise serializers.ValidationError(
                {'errors': ['User\'s e-mail is not verified.']}
            )
        return value

    class Meta:
        model = User
        fields = ('email',)


class PasswordResetConfirmSerializer(UserSerializer):
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    @property
    def service(self) -> UserService:
        return self.context.get('service')

    def validate_email(self, value):
        self.service.email = value
        if not self.service.user:
            raise serializers.ValidationError(
                {'errors': ['User with this e-mail does not exist.']}
            )

        self.instance = self.service.user
        return value

    def validate_token(self, value):
        self.service.email = self.initial_data.get('email')
        if not self.service.is_token_valid(value):
            raise serializers.ValidationError(
                {'errors': ['Token is invalid or expired.']}
            )
        return value

    def validate_new_password(self, value):
        self.service.validate_password(value)
        return value

    def update(self, instance: User, validated_data):
        self.service.set_password(validated_data.get('password'))
        return self.service.user

    class Meta:
        model = User
        fields = ('token', 'email', 'new_password')
