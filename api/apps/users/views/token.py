from rest_framework import parsers, renderers
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import AuthTokenSerializer


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


validate_token = ValidateToken.as_view()
