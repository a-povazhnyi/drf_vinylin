from rest_framework import serializers

from users.models import User, Profile
from users.tokens import TokenGenerator
from users.utils import _validate_password


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('user',)


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        exclude = (
            'date_joined', 'is_active', 'is_staff',
            'is_superuser', 'last_login', 'password'
        )


class RegistrationSerializer(UserSerializer):
    class Meta:
        model = User
        exclude = (
            'date_joined', 'is_active', 'is_staff',
            'is_superuser', 'last_login'
        )

    # def validate_password(self, value):
    #     _validate_password(password=value, user=self.instance)
    #     return value

    def create(self, validated_data):
        profile = validated_data.pop('profile')
        password = validated_data.get('password')
        _validate_password(password=password, user=None)
        # user = User(**validated_data)
        user = User.objects.create_user(**validated_data)

        if profile and not self._is_profile_blank(profile):
            Profile.objects.filter(user=user).update(**profile)
        return user

    @staticmethod
    def _is_profile_blank(profile):
        for value in profile.values():
            if value is None:
                return False
        return True


class EmailChangeSerializer(UserSerializer):
    def update(self, instance, validated_data):
        instance.is_email_verified = False
        instance.email = validated_data.get('email')
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('email',)


class EmailConfirmSerializer(UserSerializer):
    """Checks token validity and confirm email verification"""
    token = serializers.CharField(write_only=True, required=True)

    def validate_token(self, value):
        token_generator = TokenGenerator()
        if not token_generator.check_token(user=self.instance, token=value):
            raise serializers.ValidationError(
                {'errors': ['Token is invalid or expired.']}
            )
        return value

    def update(self, instance: User, validated_data):
        instance.is_email_verified = True
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('token',)


class PasswordChangeSerializer(UserSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value):
        """Old password validation"""
        if not self.instance.check_password(value):
            raise serializers.ValidationError(
                {'errors': ['Old password is incorrect.']}
            )
        return value

    def validate_password2(self, value):
        """New password validation"""
        _validate_password(password=value, user=self.instance)
        return value

    def update(self, instance: User, validated_data):
        instance.set_password(validated_data.get('password2'))
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('password', 'password2')


class PasswordResetConfirmSerializer(UserSerializer):
    token = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_token(self, value):
        token_generator = TokenGenerator()
        if not token_generator.check_token(user=self.instance, token=value):
            raise serializers.ValidationError(
                {'errors': ['Token is invalid or expired.']}
            )
        return value

    def validate_new_password(self, value):
        _validate_password(password=value, user=self.instance)
        return value

    def update(self, instance: User, validated_data):
        instance.set_password(validated_data.get('new_password'))
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('token', 'new_password')
