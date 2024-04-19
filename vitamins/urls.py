from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.VitaminHome.as_view(), name='home'),
    path('search/', views.ShopVitamin.as_view(), name='search'),
    path('<slug:brand_slug>/<slug:vit_slug>/', views.ShowVitamin.as_view(), name='vitamin'),
    path('shop/', views.ShopVitamin.as_view(), name='shop'),
    path('request_for_delivery/', views.RequestForDelivery.as_view(), name='request_for_delivery'),
    path('contacts/', views.ContactView.as_view(), name='contacts'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
