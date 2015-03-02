from rest_framework.generics import GenericAPIView
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework import status

from ..serializers import RawMeasurementListSerializer
from ..models import RawMeasurement, TideGauge


class RawMeasurements(GenericAPIView):
    """
    Store raw measurements for a tide gauge. Predictions must be given in a
    JSON array. Note that any bad prediction in the list will cause the
    entire batch to be dropped.
    """

    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    queryset = RawMeasurement.objects.none()  # req for DjangoModelPermissions
    serializer_class = RawMeasurementListSerializer

    def post(self, request, *args, **kwargs):
        tide_gauge = TideGauge.objects.get(slug=self.kwargs['tide_gauge_slug'])

        serializer = RawMeasurementListSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(tide_gauge=tide_gauge)

        return Response({'detail': 'OK.'}, status=status.HTTP_200_OK)
