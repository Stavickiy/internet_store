from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.generics import ListAPIView

from api.serializers import CategorySerializer, VitaminSerializer, BrandSerializer
from vitamins.models import Category, Vitamin, Brand


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class VitaminsByCategory(ListAPIView):
    serializer_class = VitaminSerializer

    def get_queryset(self):
        category_id = self.kwargs['pk']
        return Vitamin.objects.filter(cat_id=category_id).order_by('count')


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class VitaminsByBrand(ListAPIView):
    serializer_class = VitaminSerializer

    def get_queryset(self):
        brand_id = self.kwargs['pk']
        return Vitamin.objects.filter(brand_id=brand_id).order_by('count')

class VitaminAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = Vitamin.objects.all()
    serializer_class = VitaminSerializer
