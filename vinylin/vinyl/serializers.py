from rest_framework.serializers import ModelSerializer, SlugRelatedField

from store.serializers import (
    DiscountSerializer,
    ImageSerializer,
    StorageSerializer
)
from vinyl.models import Vinyl


class AbstractVinylSerializer(ModelSerializer):
    storage = StorageSerializer()
    images = ImageSerializer(many=True)
    tags = SlugRelatedField(slug_field='title', many=True, read_only=True)
    discount = DiscountSerializer()

    class Meta:
        model = Vinyl
        fields = '__all__'


class VinylSerializer(AbstractVinylSerializer):
    class Meta:
        model = Vinyl
        fields = (
            'id', 'title', 'price', 'storage', 'discount', 'images', 'tags'
        )


class RetrieveVinylSerializer(AbstractVinylSerializer):
    country = SlugRelatedField(slug_field='name', read_only=True)
    genres = SlugRelatedField(slug_field='title', many=True, read_only=True)
    artist = SlugRelatedField(slug_field='name', read_only=True)
    storage = StorageSerializer()

    class Meta:
        model = Vinyl
        exclude = ('created_at', 'vinyl_title')
