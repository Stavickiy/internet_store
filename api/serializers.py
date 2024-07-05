from rest_framework import serializers

from vitamins.models import Category, Vitamin, Brand
from vitamins.views import calculate_price


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name')


class VitaminSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    sale_price = serializers.SerializerMethodField()

    class Meta:
        model = Vitamin
        fields = (
            'id',
            'title',
            'count',
            'discount',
            'cat',
            'brand',
            'packaging',
            'unit',
            'absolute_url',
            'image_url',
            'final_price',
            'sale_price'
        )

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()

    def get_image_url(self, obj):
        return obj.images.filter(is_main=True).first().image.url

    def get_final_price(self, obj):
        return calculate_price(obj).final_price

    def get_sale_price(self, obj):
        return calculate_price(obj).sale_price if obj.discount else 0
