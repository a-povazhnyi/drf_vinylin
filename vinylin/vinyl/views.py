from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet

from vinyl.models import Vinyl
from vinyl.serializers import VinylSerializer, RetrieveVinylSerializer


class VinylViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    model = Vinyl
    queryset = Vinyl.objects.all()
    http_method_names = ('get',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RetrieveVinylSerializer
        return VinylSerializer
