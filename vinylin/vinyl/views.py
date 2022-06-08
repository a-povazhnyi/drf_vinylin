from rest_framework.viewsets import ReadOnlyModelViewSet

from vinyl.models import Vinyl
from vinyl.serializers import VinylSerializer, RetrieveVinylSerializer


class VinylViewSet(ReadOnlyModelViewSet):
    model = Vinyl
    queryset = Vinyl.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RetrieveVinylSerializer
        return VinylSerializer
