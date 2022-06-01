from rest_framework.viewsets import ModelViewSet

from vinyl.models import Vinyl
from vinyl.serializers import VinylSerializer, RetrieveVinylSerializer


class VinylViewSet(ModelViewSet):
    model = Vinyl
    queryset = Vinyl.objects.all()
    http_method_names = ('get',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RetrieveVinylSerializer
        return VinylSerializer
