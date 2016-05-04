from django.utils.translation import ugettext_lazy as _

from rest_framework.authtoken.models import Token
from rest_framework import serializers


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
