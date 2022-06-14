from rest_framework.serializers import ModelSerializer

from store.models import Discount, Storage, Image


class DiscountSerializer(ModelSerializer):
    class Meta:
        model = Discount
        fields = ('amount', 'price_with_discount')


class StorageSerializer(ModelSerializer):
    class Meta:
        model = Storage
        fields = ('quantity',)


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = ('image',)

    def to_representation(self, instance):
        return instance.image.url
