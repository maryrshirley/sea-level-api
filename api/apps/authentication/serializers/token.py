from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework.authtoken.models import Token
from rest_framework import serializers

User = get_user_model()


class EmailTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Invalid email {0}'.format(value))
        return value


class AuthTokenSerializer(serializers.Serializer):
    token = serializers.CharField(label=_("Token"))

    def validate(self, attrs):
        token = attrs.get('token')
        if not token:
            msg = _('Must pass "token".')
            raise serializers.ValidationError(msg)

        try:
            Token.objects.get(key=token)
        except Token.DoesNotExist:
            msg = _('Invalid token.')
            raise serializers.ValidationError(msg)

        return []
