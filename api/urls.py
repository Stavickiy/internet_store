from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import CategoryViewSet, VitaminsByCategory, BrandViewSet, VitaminsByBrand, VitaminAPIView

app_name = 'api'
router = DefaultRouter()
router.register(r'vitamins', VitaminAPIView)

urlpatterns = [
    path('categories/', CategoryViewSet.as_view({'get': 'list'})),
    path('categories/<int:pk>/vitamins/', VitaminsByCategory.as_view()),
    path('brands/', BrandViewSet.as_view({'get': 'list'})),
    path('brands/<int:pk>/vitamins/', VitaminsByBrand.as_view()),
    path('', include(router.urls)),
]
