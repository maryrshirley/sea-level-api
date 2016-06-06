from django.conf import settings
from django.contrib.auth import authenticate, load_backend
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

from nopassword.models import LoginCode

from rest_framework import parsers, renderers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.models import Token

from nopassword.utils import get_username, get_username_field

from ..serializers.token import (AuthTokenSerializer,
                                 EmailTokenSerializer)


class ValidateToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser,
                      parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response()


class AuthCodeView(APIView):
    permission_classes = ()
    lookup_url_kwarg = "login_code"

    @staticmethod
    def validate_code(login_code):
        code = get_object_or_404(LoginCode.objects.select_related('user'),
                                 code=login_code)
        username = get_username(code.user)
        user = authenticate(**{get_username_field(): username,
                               'code': login_code})
        if user is None:
            raise Http404
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'email': code.user.email})

    def get(self, request, *args, **kwargs):
        login_code = self.kwargs.get('login_code', None)

        return self.validate_code(login_code)

    def post(self, request, *args, **kwargs):
        login_code = request.data.get('code', None)
        return self.validate_code(login_code)


class BaseTokenView(CreateAPIView):
    permission_classes = ()

    def get_host(self, request):
        origin = request.META.get('HTTP_ORIGIN')
        if origin == 'null':
            return HttpResponse('Invalid site', status=400)

        if not origin:
            prefix = 'https' if request.is_secure() else 'http'
            return ("{0}://{1}".format(prefix, request.get_host()), False)

        return (origin, True)

    def get_backends(self, backend_paths):
        backends = []
        for backend_path in backend_paths:
            backend = load_backend(backend_path)
            backends.append(backend)

        return backends

    def send_login_code(self, code, host, url):
        for backend in self.get_backends(self.auth_backends):
            backend.send_login_code(code, host=host, url=url)

    def create(self, request, callback, *args, **kwargs):
        host, is_remote = self.get_host(request)
        if not is_remote:
            callback = None

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = LoginCode.create_code_for_user(serializer.user)
        self.send_login_code(
            code,
            host,
            callback
        )

        return HttpResponse('OK', status=201)


class EmailTokenView(BaseTokenView):
    serializer_class = EmailTokenSerializer
    auth_backends = settings.EMAIL_AUTHENTICATION_BACKENDS


auth_code = AuthCodeView.as_view()
email_token = EmailTokenView.as_view()
validate_token = ValidateToken.as_view()
