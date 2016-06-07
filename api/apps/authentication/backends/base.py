# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import FieldError
from django.core.urlresolvers import reverse

from nopassword.models import LoginCode
from nopassword.utils import get_user_model

from ..models import LoginCodeExpired


class NoPasswordBackend(ModelBackend):
    def authenticate(self, code=None, **credentials):
        try:
            user = get_user_model().objects.get(**credentials)
            if not self.verify_user(user):
                return None
            if code is None:
                return self.generate_code(user)
            else:
                timeout = getattr(settings, 'NOPASSWORD_LOGIN_CODE_TIMEOUT',
                                  900)
                timestamp = datetime.now() - timedelta(seconds=timeout)
                login_code = LoginCode.objects.get(user=user, code=code,
                                                   timestamp__gt=timestamp)
                user = login_code.user
                user.code = login_code
                LoginCodeExpired.objects.expire(login_code)
                return user
        except (TypeError, get_user_model().DoesNotExist,
                LoginCode.DoesNotExist, FieldError):
            return None

    def generate_code(self, user):
        code = LoginCode.create_code_for_user(user)
        while LoginCode.objects.exclude(user=user).filter(code=code).exists() \
                or LoginCodeExpired.objects.filter(code=code).exists():
            code.delete()
            code = LoginCode.create_code_for_user(user)
        return code

    def send_login_code(self, code, host=None, url=None,
                        **kwargs):
        raise NotImplementedError

    def verify_user(self, user):
        return user.is_active

    def login_url(self, code, host, url):
        if not url:
            url = reverse('auth-code', args=[code.code])
        else:
            url = url + "/" + code.code

        return '%s%s' % (
            host,
            url,
        )
