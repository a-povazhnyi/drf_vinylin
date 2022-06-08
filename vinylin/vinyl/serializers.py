from rest_framework.serializers import ModelSerializer, SlugRelatedField

from store.serializers import (
    DiscountSerializer,
    ImageSerializer,
    StorageSerializer
)
from vinyl.models import Vinyl


class BaseVinylSerializer(ModelSerializer):
    storage = StorageSerializer()
    images = ImageSerializer(many=True)
    tags = SlugRelatedField(slug_field='title', many=True, read_only=True)
    discount = DiscountSerializer()

    class Meta:
        abstract = True
        model = Vinyl
        fields = '__all__'


class VinylSerializer(BaseVinylSerializer):
    class Meta:
        model = Vinyl
        fields = (
            'id', 'title', 'price', 'storage', 'discount', 'images', 'tags'
        )


class RetrieveVinylSerializer(BaseVinylSerializer):
    country = SlugRelatedField(slug_field='name', read_only=True)
    genres = SlugRelatedField(slug_field='title', many=True, read_only=True)
    artist = SlugRelatedField(slug_field='name', read_only=True)
    storage = StorageSerializer()

    class Meta:
        model = Vinyl
        exclude = ('created_at', 'vinyl_title')
